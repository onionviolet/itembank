# Phase 18 Gates: the six-criterion A10 record

**Recorded:** 2026-09-01 · **Bar:** `READINESS-AUDIT-14A.md` section A10 ·
**Mechanics:** 18-CONTEXT D-05 · **Style:** every row carries evidence or an
explicit pending, per the Phase 13 house rule (an unexecuted row is never
marked done).

Executed under the standing directive of 2026-09-01: human tests are
deferred, so every agent-executable check below ran in full, and the two
human rows (the live signing answer, the second-person cold install) are
recorded as deferred and owed, never certified. Commands on this host ran as
`python3` (no `python` on PATH), the same deviation 18-01 and 18-02
recorded.

## Criterion 1: Install without folklore

> "Install without folklore. One downloaded artifact plus Python 3.11+, or
> the Phase 13 shell. The macOS Gatekeeper workaround is documented where
> the user hits it. V2-DEL-01's recorded trigger ('when a second person runs
> the tool') has now fired: signing gets a dated cost decision, not
> silence."

**Status: passed with one honestly recorded gap (rebuilt-on-this-host is
not achieved).**

- Check: the packaged artifact exists with recorded hashes and passing
  fixtures; the Gatekeeper and SmartScreen copy is documented at the point
  of use; the signing decision is dated.
- Evidence, shipped artifact (per 18-01-SUMMARY.md): the committed sidecar
  `src-tauri/binaries/itembank-sidecar-x86_64-pc-windows-msvc.exe`,
  2,580,996 bytes, SHA-256
  `8b019efd6b6db4b2f3fc3426c2b69d98411495154905aa44395316512ac9684e`, last
  built into the tree by commit `0b243c8` (2026-08-10, the Phase 13 build
  session). Fixture states on this host: `tests/packaging_roundtrip.py`
  exit 0 and `tests/packaging_shell_roundtrip.py` exit 0 (both with the
  honest not-built skips), `cargo test` exit 101 on the missing macOS
  sidecar triple.
- Recorded gap, stated plainly: 18-01 could not rebuild the artifact on
  this arm64 macOS host (no powershell or pwsh, Windows-wheel PyInstaller
  pin, no makensis, no aarch64 sidecar for the Tauri crate). A fresh
  rebuild-and-hash is owed on the Windows build machine that produced the
  Phase 13 artifact; the owner of that follow-up is Weibao (the build
  machine is his; recorded 18-01-SUMMARY.md, 2026-09-01). This row cites
  the shipped-artifact evidence in the interim and does not claim a
  rebuild happened.
- Gatekeeper: README Install section carries the right-click Open and
  `xattr -d com.apple.quarantine` fix at the macOS launch step.
  SmartScreen: README's release-download step (AI-assistant checklist step
  2) carries the More info / Run anyway walkthrough and the Get-FileHash
  verification instruction (landed 18-01).
- Signing: the dated cost decision (2026-09-01, quotes: Sectigo OV 219
  USD/yr, Comodo OV 219 USD/yr, DigiCert OV 400 USD/yr, Apple 99 USD/yr
  deferred with reason, decision: unsigned for v1 with documented
  workarounds) is recorded in 18-DECISIONS.md. The live checkpoint answer
  stays deferred to Weibao, as that entry states.
- Pointers: `18-01-SUMMARY.md`, `18-DECISIONS.md`, README "Install" and
  the AI-assistant checklist step 2.

## Criterion 2: Agent-guided onboarding

> "Agent-guided onboarding. The README carries a section a coding agent can
> follow cold: verify Python, fetch, launch, author a first bank from the
> user's own material, run a first graded sitting. The user's only skill is
> pasting the repo URL into Claude Code or a peer."

**Status: passed. Two runs, both kept; run 1 surfaced defects, the
defects became README fixes, and run 2 (a second cold agent against the
fixed copy) completed cleanly.**

- Check: a fresh agent session, given only the repository location and
  told to use nothing but README.md and capabilities.json, walks a
  simulated new user through verify-Python, fetch, launch, authoring a
  synthetic first bank, lint-until-clean, and a completed first graded
  sitting.
