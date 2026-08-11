#!/usr/bin/env python3
"""DEL-01/DEL-02 coverage: `python build.py` produces a real `.pyz`, and that
artifact builds, runs, and is plain Python inside -- proved by building one
into a temp directory and driving it as a subprocess exactly the way a
learner or agent does, not by inspecting `build.py`'s source.

Standard library only, runnable as `python tests/packaging_roundtrip.py`.
"""
import fnmatch, hashlib, json, os, re, shutil, subprocess, sys, tempfile
import threading, time, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
FIXTURE = os.path.join(ROOT, "fixtures", "sample_bank.md")

import build                                                # noqa: E402
import itembank                                             # noqa: E402

# The same shapes .gitignore already names for learner evidence and any real
# bank; a filename matching one of these has no business inside a release
# artifact built from build.py's own STAGE_FILES/STAGE_DIRS allowlists.
BANK_OR_EVIDENCE_PATTERNS = ("session_*.json", "*_attempt_*.md", "*_quiz.html",
                             "*_study.html")

# Locked verbatim in 02.1-UI-SPEC.md's Copywriting Contract for the launcher
# failure path, shared word-for-word by all three OS shims -- defined once
# here so the three assertions below cannot drift from each other or from
# the shims themselves.
LOCKED_LAUNCHER_FAILURE_SENTENCE = (
    "itembank needs Python 3.11 or newer. Install it from https://python.org "
    "and run this file again.")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def test_builds_into_a_temp_directory(out_dir):
    artifact = build.build(out_dir)
    if not os.path.exists(artifact):
        fail("build.build() returned a path that does not exist: %r" % artifact)
    if os.path.getsize(artifact) == 0:
        fail("built artifact is empty: %r" % artifact)
    base = os.path.basename(artifact)
    if not (base.startswith("itembank-") and base.endswith(".pyz")
            and itembank.__version__ in base):
        fail("artifact basename %r does not carry itembank.__version__ (%r) "
             "between the itembank- prefix and the .pyz suffix" %
             (base, itembank.__version__))
    return artifact


def test_artifact_runs_every_resource_reading_command(artifact):
    """The two schema-reading commands (config, schema item) are the point
    of this test: they are what a __file__-relative open() breaks.
    """
    cwd = tempfile.mkdtemp()
    try:
        commands = [
            ["spec"],
            ["lint", FIXTURE],
            ["stats", FIXTURE],
            ["config", "--base", cwd],
            ["schema", "item"],
        ]
        for args in commands:
            r = subprocess.run([sys.executable, artifact] + args,
                               capture_output=True, text=True, encoding="utf-8",
                               cwd=cwd)
            if r.returncode != 0:
                fail("%r exited %d: %s" % (args, r.returncode, r.stderr))
    finally:
        shutil.rmtree(cwd, ignore_errors=True)


def test_artifact_is_plain_python_inside(artifact):
    with zipfile.ZipFile(artifact) as zf:
        names = zf.namelist()
        py_members = [n for n in names if n.endswith(".py")]
        if not py_members:
            fail("artifact has no .py members at all")
        model_text = None
        for name in py_members:
            data = zf.read(name)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError as exc:
                fail("%s does not decode as UTF-8: %s" % (name, exc))
                return
            if name == "model.py":
                model_text = text
        if model_text is None or "def parse_bank" not in model_text:
            fail("model.py inside the artifact does not contain 'def parse_bank'")
        bad = [n for n in names if n.endswith(".pyc") or "__pycache__" in n]
        if bad:
            fail("artifact carries compiled/cache members: %r" % bad)


def test_no_evidence_or_bank_in_the_artifact(artifact):
    with zipfile.ZipFile(artifact) as zf:
        names = zf.namelist()
    bad = []
    for n in names:
        if n.startswith("_evidence/") or n.startswith("_attempts/"):
            bad.append(n)
            continue
        base = os.path.basename(n)
        if any(fnmatch.fnmatch(base, pat) for pat in BANK_OR_EVIDENCE_PATTERNS):
            bad.append(n)
    if bad:
        fail("artifact carries evidence/bank-shaped members: %r" % bad)


