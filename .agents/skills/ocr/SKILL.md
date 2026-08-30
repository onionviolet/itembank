---
name: ocr
description: OCR images (screenshots, scans, photos) into text via a local Ollama vision model — the vision bridge for text-only models like DeepSeek.
---

# OCR — read text out of images

DeepSeek (and any other text-only model) **cannot see images**. When the user
provides an image — a file path, a screenshot, a scan, a pasted picture — do
not pretend to read it. Run the local OCR bridge and use the text it returns.

## When to use

- The user gives you an image path (`*.png`, `*.jpg`, `*.jpeg`, `*.webp`, `*.bmp`).
- The user pastes an image (save it to a file first, e.g. `tmp/pasted.png`, then OCR it).
- A task needs text from a screenshot, scan, or photo (e.g. a textbook page to
  turn into an itembank question bank).

## Binding a page as a cited source

Reading an image for your own use is what the rest of this skill covers, and
it is unchanged.

Turning a photographed or scanned page into a durable, citable course source
is a different operation, and it now exists:

```bash
python itembank.py source import --base <course-root> --file <image> --adapter ocr
```

or `POST /api/source/import` with `adapter` set to `ocr`. That path runs this
same bridge, writes derived Markdown plus a locator sidecar, records one
operation journal entry, and produces a source an objective can cite. Do not
build a second way to do it.

The sidecar honestly records `bbox` and `confidence` as null, because this
bridge transcribes text and does not measure where on the page it sat. A
citation into an OCR source names the page, not a region. If you need
region-level citation, that is a change to this skill's output contract and a
locator schema version bump, not something to work around by guessing
coordinates.

The envelope confidence for an OCR source is `low` by design. Treat an OCR
transcription as the least reliable source in the course, and prefer a
text-bearing original whenever one exists.

## How to run it

```bash
python scripts/ocr.py <image-path> [more-images...]
```

The command prints the transcribed text to stdout, preserving reading order and
language. Useful variants:

```bash
python scripts/ocr.py --models                 # list models Ollama has
python scripts/ocr.py --model qwen2.5vl:7b img.png   # pick a specific model
python scripts/ocr.py --json img.png           # machine-readable output
```

If the `ocr` MCP plugin is registered (see `reasonix.toml` `[[plugins]]`), the
`ocr_image` tool is the equivalent first-class tool call — same result.

## Rules

1. **Never claim you saw the image.** You only ever see the text OCR returns.
   Say "the OCR reads: …" when relaying it, or just use it as source material.
2. **Don't invent content.** If the OCR output is garbled or has gaps, say so
   instead of guessing the missing text.
3. **Keep the original language.** OCR preserves it; do not translate the source
   text when the goal is transcription/authoring (itembank keeps original wording).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `model 'qwen2.5vl:7b' not found` | `ollama pull qwen2.5vl:7b` (on the host running Ollama) |
| `no Ollama server reachable` | Start Ollama, or set `OLLAMA_HOST` (e.g. `http://localhost:11434`); the script auto-probes localhost then the WSL gateway |
| OCR quality poor on handwriting/figures | Try a stronger vision model (`ollama pull qwen2.5vl:11b` / `llama3.2-vision`) via `--model` |

## Environment

- `OLLAMA_HOST` — endpoint override (default: auto-probe `localhost:11434`, then WSL2 gateway).
- `OCR_MODEL` — default vision model (default: `qwen2.5vl:7b`).
