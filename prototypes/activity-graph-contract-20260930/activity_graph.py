"""Executable P5 proposal. Presentation traversal never advances a sitting."""
from dataclasses import dataclass, asdict
import copy
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import identity
import journal
import model
import runtime
from surfaces import session

MODES = ("practice", "exam", "diagnostic")


class Refusal(ValueError):
    pass


def fingerprint(value):
    return "sha256:" + hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Node:
    id: str
    kind: str
    modes: tuple = MODES
    required: bool = False
    activity_id: str = ""
    children: tuple = ()
    transcript: tuple = ()
    ending: str = ""


@dataclass(frozen=True)
class Edge:
    id: str
    source: str
    target: str
    modes: tuple = MODES
    policy: str = "continue"
    label: str = "Continue"


@dataclass(frozen=True)
class Graph:
    occurrence_id: str
    entry: str
    nodes: tuple
    edges: tuple
    version: int = 1

    @classmethod
    def from_declaration(cls, declaration):
        """Proposed graph JSON only. Banks still use the shipped parser."""
        try:
            fields = dict(declaration)
            nodes = []
            for row in fields.pop("nodes"):
                node = dict(row)
                for key in ("modes", "children", "transcript"):
                    if key in node:
                        if type(node[key]) is not list:
                            raise Refusal("JSON sequence required")
                        node[key] = tuple(node[key])
                nodes.append(Node(**node))
            edges = []
            for row in fields.pop("edges"):
                edge = dict(row)
                if "modes" in edge:
                    if type(edge["modes"]) is not list:
                        raise Refusal("JSON sequence required")
                    edge["modes"] = tuple(edge["modes"])
                edges.append(Edge(**edge))
            return cls(nodes=tuple(nodes), edges=tuple(edges), **fields).validate()
        except (TypeError, KeyError, ValueError) as exc:
            raise Refusal("Invalid graph declaration: " + str(exc)) from exc

    @property
    def revision(self):
        return fingerprint(asdict(self))

    def validate(self):
        # Frozen dataclasses alone do not freeze a caller-supplied list.
        if (self.version != 1 or not self.occurrence_id or
                type(self.nodes) is not tuple or type(self.edges) is not tuple or
                not 1 <= len(self.nodes) <= 64 or len(self.edges) > 128):
            raise Refusal("Immutable version-1 graph required")
        nodes = {n.id: n for n in self.nodes}
        if len(nodes) != len(self.nodes) or self.entry not in nodes:
            raise Refusal("Duplicate node or missing entry")
        if len({e.id for e in self.edges}) != len(self.edges):
            raise Refusal("Duplicate edge identity")
        children = []
        for n in self.nodes:
            if (any(type(x) is not str for x in (n.id, n.kind, n.activity_id, n.ending)) or
                    not n.id or type(n.modes) is not tuple or not n.modes or
                    not set(n.modes) <= set(MODES) or type(n.children) is not tuple or
                    type(n.transcript) is not tuple or type(n.required) is not bool):
                raise Refusal("Invalid immutable node")
            if n.kind == "assessment":
                if not n.activity_id or len(n.children) != 2 or n.transcript or n.ending:
                    raise Refusal("Assessment must name one whole staged pair")
                children.extend(n.children)
            elif n.kind == "transcript":
                if not n.transcript or not all(type(x) is str and x for x in n.transcript):
                    raise Refusal("Static transcript anchors required")
                if n.children or n.activity_id or n.ending or set(n.modes) != {"practice"}:
                    raise Refusal("Teaching transcripts are practice-only")
            elif n.kind == "ending":
                if n.ending not in ("descriptive", "neutral") or n.transcript or n.children or n.activity_id:
                    raise Refusal("Named ending required")
                if set(n.modes) & {"exam", "diagnostic"} and n.ending != "neutral":
                    raise Refusal("Formal endings must be neutral")
            else:
                raise Refusal("Unsupported node kind")
        if len(set(children)) != len(children):
            raise Refusal("Assessment children cannot appear twice")
        activities = [n.activity_id for n in self.nodes if n.kind == "assessment"]
        if not activities or len(set(activities)) != len(activities):
            raise Refusal("Unique staged activity identities required")
        for e in self.edges:
            if (any(type(x) is not str for x in (e.id, e.source, e.target, e.policy, e.label)) or
                    not e.id or e.source not in nodes or e.target not in nodes or
                    type(e.modes) is not tuple or not e.modes or
                    not set(e.modes) <= set(nodes[e.source].modes) & set(nodes[e.target].modes) or
                    e.policy not in ("continue", "choice") or not e.label):
                raise Refusal("Missing destination or unauthorized edge policy")
            if nodes[e.source].kind == "ending":
                raise Refusal("Endings cannot have destinations")
            if set(e.modes) & {"exam", "diagnostic"} and e.policy != "continue":
                raise Refusal("Formal routing cannot reveal a choice or correctness")
        # Validate all components, including cycles disconnected from the entry.
        def walk(node, visiting, visited):
            if node in visiting:
                raise Refusal("Cycle")
            if node in visited:
                return
            for edge in self.edges:
                if edge.source == node:
                    walk(edge.target, visiting | {node}, visited)
            visited.add(node)
        seen = set()
        for node in nodes:
            walk(node, set(), seen)
        for mode in MODES:
            if mode not in nodes[self.entry].modes:
                raise Refusal("Entry must support every mode")
            reached = set()
            paths = []
            visits = [0]
            def routes(node, path):
                visits[0] += 1
                if visits[0] > 4096:
                    raise Refusal("Route validation budget exceeded")
                reached.add(node)
                path = path + (node,)
                outgoing = [e for e in self.edges if e.source == node and mode in e.modes]
                if nodes[node].kind == "ending":
                    paths.append(path)
                    if len(paths) > 512:
                        raise Refusal("Route validation budget exceeded")
                elif not outgoing:
                    raise Refusal("Non-ending dead end")
                if mode != "practice" and len(outgoing) > 1:
                    raise Refusal("Formal route identity must be response-independent")
                if len(outgoing) > 1 and any(e.policy != "choice" for e in outgoing):
                    raise Refusal("Branch requires explicit learner choice")
                for edge in outgoing:
                    routes(edge.target, path)
            routes(self.entry, ())
            applicable = {n.id for n in self.nodes if mode in n.modes}
            if reached != applicable:
                raise Refusal("Unreachable node")
            required = {n.id for n in self.nodes if mode in n.modes and
                        (n.required or n.kind == "assessment")}
            if not paths or any(not required <= set(path) for path in paths):
                raise Refusal("Unauthorized skip of required unit")
            assessment_order = tuple(n.id for n in self.nodes if n.kind == "assessment")
            if any(tuple(n for n in path if nodes[n].kind == "assessment") != assessment_order
                   for path in paths):
                raise Refusal("Assessment route must preserve runtime unit order")
            for path in paths:
                described = False
                for name in path:
                    described |= nodes[name].kind == "transcript"
                    if described and nodes[name].kind == "assessment":
                        raise Refusal("Descriptive state cannot gate a later assessment cursor")
        return self


