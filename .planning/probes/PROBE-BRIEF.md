# Subagent payload delivery probe

This is a complete, self-contained task. Do not wait for more instructions.

## Task

Create a file at exactly this path (relative to the project root
`C:/Users/wayba/Downloads/CTF/itembank`):

`.planning/probes/probe-20260810T2145Z.txt`

Its content must be exactly, with no trailing whitespace:

```
payload-ok
```

Use a plain file write (e.g. `Set-Content -NoNewline` in PowerShell or
`open(...).write(...)`). Do not create any other file.

## Done when

The file exists and its content is exactly `payload-ok`. Reply with a
one-line confirmation containing the word `PROBE_DONE`.
