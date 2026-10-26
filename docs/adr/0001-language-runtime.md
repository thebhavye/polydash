# ADR 0001: Language, runtime and tooling

Status: **Proposed**. Owner: #1. Date: 2026-10-26.

## Context and options

No implementation, manifest or runtime decision exists. The compiler needs future YAML with provenance, fixture tests, packaging and Windows/Linux/macOS support. Team familiarity is unverified and must be discussed.

| Option | Compiler implementation | YAML | Testing | Packaging and cross-platform tradeoff |
| --- | --- | --- | --- | --- |
| TypeScript + Node | Discriminated unions suit AST/IR/result types; direct JS ecosystem | Location-preserving candidates such as yaml exist | Compile with tsc, built-in node:test/assert | npm CLI, Node required on each OS; TypeScript/compiler types add dev dependencies |
| Python | Dataclasses/type hints suit a small compiler | External parser needed; evaluate node marks | Built-in unittest; pytest optional | Interpreter/environment management; standalone packaging adds work; fewer enforced static invariants |
| Rust | Enums/Result encode stage invariants | External crate needed; evaluate maintenance/spans | Cargo test | Native binaries per OS/architecture; ownership/build complexity and unverified team experience |

All can implement this pipeline. No benchmark or team-experience evidence establishes a universal winner.

## Proposal

Prefer TypeScript with a supported Node.js LTS release for explicit stage types and straightforward JS artifact generation. Compile with tsc; test emitted JS with node:test and assertions. Use standard path/filesystem APIs. Pin exact versions in the setup PR after review. Do not add a bundler, UI/test framework or parser dependency now. Initial packaging proposal is an npm CLI, not standalone binaries.

Choose handwritten JSON parsing versus library reuse in #6. Compiler-lab origins do not establish a handwritten-parser requirement. JSON.parse alone loses spans, but location-preserving libraries exist. The yaml library is evidence of feasibility, not a selection; #10 owns library approval.

## Consequences and acceptance gates

Typed boundaries help enforce the design; runtime validation is still needed. Users need Node, and cross-platform claims need CI evidence. Confirm both teammates can maintain this stack, coursework constraints, minimum runtime, numeric semantics and packaging preference before accepting.

Primary references checked 2026-10-26: [Node release policy](https://nodejs.org/en/about/previous-releases), [YAML library](https://eemeli.org/yaml/), [location-preserving JSON parser](https://github.com/microsoft/node-jsonc-parser), [Python JSON](https://docs.python.org/3/library/json.html), [Cargo guide](https://doc.rust-lang.org/cargo/guide/).
