"""Compare semantic IN/OUT facts, not incidental Worklist scheduling counts."""
from __future__ import annotations


def compare_analysis_results(key: str, reference_result, student_result) -> dict:
    """Return an inspectable JSON-compatible comparison.

    Nodes and final fact values are assessed. `statistics.iterations` and
    `statistics.updates` are shown but deliberately not scored: valid Worklist
    scheduling strategies may require different numbers of node visits.
    """
    reference = reference_result.to_dict()
    student = student_result.to_dict()
    differences: list[dict] = []

    if reference["direction"] != student["direction"]:
        differences.append({
            "field": "direction", "reference": reference["direction"],
            "student": student["direction"],
        })

    ref_nodes = {row["index"]: row for row in reference["nodes"]}
    stu_nodes = {row["index"]: row for row in student["nodes"]}
    for node in sorted(set(ref_nodes) | set(stu_nodes)):
        if node not in ref_nodes or node not in stu_nodes:
            differences.append({"node": node, "field": "node_presence",
                                "reference": node in ref_nodes,
                                "student": node in stu_nodes})
            continue
        for field in ("in", "out"):
            expected = ref_nodes[node][field]
            actual = stu_nodes[node][field]
            if expected != actual:
                differences.append({"node": node, "field": field,
                                    "reference": expected, "student": actual})

    return {
        "analysis": key,
        "equivalent": not differences,
        "differences": differences,
        "reference": reference,
        "student": student,
        "comparison_scope": "final per-node IN/OUT facts and analysis direction",
        "note": "Equal results on these examples do not prove an algorithm correct for all programs.",
    }
