# Generator-only OpenMAIC trial

This trial calls `generateSceneContent` with one fixed synthetic teaching outline from `@openmaic/generation` 0.3.6. The package's `AICallFn` is supplied by this caller. It produces one generated teaching-scene `candidate` or an `invalid_model_output` result. The earlier outline function remains a fixture-tested optional planning seam. Every output is a `DRAFT`, never an accepted Itembank lesson, source binding, bank, session, score, or evidence event.

Run the deterministic fixture contract:

```sh
npm test
```

Optional local demo:

```sh
npm run demo -- --local
```

`--local` makes one request to loopback Ollama at `http://127.0.0.1:11434` using `qwen3.5:4b`, a 30-second timeout, and a 700-token cap. It sends only the fixed synthetic water-state teaching scene. It writes its draft JSON to stdout and has no retry. A timeout or malformed model response prints an `invalid_model_output` draft result. That is an observed safe failure, not evidence of a live generation success.

No OpenMAIC classroom roles, agent roster, discussion, TTS, quiz scoring, renderer, or persistent storage is called. `generateSceneContent` accepts no agent metadata when called for this fixed slide. If a later OpenMAIC API requires metadata, use an optional empty roster and neutral static metadata only, never running subagents.

The npm package is MIT licensed. This trial copies no OpenMAIC source. See the pinned upstream [generation package manifest](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/packages/%40openmaic/generation/package.json) and [license](https://github.com/THU-MAIC/OpenMAIC/blob/29735f10d0081859ac3db1a50a0cc92f46436004/LICENSE).
