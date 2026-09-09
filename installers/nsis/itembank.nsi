; itembank NSIS installer (plan 13-03, 13-UI-SPEC section 6)
;
; Per-user by default (RequestExecutionLevel user, no UAC). A machine-wide
; variant is produced by compiling with -DMACHINE_WIDE (admin level, Program
; Files) -- an explicit choice, never silent elevation (D-07, T-13-12).
;
; The uninstaller removes ONLY the application directory. It never touches
; the user-profile evidence store or banks (Directive 4.3, T-13-09): the
; fixture in tests/packaging_roundtrip.py proves that scope by simulation.

Unicode True
!include "MUI2.nsh"

!define APP_NAME "itembank"
!define APP_VERSION "0.4.0"
!define APP_ID "itembank"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_ID}"

!ifdef MACHINE_WIDE
  RequestExecutionLevel admin
  !define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
  !define UNINSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!else
  RequestExecutionLevel user
  !define INSTALL_DIR "$LOCALAPPDATA\Programs\${APP_NAME}"
  !define UNINSTALL_DIR "$LOCALAPPDATA\Programs\${APP_NAME}"
!endif

; The install-notice values are passed by scripts/build_shell.ps1 with REAL
; values (D-11): the signed branch carries the certificate subject and sha256
; fingerprint; the unsigned branch carries the published installer SHA-256.
; Building without them must fail loudly, never ship a placeholder.
!ifndef INSTALL_NOTICE_HEADING
  !error "INSTALL_NOTICE_HEADING must be set by the build (signed or unsigned branch)"
!endif
!ifndef INSTALL_NOTICE_BODY
  !error "INSTALL_NOTICE_BODY must be set by the build (real values only)"
!endif

Name "${APP_NAME}"
OutFile "${APP_NAME}-${APP_VERSION}-setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKCU "${UNINST_KEY}" "InstallLocation"

; The learner's banks and evidence live in the user profile (the daemon's
; per-directory store). The installer never reads, moves, or deletes them.
; This comment is load-bearing: the uninstall section below scopes every
; deletion to $INSTDIR, and the packaging fixture asserts no line in this
; script targets the profile data paths.

!insertmacro MUI_PAGE_WELCOME
Page custom InstallNoticePage
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function InstallNoticePage
  !insertmacro MUI_HEADER_TEXT "Before you install" "Itembank's Python runtime and antivirus"
  nsDialogs::Create 1018
  Pop $0
  ${If} $0 == error
    Abort
  ${EndIf}
  ${NSD_CreateLabel} 0 0 100% 12u "${INSTALL_NOTICE_HEADING}"
  Pop $0
  ${NSD_CreateLabel} 0 16u 100% -16u "${INSTALL_NOTICE_BODY}"
  Pop $0
  nsDialogs::Show
FunctionEnd

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "..\..\dist\itembank-sidecar-onedir\*.*"
  ; The shell binary (produced by the Tauri bundle; absent here degrades the
  ; installer to the runtime-only layout the CLI already uses).
  ${If} ${FileExists} "..\..\src-tauri\target\release\itembank-shell.exe"
    File "..\..\src-tauri\target\release\itembank-shell.exe"
  ${EndIf}
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
SectionEnd

Section "Uninstall"
  ; T-13-09: every deletion below is scoped to $INSTDIR. No profile path is
  ; ever named; the evidence store and banks survive uninstall.
  RMDir /r "$INSTDIR\*"
  RMDir "$INSTDIR"
  DeleteRegKey HKCU "${UNINST_KEY}"
SectionEnd
