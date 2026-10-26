# PolyDash architecture baseline

Status: **Proposed**, pending teammate review for [Issue #1](https://github.com/thebhavye/polydash/issues/1). This is a target design, not an implementation or an approved API.

## Repository baseline

Reviewed 2026-10-26: main at `fce742a` contains only README.md. The checkout also contained an unfinished, untracked architecture draft; this document completes and corrects it. No compiler, runtime manifest, dependency lockfile, tests, CI, contribution guide or PR template exists. Config2UI code is not available here. No language decision is approved. The README defines intended scope.

Companion proposals:

- [Language/runtime](adr/0001-language-runtime.md)
- [Error handling](adr/0002-error-handling.md)
- [IR representation](adr/0003-ir-representation.md)
- [Shared IR/JSON contract](contracts/ir-json-shared-contract.md)
- [Backlog audit](backlog-audit.md)
- [Separate differentiation survey](research/dashboard-generator-survey.md)

## Relationship to the parallel implementation PR

[PR #15](https://github.com/thebhavye/polydash/pull/15) is an unmerged Python
validation implementation; it is not part of this branch's repository baseline.
Its existence does not accept or supersede this proposed design. Before both
are merged, review these differences explicitly:

| Baseline proposal | PR #15 implementation | Agreement needed |
| --- | --- | --- |
| TypeScript/Node candidate | Python 3.10+ package | Ratify or replace ADR 0001; do not maintain competing runtime plans. |
| UTF-16 offset ranges | Python code-point line/column plus excerpt | Choose provenance units and representation before exposing a stable contract. |
| Shared unvalidated tree then typed valid IR | Dictionary-backed Dashboard with source-map side table, checked before return | Decide whether this is the initial IR or requires a distinct semantic representation. |
| Wrong dashboard shapes are semantic | Loader reports shape failures as PD0002 | Settle the explicit #6 boundary amendment. |
| Separate proposed I/O/internal exit codes | CLI uses 2 for usage/I/O/missing YAML | Finalize #4 before claiming a shared CLI contract. |

No runtime migration or refactor is authorized by this documentation comparison.
Existing PR #15 tests demonstrate its current behavior, not conformance to every
proposal in this baseline. Its YAML extra and platform CI do not change this
branch's implementation status. Resolve these choices in review; do not silently
merge contradictory specifications.

## Pipeline and responsibilities

```text
UTF-8 configuration
 -> format frontend: lexer/parser -> LocatedConfig
 -> semantic analyzer: structure/schema checks, rules, normalization
 -> validated DashboardIR (only if no error diagnostics)
 -> generator -> HTML/CSS/JS artifacts
 -> driver writes artifacts
```

| Stage | Input | Output | Responsibility |
| --- | --- | --- | --- |
| Lexer/parser frontend | SourceFile: identity, original decoded text, format | StageResult<LocatedConfig> | Recognize format syntax, retain key/value locations, adapt to shared value tree; no dashboard-meaning checks. |
| Semantic analyzer | LocatedConfig, ComponentSchema | StageResult<DashboardIR> | Validate structure, required fields, kinds/properties/types and IDs; normalize valid input into IR. |
| Dashboard IR | Successful analysis | Typed dashboard nodes with provenance | Represent validated meaning without rereading source text. |
| Generator | DashboardIR, options | StageResult<GeneratedFile[]> | Deterministically render HTML/CSS and JS where needed; escape content for its output context. No filesystem writes. |
| Driver | Input path, options | Artifacts or diagnostics and process status | Read source, select frontend, sequence stages, gate generation, render diagnostics and write results. |

Missing fields and unknown kinds must be checked **before** valid IR exists. Rules inspect shared located values or an internal semantic context, never JSON/YAML parser classes. Later checks may use internal candidate IR, but candidate/partial structures are never exposed as validated DashboardIR. Exact registration and scheduling belong to #3. The analyzer owns lowering; neither frontend nor generator owns semantic normalization.

## Proposed stage interfaces

Pseudotypes describe boundaries; no code or API is implemented.

```text
SourceFile = { sourceId, displayPath, text, format }
SourceSpan = { sourceId, startOffset, endOffset }
Diagnostic = { code, severity, message, primarySpan?, relatedLocations[], hint? }
StageResult<T> = Success { value: T, diagnostics }
               | Failure { diagnostics } // no value
Frontend.parse(SourceFile) -> StageResult<LocatedConfig>
Analyzer.analyze(LocatedConfig, ComponentSchema) -> StageResult<DashboardIR>
Rule.check(AnalysisContext, ComponentSchema) -> Diagnostic[]
Generator.generate(DashboardIR, GenerationOptions) -> StageResult<GeneratedFile[]>
GeneratedFile = { relativePath, content }
```

Success cannot contain error diagnostics. Failure contains an error and no value. The driver stops after failure; warnings/info can accompany success. Unexpected exceptions are implementation failures handled at the driver boundary, not normal invalid-input reporting. #4 owns the final error/exit-code contract.

`LocatedConfig` is a shared **unvalidated** value tree: object, array, string, number, boolean and null. Object nodes retain ordered members with separate key/value spans, so duplicate keys are not lost in a host map. Arrays retain order. Nodes retain spans and logical paths for cross-format diagnostic matching. Number token/precision handling needs agreement in #2/#6 before choosing a host representation.

JSON initially implements the frontend. A future YAML adapter maps its syntax tree into the same LocatedConfig, preserving original YAML spans. #10 must define scalar typing, non-string keys, aliases, tags and multi-document behavior before implementation. YAML shares schema rules, analyzer and generator; it is not a second compiler.

## Component schema and Dashboard IR

The ComponentSchema is the single table of allowed kinds, required/optional properties, types, defaults and binding requirements. The analyzer reads it; frontends do not duplicate it. A new schema entry alone cannot make a component renderable: schema and generator must agree on supported kinds.

The README's Dashboard, Layout, Component and DataBinding are target concepts. Exact fields, initial component set, layout nesting, theme representation, ID comparison and binding behavior remain for #2/#6. README widget examples are candidates, not a commitment to ship every widget initially. No chart library, data connector or UI framework is selected here.

IR nodes retain origins and property origins remain addressable for later diagnostics. Defaults use an explicit enclosing-node origin rather than invented positions. Proposed representation: typed in-memory IR plus a stable test projection (ADR 0003). Only successful analysis supplies generator input.

## Source locations and diagnostics

Proposed spans use zero-based UTF-16 code-unit offsets into original decoded text and half-open `[startOffset, endOffset)` ranges. This fits the proposed TypeScript runtime; revisit if ADR 0001 changes. Preserve CRLF/LF and escape spelling before indexing. A source registry maps sourceId to text and line starts. Human output uses one-based lines/columns measured in UTF-16 code units. Caret rendering handles tabs/display width separately. An emoji occupies two code units; escaped characters retain spans covering their original source spelling.

Syntax errors point to the token or zero-width EOF span. Unknown properties point to keys, type errors to values, missing fields to containing objects. Duplicate IDs report every occurrence with related locations (#8). IR keeps provenance, with text in the source registry outside semantic identity.

Source-related diagnostics require primarySpan. I/O errors and internal failures may lack it; never fabricate a line for an unread file. One diagnostic model feeds human and structured output, including excerpts rendered from the registry. #3 owns stable code allocation, severity policy (including unknown properties) and exact goldens. Hints are advice, not automatic edits. Sort by source, offset and code with stable ties; do not collapse distinct findings just because they share a span.

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

All modules may depend on core. Frontends depend on core only. Analysis depends on core/schema/IR, never a format parser. Codegen depends on core/IR, never a frontend. Driver composes all stages; no stage imports the driver. Core has no downstream imports. This prevents frontend/analysis cycles and keeps rules reusable across formats.

## Generation, errors and tests

The generator returns relative names and text, such as index.html and CSS. Exact filenames and JS requirements await component agreement. It owns context-appropriate HTML/attribute/JS escaping and stable ordering, not network calls or directory creation. Driver checks artifact paths stay inside output. Generation completes before writes begin. #4 must define replacement/cleanup behavior; multi-file writes are not assumed atomic across platforms.

Proposed policy: stop after unsuccessful syntax parsing; collect independent semantic errors while skipping checks with invalid prerequisites. Never generate partial IR. Internal/I/O failures stop compilation distinctly. ADR 0002 supplies candidate statuses and scenarios, not approved CLI behavior.

No executable tests apply to this documentation-only baseline. Review should trace both valid and malformed input across every boundary. Once code exists:

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
| Runtime/toolchain | TypeScript + supported Node LTS; ADR 0001, not approved. |
| Parser strategy | Handwritten vs location-preserving library, #6. JSON.parse alone does not retain field spans. |
| JSON/IR vocabulary | Joint #2/#6 contract; initial kinds, property placement, layout, bindings, defaults and numbers remain open. |
| Syntax vs shape errors | Prefer malformed JSON as syntax, valid JSON with wrong dashboard shape as semantic. #6 originally classifies shape errors as parse-level; this is an explicit proposed amendment. |
| Collection / exit / output writes | ADR 0002, #4; recovery limits and publication policy still need agreement. |
| IR representation | ADR 0003, #2; no public serialized IR compatibility promise. |
| Diagnostic interface | #3; code allocation, severities and exact outputs remain open. |
| YAML subset/library | #10 after agreed JSON/IR and a working tested JSON pipeline. |

This baseline does not complete #2/#3/#4/#6/#14. #1 still requires teammate PR review. A proposal does not become accepted just because a draft exists.
