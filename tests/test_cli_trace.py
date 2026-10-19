import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / 'main.py'
IR = ROOT / 'examples/ir/live_loop.ir'


def run(*args):
    return subprocess.run([sys.executable, str(PROGRAM), str(IR), *args],
                          cwd=ROOT, text=True, capture_output=True)


def test_legacy_json_output_matches_trace_output():
    normal = run('--analysis', 'live')
    traced = run('--analysis', 'live', '--trace', 'jsonl')
    assert normal.returncode == traced.returncode == 0
    assert json.loads(normal.stdout) == json.loads(traced.stdout)
    assert traced.stderr.startswith('{')
    assert len(traced.stderr.strip().splitlines()) > 6
    for line in traced.stderr.splitlines():
        assert isinstance(json.loads(line), dict)


def test_cli_file_outputs_are_separate_and_invalid_args_fail(tmp_path):
    result_path = tmp_path / 'result.json'
    trace_path = tmp_path / 'trace.jsonl'
    done = run('--analysis', 'live', '--trace', 'jsonl',
               '--trace-output', str(trace_path), '--output', str(result_path))
    assert done.returncode == 0, done.stderr
    assert done.stdout == '' and done.stderr == ''
    assert json.loads(result_path.read_text(encoding='utf-8'))['direction'] == 'backward'
    assert json.loads(trace_path.read_text(encoding='utf-8').splitlines()[0])['node'] == 6
    assert run('--analysis', 'cfg', '--trace', 'text').returncode != 0
    assert run('--analysis', 'live', '--trace-output', str(trace_path)).returncode != 0
    assert run('--analysis', 'live', '--trace', 'text', '--trace-output', str(result_path), '--output', str(result_path)).returncode != 0
    assert run('--analysis', 'live', '--trace', 'text', '--trace-output', str(IR)).returncode != 0
