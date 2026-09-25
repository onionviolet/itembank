#!/usr/bin/env python3
"""Storage accounting and explicit cleanup preserve learner-owned records."""
import os
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import storage


def put(root, relative, value=b"synthetic"):
    path = pathlib.Path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    return path


def expect_refusal(operation):
    try:
        operation()
    except storage.StorageError:
        return
    raise AssertionError("unsafe or stale cleanup was accepted")


def check_accounting_and_cleanup():
    with tempfile.TemporaryDirectory() as root:
        preserved = [put(root, name, b"keep") for name in (
            "course.md", "_sources/cache/snapshot.html", "_notes/note.md",
            "_attempts/sitting.json", "_evidence/events.jsonl",
            "_journal/before/old.bin", "__pycache__/human.md",
            "_journal/__pycache__/history.pyc", "_sources/__pycache__/source.pyc")]
        cache = put(root, "package/__pycache__/module.cpython-314.pyc", b"bytecode")
        report = storage.inspect(root)
        assert report["complete"]
        assert report["total_bytes"] == 4 * len(preserved) + 8
        assert report["cache_bytes"] == 8
        assert report["categories"]["evidence"]["bytes"] == 8
        assert report["categories"]["recovery"]["bytes"] == 8
        result = storage.clear_python_cache(root, report["cache_token"])
        assert result["complete"] and result["removed_bytes"] == 8
        assert not cache.exists()
        assert all(path.read_bytes() == b"keep" for path in preserved)
        assert storage.inspect(root)["cache_bytes"] == 0
        html = storage.page(storage.inspect(root))
        assert html.count("<h1>") == 1
        assert 'href="/settings"' in html
        assert 'href="/settings" aria-current="page"' in html
        assert "Rust build output" not in html
        assert "No eligible Python caches" in html


def check_stale_and_links():
    with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
        cache = put(root, "pkg/__pycache__/a.pyc", b"old")
        token = storage.inspect(root)["cache_token"]
        cache.write_bytes(b"new")
        expect_refusal(lambda: storage.clear_python_cache(root, token))
        assert cache.exists()
        victim = put(outside, "victim.pyc", b"keep")
        token = storage.inspect(root)["cache_token"]
        cache.unlink()
        try:
            cache.symlink_to(victim)
            pathlib.Path(root, "linked-directory").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            return
        report = storage.inspect(root)
        assert report["skipped_links"] == 2 and report["cache_bytes"] == 0
        expect_refusal(lambda: storage.clear_python_cache(root, token))
        assert victim.read_bytes() == b"keep"
        cache.unlink()
        os.link(victim, cache)
        report = storage.inspect(root)
        assert report["cache_bytes"] == 0, "hard links must be excluded from cleanup"
        storage.clear_python_cache(root, report["cache_token"])
        assert cache.exists() and victim.read_bytes() == b"keep"


def check_partial_failure():
    with tempfile.TemporaryDirectory() as root:
        put(root, "__pycache__/a.pyc")
        put(root, "__pycache__/b.pyc")
        report = storage.inspect(root)
        original = os.unlink
        calls = []

        def fail_second(path):
            calls.append(path)
            if len(calls) == 2:
                raise PermissionError("synthetic")
            original(path)

        with mock.patch.object(storage.os, "unlink", side_effect=fail_second):
            result = storage.clear_python_cache(root, report["cache_token"])
        assert not result["complete"] and result["removed_files"] == 1
        assert storage.inspect(root)["categories"]["python_cache"]["files"] == 1