- Outcome: run 1 (2026-09-01) completed the walkthrough (7 synthetic
  items authored, lint 0 errors 0 warnings after fixes, a full JSON
  session sat, report 6 of 7 auto-correct with 1 pending short) and
  surfaced nine confusion points; run 2 (2026-09-01, after the README
  fixes) completed cleanly the same distance and confirmed the fixes
  held. Both verdicts: a newcomer agent can complete onboarding from the
  README alone.
- Evidence: `18-COLD-AGENT-TRANSCRIPT.md` (both transcripts verbatim and
  redacted; its header lists the eight README defects fixed and the
  three named defects routed onward as N-01 to N-03). Independently of
  the transcript, this plan's own fresh-install pass caught that the
  README's "whole format" sample did not parse (indented markers,
  single-line options, inline `[TYPE: short]`); the sample was replaced
  with a lint-clean file in the same README change, before run 1 read
  it.

## Criterion 3: First-run self-explanation

> "First-run self-explanation. A fresh launch shows something that explains
> itself (sample bank or walkthrough), not an empty directory."

**Status: passed on the served UI; packaged-artifact launch itself not
runnable on this host (same platform gap as criterion 1).**

- Check: launch the daemon against an empty directory and record what the
  first screen shows.
- Evidence, recorded 2026-09-01: `python3 itembank.py daemon <empty-dir>`
  served a Courses page whose visible first-screen text begins: "New here?
  A short walkthrough shows how a course works. Start walkthrough / Skip
  for now" followed by a bundled sample course "Study Skills Basics
  (Sample). For exploring itembank. Remove it anytime." Both the
  walkthrough and the sample-course controls state their CLI twin
  (`itembank shelf <action>`). Not an empty directory.
- Scope note: this exercised the browser-served UI, which per 18-CONTEXT
  D-01 is the single canonical shell the Phase 13 packaged app wraps
  (nothing chooses between shells; same served pages, one runtime). The
  packaged Windows shell itself cannot launch on this arm64 macOS host;
  its first-run observation folds into the deferred second-person cold
  install (row 7).

## Criterion 4: Scope honesty

> "Scope honesty. User-facing docs sell only the shipped bank/lesson/
> session loop. The course workspace is described as being built, never
> implied present."

**Status: passed.**

- Check: the exact D-06 copy landed under "Quick start for someone brand
  new" before the two paths, and a sweep of the quick-start, AI-assistant,
  and install sections found no sentence selling an unshipped course
  capability (the framing sections that already say "next milestone" or
  "being built" stay, as planned).
