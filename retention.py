"""retention.py -- the pure retention, pacing and trends derivation layer.

Phase 10's whole contract in one sentence: a caller captures the append-only
evidence log exactly once, and every derived claim -- objective state, trend
row, recommendation, weight, cap decision, lesson-queue entry -- is a pure
function of that one immutable snapshot plus bounded settings. Nothing here
opens a second store, writes evidence, chooses items, parses banks, or
imports a surface; the module is to `evidence.py` what `runtime.py` is to
scoring (the pattern map's evidence.py:1-12 tier rule).

Design boundaries held throughout (10-CONTEXT D-01..D-24):

- D-01/D-02: `capture()` materializes one immutable snapshot marker; every
  payload and claim references it. Derived state is disposable; the
  append-only log stays the only authority.
- D-03: insufficient evidence is `unknown`, never zero mastery or a
  fabricated trend. No denominator yields an explicit null, not 0.
- D-06: six states (unknown, weak, mastered, at-risk, due, stable) are
  deterministic labels over visible component signals; every threshold and
  interval lives in bounded settings with named invalid-configuration
  errors.
- D-09/D-16/D-22: pending manual responses count toward pacing/attempts
  only; the latest accepted human mark settles constructed work; a model
  proposal or interaction event never settles anything. Retracted events
  disappear through the existing live-event filter.
- D-14: at-risk is "previously demonstrated success plus a configured
  silence interval", never predicted failure.
- D-17/D-18/D-19/D-23: scheduler state is derived by replaying the captured
  events through one strategy interface with FSRS as the registered
  default; progress is named in WaniKani-style stages with a terminal
  "retired" state; due ordering is jpdb-style utility-weighted. A later
  algorithm is a registration plus a replay, never a migration.
- D-20: the usage measure is return rate -- sittings that occurred over
  sittings that came due, with the denominator stated. It is never a
  streak, never rendered as a consecutive count, and has no loss state.

Local-day policy: the snapshot carries `local_day_zone` (an IANA name,
"UTC", "UTC+HH:MM"/"UTC-HH:MM", or "local"); event timestamps stay
UTC-aware instants and every date-derived signal (cap day, at-risk silence,
week window) is computed by projecting that instant into the zone. Two
captures with different zones are different snapshots with different ids.
"""
import datetime
import hashlib
import json
import re
import sys

import evidence


# ---------------------------------------------------------------------------
# Settings: one bounded `retention` group, schema-mirrored defaults.
# ---------------------------------------------------------------------------

# Conservative researched defaults (10-RESEARCH.md "Initial Formula and
# Settings Contract", pinned by 10-01-PLAN.md Task 2). Every value below is
# also schema-bounded in schemas/settings.schema.json; the schema is the
# source of truth and this constant exists so tests and the pure module can
# read shipped defaults without a settings load -- the same accessor pattern
# surfaces/settings.py already uses for `style` and `paraphrase` groups.
# `daily_cap` is deliberately NOT here: it is the one cap knob, a top-level
# settings key, and plan 10-04 reads it there.
RETENTION_SETTINGS_DEFAULTS = {
    "min_settled_attempts": 3,        # settled outcomes needed before a state label
    "weak_accuracy": 0.60,            # recent settled accuracy below this is weak
    "mastery_accuracy": 0.85,         # recent settled accuracy at/above this can be mastered
    "mastery_success_days": 3,        # confirmed successes across distinct local days
    "at_risk_after_days": 28,         # prior success then this many days silent
    "review_interval_days": 7,        # interval after which a stable objective is due
    "lesson_review_after_days": 14,   # lesson completion -> queue due date
    "weight_min": 0.75,               # bounded weight floor
    "weight_max": 1.25,               # bounded weight ceiling
    "max_weight_step": 0.10,          # max per-objective weight change per snapshot
    "weak_boost": 0.20,               # formula term: weak objectives
    "due_boost": 0.10,                # formula term: due objectives
    "at_risk_boost": 0.20,            # formula term: at-risk objectives
    "mastery_reduction": 0.15,        # formula term: mastered objectives
    "focused_session_count": 5,       # recommendation session size
}


def retention_settings(cfg):
    """The `retention` group of a loaded settings dict merged over shipped
    defaults, validated for cross-key contradictions.

    `cfg` may be None (pure-module callers, tests) -- the shipped defaults
    are the conservative base. Cross-key rules that a per-key schema cannot
    express are enforced here and fail with a NAMED error rather than
    silently reclassifying objectives (10-01 Task 2): the weak threshold
    must be lower than the mastery threshold, and the weight floor must be
    below the ceiling.
    """
    group = dict(RETENTION_SETTINGS_DEFAULTS)
    if cfg:
        loaded = (cfg.get("retention") or {})
        group.update({k: v for k, v in loaded.items() if v is not None})
    if not (group["weak_accuracy"] < group["mastery_accuracy"]):
        sys.exit("retention.invalid_config: weak_accuracy (%s) must be lower "
                 "than mastery_accuracy (%s)"
                 % (group["weak_accuracy"], group["mastery_accuracy"]))
    if not (group["weight_min"] < group["weight_max"]):
        sys.exit("retention.invalid_config: weight_min (%s) must be below "
                 "weight_max (%s)"
                 % (group["weight_min"], group["weight_max"]))
    return group


