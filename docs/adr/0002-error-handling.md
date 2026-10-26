# ADR 0002: Stage failure and diagnostic collection

Status: **Proposed for #4 review**, pending #1/#2 and #3/#6 alignment. Owners: #1 baseline, #4 full contract, #3 diagnostics. Date: 2026-10-26.

The [stage-by-stage contract](../pipeline-contract.md) gives the full handoff,
error matrix and driver test cases. This ADR records the policy choice and its
tradeoffs.

## Context and alternatives

Failing on the first semantic error forces repeated edits. Unrestricted recovery risks misleading cascades. Generating partial input risks incorrect dashboards.

## Proposal

Stages return success with a value and no error diagnostics, or failure with diagnostics and no value. Syntax failure stops that input; additional syntax recovery is optional and bounded, never permission to analyze a partial parse. Semantic analysis collects independent errors and skips checks with invalid prerequisites. Only successful analysis exposes DashboardIR. Warnings permit generation. Check-only shares parsing/analysis and stops before generation.

Candidate exit codes: 0 success including warnings, 1 invalid input, 2 usage error, 3 I/O failure, 4 internal failure. No compile CLI exists on this branch. The parallel Python check adapter in PR #15 uses 2 for usage, I/O and unavailable YAML; review must choose whether to preserve or migrate that contract. Normal input errors use diagnostics; unexpected exceptions are caught by the driver and reported as internal errors.

| Scenario | Proposed observable result | Generator / writer | Exit |
| --- | --- | --- | --- |
| Malformed JSON | Located syntax error, no analysis | Neither called | 1 |
| One semantic error | Located finding, no IR | Neither called | 1 |
| Multiple independent errors | Applicable findings in stable order, no IR | Neither called | 1 |
| Warning only | Warning plus valid IR | Both unless check-only | 0 |
| Analyzer unexpectedly throws | Internal diagnostic, location optional | Neither called | 4 |
| Generator returns failure | Compilation diagnostic, location optional | Writer not called | 4 |
| Input unreadable | Path-specific I/O error, no invented span | Neither called | 3 |
| Output write fails | I/O diagnostic, no success claim | Writes may have begun | 3 |

## Consequences and unresolved details

The result distinction gates generation and supports negative tests. The linked contract scopes collection to one input, requires prerequisite-aware semantic recovery and specifies best-effort cleanup after write failure. Multi-file publication is not assumed atomic. Diagnostic limits, exact overwrite behavior, stage ordering and the public output format still require agreement with #3/#4. Nothing here is approved or implemented yet.
