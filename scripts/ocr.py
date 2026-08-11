#!/usr/bin/env python3
"""OCR command: extract text from images using a local Ollama vision model.

This is the vision bridge that lets text-only models (DeepSeek) read images:
the image never reaches the model — only the text extracted here does.

Usage:
  python scripts/ocr.py image.png [more.png ...]
  python scripts/ocr.py --model qwen2.5vl:7b --endpoint http://localhost:11434 scan.jpg
  python scripts/ocr.py --models          # list what Ollama has available

Environment:
  OLLAMA_HOST   Ollama endpoint (default: auto-probe localhost, then WSL gateway)
  OCR_MODEL     default vision model (default: qwen2.5vl:7b)
"""

import argparse
import json
import sys

from ocr_lib import DEFAULT_MODEL, find_endpoint, list_models, ocr_image


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="ocr",
        description="Extract text from images via a local Ollama vision model.",
    )
    ap.add_argument("images", nargs="*", help="image files to OCR (png/jpg/jpeg/webp/bmp)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"vision model (default: {DEFAULT_MODEL})")
    ap.add_argument("--endpoint", default=None, help="Ollama base URL (default: auto-probe)")
    ap.add_argument("--json", action="store_true", help="emit JSON {path: text}")
    ap.add_argument("--models", action="store_true", help="list available models and exit")
    args = ap.parse_args(argv)

    try:
        if args.models:
            ep = args.endpoint or find_endpoint()
            print(json.dumps({"endpoint": ep, "models": list_models(ep)}, indent=2))
            return 0
        if not args.images:
            ap.error("at least one image path is required (or --models)")
        ep = args.endpoint or find_endpoint()
        results = {}
        for path in args.images:
            results[path] = ocr_image(path, model=args.model, endpoint=ep)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for path, text in results.items():
                if len(results) > 1:
                    print(f"### {path}")
                print(text)
        return 0
    except Exception as err:  # noqa: BLE001 — CLI boundary
        print(f"ocr: error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
