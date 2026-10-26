# JSON/YAML equivalence tests

Two inputs are equivalent when their parsed Dashboard configs are deeply equal
as JSON-compatible trees and their diagnostic lists are equal after removing
physical `location` only. Dict key order is a no-op; component, child and data
array order are significant. No defaults, trimming or case folding are applied.
Source spans, source filename and source formatting are the only excluded
metadata. Logical RFC 6901 diagnostic paths must match, so errors must refer to
the same fields/occurrences even when line/column differ. Rule ID, severity,
message, diagnostic count and order are all compared.

The runner compares parser IR even for semantically invalid pairs, verifies
matching diagnostics, and checks matching acceptance/rejection. Valid pairs
must have zero error diagnostics. Authoring warnings are allowed but must match
in rule ID, severity, message, logical path and order across formats. The minimal
and metric fixtures still demonstrate completely empty diagnostic output. `unittest.assertEqual` uses unlimited readable
nested diffs (`maxDiff = None`) so a failure shows the actual divergent values.
Exact physical positions are independently covered by golden and parse tests.

Run `python -m unittest discover -v`. Paired fixtures in `tests/fixtures/pairs`:

| Pair | Meaning |
| --- | --- |
| valid-minimal | Empty dashboard |
| valid-metric | Numeric and string scalar properties |
| valid-chart | Binding, string list, enum, boolean |
| valid-nested | Multiple components with a nested group |
| valid-all-properties | Every current property type, including numeric matrix |
| invalid-multiple | Required, kind, property, type and duplicate diagnostics |
| invalid-duplicate-nested | Duplicate IDs across nesting boundaries |
| valid-reordered-properties | Object-key order and formatting are no-op distinctions |
| invalid-binding-and-series | Nested binding object shape and list type errors together |

To add a pair, create `<name>.json` and `<name>.yaml`, with prefix `valid-` or
`invalid-`, describing the same tree. Avoid YAML implicit-typing surprises and
unsupported anchors. The runner discovers pairs automatically; include both
files and run the full suite. For a new schema property extend all-properties.
Review canonical tree and diagnostic diffs in the PR. This is the initial
proposed equivalence contract; architecture-owner review remains a merge step.

The runner checks that JSON and YAML fixture stem sets match before comparing
any pairs. A YAML-only fixture is an error, not silently ignored. Its failure
message lists JSON-only and YAML-only names. It also enforces the minimum valid
and invalid pair counts. Reordered keys are exercised by an explicit valid pair;
array/component order and diagnostic order remain significant. Binding-object
and list-type errors are compared together in an additional invalid pair.
