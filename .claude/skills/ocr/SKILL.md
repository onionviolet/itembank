---
name: ocr
description: "OCR images (screenshots, scans, photos) into text via a local Ollama vision model : the vision bridge for text-only models like DeepSeek."
---

# OCR : read text out of images

Use the OCR bridge when the active model cannot inspect the image or a durable text extraction is needed. If image input is available, inspect it directly for layout and diagram relationships. OCR complements visual inspection; it does not prove those relationships.

Check the course policy and source rights before opening or transcribing an image. Use an attached local file or an authorized saved image; do not invent a path for pasted content. For transcription, preserve the original language and distinguish uncertain glyphs from verified text.

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

Inspect the returned locator sidecar rather than inventing region precision. The current bridge records `bbox` and `confidence` as null, because this
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
`ocr_image` tool is the equivalent first-class tool call : same result.

## Rules

1. **Name the evidence used.** If only OCR was inspected, say "the OCR reads" and do not claim visual inspection. Direct visual inspection supports only what was actually visible.
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

- `OLLAMA_HOST` : endpoint override (default: auto-probe `localhost:11434`, then WSL2 gateway).
- `OCR_MODEL` : default vision model (default: `qwen2.5vl:7b`).
