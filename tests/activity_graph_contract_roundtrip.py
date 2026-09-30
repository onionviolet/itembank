"""P5 immutable graph proposal, synthetic runtime sittings only."""
from dataclasses import FrozenInstanceError, asdict, replace
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototypes/activity-graph-contract-20260930"
sys.path[:0] = [str(ROOT), str(PROTO)]
import evidence
import journal
import runtime
from surfaces import session
from activity_graph import Edge, Graph, Journey, Node, Refusal, example_graph

CASE = dict(version=1, activity_id="synthetic:counter-staged",
            stimulus="A fictional counter starts at 3 and adds 2 once.",
            children=["a200000000000001", "a200000000000002"], order=["answer", "reason"])


class ActivityGraph(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.graph = example_graph()
        self.bank = self.base / "bank.md"
        text = (ROOT / "prototypes/audit-question-families/fixtures/bank.md").read_text()
        self.bank.write_text("STAGED-CASES: " + json.dumps([CASE]) + "\n" + text[:text.index("Q3.")])
        self.sitting = self.base / "sitting.json"

    def start(self, mode="practice"):
        session.do_start(str(self.bank), {"count": 2, "selection_mode": "exam"},
                         mode, str(self.sitting), False)
        return Journey.attach(self.base, self.graph, self.graph.revision)

    def commit(self, answer):
        activity = session.do_next(str(self.sitting))["activity"]
        return session.do_action(str(self.sitting), dict(kind="submit", answer=answer, **{
            k: activity[k] for k in ("activity_id", "child_id", "submission_token")}))

    def finish(self, obj, branch="choose-a"):
        self.commit("B")
        self.commit("B")
        obj.follow(branch, obj.revision())

    def test_immutable_identity_and_revision(self):
        self.graph.validate()
        with self.assertRaises(FrozenInstanceError):
            self.graph.nodes[0].id = "changed"
        changed = replace(self.graph, nodes=(self.graph.nodes[0], replace(
            self.graph.nodes[1], transcript=("Changed demand.",)), *self.graph.nodes[2:]))
        self.assertEqual(changed.occurrence_id, self.graph.occurrence_id)
        self.assertNotEqual(changed.revision, self.graph.revision)
        with self.assertRaises(Refusal):
            replace(self.graph, nodes=list(self.graph.nodes)).validate()

    def test_portable_declaration_and_unknown_policy_fields(self):
        declaration = json.loads(json.dumps(asdict(self.graph)))
        self.assertEqual(Graph.from_declaration(declaration), self.graph)
        self.assertEqual(Graph.from_declaration(declaration).revision, self.graph.revision)
        declaration["edges"][0]["when_correct"] = True
        with self.assertRaises(Refusal):
            Graph.from_declaration(declaration)

    def test_cycle_missing_destination_duplicate_unreachable_and_dead_end(self):
        mutations = [
            replace(self.graph, edges=self.graph.edges + (Edge("cycle", "route-a", "case", ("practice",)),)),
            replace(self.graph, edges=(replace(self.graph.edges[0], target="missing"), *self.graph.edges[1:])),
            replace(self.graph, nodes=self.graph.nodes + (self.graph.nodes[0],)),
            replace(self.graph, edges=self.graph.edges + (self.graph.edges[0],)),
            replace(self.graph, nodes=self.graph.nodes + (Node("orphan", "ending", ("practice",), ending="descriptive"),)),
            replace(self.graph, edges=self.graph.edges[1:]),
            replace(self.graph, edges=tuple(e for e in self.graph.edges if e.id != "finish-a")),
        ]
        for graph in mutations:
            with self.subTest(graph=graph), self.assertRaises(Refusal):
                graph.validate()

    def test_invalid_endings_formal_choices_and_timed_refusal(self):
        for ending in ("mastered", "descriptive"):
            nodes = (*self.graph.nodes[:-1], replace(self.graph.nodes[-1], ending=ending))
            with self.assertRaises(Refusal):
                replace(self.graph, nodes=nodes).validate()
        edges = (*self.graph.edges[:-1], replace(self.graph.edges[-1], policy="choice"))
        with self.assertRaises(Refusal):
            replace(self.graph, edges=edges).validate()
        obj = self.start()
        data = runtime.read_session(str(self.sitting))
        data["timing"] = {"synthetic": True}
        runtime.write_session(str(self.sitting), data)
        with self.assertRaisesRegex(Refusal, "Timed"):
            obj.view()

    def test_required_skip_and_policy_refusal(self):
        nodes = tuple(replace(n, required=True) if n.id == "route-a" else n for n in self.graph.nodes)
        with self.assertRaisesRegex(Refusal, "skip"):
            replace(self.graph, nodes=nodes).validate()
        for policy in ("correct", "incorrect", "score", "continue"):
            edges = (replace(self.graph.edges[0], policy=policy), *self.graph.edges[1:])
            with self.subTest(policy=policy), self.assertRaises(Refusal):
                replace(self.graph, edges=edges).validate()

    def test_multiple_units_preserve_runtime_order_and_do_not_expose_next_child(self):
        text = self.bank.read_text()
        body = text[text.index("Q1."):]
        second = body.replace("Q1.", "Q3.").replace("Q2.", "Q4.").replace(
            "a200000000000001", "a200000000000003").replace("a200000000000002", "a200000000000004")
        second = second.replace("Q3. What", "Q3. Again, what").replace("Q4. Which", "Q4. Again, which")
        second_case = dict(CASE, activity_id="synthetic:second",
                           children=["a200000000000003", "a200000000000004"])
        self.bank.write_text("STAGED-CASES: " + json.dumps([CASE, second_case]) + "\n" + body + second)
        second_node = Node("case2", "assessment", required=True, activity_id=second_case["activity_id"],
                           children=tuple(second_case["children"]))
        self.graph = replace(self.graph, nodes=(self.graph.nodes[0], second_node, *self.graph.nodes[1:]),
            edges=(Edge("next-case", "case", "case2"), *tuple(
                replace(e, source="case2") if e.source == "case" else e for e in self.graph.edges)))
        session.do_start(str(self.bank), {"count": 4, "pair": "a2-counter"}, "practice", str(self.sitting), False)
        obj = Journey.attach(self.base, self.graph, self.graph.revision)
        self.commit("B")
        self.commit("B")
        self.assertNotIn("item", obj.view()["assessment"])
        obj.follow("next-case", obj.revision())
        self.assertEqual(obj.view()["assessment"]["activity"]["stage"], "answer")
        with self.assertRaises(Refusal):
            obj.follow("choose-a", obj.revision())
        self.commit("B")
        self.commit("B")
        obj.follow("choose-a", obj.revision())
        self.assertEqual(obj.view()["denominators"]["assessment_selected_children"], 4)

    def test_whole_unit_and_accepted_revision(self):
        for spec in ({"count": 1}, {"count": 2, "objective": "synthetic:counter-result"}):
            with self.assertRaises(SystemExit):
                session.do_start(str(self.bank), spec, "practice", str(self.sitting), False)
        obj = self.start()
        with self.assertRaises(Refusal):
            Journey.attach(self.base, self.graph, "stale")
        self.assertEqual(obj.view()["node"], "case")
        bad = replace(self.graph, nodes=(replace(self.graph.nodes[0], children=tuple(reversed(CASE["children"]))), *self.graph.nodes[1:]))
        with self.assertRaises(Refusal):
            Journey(self.base, bad)._runtime()

    def test_no_jump_before_commit_or_between_children(self):
        obj = self.start()
        original = obj.sidecar.read_bytes()
        for edge in ("choose-a", "finish-a", "formal-finish", "missing"):
            with self.assertRaises(Refusal):
                obj.follow(edge, obj.revision())
        self.commit("B")
        with self.assertRaises(Refusal):
            obj.follow("choose-a", obj.revision())
        self.assertEqual(obj.sidecar.read_bytes(), original)
        self.assertNotIn("score", json.dumps(obj.view()))
        self.assertNotIn("panels", obj.render())

    def test_checkpoint_restart_cancel_and_valid_ending(self):
        obj = self.start()
        self.finish(obj, "choose-b")
        obj.checkpoint(0, False, obj.revision())
        view = obj.view()
        self.assertEqual(view["choices"], [])
        for anchor, declared in ((-1, True), (99, True), (True, False), (0, "yes")):
            with self.assertRaises(Refusal):
                obj.checkpoint(anchor, declared, obj.revision())
        obj.cancel(obj.revision())
        cancelled = obj.sidecar.read_bytes()
        with self.assertRaises(Refusal):
            obj.checkpoint(1, True, obj.revision())
        self.assertEqual(cancelled, obj.sidecar.read_bytes())
        restarted = Journey(self.base, example_graph())
        self.assertEqual(restarted.view()["node"], "route-b")
        self.assertEqual(restarted.view()["checkpoint"], {"anchor": 0, "reported_read": False})
        self.assertTrue(restarted.view()["cancelled"])
        restarted.resume(restarted.revision())
        restarted.checkpoint(1, True, restarted.revision())
        restarted.follow("finish-b", restarted.revision())
        self.assertEqual(restarted.view()["ending"], "descriptive")
        with self.assertRaises(Refusal):
            restarted.follow("choose-a", restarted.revision())

    def test_fresh_process_reopens_same_branch_and_anchor(self):
        obj = self.start()
        self.finish(obj)
        obj.checkpoint(1, False, obj.revision())
        code = "import sys,json;sys.path.insert(0,sys.argv[1]);from activity_graph import Journey,example_graph;print(json.dumps(Journey(sys.argv[2],example_graph()).view()))"
        result = subprocess.run([sys.executable, "-c", code, str(PROTO), str(self.base)],
                                check=True, capture_output=True, text=True)
        view = json.loads(result.stdout)
        self.assertEqual(view["node"], "route-a")
        self.assertEqual(view["checkpoint"], {"anchor": 1, "reported_read": False})

    def test_stale_graph_bank_session_and_cas_preserve_state(self):
        obj = self.start()
        self.finish(obj)
        original = obj.sidecar.read_bytes()
        changed = replace(self.graph, occurrence_id="other")
        with self.assertRaises(Refusal):
            Journey(self.base, changed).view()
        changed = replace(self.graph, nodes=(self.graph.nodes[0], replace(
            self.graph.nodes[1], transcript=("Changed transcript.",)), *self.graph.nodes[2:]))
        with self.assertRaises(Refusal):
            Journey(self.base, changed).view()
        bank = self.bank.read_bytes()
        self.bank.write_bytes(bank + b"\n")
        with self.assertRaises(SystemExit):
            obj.view()
        self.bank.write_bytes(bank)
        sitting = self.sitting.read_bytes()
        data = runtime.read_session(str(self.sitting))
        data["session_id"] = "different"
        runtime.write_session(str(self.sitting), data)
        with self.assertRaises((Refusal, SystemExit)):
            obj.view()
        self.sitting.write_bytes(sitting)
        with self.assertRaises(journal.JournalError):
            obj.checkpoint(1, True, "stale")
        self.assertEqual(original, obj.sidecar.read_bytes())

    def test_out_of_band_presentation_conflict_and_runtime_recovery_required(self):
        obj = self.start()
        original = obj.sidecar.read_bytes()
        state = json.loads(original)
        state["path"] = ["formal-end"]
        obj.sidecar.write_bytes(obj.encode(state))
        with self.assertRaisesRegex(Refusal, "conflict"):
            obj.view()
        obj.sidecar.write_bytes(original)
        activity = session.do_next(str(self.sitting))["activity"]
        action = dict(kind="submit", answer="B", **{k: activity[k]
            for k in ("activity_id", "child_id", "submission_token")})
        sitting = obj.sitting.read_bytes()
        with patch.object(session, "write_session", side_effect=OSError("after append")):
            with self.assertRaises(OSError):
                session.do_action(str(self.sitting), action)
        with self.assertRaisesRegex(Refusal, "recovery required"):
            obj.view()
        self.assertEqual(sitting, obj.sitting.read_bytes())
        session.do_next(str(self.sitting))
        self.assertEqual(obj.view()["assessment"]["activity"]["stage"], "reason")

    def test_journal_write_failure_preserves_checkpoint_and_sitting(self):
        obj = self.start()
        self.finish(obj)
        original = obj.sidecar.read_bytes()
        sitting = self.sitting.read_bytes()
        with patch.object(journal, "commit_operation", side_effect=OSError("injected boundary")):
            with self.assertRaises(OSError):
                obj.checkpoint(1, True, obj.revision())
        self.assertEqual(original, obj.sidecar.read_bytes())
        self.assertEqual(sitting, obj.sitting.read_bytes())

    def test_competing_choices_have_one_journal_winner(self):
        obj = self.start()
        self.commit("B")
        self.commit("B")
        expected = obj.revision()
        sitting = obj.sitting.read_bytes()
        def choose(edge):
            try:
                obj.follow(edge, expected)
                return "accepted"
            except (journal.JournalError, Refusal):
                return "refused"
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(choose, ("choose-a", "choose-b")))
        self.assertEqual(sorted(outcomes), ["accepted", "refused"])
        self.assertIn(Journey(self.base, self.graph).view()["node"], ("route-a", "route-b"))
        self.assertEqual(sitting, obj.sitting.read_bytes())

    def test_descriptive_progress_does_not_add_response_evidence(self):
        obj = self.start()
        self.finish(obj)
        log = Path(evidence.log_path(str(self.base)))
        original = log.read_bytes()
        sitting = self.sitting.read_bytes()
        obj.checkpoint(0, True, obj.revision())
        obj.follow("finish-a", obj.revision())
        self.assertEqual(obj.view()["denominators"], dict(assessment_selected_children=2,
            descriptive_selected_nodes=1, descriptive_reported_read=1, descriptive_denominator_final=True))
        self.assertEqual(log.read_bytes(), original)
        self.assertEqual(sitting, obj.sitting.read_bytes())
        rows = [r for r in evidence.events(str(log)) if r["event_type"] == "response"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r["objective"] for r in rows}), 2)
        self.assertEqual([r["score"] for r in rows], [False, True])

    def test_formal_route_identity_independent_of_correctness(self):
        routes = []
        for mode in ("exam", "diagnostic"):
            for answer in ("A", "B"):
                with tempfile.TemporaryDirectory() as directory:
                    old_base, old_bank, old_sitting = self.base, self.bank, self.sitting
                    self.base = Path(directory)
                    self.bank = self.base / "bank.md"
                    self.bank.write_bytes(old_bank.read_bytes())
                    self.sitting = self.base / "sitting.json"
                    obj = self.start(mode)
                    self.commit(answer)
                    self.assertEqual(obj.view()["choices"], [])
                    self.commit("B")
                    view = obj.view()
                    self.assertNotIn("score", json.dumps(view))
                    self.assertEqual(view["choices"], [{"id": "formal-finish", "label": "Continue"}])
                    for edge in ("choose-a", "choose-b"):
                        with self.assertRaises(Refusal):
                            obj.follow(edge, obj.revision())
                    obj.follow("formal-finish", obj.revision())
                    routes.append((obj.view()["node"], obj.render()))
                    self.base, self.bank, self.sitting = old_base, old_bank, old_sitting
        self.assertTrue(all(route == routes[0] for route in routes))

    def test_static_transcript_and_native_keyboard_controls(self):
        obj = self.start()
        self.commit("B")
        self.commit("B")
        self.assertIn('<button name="edge"', obj.render())
        self.assertNotIn("<script", obj.render())
        obj.follow("choose-a", obj.revision())
        rendered = obj.render()
        for paragraph in self.graph.nodes[1].transcript:
            self.assertIn(paragraph, rendered)
        self.assertNotIn(self.graph.nodes[2].transcript[0], rendered)
        self.assertIn('<select id="anchor"', rendered)
        self.assertIn('type="checkbox"', rendered)


if __name__ == "__main__":
    unittest.main()
