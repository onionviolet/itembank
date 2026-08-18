"""The synthetic multi-root corpus 14A's discovery walker and identity
kernel are proven against.

`build_corpus(dest, size)` builds three sibling roots under `dest`, filled
with fictional Markdown, and returns a dict describing what it built,
including whether it could create symlinks on this platform and which mode
its permission-denied pocket used. Every file's content is generated from a
fixed seed and names no real course, book, or learner: this is the only
source of 14A test data (project content rule), and it lives in temp
directories at test time so `python itembank.py guard .` never sees it.

`teardown_corpus(dest)` restores write permissions on every path before
removing `dest`, so `shutil.rmtree` succeeds even where a path was made
read-only.
"""
import os
import random
import shutil
import stat

ROOTS = ("root_vault", "root_sources", "root_banks")
SIZES = {"1k": 1000, "10k": 10000}

_FILLER = (
    "This synthetic passage exists only to give the discovery walker "
    "something to read. It names no real course, book, or learner, and "
    "its content is generated from a fixed seed so a rebuild is "
    "byte-identical.",
    "The corpus generator repeats this paragraph with small variations "
    "so every file has plausible, fictional prose without needing a "
    "second author.",
)


def _file_body(n, rng):
    para1 = _FILLER[n % 2]
    para2 = _FILLER[(n + 1) % 2]
    return "# Synthetic file %04d\n\n%s\n\n%s\n" % (n, para1, para2)


def _relative_dirs(rng):
    # A short, deterministic set of nested subdirectory shapes so the tree
    # has real depth without every file landing directly in its root.
    shapes = [
        (), ("unit_01",), ("unit_02",), ("unit_03",), ("unit_04",),
        ("unit_04", "sub"), ("notes",), ("notes", "week_1"),
    ]
    return shapes[rng.randrange(len(shapes))]


def build_corpus(dest, size="1k"):
    if size not in SIZES:
        raise ValueError("size must be one of %s" % sorted(SIZES))
    total = SIZES[size]
    rng = random.Random(1400)  # fixed seed: a rebuild is byte-identical

    root_paths = {name: os.path.join(dest, name) for name in ROOTS}
    for p in root_paths.values():
        os.makedirs(p, exist_ok=True)

    per_root = total // len(ROOTS)
    counts = {name: per_root for name in ROOTS}
    counts[ROOTS[0]] += total - per_root * len(ROOTS)  # remainder to root 0

    n = 0
    for name in ROOTS:
        for _ in range(counts[name]):
            rel_dir = _relative_dirs(rng)
            d = os.path.join(root_paths[name], *rel_dir)
            os.makedirs(d, exist_ok=True)
            fname = "file_%04d.md" % n
            with open(os.path.join(d, fname), "w", encoding="utf-8") as fh:
                fh.write(_file_body(n, rng))
            n += 1

    result = {
        "dest": dest,
        "roots": [root_paths[name] for name in ROOTS],
        "root_paths": root_paths,
        "total_files": n,
        "symlinks": True,
        "denied_mode": "read",
    }

    # Duplicate-fingerprint pair: two files in different roots with
    # identical bytes.
    dup_body = "# Synthetic duplicate\n\nByte-identical content in two roots.\n"
    dup_a = os.path.join(root_paths["root_vault"], "duplicate_a.md")
    dup_b = os.path.join(root_paths["root_banks"], "duplicate_b.md")
    with open(dup_a, "w", encoding="utf-8") as fh:
        fh.write(dup_body)
    with open(dup_b, "w", encoding="utf-8") as fh:
        fh.write(dup_body)
    result["duplicate_pair"] = (dup_a, dup_b)

    # Near-identically-named pair that differs in bytes, for 14A-03's use.
    unit04 = os.path.join(root_paths["root_sources"], "unit_04")
    os.makedirs(unit04, exist_ok=True)
    notes_a = os.path.join(unit04, "notes.md")
    with open(notes_a, "w", encoding="utf-8") as fh:
        fh.write("# Notes A\n\nFirst version of these synthetic notes.\n")
    case_sensitive = not os.path.exists(os.path.join(unit04, "NOTES.md"))
    if case_sensitive:
        notes_b = os.path.join(unit04, "Notes.md")
    else:
        notes_b = os.path.join(unit04, "notes .md")
    with open(notes_b, "w", encoding="utf-8") as fh:
        fh.write("# Notes B\n\nSecond, differently-named version.\n")
    result["near_duplicate_pair"] = (notes_a, notes_b)

    # Symlink cycle and out-of-root symlink, both attempted with os.symlink.
    try:
        vault_sub = os.path.join(root_paths["root_vault"], "cycle_parent",
                                  "cycle_child")
        os.makedirs(vault_sub, exist_ok=True)
        cycle_link = os.path.join(vault_sub, "back_to_parent")
        os.symlink(os.path.join(root_paths["root_vault"], "cycle_parent"),
                    cycle_link, target_is_directory=True)

        outside_target = os.path.join(dest, "outside_all_roots.md")
        with open(outside_target, "w", encoding="utf-8") as fh:
            fh.write("# Outside every approved root\n\nDiscovery must never read this.\n")
        out_of_root_link = os.path.join(root_paths["root_sources"],
                                         "escapes_root.md")
        os.symlink(outside_target, out_of_root_link)
        result["symlinks"] = True
        result["cycle_link"] = cycle_link
        result["out_of_root_link"] = out_of_root_link
        result["outside_target"] = outside_target
    except (OSError, NotImplementedError, AttributeError):
        result["symlinks"] = False
        # Ordinary placeholder files in the symlinks' place, so the tree
        # shape is still exercised even where symlinks are unavailable.
        placeholder_dir = os.path.join(root_paths["root_vault"], "cycle_parent",
                                        "cycle_child")
        os.makedirs(placeholder_dir, exist_ok=True)
        with open(os.path.join(placeholder_dir, "back_to_parent.md"), "w",
                  encoding="utf-8") as fh:
            fh.write("# Symlinks unavailable on this platform\n\n"
                     "Placeholder standing in for a symlink cycle.\n")
        with open(os.path.join(root_paths["root_sources"], "escapes_root.md"),
                  "w", encoding="utf-8") as fh:
            fh.write("# Symlinks unavailable on this platform\n\n"
                     "Placeholder standing in for an out-of-root symlink.\n")

    # Permission-denied pocket.
    private_dir = os.path.join(root_paths["root_vault"], "private")
    os.makedirs(private_dir, exist_ok=True)
    denied_path = os.path.join(private_dir, "denied.md")
    with open(denied_path, "w", encoding="utf-8") as fh:
        fh.write("# Synthetic denied content\n\nThis file is made inaccessible.\n")
    if os.name == "nt":
        os.chmod(denied_path, stat.S_IREAD)
        result["denied_mode"] = "write"
    else:
        os.chmod(denied_path, 0o000)
        result["denied_mode"] = "read"
    result["denied_path"] = denied_path

    return result


def teardown_corpus(dest):
    """Restore write (and read) permissions on every path under `dest`
    before removing it, so a permission-denied pocket does not block
    `shutil.rmtree`."""
    for root, dirs, files in os.walk(dest):
        for d in dirs:
            p = os.path.join(root, d)
            try:
                os.chmod(p, stat.S_IRWXU)
            except OSError:
                pass
        for f in files:
            p = os.path.join(root, f)
            try:
                os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
            except OSError:
                pass
    try:
        os.chmod(dest, stat.S_IRWXU)
    except OSError:
        pass
    shutil.rmtree(dest, ignore_errors=True)
