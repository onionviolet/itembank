# Probe A: inline message, fork_turns="none" (20260810165252)

You are a generic probe subagent. This file mirrors the task text that was
also sent in your spawn message. Your complete task:

1. Create the file exactly at:
   `C:\Users\wayba\Downloads\CTF\itembank\.planning\probes\probe-a-inline-forknone-20260810165252.txt`
2. Its content must be exactly `payload-ok` with NO trailing newline,
   carriage return, or spaces (9 bytes).
3. Write it byte-exact, e.g. in PowerShell:
   `[System.IO.File]::WriteAllText('C:\Users\wayba\Downloads\CTF\itembank\.planning\probes\probe-a-inline-forknone-20260810165252.txt', 'payload-ok')`
4. Verify the file exists and its raw byte length is 9, then reply with a
   one-line confirmation: `PROBE_DONE a`

Do not create any other files.
