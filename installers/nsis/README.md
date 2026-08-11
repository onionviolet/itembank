# NSIS installer

`itembank.nsi` is the NSIS 3.x installer script (plan 13-03):

- per-user default install (no UAC) with a machine-wide variant compiled
  with `-DMACHINE_WIDE` (D-07, T-13-12);
- an install-notice page whose copy is the 13-UI-SPEC 6.1 signed or unsigned
  branch verbatim, driven by `INSTALL_NOTICE_HEADING`/`INSTALL_NOTICE_BODY`
  defines supplied by `scripts/build_shell.ps1` with **real** values -- the
  script fails to compile without them, so a placeholder can never ship
  (D-11, T-13-10);
- an uninstaller scoped to `$INSTDIR` only -- it never names the
  user-profile evidence store or banks (Directive 4.3, T-13-09), and
  `tests/packaging_roundtrip.py` proves that scope by simulation.

`makensis` (NSIS 3.x) is required to compile it. It is absent on the current
build machine; the gap is recorded in 13-03-SUMMARY.md and the fixtures
simulate the installer's path logic until the toolchain is present.

The unsigned branch's warning (13-UI-SPEC 6.1, verbatim): "Windows
SmartScreen will warn you when you run itembank, and some antivirus products
flag applications that bundle a Python runtime. Both are expected for an
unsigned build." The signed branch names the real certificate subject and
SHA-256 fingerprint; neither branch ever ships a placeholder value.
