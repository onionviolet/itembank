"""Generated MCP tool projection over the daemon's existing JSON handlers.

The daemon route table and its three-column parity inventory own membership
and names. This module only projects those rows, validates calls, and adapts
the already-existing handlers to JSON-RPC transports.
"""
import io
import json
import sys

import resources
import schema_validate


PROTOCOL_VERSION = "2026-07-28"
SERVER_INFO = {"name": "itembank", "version": "0.3.0"}


def _document(relpath):
    return json.loads(resources.read_text(relpath))


def _schema_for(path, output=False):
    """Return a resource-backed contract for one route.

    Course operations have individual request nodes in the published course
    operation document. Other routes retain their published result document
    as metadata while using its object shape as the transport envelope. The
    handler remains the stricter authority for those older request contracts.
    """
    if path.startswith("/api/course/"):
        document = _document("schemas/course_operation.schema.json")
        operation = path.rsplit("/", 1)[-1].replace("-", "_")
        if operation == "bind":
            operation = "bind"
        node = document["$defs"][operation]
        if output:
            return {"type": "object", "description": node.get("description", "")}
        # Preserve local refs while exposing exactly the operation signature.
        projected = dict(node)
        projected["$defs"] = document["$defs"]
        return projected
    operation = path[len("/api/"):].replace("/", "_").replace("-", "_")
    request_document = _document("schemas/api_request.schema.json")
    request_node = request_document["$defs"][operation]
    output_files = {
        "/api/start": "schemas/session.schema.json",
        "/api/next": "schemas/item.schema.json",
        "/api/submit": "schemas/response.schema.json",
        "/api/report": "schemas/report.schema.json",
        "/api/interact": "schemas/visual_interaction.schema.json",
        "/api/lesson/run": "schemas/lesson_run.schema.json",
        "/api/source/import": "schemas/normalized_document.schema.json",
        "/api/source/recheck": "schemas/normalized_document.schema.json",
        "/api/shelf": "schemas/course_graph.schema.json",
    }
    document = _document(output_files.get(path, "schemas/response.schema.json"))
    if output:
        return {
            "type": "object",
            "description": document.get("description", ""),
            "x-itembank-resource-id": document.get("$id", ""),
            "x-itembank-version": document.get("x-itembank-version"),
        }
    projected = dict(request_node)
    projected["$defs"] = request_document["$defs"]
    return projected


def tool_table():
    from surfaces import daemon
    parity = {route: (cli, name)
              for route, cli, name in daemon.SURFACE_PARITY}
    routes = {(method, path): handler
              for method, path, handler in daemon.API_ROUTES}
    if set(routes) != set(parity):
        missing_tools = sorted(set(routes) - set(parity))
        missing_routes = sorted(set(parity) - set(routes))
        raise ValueError("MCP parity mismatch: routes=%r tools=%r" %
                         (missing_tools, missing_routes))
    tools = []
    for method, path, _handler in daemon.API_ROUTES:
        _cli, name = parity[(method, path)]
        tools.append({
            "name": name,
            "description": "%s %s through the existing itembank handler."
                           % (method, path),
            "inputSchema": _schema_for(path),
            "outputSchema": _schema_for(path, output=True),
        })
    names = [tool["name"] for tool in tools]
    if len(names) != len(set(names)):
        raise ValueError("MCP tool names must be unique")
    return tools


class HandlerAdapter:
    """Small byte adapter that lets every transport call daemon handlers."""
    actor_kind = "agent"
    lan = False
    sidecar_token = None

    def __init__(self, source, arguments):
        self.root = source.root
        self.banks = source.banks
        self.plans = source.plans
        self.sessions = source.sessions
        self.day_states = getattr(source, "day_states", {})
        self.day_extra = getattr(source, "day_extra", {})
        self.collisions = getattr(source, "collisions", [])
        self.headers = {}
        self.client_address = ("127.0.0.1", 0)
        self._body = arguments
        self.status = 200
        self.payload = None

    def read_json(self):
        return self._body

    def send_json(self, payload, status=200):
        self.status = status
        self.payload = payload

    def send_bytes(self, body, _content_type, status=200, **_kwargs):
        self.status = status
        try:
            self.payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self.payload = {"message": body.decode("utf-8", "replace")}

    def send_error(self, code, message=None, explain=None):
        self.status = code
        self.payload = {"error": message or explain or "request refused"}

    def send_not_found(self, name):
        self.send_error(404, "not found: %s" % name)

    def send_server_error(self, exc):
        print("itembank MCP handler error: %s" % exc, file=sys.stderr)
        self.send_error(500, "internal error")


def dispatch_tool(source, name, arguments):
    from surfaces import daemon
    matches = [(method, path, handler)
               for method, path, handler in daemon.API_ROUTES
               if next((row[2] for row in daemon.SURFACE_PARITY
                        if row[0] == (method, path)), None) == name]
    if len(matches) != 1:
        return _tool_result({"error": "unknown tool: %s" % name}, True)
    method, path, handler_name = matches[0]
    schema = _schema_for(path)
    errors = schema_validate.validate(arguments, schema)
    if errors:
        return _tool_result({"error": "invalid arguments: %s" % "; ".join(errors)}, True)
    adapter = HandlerAdapter(source, arguments)
    getattr(daemon, handler_name)(adapter)
    failed = adapter.status >= 400 or (
        isinstance(adapter.payload, dict) and
        adapter.payload.get("status") in ("refused", "locked", "invalid"))
    return _tool_result(adapter.payload, failed)


def _tool_result(payload, is_error=False):
    if payload is None:
        payload = {}
    result = {
        "content": [{"type": "text", "text": json.dumps(payload, sort_keys=True)}],
        "structuredContent": payload,
    }
    if is_error:
        result["isError"] = True
    return result


def frame(source, message):
    """Frame one JSON-RPC request for stdio, HTTP, or another byte transport."""
    if not isinstance(message, dict):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "invalid request"}}
    method = message.get("method")
    msg_id = message.get("id")
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method in ("initialize", "server/discover"):
        result = {"protocolVersion": PROTOCOL_VERSION,
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": SERVER_INFO}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": tool_table()}
    elif method == "tools/call":
        params = message.get("params") or {}
        result = dispatch_tool(source, params.get("name"),
                               params.get("arguments") or {})
    else:
        return {"jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601,
                          "message": "method not found: %s" % method}}
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


class StdioSource:
    def __init__(self, root):
        from surfaces import daemon
        self.root = root
        self.banks, self.plans, self.collisions = daemon.scan_dir(root)
        self.sessions = {}
        self.day_states = {}
        self.day_extra = {}


def serve_stdio(root=".", instream=None, outstream=None):
    source = StdioSource(root)
    instream = instream or sys.stdin
    outstream = outstream or sys.stdout
    for line in instream:
        try:
            message = json.loads(line)
            response = frame(source, message)
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            outstream.write(json.dumps(response, separators=(",", ":")) + "\n")
            outstream.flush()
    return 0


def cmd_mcp(args):
    return serve_stdio(getattr(args, "base", "."))
