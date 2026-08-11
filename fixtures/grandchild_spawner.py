#!/usr/bin/env python3
"""A synthetic process-tree kill fixture (plan 05-02 Task 3).

Spawns one child that writes a heartbeat line to a path roughly ten times a
second, then hangs forever itself. The child does not start its own session or
process group -- it inherits the group (POSIX) or job (Windows) the runner made
for the direct process, which is what makes a tree-wide kill reaching it
evidence about depth rather than about the direct process.

The heartbeat path comes from argv[1] when this file is run directly, or from
the GRANDCHILD_HEARTBEAT env var when the runner executes this file as a check
submission (which sets no argv beyond the source path). No OS-specific branch:
only the runner branches, and this fixture proves the same thing on both.
"""
import os, subprocess, sys, time

# The heartbeat writer: appends a timestamp line and flushes, forever.
GRANDCHILD = (
    "import sys, time\n"
    "with open(sys.argv[1], 'a') as fh:\n"
    "    while True:\n"
    "        fh.write(str(time.time()) + chr(10)); fh.flush(); time.sleep(0.1)\n"
)

HEARTBEAT = (os.environ.get("GRANDCHILD_HEARTBEAT")
             or (sys.argv[1] if len(sys.argv) > 1 else None))


def main():
    if HEARTBEAT in ("--help", "-h"):
        print("usage: grandchild_spawner.py <heartbeat_path>")
        return 0
    if not HEARTBEAT:
        print("usage: grandchild_spawner.py <heartbeat_path>", file=sys.stderr)
        return 1
    subprocess.Popen([sys.executable, "-c", GRANDCHILD, HEARTBEAT])
    while True:
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
