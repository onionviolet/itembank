#!/usr/bin/env bash
# Run 17A-07 then 17A-08 unattended against Ox Alpha on OpenRouter.
#
# Tool config, not product config. Nothing here is imported by itembank.
#
# Usage:
#   export OPENROUTER_API_KEY=...        # per-run override, or save it once in
#                                        # ~/.dsh/.credentials.yaml and skip this.
#                                        # Never stored in this repo either way.
#   scripts/ox_overnight.sh              # both plans, in this checkout
#   scripts/ox_overnight.sh 17A-07       # one plan
#   IB_DIR=~/dev/IB-17A-03 scripts/ox_overnight.sh 17A-03    # in a worktree
#   scripts/ox_overnight.sh 13.9-01 13.9-02 17A-03           # spans phases; the
#                                                            # prompt is chosen
#                                                            # per plan id
#   IB_FORCE=1 scripts/ox_overnight.sh 13.9-01 13.9-02       # deliberate re-run
#
# A plan that already has non-planning commits is skipped, because one session
# can run past its own plan into the next one and a queued invocation would then
# redo finished work. A deliberate re-run needs IB_FORCE=1: the 13.9 rebuild is
# exactly that case, since 13.9-01 carries a commit from the Windows execution
# whose output is now unreachable.
#
# Run two plans concurrently ONLY from separate worktrees, and only when their
# plans' files_modified sets do not intersect. 17A-03 and 17A-07 both write
# surfaces/visual_fixture.py, so that pair must never overlap.
#
# Written 2026-08-22. The free Ox Alpha preview ends 2026-08-27.

set -u -o pipefail

SELF_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${IB_DIR:-$SELF_REPO}"
REPO="$(cd "$REPO" 2>/dev/null && pwd)" || { echo "ox_overnight: IB_DIR is not a directory" >&2; exit 1; }
DSH="$SELF_REPO/deps/dsh/node_modules/.bin/dsh"   # one install serves every worktree
PATCH="$HOME/.dsh/ox-alpha.patch.yml"
# Prompt is chosen per plan, so one queue can span phases. IB_PROMPT overrides.
prompt_for() {
  case "$1" in
    13.9-*) echo "PROMPT-ox-13.9-rebuild-2026-08-22.md" ;;
    *)      echo "PROMPT-ox-17A-overnight-2026-08-22.md" ;;
  esac
}
LOGDIR="$REPO/.planning/_ox-logs"
STAMP="$(date +%Y%m%d-%H%M%S)"
read -r -a PLANS <<< "${*:-17A-07 17A-08}"

fail() { echo "ox_overnight: $*" >&2; exit 1; }

# Key resolution, in dsh's own precedence order: the launching environment wins,
# then the managed credentials document. Saving it in the document means no
# export is needed and the key never sits in shell history.
CREDS="$HOME/.dsh/.credentials.yaml"
if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -f "$CREDS" ]; then
  OPENROUTER_API_KEY="$(sed -n 's/^OPENROUTER_API_KEY:[[:space:]]*//p' "$CREDS" | head -1 | tr -d '"'"'"' \r')"
fi
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  fail "no key. Either export OPENROUTER_API_KEY, or put it in $CREDS as: OPENROUTER_API_KEY: sk-or-..."
fi
[ -x "$DSH" ] || fail "dsh not installed. Run: cd deps/dsh && npm ci"
[ -f "$PATCH" ] || fail "missing $PATCH"
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
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "ox_overnight: tree $REPO on branch $BRANCH"

for PLAN in "${PLANS[@]}"; do
  if [ -n "${IB_PROMPT:-}" ]; then PROMPT="$IB_PROMPT"; else PROMPT="$REPO/.planning/$(prompt_for "$PLAN")"; fi
  [ -f "$PROMPT" ] || PROMPT="$SELF_REPO/.planning/$(basename "$PROMPT")"
  [ -f "$PROMPT" ] || fail "no prompt file for $PLAN"
  # Skip a plan another session already executed. The 17A-07 run continued
  # into 17A-08 inside one session, so a queued invocation would redo it.
  if [ -z "${IB_FORCE:-}" ] && git log --oneline --grep="($PLAN)" | grep -qv "^[0-9a-f]* docs($PLAN): plan"; then
    echo "ox_overnight: $PLAN already has commits, skipping. IB_FORCE=1 to run anyway."
    continue
  fi
  LOG="$LOGDIR/$STAMP-$PLAN.log"
  echo "ox_overnight: starting $PLAN in $REPO with $(basename "$PROMPT"), logging to $LOG"
  TASK="$(sed -e "s/<PLAN_ID>/$PLAN/g" -e "s#/Users/weiwei/Documents/Dev/itembank#$REPO#g" "$PROMPT")"
  "$DSH" --profile headless --patch "$PATCH" "$TASK" 2>&1 | tee "$LOG"
  echo "ox_overnight: $PLAN exited with ${PIPESTATUS[0]}" | tee -a "$LOG"
  echo "ox_overnight: commits since start:" | tee -a "$LOG"
  git log --oneline -5 | tee -a "$LOG"
done

echo "ox_overnight: done. Read $LOGDIR/$STAMP-*.log and git log before trusting anything."
