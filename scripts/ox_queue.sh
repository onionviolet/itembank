#!/usr/bin/env bash
# Wait for any in-flight dsh run to finish, then start another.
#
# Two agents in one working tree contend for the git index and can commit each
# other's half-written files. Queuing is the cheap answer when the two jobs are
# not urgent; a worktree (IB_DIR) is the answer when they are.
#
# Usage:
#   export OPENROUTER_API_KEY=...
#   IB_PROMPT=.planning/PROMPT-ox-13.9-rebuild-2026-08-22.md \
#     scripts/ox_queue.sh 13.9-01 13.9-02

set -u -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ -n "${OPENROUTER_API_KEY:-}" ] || { echo "ox_queue: OPENROUTER_API_KEY is not set" >&2; exit 1; }

waited=0
while pgrep -f "dsh --profile headless" >/dev/null 2>&1; do
  if [ "$waited" -eq 0 ]; then
    echo "ox_queue: a run is in flight, waiting for it to finish"
  fi
  sleep 60
  waited=$((waited + 1))
  if [ $((waited % 15)) -eq 0 ]; then
    echo "ox_queue: still waiting, ${waited} minutes"
  fi
done

echo "ox_queue: tree is clear after ${waited} minutes, starting"
exec "$HERE/ox_overnight.sh" "$@"
