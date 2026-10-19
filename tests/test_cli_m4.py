"""User workflows: reference runs, student runs, comparison, clear failures."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT/'main.py'


def run(ir=None, *args):
    cmd = [sys.executable, str(MAIN)]
    if ir:
        cmd.append(str(ROOT/'examples'/'ir'/ir))
    cmd.extend(args)
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def test_list_algorithms_without_file():
    cmd = run(None, '--list-analyses')
    assert cmd.returncode == 0
    listed = json.loads(cmd.stdout)
    assert listed == {'reference': ['live', 'rd'], 'student': ['live', 'rd']}


def test_default_is_reference_and_legacy_json_is_identical():
    for analysis in ('live', 'rd', 'ir', 'cfg'):
        old = run('rd_branch.ir', '--analysis', analysis)
        explicit = run('rd_branch.ir', '--analysis', analysis, '--impl', 'reference')
        assert old.returncode == explicit.returncode == 0
        assert old.stdout == explicit.stdout


def test_student_live_matches_reference_and_compare_succeeds():
    student = run('live_loop.ir', '--analysis', 'live', '--impl', 'student')
    reference = run('live_loop.ir', '--analysis', 'live', '--impl', 'reference')
    assert student.returncode == reference.returncode == 0
    assert json.loads(student.stdout) == json.loads(reference.stdout)
    comparison = run('live_loop.ir', '--analysis', 'live', '--compare')
    assert comparison.returncode == 0
    result = json.loads(comparison.stdout)
    assert result['equivalent'] is True
    assert result['differences'] == []
    assert result['reference']['nodes'] == result['student']['nodes']


def test_student_trace_works_and_does_not_change_result():
    ordinary = run('live_loop.ir', '--analysis', 'live', '--impl', 'student')
    traced = run('live_loop.ir', '--analysis', 'live', '--impl', 'student', '--trace', 'jsonl')
    assert ordinary.returncode == traced.returncode == 0
    assert json.loads(ordinary.stdout) == json.loads(traced.stdout)
    assert json.loads(traced.stderr.splitlines()[0])['direction'] == 'backward'


def test_incomplete_student_does_not_silently_use_reference():
    broken = run('rd_branch.ir', '--analysis', 'rd', '--impl', 'student')
    assert broken.returncode != 0
    assert broken.stdout == ''
    assert 'Student RD lab unfinished' in broken.stderr
    assert 'Traceback' not in broken.stderr
    normal = run('rd_branch.ir', '--analysis', 'rd')
    assert normal.returncode == 0
    assert 'x@4' in normal.stdout


def test_compare_incomplete_student_exits_nonzero_with_actionable_message():
    cmd = run('rd_branch.ir', '--analysis', 'rd', '--compare')
    assert cmd.returncode != 0
    assert 'Student RD lab unfinished' in cmd.stderr
    assert not cmd.stdout.strip()


def test_invalid_modes_are_rejected():
    commands = [
        ('rd_branch.ir', '--analysis', 'cfg', '--impl', 'student'),
        ('rd_branch.ir', '--analysis', 'ir', '--compare'),
        ('rd_branch.ir', '--analysis', 'rd', '--compare', '--trace', 'text'),
        ('rd_branch.ir', '--analysis', 'rd', '--compare', '--impl', 'student'),
        ('rd_branch.ir', '--analysis', 'not-known'),
        (None, '--analysis', 'live'),
    ]
    for command in commands:
        assert run(command[0], *command[1:]).returncode != 0


def test_cli_will_not_overwrite_input_with_results_or_trace():
    input_name = 'rd_branch.ir'
    path = ROOT/'examples'/'ir'/input_name
    before = path.read_bytes()
    assert run(input_name, '--analysis', 'rd', '--output', str(path)).returncode != 0
    assert run(input_name, '--analysis', 'live', '--trace', 'text',
               '--trace-output', str(path)).returncode != 0
    assert path.read_bytes() == before


def test_compare_can_save_json_without_trace(tmp_path):
    path = tmp_path/'comparison.json'
    result = run('rd_branch.ir', '--analysis', 'live', '--compare', '--output', str(path))
    assert result.returncode == 0 and result.stdout == ''
    assert json.loads(path.read_text(encoding='utf-8'))['equivalent']


def test_compare_mismatch_returns_one_and_explains_node_fact(monkeypatch, capsys):
    # Deliberately incorrect plugin tests the real CLI mismatch exit contract.
    from main import main
    from analyzer.dataflow.fact import SetFact
    from labs.student.live_variable import StudentLiveVariableAnalysis
    from labs.student.registry import STUDENT_ANALYSES

    # Put this class on an importable module, not a dynamic eval or exec.
    class IncorrectStudentLive(StudentLiveVariableAnalysis):
        def transfer_node(self, node, out_fact):
            return SetFact()  # mathematically wrong; should generate a difference

    import types
    import sys as py_sys
    custom_module = types.ModuleType('student_wrong_for_test')
    custom_module.IncorrectStudentLive = IncorrectStudentLive
    monkeypatch.setitem(py_sys.modules, 'student_wrong_for_test', custom_module)
    monkeypatch.setitem(STUDENT_ANALYSES, 'live',
                        'student_wrong_for_test:IncorrectStudentLive')
    monkeypatch.setattr(py_sys, 'argv', ['main.py', str(ROOT/'examples/ir/live_loop.ir'),
                                      '--analysis', 'live', '--compare'])
    assert main() == 1
    value = json.loads(capsys.readouterr().out)
    assert value['equivalent'] is False
    assert any(item.get('field') in ('in', 'out') for item in value['differences'])
