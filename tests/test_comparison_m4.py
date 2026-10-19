from analyzer.comparison import compare_analysis_results
from analyzer.dataflow.analysis import Direction
from analyzer.dataflow.fact import SetFact
from analyzer.dataflow.result import AnalysisResult


def result(direction=Direction.FORWARD, values=('d1',), iterations=3, updates=2):
    return AnalysisResult('test', direction, {1: SetFact(set(values))},
                          {1: SetFact({'d2'})}, iterations, updates)


def test_comparison_ignores_queue_counts_but_checks_facts():
    reference = result(iterations=3, updates=2)
    student = result(iterations=15, updates=8)
    response = compare_analysis_results('toy', reference, student)
    assert response['equivalent'] and response['differences'] == []
    assert response['reference']['statistics'] != response['student']['statistics']


def test_comparison_reports_node_fact_and_direction_mismatches():
    reference = result()
    student = result(direction=Direction.BACKWARD, values=('wrong',))
    response = compare_analysis_results('toy', reference, student)
    assert not response['equivalent']
    assert any(d['field'] == 'in' and d['node'] == 1 for d in response['differences'])
    assert any(d['field'] == 'direction' for d in response['differences'])


def test_comparison_reports_missing_nodes():
    reference = result()
    student = AnalysisResult('test', Direction.FORWARD, {2: SetFact()}, {2: SetFact()}, 1, 0)
    response = compare_analysis_results('toy', reference, student)
    assert not response['equivalent']
    assert sum(d['field'] == 'node_presence' for d in response['differences']) == 2
