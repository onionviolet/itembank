"""Fictional fixed-span readiness adapter, never a production bank parser.

The shipped model parses banks. This adapter validates a proposed JSON
declaration and projects it onto existing multi options. Only the shipped
session runtime scores responses, records evidence and releases feedback.
"""
import copy
import hashlib
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import course
import graph
import identity
import journal
import model
import runtime
from surfaces import course_ops, session

HERE = Path(__file__).resolve().parent
PASSAGE = "Café 🧭: Add two. Start at three. Add two."


class Refusal(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def refuse(code, message):
    raise Refusal(code, message)


def digest(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def revision(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")))


def validate(base, declaration, question):
    """Prototype contract validation; no bank syntax or correctness logic."""
    fields = {"version", "binding_ref", "source_ref", "source_bytes_fingerprint", "offset_unit",
              "passage_fingerprint", "anchors"}
    if not isinstance(declaration, dict) or set(declaration) != fields:
        refuse("declaration", "Use the closed fixed-anchor declaration.")
    if type(declaration["version"]) is not int or declaration["version"] != 1:
        refuse("version", "Only fixed-anchor version 1 is supported.")
    if declaration["offset_unit"] != "unicode-code-point":
        refuse("offset-unit", "Offsets count Unicode code points, not UTF-16 or bytes.")
    read = course.read_course(str(base))
    accepted = course.accepted_reading_graph(str(base), read["fingerprint"])
    ref = declaration["binding_ref"]
    if not isinstance(ref, dict) or set(ref) != {"binding_id", "binding_revision_id"}:
        refuse("binding", "Pin a permanent accepted binding revision.")
    try:
        for field, value in ref.items():
            graph._opaque_id(value, field)
    except graph.GraphError as error:
        refuse("binding", str(error))
    bindings = [row for row in accepted["doc"]["bindings"]
                if all(row.get(key) == value for key, value in ref.items())]
    if len(bindings) != 1:
        refuse("binding", "Restore the exact accepted binding revision.")
    if question.get("objective") != bindings[0].get("objective"):
        refuse("objective-mismatch", "The item must name the pinned binding objective.")
    source = declaration["source_ref"]
    if not isinstance(source, dict) or set(source) != {
            "source_object_id", "source_fingerprint", "locator", "range"}:
        refuse("source-ref", "Use the existing closed reading source reference.")
    try:
        graph._opaque_id(source["source_object_id"], "source_object_id")
        for field, value in (("source_fingerprint", source["source_fingerprint"]),
                             ("source_bytes_fingerprint", declaration["source_bytes_fingerprint"]),
                             ("passage_fingerprint", declaration["passage_fingerprint"])):
            graph._fingerprint(value, field)
    except graph.GraphError as error:
        refuse("source-ref", str(error))
    if not isinstance(source["locator"], str):
        refuse("source-ref", "Locator must be authored text.")
    if any(source.get(key) != bindings[0].get(key) for key in
           ("source_object_id", "source_fingerprint", "locator")):
        refuse("binding-mismatch", "Source and locator must match the pinned binding.")
    selected = source["range"]
    if not isinstance(selected, dict) or set(selected) != {
            "span_id", "locator_id", "locator_sidecar_fingerprint"}:
        refuse("range", "Pin one existing normalized span and its locator provenance.")
    if not isinstance(selected["span_id"], str) or not selected["span_id"]:
        refuse("range", "Name one normalized span.")
    if (selected["locator_id"] is None) != (selected["locator_sidecar_fingerprint"] is None):
        refuse("range", "Both adapter locator fields must be present or null.")
    if selected["locator_id"] is not None:
        if not isinstance(selected["locator_id"], str) or not selected["locator_id"]:
            refuse("range", "Adapter locator ID must be nonempty text.")
        try:
            graph._fingerprint(selected["locator_sidecar_fingerprint"], "locator_sidecar_fingerprint")
        except graph.GraphError as error:
            refuse("range", str(error))
    # Existing owner checks rights, accepted bytes, approved root, adapter
    # locator provenance and exact source revision. Never resolve by filename.
    passage = course.validate_reading_source(str(base), source)["verbatim"]
    source_row = journal.read_registry(str(base))[source["source_object_id"]]
    raw = (Path(base) / source_row["path"]).read_bytes()
    if "sha256:" + hashlib.sha256(raw).hexdigest() != declaration["source_bytes_fingerprint"]:
        refuse("source-bytes-stale", "Restore the exact source bytes before resuming.")
    if digest(passage) != declaration["passage_fingerprint"]:
        refuse("passage-stale", "Retain selection and review the pinned passage.")
    anchors = declaration["anchors"]
    if not isinstance(anchors, list) or not 1 <= len(anchors) <= 64:
        refuse("anchors", "Declare between one and 64 fixed spans.")
    seen_ids, seen_options, ranges = set(), set(), []
    for anchor in anchors:
        if not isinstance(anchor, dict) or set(anchor) != {
                "id", "option", "label", "start", "end", "quote"}:
            refuse("anchor", "Use the closed anchor shape.")
        ident, option = anchor["id"], anchor["option"]
        if (not isinstance(ident, str) or not ident or len(ident) > 64 or
                any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in ident) or
                ident in seen_ids):
            refuse("anchor-id", "Anchor IDs must be unique lowercase tokens.")
        if not isinstance(option, str) or option in seen_options:
            refuse("option", "Each multi option maps to one distinct anchor.")
        if not isinstance(anchor["label"], str) or not anchor["label"].strip():
            refuse("label", "Give each anchor a visible label.")
        start, end = anchor["start"], anchor["end"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(passage):
            refuse("offset", "Use nonempty half-open offsets within the passage.")
        if not isinstance(anchor["quote"], str) or passage[start:end] != anchor["quote"]:
            refuse("quote", "Quote must exactly match the declared occurrence.")
        if any(start < old_end and old_start < end for old_start, old_end in ranges):
            refuse("overlap", "Version 1 requires disjoint fixed spans.")
        seen_ids.add(ident); seen_options.add(option); ranges.append((start, end))
    if question["type"] != "multi" or seen_options != set(question["opts"]):
        refuse("projection", "Fixed spans must cover exactly the existing multi options.")
    return passage


def make_declaration(binding, source_id, source_fp):
    entries = [("rule-first", "A", "Rule sentence", 8, 16),
               ("start", "B", "Initial state", 17, 32),
               ("rule-second", "C", "Rule sentence", 33, 41)]
    return {"version": 1, "binding_ref": {key: binding[key] for key in
            ("binding_id", "binding_revision_id")}, "source_ref": {
            "source_object_id": source_id, "source_fingerprint": source_fp,
            "locator": "line 1", "range": {"span_id": "sp-0", "locator_id": None,
            "locator_sidecar_fingerprint": None}}, "offset_unit": "unicode-code-point",
            "source_bytes_fingerprint": digest(PASSAGE + "\n"),
            "passage_fingerprint": digest(PASSAGE), "anchors": [
            {"id": ident, "option": option, "label": label, "start": start,
             "end": end, "quote": PASSAGE[start:end]}
            for ident, option, label, start, end in entries]}


class Journey:
    """Single-process readiness tracer; draft is presentation, not evidence."""
    def __init__(self, base):
        self.base = Path(base)
        self.bank = self.base / "bank.md"
        self.sitting = self.base / "sitting.json"
        self.sidecar = self.base / "anchor-draft.json"

    @classmethod
    def create(cls, root, mode="exam"):
        if mode not in ("practice", "exam", "diagnostic"):
            refuse("mode", "Use an actual shipped feedback mode.")
        base = Path(root) / "synthetic"
        if base.exists():
            refuse("exists", "Use a fresh disposable root.")
        def op(name, **body):
            return course_ops.run(str(root), name, dict(course_id="synthetic", **body))
        op("create", title="Fictional evidence selection")
        objective = op("add_objective", statement="Identify fictional rule evidence")["objective_id"]
        source = op("register_source", filename="fiction.md", content=PASSAGE + "\n",
                    grants={"read": "granted", "transform": "granted"})
        op("add_source", source_object_id=source["source_object_id"], title="Fictional rule")
        op("bind_treatment", objective=objective, source=source["source_object_id"],
           treatment="direct-reading", locator="line 1")
        read = course.read_course(str(base))
        binding = graph.enroll_binding(read["doc"], 0, source["fingerprint"])
        declaration = make_declaration(binding, source["source_object_id"], source["fingerprint"])
        course.write_course(str(base), read["doc"], read["fingerprint"], "human", "synthetic")
        obj = cls(base)
        fixture = (HERE / "fixtures" / "bank.md").read_text()
        fixture = fixture.replace("synthetic:fixed-evidence-recheck", objective)
        fixture = fixture.replace("synthetic:fixed-evidence", objective)
        obj.bank.write_text(fixture)
        qs = model.load(str(obj.bank))
        if model.lint(qs)[0]:
            refuse("bank", "Synthetic bank must lint with the shipped parser.")
        for q in qs:
            validate(base, declaration, q)
        state = {"object_id": identity.new_object_id(), "declaration": declaration,
                 "declaration_revision": revision(declaration),
                 "bank_fingerprint": digest(obj.bank.read_text()), "draft": None}
        journal.commit_operation(str(base), state["object_id"], "component", obj.sidecar.name,
                                 "mint", obj.encode(state), None, "human", "synthetic",
                                 create_if_missing=True)
        session.do_start(str(obj.bank), {"count": 2, "seed": 3}, mode, str(obj.sitting), False)
        return obj

    @staticmethod
    def encode(state):
        return (json.dumps(state, sort_keys=True, indent=2) + "\n").encode()

    def state(self):
        state = json.loads(self.sidecar.read_text())
        if digest(self.bank.read_text()) != state["bank_fingerprint"]:
            refuse("bank-stale", "Retain the draft and reopen the original bank revision.")
        if revision(state["declaration"]) != state["declaration_revision"]:
            refuse("declaration-stale", "Retain the draft and restore its declaration.")
        return state

    def fingerprint(self):
        return identity.object_fingerprint(self.sidecar.read_bytes(), "component")

    def view(self):
        state = self.state()
        qs = model.load(str(self.bank))
        passage = validate(self.base, state["declaration"], qs[0])
        out = session.do_next(str(self.sitting))
        out.update(passage=passage, anchors=copy.deepcopy(state["declaration"]["anchors"]),
                   declaration_revision=state["declaration_revision"],
                   draft=state["draft"], draft_fingerprint=self.fingerprint())
        return out

    def save_draft(self, item_id, answer, expected):
        state = self.state()
        current = self.view().get("item")
        if not current or current["id"] != item_id:
            refuse("item-stale", "Reload the exact current item without discarding input.")
        state["draft"] = {"item_id": item_id, "declaration_revision": state["declaration_revision"],
                          "anchor_ids": answer}
        if expected == self.fingerprint() and self.encode(state) == self.sidecar.read_bytes():
            return None
        return journal.commit_operation(str(self.base), state["object_id"], "component",
                                        self.sidecar.name, "edit_in_place", self.encode(state),
                                        expected, "human", "synthetic")

    def submit(self, item_id, anchor_ids, expected, expected_responses):
        state = self.state()
        if type(expected_responses) is not int or self.view()["responses"] != expected_responses:
            refuse("sitting-stale", "This form already committed or the sitting changed. Reload.")
        anchors = {a["id"]: a["option"] for a in state["declaration"]["anchors"]}
        self.save_draft(item_id, anchor_ids, expected)
        if (not isinstance(anchor_ids, list) or not anchor_ids or
                any(not isinstance(x, str) or x not in anchors for x in anchor_ids) or
                len(set(anchor_ids)) != len(anchor_ids)):
            refuse("selection", "Select distinct declared anchor IDs.")
        # No key comparison here. Option letters are only a response projection.
        return session.do_submit(str(self.sitting), [anchors[x] for x in anchor_ids], None)

    def render(self):
        view = self.view()
        esc = lambda value: html.escape(str(value), quote=True)
        out = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fixed evidence anchors</title><style>body{max-width:72ch;margin:1rem auto;padding:1rem;font:1rem system-ui;color:#111;background:#fff}label,button,summary{display:block;min-height:44px;padding:.4rem;overflow-wrap:anywhere}input:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid #0645ad;outline-offset:3px}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media(forced-colors:active){input,button{forced-color-adjust:auto}}</style><h1>Fictional evidence selection</h1><p>Predefined whole spans. Choose evidence for the rule.</p><h2>Source passage</h2><p>' + esc(view["passage"]) + '</p>'
        item = view.get("item")
        if item:
            draft = view.get("draft") or {}
            selected = draft.get("anchor_ids", []) if draft.get("item_id") == item["id"] else []
            if not isinstance(selected, list):
                selected = []
            out += '<form method="post"><fieldset><legend>' + esc(item["stem"]) + '</legend>'
            for name, value in (("item_id", item["id"]), ("expected", view["draft_fingerprint"]),
                                ("expected_responses", view["responses"])):
                out += '<input type="hidden" name="' + name + '" value="' + esc(value) + '">'
            for a in view["anchors"]:
                checked = ' checked' if a["id"] in selected else ''
                out += '<label for="' + esc(a["id"]) + '"><input type="checkbox" name="anchor" id="' + esc(a["id"]) + '" value="' + esc(a["id"]) + '"' + checked + '>' + esc(a["label"]) + ' (' + esc(a["start"]) + ':' + esc(a["end"]) + '): ' + esc(a["quote"]) + '</label>'
            out += '</fieldset><button type="submit" name="action" value="save">Save draft</button><button type="submit" name="action" value="submit">Submit selection</button></form>'
        out += '<details><summary>Prototype public-state diagnostics</summary><pre>' + esc(json.dumps(view, indent=2)) + '</pre></details></html>'
        return out


def main():
    import argparse
    import tempfile
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs
    parser = argparse.ArgumentParser(description="Fictional fixed evidence anchor prototype")
    parser.add_argument("--mode", choices=("practice", "exam", "diagnostic"), default="exam")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--inspect-root", type=Path,
                        help="Read a disposable prototype course root in a fresh process")
    args = parser.parse_args()
    if args.inspect_root is not None:
        print(json.dumps(Journey(args.inspect_root).view(), sort_keys=True))
        return
    with tempfile.TemporaryDirectory(prefix="fixed-evidence-demo-") as root:
        obj = Journey.create(root, args.mode)
        class Handler(BaseHTTPRequestHandler):
            def page(self, message="", status=200):
                try:
                    page = obj.render()
                except (Refusal, course.CourseError, journal.JournalError) as error:
                    status = 409
                    page = '<!doctype html><html lang="en"><h1>Source unavailable or stale</h1><p role="alert">' + html.escape(str(error)) + '</p><p>Your original draft and sitting remain on disk. Restore the pinned source revision and reload.</p></html>'
                if message:
                    page = page.replace('<h1>', '<p role="status">' + html.escape(message) + '</p><h1>', 1)
                raw = page.encode()
                self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(raw))); self.end_headers(); self.wfile.write(raw)
            def do_GET(self):
                self.page()
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 8192:
                    self.page("Request too large; original draft preserved.", 413); return
                fields = parse_qs(self.rfile.read(length).decode("utf-8"))
                try:
                    ident = fields.get("item_id", [""])[0]
                    expected = fields.get("expected", [""])[0]
                    ids = fields.get("anchor", [])
                    if fields.get("action") == ["save"]:
                        obj.save_draft(ident, ids, expected)
                        message = "Draft saved without an assessment attempt."
                    elif fields.get("action") == ["submit"]:
                        result = obj.submit(ident, ids, expected,
                                            int(fields.get("expected_responses", ["-1"])[0]))
                        # Runtime result is the only feedback source.
                        message = result.get("selection_feedback", {}).get("display")
                        if not message:
                            message = ("Response committed. Feedback is held by the runtime."
                                       if "score" not in result else
                                       "Runtime result: " + ("correct." if result["score"] else "incorrect."))
                    else:
                        refuse("action", "Choose Save draft or Submit selection.")
                    self.page(message)
                except (Refusal, course.CourseError, journal.JournalError, ValueError) as error:
                    self.page(str(error), 409)
        server = HTTPServer(("127.0.0.1", args.port), Handler)
        print("Fictional temporary workspace:", obj.base, flush=True)
        print("Open http://127.0.0.1:%d (actual %s mode)" % (server.server_port, args.mode), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
