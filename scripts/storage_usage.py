#!/usr/bin/env python3
"""Preview storage use, then explicitly clear bytecode or Cargo build output."""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import storage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=ROOT, help="workspace or developer checkout to inspect")
    parser.add_argument("--json", action="store_true", help="print the preview as JSON")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--clear-python-cache", action="store_true")
    action.add_argument("--clean-build", action="store_true")
    parser.add_argument("--expected", help="matching cache_token or build_token from a fresh preview")
    args = parser.parse_args()
    root = os.path.realpath(os.path.abspath(args.root))
    try:
        if args.clear_python_cache or args.clean_build:
            if not args.expected:
                parser.error("cleanup requires --expected from a fresh preview")
            if args.clear_python_cache:
                result = storage.clear_python_cache(root, args.expected)
                print(json.dumps(result, indent=2))
                return 0 if result["complete"] else 1
            manifest, target = storage.validate_build_cleanup(root, args.expected)
            cargo = shutil.which("cargo")
            if cargo is None:
                raise storage.StorageError("Cargo is unavailable. Build output was preserved.")
            # Cargo owns build locking and removal. Never remove its target by hand.
            return subprocess.run([cargo, "clean", "--offline", "--manifest-path", manifest,
                                   "--target-dir", target], cwd=root).returncode
        report = storage.inspect(root)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for key, label in storage.CATEGORIES.items():
                print("%9s  %s" % (storage.size_label(report["categories"][key]["bytes"]), label))
            print("\nFile bytes, excluding links. No files changed.")
            print("cache_token: " + report["cache_token"])
            if report["developer_root"]:
                print("build_token: " + report["build_token"])
            print("Use --clear-python-cache or --clean-build with --expected TOKEN to clean.")
            print("Deleted caches and build output are recovered by rebuilding. Release files are preserved.")
            if not report["complete"]:
                print("Some locations were unreadable. Totals are partial.")
        return 0 if report["complete"] else 1
    except storage.StorageError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
