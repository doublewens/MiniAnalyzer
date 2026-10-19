"""MiniAnalyzer v0.4 M1-M4: backwards-compatible Teaching IR CLI.

Default (no --impl/--compare): same schema as v0.3/M3.
Student algorithms are loaded only when explicitly selected.
"""
import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import sys

from analyzer.ir.reader import IRReader
from analyzer.cfg.builder import CFGBuilder
from analyzer.dataflow.solver import WorklistSolver
from analyzer.dataflow.trace import TextTraceWriter, JSONLTraceWriter
from analyzer.comparison import compare_analysis_results
from analyzer.registry import (AnalysisRegistrationError, available_analyses,
                               create_analysis)


def _render_trace(trace_format, stream):
    if trace_format == "text":
        return TextTraceWriter(stream)
    if trace_format == "jsonl":
        return JSONLTraceWriter(stream)
    return None


def main():
    parser = argparse.ArgumentParser(description="MiniAnalyzer v0.4 M1-M4 teaching preview")
    parser.add_argument("file", nargs="?", help="input Teaching IR file")
    parser.add_argument("--analysis", default="cfg",
                        help="ir, cfg, live, rd, or a registered student extension")
    parser.add_argument("--impl", choices=["reference", "student"], default="reference",
                        help="algorithm implementation (default: reference)")
    parser.add_argument("--compare", action="store_true",
                        help="compare reference and student final IN/OUT facts; requires a registered pair")
    parser.add_argument("--list-analyses", action="store_true",
                        help="list registered reference/student algorithms and exit")
    parser.add_argument("--output", help="optional JSON result output file")
    parser.add_argument("--trace", choices=["text", "jsonl"],
                        help="trace Worklist processing; available for individual dataflow runs")
    parser.add_argument("--trace-output", help="optional trace file; defaults to stderr")
    args = parser.parse_args()

    if args.list_analyses:
        if args.file or args.trace or args.trace_output or args.output or args.compare:
            parser.error("--list-analyses must be used without file/output/trace/compare")
        print(json.dumps(available_analyses(), ensure_ascii=False, indent=2))
        return 0
    if not args.file:
        parser.error("an IR file is required unless --list-analyses is used")
    if args.trace and args.analysis in ("ir", "cfg"):
        parser.error("--trace requires a registered dataflow analysis")
    if args.trace_output and not args.trace:
        parser.error("--trace-output requires --trace")
    if args.compare and args.analysis in ("ir", "cfg"):
        parser.error("--compare requires a registered dataflow analysis")
    if args.compare and args.trace:
        parser.error("--compare and --trace are separate operations; run trace with --impl")
    if args.compare and args.impl != "reference":
        parser.error("--compare selects both implementations; omit --impl student")
    if args.analysis in ("ir", "cfg") and args.impl != "reference":
        parser.error("IR and CFG are shared infrastructure; --impl student is for dataflow analyses")

    source_path = Path(args.file).resolve()
    output_path = Path(args.output).resolve() if args.output else None
    trace_path = Path(args.trace_output).resolve() if args.trace_output else None
    if output_path and output_path == source_path:
        parser.error("result output must not overwrite the input IR file")
    if trace_path and trace_path == source_path:
        parser.error("trace output must not overwrite the input IR file")
    if output_path and trace_path and output_path == trace_path:
        parser.error("trace output must not overwrite analysis result output")

    try:
        program = IRReader.read(args.file)
        if args.analysis == "ir":
            result = program.to_dict()
        else:
            cfg = CFGBuilder.build(program)
            if args.analysis == "cfg":
                result = cfg.to_dict()
            elif args.compare:
                reference = WorklistSolver().solve(
                    create_analysis(args.analysis, "reference", program, cfg)
                )
                student = WorklistSolver().solve(
                    create_analysis(args.analysis, "student", program, cfg)
                )
                result = compare_analysis_results(args.analysis, reference, student)
            else:
                analysis = create_analysis(args.analysis, args.impl, program, cfg)
                if args.trace_output:
                    stream_ctx = open(args.trace_output, "w", encoding="utf-8")
                else:
                    stream_ctx = nullcontext(sys.stderr)
                with stream_ctx as stream:
                    observer = _render_trace(args.trace, stream)
                    result = WorklistSolver().solve(analysis, observer=observer).to_dict()
    except (AnalysisRegistrationError, NotImplementedError) as exc:
        parser.error(str(exc))

    output_text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)
    # A mismatched comparison emits a fully inspectable JSON result, and
    # returns a failure code for automated student tests/CI.
    return 1 if args.compare and not result["equivalent"] else 0


if __name__ == "__main__":
    sys.exit(main())
