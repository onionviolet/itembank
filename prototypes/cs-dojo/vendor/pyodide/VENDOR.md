# Pyodide runtime for the disposable CS Dojo prototype

Version: `314.0.6`, as declared by the installed `pyodide` npm package used
for this local prototype. The five runtime assets were copied from that
package's matching locally served distribution. They are Pyodide's files, not
Code Learner application code or question content. Pyodide is licensed under
MPL-2.0. `LICENSE` is the upstream license text from the Pyodide repository.
The runtime runs only on the dedicated loopback prototype origin. It is not
part of the installed Itembank application.

SHA-256 checksums:

```text
3fdaef09e9e365c85e002737720f8d0ab8f278c1c244a2dde6a37663cf488ad4  pyodide-lock.json
2ac5eba365ec12839c75c03b39b3be1dd63b798852cc460b014b52238be042f7  pyodide.asm.mjs
3a0a00dfeaa348ac20f9ef09904233d32d33f644339662d4af368f8a2010f37a  pyodide.asm.wasm
69e3f6ccec3e14b465df60be577ca62f536251406b9a00cce019eac5252a2495  pyodide.mjs
80c5be6babfe03297069703410c3c29404dcf2525d2b128746bae5536f94831f  python_stdlib.zip
```

Upstream: https://github.com/pyodide/pyodide
License: https://github.com/pyodide/pyodide/blob/main/LICENSE
