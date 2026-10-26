"""PolyDash's shared parse → analyze → IR boundary."""
from dataclasses import dataclass

from .analyzer import analyze
from .loaders import ParseFailure, load
from .model import Dashboard, Diagnostic


@dataclass
class Result:
    ir: Dashboard | None
    diagnostics: list[Diagnostic]

    def structured(self):
        return [diagnostic.to_dict() for diagnostic in self.diagnostics]

    def human(self):
        return "\n".join(diagnostic.human() for diagnostic in self.diagnostics)


def check(text: str, filename: str = "dashboard.json") -> Result:
    try:
        ir = load(text, filename)
    except ParseFailure as error:
        return Result(None, [error.diagnostic])
    diagnostics = analyze(ir)
    # Only validated IR can cross the downstream generation boundary.
    return Result(None if any(d.severity == "error" for d in diagnostics) else ir, diagnostics)
