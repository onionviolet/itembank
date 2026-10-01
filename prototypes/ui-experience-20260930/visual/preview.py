"""Loopback-only visual preview with vendored font routing."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

class Preview(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = path.split('?', 1)[0]
        if clean.startswith('/assets/fonts/'):
            target = (ROOT / 'fonts' / clean.removeprefix('/assets/fonts/')).resolve()
            if target.is_relative_to(ROOT / 'fonts'):
                return str(target)
        return super().translate_path(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8808)
    args = parser.parse_args()
    print(f'Visual comparison: http://127.0.0.1:{args.port}/comparison.html', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), partial(Preview, directory=str(HERE))).serve_forever()
