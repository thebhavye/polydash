from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Span:
    file: str
    line: int
    column: int
    excerpt: str


@dataclass(frozen=True)
class Diagnostic:
    rule_id: str
    severity: str
    message: str
    path: str
    location: Span

    def to_dict(self):
        return asdict(self)

    def human(self):
        s = self.location
        return (f"{s.file}:{s.line}:{s.column}: {self.severity} {self.rule_id}: "
                f"{self.message}\n{s.excerpt}\n{' ' * (s.column - 1)}^")


@dataclass
class Dashboard:
    """Shared IR. Paths in spans identify all nodes, fields, and list items."""
    config: dict[str, Any]
    spans: dict[tuple, Span]

    def location(self, path):
        while path not in self.spans:
            path = path[:-1]
        return self.spans[path]


def pointer(path):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in path)
