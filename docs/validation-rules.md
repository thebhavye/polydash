# Validation and diagnostics contract v1

Analysis runs after parsing/shape checking and before IR can reach generation.
`analyze(Dashboard, component_schema=None) -> list[Diagnostic]` is the rule pass.
It receives the shared tree, its source map, and the schema registry. Rules add
findings through `report(rule_id, message, path, severity="error")`, which resolves source positions.
The pass never mutates the input and collects recoverable errors and warnings.

| ID | Severity | Category | Condition |
| --- | --- | --- | --- |
| PD0001 | error | parse | Invalid JSON/YAML syntax or duplicate key |
| PD0002 | error | parse | Wrong structural shape |
| PD0003 | error | parse | Unsupported format/YAML construct |
| PD1001 | error | component | Unknown component type |
| PD1002 | error | property | Unknown property |
| PD1003 | error | required | Missing required field |
| PD1004 | error | type | Wrong scalar/list/object type, dimensions, enum or object shape |
| PD1005 | error | identity | Every occurrence of a colliding component ID |
| PD2001 | warning | accessibility | Known filter has an omitted or blank title |
| PD2002 | warning | accessibility | Known chart has an omitted or blank title |

`analyzer.RULES` registers the semantic IDs in the above order; findings are
ordered by rule and then traversal/insertion order. The generic property walker
reads requirements from `schema.py`; new schema properties require no rule
changes. Unknown fields do not receive type checks. An outer type mismatch
stops traversal of that value, while other fields/components continue.
Duplicates are checked across the entire dashboard, including children.

Diagnostic fields are exactly `rule_id`, `severity`, `message`, `path`,
`location`. Severity values are error/warning/info (warnings preserve valid IR and exit status 0).
`path` is an RFC 6901 JSON pointer, root `""`. Missing fields use the absent
field's logical path and their parent's source span. Messages are concise,
stable text, without embedded file names or formatting.

For one-line input `{"layout":{"direction":"row"},"components":[]}` in
`broken.json`, the exact structured result is:

```json
[
  {
    "rule_id": "PD1003",
    "severity": "error",
    "message": "Missing required field 'title'",
    "path": "/title",
    "location": {
      "file": "broken.json",
      "line": 1,
      "column": 1,
      "excerpt": "{\"layout\":{\"direction\":\"row\"},\"components\":[]}"
    }
  }
]
```

The exact human output from the same object is:

```text
broken.json:1:1: error PD1003: Missing required field 'title'
{"layout":{"direction":"row"},"components":[]}
^
```

`Result.structured()` emits the list above; `Result.human()` renders each finding
as location/severity/ID/message, the source line, and a caret. The check adapter
prints human output to stderr and writes JSON when `--diagnostics-json FILE` is
supplied. Exit codes: 0 success, 1 rejected configuration, 2 I/O/usage/unavailable
YAML dependency. Invalid files expose no downstream IR. There is no generator.

## Golden tests

Run `python -m unittest discover -v` from the repository root. The golden runner
compares the complete structured output 1:1 with adjacent `.expected.json`
files, including messages, source excerpts, paths, and exact positions. There
are valid fixtures with zero diagnostics, separate cases for missing fields,
unknown types/properties, every current schema property type, duplicate IDs,
syntax/shape failures, and one realistic multi-error configuration.

After an intentional contract change run `python -m tests.update_goldens`, then
review `git diff -- tests/fixtures/golden` before committing. Regeneration is
explicit and never runs during tests. Golden changes need explanation in the
PR; do not regenerate to hide a regression. To add a case, add a `.json` file,
regenerate, inspect the diagnostics manually, and run the full suite.

## Title authoring warnings (#17, #18)

PD2001/PD2002 share the schema-aware walker, including nested children. Missing
or whitespace-only titles warn at the logical `/title` path; missing titles
anchor the containing component and blank titles anchor their value. Non-string
titles receive the existing PD1004 error only. Unknown kinds are not inspected.
Whitespace checking does not modify the stored title. All findings are collected.

These are authoring-context warnings, not WCAG conformance checks. A future
generator should render filter titles as visible, programmatically associated
input labels and chart titles as visible headings associated with their chart.
The concrete HTML mapping needs generator review; no generator exists yet.
Chart titles do not replace useful data summaries, tables or text alternatives.
