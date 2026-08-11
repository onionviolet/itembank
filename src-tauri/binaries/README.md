# Sidecar binaries

`itembank-sidecar-x86_64-pc-windows-msvc.exe` in this directory is a
**placeholder stub** (prints an error and exits) that exists so `tauri-build`
can validate `bundle.externalBin` during dev builds before the real sidecar
exists.

Plan 13-03 builds the real PyInstaller **onedir** sidecar (the daemon entry,
loopback-only, stdout handshake) and its `scripts/build_shell.ps1` replaces
this stub before `tauri build`. Never ship the stub.
