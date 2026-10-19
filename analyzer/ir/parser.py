from __future__ import annotations
import re

from .operand import Operand, Variable
from .instruction import (
    AssignInstruction,
    BinaryOpInstruction,
    UnaryOpInstruction,
    BranchInstruction,
    GotoInstruction,
    CallInstruction,
    ReturnInstruction,
    ExitInstruction,
)

VAR = r"[A-Za-z_][A-Za-z0-9_]*"
OPERAND = rf"(?:{VAR}|-?\d+|true|false)"


class IRParser:
    @staticmethod
    def parse_instruction(index: int, body: str):
        body = body.strip()

        if body == "exit":
            return ExitInstruction(index)

        if body == "return":
            return ReturnInstruction(index)

        m = re.fullmatch(rf"return\s+({OPERAND})", body)
        if m:
            return ReturnInstruction(index, Operand.parse(m.group(1)))

        m = re.fullmatch(r"goto\s+(\d+)", body)
        if m:
            return GotoInstruction(index, int(m.group(1)))

        m = re.fullmatch(
            rf"if\s+({OPERAND})\s*(==|!=|<=|>=|<|>)\s*({OPERAND})\s+goto\s+(\d+)",
            body,
        )
        if m:
            return BranchInstruction(
                index,
                Operand.parse(m.group(1)),
                m.group(2),
                Operand.parse(m.group(3)),
                int(m.group(4)),
            )

        m = re.fullmatch(rf"({VAR})\s*=\s*call\s+({VAR})\((.*)\)", body)
        if m:
            return CallInstruction(
                index=index,
                function=m.group(2),
                arguments=IRParser._parse_args(m.group(3)),
                result=Variable(m.group(1)),
            )

        m = re.fullmatch(rf"call\s+({VAR})\((.*)\)", body)
        if m:
            return CallInstruction(
                index=index,
                function=m.group(1),
                arguments=IRParser._parse_args(m.group(2)),
                result=None,
            )

        m = re.fullmatch(rf"({VAR})\s*=\s*([!-])\s*({OPERAND})", body)
        if m:
            return UnaryOpInstruction(
                index,
                Variable(m.group(1)),
                m.group(2),
                Operand.parse(m.group(3)),
            )

        m = re.fullmatch(rf"({VAR})\s*=\s*({OPERAND})\s*([+\-*/%])\s*({OPERAND})", body)
        if m:
            return BinaryOpInstruction(
                index,
                Variable(m.group(1)),
                Operand.parse(m.group(2)),
                m.group(3),
                Operand.parse(m.group(4)),
            )

        m = re.fullmatch(rf"({VAR})\s*=\s*({OPERAND})", body)
        if m:
            return AssignInstruction(
                index,
                Variable(m.group(1)),
                Operand.parse(m.group(2)),
            )

        raise ValueError(f"unsupported IR instruction: {body}")

    @staticmethod
    def _parse_args(text: str):
        text = text.strip()
        if not text:
            return []
        return [Operand.parse(part.strip()) for part in text.split(",")]
