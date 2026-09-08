# Phase 20 audit crosswalk

**Current owner:** Phase 20 context and plan
**Historical evidence:** The source audits remain unchanged
**Checked:** 2026-09-08, implementation audit link

This file is the current routing answer for UI findings relevant to Phase 20. It does not replace the historical audits. A finding appears here once with one disposition and one implementation owner.

## Terminal dispositions

| Finding | Strongest evidence | Terminal disposition | Evidence or external owner |
|---|---|---|---|
| Study renders hidden action groups because `.acts{display:flex}` defeats the hidden state | `UI-CHARACTER-AUDIT-2026-09-06.md` F1.1 | Fixed and deterministically verified | `surfaces/study.py` gives `[hidden]` precedence. `tests/surface_roundtrip.py` and `tests/component_primitives_roundtrip.py` verify reveal order, one primary action, focus order, and no hidden focusable controls |
| Quiz table and build selects render below the project target and text size | UI character F1.1 and 13.5 responsive gates | Fixed and deterministically verified | `surfaces/quiz_page.py` uses 44px controls and 16px action text. `tests/presentation_profiles_roundtrip.py` covers all response types and `tests/component_primitives_roundtrip.py` covers the target floor |
| Walkthrough controls use browser-default styling beside production controls | UI character F1.1 | Fixed and deterministically verified | The walkthrough uses the shared primitive treatment. `tests/component_primitives_roundtrip.py` and `tests/ia_route_roundtrip.py::check_walkthrough_interruption` cover controls and state preservation |
| Shelf and course areas lack a consistent application and course navigation frame | UI character F1.2, remediation R5, 16B route contract | Fixed and deterministically verified | `presentation.surface_adapter_manifest()` declares the shared course-area frame. `tests/presentation_profiles_roundtrip.py` and `tests/ia_route_roundtrip.py` verify course context, stable routes, Back, and Home behavior |
| Quiz exposes all locked hint tiers and internal tier vocabulary before use | UI character F1.3, 13.5 wrong-answer contract, 17A progressive disclosure | Fixed, directly observed, and deterministically verified | The local served Quiz had regressed to six visible locked tiers. It now shows only the next permitted tier and one help action. `tests/serve_roundtrip.py` asserts one locked tier. The local browser recheck observed only Tier 0 and "I'm stumped" on a fresh sitting. Runtime disclosure authority remains unchanged |
| Repeated rounded containers and drifting type sizes weaken hierarchy | UI character F1.4 and 13.5 five-size contract | Blocked on an owned deterministic condition | Shared semantic roles and the in-scope lesson, presentation, and Quiz type scale pass. `tests/stylesheet_roundtrip.py` explicitly reports `surfaces.theme` Settings CSS, `surfaces.day`, and `surfaces.study` as off-scale and owed rather than done. Those modules must enter the enforced type-scale scope and pass before this finding is fixed. Human aesthetic acceptance also remains Weibao-owned |
| Settings gives appearance choices more space than learner-critical controls | UI character F1.5 and 16B settings contract | Fixed and deterministically verified | Settings has a compact preview and uses the active profile shell. `tests/settings_roundtrip.py` verifies migration, preview, save recovery, and all shipped values |
| Empty course areas tell the truth but offer no next supported action | UI character F1.5 and 16B degraded-state matrix | Fixed and deterministically verified | `tests/presentation_profiles_roundtrip.py::check_course_transition_and_degraded_state_contract` and component zero, error, and partial-state checks require a supported action or an exact blocker |
| Search or sticky chrome can cover mobile content | UI character A1.4 and V1.4 | Human owed, automated leg verified | `tests/visual_accessibility_roundtrip.py` and responsive profile fixtures cover fixed widths and reflow. Weibao owns the skipped touch-device and perceived-clarity check |
| Activity purpose and item response format are visually conflated | ACTIVITY-01, 16B Activity naming warning, user direction | Fixed and deterministically verified | `presentation.activity_frame()` orders Purpose before Response format. `tests/presentation_profiles_roundtrip.py::check_activity_separation` covers every purpose and shipped response format |
| Profile and appearance settings could become one accidental theme switch | UI character selected-pair contract and extension delivery | Fixed and deterministically verified | `tests/settings_roundtrip.py::check_axis_independence_and_shipped_values` verifies profile, home mode, look, theme, contrast, accent, density, and motion remain independent |
| State coverage is incomplete if only happy-path screens are compared | 16B degraded-state matrix, 17A component matrix, 17B G8 | Fixed for deterministic state coverage, human owed for perception | Profile, home, and component suites cover populated, empty, loading, unavailable, conflict, interrupted, pending, invalid, and recovery states. Weibao owns the skipped visual and screen-reader comparison |

