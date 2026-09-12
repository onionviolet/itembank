# CS Dojo prototype

Status: first executable prototype built and browser-verified, 2026-09-12. Owner: this task for
implementation and Weibao for experience review. User request: "work on cs dojo".
This advances D3.1 and IL-20260906-09 without accepting a course format.

## Bounded packet

Build one original synthetic JavaScript unit around array boundaries and
functions. Include prediction before execution, debugging with declared examples,
and a two-file module/test lab. Use the accepted study-desk identity with an
editor-centered workspace. All examples and explanations are public teaching
material. No formal sitting or restricted assessment content is loaded.

Read scope: the Dojo vision entries, D3.1, source-to-course contract, workflow,
current state, and neighboring prototype styles. Product write scope: this
directory only. Machine-local launch findings were appended to `.reasonix/REASONIX.md`.
All created paths have an absent expected base. Patch additions are the
operation record. Source material and code are original synthetic fixtures.
No learner source or evidence leaves the machine. Public browser documentation
was consulted without uploading project content. No third-party code is copied.

The browser runs JavaScript in a replaceable dedicated worker on a separate
loopback prototype origin. A small read-only server serves an exact file list.
The worker response denies connections, imported scripts, and nested workers
using CSP. A main-thread deadline and output limits bound ordinary runaway
programs. This is a prototype execution boundary, not a production hostile-code
sandbox or a hard memory quota. Do not host it on the production app's origin.

Observed outputs and learner-written examples are untrusted program reports.
They do not settle correctness, assign scores, unlock assessment feedback, or
create evidence. Notes and code live in page memory until explicit download.
Reload discards the page draft. Downloads are learner-owned, unreviewed artifacts.
No persistence format, runtime adapter, or accepted revision is added.

## Ready decisions and gate

JavaScript is the first executable language because the browser supplies its
runtime without a new package. Python remains a required follow-up candidate,
not a fake language selector. The two-file example uses an explicitly declared
CommonJS-style `require` and `module.exports` harness. It does not claim Node.js,
a filesystem, packages, or native ES-module support.

Verify the whole unit in Chromium, including keyboard editing and navigation,
draft retention between activities and files, error feedback, stop, timeout,
fresh execution after timeout, output limits, blocked fetch/import/nested
workers, server path refusal, export, and 390px layout. Run quick preflight.
Human touch, screen-reader, zoom, aesthetic and real-course review remain open.

Undo: remove this newly created directory. Downloaded drafts remain separate.
Concurrent source/reading/runtime changes are outside this packet. No commit or
push is authorized. The shared STATE and ledger stay with their active writers.

## Browser references

- [Worker execution and CSP](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)
- [Worker termination](https://developer.mozilla.org/en-US/docs/Web/API/Worker/terminate)
- [CSP worker-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/worker-src)

## Open and verify

From the repository root:

```sh
python3 prototypes/cs-dojo/server.py
```

Open `http://127.0.0.1:8774`. Use `--port 0` for an available dedicated port.
The server prints its address. Do not serve this directory using a generic
static server, because `runner.js` needs the separate worker CSP header.
Opening `index.html` directly retains the reading and export interface but
correctly reports execution as unavailable. `source.md` needs no JavaScript.

Run the focused browser gate with:

```sh
node prototypes/cs-dojo/verify.mjs
```

It uses an existing Playwright installation. Set `ITEMBANK_PLAYWRIGHT_MODULE`
to its module entry and `ITEMBANK_CHROMIUM` to an installed Chromium executable
when they are outside the normal resolution paths. No browser dependency is
added to the root project. `ITEMBANK_DOJO_EVIDENCE` selects the screenshot
directory. The verifier starts and stops its own dedicated loopback server.

## Verified result, 2026-09-12

All 14 focused browser groups passed on the final candidate. They cover the
full prediction, repair, two-file and learner-authored-example flow, source
dialog focus return, Tab escape, independent drafts, confirmed reset,
all-activity Markdown download, syntax errors, stop, two-second timeout,
replacement workers, output flooding, oversized input, blocked network and
script imports, blocked nested-worker loading, literal output escaping,
server path/Host/write refusals, reload behavior, and static-file degradation.
No unexpected remote request or page exception was observed.

Screenshots of desktop prediction and debugging and the 390px lab were
inspected. All three activities fit the narrow viewport without page overflow.
Reduced-motion and forced-color smoke checks passed. These automated checks
and screenshots do not certify touch, screen-reader, zoom or human preference.

Quick preflight passed every executed gate, including fixture lint, build,
bank guard, mirrors, schemas and path checks. Full Python, repository-wide
JavaScript and clean-tree gates were skipped by quick mode. No production
modules were modified or audited in this slice. Reads of large project
contracts were scoped to the relevant vision, workflow and Dojo sections.

The first verification launch found a Playwright/browser cache-version mismatch.
Using the already installed Chromium executable resolved it without a download.
Two test assumptions were corrected: nested-worker CSP rejection is reported
asynchronously through an error event, and a raw HTTP request is required to
test a forged Host header because the installed fetch implementation replaced
it. The final probes verify the actual refusal behavior.

## Remaining promotion gate

JavaScript execution is one adapter candidate. Python, formal runtime scoring
and disclosure, durable objective evidence, restore, and production execution
isolation remain unimplemented. Browser workers lack a hard per-run memory
quota here, and worker-origin storage is not a learner-data authority. The
next bounded candidate is a Python execution adapter over this same synthetic
unit, with an explicit runtime distribution and isolation review before any
real coursework is connected. No real course policy or source permission is
inferred from this prototype.