class Journey:
    """Journal-owned descriptive position; runtime-owned assessment position."""
    def __init__(self, base, graph):
        self.base = Path(base)
        self.graph = graph.validate()
        self.sidecar = self.base / "presentation.json"
        self.sitting = self.base / "sitting.json"
        self.nodes = {n.id: n for n in graph.nodes}

    @classmethod
    def attach(cls, base, graph, accepted_revision):
        obj = cls(base, graph)
        if accepted_revision != graph.revision:
            raise Refusal("Accepted graph revision does not match")
        data = obj._runtime()
        state = dict(object_id=identity.new_object_id(), occurrence_id=graph.occurrence_id,
                     accepted_revision=accepted_revision, session_id=data["session_id"],
                     bank_fingerprint=data["staged_cases"][0]["bank_fingerprint"],
                     path=[graph.entry], edges=[], checkpoints={}, cancelled=False)
        journal.commit_operation(str(obj.base), state["object_id"], "component",
                                 obj.sidecar.name, "mint", obj.encode(state), None,
                                 "human", "synthetic-p5", create_if_missing=True)
        return obj

    @staticmethod
    def encode(state):
        return (json.dumps(state, sort_keys=True, indent=2) + "\n").encode()

    def revision(self):
        return identity.object_fingerprint(self.sidecar.read_bytes(), "component")

    def _runtime(self):
        # Reuse the canonical reconciler only as a check. A graph never repairs
        # or writes a sitting. The existing next/action client owns recovery.
        data = runtime.read_session(str(self.sitting))
        qs = model.load(data["bank"])
        repaired = session._reconcile_staged(copy.deepcopy(data), qs)
        if repaired != data:
            raise Refusal("Runtime recovery required; use the existing next command")
        if data.get("timing"):
            raise Refusal("Timed route support requires the runtime expiry projection")
        cases = data.get("staged_cases", [])
        assessment = [n for n in self.graph.nodes if n.kind == "assessment"]
        selected = tuple(qs[i].get("item_id") for i in data["items"])
        declared = tuple(c for n in assessment for c in n.children)
        if selected != declared or len(cases) != len(assessment):
            raise Refusal("Select complete staged units in declared runtime order")
        for node, case in zip(assessment, cases):
            if node.activity_id != case["activity_id"] or node.children != tuple(case["children"]):
                raise Refusal("Staged unit binding differs")
        return data

    def state(self):
        state = json.loads(self.sidecar.read_text())
        registered = journal.read_registry(str(self.base)).get(state["object_id"], {})
        if registered.get("fingerprint") != self.revision():
            raise Refusal("Presentation conflict; restore or reconcile through the journal")
        data = self._runtime()
        if (state["accepted_revision"] != self.graph.revision or
                state["occurrence_id"] != self.graph.occurrence_id or
                state["session_id"] != data["session_id"] or
                state["bank_fingerprint"] != data["staged_cases"][0]["bank_fingerprint"]):
            raise Refusal("Stale graph, occurrence or sitting; preserve original files")
        return state, data

    def _save(self, state, expected):
        return journal.commit_operation(str(self.base), state["object_id"], "component",
                                        self.sidecar.name, "edit_in_place", self.encode(state),
                                        expected, "human", "synthetic-p5")

    def _ready(self, node, state, data):
        if node.kind == "assessment":
            case = next(c for c in data["staged_cases"] if c["activity_id"] == node.activity_id)
            return data["cursor"] > case["positions"][-1]
        if node.kind == "transcript":
            return state["checkpoints"].get(node.id, {}).get("reported_read", False)
        return False

    def view(self):
        state, data = self.state()
        node = self.nodes[state["path"][-1]]
        ready = self._ready(node, state, data)
        edges = [dict(id=e.id, label=e.label) for e in self.graph.edges
                 if e.source == node.id and data["mode"] in e.modes] if ready and not state["cancelled"] else []
        result = dict(occurrence_id=self.graph.occurrence_id, accepted_revision=self.graph.revision,
                      node=node.id, kind=node.kind, revision=self.revision(), choices=edges,
                      cancelled=state["cancelled"], ending=node.ending or None)
        descriptive = [n for n in state["path"] if self.nodes[n].kind == "transcript"]
        result["denominators"] = dict(assessment_selected_children=len(data["items"]),
            descriptive_selected_nodes=len(descriptive),
            descriptive_reported_read=sum(bool(state["checkpoints"].get(n, {}).get("reported_read"))
                                          for n in descriptive),
            descriptive_denominator_final=node.kind == "ending")
        if node.kind == "assessment":
            # No private response rows, scores, keys or feedback enter branch policy.
            result["assessment"] = (dict(activity_id=node.activity_id, commitment="complete")
                if ready else runtime.session_view(data, model.load(data["bank"])))
        if node.kind == "transcript":
            result.update(transcript=node.transcript, checkpoint=state["checkpoints"].get(node.id, {}))
        return result

    def follow(self, edge_id, expected):
        state, data = self.state()
        node = self.nodes[state["path"][-1]]
        edge = next((e for e in self.graph.edges if e.id == edge_id), None)
        if (state["cancelled"] or edge is None or edge.source != node.id or
                data["mode"] not in edge.modes or not self._ready(node, state, data)):
            raise Refusal("Unopened destination or uncommitted unit")
        state["path"].append(edge.target)
        state["edges"].append(edge.id)
        return self._save(state, expected)

    def checkpoint(self, anchor, reported_read, expected):
        state, _ = self.state()
        node = self.nodes[state["path"][-1]]
        if (state["cancelled"] or node.kind != "transcript" or type(anchor) is not int or
                not 0 <= anchor < len(node.transcript) or type(reported_read) is not bool):
            raise Refusal("Valid transcript anchor and explicit declaration required")
        state["checkpoints"][node.id] = dict(anchor=anchor, reported_read=reported_read)
        return self._save(state, expected)

    def cancel(self, expected):
        state, _ = self.state()
        state["cancelled"] = True
        return self._save(state, expected)

    def resume(self, expected):
        state, _ = self.state()
        state["cancelled"] = False
        return self._save(state, expected)

    def render(self):
        view = self.view()
        esc = lambda x: html.escape(str(x), quote=True)
        parts = ['<h1>Synthetic activity</h1>', '<p>Descriptive progress is not a grade.</p>']
        for i, text in enumerate(view.get("transcript", ())):
            parts.append('<p id="anchor-' + str(i) + '">' + esc(text) + '</p>')
        if view.get("transcript") and not view["cancelled"]:
            parts.append('<form method="post"><label for="anchor">Transcript position</label><select id="anchor" name="anchor">')
            for i in range(len(view["transcript"])):
                selected = ' selected' if i == view["checkpoint"].get("anchor", 0) else ''
                parts.append('<option value="' + str(i) + '"' + selected + '>Paragraph ' + str(i + 1) + '</option>')
            parts.append('</select><label><input type="checkbox" name="reported_read">I report reading this transcript</label><button>Save checkpoint</button></form>')
        if view["kind"] == "assessment":
            parts.append('<p>Continue the existing runtime sitting.</p>')
        for edge in view["choices"]:
            parts.append('<button name="edge" value="' + esc(edge["id"]) + '">' + esc(edge["label"]) + '</button>')
        if view["ending"]:
            parts.append('<p>Activity ended. Completion describes this route only.</p>')
        return '\n'.join(parts)


def example_graph():
    return Graph("synthetic:p5-occurrence", "case", (
        Node("case", "assessment", required=True, activity_id="synthetic:counter-staged",
             children=("a200000000000001", "a200000000000002")),
        Node("route-a", "transcript", ("practice",), transcript=(
            "Fictional lantern: compare two painted panels.", "Describe one visible difference.")),
        Node("route-b", "transcript", ("practice",), transcript=(
            "Fictional lantern: trace the outline of one panel.", "Describe one visible similarity.")),
        Node("read-end", "ending", ("practice",), ending="descriptive"),
        Node("formal-end", "ending", ("exam", "diagnostic"), ending="neutral")), (
        Edge("choose-a", "case", "route-a", ("practice",), "choice", "Compare panels"),
        Edge("choose-b", "case", "route-b", ("practice",), "choice", "Trace a panel"),
        Edge("finish-a", "route-a", "read-end", ("practice",)),
        Edge("finish-b", "route-b", "read-end", ("practice",)),
        Edge("formal-finish", "case", "formal-end", ("exam", "diagnostic"))))


if __name__ == "__main__":
    graph = example_graph().validate()
    print(json.dumps(dict(proposal=asdict(graph), proposed_revision=graph.revision), indent=2))
