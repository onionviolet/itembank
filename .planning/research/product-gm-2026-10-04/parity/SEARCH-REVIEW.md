# F1 independent search review

STATUS: review released; two concrete findings need source-owner resolution

Read-only review on October 4 compared the two owned modules to the ignored
`parity-search/before/*.py.txt` snapshots and inspected the new search suite.
Only this report was written. Reproductions used temporary synthetic fixture
directories and did not alter repository source or private data. No broad suite
was rerun. The findings were sent to the parent implementation owner.

## Findings

**F1-R1, medium: late stale-source removal can end a page before remaining
valid matches.** `course_source_search.search` stops collecting at
`offset + MAX_HITS + 1` before its final cross-source re-admission. If an early
source becomes stale while a later source is searched, the final filter drops
the early hits but does not refill from the later source or remaining corpus.
The result then has no next page despite valid unscanned matches.

Exact executed reproduction: use the existing `CourseSourceSearch` synthetic
fixture; add `early.md` with 32 literal `needle` matches and `later.md` with 70.
Patch `_safe_source` to rewrite `early.md` to `CHANGED` only on the first
admission of `later.md`, after the early source's post-scan check. Call
`search(base, 'needle')`. Observed result:

```text
hits=1, later_hits=1, next_offset=None, more_matches=False, limited=True
omissions=['assessment', 'stale']
```

A fresh call after the same mutation returns 32 valid later hits and
`next_offset=32`. No stale snippets leaked, but pagination fairness fails.
Requested hunk: the hit-limit stop at `course_source_search.py:145-146` and
final recheck/filter at `149-170` must resume bounded scanning or refill after
removed sources, or expose an explicit retry-needed state without implying the
remaining page is terminal. A bounded retry/refill must retain admission and
source/passages/bytes caps. Add a regression that removes actual captured
matches. The current fairness test invalidates `refs[0]`, which contributes no
`STRASSE` hits, so cannot catch lost page slots.

**F1-R2, medium: a rejected partial expansion skips a valid later Unicode
match.** The new insensitive course search reuses the preexisting
`research_context._literal_ranges`. Its projection correctly rejects a match
that selects only part of an expanded character, but advances the folded cursor
to the rejected match's end. That can skip the next valid start.

Executed reproduction:

```python
list(_literal_ranges('sß', 'ss', False))  # observed []
# Expected [(1, 2)]: original text[1:2] is 'ß', whose casefold is 'ss'.
```

The first folded candidate projects to `sß` and is correctly rejected. Advancing
to `stop=2` skips valid folded start 1. Requested hunk:
`research_context.py:119-122`, advance to `found + 1` on a rejected projection;
retain `stop` after a valid yield to preserve existing non-overlapping match
semantics. Add helper and insensitive course-route regressions for this case.
The helper bug predates this delta, but F1 newly exposes it in course-wide
search. Existing `Straße` and single `s` tests do not cover an invalid candidate
before a valid expansion.

## Verified by inspection and review limits

Hidden-source admission remains centralized: search walks only accepted course
source rows, requires read and quote grants, checks registered kind and current
object state, and uses `_safe_source` for accepted fingerprint, rooted path,
locator-sidecar and assessment exclusion. Returned snippets are re-admitted
both per source and at the end. No new discovery, private-note scope or model
egress appears in this delta. Existing compatibility tests cover unregistered,
private-note and assessment exclusion; they were inspected, not rerun here.

The new default is still case-sensitive. Valid Unicode results use original
offsets and original-length highlights; direct search rejects boolean offsets,
noninteger offsets and nonboolean modes. Research forms retain duplicate-field
rejection through `_one`, whitelist operation fields, parse offset bounds, and
accept only empty or `yes` capitalization values. Exact-match preview validates
original substring content and current quote rights, and its return form carries
query, mode and offset. The inspected native test exercises page 32, preview,
return and daemon restart.

Source, passage and byte coverage limits are disclosed separately from the
32-hit page size and maximum offset. The R1 response does say more content or
matches may remain, so this review does not claim a false completeness promise;
the concrete gap is lack of a correct continuation or an explicit retry state.
No accessibility, full browser rendering, package, installation or learning
quality acceptance is claimed. Files were sampled by symbols after delta review.

## Reviewed pins and recovery

| File | Before SHA-256 | Reviewed SHA-256 |
| --- | --- | --- |
| `surfaces/course_source_search.py` | `6f6fbb6c21b44a022c77fdac6200de9f9c436d8a63224f4667d0734ecb25ffdf` | `32d76eb95f975752cabce433830dc01e4cec71c3b760fa776b9decff59b9af9d` |
| `surfaces/research_context.py` | `504d12c3e95683e51ab2560cfb38b62348c23f71d16fc3098a1a84132b56b4b6` | `7dc517ab1587b56bc3d2fdf15cb47a121810c5eae70d1470f6e2dd9a99f3a562` |
| `tests/product_gm_parity_search_roundtrip.py` | New file | `5fca1df8538dbef5b6e2ffd1729ec536ba6b87538a2cec5210c609ebca3d0e1e` |

Undo this review by removing only this report if no later editor has changed
it. Temporary fixture reproductions were cleaned by their existing cleanup
handlers. Source-owner fixes and their new gate receipts need a subsequent
review; these observations refer to the exact pins above.

## Final bounded re-review after owner repairs

CURRENT STATUS: F1-R1 and F1-R2 resolved at the pins below; all unblocked
reviewed source work released for integration. Original findings above remain
as the dated pre-repair record.

| File | Repaired SHA-256 verified locally |
| --- | --- |
| `surfaces/course_source_search.py` | `6d9c5120783635bc14411c5eed5faf7d1ce0712ce200388f2b2f74ddc3b8b1e9` |
| `surfaces/research_context.py` | `caac56e280bceb80cbce4b538d03725efd573c71714b3ed30d93fd00526a49af` |
| `tests/product_gm_parity_search_roundtrip.py` | `ecc88fcbe6bca7981fe3a98e521c76193ab515c6f0bfdd62a7bed345a85c72c2` |

Re-ran only the two exact synthetic reproductions, with exit 0. Late removal
after a hit-limited scan now sets `retry_required`, withholds all page hits and
keeps the stale omission. The rendered status explicitly says no matches are
released and supplies `Retry current course search page`. Its parsed form
retained exact query `needle`, insensitive mode `yes`, and offset `0`; applying
that form after the same mutation returned 32 later-source hits and next offset
32. The output no longer presents a sparse valid terminal page. The first
re-review probe called a nonexistent rendering helper, then the completed probe
used the actual `panel` helper and passed.

The exact Unicode reproduction now returns `[(1, 2)]` for `sß` and `ss` in
insensitive mode. Inspection confirms rejected projections advance `found + 1`
while successful matches retain `stop`. The two new regressions cover actual
captured-slot removal and the Unicode case, including native highlighting.
Their broader gate receipts were reported by the owner, not rerun by this
reviewer.

F2's source review and exact current assignment links are released, but full
detour continuity remains partial: current reading and lesson return controls
lead to Learn or the course overview, rather than the exact originating source
review. Parent integration request I1 owns that shared route/UI return gate.
This report does not claim full F2 continuity until I1's normal-route gate
passes. No production file was edited during either review.
