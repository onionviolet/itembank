"""Bounded, process-local classification cache for daemon discovery.

The caller still walks and checks every candidate on every scan. This cache
only avoids repeating the existing bank and day-plan parsers for an unchanged
regular file. It stores no parsed content or assessment keys.
"""

from collections import OrderedDict
from contextlib import contextmanager
import os
import stat
import threading


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _inside(real, allowed_real):
    try:
        return os.path.commonpath((real, allowed_real)) == allowed_real
    except ValueError:
        return False


class _Scan:
    def __init__(self, cache, root):
        self.cache = cache
        self.root = root
        self.seen = set()

    def classify(self, path, allowed_real, year, parse_bank, parse_plan):
        """Return 'bank', 'plan', or None after rechecking containment.

        Both parsers are supplied by the daemon, so its parser authority stays
        unchanged. Unreadable and unstable files are skipped without caching.
        """
        allowed_real = os.path.realpath(allowed_real)
        entries = self.cache._roots[self.root]
        for _attempt in range(3):
            real = os.path.realpath(path)
            if not _inside(real, allowed_real):
                entries.pop(real, None)
                return None
            try:
                before = os.stat(path)
            except OSError:
                entries.pop(real, None)
                return None
            if not stat.S_ISREG(before.st_mode):
                entries.pop(real, None)
                return None
            self.seen.add(real)
            identity = _identity(before)
            cached = entries.get(real)
            if cached is not None and cached[:2] == (identity, year):
                # A path may have been redirected since the first realpath.
                if os.path.realpath(path) == real:
                    try:
                        after = os.stat(path)
                    except OSError:
                        continue
                    if _identity(after) == identity:
                        entries.move_to_end(real)
                        return cached[2]
                continue
            try:
                with open(path, encoding="utf-8") as source:
                    text = source.read()
                if parse_bank(text):
                    kind = "bank"
                elif parse_plan(path, year):
                    kind = "plan"
                else:
                    kind = None
            except (OSError, UnicodeError):
                entries.pop(real, None)
                return None
            try:
                after = os.stat(path)
            except OSError:
                entries.pop(real, None)
                continue
            if os.path.realpath(path) != real or _identity(after) != identity:
                entries.pop(real, None)
                continue
            entries[real] = (identity, year, kind)
            entries.move_to_end(real)
            while len(entries) > self.cache.max_entries_per_root:
                entries.popitem(last=False)
            return kind
        return None


class DiscoveryCache:
    """Serialize scans and retain at most ``max_roots * max_entries`` kinds."""

    def __init__(self, max_roots=8, max_entries_per_root=2048):
        if max_roots < 1 or max_entries_per_root < 1:
            raise ValueError("cache limits must be positive")
        self.max_roots = max_roots
        self.max_entries_per_root = max_entries_per_root
        self._roots = OrderedDict()
        self._lock = threading.RLock()

    @contextmanager
    def scan(self, root):
        """Use around one complete walk, including its classification loop.

        Entries missing from this walk are removed on exit. Concurrent scans
        share one lock so an older walk cannot prune a newer walk's results.
        """
        root = os.path.abspath(root)
        with self._lock:
            entries = self._roots.setdefault(root, OrderedDict())
            self._roots.move_to_end(root)
            while len(self._roots) > self.max_roots:
                self._roots.popitem(last=False)
            scan = _Scan(self, root)
            try:
                yield scan
            finally:
                for real in list(entries):
                    if real not in scan.seen:
                        del entries[real]

    def counts(self):
        """Return bounded cache occupancy for diagnostics and tests."""
        with self._lock:
            return {root: len(entries) for root, entries in self._roots.items()}
