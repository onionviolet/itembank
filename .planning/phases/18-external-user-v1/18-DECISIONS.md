# Phase 18 decisions

Durable decision records for Phase 18 (external-user v1). Each entry is
dated and cites the context decision it transcribes. Entries are appended,
never rewritten.

## IL-20260815-11 resolved (18-CONTEXT D-01), 2026-08-17

The packaging conflict IL-20260815-11 is resolved, not re-decided. The
delivery vehicle is the Phase 13 desktop shell (the shipped Tauri-sidecar
packaging in `phases/13-desktop-packaging-tauri-sidecar/`) wrapping the
browser-served UI that 17A-CONTEXT D-08 fixed as the single canonical
shell. Nothing chooses between shells: the packaged app and the browser
reach the same served pages from the one runtime (IL-20260816-02). The
historical "no build step" reading and the miscited DEL-02 ground against
PyInstaller (constraint audit F9, F15) are both dead: a build step is
permitted on merit per the 2026-08-09 amendment, and no new
PyInstaller-class freezer is adopted because the Phase 13 shell already
exists and shipped. Any new packaging tool this phase touches goes through
`SUPPLY-CHAIN-POLICY.md` section 3; none was needed here.

Cite: (18-CONTEXT D-01), IL-20260815-11, IL-20260816-02.

## Code signing cost decision (V2-DEL-01, 18-CONTEXT D-02), 2026-09-01

The V2-DEL-01 trigger ("when a second person runs the tool") fired
2026-08-14. Per READINESS-AUDIT-14A.md A10 criterion 1, signing gets a
dated cost decision, not silence; the criterion is satisfied by the
record, not by signing itself.

Real costs gathered 2026-09-01:

- Windows Authenticode OV certificate. Quote gathered 2026-09-01 from
  SSL Dragon (reseller, ssldragon.com/ssl-certificates/code-signing/):
  Sectigo OV 219 USD per year, Comodo OV 219 USD per year, DigiCert OV
  400 USD per year. This lands inside the 100 to 400 USD per year range
  18-CONTEXT D-02 estimated. Since June 2023, CA/Browser Forum rules
  require the private key on FIPS 140-2 Level 2 hardware, which can add
  a token cost on top of the certificate price.
- Apple Developer Program, 99 USD per year, applicable only if a macOS
  artifact ships. No macOS artifact exists and no Windows-signing or
  macOS-notarization toolchain is exercised in this environment, so per
  18-CONTEXT this option is recorded as a deferral with reason, not an
  untested claim.
- Ship unsigned for v1, with the SmartScreen and Gatekeeper workarounds
  documented exactly where the user hits them.

Decision recorded: the 18-CONTEXT D-02 recommended default stands, ship
unsigned for v1 with documented workarounds, revisit on wider
distribution. The compensating control is the workaround documentation:
the README release-download step carries the SmartScreen workaround and
the Get-FileHash verification instruction (this plan's Task 4), and the
Install section's macOS Gatekeeper workaround stays as shipped. The NSIS
installer's unsigned-branch install notice shipped in 13-03 and is
fixture-pinned.

Checkpoint status: this entry transcribes the recorded D-02 default and
does not re-litigate it. The live checkpoint answer itself is DEFERRED
and owed to Weibao (dated 2026-09-01, per the standing directive of the
same date deferring human reviews). If Weibao instead chooses to buy a
certificate (option 1 or 2), the purchase is Weibao's own action in a
later session and this file gains a superseding dated entry; nothing
here executes a purchase.

Cite: (18-CONTEXT D-02), V2-DEL-01, READINESS-AUDIT-14A.md A10
criterion 1.
