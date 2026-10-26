# ADR 0001: Language, runtime and tooling

Status: **Proposed**. Owner: #1. Date: 2026-10-26.

## Context and options

At the original README baseline no implementation or runtime decision existed. Since then [PR #15](https://github.com/thebhavye/polydash/pull/15) has produced a working Python 3.10+ validation package, a declared optional PyYAML extra, and six green Windows/Linux/macOS CI jobs on Python 3.10/3.12 ([run](https://github.com/thebhavye/polydash/actions/runs/40285073940)). This changes the choice from a greenfield comparison to adopting a tested implementation or funding a migration. The team still needs to review the architecture as a whole.

| Option | Compiler implementation | YAML | Testing | Packaging and cross-platform tradeoff |
| --- | --- | --- | --- | --- |
| TypeScript + Node | Discriminated unions suit AST/IR/result types; direct JS ecosystem | Location-preserving candidates such as yaml exist | Compile with tsc, built-in node:test/assert | npm CLI, Node required on each OS; TypeScript/compiler types add dev dependencies |
| Python | Dataclasses/type hints suit a small compiler | External parser needed; evaluate node marks | Built-in unittest; pytest optional | Interpreter/environment management; standalone packaging adds work; fewer enforced static invariants |
| Rust | Enums/Result encode stage invariants | External crate needed; evaluate maintenance/spans | Cargo test | Native binaries per OS/architecture; ownership/build complexity and unverified team experience |

All can implement this pipeline. No benchmark or team-experience evidence establishes a universal winner.

## Proposal

Adopt Python 3.10+ for the initial compiler, matching PR #15's tested foundation. Use standard-library `unittest`, the existing `pyproject.toml` package and the declared optional `PyYAML>=6.0.3,<7` extra for YAML. Keep JSON parsing/source tracking in the existing loader until an evidence-backed change warrants replacing it. Avoid a second runtime, bundler or test framework for the first pipeline. TypeScript/Node remains a viable alternative if the team explicitly funds and reviews a migration; it is not the default proposal while the Python implementation is under review.

This is an **adoption proposal**, not approval of PR #15's schema, IR or every loader behavior. The shared architecture should describe the staged validation behavior that works today and mark any richer source spans or typed nodes as future proposals requiring tests. A generator remains unimplemented.

## Consequences and acceptance gates

Adoption keeps the existing test/CI investment and avoids simultaneous Python and TypeScript implementations. Python type hints do not enforce runtime input shape; parser and analyzer tests stay necessary. Packaging still requires a Python environment and the YAML extra is optional. Confirm team/coursework support, review the declared dependencies and record the decision in #1/#2 before calling the architecture finalized. Cross-platform CI evidence covers the current validator, not a future generator.

Primary references checked 2026-10-26: [Node release policy](https://nodejs.org/en/about/previous-releases), [YAML library](https://eemeli.org/yaml/), [location-preserving JSON parser](https://github.com/microsoft/node-jsonc-parser), [Python JSON](https://docs.python.org/3/library/json.html), [Cargo guide](https://doc.rust-lang.org/cargo/guide/).
