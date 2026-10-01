"""Run the exact prototype presentation module on a disposable synthetic root."""
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import surfaces
path = Path(__file__).with_name('reading_desk.candidate.py.txt')
module = types.ModuleType('surfaces.reading_desk')
module.__file__ = str(path)
sys.modules[module.__name__] = module
surfaces.reading_desk = module
exec(compile(path.read_text(), str(path), 'exec'), module.__dict__)
import itembank
itembank.main()