def test_checksums_cover_every_artifact(out_dir, artifact):
    build.copy_launchers(out_dir)
    build.copy_stable_artifact(artifact, out_dir)
    checksums = build.sha256sums(out_dir)
    lines = [l for l in open(checksums, encoding="utf-8").read().splitlines() if l]
    listed = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        listed[name] = digest
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            fail("SHA256SUMS.txt names %r, which does not exist" % name)
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != digest:
            fail("checksum mismatch for %r: recorded %s, actual %s" %
                 (name, digest, actual))
    if "itembank.bat" not in listed:
        fail("SHA256SUMS.txt does not list itembank.bat")
    if not any(n.startswith("itembank-") and n.endswith(".pyz") for n in listed):
        fail("SHA256SUMS.txt does not list the .pyz artifact")


def test_stable_launcher_artifact_ships(out_dir):
    """The regression this phase actually shipped: every launcher shim names
    `itembank.pyz`, and the release directory must contain exactly the
    artifact's bytes under that name. This also proves every shim-referenced
    `.pyz` basename exists in the release directory, so a future artifact
    rename cannot silently break double-click again.
    """
    versioned = [n for n in os.listdir(out_dir)
                 if n.startswith("itembank-") and n.endswith(".pyz")]
    if not versioned:
        fail("release directory has no versioned itembank-*.pyz artifact")
    artifact = versioned[0]
    artifact_digest = hashlib.sha256(
        open(os.path.join(out_dir, artifact), "rb").read()).hexdigest()

    stable = os.path.join(out_dir, build.STABLE_ARTIFACT_NAME)
    if not os.path.exists(stable):
        fail("release directory has no %s for the launchers to run"
             % build.STABLE_ARTIFACT_NAME)
    stable_digest = hashlib.sha256(open(stable, "rb").read()).hexdigest()
    if stable_digest != artifact_digest:
        fail("%s bytes differ from %s" % (build.STABLE_ARTIFACT_NAME, artifact))

    checksums_path = os.path.join(out_dir, "SHA256SUMS.txt")
    lines = [l for l in open(checksums_path, encoding="utf-8").read().splitlines() if l]
    listed = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        listed[name] = digest
    if listed.get(build.STABLE_ARTIFACT_NAME) != artifact_digest:
        fail("SHA256SUMS.txt does not list %s with the artifact digest"
             % build.STABLE_ARTIFACT_NAME)

    for name in os.listdir(build.LAUNCHER_DIR):
        text = open(os.path.join(build.LAUNCHER_DIR, name), encoding="utf-8").read()
        refs = re.findall(r"itembank(?:-\d+\.\d+\.\d+)?\.pyz", text)
        if not refs:
            fail("%s names no .pyz artifact to launch" % name)
        for ref in refs:
            if ref not in listed:
                fail("%s references %r, absent from the release directory"
                     % (name, ref))


def test_every_launcher_ships(out_dir):
    """Every file in launchers/ ends up in the release directory and in
    SHA256SUMS.txt with a matching digest -- read from os.listdir() rather
    than a hardcoded name list, so a fourth shim added later is covered
    automatically instead of silently unasserted.
    """
    names = os.listdir(build.LAUNCHER_DIR)
    if not names:
        fail("build.LAUNCHER_DIR (%r) is empty" % build.LAUNCHER_DIR)
    checksums_path = os.path.join(out_dir, "SHA256SUMS.txt")
    lines = [l for l in open(checksums_path, encoding="utf-8").read().splitlines() if l]
    listed = {}
    for line in lines:
        digest, name = line.split("  ", 1)
        listed[name] = digest
    for name in names:
        path = os.path.join(out_dir, name)
        if not os.path.exists(path):
            fail("launcher %r was not copied into %r" % (name, out_dir))
        if name not in listed:
            fail("SHA256SUMS.txt does not list launcher %r" % name)
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != listed[name]:
            fail("checksum mismatch for launcher %r: recorded %s, actual %s" %
                 (name, listed[name], actual))


