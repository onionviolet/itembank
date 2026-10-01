"""Verify owned source and frozen lane inputs before handing off this iteration."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def script_value(path):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'SCRIPT' for target in node.targets):
            if isinstance(node.value, ast.Constant):
                return node.value.value
    raise AssertionError('Missing core reading SCRIPT')


if __name__ == '__main__':
    operation_path = HERE / 'recovery/character-operation.json'
    if not operation_path.exists():
        operation_path = HERE / 'recovery/operation.json'
    operation = json.loads(operation_path.read_text())
    source = ROOT / operation['path']
    baseline = HERE / 'recovery/reading_desk.py.txt'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == operation['before']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == operation['after']
    assert script_value(source) == script_value(baseline), 'Core persistence/recovery script changed'
    for name, expected in json.loads((HERE / 'lane-inputs.json').read_text()).items():
        assert hashlib.sha256((HERE.parent / name).read_bytes()).hexdigest() == expected, name
    result = dict(source_sha256=operation['after'], core_reading_script='unchanged', frozen_lane_inputs='match')
    (HERE / 'freeze.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
