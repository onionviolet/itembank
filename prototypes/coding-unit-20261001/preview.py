"""Preview the original unit through native runtime-owned practice sessions."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from surfaces import session
from daemon_roundtrip import start_daemon

BANK = ROOT / 'fixtures' / 'coding_boundary_unit.md'


def prepare(root):
    """Use the existing paired composition to retain the authored unit order."""
    root = Path(root)
    bank = root / BANK.name
    shutil.copy2(BANK, bank)
    out = root / '_attempts' / 'session_boundary_workshop.json'
    return session.do_start(str(bank), {'count': 4, 'seed': 0,
                                      'pair': 'boundary-workshop'},
                            'practice', str(out), False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='itembank-coding-unit-') as root:
        view = prepare(root)
        proc, base, _lines = start_daemon(root, '--port', str(args.port))
        try:
            print('Lesson: ' + base + 'lesson/coding_boundary_unit', flush=True)
            print('Practice: ' + base + 'quiz/coding_boundary_unit?mode=practice&session=' + view['session_id'], flush=True)
            print('Disposable root: ' + root, flush=True)
            try:
                input('Press Enter to stop the preview and remove its synthetic files: ')
            except (EOFError, KeyboardInterrupt):
                pass
        finally:
            proc.terminate()
            proc.wait(timeout=5)
            proc.stdout.close()


if __name__ == '__main__':
    main()
