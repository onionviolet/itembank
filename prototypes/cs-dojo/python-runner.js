/* Disposable Python execution adapter. Its messages are observations only. */
'use strict';
import {loadPyodide} from './vendor/pyodide/pyodide.mjs';

const runtime = loadPyodide({indexURL: new URL('./vendor/pyodide/', import.meta.url).href});
const HARNESS = String.raw`
import contextlib, json

payload = json.loads(dojo_payload)
events = []

class OutputLimit(Exception):
    pass

class BoundedOutput:
    def __init__(self):
        self.parts = []
        self.size = 0

    def write(self, text):
        self.size += len(text)
        if self.size > 16000:
            raise OutputLimit()
        self.parts.append(text)
        return len(text)

    def flush(self):
        pass

    def getvalue(self):
        return "".join(self.parts)

def show(value):
    if value is None:
        return "None"
    return str(value)[:2000]

def report(label, actual, expected):
    if len(events) >= 80:
        raise OutputLimit()
    events.append({"type": "observation", "label": show(label), "actual": show(actual), "expected": show(expected)})

output = BoundedOutput()
scope = {"report": report, "__name__": "__main__"}
try:
    with contextlib.redirect_stdout(output):
        exec(compile(payload["files"][payload["entry"]], payload["entry"], "exec"), scope)
    for line in output.getvalue().splitlines():
        events.append({"type": "log", "text": line[:2000]})
    events.append({"type": "done"})
except OutputLimit:
    events = [{"type": "limit"}]
except Exception as error:
    for line in output.getvalue().splitlines():
        events.append({"type": "log", "text": line[:2000]})
    events.append({"type": "error", "text": f"{type(error).__name__}: {error}"[:2000]})
json.dumps(events if len(events) <= 85 else [{"type": "limit"}])
`;

runtime.then(() => self.postMessage({type: 'ready'})).catch(() => self.postMessage({type: 'unavailable'}));

self.onmessage = async ({data}) => {
  self.onmessage = null;
  try {
    const pyodide = await runtime;
    pyodide.globals.set('dojo_payload', JSON.stringify(data));
    const raw = await pyodide.runPythonAsync(HARNESS);
    pyodide.globals.delete('dojo_payload');
    for (const message of JSON.parse(String(raw))) self.postMessage(message);
  } catch (error) {
    self.postMessage({type: 'error', text: `${error?.name || 'Error'}: ${error?.message || 'Python execution failed'}`.slice(0, 2000)});
  }
};
