#!/usr/bin/env bash
# Run 17A-07 then 17A-08 unattended against Ox Alpha on OpenRouter.
#
# Tool config, not product config. Nothing here is imported by itembank.
#
# Usage:
#   export OPENROUTER_API_KEY=...        # your key, never stored in this repo
#   scripts/ox_overnight.sh              # both plans
#   scripts/ox_overnight.sh 17A-07       # one plan
#
# Written 2026-08-22. The free Ox Alpha preview ends 2026-08-27.

set -u -o pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DSH="$REPO/deps/dsh/node_modules/.bin/dsh"
PATCH="$HOME/.dsh/ox-alpha.patch.yml"
PROMPT="$REPO/.planning/PROMPT-ox-17A-overnight-2026-08-22.md"
LOGDIR="$REPO/.planning/_ox-logs"
STAMP="$(date +%Y%m%d-%H%M%S)"
read -r -a PLANS <<< "${*:-17A-07 17A-08}"

fail() { echo "ox_overnight: $*" >&2; exit 1; }

[ -n "${OPENROUTER_API_KEY:-}" ] || fail "OPENROUTER_API_KEY is not set. Export it, then rerun."
[ -x "$DSH" ] || fail "dsh not installed. Run: cd deps/dsh && npm ci"
[ -f "$PATCH" ] || fail "missing $PATCH"
[ -f "$PROMPT" ] || fail "missing $PROMPT"
mkdir -p "$LOGDIR"

# Smoke test before committing a night to it. Catches a bad key, a rate limit,
# and a retired preview, all of which look identical from inside a long run.
echo "ox_overnight: smoke testing stealth/ox-alpha"
SMOKE="$(curl -sS -o /dev/null -w '%{http_code}' \
  -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"stealth/ox-alpha","max_tokens":8,"messages":[{"role":"user","content":"say ok"}]}')"
case "$SMOKE" in
  200) echo "ox_overnight: smoke ok" ;;
  401|403) fail "auth rejected (HTTP $SMOKE). Check the key." ;;
  404)     fail "model not found (HTTP $SMOKE). The preview may have ended." ;;
  429)     fail "rate limited (HTTP $SMOKE) on the very first request. Do not start a night on this." ;;
  *)       fail "unexpected HTTP $SMOKE from OpenRouter." ;;
esac

cd "$REPO" || fail "cannot enter $REPO"
git rev-parse --abbrev-ref HEAD | grep -qx main || echo "ox_overnight: WARNING, not on main"

for PLAN in "${PLANS[@]}"; do
  LOG="$LOGDIR/$STAMP-$PLAN.log"
  echo "ox_overnight: starting $PLAN, logging to $LOG"
  TASK="$(sed "s/<PLAN_ID>/$PLAN/g" "$PROMPT")"
  "$DSH" --profile headless --patch "$PATCH" "$TASK" 2>&1 | tee "$LOG"
  echo "ox_overnight: $PLAN exited with ${PIPESTATUS[0]}" | tee -a "$LOG"
  echo "ox_overnight: commits since start:" | tee -a "$LOG"
  git log --oneline -5 | tee -a "$LOG"
done

echo "ox_overnight: done. Read $LOGDIR/$STAMP-*.log and git log before trusting anything."
