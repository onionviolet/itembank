#!/usr/bin/env python3
"""Reproduce the clean fixture workflow without building an app archive."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from a5_integrated_package_roundtrip import stage_test_fixtures


def main():
    with tempfile.TemporaryDirectory(prefix='itembank-fixture-closure-') as temp:
        clean = Path(temp)
        shutil.copytree(ROOT / 'tests', clean / 'tests',
                        ignore=shutil.ignore_patterns('node_modules', '__pycache__'))
        stage_test_fixtures(clean)
        # Modules come from source; only the test and synthetic inputs live in
        # the disposable root. This checks fixture closure without an archive.
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        result = subprocess.run(
            [sys.executable, str(clean / 'tests' / 'a3_course_workflows_roundtrip.py')],
            cwd=clean, env=env, capture_output=True, text=True, timeout=180)
        assert result.returncode == 0, result.stdout + result.stderr
    print('Clean synthetic A3 fixture journey passes without an app build')


if __name__ == '__main__':
    main()
