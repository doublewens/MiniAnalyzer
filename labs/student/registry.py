"""Students may add a new name -> 'module:Class' entry here.

Do NOT change analyzer/dataflow/solver.py or the IR/CFG foundations.
Modules are loaded only if their implementation is selected, keeping the
reference demonstrations independent of unfinished student code.
"""
STUDENT_ANALYSES = {
    # Full, runnable example: how a student-written module plugs in.
    "live": "labs.student.live_variable:StudentLiveVariableAnalysis",
    # Independent assignment: incomplete by design; no reference fallback.
    "rd": "labs.student.reaching_definitions:StudentReachingDefinitionsAnalysis",
}
