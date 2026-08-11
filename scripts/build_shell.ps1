<#
    The packaged-app build (plan 13-03): the PyInstaller onedir sidecar over
    the existing .pyz runtime build, the triple-suffixed sidecar binary the
    Tauri externalBin consumes, the measured installed size, and the Tauri
    bundle + NSIS installer when the toolchain is present.

    Run from the repo root:  powershell -File scripts/build_shell.ps1
#>
param(
    [string]$Out = "dist",
    [switch]$SkipBundle
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$TargetTriple = "x86_64-pc-windows-msvc"

Write-Host "== itembank shell build =="

# 1. The runtime release artifact (the .pyz) -- build.py is the one build of
#    the runtime; PyInstaller wraps it, never re-builds it (13-CONTEXT).
python build.py --out $Out

# 2. PyInstaller onedir freeze of the CLI entry (the sidecar is a CLI mode) --
#    never onefile (D-09). --noconsole keeps the sidecar window-less; the
#    shell reads its stdout through the pipe.
$Onedir = Join-Path $Out "itembank-sidecar-onedir"
if (Test-Path $Onedir) { Remove-Item -Recurse -Force $Onedir }
python -m PyInstaller `
    --onedir --noconsole --noupx --clean `
    --name itembank-sidecar `
    --distpath $Onedir `
    --workpath (Join-Path $Out ".pyinstaller-work") `
    --specpath (Join-Path $Out ".pyinstaller-spec") `
    --add-data ($Root + "\schemas;schemas") `
    --add-data ($Root + "\styles;styles") `
    --add-data ($Root + "\fonts;fonts") `
    itembank.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller freeze failed" }

# 3. The triple-suffixed binary Tauri's bundle.externalBin consumes, replacing
#    the dev placeholder stub in src-tauri/binaries/. PyInstaller's onedir
#    layout nests the app directory, so the exe is located by search, not
#    assumed.
$FrozenExe = Get-ChildItem $Onedir -Recurse -Filter "itembank-sidecar.exe" |
    Select-Object -First 1 -ExpandProperty FullName
if (-not $FrozenExe) { throw ("frozen sidecar exe not found under " + $Onedir) }
$BundledExe = Join-Path $Root ("src-tauri\binaries\itembank-sidecar-" + $TargetTriple + ".exe")
Copy-Item $FrozenExe $BundledExe -Force
Write-Host ("sidecar binary -> " + $BundledExe)

# 4. Measured installed size of the onedir (D-09): every byte a fresh copy
#    of the sidecar directory costs, reported honestly against the 25-45 MB
#    target.
$Bytes = (Get-ChildItem $Onedir -Recurse -File | Measure-Object -Property Length -Sum).Sum
$MiB = [math]::Round($Bytes / 1MB, 1)
Write-Host ("sidecar onedir size: " + $MiB + " MiB (target 25-45 MiB)")

# 5. The Tauri bundle + NSIS installer. Requires makensis (NSIS 3.x) and the
#    Tauri CLI; both absent -> degrade honestly, never fake the installer.
if ($SkipBundle) {
    Write-Host "bundle skipped (-SkipBundle)"
    exit 0
}
$Makensis = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $Makensis) {
    Write-Host "NSIS bundle skipped: makensis not installed (recorded gap; install NSIS 3.x to produce the installer)"
    exit 0
}
if (Get-Command npx -ErrorAction SilentlyContinue) {
    npx --yes @tauri-apps/cli@2 build --config src-tauri/tauri.conf.json
} else {
    Write-Host "Tauri CLI unavailable (npx missing) - bundle skipped"
}

# 6. The updater assets (D-08, 13-RESEARCH section 2): the minisign
#    signature over the installer bytes, then latest.json beside
#    SHA256SUMS.txt from the same tag. The signing key is a build secret
#    (ITEMBANK_MINISIGN_KEY); without it or the installer, the step degrades
#    honestly -- the CLI updater's SHA256SUMS.txt channel is unchanged.
$Installer = Get-ChildItem $Out -Filter "itembank-*-setup.exe" -ErrorAction SilentlyContinue
$Minisign = Get-Command minisign -ErrorAction SilentlyContinue
if ($Installer -and $Minisign -and $env:ITEMBANK_MINISIGN_KEY) {
    minisign -S -s $env:ITEMBANK_MINISIGN_KEY -m $Installer.FullName
    if ($LASTEXITCODE -ne 0) { throw "minisign signing failed" }
    python build.py --out $Out
    Write-Host "latest.json + minisign signature published for " $Installer.Name
} elseif (-not $Installer) {
    Write-Host "latest.json + signature skipped: no installer produced (makensis absent)"
} else {
    Write-Host "latest.json + signature skipped: minisign or ITEMBANK_MINISIGN_KEY absent (build secret required)"
}
