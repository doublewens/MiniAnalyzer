"""M4 reference/student plugin contract and lazy-import checks."""
import pytest

from analyzer.analysis.live_variable import LiveVariableAnalysis
from analyzer.comparison import compare_analysis_results
from analyzer.cfg.builder import CFGBuilder
from analyzer.dataflow.solver import WorklistSolver
from analyzer.ir.reader import IRReader
from analyzer.registry import (AnalysisRegistrationError, available_analyses,
                               create_analysis)
from labs.student.registry import STUDENT_ANALYSES
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def context(fname='live_loop.ir'):
    ir = IRReader.read(ROOT/'examples'/'ir'/fname)
    return ir, CFGBuilder.build(ir)


def test_registry_contains_reference_and_student_and_loads_lazily():
    listed = available_analyses()
    assert listed['reference'] == ['live', 'rd']
    assert listed['student'] == ['live', 'rd']
    ir, cfg = context()
    teacher = create_analysis('live', 'reference', ir, cfg)
    student = create_analysis('live', 'student', ir, cfg)
    assert isinstance(teacher, LiveVariableAnalysis)
    assert teacher.__class__ is not student.__class__
    assert teacher.name == student.name


def test_student_live_is_independent_and_semantically_matches_teacher():
    for name in ('live.ir', 'live_loop.ir', 'rd_branch.ir'):
        ir, cfg = context(name)
        reference = WorklistSolver().solve(create_analysis('live', 'reference', ir, cfg))
        student = WorklistSolver().solve(create_analysis('live', 'student', ir, cfg))
        comparison = compare_analysis_results('live', reference, student)
        assert comparison['equivalent']
        assert comparison['differences'] == []


def test_student_rd_is_intentionally_unfinished_and_does_not_fallback():
    ir, cfg = context('rd_branch.ir')
    student = create_analysis('rd', 'student', ir, cfg)
    with pytest.raises(NotImplementedError, match='Student RD lab unfinished'):
        WorklistSolver().solve(student)
    # Student failure cannot break an independently resolved reference run.
    reference = WorklistSolver().solve(create_analysis('rd', 'reference', ir, cfg))
    assert 'x@4' in reference.in_facts[7].values


def test_new_student_algorithm_can_be_registered_without_core_changes(monkeypatch):
    monkeypatch.setitem(STUDENT_ANALYSES, 'extra-live',
                        'labs.student.live_variable:StudentLiveVariableAnalysis')
    ir, cfg = context()
    analysis = create_analysis('extra-live', 'student', ir, cfg)
    assert WorklistSolver().solve(analysis).in_facts[3].values == {'x', 'y'}


def test_invalid_or_missing_plugin_is_explained_without_reference_damage(monkeypatch):
    ir, cfg = context()
    with pytest.raises(AnalysisRegistrationError, match='not registered'):
        create_analysis('does-not-exist', 'student', ir, cfg)
    monkeypatch.setitem(STUDENT_ANALYSES, 'broken', 'missing_student_module:BadClass')
    with pytest.raises(AnalysisRegistrationError, match='cannot load'):
        create_analysis('broken', 'student', ir, cfg)
    monkeypatch.setitem(STUDENT_ANALYSES, 'invalid', 'analyzer.ir.reader:IRReader')
    with pytest.raises(AnalysisRegistrationError, match='DataflowAnalysis subclass'):
        create_analysis('invalid', 'student', ir, cfg)
    assert WorklistSolver().solve(create_analysis('live', 'reference', ir, cfg))