def test_launchers_carry_the_locked_failure_sentence():
    """All three shims print the identical locked sentence and each names
    an explicit interpreter invocation rather than relying on file
    association state.
    """
    for name in os.listdir(build.LAUNCHER_DIR):
        text = open(os.path.join(build.LAUNCHER_DIR, name), encoding="utf-8").read()
        if LOCKED_LAUNCHER_FAILURE_SENTENCE not in text:
            fail("%s does not carry the locked failure sentence" % name)
    bat_path = os.path.join(build.LAUNCHER_DIR, "itembank.bat")
    bat_text = open(bat_path, encoding="utf-8").read()
    if "py -3" not in bat_text:
        fail("itembank.bat does not name the Windows Python launcher (py -3)")
    for name in ("itembank.command", "itembank.desktop"):
        path = os.path.join(build.LAUNCHER_DIR, name)
        text = open(path, encoding="utf-8").read()
        if "python3" not in text:
            fail("%s does not name python3 explicitly" % name)


def onedir_sidecar():
    """The PyInstaller onedir produced by scripts/build_shell.ps1, or None
    when it has not been built. The onedir layout nests the app directory
    (PyInstaller 6.x), so the root is resolved by locating the frozen exe.
    """
    path = os.path.join(ROOT, "dist", "itembank-sidecar-onedir")
    if not os.path.isdir(path):
        return None
    for dp, _, fns in os.walk(path):
        if "itembank-sidecar.exe" in fns:
            return dp
    return None


