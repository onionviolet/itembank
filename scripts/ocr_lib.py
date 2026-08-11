"""OCR via a local Ollama vision model — the vision bridge for text-only LLMs.

DeepSeek (and other text-only models) cannot see images. This module runs a
local vision model through Ollama over an image and returns the extracted text,
so the text-only model only ever consumes text. Python stdlib only.

Endpoints are probed in order:
  1. $OLLAMA_HOST (if set)
  2. http://localhost:11434
  3. the WSL2 default-gateway (NAT case: Ollama runs on the Windows host and
     localhost inside WSL does not reach it)

Model default: $OCR_MODEL or qwen2.5vl:7b (good Chinese + English OCR).
"""

import base64
import json
import os
import urllib.error
import urllib.request

DEFAULT_MODEL = os.environ.get("OCR_MODEL", "qwen2.5vl:7b")

TRANSCRIBE_PROMPT = (
    "You are an OCR engine. Transcribe ALL visible text in the image exactly as "
    "written, preserving reading order (top to bottom, left to right). Keep the "
    "original language; do not translate. Preserve line breaks where they are "
    "meaningful. Do not add, summarize, or comment — output only the transcribed "
    "text. If the image contains no text, output exactly: [no text]"
)


def candidate_endpoints():
    env = os.environ.get("OLLAMA_HOST")
    if env:
        yield env.rstrip("/")
    yield "http://localhost:11434"
    # WSL2 NAT fallback: the Windows host usually runs Ollama; localhost inside
    # WSL does not reach it, but the default-gateway IP does.
    try:
        with open("/proc/net/route", encoding="utf-8") as fh:
            for line in fh.readlines()[1:]:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "00000000" and parts[2] != "00000000":
                    gw = parts[2]
                    ip = ".".join(str(int(gw[i : i + 2], 16)) for i in (6, 4, 2, 0))
                    yield f"http://{ip}:11434"
                    break
    except OSError:
        pass


def find_endpoint():
    """Return the first reachable Ollama endpoint."""
    tried = []
    for ep in candidate_endpoints():
        tried.append(ep)
        try:
            req = urllib.request.Request(ep + "/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return ep
        except Exception:
            continue
    raise RuntimeError(
        "no Ollama server reachable (tried: %s). Start Ollama, or set OLLAMA_HOST."
        % ", ".join(tried)
    )


def list_models(endpoint=None):
    ep = endpoint or find_endpoint()
    with urllib.request.urlopen(ep + "/api/tags", timeout=10) as resp:
        data = json.load(resp)
    return [m.get("name") for m in data.get("models", [])]


def ocr_image(path, model=None, endpoint=None):
    """Transcribe all text in the image file at `path`. Returns the text."""
    model = model or DEFAULT_MODEL
    endpoint = endpoint or find_endpoint()
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "user", "content": TRANSCRIBE_PROMPT, "images": [b64]}
        ],
    }
    req = urllib.request.Request(
        endpoint + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        if err.code == 404 and "model" in body.lower():
            raise RuntimeError(
                f"model '{model}' not found on {endpoint}; pull it first: "
                f"ollama pull {model}"
            ) from err
        raise RuntimeError(f"ollama error {err.code}: {body[:500]}") from err
    return (data.get("message") or {}).get("content", "").strip()
