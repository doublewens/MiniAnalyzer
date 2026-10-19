"""Read-only teaching observations for the v0.3-compatible Worklist solver.

Trace events store detached JSON-compatible snapshots, not references to Facts.
Observers are deliberately outside the solver's transfer / scheduling decisions.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from typing import Any


@dataclass(frozen=True)
class TraceEvent:
    """One *processed node* (not one whole-graph iteration).

    For forward analysis, ``merged`` represents new IN and ``transferred``
    represents new OUT. For backward analysis, the roles reverse.
    """

    step: int
    analysis: str
    direction: str
    node: int
    instruction: str
    queue_before: tuple[int, ...]
    queue_after: tuple[int, ...]
    sources: tuple[dict[str, Any], ...]
    old_in: Any
    old_out: Any
    merged: Any
    transferred: Any
    new_in: Any
    new_out: Any
    changed: bool
    enqueued: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a detached serializable representation."""
        return deepcopy({
            "step": self.step,
            "analysis": self.analysis,
            "direction": self.direction,
            "node": self.node,
            "instruction": self.instruction,
            "queue_before": list(self.queue_before),
            "queue_after": list(self.queue_after),
            "sources": list(self.sources),
            "old_in": self.old_in,
            "old_out": self.old_out,
            "merged": self.merged,
            "transferred": self.transferred,
            "new_in": self.new_in,
            "new_out": self.new_out,
            "changed": self.changed,
            "enqueued": list(self.enqueued),
        })


class TraceCollector:
    """In-memory observer for tests, student replay and demonstrations."""
    def __init__(self):
        self.events: list[dict[str, Any]] = []

    def on_step(self, event: TraceEvent) -> None:
        self.events.append(event.to_dict())


class JSONLTraceWriter:
    """Append one standalone JSON object per processed node to a text stream."""
    def __init__(self, stream):
        self.stream = stream

    def on_step(self, event: TraceEvent) -> None:
        self.stream.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


class TextTraceWriter:
    """Readable trace for teacher-led live demonstrations."""
    def __init__(self, stream):
        self.stream = stream

    def on_step(self, event: TraceEvent) -> None:
        d = event.to_dict()
        s = self.stream
        s.write(f"[Step {d['step']:>3}] Node {d['node']}: {d['instruction']} "
                f"({d['direction']})\n")
        s.write(f"  worklist before: {d['queue_before']}\n")
        for src in d['sources']:
            via = 'boundary' if src['source'] == 'boundary' else f"node {src['node']}"
            s.write(f"  incoming from {via}: {src['fact']}\n")
        label = 'IN' if d['direction'] == 'forward' else 'OUT'
        other = 'OUT' if d['direction'] == 'forward' else 'IN'
        s.write(f"  merge -> {label}[{d['node']}] = {d['merged']}\n")
        s.write(f"  transfer -> {other}[{d['node']}] = {d['transferred']}\n")
        s.write(f"  old IN/OUT: {d['old_in']} / {d['old_out']}\n")
        s.write(f"  new IN/OUT: {d['new_in']} / {d['new_out']}\n")
        s.write(f"  changed: {'yes' if d['changed'] else 'no'}; "
                f"enqueued: {d['enqueued']}; worklist after: {d['queue_after']}\n\n")


def notify(observer, event: TraceEvent) -> None:
    """Call an observer object, or a plain callback if one was supplied."""
    if hasattr(observer, 'on_step'):
        observer.on_step(event)
    elif callable(observer):
        observer(event)
    else:
        raise TypeError('observer must be callable or expose on_step(event)')
