# PolyDash — Multi-Format Dashboard Compiler

PolyDash validates dashboard configurations before code generation, with errors
that point back to the source file. It builds on the Config2UI lab project idea;
the earlier prototype is not included in this repository.

## Current status

Implemented in this increment (issues #6–#11):

- JSON parsing with source positions and a documented grammar.
- Shared Dashboard IR and a small, data-driven component schema.
- Required-field, unknown-component/property, property-type and duplicate-ID
  validation, collecting all recoverable errors.
- Human and structured JSON diagnostics, a golden regression corpus and
  JSON/YAML equivalence tests.
- Optional YAML/YML front end: install the declared `yaml` extra (PyYAML).
  See [YAML support](docs/yaml-support.md) for the subset and installation.

HTML/CSS/JS code generation, live data access and a full compile CLI are
still planned. The CI workflow targets Windows, Linux and macOS. The check
adapter below validates input only. The new schema/IR
and diagnostic contracts are initial baselines for architecture-owner review;
the prerequisite architecture issues #2/#3 have not been marked approved.

## Local setup and checks

Python 3.10+ is required. Run commands from the repository root; JSON checking
needs no third-party libraries and no install step:

```sh
python -m polydash tests/fixtures/pairs/valid-minimal.json
python -m polydash tests/fixtures/golden/multiple.json --diagnostics-json diagnostics.json
```

Human diagnostics go to stderr; the option also writes a JSON artifact.
Exit status is 0 for success, 1 for invalid input, and 2 for usage/I/O errors or
an unavailable YAML library. Invalid input never exposes downstream IR.

Install the optional YAML dependency before running the full suite:

```sh
python -m pip install ".[yaml]"
python -m unittest discover -v
```

Tests cover 36 golden configurations, 29 malformed-input fixtures, seven
JSON/YAML pairs, source locations, schema extensibility and CLI behavior. No
external services are required by these tests. A GitHub Actions matrix runs the
suite on Windows/Linux/macOS with Python 3.10 and 3.12 (issue #12). See
[clean development setup](docs/dev-setup.md).

Regenerate goldens only for intentional diagnostic changes:

```sh
python -m tests.update_goldens
git diff -- tests/fixtures/golden
python -m unittest discover -v
```

Review every changed expected diagnostic before committing.

## Configuration example

```json
{
  "title": "Sales",
  "layout": {"direction": "column"},
  "components": [
    {"id": "revenue", "type": "metric", "value": 42, "unit": "USD"},
    {
      "id": "trend",
      "type": "chart",
      "data": {"source": "sales.csv"},
      "series": ["revenue"],
      "kind": "line",
      "stacked": false
    }
  ]
}
```

Supported component types: metric, chart, table, filter and nested group.
Data sources are opaque strings; they are not fetched or executed.
JSON and YAML both lower into the same IR, then pass through the same analyzer.
Source spans stay beside the IR so physical positions survive parsing.

## Contracts and tests

- [Shared IR and component schema](docs/ir.md)
- [JSON grammar, parse/semantic boundary and fixture inventory](docs/json-grammar.md)
- [Validation rules, diagnostics and golden regeneration](docs/validation-rules.md)
- [YAML subset and dependency approval status](docs/yaml-support.md)
- [Cross-format equivalence and adding paired fixtures](docs/equivalence-tests.md)

The v1 scope excludes expressions, variables, custom components, includes,
YAML aliases/anchors and multi-document streams. TOML and a Markdown DSL remain
possible future front ends. Accessibility and responsive-layout rules remain
research topics, not implemented features.

## Contributing

Use feature branches and pull requests; do not push directly to main. Describe
the behavior, linked issues and validation in each PR. Architecture contracts and
new dependencies require owner review before merge. Compiler changes need
positive/negative fixtures; cross-format changes need paired fixtures. The goal
is consistent behavior on Windows, Linux and macOS; the test matrix verifies
these platforms on each PR and push.

| Member | Focus |
| --- | --- |
| [Bhavye Kathuria](https://github.com/thebhavye) | Architecture and integration |
| Ayush Kumar Verma | Implementation and validation; GitHub account pending verification |
