import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'main.py'


def cli(ir, *args):
    return subprocess.run([sys.executable, str(MAIN), str(ROOT / 'examples/ir' / ir), *args],
                          cwd=ROOT, capture_output=True, text=True)


def test_rd_cli_json_and_text_trace_do_not_change_result():
    normal = cli('rd_branch.ir', '--analysis', 'rd')
    traced = cli('rd_branch.ir', '--analysis', 'rd', '--trace', 'text')
    assert normal.returncode == traced.returncode == 0, traced.stderr
    assert json.loads(normal.stdout) == json.loads(traced.stdout)
    assert 'reaching-definitions' in normal.stdout
    assert 'Node 7' in traced.stderr
    assert 'merge -> IN[7]' in traced.stderr


def test_rd_jsonl_trace_and_result_are_isolated(tmp_path):
    result_path = tmp_path / 'rd_result.json'
    trace_path = tmp_path / 'rd_steps.jsonl'
    done = cli('rd_loop.ir', '--analysis', 'rd', '--trace', 'jsonl',
               '--output', str(result_path), '--trace-output', str(trace_path))
    assert done.returncode == 0, done.stderr
    assert done.stdout == done.stderr == ''
    result = json.loads(result_path.read_text(encoding='utf-8'))
    events = [json.loads(line) for line in trace_path.read_text(encoding='utf-8').splitlines()]
    assert result['direction'] == 'forward'
    assert len(events) == result['statistics']['iterations']
    assert any(e['node'] == 3 and 'x@4' in e['new_in'] for e in events)


def test_bad_trace_args_for_rd_are_rejected(tmp_path):
    ir = ROOT / 'examples/ir/rd_branch.ir'
    assert cli('rd_branch.ir', '--analysis', 'rd', '--trace-output', str(tmp_path / 'x')).returncode != 0
    assert cli('rd_branch.ir', '--analysis', 'cfg', '--trace', 'text').returncode != 0
    assert cli('rd_branch.ir', '--analysis', 'rd', '--trace', 'text',
               '--trace-output', str(ir)).returncode != 0