def check_developer_cleanup_boundary():
    with tempfile.TemporaryDirectory() as root:
        put(root, "build.py")
        put(root, "src-tauri/Cargo.toml")
        put(root, "src-tauri/target/release/deps/synthetic.rlib", b"compiled")
        put(root, "dist/itembank.pyz", b"release")
        report = storage.inspect(root)
        assert report["developer_root"]
        assert report["categories"]["build"]["bytes"] == 8
        assert report["categories"]["release"]["bytes"] == 7
        expect_refusal(lambda: storage.validate_build_cleanup(root, report["build_token"]))
        put(root, "src-tauri/target/CACHEDIR.TAG", (storage.CACHE_TAG + "\n").encode())
        report = storage.inspect(root)
        manifest, target = storage.validate_build_cleanup(root, report["build_token"])
        assert target == os.path.realpath(os.path.join(root, "src-tauri", "target"))
        assert manifest.endswith("Cargo.toml")
        put(root, "src-tauri/target/new-output", b"new")
        expect_refusal(lambda: storage.validate_build_cleanup(root, report["build_token"]))
        command = [sys.executable, os.path.join(ROOT, "scripts", "storage_usage.py"), "--root", root]
        preview = subprocess.run(command, capture_output=True, text=True)
        assert preview.returncode == 0 and "No files changed" in preview.stdout
        refused = subprocess.run(command + ["--clean-build"], capture_output=True, text=True)
        assert refused.returncode != 0 and "--expected" in refused.stderr
        assert pathlib.Path(target, "new-output").exists()
        protected = put(root, "src-tauri/target/_attempts/sitting.json", b"keep")
        report = storage.inspect(root)
        expect_refusal(lambda: storage.validate_build_cleanup(root, report["build_token"]))
        assert protected.read_bytes() == b"keep"
        protected.unlink()
        protected.parent.rmdir()
        report = storage.inspect(root)
        link = pathlib.Path(target, "linked")
        try:
            link.symlink_to(pathlib.Path(root, "dist"), target_is_directory=True)
        except (OSError, NotImplementedError):
            return
        expect_refusal(lambda: storage.validate_build_cleanup(root, report["build_token"]))
        current = storage.inspect(root)
        assert current["build_token"] != report["build_token"]
        expect_refusal(lambda: storage.validate_build_cleanup(root, current["build_token"]))
        link.unlink()
        link.symlink_to(pathlib.Path(target, "release"), target_is_directory=True)
        current = storage.inspect(root)
        assert not current["build_blockers"], "contained bundle links do not widen deletion"
        storage.validate_build_cleanup(root, current["build_token"])


def check_http_and_cli():
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    from daemon_roundtrip import start_daemon, get
    with tempfile.TemporaryDirectory() as root:
        keep = put(root, "_sources/cache/accepted.txt", b"keep")
        cache = put(root, "__pycache__/synthetic.pyc", b"bytecode")
        proc, url, _lines = start_daemon(root)
        try:
            status, body = get(url + "settings")
            assert status == 200 and 'href="/settings/storage"' in body
            status, body = get(url + "settings/storage")
            assert status == 200 and '<h1>Storage use</h1>' in body
            token = re.search(r'name="cache_token" value="([a-f0-9]{64})"', body).group(1)

            def post(value, origin=None):
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                if origin:
                    headers["Origin"] = origin
                request = urllib.request.Request(url + "settings/storage", headers=headers,
                    data=urllib.parse.urlencode({"cache_token": value}).encode())
                try:
                    with urllib.request.urlopen(request) as response:
                        return response.status, response.read().decode()
                except urllib.error.HTTPError as exc:
                    return exc.code, exc.read().decode()

            status, _body = post(token, "https://foreign.example")
            assert status == 403 and cache.exists()
            cache.write_bytes(b"changed")
            status, _body = post(token)
            assert status == 409 and cache.exists()
            result = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                                     "storage", "--base", root], capture_output=True, text=True)
            assert result.returncode == 0
            token = json.loads(result.stdout)["cache_token"]
            status, body = post(token)
            assert status == 200 and "Removed 1 cache file" in body
            assert not cache.exists() and keep.read_bytes() == b"keep"
            status, _body = post(token)
            assert status == 409, "stale form must not silently authorize another cleanup"
        finally:
            proc.terminate()
            proc.wait(timeout=5)


if __name__ == "__main__":
    for check in (check_accounting_and_cleanup, check_stale_and_links,
                  check_partial_failure, check_developer_cleanup_boundary, check_http_and_cli):
        check()
        print("ok - " + check.__name__)
