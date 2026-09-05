"""The Phase 17B clean-machine restore drill (gate G10, 17B-CONTEXT D-07).

A course that only restores on the machine that authored it is not portable,
and a restore that silently drops a capability is worse than one that refuses:
this drill exists so neither claim can be made on trust. It clones the
repository at a named commit into a temporary directory, gives the process
under test a fresh empty data directory, an empty home, and no network, then
exports the tracer's course through the frozen Phase 14B package surface and
restores it into that empty directory with the cloned code. Every canonical
object the source registry holds is checked for at the destination by object
id and by file, and everything the restore could not carry is printed in one
loss report rather than left for a reader to notice.

Stdlib only, by 17B-CONTEXT D-08. It takes a commit hash rather than this
working tree's state so Phase 17C can rerun it as a sweep against any commit.

The drill runs its own body twice: once as the driver in this repository, and
once as the worker inside the clone. The worker is this same file, copied into
the work directory and run with the clone on `PYTHONPATH`, so every itembank
import the worker makes resolves to the code at the tested commit and never to
the code in this working tree.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

# The unreachable address every proxy variable points at. Port 9 is the
# discard port and nothing listens on loopback there; a process that tries to
# reach the network through the environment fails fast rather than hanging.
UNREACHABLE_PROXY = "http://127.0.0.1:9"

PROXY_VARIABLES = ("http_proxy", "https_proxy", "ftp_proxy", "all_proxy",
                   "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "ALL_PROXY")

# Phase 14B froze no offline flag: `course_package.py` is structurally offline
# (it imports no urllib, no socket, and no subprocess) and the 14B clean
# restore scenario enforced offline by redirecting the home directory only.
# `ITEMBANK_NO_NETWORK` is this repository's conventional offline marker,
# recorded in 16B-03 as read by no shipped code, so it is set as a declaration
# of intent and the enforcement below is what actually holds.
OFFLINE_MARKER = "ITEMBANK_NO_NETWORK"

# The home variables the frozen 14B drill redirects (fixtures/corpus_14b.py,
# `clean_machine_dest`). A restore that quietly read the exporting machine's
# settings or evidence store would pass while proving nothing.
HOME_VARIABLES = ("HOME", "APPDATA", "XDG_DATA_HOME", "USERPROFILE")

# Installed on the worker's path so a socket call raises instead of reaching
# the network. The proxy variables alone only redirect libraries that honor
# them; this closes the rest.
BLOCKER_SOURCE = '''"""Make the network unavailable to the process under test.