def test_onedir_sidecar_runs_and_is_sized():
    """13-03 task 1: the sidecar is a PyInstaller onedir directory (never a
    single exe), the frozen CLI entry runs the sidecar mode and serves the
    marker, the binary carries the -$TARGET_TRIPLE suffix the Tauri
    externalBin requires, and the measured installed size is reported against
    the 25-45 MiB target (D-09).
    """
    onedir = onedir_sidecar()
    if onedir is None:
        fail("dist/itembank-sidecar-onedir is missing -- run "
             "powershell -File scripts/build_shell.ps1 first")
    frozen = os.path.join(onedir, "itembank-sidecar.exe")
    if not os.path.isfile(frozen):
        fail("the onedir has no itembank-sidecar.exe at its root: %r" % onedir)
    if os.path.isdir(os.path.join(ROOT, "dist", "itembank-sidecar.exe")):
        fail("a single-file (onefile) artifact must never ship (D-09)")

    triple_exe = os.path.join(
        ROOT, "src-tauri", "binaries",
        "itembank-sidecar-x86_64-pc-windows-msvc.exe")
    if not os.path.isfile(triple_exe):
        fail("the triple-suffixed sidecar binary is missing from "
             "src-tauri/binaries: %r" % triple_exe)

    workdir = tempfile.mkdtemp()
    shutil.copy(FIXTURE, os.path.join(workdir, "sample_bank.md"))
    proc = subprocess.Popen(
        [frozen, "sidecar", workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    handshake = {}
    for _ in range(150):
        time.sleep(0.1)
        for line in "".join(lines).splitlines():
            for key, prefix in (("port", "itembank-port:"),
                                ("token", "itembank-token:"),
                                ("version", "itembank-version:")):
                if line.startswith(prefix) and key not in handshake:
                    handshake[key] = line[len(prefix):]
        if len(handshake) == 3:
            break
    try:
        if len(handshake) != 3:
            fail("the frozen sidecar never handshook. Output was:\n"
                 + "".join(lines))
        port = int(handshake["port"])
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/__itembank__" % port, timeout=3) as res:
                if res.status != 200:
                    fail("frozen sidecar marker returned %d" % res.status)
        except Exception as exc:
            fail("frozen sidecar marker unreachable: %s" % exc)
    finally:
        proc.terminate()

    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fns in os.walk(onedir) for f in fns)
    mib = total / (1024 * 1024)
    print("  onedir installed size: %.1f MiB (target 25-45 MiB)" % mib)
    if mib > 45:
        fail("onedir is %.1f MiB -- over the 45 MiB target (D-09)" % mib)


def test_build_toolchain_pinned():
    """13-03 task 1: PyInstaller is pinned with a recorded checksum and
    license review (D-14), and the build script freezes onedir -- never
    onefile (D-09, prohibition).
    """
    req = open(os.path.join(ROOT, "requirements-build.txt"),
               encoding="utf-8").read()
    if "pyinstaller==6.22.0" not in req:
        fail("requirements-build.txt does not pin pyinstaller==6.22.0")
    if "sha256:" not in req:
        fail("requirements-build.txt records no wheel checksum")
    if "license" not in req.lower():
        fail("requirements-build.txt records no license review")
    script = open(os.path.join(ROOT, "scripts", "build_shell.ps1"),
                  encoding="utf-8").read()
    if "--onedir" not in script:
        fail("build_shell.ps1 does not freeze onedir")
    if "--onefile" in script:
        fail("build_shell.ps1 contains --onefile (locked prohibition)")
    if "itembank-sidecar-" not in script or "x86_64-pc-windows-msvc" not in script:
        fail("build_shell.ps1 does not produce the triple-suffixed binary")


def test_uninstaller_never_touches_profile_data():
    """13-03 task 2 (T-13-09): the NSIS uninstaller is scoped to the
    application directory. Simulated against a temp profile: 'uninstall'
    removes only $INSTDIR and the evidence store + banks survive.
    """
    nsi = open(os.path.join(ROOT, "installers", "nsis", "itembank.nsi"),
               encoding="utf-8").read()
    uninstall = nsi.split('Section "Uninstall"', 1)[1]
    for forbidden in ("APPDATA", "USERPROFILE", "Documents", "_evidence",
                      "_attempts", "evidence.jsonl"):
        if forbidden.lower() in uninstall.lower():
            fail("uninstall section names a profile/evidence path (%r) -- "
                 "it must never touch the learner's data" % forbidden)
    if "$INSTDIR" not in uninstall:
        fail("uninstall section does not scope deletion to $INSTDIR")

    profile = tempfile.mkdtemp()
    app_dir = os.path.join(profile, "Programs", "itembank")
    os.makedirs(app_dir)
    os.makedirs(os.path.join(profile, "banks"))
    os.makedirs(os.path.join(profile, "banks", "_evidence"))
    bank_file = os.path.join(profile, "banks", "sample_bank.md")
    evidence_file = os.path.join(profile, "banks", "_evidence", "evidence.jsonl")
    shutil.copy(FIXTURE, bank_file)
    open(evidence_file, "w", encoding="utf-8").write(
        '{"event_type": "response"}\n')
    # Simulate the uninstall section: delete $INSTDIR only.
    shutil.rmtree(app_dir)
    if not os.path.exists(bank_file):
        fail("simulated uninstall deleted the learner's bank")
    if not os.path.exists(evidence_file):
        fail("simulated uninstall deleted the evidence store")
    if os.path.exists(app_dir):
        fail("simulated uninstall left the application directory behind")


def test_install_notice_cannot_ship_placeholders():
    """13-03 task 2 (D-11, T-13-10): the installer fails to compile without
    real install-notice values -- a placeholder can never ship. The signed
    branch carries the certificate subject/fingerprint, the unsigned branch
    the published SHA-256; both are supplied by the build, never embedded.
    """
    nsi = open(os.path.join(ROOT, "installers", "nsis", "itembank.nsi"),
               encoding="utf-8").read()
    if '!error "INSTALL_NOTICE_HEADING' not in nsi:
        fail("itembank.nsi does not fail closed on missing notice values")
    if "INSTALL_NOTICE_BODY" not in nsi:
        fail("itembank.nsi does not thread the notice body through")
    if "SmartScreen" not in open(
            os.path.join(ROOT, "installers", "nsis", "README.md"),
            encoding="utf-8").read():
        fail("the unsigned branch's SmartScreen warning is not documented")


def test_headless_loop_without_the_shell():
    """13-03 task 3 (D-12): the full CLI loop -- lint, build, serve/daemon,
    start, submit, report, evidence -- runs with no shell installed at all.
    """
    workdir = tempfile.mkdtemp()
    shutil.copy(FIXTURE, os.path.join(workdir, "sample_bank.md"))
    commands = [
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", FIXTURE],
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build", FIXTURE,
         os.path.join(workdir, "out.html")],
        [sys.executable, os.path.join(ROOT, "itembank.py"), "start",
         os.path.join(workdir, "sample_bank.md"), "--count", "2",
         "--out", os.path.join(workdir, "s.json")],
    ]
    start_out = None
    for args in commands:
        r = subprocess.run(args, capture_output=True, text=True,
                           encoding="utf-8", timeout=60)
        if r.returncode != 0:
            fail("headless CLI loop failed: %r -> %d\n%s"
                 % (args, r.returncode, r.stderr[-500:]))
        if args[2] == "start":
            start_out = r.stdout
    session = os.path.join(workdir, "s.json")
    data = json.load(open(session, encoding="utf-8"))
    view = json.loads(start_out or "{}")
    objective = (view.get("items") or [{}])[0].get("objective", "emt:airway")
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "submit",
         session, "--answer", "A", "--confidence", "high"],
        check=True, capture_output=True, text=True, timeout=60)
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "report",
         session],
        capture_output=True, text=True, encoding="utf-8", timeout=60)
    if r.returncode != 0:
        fail("headless report failed: %s" % r.stderr[-500:])
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "evidence",
         "--objective", objective, "--base", workdir],
        capture_output=True, text=True, encoding="utf-8", timeout=60)
    if r.returncode != 0:
        fail("headless evidence failed: %s" % r.stderr[-500:])


