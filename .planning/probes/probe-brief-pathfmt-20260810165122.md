# Probe brief C (fork_turns="none", relative/forward-slash message)

This is a complete, self-contained task. Do not wait for more instructions.

## Task

Create a file at exactly this path (relative to the project root
`C:/Users/wayba/Downloads/CTF/itembank`):

`.planning/probes/probe-pathfmt-20260810165122.txt`

Its content must be exactly, with no trailing whitespace:

```
payload-ok
```

Use a plain file write (e.g. `[System.IO.File]::WriteAllText(path, 'payload-ok')`
in PowerShell). Do not create any other file.

## Done when

The file exists and its content is exactly `payload-ok`. Reply with a one-line
confirmation containing the word `PROBE_DONE`.