- Evidence: the README diff in this plan's commit; `python3 itembank.py
  guard .` exit 0; `python3 scripts/check_readme_commands.py` exit 0 (52
  registered commands, unchanged).

## Criterion 5: Privacy defaults hold for a stranger

> "Privacy defaults hold for a stranger. Fresh install never phones home
> without disclosure (the D-13 divergence stays repo-only), evidence stays
> on disk, and the update check discloses before its first request."

**Status: passed.**

- Staging: the repository tree (minus `.git`, minus `itembank.json`, minus
  `_attempts` and `.planning`) copied to a temp directory outside the
  repository; verified no `itembank.json` present.
- Monitoring method: a `sitecustomize.py` on `PYTHONPATH` wrapping
  `socket.socket.connect` and `socket.create_connection` to append every
  outbound connection attempt to a log (all stdlib network paths,
  `urllib` included, go through these). A second, blocking variant raised
  `OSError` on any non-loopback connect to simulate an unplugged network.
- Evidence, verbatim printed lines (2026-09-01):
  - `python3 itembank.py config` exit 0; its update_policy row:
    `update_policy  string  opt_in|check_on_launch  'opt_in'  'opt_in'  read by this phase`
    (DEFAULT and CURRENT both `opt_in`, resolved from the schema default
    with no settings file present).
  - `python3 itembank.py disclosure` exit 0, printing
    `"show": true, "notified_at": null` with the copy: "itembank will
    check GitHub for a new version at most once every 24 hours. Nothing
    but the request leaves this machine. Set \"update_policy\":
    \"opt_in\" in itembank.json to turn it off. This notice appears
    once." The notice has not been rendered and no update request has
    been made.
  - Monitor log after config, disclosure, `lint` of a synthetic bank, and
    a `serve` startup, one scored-page GET, and shutdown: empty. Zero
    connection attempts.
  - Blocked-network run (simulated unplugged): `lint` exit 0, `serve`
    startup and `GET /` 200, clean shutdown; blocked-attempt log empty.
    Degraded state proven by the same run: the loop worked with the
    network unplugged.
  - Explicit `python3 itembank.py update` under the block (the one
    user-initiated network command): prints "Could not reach GitHub to
    check for updates (offline, or the connection failed). Try again
    later." and exits 0; the log shows exactly one blocked attempt to
    GitHub, made only because the user ran the update command.
- D-13 divergence recorded: the repository's own checked-in
  `itembank.json` sets `check_on_launch` to dogfood the updater; that file
  is repo-only. A fresh install ships no such file, so `opt_in` holds for
  a stranger, exactly as `schemas/settings.schema.json` declares
  (default `opt_in`) and as the `check_on_daemon_launch` policy gate in
  `surfaces/update.py` enforces (a directory with no itembank.json
  returns at the policy gate before any request or notice exists).

## Criterion 6: Recovery

> "Recovery. Common failure states (wrong Python, port taken, quarantine
> flag, offline) name the next safe action in the error itself."

**Status: three of four states provoked and passing on this host; the
quarantine dialog and any packaged-artifact provocation fold into row 7
(same rebuilt-on-this-host gap as criterion 1, honestly recorded).**

- Wrong Python, provoked 2026-09-01 (a fake `python3` failing the version
  probe, launcher `launchers/itembank.command` run headless): prints
  "itembank needs Python 3.11 or newer. Install it from
  https://python.org and run this file again." and holds the window open.
  Names the next safe action. The `.bat` and `.desktop` shims carry the
  same copy.
- Port taken, provoked 2026-09-01 (a blocker bound to 127.0.0.1:8730,
  then `python3 itembank.py daemon .`): the daemon first probes
  `/__itembank__` on the occupier (so a second launch attaches to an
  existing itembank instead of erroring), then prints "port 8730
  unavailable (OSError), using a free one instead" and serves on a free
  port. The next safe action is taken automatically and said aloud.
- Offline, provoked 2026-09-01 (non-loopback connects blocked): the core
  loop runs unchanged (criterion 5 evidence), and explicit
  `python3 itembank.py update` prints "Could not reach GitHub to check
  for updates (offline, or the connection failed). Try again later." and
  exits 0. Names the state and the next safe action.
- Quarantine flag: the block is a macOS Gatekeeper GUI dialog (Apple's
  copy, not this project's), which cannot be provoked from a headless
  agent session. The compensating control is documented where the user
  hits it: the README Install section's right-click Open and
  `xattr -d com.apple.quarantine` fix, plus the AI-assistant checklist
  step 2 telling the onboarding agent to expect the block. Real-machine
  provocation is owed to the row 7 cold install; this sub-check is
  recorded as documented-but-not-provoked, not as passed.
- Packaged-artifact caveat: these provocations ran against the repo
  runtime and launcher shims on this host, because the packaged Windows
  artifact cannot execute here; see criterion 1's recorded rebuild gap
  (18-01-SUMMARY.md). Rebuilt-artifact provocation is owed with that
  rebuild.

## Row 7: Second-person cold install (the closing human gate)

**Status: DEFERRED, owed to Weibao (2026-09-01). Not certified. The phase
close is explicitly conditional on this row; it is a human checkpoint and
is never self-certified by an agent.**

- What is owed: a second person (Weibao's friend is fine, per 18-CONTEXT
  D-05) performs a cold install on a machine this project has never
  touched: download, install past SmartScreen using only the README copy,
  and reach a first graded sitting, with or without an AI agent's help.
  Record: did they get there, where they stalled, the words on screen when
  they stalled, the installer hash they verified, the date, and the
  person's role (not their name). Stalls are defects: fix and rerun
  before marking this row passed.
- Deferral authority: the standing directive of 2026-09-01 defers human
  tests; an unanswered checkpoint stops the phase and never gets a silent
  default. This row also absorbs the real-machine checks rows 1, 3, and 6
  could not perform on this host (packaged first run, Gatekeeper and
  SmartScreen dialogs as actually seen).
