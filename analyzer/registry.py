"""Explicit, lazily-loaded teaching algorithm registry.

Reference analyses never import student implementations. Student extensions are
registered in labs/student/registry.py, not by modifying solver or parser.

Plugin modules are Python code running with the user's privileges: only load
trusted student code in a normal Python environment.
"""
from __future__ import annotations

from importlib import import_module
from typing import Mapping

from analyzer.dataflow.analysis import DataflowAnalysis


REFERENCE_ANALYSES: dict[str, str] = {
    "live": "analyzer.analysis.live_variable:LiveVariableAnalysis",
    "rd": "analyzer.analysis.reaching_definitions:ReachingDefinitionsAnalysis",
}


class AnalysisRegistrationError(ValueError):
    """Invalid name, implementation kind or plugin contract."""


def registered_analyses(implementation: str) -> Mapping[str, str]:
    """Lookup a *configuration*, without importing any specific analysis module."""
    if implementation == "reference":
        return REFERENCE_ANALYSES
    if implementation == "student":
        from labs.student.registry import STUDENT_ANALYSES
        return STUDENT_ANALYSES
    raise AnalysisRegistrationError(
        f"unsupported implementation {implementation!r}; choose reference or student"
    )


def available_analyses() -> dict[str, list[str]]:
    return {
        implementation: sorted(registered_analyses(implementation))
        for implementation in ("reference", "student")
    }


def create_analysis(key: str, implementation: str, program, cfg) -> DataflowAnalysis:
    registered = registered_analyses(implementation)
    if key not in registered:
        options = ", ".join(sorted(registered)) or "(none)"
        raise AnalysisRegistrationError(
            f"analysis {key!r} is not registered for {implementation}; "
            f"available: {options}"
        )
    target = registered[key]
    if not isinstance(target, str) or target.count(":") != 1:
        raise AnalysisRegistrationError(
            f"invalid {implementation} registration for {key!r}: expected module:Class"
        )
    module_name, class_name = target.split(":", 1)
    if not module_name or not class_name:
        raise AnalysisRegistrationError(f"incomplete registration for {key!r}")
    try:
        module = import_module(module_name)
        analysis_class = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise AnalysisRegistrationError(
            f"cannot load {implementation} analysis {key!r} from {target}: {exc}"
        ) from exc
    if not isinstance(analysis_class, type) or not issubclass(analysis_class, DataflowAnalysis):
        raise AnalysisRegistrationError(
            f"{target} must be a DataflowAnalysis subclass"
        )
    return analysis_class(program, cfg)
