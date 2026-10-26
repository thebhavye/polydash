# YAML support v1

## Dependency status

The front end uses `PyYAML` (`yaml.SafeLoader`); version 6.0.3 was used for local
verification. **Owner approval remains pending**, as requested in this session
and required by issue #10. It is deliberately not added to `pyproject.toml`.
Before merging the YAML feature, the owner must approve this library and declare
`PyYAML>=6.0.3,<7` as a runtime dependency. This approval has not occurred.
JSON has no third-party runtime dependencies. The local full suite requires
PyYAML already available; a missing library yields a clear CLI error.

`.json`, `.yaml`, `.yml` (case-insensitive) select loader classes through the
`LOADERS` registry. Both return the same Dashboard/config + source map. Semantic
analysis and the downstream IR gate are format-blind. No generator is changed.

## Supported subset

One YAML document with string mapping keys, mappings, sequences, and JSON-like
scalars is accepted. Block/flow styles, comments, quoted strings and multiline
strings are supported by SafeLoader. Structural shape and component schema are
identical to JSON. Duplicate mapping keys are rejected as PD0001.

Implicit scalar typing follows **PyYAML SafeLoader's YAML 1.1 resolution**:
`yes/no/on/off` resolve to booleans, legacy octal and hexadecimal numbers resolve
to integers, and `null`/`~` resolve to null. Quote strings such as `"on"` or
`"2026-01-01"` when literal text is intended. Timestamps and other non-JSON scalar
types are rejected as PD0003. Non-finite floats are rejected; booleans never
satisfy numeric schema fields. JSON-compatible meanings must match for
cross-format equivalence; byte-identical scalar spelling is not sufficient.

Anchors, aliases, merge keys and explicit tags are **rejected**, including safe
explicit tags. Rejecting them avoids cyclic graphs, expansion, and ambiguous
source provenance. Complex/non-string keys are rejected. Multi-document streams
are rejected with PD0001 at the second document; no documents are silently
ignored. An empty document is PD0002 (expected dashboard object). Unsupported
constructs produce PD0003, malformed YAML PD0001, structural mismatches PD0002.
All carry file/line/column/excerpt. Syntax-level paths can be root when parsing
cannot determine a logical path. No custom constructors or unsafe loaders run.

## Fixtures

`tests/fixtures/pairs` contains YAML counterparts of all three IR conformance
examples and all-properties coverage, plus two semantically invalid pairs.
`tests/fixtures/parse/*.yaml` covers malformed flow syntax, indentation,
duplicate keys, multiple documents, anchors, aliases, tags, timestamps, sets,
complex/non-string keys, merge keys, non-finite numbers and empty documents.
The standard runner asserts rejection categories and source positions.