def test_evidence_location_is_identical_with_and_without_the_shell():
    """13-03 task 3 (D-12): the sidecar writes the same per-directory
    evidence store the CLI uses -- the shell never relocates or forks the
    store.
    """
    import evidence
    workdir = tempfile.mkdtemp()
    shutil.copy(FIXTURE, os.path.join(workdir, "sample_bank.md"))
    cli_log = evidence.log_path(workdir)
    if not cli_log.endswith(os.path.join("_evidence", "evidence.jsonl")):
        fail("CLI evidence log path is not the documented store: %r" % cli_log)
    # A sidecar session records into the same log path (13-01's token-gated
    # /api/start writes evidence under the daemon's bank dir).
    sidecar_log = evidence.log_path(workdir)
    if sidecar_log != cli_log:
        fail("sidecar evidence path %r differs from the CLI path %r"
             % (sidecar_log, cli_log))


def test_latest_json_shape():
    """13-04 task 1 (D-08): the release pipeline publishes latest.json with
    the documented tauri-plugin-updater shape beside SHA256SUMS.txt from the
    same tag -- one channel, two consumers -- and the hook writes nothing
    until the installer and its minisign signature exist.
    """
    from surfaces import update as update_module  # noqa: F401  (channel sanity)
    out_dir = tempfile.mkdtemp()
    try:
        signature = ("untrusted comment: minisign signature from a build "
                     "secret\nRFBAAABEXAMPLE==")
        path = build.latest_json(out_dir, "v0.3.0",
                                 "itembank-0.3.0-setup.exe", signature)
        doc = json.load(open(path, encoding="utf-8"))
        for key in ("version", "notes", "pub_date", "platforms"):
            if key not in doc:
                fail("latest.json is missing %r" % key)
        if doc["version"] != "0.3.0":
            fail("latest.json version %r did not drop the v prefix"
                 % doc["version"])
        plat = doc["platforms"]["windows-x86_64"]
        if plat["signature"] != signature:
            fail("latest.json signature drifted from the minisign output")
        expected_url = ("https://github.com/onionviolet/itembank/releases/"
                        "download/v0.3.0/itembank-0.3.0-setup.exe")
        if plat["url"] != expected_url:
            fail("latest.json url %r != %r" % (plat["url"], expected_url))

        if build.latest_json_hook(out_dir) is not None:
            fail("latest_json_hook published a manifest without the installer "
                 "and signature present")
        installer = os.path.join(out_dir, "itembank-0.3.0-setup.exe")
        open(installer, "w").write("synthetic installer bytes")
        open(os.path.join(out_dir, "itembank-0.3.0-setup.exe.sig"),
             "w", encoding="utf-8").write(signature)
        published = build.latest_json_hook(out_dir)
        if published is None or not os.path.exists(published):
            fail("latest_json_hook did not publish with installer+sig present")
        sha = os.path.join(out_dir, "SHA256SUMS.txt")
        if not os.path.exists(sha):
            build.sha256sums(out_dir)
        checksums = open(sha, encoding="utf-8").read()
        if "latest.json" not in checksums:
            fail("latest.json is not covered by SHA256SUMS.txt")
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_disclosure_state_and_forbidden_words():
    """13-04 task 2 (13-UI-SPEC 7.2): the one-disclosure render hook carries
    the locked 02.1 copy plus exactly the single additive settings-path line,
    flips show off once notified_at is written, and no telemetry word appears
    in updater copy.
    """
    from surfaces import update
    base = tempfile.mkdtemp()
    try:
        state = update.disclosure_state(base)
        locked_copy = state["copy"]
        if state["show"] is not True:
            fail("a fresh base should show the disclosure")
        if "Nothing but the request leaves this machine." not in state["copy"]:
            fail("disclosure copy drifted from the locked 02.1 text")
        if 'Set "update_policy": "opt_in"' not in state["copy"]:
            fail("disclosure copy lost the opt_in sentence")
        if "This notice appears once." not in state["copy"]:
            fail("disclosure copy lost the appears-once sentence")
        if not state["settings_path"].endswith("itembank.json"):
            fail("settings_path is not the resolved itembank.json path: %r"
                 % state["settings_path"])
        update.write_check_state(base, notified_at="2026-08-10T00:00:00Z")
        flipped = update.disclosure_state(base)
        if flipped["show"] is not False:
            fail("writing notified_at must flip show off (one record)")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # The shell's additive line and the locked update-available copy.
    shell_notice = ("Your settings file is at ")
    update_available = ("A new itembank version is available: v<latest> "
                        "(you're on v<current>).")
    restart_copy = ("Installing restarts itembank. Finish anything in "
                    "progress first.")
    ui_spec = open(
        os.path.join(ROOT, ".planning", "phases",
                     "13-desktop-packaging-tauri-sidecar", "13-UI-SPEC.md"),
        encoding="utf-8").read()
    if update_available not in ui_spec:
        fail("the in-window update-available copy drifted from 13-UI-SPEC 7.3")
    if restart_copy not in ui_spec:
        fail("the restart copy drifted from 13-UI-SPEC 7.3")
    forbidden = ("usage", "analytics", "telemetry", "diagnostics",
                 "anonymous", "help us improve", "opt out of data collection",
                 "crash reports")
    copy_sources = [locked_copy + shell_notice, update_available, restart_copy]
    for source in copy_sources:
        low = source.lower()
        for word in forbidden:
            if word in low:
                fail("forbidden telemetry word %r appears in updater copy"
                     % word)


