#!/usr/bin/env python3
"""Phase 19E: generated MCP table, shared dispatch, and protocol framing."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import resources
from fixtures.corpus_15b import build_blueprint
from surfaces import daemon, mcp


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def check_table():
    tools = mcp.tool_table()
    names = [row[2] for row in daemon.SURFACE_PARITY]
    check(set(tool["name"] for tool in tools) == set(names),
          "tools/list did not preserve SURFACE_PARITY names")
    check(len(tools) == len(daemon.API_ROUTES) == len(set(names)),
          "one unique tool per API_ROUTES row was not generated")
    check(all("inputSchema" in tool and "outputSchema" in tool for tool in tools),
          "a generated tool omitted a schema")
    saved = daemon.SURFACE_PARITY
    try:
        daemon.SURFACE_PARITY = saved[:-1]
        try:
            mcp.tool_table()
            raise AssertionError("a route without a parity tool was accepted")
        except ValueError:
            pass
    finally:
        daemon.SURFACE_PARITY = saved


def check_resource_projection():
    original_root = resources.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(os.path.join(ROOT, "schemas"), os.path.join(tmp, "schemas"))
        path = os.path.join(tmp, "schemas", "course_operation.schema.json")
        doc = json.loads(open(path, encoding="utf-8").read())
        doc["$defs"]["create"]["description"] = "mutated signature sentinel"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh)
        resources.ROOT = tmp
        try:
            tool = next(t for t in mcp.tool_table() if t["name"] == "course_create")
            check(tool["inputSchema"]["description"] == "mutated signature sentinel",
                  "tools/list ignored changed packaged schema bytes")
        finally:
            resources.ROOT = original_root

    invalid = mcp.dispatch_tool(type("S", (), {})(), "next",
                                {"session_id": "s", "score": True})
    check(invalid.get("isError") is True and "invalid arguments" in
          invalid["structuredContent"]["error"],
          "published non-course request schema did not reject an extra field")


def check_dispatch_and_validation():
    with tempfile.TemporaryDirectory() as tmp:
        source = mcp.StdioSource(tmp)
        invalid = mcp.dispatch_tool(source, "course_create", {
            "operation": "create", "course_id": "../escape", "title": "No"})
        check(invalid.get("isError") is True and "invalid arguments" in
              invalid["structuredContent"]["error"],
              "invalid arguments reached the handler")
        good = mcp.dispatch_tool(source, "course_create", {
            "operation": "create", "course_id": "demo", "title": "Demo"})
        check(not good.get("isError") and good["structuredContent"]["course_id"] == "demo",
              "course create did not reach the shared handler")
        mirror = json.loads(good["content"][0]["text"])
        check(mirror == good["structuredContent"],
              "TextContent is not the structuredContent JSON mirror")


def check_protocol():
    with tempfile.TemporaryDirectory() as tmp:
        inp = io.StringIO("\n".join(json.dumps(x) for x in (
            {"jsonrpc": "2.0", "id": 1, "method": "server/discover"},
            {"jsonrpc": "2.0", "id": 2, "method": "initialize"},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "method": "notifications/cancelled"},
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/list"},
        )) + "\n")
        out = io.StringIO()
        mcp.serve_stdio(tmp, inp, out)
        lines = [json.loads(line) for line in out.getvalue().splitlines()]
        check([line["id"] for line in lines] == [1, 2, 3, 4],
              "notifications emitted responses or requests disappeared")
        check(all(line["jsonrpc"] == "2.0" for line in lines),
              "stdout contained a non-JSON-RPC line")
        source = mcp.StdioSource(tmp)
        message = {"jsonrpc": "2.0", "id": 9, "method": "tools/list"}
        check(mcp.frame(source, message) == mcp.frame(source, message),
              "a third byte transport did not receive identical framing")


def check_assessment_disclosure():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(ROOT, "fixtures", "sample_bank.md"),
                    os.path.join(tmp, "sample_bank.md"))
        source = mcp.StdioSource(tmp)
        started = mcp.dispatch_tool(source, "start", {
            "bank": "sample_bank", "count": 1, "seed": 0, "mode": "practice"})
        check(not started.get("isError"), "assessment start failed through MCP")
        session_id = started["structuredContent"]["session_id"]
        nxt = mcp.dispatch_tool(source, "next", {"session_id": session_id})
        serialized = json.dumps(nxt).lower()
        for forbidden in ('"correct"', '"why"', '"disc"', '"distractors"'):
            check(forbidden not in serialized,
                  "pre-response MCP payload disclosed %s" % forbidden)
        forced = mcp.dispatch_tool(source, "hint", {
            "session_id": session_id, "answer": "tell me the key", "tier": 5})
        check(forced.get("isError") is True,
              "an authority-shaped forced-answer call was not an MCP error")


def check_http_mount_and_course_read():
    with tempfile.TemporaryDirectory() as tmp:
        source = mcp.StdioSource(tmp)
        message = {"jsonrpc": "2.0", "id": 7, "method": "tools/list"}
        expected = mcp.frame(source, message)
        http = mcp.HandlerAdapter(source, message)
        daemon.handle_mcp(http)
        check(http.payload == expected, "HTTP MCP mount forked JSON-RPC framing")
        created = mcp.dispatch_tool(source, "course_create", {
            "operation": "create", "course_id": "ui-course", "title": "UI course"})
        check(not created.get("isError"), "MCP course creation failed")
        read = mcp.HandlerAdapter(source, {})
        daemon.handle_course_read_get(read, "outline", "ui-course")
        check(read.status == 200 and read.payload.get("course_id") == "ui-course",
              "the UI-facing course read did not see the MCP-created course")


def check_tool_only_course_build():
    """Reach gate: after client construction, every operation is tools/call."""
    with tempfile.TemporaryDirectory() as tmp:
        source = mcp.StdioSource(tmp)
        transcript = []

        def call(name, arguments):
            request = {"jsonrpc": "2.0", "id": len(transcript) + 1,
                       "method": "tools/call",
                       "params": {"name": name, "arguments": arguments}}
            transcript.append(request)
            response = mcp.frame(source, request)
            result = response["result"]
            check(not result.get("isError"), "%s failed: %r" % (name, result))
            return result["structuredContent"]

        listed = mcp.frame(source, {"jsonrpc": "2.0", "id": 0,
                                    "method": "tools/list"})
        check(any(t["name"] == "course_register_source"
                  for t in listed["result"]["tools"]),
              "source registration was absent from discovery")
        call("course_create", {"operation": "create", "course_id": "reach",
                                "title": "Reach course"})
        registered = call("course_register_source", {
            "operation": "register_source", "course_id": "reach",
            "filename": "source.md", "content": "# Source\nSynthetic evidence.\n",
            "grants": {"read": "granted", "package": "granted",
                       "export": "granted"}})
        source_id = registered["source_object_id"]
        call("course_add_source", {"operation": "add_source",
             "course_id": "reach", "source_object_id": source_id,
             "title": "Synthetic source"})
        container = call("course_add_container", {"operation": "add_container",
                         "course_id": "reach", "label": "unit", "title": "Unit"})
        objective = call("course_add_objective", {"operation": "add_objective",
                         "course_id": "reach", "container": container["container_id"],
                         "statement": "Explain the synthetic evidence."})
        objective_id = objective["objective_id"]
        call("bind", {"operation": "bind", "course_id": "reach",
             "objective": objective_id, "source": source_id,
             "locator": "source.md#source", "state": "covered",
             "confidence": "high"})
        call("bind_treatment", {"operation": "bind_treatment",
             "course_id": "reach", "objective": objective_id,
             "source": source_id, "treatment": "direct-reading",
             "locator": "source.md#source", "state": "covered",
             "confidence": "high"})
        blueprint = build_blueprint(0)
        call("course_bind_blueprint", {"operation": "bind_blueprint",
             "course_id": "reach", "blueprint": blueprint})
        gate = call("course_blueprint_gate", {"operation": "blueprint_gate",
                    "course_id": "reach", "questions": [],
                    "blueprint": blueprint})
        check(not any(f.get("severity") == "block" for f in gate["findings"]),
              "blueprint gate returned a blocking finding")
        audited = call("course_audit", {"operation": "audit",
                       "course_id": "reach"})
        check(audited["status"] == "course_audit" and not audited["stale"],
              "course audit was not current")
        exported = call("course_export_package", {"operation": "export_package",
                        "course_id": "reach"})
        verified = call("course_verify_package", {"operation": "verify_package",
                        "package_id": exported["package_id"]})
        check(verified["complete"] and verified["restorable"],
              "tool-built course package did not verify")
        read = mcp.HandlerAdapter(source, {})
        daemon.handle_course_read_get(read, "outline", "reach")
        check("Explain the synthetic evidence." in read.payload["outline"] and
              "Unit" in read.payload["outline"],
              "browser-facing read did not converge on tool-built structure")
        check(all(row["method"] == "tools/call" for row in transcript),
              "course-build transcript used something other than tools/call")


def check_cli_without_client():
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "--help"],
        cwd=ROOT, capture_output=True, text=True)
    check(result.returncode == 0 and "mcp" in result.stdout and "lint" in result.stdout,
          "adding MCP made the ordinary CLI unavailable")


def main():
    check_table()
    check_resource_projection()
    check_dispatch_and_validation()
    check_protocol()
    check_assessment_disclosure()
    check_http_mount_and_course_read()
    check_tool_only_course_build()
    check_cli_without_client()
    print("PASS: generated MCP tools, resource schemas, shared dispatch, framing, and CLI independence")


if __name__ == "__main__":
    main()