Imported automatically by the interpreter, before the code under test runs, so
any attempt to open a socket raises rather than reaching a host.
"""
import socket


class NetworkUnavailable(OSError):
    pass


def refuse(*args, **kwargs):
    raise NetworkUnavailable(
        "the restore drill made the network unavailable to this process")


socket.socket = refuse
socket.create_connection = refuse
socket.create_server = refuse
socket.getaddrinfo = refuse
'''


def run_git(repo, args):
    """Run one git command in `repo` and return its stripped stdout.

    Git is the only subprocess the driver runs, and it runs none inside the
    worker: the clone is set up before the process under test starts.
    """
    proc = subprocess.run(["git", "-C", repo] + args, capture_output=True,
                          text=True)
    if proc.returncode != 0:
        sys.exit("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout.strip()


def prepare_workdir(workdir):
    """An empty work directory, rebuilt from scratch on every run.

    A drill that reused a previous run's directory could pass on last run's
    bytes, which is exactly the failure this gate exists to catch.
    """
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    return workdir


def clone_at_commit(repo, commit, clone_dir):
    """Clone `repo` into `clone_dir` and check out `commit` detached.

    A local clone is a file copy, so this step needs no network either.
    """
    proc = subprocess.run(["git", "clone", "--quiet", "--no-checkout", repo,
                           clone_dir], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("git clone failed: %s" % proc.stderr.strip())
    run_git(clone_dir, ["checkout", "--quiet", "--detach", commit])
    return clone_dir


def worker_environment(clone_dir, offline_dir, home_dir):
    """The environment of the process under test: the clone on the path, an
    empty home, every proxy pointing nowhere, and the socket blocker armed."""
    env = dict(os.environ)
    for name in PROXY_VARIABLES:
        env[name] = UNREACHABLE_PROXY
    env["no_proxy"] = ""
    env["NO_PROXY"] = ""
    env[OFFLINE_MARKER] = "1"
    for name in HOME_VARIABLES:
        env[name] = home_dir
    env["PYTHONPATH"] = os.pathsep.join([offline_dir, clone_dir])
    env.pop("ANKI_CONNECT_URL", None)
    return env


def object_label(row):
    return "%s %s (%s)" % (row.get("kind"), row.get("path"),
                           row.get("object_id"))


def loss_rows(result):
    """One flat list of every capability the drill could not carry, from the
    export-time report, the restore's own report, and the drill's own checks.

    The three sources stay distinguishable in the `origin` column, because an
    export-time loss and a restore-time loss are different failures and a
    reader who cannot tell them apart cannot route either one.
    """
    rows = []
    for row in result["export_losses"]:
        rows.append(("export", row["category"], row["target"], row["reason"]))
    for row in result["restore_losses"]:
        rows.append(("restore", row["category"], row["target"], row["reason"]))
    for row in result["missing_objects"]:
        rows.append(("drill", "canonical-object-missing", object_label(row),
                     "this object is in the source registry and is not at the "
                     "destination after the restore"))
    events = result["source_events"]
    exported = result["exported_events"]
    if events and not exported:
        rows.append(("drill", "evidence-not-carried",
                     "%s/%s events" % (exported, events),
                     "the source evidence log holds %d events and the package "
                     "carried %d; no loss category names this"
                     % (events, exported)))
    return rows


def print_loss_report(rows):
    """Print the loss report, and say so in words when it is empty.

    An empty report printed as nothing reads as "nothing was checked" exactly
    as easily as "nothing was lost", and those are different claims. The
    wording follows `course_package.loss_report_text` for the same reason.
    """
    if not rows:
        print("loss report: none")
        return
    print("loss report: %d row(s)" % len(rows))
    for origin, category, target, reason in rows:
        print("  [%s] %s: %s" % (origin, category, target))
        print("      %s" % reason)


def worker_spec(workdir, source_course):
    return {
        "source_course": source_course,
        "package_dir": os.path.join(workdir, "package"),
        "dest_dir": os.path.join(workdir, "data"),
    }


def run_worker(spec_path):
    """The process under test: export, verify, restore, and report, using the
    cloned code and nothing from the calling tree.

    Every import happens here rather than at module import time, so the driver
    can run in a working tree whose modules must never be the ones exercised.
    """
    import socket

    import course_package
    import evidence
    import identity
    import journal

    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    source_course = spec["source_course"]
    package_dir = spec["package_dir"]
    dest_dir = spec["dest_dir"]

    network_refused = False
    try:
        socket.create_connection(("127.0.0.1", 9), 0.1)
    except Exception:
        # Any failure proves the point the drill needs proven: this process
        # cannot open a connection. The exception type is not asserted,
        # because a blocked socket and a refused connection are both offline.
        network_refused = True

    registry = journal.read_registry(source_course)
    source_rows = [
        {"object_id": row.get("object_id"), "kind": row.get("kind"),
         "path": row.get("path"), "fingerprint": row.get("fingerprint")}
        for row in identity.registry_rows(list(registry.values()))]

    manifest = course_package.export_package(source_course, source_course,
                                             package_dir)
    verified = course_package.verify_manifest(package_dir)
    restored = course_package.restore_package(package_dir, dest_dir, "human",
                                              "weibao")

    dest_registry = journal.read_registry(dest_dir)
    missing = []
    for row in source_rows:
        landed = dest_registry.get(row["object_id"])
        on_disk = os.path.exists(os.path.join(dest_dir, row["path"] or ""))
        if landed is None or not on_disk:
            missing.append(row)

    source_log = evidence.log_path(source_course)
    source_events = 0
    if os.path.exists(source_log):
        source_events = sum(1 for _ in evidence.events(source_log))
    # The count of events the package actually carried, read from the package
    # itself rather than recomputed, so the number is what a receiving machine
    # would get and not what this drill believes it should have got.
    exported_path = os.path.join(package_dir, course_package.EVIDENCE_DIRNAME,
                                 course_package.EVIDENCE_FILENAME)
    exported_events = 0
    if os.path.exists(exported_path):
        with open(exported_path, "r", encoding="utf-8") as fh:
            exported_events = sum(1 for line in fh if line.strip())

    print(json.dumps({
        "network_refused": network_refused,
        "manifest_keys": sorted(manifest.keys()),
        "manifest_state": manifest["state"],
        "entries": [{"kind": e["kind"], "relpath": e["relpath"],
                     "object_id": e["object_id"]}
                    for e in manifest["entries"]],
        "verify": {"entries_verified": verified["entries_verified"],
                   "complete": verified["complete"],
                   "mismatches": verified["mismatches"],
                   "missing": verified["missing"]},
        "restore": {"entries_verified": restored["entries_verified"],
                    "entries_in_manifest": restored["entries_in_manifest"],
                    "complete": restored["complete"],
                    "evidence_recorded": restored["evidence_recorded"]},
        "export_losses": restored["losses"],
        "restore_losses": restored["restore_losses"],
        "source_objects": source_rows,
        "missing_objects": missing,
        "source_events": source_events,
        "exported_events": exported_events,
    }))
    return 0


def drive(commit, workdir, course_relpath):
    """Set the drill up, run the worker inside the clone, and judge it.

    The judgment is deliberately here and not in the worker: the worker
    reports what happened, the driver decides whether that is a pass, so a
    change to the code under test can never move the bar it is judged by.
    """
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resolved = run_git(repo, ["rev-parse", commit])
    workdir = prepare_workdir(os.path.abspath(workdir))

    print("restore drill: repository %s" % repo)
    print("restore drill: commit %s (%s)" % (resolved, commit))
    print("restore drill: workdir %s" % workdir)

    clone_dir = clone_at_commit(repo, resolved, os.path.join(workdir, "clone"))
    print("restore drill: cloned at commit, HEAD %s"
          % run_git(clone_dir, ["rev-parse", "HEAD"]))

    # The journal, the registry, and the evidence log are deliberately
    # untracked (non-negotiable 3: evidence stays on disk, never in the
    # repository), so the exporting side has to come from the live course
    # rather than from the clone. It is copied first, so the drill never
    # mutates the repository's own fixture.
    source_course = os.path.join(workdir, "source_course")
    shutil.copytree(os.path.join(repo, course_relpath), source_course)
    print("restore drill: source course copied from %s" % course_relpath)

    dest_dir = os.path.join(workdir, "data")
    os.makedirs(dest_dir)
    home_dir = os.path.join(workdir, "home")
    os.makedirs(home_dir)
    if os.listdir(dest_dir):
        sys.exit("restore drill: the data directory must start empty")
    print("restore drill: fresh empty data directory %s" % dest_dir)

    offline_dir = os.path.join(workdir, "offline")
    os.makedirs(offline_dir)
    with open(os.path.join(offline_dir, "sitecustomize.py"), "w",
              encoding="utf-8") as fh:
        fh.write(BLOCKER_SOURCE)
    print("restore drill: network made unavailable (proxies at %s, sockets "
          "refused, %s=1)" % (UNREACHABLE_PROXY, OFFLINE_MARKER))

    spec_path = os.path.join(workdir, "spec.json")
    with open(spec_path, "w", encoding="utf-8") as fh:
        json.dump(worker_spec(workdir, source_course), fh)
    worker_path = os.path.join(workdir, "restore_drill_worker.py")
    shutil.copyfile(os.path.abspath(__file__), worker_path)

    env = worker_environment(clone_dir, offline_dir, home_dir)
    proc = subprocess.run([sys.executable, worker_path, "--worker", spec_path],
                          cwd=clone_dir, env=env, capture_output=True,
                          text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        print("restore drill: FAIL, the export and restore raised")
        return 1
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        sys.stderr.write(proc.stdout)
        print("restore drill: FAIL, the worker printed no result")
        return 1

    print("restore drill: network refused inside the worker = %s"
          % result["network_refused"])
    print("manifest: state %s, keys %s" % (result["manifest_state"],
                                           ", ".join(result["manifest_keys"])))
    print("manifest: %d payload entr(y/ies) carried" % len(result["entries"]))
    for entry in result["entries"]:
        print("  carried: %s %s (%s)" % (entry["kind"], entry["relpath"],
                                         entry["object_id"]))
    verify = result["verify"]
    print("manifest validation: %d of %d entries verified by recomputation, "
          "complete = %s" % (verify["entries_verified"],
                             len(result["entries"]), verify["complete"]))
    restore = result["restore"]
    print("restore: %d of %d entries verified, complete = %s, evidence events "
          "recorded = %d" % (restore["entries_verified"],
                             restore["entries_in_manifest"],
                             restore["complete"],
                             restore["evidence_recorded"]))
    print("source registry: %d canonical object(s); %d did not reach the "
          "destination" % (len(result["source_objects"]),
                           len(result["missing_objects"])))
    print("evidence: %d event(s) in the source log, %d carried by the package"
          % (result["source_events"], result["exported_events"]))

    rows = loss_rows(result)
    print_loss_report(rows)

    failures = []
    if not result["network_refused"]:
        failures.append("the worker could still open a socket, so the drill "
                        "did not run offline")
    if not verify["complete"]:
        failures.append("manifest validation is incomplete")
    if not restore["complete"]:
        failures.append("the restore did not verify every manifest entry")
    if result["missing_objects"]:
        failures.append("the first canonical object the restore did not carry "
                        "is %s" % object_label(result["missing_objects"][0]))
    if result["source_events"] and not result["exported_events"]:
        failures.append("the source evidence log holds %d event(s) and the "
                        "package carried none"
                        % result["source_events"])

    if failures:
        for reason in failures:
            print("restore drill: FAIL, %s" % reason)
        return 1
    print("restore drill: PASS")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(
        description="Phase 17B clean-machine restore drill (gate G10)")
    parser.add_argument("--commit", default="HEAD",
                        help="the commit to clone and test")
    parser.add_argument("--workdir", required=False,
                        help="a temporary directory, rebuilt on every run")
    parser.add_argument("--course", default="course_fixture_17b",
                        help="the course directory, relative to the repository")
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        return run_worker(args.worker)
    if not args.workdir:
        parser.error("--workdir is required")
    return drive(args.commit, args.workdir, args.course)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
