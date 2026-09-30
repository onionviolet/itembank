# Immutable activity graph proposal

Executable P5 readiness, not a registered bank format or production feature.
All inputs are fictional and local. The shipped parser, staged session v4,
scorer, evidence writer and operation journal remain authoritative.

Run from the repository root:

```sh
python3 prototypes/activity-graph-contract-20260930/activity_graph.py
python3 tests/activity_graph_contract_roundtrip.py
```

The first command prints portable proposed graph JSON and its content
fingerprint. `Graph.from_declaration(payload["proposal"])` validates and
freezes it. `Journey.attach(base, graph, accepted_revision)` binds that exact
revision to an already started synthetic `sitting.json`. The test is the
executable setup and operation example. Supplying a fingerprint in this
prototype simulates reviewer acceptance; it does not implement acceptance.

`Journey.follow(edge_id, expected_presentation_fingerprint)` journals a
descriptive route choice. `checkpoint(anchor, reported_read, expected)` saves
a zero-based transcript paragraph and explicit declaration. `cancel(expected)`
preserves that position; `resume(expected)` reopens it. Constructing another
`Journey` reopens the same route without a new attempt or occurrence. A new
sitting is a separate action through the existing runtime, never a graph reset.

`render()` produces a static preview of only the open node. It includes native
button, select and checkbox markup for a future keyboard client, but has no
HTTP handler or wired form submission. Plain transcript strings remain fully
readable without HTML or JavaScript. Keyboard operation, screen readers and
touch have not been verified in a browser. No media player is implemented.

See the named [readiness report](../../.planning/research/question-types-2026-09-25/ACTIVITY-GRAPH-READINESS-2026-09-30.md)
for authority, decisions, exact checks, fingerprints and promotion gates.
