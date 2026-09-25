#!/usr/bin/env python3
"""Classification cache behavior with disposable roots and real parsers."""

from concurrent.futures import ThreadPoolExecutor
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from model import parse_bank
from surfaces.day import parse_plan
from surfaces.discovery_cache import DiscoveryCache


BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def run():
    with tempfile.TemporaryDirectory(prefix="itembank-discovery-cache-") as root:
        bank_text = open(BANK, encoding="utf-8").read()
        calls = {"bank": 0, "plan": 0}

        def counted_bank(text):
            calls["bank"] += 1
            return parse_bank(text)

        def counted_plan(path, year):
            calls["plan"] += 1
            return parse_plan(path, year)

        cache = DiscoveryCache(max_roots=2, max_entries_per_root=128)

        def classify(path, year=2026, allowed=None):
            with cache.scan(root) as scan:
                return scan.classify(path, allowed or root, year,
                                     counted_bank, counted_plan)

        path = os.path.join(root, "one.md")
        with open(path, "w", encoding="utf-8") as target:
            target.write(bank_text)
        assert classify(path) == "bank"
        assert classify(path) == "bank"
        assert calls == {"bank": 1, "plan": 0}, calls

        # A same-length edit with its mtime restored still changes ctime.
        before = os.stat(path)
        with open(path, "r+", encoding="utf-8") as target:
            target.seek(0)
            target.write("X" + bank_text[1:])
            target.truncate()
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        assert classify(path) == "bank"
        assert calls["bank"] == 2

        # Atomic replacement changes inode even if size and mtime are copied.
        replacement = os.path.join(root, "replacement.tmp")
        with open(replacement, "w", encoding="utf-8") as target:
            target.write(bank_text)
        os.utime(replacement, ns=(before.st_atime_ns, before.st_mtime_ns))
        os.replace(replacement, path)
        assert classify(path) == "bank"
        assert calls["bank"] == 3

        plan = os.path.join(root, "plan.md")
        with open(plan, "w", encoding="utf-8") as target:
            target.write("| Date | EMT |\n| --- | --- |\n| Sep 25 | Read |\n")
        assert classify(plan, 2026) == "plan"
        assert classify(plan, 2026) == "plan"
        assert calls["plan"] == 1
        assert classify(plan, 2027) == "plan"
        assert calls["plan"] == 2

        # Each completed scan evicts files no longer seen, including removals.
        os.unlink(plan)
        with cache.scan(root) as scan:
            assert scan.classify(path, root, 2026, counted_bank,
                                 counted_plan) == "bank"
        assert cache.counts()[root] == 1
        os.rename(path, os.path.join(root, "renamed.md"))
        with cache.scan(root) as scan:
            renamed = os.path.join(root, "renamed.md")
            assert scan.classify(renamed, root, 2026, counted_bank,
                                 counted_plan) == "bank"
        assert cache.counts()[root] == 1

        outside = os.path.join(os.path.dirname(root), "itembank-cache-outside-%d.md" % os.getpid())
        try:
            with open(outside, "w", encoding="utf-8") as target:
                target.write(bank_text)
            link = os.path.join(root, "link.md")
            os.symlink(renamed, link)
            with cache.scan(root) as scan:
                assert scan.classify(link, root, 2026, counted_bank,
                                     counted_plan) == "bank"
            os.unlink(link)
            os.symlink(outside, link)
            before_calls = dict(calls)
            with cache.scan(root) as scan:
                assert scan.classify(link, root, 2026, counted_bank,
                                     counted_plan) is None
            assert calls == before_calls
        finally:
            if os.path.exists(outside):
                os.unlink(outside)

        unreadable = os.path.join(root, "bad.md")
        with open(unreadable, "wb") as target:
            target.write(b"\xff")
        with cache.scan(root) as scan:
            assert scan.classify(unreadable, root, 2026, counted_bank,
                                 counted_plan) is None
        with open(unreadable, "w", encoding="utf-8") as target:
            target.write(bank_text)
        with cache.scan(root) as scan:
            assert scan.classify(unreadable, root, 2026, counted_bank,
                                 counted_plan) == "bank"

        # Per-root cap and concurrent callers stay bounded and race-free.
        small = DiscoveryCache(max_roots=1, max_entries_per_root=2)
        copies = []
        for i in range(3):
            copy = os.path.join(root, "copy-%d.md" % i)
            shutil.copyfile(BANK, copy)
            copies.append(copy)

        def scan_copies(_):
            with small.scan(root) as scan:
                return [scan.classify(copy, root, 2026, parse_bank, parse_plan)
                        for copy in copies]

        with ThreadPoolExecutor(max_workers=8) as pool:
            for result in pool.map(scan_copies, range(24)):
                assert result == ["bank"] * 3
        assert small.counts()[root] == 2

        # The benchmark is diagnostic, not a timing assertion.
        bench = DiscoveryCache(max_entries_per_root=128)
        bench_calls = [0]

        def bench_bank(text):
            bench_calls[0] += 1
            return parse_bank(text)

        bench_files = []
        for i in range(100):
            copy = os.path.join(root, "bench-%03d.md" % i)
            shutil.copyfile(BANK, copy)
            bench_files.append(copy)

        def bench_scan():
            with bench.scan(root) as scan:
                return [scan.classify(copy, root, 2026, bench_bank, parse_plan)
                        for copy in bench_files]

        start = time.perf_counter()
        assert bench_scan() == ["bank"] * 100
        cold = time.perf_counter() - start
        start = time.perf_counter()
        assert bench_scan() == ["bank"] * 100
        warm = time.perf_counter() - start
        assert bench_calls[0] == 100
        print("ok - 100 banks cold %.3fs, warm %.3fs, parser calls %d/%d" %
              (cold, warm, 100, bench_calls[0] - 100))


if __name__ == "__main__":
    run()
