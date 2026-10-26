"""Collect-all rules driven by the shared schema, independent of source format."""
from collections import defaultdict

from .model import Diagnostic, pointer
from .schema import COMPONENTS, DASHBOARD

# Stable registration order is also the diagnostic order.
RULES = ("PD1001", "PD1002", "PD1003", "PD1004", "PD1005", "PD2001", "PD2002")


def analyze(dashboard, component_schema=None):
    registry = COMPONENTS if component_schema is None else component_schema
    findings = {rule: [] for rule in RULES}
    ids = defaultdict(list)

    def report(rule, message, path, severity="error"):
        findings[rule].append(Diagnostic(rule, severity, message, pointer(path), dashboard.location(path)))

    def check(value, spec, path):
        kind = spec.get("type", "object")
        matches = {
            "string": lambda: isinstance(value, str),
            "number": lambda: type(value) in (int, float),
            "boolean": lambda: isinstance(value, bool),
            "array": lambda: isinstance(value, list),
            "object": lambda: isinstance(value, dict),
        }
        if not matches[kind]():
            report("PD1004", f"Expected {kind}", path)
            return
        if "enum" in spec and value not in spec["enum"]:
            report("PD1004", f"Expected one of {spec['enum']}", path)
        if kind == "object" and "properties" in spec:
            properties(value, spec, path)
        elif kind == "array" and "items" in spec:
            for i, item in enumerate(value):
                check(item, spec["items"], path + (i,))

    def properties(value, spec, path):
        for required in spec.get("required", []):
            if required not in value:
                report("PD1003", f"Missing required field '{required}'", path + (required,))
        for name, item in value.items():
            here = path + (name,)
            if name not in spec["properties"]:
                report("PD1002", f"Unknown property '{name}'", here)
            else:
                check(item, spec["properties"][name], here)

    def walk(items, path):
        for i, component in enumerate(items):
            here = path + (i,)
            identity = component.get("id")
            if isinstance(identity, str):
                ids[identity].append(here + ("id",))
            kind = component.get("type")
            if kind is None and "type" not in component:
                properties(component, {"properties": {"id": {"type": "string"}, "type": {"type": "string"}},
                                       "required": ["id", "type"]}, here)
            elif not isinstance(kind, str):
                report("PD1004", "Expected string", here + ("type",))
                if "id" not in component:
                    report("PD1003", "Missing required field 'id'", here + ("id",))
            elif kind not in registry:
                report("PD1001", f"Unknown component type '{kind}'", here + ("type",))
                if "id" not in component:
                    report("PD1003", "Missing required field 'id'", here + ("id",))
            else:
                properties(component, registry[kind], here)
                title_spec = registry[kind]["properties"].get("title", {})
                title = component.get("title")
                # Leave unknown/ill-typed properties to the schema rules.
                if (kind in ("filter", "chart") and title_spec.get("type") == "string"
                        and ("title" not in component
                             or isinstance(title, str) and not title.strip())):
                    rule = "PD2001" if kind == "filter" else "PD2002"
                    report(rule, f"{kind.capitalize()} title is missing or blank",
                           here + ("title",), severity="warning")
            if "children" in component:
                walk(component["children"], here + ("children",))

    properties(dashboard.config, DASHBOARD, ())
    walk(dashboard.config.get("components", []), ("components",))
    for identity, paths in ids.items():
        if len(paths) > 1:
            for path in paths:
                report("PD1005", f"Duplicate component ID '{identity}'", path)
    return [diagnostic for rule in RULES for diagnostic in findings[rule]]