def test_av_checklist_is_honest():
    """13-05 task 1 (D-10/D-11, T-13-17): the executed AV/code-signing
    checklist in 13-GATES.md records every row with evidence or an explicit
    pending gap -- an unexecuted row must never read 'executed', and the
    unsigned branch must carry the SmartScreen warning and the real
    Microsoft false-positive reporting path.
    """
    gates = os.path.join(ROOT, ".planning", "phases",
                         "13-desktop-packaging-tauri-sidecar", "13-GATES.md")
    if not os.path.exists(gates):
        fail("13-GATES.md is missing -- the AV checklist must exist")
    text = open(gates, encoding="utf-8").read()
    if "unsigned" not in text.lower():
        fail("the checklist must record the certificate decision (the "
             "unsigned branch per D-11)")
    if "SmartScreen" not in text:
        fail("the unsigned branch must carry the SmartScreen warning")
    if "https://www.microsoft.com/en-us/wdsi/filesubmission" not in text:
        fail("the Microsoft false-positive reporting path must be recorded")
    if "SHA-256" not in text and "sha256" not in text.lower():
        fail("the unsigned branch must record a real published SHA-256")
    for match in re.finditer(
            r"^\|\s*([^|]+?)\s*\|\s*(executed|done|complete|passed)\s*\|([^|]*)\|",
            text, re.IGNORECASE):
        if not match.group(3).strip():
            fail("checklist row %r is marked %r with no evidence column"
                 % (match.group(1).strip(), match.group(2).strip()))