def settings_version(cfg):
    """A canonical content hash of the retention settings values actually in
    effect, so a claim names the exact thresholds it was derived under
    (D-01: settings_version in every claim). Changing a threshold changes
    the version, which changes the snapshot id.
    """
    group = retention_settings(cfg)
    canon = json.dumps(group, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Local-day zone policy.
# ---------------------------------------------------------------------------

_UTC_RE = re.compile(r"^UTC([+-])(\d{1,2}):?(\d{2})?$", re.I)


def resolve_zone(zone):
    """Resolve a local-day zone policy to a tzinfo plus a canonical label.

    Accepts "UTC" (default), "local" (the machine's local zone, resolved
    via the system tz database -- stdlib-only), a fixed offset in the form
    "UTC+05:30"/"UTC-0800", or an IANA name such as "America/New_York".
    An IANA name that the system tz database cannot resolve (a Windows box
    without the `tzdata` package) fails with a named error rather than
    silently deriving every date in UTC.
    """
    if zone is None or str(zone).lower() == "local":
        tz = datetime.datetime.now().astimezone().tzinfo
        return tz, "local(%s)" % tz
    if str(zone).upper() == "UTC":
        return datetime.timezone.utc, "UTC"
    m = _UTC_RE.match(str(zone))
    if m:
        sign = 1 if m.group(1) == "+" else -1
        hours = int(m.group(2))
        minutes = int(m.group(3) or "0")
        if hours > 14 or minutes > 59 or (hours == 14 and minutes):
            sys.exit("retention.invalid_zone: %r is not a legal UTC offset"
                     % (zone,))
        tz = datetime.timezone(sign * datetime.timedelta(
            hours=hours, minutes=minutes))
        label = "UTC%+03d:%02d" % (sign * hours, minutes) if minutes else \
            "UTC%+03d" % (sign * hours)
        return tz, label
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(str(zone)), str(zone)
    except Exception:
        sys.exit("retention.invalid_zone: %r is not a known IANA zone on this "
                 "system; use 'UTC', 'local', 'UTC+HH:MM'/'UTC-HH:MM', or an "
                 "IANA name" % (zone,))


def _parse_utc(ts):
    """Parse an ISO-8601 UTC timestamp from the evidence log
    (`2026-08-10T14:49:25.025Z`) into an aware UTC datetime; returns None
    when unparseable so a torn/foreign line degrades, never crashes."""
    try:
        dt = datetime.datetime.strptime(
            ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def local_date(ts, tz):
    """The local calendar date of a UTC evidence timestamp in `tz`, or None
    when the timestamp is unparseable (D-03: unknown, not a fabricated
    day)."""
    dt = _parse_utc(ts)
    if dt is None:
        return None
    return dt.astimezone(tz).date()


# ---------------------------------------------------------------------------
# Snapshot capture (D-01/D-02): one immutable marker + the captured events.
# ---------------------------------------------------------------------------

CLAIM_FIELDS = ("snapshot_id", "cutoff", "local_day_zone", "window",
                "filters", "live_event_count", "settings_version")


def _canonical_claim(cutoff, zone_label, weeks, filters, live_count,
                     settings_ver):
    """The canonical claim body: everything except the snapshot id, so the
    id is a pure hash of the inputs the claim names."""
    return {
        "cutoff": cutoff,
        "local_day_zone": zone_label,
        "window": {"weeks": weeks},
        "filters": dict(filters or {}),
        "live_event_count": live_count,
        "settings_version": settings_ver,
    }


def _snapshot_id(claim, events):
    """sha256 over the canonical claim plus the ordered live event
    identities -- two captures of identical bytes/cutoff/zone/filters/
    settings produce the same id, and appending after capture cannot change
    the already-returned snapshot (T-10-01). Not a security boundary; a
    change-detection checksum, like every sha256 in evidence.py."""
    h = hashlib.sha256()
    h.update(json.dumps(claim, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    for ev in events:
        h.update((ev.get("event_id") or "").encode("utf-8"))
        h.update((ev.get("event_type") or "").encode("utf-8"))
        h.update((ev.get("ts") or "").encode("utf-8"))
    return h.hexdigest()


def capture(events, *, cutoff=None, zone="UTC", weeks=4, filters=None,
            cfg=None):
    """Materialize ONE immutable snapshot from a captured event sequence.

    `events` must be `evidence.capture_events(log)` output (or an
    equivalent immutable tuple) -- this function never reads a log itself.
    `cutoff` is an ISO-8601 UTC timestamp; default is now. `zone` is the
    local-day policy (see `resolve_zone`). `weeks` is the report window.
    `filters` narrows which events count (subject/objective/bank). `cfg` is
    the loaded settings dict (or None for shipped defaults).

    Returns a dict with `claim` (the public provenance marker), `events`
    (the immutable sequence this snapshot was derived from), and derived
    local-day context. Every nested row/recommendation/weight produced from
    this snapshot references `claim["snapshot_id"]` (D-01, D-13, D-15).
    """
    cutoff = cutoff or evidence.utc_now()
    tz, zone_label = resolve_zone(zone)
    live = list(events)
    claim = _canonical_claim(cutoff, zone_label, weeks, filters or {},
                             len(live), settings_version(cfg))
    claim["snapshot_id"] = _snapshot_id(claim, live)
    cutoff_dt = _parse_utc(cutoff) or datetime.datetime.now(
        datetime.timezone.utc)
    # One marks_by_event-equivalent join, computed once per capture (D-16:
    # latest LIVE accepted human mark per response event id) and shared by
    # every derivation below -- never a per-call rescan (T-10-04).
    marks = {}
    for ev in live:
        if ev.get("event_type") == evidence.MARK_EVENT_TYPE:
            target = ev.get("marks_event")
            if target:
                marks[target] = ev
    return {
        "claim": claim,
        "events": tuple(live),
        "marks": marks,
        "tz": tz,
        "zone_label": zone_label,
        "cutoff_dt": cutoff_dt,
        "local_day": cutoff_dt.astimezone(tz).date(),
        "settings": retention_settings(cfg),
    }


def _match_filters(ev, filters):
    """True when `ev` satisfies the snapshot filters (D-15: filter changes
    are named in `filters` and never reuse a misleading claim). A subject
    filter matches the event's subject alone; an objective filter matches
    exactly; a bank filter matches the recorded basename."""
    f = filters or {}
    if f.get("subject") and ev.get("subject") != f["subject"]:
        return False
    if f.get("objective") and ev.get("objective") != f["objective"]:
        return False
    if f.get("bank") and ev.get("bank") != f["bank"]:
        return False
    return True


# ---------------------------------------------------------------------------
# Objective state grammar (D-06, D-09, D-14, D-16).
# ---------------------------------------------------------------------------

STATES = ("unknown", "weak", "mastered", "at-risk", "due", "stable")


def _settled_verdict(ev, marks):
    """The settled outcome of one response event, or None when it is
    pending (D-09/D-16): an auto-scored bool is settled; a `short` response
    is settled only by the most recent LIVE accepted human mark
    (`marks_by_event`). A model proposal/interaction event is not a
    response and is never settled here (D-22)."""
    score = ev.get("score")
    if score is True or score is False:
        return bool(score)
    mark = marks.get(ev.get("event_id"))
    if mark is not None:
        return bool(mark.get("verdict"))
    return None


def objective_summaries(snapshot):
    """One summary row per objective with evidence, plus the bank-level
    derived facts the report needs, computed in ONE pass over the captured
    events (T-10-04: no per-objective log rescan).

    Every row carries: attempts (all live responses), settled/correct with
    raw counts, recent accuracy over the last `min_settled_attempts`
    settled outcomes, confirmed-success distinct local days, pending count,
    highest/average Phase 6 hint tier, last evidence date, last confirmed
    success date, and the snapshot id.
    """
    cfg = snapshot["settings"]
    tz = snapshot["tz"]
    marks = snapshot["marks"]
    per_obj = {}
    for ev in snapshot["events"]:
        if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
            continue
        if not _match_filters(ev, snapshot["claim"]["filters"]):
            continue
        objective = ev.get("objective") or ""
        row = per_obj.setdefault(objective, {
            "objective": objective,
            "subject": evidence.subject_of(objective),
            "attempts": 0, "settled": 0, "correct": 0,
            "pending": 0, "hints": [], "last_evidence": None,
            "last_success": None, "last_settled": None,
            "settled_dates": [],
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        })
        row["attempts"] += 1
        date = local_date(ev.get("ts"), tz)
        if date is not None and (row["last_evidence"] is None
                                 or date > row["last_evidence"]):
            row["last_evidence"] = date
        verdict = _settled_verdict(ev, marks)
        if verdict is None:
            row["pending"] += 1
        else:
            row["settled"] += 1
            if date is not None and (row["last_settled"] is None
                                     or date > row["last_settled"]):
                row["last_settled"] = date
            if verdict:
                row["correct"] += 1
                if date is not None and (row["last_success"] is None
                                         or date > row["last_success"]):
                    row["last_success"] = date
                if date is not None:
                    row["settled_dates"].append((date, True))
            else:
                if date is not None:
                    row["settled_dates"].append((date, False))
        tier = ev.get("hint_tier")
        if isinstance(tier, int):
            row["hints"].append(tier)
    rows = []
    for objective, row in per_obj.items():
        settled_dates = sorted(row.pop("settled_dates"))
        recent = settled_dates[-cfg["min_settled_attempts"]:]
        recent_correct = sum(1 for _d, ok in recent if ok)
        success_days = {d for d, ok in settled_dates if ok}
        row.update({
            "accuracy": (row["correct"] / row["settled"])
            if row["settled"] else None,
            "recent_accuracy": (recent_correct / len(recent))
            if recent else None,
            "success_days": len(success_days),
            "highest_hint": max(row["hints"]) if row["hints"] else None,
            "average_hint": (sum(row["hints"]) / len(row["hints"]))
            if row["hints"] else None,
        })
        row.pop("hints", None)
        rows.append(row)
    rows.sort(key=lambda r: (r["subject"], r["objective"]))
    return rows


def objective_state(row, snapshot):
    """The deterministic six-state label plus due flag for one summary row
    (D-03/D-06/D-14). Precedence, in order:

    1. fewer than `min_settled_attempts` settled outcomes -> unknown (and a
       pending-only objective stays unknown -- D-09).
    2. at least one confirmed success AND at least `at_risk_after_days`
       since the last confirmed success -> at-risk (D-14, TREND-04).
    3. recent accuracy at/above `mastery_accuracy` on at least
       `mastery_success_days` distinct local days -> mastered.
    4. recent accuracy below `weak_accuracy` -> weak.
    5. at least `review_interval_days` since the latest settled evidence,
       with a confirmed success on record -> due.
    6. otherwise -> stable.

    `due` is a separate boolean: weak/at-risk/interval-elapsed objectives
    are due (10-01 Task 2: "elapsed configured review interval or
    weak/at-risk makes due"), and an objective with no confirmed success is
    never due -- due is a recommendation label over demonstrated work, and
    a never-settled objective has nothing to recommend.
    """
    cfg = snapshot["settings"]
    cutoff = snapshot["local_day"]
    if row["settled"] < cfg["min_settled_attempts"]:
        return {"state": "unknown", "due": False}
    has_success = row["correct"] > 0
    if has_success and row["last_success"] is not None:
        silence = (cutoff - row["last_success"]).days
        if silence >= cfg["at_risk_after_days"]:
            return {"state": "at-risk", "due": True}
    recent = row["recent_accuracy"]
    if recent is not None and recent >= cfg["mastery_accuracy"] \
            and row["success_days"] >= cfg["mastery_success_days"]:
        return {"state": "mastered", "due": False}
    if recent is not None and recent < cfg["weak_accuracy"]:
        return {"state": "weak", "due": True}
    if has_success and row["last_settled"] is not None:
        elapsed = (cutoff - row["last_settled"]).days
        if elapsed >= cfg["review_interval_days"]:
            return {"state": "due", "due": True}
    return {"state": "stable", "due": False}


def risk_reason(row, state, snapshot):
    """The human-readable, evidence-anchored reason for an objective's
    state, or None. At-risk names the last proven success date and the
    configured silence threshold (D-14); weak names the raw accuracy;
    mastered names the success-day count; due names the elapsed interval."""
    cfg = snapshot["settings"]
    if state["state"] == "at-risk":
        return ("last confirmed success was %s, %s days ago (at-risk after "
                "%s days without confirmation)"
                % (row["last_success"],
                   (snapshot["local_day"] - row["last_success"]).days,
                   cfg["at_risk_after_days"]))
    if state["state"] == "weak":
        return ("recent settled accuracy is %s (raw %s/%s), below the "
                "weak threshold %s"
                % (("0" if row["recent_accuracy"] == 0
                    else "%.2f" % row["recent_accuracy"]),
                   row["settled"] - row["correct"], row["settled"],
                   cfg["weak_accuracy"]))
    if state["state"] == "mastered":
        return ("recent settled accuracy %s at/above mastery %s on %s "
                "distinct success day(s)"
                % ("%.2f" % row["recent_accuracy"], cfg["mastery_accuracy"],
                   row["success_days"]))
    if state["state"] == "due":
        return ("no settled evidence for %s days, at/over the review "
                "interval of %s days"
                % ((snapshot["local_day"] - row["last_settled"]).days,
                   cfg["review_interval_days"]))
    return None


# ---------------------------------------------------------------------------
# Week series (D-13): raw counts beside every rate, uncertainty as null.
# ---------------------------------------------------------------------------

WEEK_BUCKETS = (1, 2, 4, 8, 12)


def week_series(row, snapshot):
    """The per-objective longitudinal series over the selectable
    1/2/4/8/12-week buckets (D-13). Every bucket carries raw
    numerator/denominator beside the rate; a bucket with no settled
    evidence has an explicit null accuracy, never zero (D-03).

    The marks join comes from the snapshot's single capture-time join
    (snapshot["marks"]), so the buckets and the state rows settle the same
    way (D-16)."""
    tz = snapshot["tz"]
    cutoff = snapshot["local_day"]
    marks = snapshot["marks"]
    buckets = {}
    for weeks in WEEK_BUCKETS:
        start = cutoff - datetime.timedelta(days=7 * weeks)
        attempts = correct = pending = 0
        hints = []
        last = None
        for ev in snapshot["events"]:
            if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
                continue
            if ev.get("objective") != row["objective"]:
                continue
            date = local_date(ev.get("ts"), tz)
            if date is None or date < start or date > cutoff:
                continue
            attempts += 1
            verdict = _settled_verdict(ev, marks)
            if verdict is None:
                pending += 1
            elif verdict:
                correct += 1
            tier = ev.get("hint_tier")
            if isinstance(tier, int):
                hints.append(tier)
            if last is None or date > last:
                last = date
        settled = attempts - pending
        buckets["%dw" % weeks] = {
            "attempts": attempts,
            "correct": correct,
            "settled": settled,
            "accuracy": (correct / settled) if settled else None,
            "pending": pending,
            "highest_hint": max(hints) if hints else None,
            "average_hint": (sum(hints) / len(hints)) if hints else None,
            "last_evidence": last.isoformat() if last else None,
        }
    return buckets


# ---------------------------------------------------------------------------
# Bounded objective weights (D-11/D-12, TREND-01) -- the Phase 7 handoff.
# ---------------------------------------------------------------------------

def objective_weights(summaries, snapshot, previous=None):
    """Normalized bounded objective weight map for Phase 7's selector
    (D-10/D-11): Phase 10 supplies weights + snapshot, never item choices.

    Formula (10-RESEARCH.md, pinned by 10-01 Task 2):
        raw = 1 + weak_boost + due_boost + at_risk_boost - mastery_reduction
    where each term is present only when the objective is in that state.
    The raw value is clamped to [weight_min, weight_max], then normalized
    so the mean multiplier over the eligible objectives is 1.0 (weights are
    relative, and a lone objective must not grow to the ceiling), and then
    each objective's absolute change from the previous snapshot's map is
    capped at `max_weight_step` (D-12: gradual, per-snapshot). `previous`
    is the map from the most recent live selection event in the captured
    snapshot (10-03); None means no history, so no cap applies.

    The returned map is keyed by objective with the multiplier plus the
    named components and the snapshot id, so the selector trace can explain
    every influence (D-11, 10-03).
    """
    cfg = snapshot["settings"]
    raw = {}
    components = {}
    for row in summaries:
        st = objective_state(row, snapshot)["state"]
        comp = {
            "weak": cfg["weak_boost"] if st == "weak" else 0.0,
            "due": cfg["due_boost"] if st in ("weak", "due", "at-risk") else 0.0,
            "at_risk": cfg["at_risk_boost"] if st == "at-risk" else 0.0,
            "mastery": -cfg["mastery_reduction"] if st == "mastered" else 0.0,
        }
        value = 1.0 + sum(comp.values())
        value = max(cfg["weight_min"], min(cfg["weight_max"], value))
        raw[row["objective"]] = value
        components[row["objective"]] = comp
    if raw:
        mean = sum(raw.values()) / len(raw)
        if mean > 0:
            raw = {k: v / mean for k, v in raw.items()}
    # Gradual change cap (D-12): bounded per objective, per snapshot.
    out = {}
    for objective, value in raw.items():
        if previous and objective in previous:
            prev = previous[objective]
            step = cfg["max_weight_step"]
            value = max(prev - step, min(prev + step, value))
        out[objective] = {
            "weight": round(value, 6),
            "components": components[objective],
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        }
    return out


# ---------------------------------------------------------------------------
# Focused-session recommendation (D-04, D-13; no gamification -- ROADMAP SC6).
# ---------------------------------------------------------------------------

def recommendation(summaries, snapshot):
    """One bounded focused-session recommendation: names why it exists,
    limits itself to `focused_session_count` objectives, and may carry
    optional reflection prompts anchored to observed evidence. It has no
    points, streaks, levels, composite score, or model inference. When no
    objective is due/weak/at-risk, the recommendation is empty with a
    reason that says so (D-03: never a fabricated due claim)."""
    cfg = snapshot["settings"]
    targets = []
    for row in summaries:
        st = objective_state(row, snapshot)
        if st["due"]:
            targets.append(row)
    targets.sort(key=lambda r: (r["subject"], r["objective"]))
    selected = targets[:cfg["focused_session_count"]]
    if not selected:
        return {"reason": "no objective is currently due",
                "session_count": 0, "objectives": [], "reflection": [],
                "snapshot_id": snapshot["claim"]["snapshot_id"]}
    reason = ("%d objective(s) are due for review: %s"
              % (len(selected),
                 ", ".join(r["objective"] for r in selected)))
    reflection = []
    for row in selected:
        st = objective_state(row, snapshot)
        if st["state"] == "weak" and row["accuracy"] is not None:
            reflection.append(
                "On %r, %d of the last %d settled responses were correct; "
                "consider reviewing the material behind the missed ones."
                % (row["objective"], row["correct"], row["settled"]))
        elif st["state"] == "at-risk":
            reflection.append(
                "You last confirmed %r on %s; re-attempt it to refresh it."
                % (row["objective"], row["last_success"]))
    return {"reason": reason, "session_count": len(selected),
            "objectives": [r["objective"] for r in selected],
            "reflection": reflection,
            "snapshot_id": snapshot["claim"]["snapshot_id"]}


# ---------------------------------------------------------------------------
# Scheduler strategy interface (D-17/D-18/D-19/D-23): FSRS default, stages,
# jpdb-style utility-weighted due ordering, return rate (D-20).
# ---------------------------------------------------------------------------

# Published FSRS default parameter set (reference implementation defaults,
# no fitted tuning this phase -- D-17/D-23). The strategy interface, not
# the formula, is what future profiles replace.
FSRS_DEFAULT_W = (
    0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14,
    0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61,
)
FSRS_FACTOR = 19.0 / 81.0
FSRS_DECAY = -0.5

# WaniKani-style stage names with a terminal "retired" state (D-19). The
# stage is a legible presentation over the derived interval, never a second
# scheduler. "Retired" is terminal: an objective that far out has left
# ordinary rotation entirely.
STAGE_NAMES = ("Apprentice I", "Apprentice II", "Apprentice III",
               "Apprentice IV", "Guru I", "Guru II", "Master",
               "Enlightened", "Retired")
STAGE_THRESHOLDS = (0, 1, 3, 7, 14, 30, 90, 180, 365)  # interval days, exclusive upper


def stage_for_interval(interval_days):
    """Map a scheduler interval in days to a WaniKani-style stage name;
    intervals at/above the final threshold are the terminal "retired"
    state (D-19)."""
    for i, threshold in enumerate(STAGE_THRESHOLDS):
        if interval_days < threshold:
            return STAGE_NAMES[i]
    return STAGE_NAMES[-1]


class SchedulerStrategy:
    """The one scheduler interface (D-18): a registered strategy turns the
    captured live events for one objective into derived scheduling state
    (interval, due date, stage). Rebuilding from the log alone must
    reproduce it exactly (D-17); a later strategy is a registration plus a
    replay, never a migration. Strategies are pure: no I/O, no settings
    beyond what `replay` receives."""
    name = "base"

    def replay(self, objective, summaries, snapshot):
        raise NotImplementedError


def _fsrs_review_sequence(row, snapshot):
    """The ordered review sequence for one objective: every live response
    event, oldest first, with its settled verdict (accepted marks only --
    D-22). Pending responses are skipped: a pending suggestion counts as an
    attempt but never advances an interval."""
    out = []
    for ev in snapshot["events"]:
        if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
            continue
        if ev.get("objective") != row["objective"]:
            continue
        verdict = _settled_verdict(ev, snapshot["marks"])
        if verdict is None:
            continue
        date = local_date(ev.get("ts"), snapshot["tz"])
        out.append({"date": date, "correct": verdict})
    out.sort(key=lambda r: (r["date"] or datetime.date.min,))
    return out


class FSRSStrategy(SchedulerStrategy):
    """The default scheduler strategy: FSRS with the published reference
    parameter set, replayed over accepted settled reviews only (D-17/D-22).

    State per objective: retrievability R, stability S, difficulty D,
    interval (days), and the derived due date / stage. The core update
    rules are FSRS's: R decays with elapsed days, a success grows S and
    lowers D, a failure collapses S and raises D; interval is S rounded.
    This is a transparent bounded implementation of the published model --
    not a fitted or ML variant (D-23) -- and the numbers it produces are
    deterministic functions of the log alone, so replay reproduces state
    exactly. `scheduled_due_dates` records the due date each review
    scheduled (used by the D-20 return-rate denominator).
    """
    name = "fsrs"

    def replay(self, objective, summaries, snapshot):
        row = next((r for r in summaries
                    if r["objective"] == objective), None)
        if row is None:
            return None
        seq = _fsrs_review_sequence(row, snapshot)
        if not seq:
            return {"objective": objective, "strategy": self.name,
                    "reviews": 0, "interval_days": None, "due_date": None,
                    "scheduled_due_dates": [], "stage": "Apprentice I",
                    "snapshot_id": snapshot["claim"]["snapshot_id"]}
        s, d, last, interval = 0.0, 0.0, None, 1
        scheduled = []
        for review in seq:
            date = review["date"] or snapshot["local_day"]
            elapsed = (date - last).days if last else 0
            r = 1.0
            if last is not None and s > 0 and elapsed >= 0:
                r = (1.0 + FSRS_FACTOR * elapsed / s) ** FSRS_DECAY
                r = max(0.0, min(1.0, r))
            w = FSRS_DEFAULT_W
            if review["correct"]:
                if s == 0:
                    s = w[0] + w[1] * 2.0          # first success (rating good)
                    d = w[2]
                else:
                    s = s * (1.0 + w[7] * (11.0 - d) * (s ** -w[8])
                             * (2.71828 ** (w[9] * (1.0 - r)) - 1.0))
                    d = max(1.0, min(10.0, d - w[5] * (4.0 - 3.0)))
            else:
                if s == 0:
                    s = w[0] + w[1] * 0.0          # first failure (rating again)
                    d = w[2] + w[5]
                else:
                    s = w[10] * (d ** -w[11]) * (((s + 1.0) ** w[12]) - 1.0) \
                        * (2.71828 ** (w[13] * (1.0 - r)))
                    d = min(10.0, d + w[5] * (4.0 - 3.0))
            interval = max(1, int(round(s)))
            if last is not None and date is not None:
                scheduled.append((last + datetime.timedelta(days=interval))
                                 .isoformat())
            last = date
        due = last + datetime.timedelta(days=interval) if last else None
        return {
            "objective": objective, "strategy": self.name,
            "reviews": len(seq), "stability": round(s, 4),
            "difficulty": round(d, 4), "interval_days": interval,
            "due_date": due.isoformat() if due else None,
            "scheduled_due_dates": scheduled,
            "stage": stage_for_interval(interval),
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        }


_SCHEDULERS = {}


def register_scheduler(strategy):
    """Register a scheduler strategy by name (D-18). Registration is the
    only step a future profile needs beyond a replay."""
    _SCHEDULERS[strategy.name] = strategy


def get_scheduler(name="fsrs"):
    """The registered strategy, or the default FSRS strategy when `name`
    is unknown-safe (D-23: defaults stay conservative; nothing is hidden
    behind a single 'smart' score)."""
    if not _SCHEDULERS:
        register_scheduler(FSRSStrategy())
    return _SCHEDULERS.get(name, _SCHEDULERS["fsrs"])


def scheduler_states(summaries, snapshot, strategy_name="fsrs"):
    """Replay every objective's scheduling state through the registered
    strategy (D-17). `retention.py` never writes these -- they are derived
    rows, disposable and reproducible from the log alone (D-02)."""
    strategy = get_scheduler(strategy_name)
    return {row["objective"]: strategy.replay(row["objective"], summaries,
                                              snapshot)
            for row in summaries}


def utility_order(summaries, scheduler, snapshot):
    """jpdb-style utility-weighted due ordering (D-19): among due
    objectives, order by descending utility = bounded weight * (1 + days
    overdue / interval), so an objective that is more overdue and more
    heavily weighted is served first. Non-due objectives are not in the
    due order at all. Legible and deterministic -- the utility is a plain
    derived number a learner can inspect, not a hidden score."""
    weights = objective_weights(summaries, snapshot)
    entries = []
    for row in summaries:
        st = objective_state(row, snapshot)
        if not st["due"]:
            continue
        sched = (scheduler or {}).get(row["objective"]) or {}
        interval = sched.get("interval_days") or 1
        weight = weights.get(row["objective"], {}).get("weight", 1.0)
        due_date = sched.get("due_date")
        overdue = 0
        if due_date:
            try:
                due_dt = datetime.date.fromisoformat(due_date)
                overdue = max(0, (snapshot["local_day"] - due_dt).days)
            except ValueError:
                overdue = 0
        utility = weight * (1.0 + overdue / max(1, interval))
        entries.append({"objective": row["objective"], "utility": round(utility, 4),
                        "weight": weight, "overdue_days": overdue})
    entries.sort(key=lambda e: (-e["utility"], e["objective"]))
    return entries


def return_rate(summaries, scheduler, snapshot):
    """D-20: return rate -- sittings that occurred over sittings that came
    due -- with the denominator stated. A property of the system's pacing,
    never a judgement of the person: a ratio with counts, no target, no
    streak, no loss state.

    Occurred = distinct local days in the window with at least one settled
    response; due = distinct local days in the window on which the
    scheduler had scheduled a review (each review's derived due date,
    replayed from the log). With no due days the ratio is null (unknown),
    never zero (D-03) -- there is nothing to measure."""
    tz = snapshot["tz"]
    weeks = snapshot["claim"]["window"]["weeks"]
    window_start = snapshot["local_day"] - datetime.timedelta(days=7 * weeks)
    occurred = set()
    for ev in snapshot["events"]:
        if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
            continue
        date = local_date(ev.get("ts"), tz)
        if date and window_start <= date <= snapshot["local_day"]:
            occurred.add(date)
    due_days = set()
    for row in summaries:
        sched = (scheduler or {}).get(row["objective"]) or {}
        for due in sched.get("scheduled_due_dates") or []:
            try:
                d = datetime.date.fromisoformat(due)
            except ValueError:
                continue
            if window_start <= d <= snapshot["local_day"]:
                due_days.add(d)
    if not due_days:
        return {"occurred": len(occurred), "due": 0, "rate": None}
    return {"occurred": len(occurred), "due": len(due_days),
            "rate": round(len(occurred) / len(due_days), 4)}


# ---------------------------------------------------------------------------
# The surface-neutral report payload (D-13/D-15) and its plain-text twin.
# ---------------------------------------------------------------------------

def retention_report(events, *, cutoff=None, zone="UTC", weeks=4,
                     filters=None, cfg=None, previous_weights=None):
    """The one longitudinal report derivation: capture once, derive every
    section from that snapshot. Surface-neutral -- no HTML, chart geometry,
    Anki count, browser field, answer key, hidden tier, provider payload,
    or model content enters this payload (10-01 Task 3)."""
    snapshot = capture(events, cutoff=cutoff, zone=zone, weeks=weeks,
                       filters=filters, cfg=cfg)
    summaries = objective_summaries(snapshot)
    scheduler = scheduler_states(summaries, snapshot)
    subjects = {}
    for row in summaries:
        subj = row["subject"] or "(unmapped)"
        sub = subjects.setdefault(subj, {"subject": subj, "objective_count": 0,
                                         "attempts": 0, "settled": 0,
                                         "correct": 0, "due": 0})
        st = objective_state(row, snapshot)
        sub["objective_count"] += 1
        sub["attempts"] += row["attempts"]
        sub["settled"] += row["settled"]
        sub["correct"] += row["correct"]
        if st["due"]:
            sub["due"] += 1
    objectives = {}
    for row in summaries:
        st = objective_state(row, snapshot)
        objectives[row["objective"]] = {
            "state": st["state"], "due": st["due"],
            "risk_reason": risk_reason(row, st, snapshot),
            "attempts": row["attempts"], "settled": row["settled"],
            "correct": row["correct"], "pending": row["pending"],
            "accuracy": row["accuracy"], "recent_accuracy": row["recent_accuracy"],
            "success_days": row["success_days"],
            "highest_hint": row["highest_hint"],
            "average_hint": row["average_hint"],
            "last_evidence": (row["last_evidence"].isoformat()
                              if row["last_evidence"] else None),
            "weeks": week_series(row, snapshot),
            "scheduler": scheduler.get(row["objective"]),
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        }
    overview_states = {}
    for row in summaries:
        st = objective_state(row, snapshot)["state"]
        overview_states[st] = overview_states.get(st, 0) + 1
    return {
        "schema_version": 2,
        "kind": "retention_report",
        "claim": snapshot["claim"],
        "overview": {
            "objective_count": len(summaries),
            "subject_count": len(subjects),
            "attempts": sum(r["attempts"] for r in summaries),
            "settled": sum(r["settled"] for r in summaries),
            "correct": sum(r["correct"] for r in summaries),
            "states": overview_states,
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        },
        "subjects": subjects,
        "objectives": objectives,
        "weights": objective_weights(summaries, snapshot,
                                     previous_weights),
        "recommendation": recommendation(summaries, snapshot),
        "due_order": utility_order(summaries, scheduler, snapshot),
        "return_rate": return_rate(summaries, scheduler, snapshot),
    }


def _fmt_rate(value):
    return "unknown" if value is None else ("%.2f" % value)


def report_text(payload):
    """Plain-text rendering of the SAME report dict the JSON twin prints
    (D-15): labels may reorder for readability but never recompute, omit
    uncertainty, or drop provenance. No arithmetic in the renderer."""
    claim = payload["claim"]
    L = ["Retention & trends report", "",
         "snapshot: %s" % claim["snapshot_id"],
         "cutoff: %s  zone: %s  window: %s week(s)" %
         (claim["cutoff"], claim["local_day_zone"], claim["window"]["weeks"]),
         "filters: %s  live events: %s  settings: %s" %
         (json.dumps(claim["filters"], ensure_ascii=False)
          if claim["filters"] else "(none)",
          claim["live_event_count"], claim["settings_version"]),
         "",
         "overview: %d objective(s) across %d subject(s); %d attempts, %d "
         "settled, %d correct" % (payload["overview"]["objective_count"],
                                  payload["overview"]["subject_count"],
                                  payload["overview"]["attempts"],
                                  payload["overview"]["settled"],
                                  payload["overview"]["correct"]),
         "return rate: %s (%d occurred / %d due sittings)"
         % (_fmt_rate(payload["return_rate"]["rate"]),
            payload["return_rate"]["occurred"], payload["return_rate"]["due"]),
         ""]
    for subject, sub in sorted(payload["subjects"].items()):
        L.append("subject %r: %d objective(s), %d attempts, %d settled, %d "
                 "correct, %d due"
                 % (subject, sub["objective_count"], sub["attempts"],
                    sub["settled"], sub["correct"], sub["due"]))
    L.append("")
    for objective, o in sorted(payload["objectives"].items()):
        L.append("%-28s %-8s %s"
                 % (objective[:28], o["state"], "due" if o["due"] else ""))
        if o["risk_reason"]:
            L.append("    reason: %s" % o["risk_reason"])
        L.append("    raw: %d/%d settled, %d pending; recent accuracy %s; "
                 "hints high %s avg %s; last evidence %s"
                 % (o["correct"], o["settled"], o["pending"],
                    _fmt_rate(o["recent_accuracy"]),
                    o["highest_hint"], o["average_hint"],
                    o["last_evidence"] or "unknown"))
    rec = payload["recommendation"]
    if rec["objectives"]:
        L.append("")
        L.append("recommendation: %s (session of %d)" %
                 (rec["reason"], rec["session_count"]))
        for ref in rec["reflection"]:
            L.append("  reflection: %s" % ref)
    if payload["due_order"]:
        L.append("")
        L.append("due order (utility-weighted):")
        for e in payload["due_order"]:
            L.append("  %-28s utility %.3f (weight %.3f, %d day(s) overdue)"
                     % (e["objective"][:28], e["utility"], e["weight"],
                        e["overdue_days"]))
    L.append("")
    return "\n".join(L)
