# ADR 0003: Validated IR and test serialization

Status: **Proposed**. Owners: #1 baseline, #2 final design. Date: 2026-10-26.

## Context and alternatives

JSON and future YAML need one generator. Untyped dictionaries make validity ambiguous. Public serialized IR would impose versioning obligations before node kinds are agreed. In-memory types alone make equivalence comparisons harder to inspect.

## Proposal

Use typed in-memory DashboardIR constructed only after successful analysis. Preserve node/property origins directly or through an IR-owned provenance table. Internal candidate structures are not valid generator inputs.

After #2 defines nodes, provide a deterministic JSON-compatible test projection. Semantic equivalence excludes paths, offsets and format labels, but preserves meaningful order, values and layout. Verify provenance separately. Serialization and numeric behavior require agreement before freezing fixtures.

## Consequences

Generator stays format-independent and golden diffs remain reviewable, at a small projection-maintenance cost. Public IR import/export, compatibility guarantees and IR CLI commands are outside this baseline. #2 still owes the complete schema, origin representation and at least three worked input-to-IR examples.