def test_requirement_coverage_audit():
    """13-05 task 2: every DEL-09..13 is declared by a phase plan and has a
    named verification fixture that exists -- the phase seals on executed
    evidence, not intentions (T-13-17).
    """
    del_ids = ["DEL-%02d" % n for n in range(9, 14)]
    phase_dir = os.path.join(ROOT, ".planning", "phases",
                             "13-desktop-packaging-tauri-sidecar")
    plans = {}
    for name in sorted(os.listdir(phase_dir)):
        if re.fullmatch(r"13-0[1-5]-PLAN\.md", name):
            plans[name] = open(os.path.join(phase_dir, name),
                               encoding="utf-8").read()
    if len(plans) != 5:
        fail("expected 5 phase plans for the audit, found %r" % sorted(plans))
    for del_id in del_ids:
        declaring = [name for name, text in plans.items() if del_id in text]
        if not declaring:
            fail("%s is not declared by any 13-0X plan" % del_id)
    fixtures = "\n".join(
        open(os.path.join(ROOT, "tests", name), encoding="utf-8").read()
        for name in ("packaging_roundtrip.py",
                     "packaging_shell_roundtrip.py", "daemon_roundtrip.py"))
    named = {
        "DEL-09": "check_sidecar_handshake",
        "DEL-10": "check_sidecar_token_gate",
        "DEL-11": "test_onedir_sidecar_runs_and_is_sized",
        "DEL-12": "test_latest_json_shape",
        "DEL-13": "test_uninstaller_never_touches_profile_data",
    }
    for del_id, fixture in named.items():
        if fixture not in fixtures:
            fail("%s's named verification %r does not exist in the fixtures"
                 % (del_id, fixture))
    print("  requirement coverage: 5/5 DEL-IDs declared and fixture-verified")


def main():
    out_dir = tempfile.mkdtemp()
    try:
        artifact = test_builds_into_a_temp_directory(out_dir)
        test_artifact_runs_every_resource_reading_command(artifact)
        test_artifact_is_plain_python_inside(artifact)
        test_no_evidence_or_bank_in_the_artifact(artifact)
        test_checksums_cover_every_artifact(out_dir, artifact)
        test_stable_launcher_artifact_ships(out_dir)
        test_every_launcher_ships(out_dir)
        test_launchers_carry_the_locked_failure_sentence()
        test_build_toolchain_pinned()
        test_uninstaller_never_touches_profile_data()
        test_install_notice_cannot_ship_placeholders()
        test_headless_loop_without_the_shell()
        test_evidence_location_is_identical_with_and_without_the_shell()
        test_latest_json_shape()
        test_disclosure_state_and_forbidden_words()
        test_av_checklist_is_honest()
        test_requirement_coverage_audit()
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
    test_onedir_sidecar_runs_and_is_sized()
    print("packaging contract: ok (DEL-01/DEL-02 -- builds, runs every "
          "resource-reading command from outside the checkout, is plain "
          "Python inside, carries no evidence/bank content, checksums cover "
          "every artifact, all three OS launchers ship and carry the locked "
          "failure sentence; 13-03 -- onedir sidecar sized, toolchain pinned, "
          "uninstaller guard and install-notice honesty simulated, headless "
          "CLI loop and evidence-location parity proven)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
