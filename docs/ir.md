# Dashboard IR and schema v1

This is the initial contract needed by issues #6–#11. At implementation time the
repository contained only README.md; the architecture specs requested in #2/#3
had not landed. This document supplies a small proposed baseline for owner review,
not a claim that those architecture issues have been approved or closed.

The runtime is Python 3.10+. `Dashboard` is an in-memory dataclass with `config`
(a JSON-compatible tree) and `spans` (a map from tuple paths to `Span`). The same
representation is returned by both loaders. A span has file, 1-based line and
column, and the full source line as excerpt. Columns count Unicode code points,
not bytes; tabs count as one character. Every object, list, scalar, property
value and array item has an entry. Missing-field diagnostics use the containing
object's span. Field values, not field-name tokens, are the diagnostic anchor.
These are start spans only; end offsets are reserved for a future revision.

Node kinds in the tree:

- Dashboard: required `title`, `layout`, `components`; optional `theme`.
- Layout: required `direction`, one of `row` or `column`.
- Component: required `type` and `id`, plus the type's properties below.
- DataBinding: object with required string `source`. A source is an opaque
  reference, not an expression or an instruction to fetch a file or URL.
- Group: a component with its own layout and ordered child components.

Schema data lives in `polydash/schema.py` and is authoritative for required
fields, types, enums and object properties. No default values are inserted.
Unknown properties are errors at every schema-defined object level.

| Component | Required beyond id/type | Optional beyond title |
| --- | --- | --- |
| metric | value: number | unit: string |
| chart | data: DataBinding, series: string[] | kind: line/bar, stacked: boolean |
| table | data: DataBinding, columns: string[] | rows: number[][] |
| filter | options: string[] | multiple: boolean |
| group | layout: Layout, children: Component[] | none |

All components accept optional string `title`. Dashboard title is a string;
theme is `light` or `dark`. Numbers exclude booleans and non-finite floats.
Array dimensions are exact, but empty arrays are accepted and matrix rows need
not have equal lengths. There are no minimum lengths or nonempty-string rules.
IDs compare exactly, case-sensitively, without trimming or Unicode normalization:
`x`, `X` and `x ` are distinct. IDs are globally unique across nested groups.

Serialization for tests is `Dashboard.config` as JSON; spans are compared
separately in source-aware diagnostics. Sorted object keys are canonical; list
order and every scalar value are preserved. A parse-success tree can contain
semantic errors; `check` exposes IR only after analysis passes. No code generator
exists, and none is introduced or changed here.

## Conformance examples

These fixtures are used verbatim by both front ends and the equivalence runner.
No fields are renamed or dropped during lowering:

1. `tests/fixtures/pairs/valid-minimal.json`: input
   `{"title":"Overview","layout":{"direction":"column"},"components":[]}`
   lowers to exactly that `config`. The root span is `(file,1,1)` when written
   on one line; `title` starts at column 10. The checked-in pretty-printed
   fixture has its own corresponding multiline spans.
2. `tests/fixtures/pairs/valid-chart.json`: input has a chart `trend` with
   `data:{"source":"sales.csv"}`, `series:["revenue"]`, `kind:"line"`, and
   `stacked:false`. Expected config retains that Dashboard → Component →
   DataBinding nesting and the boolean `false`. The source path of the binding
   is `("components",0,"data")`; its source is tracked at that path plus `"source"`.
3. `tests/fixtures/pairs/valid-nested.json`: input has group `summary` with
   metric `sales` and chart `trend` as children, followed by table `details`
   and filter `region`. Expected config retains that order, both layouts and
   all binding/property values. The nested metric's ID is at
   `("components",0,"children",0,"id")`.

`valid-all-properties` extends these with every schema property and theme.
The paired YAML files must produce exactly the same configs. The identity
lowering is intentional: a second normalized copy adds no value in v1.

## Grammar alignment

`json-grammar.md` and `yaml-support.md` use this exact surface. Group nesting is
represented through `children`, rather than a second layout-owned component
list. Source format metadata is kept out of config; spans hold source-specific
information. These choices finalize the README's provisional layout/metadata
ideas for this increment and remain subject to architecture review.
