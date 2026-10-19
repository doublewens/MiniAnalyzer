import re

from .program import Program
from .parser import IRParser


class IRReader:
    LINE_RE = re.compile(r"^\s*(\d+)\s*:\s*(.*?)\s*$")

    @staticmethod
    def read(filename):
        program = Program()

        with open(filename, "r", encoding="utf-8") as f:
            for file_line, raw in enumerate(f, start=1):
                raw = raw.strip()

                if not raw or raw.startswith("#"):
                    continue

                m = IRReader.LINE_RE.fullmatch(raw)
                if not m:
                    raise ValueError(
                        f"invalid IR syntax at file line {file_line}: {raw}"
                    )

                index = int(m.group(1))
                body = m.group(2).strip()

                if not body:
                    raise ValueError(
                        f"empty instruction at file line {file_line}"
                    )

                try:
                    inst = IRParser.parse_instruction(index, body)
                except ValueError as exc:
                    raise ValueError(
                        f"invalid IR at file line {file_line}: {exc}"
                    ) from exc

                program.add(inst)

        if not program.instructions:
            raise ValueError("IR program is empty")

        program.finalize()
        return program