## External inspiration routed into Phase 20

The detailed fact, adaptation, rejection, and acceptance mapping lives in `20-INSPIRATION-MATRIX.md`. Its current plan ownership is:

| Pattern family | Terminal disposition |
|---|---|
| Canvas, Moodle, Google Classroom, and Khan Academy home projections | Adapted and deterministically verified in `tests/home_roundtrip.py`. Resume and Shelf are retained. Agenda remains a registered prototype pending Weibao's comparison |
| Duolingo and Open edX course path and navigation | Adapted and deterministically verified. Path remains a registered prototype pending Weibao's comparison. Stable course navigation is verified in profile and IA-route suites |
| Kolibri offline, interruption, and degraded-state behavior | Adapted and deterministically verified in IA-route, profile, serve, and transition fixtures |
| Runestone lesson-to-check flow and H5P-style capability description | Adapted and deterministically verified in profile, component, settings, and adapter-manifest fixtures |
| PrairieLearn authoring-time variants and Anki scheduling separation | PrairieLearn runtime generation rejected and absent. Authoring-time variants remain externally owned by the future authoring plan. Anki separation is verified in `tests/home_roundtrip.py` |

## Inherited contracts, not reopened

| Contract | Current disposition |
|---|---|
| One parser, scorer, evidence authority, and runtime-owned disclosure | Binding. Phase 20 changes derived presentation only |
| Five shared type sizes, existing spacing scale, 6/8/12px role-based radii, 44px project targets | Reused unless a measured Phase 20 comparison proves a conflict |
| Stable course routes, deep links, parent and Back behavior, exact resume | Binding from 16B. Task 3 adds missing observable coverage |
| Reader measure, glossary focus return, one live-status region, wrong-answer disclosure rules | Binding from 13.5 and 17A |
| Human visual and screen-reader acceptance | Remains human-owned. Automation may prepare evidence only |

## Routed elsewhere

| Finding | Disposition and owner |
|---|---|
| Reach walkthrough and instructional-quality proof | Phase 19D. Phase 20 may consume its evidence but cannot claim or replace it |
| Clean-package restore losses | Phase 17C and the existing recovery owners |
| External-user cold install | Phase 18 human leg |
| Shipped `shelf`, `next-action`, `agent`, and `split` home modes | Preserve all four. `shelf` remains default. Phase 20-02 tests both presentation profiles and migration without silent deletion or rename |
| Resume, Shelf, Agenda, and Path learner jobs | Phase 20-02 maps Resume and Shelf to existing modes first. Agenda and Path prototype without stable setting values until human review retains, combines, or supersedes them |
| Full migration of Agent, Sources, Map, Evidence, authoring, export, and integrations | Agent, Sources, Map, Evidence, and Build use the shared course frame. Settings uses the active profile shell. Authoring, export, and MCP retain their deterministic output identity through the named `authoring-export-integrations` compatibility adapter |
| External extension packages, package loading, runtime fetching, and live reload | EXT-05 decision gate, not Phase 20 |

## Phase closure status

Every current row above has a terminal disposition and either deterministic
evidence, an exact blocked condition, or a named owner. Phase 20 itself remains
blocked from full closure by three gates outside this Task 3 write: the owed
Settings, Day, and Study type-scale enforcement reported by the stylesheet
suite, Weibao's skipped human visual, touch, and screen-reader acceptance, and
the unavailable `tests/daemon_roundtrip.py` transition gate recorded in
`20-TRANSITION-GATES.md`. The runner terminates that full suite at about 30
seconds before a result. It is owed and none of these conditions is represented
as passed.

## Reopen triggers

- A Phase 20 fixture shows that an inherited contract blocks a supported learner task.
- The Phase 19D walkthrough adds a state or transition missing from this crosswalk.
- A profile needs a different route, scorer, state store, or disclosure path. Treat that as a design defect, not permission to fork authority.
- A retained home projection cannot demonstrate a distinct learner job during comparison.
