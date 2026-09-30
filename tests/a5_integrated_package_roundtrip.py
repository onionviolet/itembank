#!/usr/bin/env python3
"""Compare the explicit shipping inventory and run disposable package journeys."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build


def stage_test_fixtures(destination):
    """Carry every synthetic root used by the clean candidate journeys."""
    for name in ('fixtures', 'schemas', 'course_fixture_17b'):
        shutil.copytree(ROOT / name, destination / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))


def check_inventory(artifact):
    expected = set(build.STAGE_FILES)
    for directory in build.STAGE_DIRS:
        expected.update(str(path.relative_to(ROOT))
                        for path in (ROOT / directory).rglob('*')
                        if path.is_file() and '__pycache__' not in path.parts
                        and path.suffix != '.pyc')
    local_modules = {path.stem for path in ROOT.glob('*.py')}
    with zipfile.ZipFile(artifact) as archive:
        actual = {name for name in archive.namelist() if not name.endswith('/')}
        assert actual == expected | {'__main__.py'}, (actual - expected, expected - actual)
        for name in sorted(expected):
            raw = (ROOT / name).read_bytes()
            assert archive.read(name) == raw, 'Source/package bytes differ: ' + name
            if not name.endswith('.py'):
                continue
            tree = ast.parse(raw, filename=name)
            for node in ast.walk(tree):
                dependencies = []
                if isinstance(node, ast.Import):
                    dependencies = [alias.name.split('.')[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    dependencies = [node.module.split('.')[0]]
                for dependency in dependencies:
                    if dependency in local_modules:
                        assert dependency + '.py' in expected, (
                            name + ' imports an unstaged local module: ' + dependency)
    digest = hashlib.sha256(Path(artifact).read_bytes()).hexdigest()
    print('A5 package inventory: %d byte-identical source members; SHA256 %s' %
          (len(expected), digest), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--journeys', action='store_true',
                        help='Run existing served synthetic journeys against this fresh package')
    parser.add_argument('--out', type=Path,
                        help='Keep the disposable candidate and its fingerprint for review')
    parser.add_argument('--offline-restore', action='store_true',
                        help='Exercise package authorities without checkout module imports')
    parser.add_argument('--inventory-only', action='store_true',
                        help='Inspect byte coverage while integration owners are still active')
    parser.add_argument('--existing', type=Path,
                        help='Inspect source drift against an existing archive without building')
    args = parser.parse_args()
    if args.existing:
        expected = set(build.STAGE_FILES)
        for directory in build.STAGE_DIRS:
            expected.update(str(path.relative_to(ROOT)) for path in (ROOT / directory).rglob('*')
                            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
        with zipfile.ZipFile(args.existing) as archive:
            actual = set(archive.namelist())
            missing = sorted(expected - actual)
            changed = sorted(name for name in expected & actual
                             if archive.read(name) != (ROOT / name).read_bytes())
        report = {'archive_sha256': hashlib.sha256(args.existing.read_bytes()).hexdigest(),
                  'missing': missing, 'changed': changed,
                  'state': 'drift; new package verification deferred' if missing or changed else 'byte-identical'}
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / 'archive-drift.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        return
    with tempfile.TemporaryDirectory(prefix='itembank-a5-package-') as directory:
        artifact = build.build(str(args.out or directory))
        check_inventory(artifact)
        if not args.inventory_only or args.offline_restore:
            clean = Path(directory) / 'clean'
            (clean / 'tests').mkdir(parents=True)
            for path in (ROOT / 'tests').glob('*.py'):
                shutil.copy2(path, clean / 'tests' / path.name)
            # Redirect only the copied helper's launcher. Its imports still
            # resolve exclusively from the archive, not checkout modules.
            helper = clean / 'tests' / 'daemon_roundtrip.py'
            text = helper.read_text()
            launcher = 'os.path.join(ROOT, "itembank.py")'
            assert launcher in text, 'Daemon helper launcher changed; review package wiring'
            helper.write_text(text.replace(launcher, repr(str(Path(artifact).resolve()))))
            stage_test_fixtures(clean)
            env = dict(os.environ, PYTHONPATH=str(Path(artifact).resolve()))
            failures = []
            for name in ('course_package_roundtrip.py', 'reading_package_roundtrip.py',
                         'source_binding_surface_roundtrip.py', 'open_notebook_roundtrip.py',
                         'a4_source_recovery_roundtrip.py', 'a5_research_context_roundtrip.py',
                         'a5_inline_fields_roundtrip.py', 'a3_course_workflows_roundtrip.py'):
                result = subprocess.run([sys.executable, str(clean / 'tests' / name)],
                                        cwd=clean, env=env, timeout=180,
                                        capture_output=True, text=True)
                log = result.stdout + result.stderr
                if args.out:
                    (args.out / (name + '.log')).write_text(log)
                print('%s: %s' % (name, 'FAIL' if result.returncode else 'PASS'), flush=True)
                if result.returncode:
                    failures.append(name)
                    print(log[-4000:], flush=True)
            assert not failures, 'Clean packaged source/restore failed: ' + ', '.join(failures)
            print('A5 clean packaged source/rights/offline restore journeys pass')
        if args.journeys:
            for name in ('matching_workflow_roundtrip.py', 'ordering_workflow_roundtrip.py',
                         'question_workflow_recovery_roundtrip.py', 'course_workbench_roundtrip.py'):
                result = subprocess.run([sys.executable, str(ROOT / 'tests' / name),
                                         '--runtime', artifact], cwd=ROOT, timeout=180)
                assert result.returncode == 0, 'Packaged journey failed: ' + name
            print('A5 fresh packaged synthetic question/review/recovery journeys pass')


if __name__ == '__main__':
    main()
