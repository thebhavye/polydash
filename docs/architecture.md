# PolyDash architecture baseline

Status: **Proposed**, pending team agreement for [Issue #1](https://github.com/thebhavye/polydash/issues/1). This is a target design, not an approved API. The validation adapter has merged; a small static HTML preview now exists, while the full generator contract remains unimplemented.

## Repository baseline

Historical starting point, reviewed 2026-10-26: main at `fce742a` contained only README.md. The architecture and Python validation adapter have since merged. A code generator does not yet exist. Config2UI code is not available here. The README defines intended scope.

Companion proposals:

- [Language/runtime](adr/0001-language-runtime.md)
- [Error handling](adr/0002-error-handling.md)
- [Stage integration contract](pipeline-contract.md)
- [IR representation](adr/0003-ir-representation.md)
- [Shared IR/JSON contract](contracts/ir-json-shared-contract.md)
- [Backlog audit](backlog-audit.md)
- [Separate differentiation survey](research/dashboard-generator-survey.md)

## Relationship to the merged validation adapter

[PR #15](https://github.com/thebhavye/polydash/pull/15) merged the Python
validation adapter. Its implemented behavior informs this proposed design;
the remaining public contracts still require review:

| Baseline proposal | PR #15 implementation | Agreement needed |
| --- | --- | --- |
| Python 3.10+ adoption proposed in revised ADR 0001 | Python 3.10+ package | Keep one runtime for v1; review schema/IR separately. |
| Code-point line/column plus excerpt for v1 | Python code-point line/column plus excerpt | End offsets/key ranges would be a later versioned improvement. |
| Shared configuration plus side-table locations, validated before downstream return | Dictionary-backed Dashboard with source-map side table, checked before return | Treat this as v1 IR candidate; typed nodes require a separate reviewed migration. |
| Structural shape failures in loader for v1 | Loader reports shape failures as PD0002 | Record as adopted v1 boundary; future reclassification requires coordinated spec/test change. |
| Current check CLI 0/1/2; future compiler statuses open | CLI uses 2 for usage/I/O/missing YAML | #4 should preserve this adapter or explicitly plan a versioned CLI change. |

ADR 0001 proposes adopting the now-merged Python implementation. #2/#3 review
still owns final IR and diagnostic contracts.

## Pipeline and responsibilities

```text
UTF-8 configuration
 -> format frontend: lexer/parser -> LocatedConfig
 -> semantic analyzer: schema checks, rules, validation gate
 -> validated DashboardIR (only if no error diagnostics)
 -> generator -> HTML/CSS/JS artifacts
 -> driver writes artifacts
```

| Stage | Input | Output | Responsibility |
| --- | --- | --- | --- |
| Lexer/parser frontend | SourceFile: identity, original decoded text, format | StageResult<LocatedConfig> | Recognize format syntax, retain value locations, reject malformed structural shapes, adapt to shared value tree; no component-schema checks. |
| Semantic analyzer | LocatedConfig, ComponentSchema | StageResult<DashboardIR> | Validate required fields, kinds/properties/types and IDs; gate the shared candidate as valid IR. |
| Dashboard IR | Successful analysis | Typed dashboard nodes with provenance | Represent validated meaning without rereading source text. |
| Generator | DashboardIR, options | StageResult<GeneratedFile[]> | Deterministically render HTML/CSS and JS where needed; escape content for its output context. No filesystem writes. |
| Driver | Input path, options | Artifacts or diagnostics and process status | Read source, select frontend, sequence stages, gate generation, render diagnostics and write results. |

Missing fields and unknown kinds must be checked **before** valid IR exists. Rules inspect shared located values or an internal semantic context, never JSON/YAML parser classes. Later checks may use internal candidate IR, but candidate/partial structures are never exposed as validated DashboardIR. Exact registration and scheduling belong to #3. For v1, the loader constructs a format-independent candidate and the analyzer certifies it; the generator sees only a validated candidate. Future normalization belongs to the analyzer.

The [detailed proposed handoff and failure matrix](pipeline-contract.md) extends
these boundaries for Issue #4; it does not finalize the unresolved runtime or IR.

## Proposed stage interfaces

Pseudotypes describe boundaries; no code or API is implemented.

```text
SourceFile = { sourceId, displayPath, text, format }
SourceLocation = { sourceId, line, column, excerpt }  // v1 start position
Diagnostic = { code, severity, message, primaryLocation?, relatedLocations[], hint? }  // target sketch
StageResult<T> = Success { value: T, diagnostics }
               | Failure { diagnostics } // no value
Frontend.parse(SourceFile) -> StageResult<LocatedConfig>
Analyzer.analyze(LocatedConfig, ComponentSchema) -> StageResult<DashboardIR>  // v1 returns checked candidate
Rule.check(AnalysisContext, ComponentSchema) -> Diagnostic[]
Generator.generate(DashboardIR, GenerationOptions) -> StageResult<GeneratedFile[]>
GeneratedFile = { relativePath, content }
```

Success cannot contain error diagnostics. Failure contains an error and no value. The driver stops after failure; warnings/info can accompany success. Unexpected exceptions are implementation failures handled at the driver boundary, not normal invalid-input reporting. #4 owns the final error/exit-code contract.

`LocatedConfig` is a shared **unvalidated** value tree: object, array, string, number, boolean and null. The v1 loader rejects duplicate keys before constructing the object map. Arrays retain order. A side table maps logical paths to start locations; Python columns count Unicode code points. Key-token spans and end offsets are possible later enhancements, not prerequisites for the working validator. Number precision remains a #2/#6 review item.

PR #15 implements JSON and a restricted YAML adapter, both producing the same configuration shape and path-to-location map. YAML scalar typing, keys, aliases, tags and multi-document behavior are documented there and remain subject to #10 review. Both frontends share analyzer rules. A small static HTML preview now consumes the validated IR; the proposed full generator contract is still open.

## Component schema and Dashboard IR

The ComponentSchema is the single table of allowed kinds, required/optional properties, types, defaults and binding requirements. The analyzer reads it; frontends do not duplicate it. A new schema entry alone cannot make a component renderable: schema and generator must agree on supported kinds.

The README's Dashboard, Layout, Component and DataBinding are target concepts. PR #15 supplies an initial set and examples for #2/#6 review; final fields, layout nesting, theme representation, ID comparison and binding behavior remain subject to that review. README widget examples are candidates, not a commitment to ship every widget initially. No chart library, data connector or UI framework is selected here.

IR nodes retain origins and property origins remain addressable for later diagnostics. Defaults use an explicit enclosing-node origin rather than invented positions. Proposed v1 representation: an in-memory Dashboard carrying a JSON-compatible configuration and a separate path-to-location map, released downstream only after successful analysis (ADR 0003). Only successful analysis supplies generator input.

## Source locations and diagnostics

The v1 location contract uses source file, one-based line/column and excerpt;
columns count Python Unicode code points and tabs count as one column. Loader
locations point to the start of values; missing-field errors use the containing
object. Original text is retained for excerpts, including CRLF/LF spelling.
Optional offset ranges and key-token positions are future proposals requiring
cross-format fixtures; they are not claimed by PR #15.

Syntax errors point to the offending start position or EOF position. Unknown properties and type errors currently point to value starts; missing fields point to containing objects. Duplicate IDs report every occurrence (#8). A future key-span and related-location enhancement requires parser changes and test coverage.

Source-related diagnostics require a location. I/O errors and internal failures may lack one; never fabricate a line for an unread file. One model feeds human and structured output. PR #15 currently orders semantic findings by registered rule then traversal order, with golden tests locking that behavior. #3 owns the final diagnostic format, severities, source mapping and any ordering change. Do not collapse distinct findings sharing a location.

## Proposed source tree and dependency direction

These are future paths, not existing modules. Extensions depend on runtime agreement.

```text
src/
  core/        source registry, spans, diagnostics, stage results, located values
  frontend/
    json/      lexer/parser and adapter to located values
    yaml/      future adapter after shared contract agreement
  schema/      component definitions
  analysis/    rules, semantic context, validation and IR construction
  ir/          validated dashboard types and test projection
  codegen/     artifact construction from IR
  driver/      CLI, I/O, orchestration, diagnostic rendering
tests/
  fixtures/    valid/invalid inputs, paired formats when YAML exists
  golden/      expected diagnostics, IR and generated artifacts
```

All modules may depend on core. Frontends depend on core only. Analysis depends on core/schema/IR, never a format parser. Future codegen depends on core/IR, never a frontend. Driver composes all stages; no stage imports the driver. Core has no downstream imports. This prevents frontend/analysis cycles and keeps rules reusable across formats.

## Generation, errors and tests

The generator returns relative names and text, such as index.html and CSS. Exact filenames and JS requirements await component agreement. It owns context-appropriate HTML/attribute/JS escaping and stable ordering, not network calls or directory creation. Driver checks artifact paths stay inside output. Generation completes before writes begin. #4 must define replacement/cleanup behavior; multi-file writes are not assumed atomic across platforms.

Proposed policy: stop after unsuccessful syntax parsing; collect independent semantic errors while skipping checks with invalid prerequisites. Never generate partial IR. Internal/I/O failures stop compilation distinctly. ADR 0002 supplies candidate statuses and scenarios, not approved CLI behavior.

No executable tests apply to this documentation-only baseline. PR #15 separately tests its Python validator on three operating systems. Review should trace both valid and malformed input across every boundary. Once code exists:

- Parser fixtures: valid/malformed JSON, duplicate keys, EOF, escapes, CRLF/LF, tabs and non-BMP characters with exact spans.
- Analyzer fixtures: positive and negative examples for each rule, multiple independent findings and every duplicate-ID occurrence.
- Driver tests: failure never calls generator/writer, warnings permit success, check-only writes nothing, internal/I/O errors are distinct.
- IR/generator goldens: deterministic structure/output and correct escaping; reviewed golden updates.
- Future YAML pairs: compare semantic IR excluding documented provenance/format metadata only; invalid pairs compare rule IDs/logical paths and independently verify each format's source positions.
- #12 runs tests on Windows/Linux/macOS. Browser behavior checks follow actual interactive output.

## Cross-platform design

Use standard path/filesystem APIs, explicit UTF-8 and LF output. Preserve source endings for locations. Avoid shell-specific scripts, symlink requirements, case-insensitive filename assumptions and developer paths. Use portable relative artifact URLs and stable ordering; omit timestamps/machine paths from generated output. Human output works without ANSI; structured output contains no terminal escapes. Pin runtime/tool versions only after agreement and verify packaging and behavior on all three OSes before claiming portability.

## Decisions requiring agreement

| Decision | Proposal / owner |
| --- | --- |
| Runtime/toolchain | Adopt Python 3.10+ from tested PR #15; ADR 0001, pending review. |
| Parser strategy | PR #15 has a source-aware JSON loader; #6 review owns grammar and any future replacement. |
| JSON/IR vocabulary | Joint #2/#6 contract; initial kinds, property placement, layout, bindings, defaults and numbers remain open. |
| Syntax vs shape errors | Adopt PR #15 loader-level structural shape errors for v1, subject to #6 review. |
| Collection / exit / output writes | ADR 0002, #4; recovery limits and publication policy still need agreement. |
| IR representation | ADR 0003, #2; no public serialized IR compatibility promise. |
| Diagnostic interface | #3; code allocation, severities and exact outputs remain open. |
| YAML subset/library | PR #15 implements a restricted YAML frontend with optional PyYAML; #10 review owns the final subset. |

This baseline does not complete #2/#3/#4/#6/#14. #1 still requires teammate PR review. A proposal does not become accepted just because a draft exists.
