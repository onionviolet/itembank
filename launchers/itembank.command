#!/bin/bash
# macOS double-click shim. Resolves its own directory from $0 so a launch
# from Finder finds itembank.pyz beside it regardless of Finder's own
# working directory, probes for Python 3.11+, and holds the Terminal
# window open on failure so the message is actually readable.
cd "$(dirname "$0")" || exit 1
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "itembank needs Python 3.11 or newer. Install it from https://python.org and run this file again."
    read -p "Press Enter to close..."
    exit 1
fi
exec python3 itembank.pyz "$@"
