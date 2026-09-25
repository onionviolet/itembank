"""On-demand storage accounting and explicit, rebuildable cache cleanup.

No course object or accepted artifact is a cleanup candidate. File bytes are
logical sizes, not a promise about APFS compression or freed physical blocks.
"""
import hashlib
import json
import os
import stat
import sys
import threading


CATEGORIES = {
    "content": "Courses, sources, and other files",
    "evidence": "Attempts and evidence",
    "recovery": "Journals and recovery history",
    "python_cache": "Rebuildable Python caches",
    "build": "Rust build output",
    "release": "Release files",
    "git": "Git history",
}
CACHE_TAG = "Signature: 8a477f597d28d172789f06886806bc55"
PROTECTED_DIRS = {"_journal", "_before", "_operations", "_proposals",
                  "_attempts", "_evidence", "_sources", "_notes", ".git"}
_CLEAN_LOCK = threading.Lock()


class StorageError(ValueError):
    pass


def _signature(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns, info.st_nlink]


def _token(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _plain_path(root, relative):
    """Resolve only ordinary directories and a regular final file."""
    path = root
    parts = relative.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise StorageError("The cleanup path is invalid.")
    for index, part in enumerate(parts):
        path = os.path.join(path, part)
        info = os.lstat(path)
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(info.st_mode):
            raise StorageError("A cleanup path changed or became a link. Refresh storage use.")
    return path, info


def is_developer_root(root):
    try:
        _plain_path(root, "src-tauri/Cargo.toml")
        _plain_path(root, "build.py")
        return True
    except (OSError, StorageError):
        return False


def _category(parts, developer):
    # Protect domain records even if a file happens to be named like a cache.
    if any(p in ("_journal", "_before", "_operations", "_proposals") for p in parts):
        return "recovery"
    if any(p in ("_attempts", "_evidence") for p in parts):
        return "evidence"
    if ".git" in parts:
        return "git"
    if developer and parts[:2] == ["src-tauri", "target"]:
        return "build"
    if developer and parts[0] == "dist":
        return "release"
    if any(p in ("_sources", "_notes") for p in parts):
        return "content"
    if len(parts) > 1 and parts[-2] == "__pycache__" and parts[-1].endswith(".pyc"):
        return "python_cache"
    return "content"


def inspect(root):
    """Read metadata once, without following links or reading learner content."""
    root = os.path.realpath(os.path.abspath(root))
    if not os.path.isdir(root):
        raise StorageError("Storage root is unavailable.")
    developer = is_developer_root(root)
    totals = {key: {"bytes": 0, "files": 0} for key in CATEGORIES}
    caches, build_entries, errors, build_blockers = [], [], [], []
    skipped_links = 0
    stack = [(root, [])]
    while stack:
        directory, prefix = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        except OSError:
            errors.append("/".join(prefix) or ".")
            continue
        for entry in entries:
            parts = prefix + [entry.name]
            relative = "/".join(parts)
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                errors.append(relative)
                continue
            in_build = developer and parts[:2] == ["src-tauri", "target"]
            if in_build:
                build_entries.append([relative, _signature(info)])
                protected = any(part in PROTECTED_DIRS for part in parts[2:])
                escaped = False
                if stat.S_ISLNK(info.st_mode):
                    try:
                        build_root = os.path.join(root, "src-tauri", "target")
                        escaped = os.path.commonpath([build_root, os.path.realpath(entry.path)]) != build_root
                        build_entries[-1].append(os.readlink(entry.path))
                    except (OSError, ValueError):
                        escaped = True
                if protected or escaped:
                    build_blockers.append(relative)
            if stat.S_ISLNK(info.st_mode):
                skipped_links += 1
                continue
            if stat.S_ISDIR(info.st_mode):
                stack.append((entry.path, parts))
                continue
            if not stat.S_ISREG(info.st_mode):
                continue
            category = _category(parts, developer)
            totals[category]["bytes"] += info.st_size
            totals[category]["files"] += 1
            if category == "python_cache" and info.st_nlink == 1:
                caches.append([relative, _signature(info)])
    caches.sort()
    build_entries.sort()
    root_identity = [root, os.stat(root).st_dev, os.stat(root).st_ino]
    return {"categories": totals, "total_bytes": sum(v["bytes"] for v in totals.values()),
            "total_files": sum(v["files"] for v in totals.values()),
            "cache_files": caches, "cache_bytes": sum(row[1][3] for row in caches),
            "cache_token": _token([root_identity, caches]),
            "build_token": _token([root_identity, build_entries]),
            "build_blockers": build_blockers,
            "developer_root": developer, "skipped_links": skipped_links,
            "unreadable": errors, "complete": not errors}


def clear_python_cache(root, expected_token):
    """Delete only unchanged single-link bytecode. Python regenerates it."""
    root = os.path.realpath(os.path.abspath(root))
    with _CLEAN_LOCK:
        report = inspect(root)
        if not report["complete"]:
            raise StorageError("Some files could not be inspected. Nothing was removed.")
        if report["cache_token"] != expected_token:
            raise StorageError("Caches changed after the preview. Refresh storage use.")
        checked = []
        for relative, signature in report["cache_files"]:
            try:
                path, info = _plain_path(root, relative)
            except OSError as exc:
                raise StorageError("Caches changed after the preview. Refresh storage use.") from exc
            if _signature(info) != signature:
                raise StorageError("Caches changed after the preview. Refresh storage use.")
            checked.append((relative, path, signature))
        removed, removed_bytes = 0, 0
        for relative, path, signature in checked:
            try:
                current_path, info = _plain_path(root, relative)
                if current_path != path or _signature(info) != signature:
                    raise StorageError("A cache changed during cleanup.")
                os.unlink(path)
            except (OSError, StorageError):
                return {"removed_files": removed, "removed_bytes": removed_bytes,
                        "complete": False,
                        "notice": "Cleanup stopped because a cache changed or could not be removed. Refresh storage use."}
            removed += 1
            removed_bytes += signature[3]
        return {"removed_files": removed, "removed_bytes": removed_bytes,
                "complete": True, "notice": "Python rebuilds these caches when needed."}


def validate_build_cleanup(root, expected_token):
    """Keep developer-only build cleanup outside the learner HTTP surface."""
    root = os.path.realpath(os.path.abspath(root))
    report = inspect(root)
    if not report["developer_root"] or not report["complete"]:
        raise StorageError("Build cleanup requires a readable developer checkout.")
    if report["build_blockers"]:
        raise StorageError("Build output contains escaping links or protected data. Nothing was removed.")
    if report["build_token"] != expected_token:
        raise StorageError("Build output changed after the preview. Run the preview again.")
    try:
        tag, _ = _plain_path(root, "src-tauri/target/CACHEDIR.TAG")
        with open(tag, encoding="utf-8") as stream:
            marked = stream.readline().strip() == CACHE_TAG
    except (OSError, UnicodeError):
        marked = False
    if not marked:
        raise StorageError("The target directory lacks Cargo's cache marker. Nothing was removed.")
    return os.path.join(root, "src-tauri", "Cargo.toml"), os.path.join(root, "src-tauri", "target")


def size_label(amount):
    value = float(amount)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return "%s %s" % (str(int(value)) if unit == "B" else "%.1f" % value, unit)
        value /= 1024


def cmd_storage(args):
    """The same inventory and bytecode cleanup used by Settings."""
    try:
        if args.clear_python_cache:
            if not args.expected:
                raise StorageError("Cleanup requires --expected with the preview's cache_token.")
            result = clear_python_cache(args.base, args.expected)
        else:
            result = inspect(args.base)
        print(json.dumps(result, indent=2))
        return 0 if result["complete"] else 1
    except StorageError as exc:
        print(str(exc), file=sys.stderr)
        return 1


def page(report, theme_css="", notice=""):
    from surfaces import presentation
    esc = presentation.esc
    rows = "".join('<tr><th scope="row">%s</th><td>%s</td><td>%d</td></tr>' %
                   (esc(label), size_label(report["categories"][key]["bytes"]),
                    report["categories"][key]["files"]) for key, label in CATEGORIES.items()
                   if report["developer_root"] or key not in ("build", "release", "git"))
    status = '<p role="status">%s</p>' % esc(notice) if notice else ""
    warning = ('<p role="status">Some locations could not be read. Totals are partial and cleanup is unavailable.</p>'
               if not report["complete"] else "")
    cleanup = '<p>No eligible Python caches to clear.</p>'
    if report["cache_files"] and report["complete"]:
        cleanup = ('<form method="post" action="/settings/storage">'
                   '<input type="hidden" name="cache_token" value="%s">'
                   '<button class="go" type="submit">Clear %s of Python caches</button>'
                   '</form><p>Python recreates these files when needed. The next load may take longer.</p>' %
                   (esc(report["cache_token"]), size_label(report["cache_bytes"])))
    body = ('%s%s<p>%s in %d files in this workspace.</p>'
            '<p>Sizes are file bytes. Linked folders are excluded. %d links were skipped.</p>'
            '<table class="storage-usage"><caption>Workspace storage</caption><thead><tr><th scope="col">Category</th>'
            '<th scope="col">Size</th><th scope="col">Files</th></tr></thead><tbody>%s</tbody></table>'
            '<h2>Clear rebuildable caches</h2>%s'
            '<p>Courses, sources, downloaded snapshots, notes, attempts, journals, and release files are preserved.</p>'
            '<p><a href="/settings/storage">Refresh storage use</a></p>' %
            (status, warning, size_label(report["total_bytes"]), report["total_files"],
             report["skipped_links"], rows, cleanup))
    return presentation.surface_shell("Storage use", body, theme_css=theme_css,
                                      back={"href": "/settings", "label": "Settings"},
                                      extra_css=".storage-usage td,.storage-usage th:not(:first-child){white-space:nowrap}")
