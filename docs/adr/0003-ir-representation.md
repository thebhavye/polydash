# ADR 0003: Validated IR and test serialization

Status: **Proposed**. Owners: #1 baseline, #2 final design. Date: 2026-10-26.

## Context and alternatives

JSON and future YAML need one generator. Untyped dictionaries make validity ambiguous. Public serialized IR would impose versioning obligations before node kinds are agreed. In-memory types alone make equivalence comparisons harder to inspect.

## Proposal

Adopt PR #15's initial in-memory `Dashboard` candidate: a JSON-compatible configuration plus a path-to-source-location side table. The loader constructs this candidate, the analyzer checks it, and the driver returns it as validated IR only when no errors remain. A generator must never accept the unvalidated candidate. More strongly typed nodes and property origins are future proposals requiring a reviewed migration.

PR #15 already compares the JSON-compatible configuration in equivalence tests, excluding only source locations; component/layout order and values remain significant. Keep provenance tests separate. #2 should review this representation and at least three worked examples before public IR serialization or stronger compatibility guarantees are claimed.

## Consequences

The existing JSON-compatible tree gives readable cross-format comparisons. Its Python type hints do not by themselves prove semantic validity; the analyzer gate is the contract. Public IR import/export, compatibility guarantees and IR CLI commands remain outside this baseline. #2 still owes review of the schema, origin representation and worked examples.
