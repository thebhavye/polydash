# JSON configuration grammar v1

See [IR and schema](ir.md) for the shared representation. JSON input is UTF-8,
strict JSON: quoted keys, standard JSON whitespace, one root value, no trailing
commas/comments, duplicate keys, NaN or Infinity. Floats overflowing to infinity
are also rejected. Escapes follow Python's standard JSON decoder.

Accepted shape (requiredness is checked by analysis):

```text
Dashboard = { title?: string, layout?: Layout, components?: Component[], theme?: string }
Layout = { direction?: string }
Component = { id?: string, type?: string, title?: string, ...schema properties... }
Group = Component with layout?: Layout and children?: Component[]
DataBinding = { source?: string }
```

`?` means the parser accepts omission so analysis can report missing fields; it
does not mean the field is semantically optional. `components` and any `children`
are arrays of component objects. Dashboard and component `layout` values must be
objects. The root must be an object. These structural requirements are checked
regardless of component type. Property nesting otherwise follows `schema.py`:
chart/table data is a DataBinding, string lists are one-dimensional, table rows
are two-dimensional numeric lists, and groups recurse through children.

## Parse versus semantic errors

| Example | Stage/category |
| --- | --- |
| `{"title":}` | parse PD0001: invalid syntax |
| repeated object key | parse PD0001: ambiguous JSON syntax |
| `[]` | parse PD0002: wrong root shape |
| `{"components":{}}` | parse PD0002: wrong structural shape |
| `{"components":[3]}` | parse PD0002: component must be an object |
| `{}` | semantic PD1003: missing title, layout, components |
| unknown component `type` | semantic PD1001 |
| unknown property | semantic PD1002 |
| metric value `"five"`, chart series `3`, data `[]` | semantic PD1004 |
| duplicate component IDs | semantic PD1005 |

Parse errors stop analysis for that file. Semantic analysis collects all
recoverable findings. Unknown kinds produce a kind error (and missing ID if
applicable), without guessing a schema for their other properties. A missing
kind uses the common id/type requirements; other fields are unknown until a
kind is supplied. A non-string kind produces a type error.

Every parse diagnostic has rule ID, severity, message, logical path when known,
and `location:{file,line,column,excerpt}`. Positions are 1-based. EOF points one
character past the last input character; an empty EOF line has an empty excerpt.
Semantic positions anchor values; missing fields anchor their parent objects.
See [diagnostics](validation-rules.md) for the exact output contract.

## Fixture inventory

Valid fixtures in `tests/fixtures/golden/` (accepted with no errors; chart/filter
fixtures may emit documented title authoring warnings):
`valid-minimal`, `valid-metric`, `valid-chart`, `valid-table`, `valid-filter`,
`valid-nested`, `valid-all-properties`, `valid-unique-case-space`.
These exercise empty dashboards, scalar properties, bindings, lists, matrices,
booleans, enums, group nesting and exact ID comparison.

Malformed fixtures in `tests/fixtures/parse/` (all `.json`):

| Fixture | Example | Expected category |
| --- | --- | --- |
| root-array | `[]` | PD0002 |
| layout-array | `{"layout":[]}` | PD0002 |
| components-object | `{"components":{}}` | PD0002 |
| component-scalar | `{"components":[3]}` | PD0002 |
| children-object | `{"components":[{"children":{}}]}` | PD0002 |
| layout-null | `{"layout":null}` | PD0002 |
| trailing-comma | `{"title":"x",}` | PD0001 |
| unquoted-key | `{title:"x"}` | PD0001 |
| duplicate-key | `{"title":"a","title":"b"}` | PD0001 |
| nonfinite / overflow | `NaN` / `1e999` property value | PD0001 |
| trailing-input | `{} {}` | PD0001 |
| empty / truncated / comment | empty / `{"title":` / `// comment` | PD0001 |

No expressions, variables, interpolation, references between components,
external includes, user-defined components, live data fetching, or additional
layout syntax are supported in v1. Strings containing expression-like text
remain literal strings. No YAML constructs apply to JSON.

## Excessive nesting

Parser/structural-validation recursion overflow is reported as PD0001 at the
source root, with no IR and CLI exit status 1 rather than a Python traceback.
The exact accepted depth depends on the interpreter; no fixed depth is promised.
