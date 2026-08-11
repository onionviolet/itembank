#!/usr/bin/env python3
"""MCP stdio server exposing an OCR tool backed by a local Ollama vision model.

Lets any model (including text-only DeepSeek) read images: the tool returns the
transcribed text, the image never reaches the model.

Register in a Reasonix config as a stdio plugin, e.g. in a local
`reasonix.toml` (see `reasonix.toml.example` in the repo root; the file is
gitignored so the wiring stays personal):

    [[plugins]]
    name = "ocr"
    type = "stdio"
    command = "python"
    args = ["<checkout>/scripts/ocr_mcp.py"]   # point at YOUR checkout
    # env = { OLLAMA_HOST = "http://localhost:11434" }   # optional

Tools:
  ocr_image(path, model?) -> transcribed text
"""

import json
import sys

from ocr_lib import find_endpoint, ocr_image

TOOLS = [
    {
        "name": "ocr_image",
        "description": (
            "Extract all text from an image file using a local Ollama vision "
            "model, and return it as plain text. Use whenever the user provides "
            "an image (screenshot, scan, photo, pasted picture) and the text "
            "inside it is needed. This is the vision bridge: the caller model "
            "never sees the image, only the extracted text."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the image file (png/jpg/jpeg/webp/bmp).",
                },
                "model": {
                    "type": "string",
                    "description": "Ollama vision model to use (default: OCR_MODEL env or qwen2.5vl:7b).",
                },
            },
            "required": ["path"],
        },
    }
]

PROTOCOL_VERSION = "2024-11-05"


def send(msg):
    sys.stdout.buffer.write(json.dumps(msg).encode("utf-8") + b"\n")
    sys.stdout.buffer.flush()


def read_msg():
    line = sys.stdin.buffer.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def handle_tools_call(params):
    args = params.get("arguments", {}) or {}
    path = args.get("path")
    if not path:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "ocr error: missing required argument 'path'"}],
        }
    try:
        text = ocr_image(path, model=args.get("model"))
        return {"content": [{"type": "text", "text": text}]}
    except Exception as err:  # noqa: BLE001 — MCP boundary; errors go to the caller
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"ocr error: {err}"}],
        }


def main():
    while True:
        msg = read_msg()
        if msg is None:
            return 0
        msg_id = msg.get("id")
        method = msg.get("method")

        if method == "initialize":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "ocr", "version": "1.0.0"},
                    },
                }
            )
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": handle_tools_call(msg.get("params", {}) or {}),
                }
            )
        else:
            send(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"method not found: {method}"},
                }
            )


if __name__ == "__main__":
    sys.exit(main())
