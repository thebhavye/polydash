# ADR 0002: Stage failure and diagnostic collection

Status: **Proposed**. Owners: #1 baseline, #4 full contract, #3 diagnostics. Date: 2026-10-26.

## Context and alternatives

Failing on the first semantic error forces repeated edits. Unrestricted recovery risks misleading cascades. Generating partial input risks incorrect dashboards.

## Proposal

Stages return success with a value and no error diagnostics, or failure with diagnostics and no value. Syntax failure stops that input; additional syntax recovery is optional and bounded, never permission to analyze a partial parse. Semantic analysis collects independent errors and skips checks with invalid prerequisites. Only successful analysis exposes DashboardIR. Warnings permit generation. Check-only shares parsing/analysis and stops before generation.

Candidate exit codes: 0 success including warnings, 1 invalid input, 2 usage error, 3 I/O failure, 4 internal failure. No CLI exists. #4 owns final options, stdout/stderr routing and batch behavior. Normal input errors use diagnostics; unexpected exceptions are caught by the driver and reported as internal errors.

| Scenario | Proposed observable result | Generator / writer | Exit |
| --- | --- | --- | --- |
| Malformed JSON | Located syntax error, no analysis | Neither called | 1 |
| One semantic error | Located finding, no IR | Neither called | 1 |
| Multiple independent errors | Applicable findings in stable order, no IR | Neither called | 1 |
| Warning only | Warning plus valid IR | Both unless check-only | 0 |
| Analyzer unexpectedly throws | Internal diagnostic, span optional | Neither called | 4 |
| Input unreadable | Path-specific I/O error, no invented span | Neither called | 3 |
| Output write fails | I/O diagnostic, no success claim | Writes may have begun | 3 |

## Consequences and unresolved details

The result distinction gates generation and supports negative tests. #4 must finalize collection limits, cleanup, pre-existing output and write-failure behavior; multi-file publication is not assumed atomic. Nothing here is approved or implemented yet.
