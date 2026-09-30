"""Isolated read-only cited tutor preview over runtime-released context.

No model transport, grade, new evidence type, or production route is added.
The caller supplies a disposable synthetic course and its admitted bank stem.
"""
import os
import urllib.parse

import course
import runtime
from surfaces import course_workbench, presentation, session


def context(base, session_file, stem):
    data = runtime.read_session(session_file)
    bank = os.path.realpath(data["bank"])
    root = os.path.realpath(base)
    if os.path.commonpath([root, bank]) != root or os.path.splitext(os.path.basename(bank))[0] != stem:
        raise ValueError("tutor.bank_not_admitted")
    # This existing adapter is read-only. It returns the runtime's released
    # tiers, including unavailable mode states, without unlocking a tier.
    teaching, private_item, sitting = session._teach_read(session_file)
    public_item = runtime.public_item(private_item, sitting.get("seed", 0))
    doc = course.read_course(base)["doc"]
    cid = doc["header"]["course_object_id"]
    resume = '/quiz/' + urllib.parse.quote(stem, safe='') + '?' + urllib.parse.urlencode(
        {"mode": data["mode"], "session": data["session_id"], "course": cid})
    citations = []
    if teaching["available"]:
        sources = {source["source_object_id"]: source for source in doc["sources"]}
        for binding in doc["bindings"]:
            if binding.get("objective") != private_item.get("objective") or binding.get("binding_kind") != "source":
                continue
            sid = binding["source_object_id"]
            text, notice = course_workbench._source_text(base, sid, {bank})
            citations.append({"origin": "Source", "source_id": sid, "locator": binding.get("locator"),
                              "title": sources.get(sid, {}).get("title") or sid,
                              "text": text, "unavailable": notice})
    return {"item": public_item, "teaching": teaching, "citations": citations,
            "session_id": data["session_id"], "course_id": cid, "resume_href": resume,
            "egress": "none", "authority": "runtime", "prototype": True}


def render(payload):
    esc = presentation.esc
    parts = ['<section><h3>Cited tutor prototype</h3><p>Assessment state and released feedback stay owned by the runtime.</p>',
             '<p>%s</p>' % esc(payload["item"]["stem"])]
    teaching = payload["teaching"]
    if not teaching["available"]:
        parts.append('<p role="status">%s</p>' % esc(teaching["unavailable_reason"]))
    else:
        for tier in teaching["shown"]:
            parts.append('<p>Released feedback: %s</p>' % esc(tier["display"]))
        for citation in payload["citations"]:
            parts.append('<h4>Source: %s</h4><p>Locator: %s</p><pre>%s</pre>' % (
                esc(citation["title"]), esc(citation["locator"]),
                esc(citation["text"] or citation["unavailable"])))
        parts.append('<label>What in this cited source would help you revise your explanation? '
                     '<textarea aria-label="Private reflection, not submitted or scored"></textarea></label>'
                     '<p>This scratch reflection is not saved or scored.</p>')
    parts.append('<p><a href="%s">Return to this exact sitting</a></p></section>' % esc(payload["resume_href"]))
    return ''.join(parts)
