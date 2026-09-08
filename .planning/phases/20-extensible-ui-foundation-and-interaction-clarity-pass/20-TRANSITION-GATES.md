# Phase 20 deterministic transition gates

**Checked:** 2026-09-08
**Scope:** Plan 20-04 Tasks 1 and 2
**Overall gate:** Blocked

The lifecycle graph has all 11 required transition families. Its focused graph,
IA-route, presentation-profile, quick-preflight, and diff checks pass. The
theme-picker timeout was repaired by removing the live native-picker request
from automated daemon coverage. The daemon picker contract now passes without
opening a visible system dialog. The required full daemon suite remains
unverified because this task runner ends foreground commands at about 30
seconds before the suite returns a result. This is an unavailable deterministic
leg, not a pass or a product-failure attribution, so this record is not green.

Every row below has a passed deterministic contract leg and a human-owed
acceptance leg. `check_lifecycle_transition_graph` verifies the family names,
required events, actor, durable authority, derived UI state, destination, Back,
Home, unsaved-work rule, idempotency, unavailable behavior, announcement,
narrow composition, distinct failure states, safe actions, and defensive copy.

| Transition family | Deterministic status | Exact automated evidence | Human status |
|---|---|---|---|
| Walkthrough | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_first_launch_offline`](../../../tests/ia_route_roundtrip.py#L1376), [`check_walkthrough_interruption`](../../../tests/ia_route_roundtrip.py#L1438) | Human owed: screen reader, touch device, and perceived clarity |
| Home | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_state_labels`](../../../tests/presentation_profiles_roundtrip.py#L178), [`check_course_transition_and_degraded_state_contract`](../../../tests/presentation_profiles_roundtrip.py#L194) | Human owed: screen reader, touch device, and perceived clarity |
| Course entry | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_deep_link_scenarios`](../../../tests/ia_route_roundtrip.py#L1069), [`check_walkthrough_interruption`](../../../tests/ia_route_roundtrip.py#L1438) | Human owed: screen reader, touch device, and perceived clarity |
| Course navigation | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_course_lesson_practice_context`](../../../tests/presentation_profiles_roundtrip.py#L228), [`check_same_routes_both_widths`](../../../tests/ia_route_roundtrip.py#L977) | Human owed: screen reader, touch device, and perceived clarity |
| Lesson and source | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_course_lesson_practice_context`](../../../tests/presentation_profiles_roundtrip.py#L228), [`check_gate_route_reload_no_resubmit`](../../../tests/daemon_roundtrip.py#L3754) | Human owed: screen reader, touch device, and perceived clarity |
| Practice | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_api_duplicate_submit_dedupes`](../../../tests/daemon_roundtrip.py#L2039), [`check_gate_route_skip_single_event`](../../../tests/daemon_roundtrip.py#L3708) | Human owed: screen reader, touch device, and perceived clarity |
| Assessment active | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_form_submit_writes_the_attempt_file`](../../../tests/serve_roundtrip.py#L234), [`check_a_failed_submit_keeps_the_answer`](../../../tests/serve_roundtrip.py#L517) | Human owed: screen reader, touch device, and perceived clarity |
| Assessment result | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_banner_id_is_the_evidence_id`](../../../tests/serve_roundtrip.py#L377), [`check_serve_attempt_refresh`](../../../tests/daemon_roundtrip.py#L2382) | Human owed: screen reader, touch device, and perceived clarity |
| Course completion | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_course_transition_and_degraded_state_contract`](../../../tests/presentation_profiles_roundtrip.py#L194), [`check_state_labels`](../../../tests/presentation_profiles_roundtrip.py#L178) | Human owed: screen reader, touch device, and perceived clarity |
| Agent proposal | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71) | Human owed: screen reader, touch device, and perceived clarity |
| Capability loss | Passed | [`check_lifecycle_transition_graph`](../../../tests/serve_roundtrip.py#L71), [`check_first_launch_offline`](../../../tests/ia_route_roundtrip.py#L1376), [`check_course_transition_and_degraded_state_contract`](../../../tests/presentation_profiles_roundtrip.py#L194) | Human owed: screen reader, touch device, and perceived clarity |

## Executed evidence

| Gate | Result |
|---|---|
| `python3 tests/serve_roundtrip.py` | Passed. It reported 11 lifecycle families and distinct recovery actions |
| `python3 tests/ia_route_roundtrip.py` | Passed, 26 checks |
| `python3 tests/presentation_profiles_roundtrip.py` | Passed |
| `python3 -c '...check_theme_pick_contract()...'` | Passed. The daemon contract confirms the picker bridge and Settings fallback without invoking a native picker. |
| `python3 tests/daemon_roundtrip.py` | Unavailable in this task runner. The command exceeded the runner's roughly 30-second foreground limit before returning a final result. Rerun in a normal terminal or CI. |
| `python3 scripts/preflight.py --quick` | Passed. Tests, clean, and JavaScript legs were intentionally skipped by `--quick`. |
| `git diff --check` | Passed |
| Human visual comparison | Human owed. Skipped by explicit user direction |
| Touch-device review | Human owed. Skipped by explicit user direction |
| Screen-reader review | Human owed. Skipped by explicit user direction |

The automated passes do not certify perceived clarity, touch behavior, or
screen-reader behavior. No real Math 1400 sitting was run.
