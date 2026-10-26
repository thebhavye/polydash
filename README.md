# PolyDash — Multi-Format Configuration-to-HTML Dashboard Compiler

PolyDash is a compiler project that accepts a configuration file describing a
dashboard and compiles it into a working web dashboard: generated **HTML**, **CSS**,
and **JavaScript** where required.

It extends the concept of our existing Compiler Design Lab project, originally
called **Config2UI**. The earlier Config2UI lab prototype is not present in this
repository — **PolyDash starts fresh in this repository**, reusing the original
idea and evolving it toward multiple configuration formats, stronger static
analysis, useful compiler diagnostics, and cross-platform execution.

> **Repository status: bootstrap / pre-implementation.** No compiler code exists
> yet. Everything below describes the *intended* project. Implemented vs. planned
> features are called out explicitly in
> [Current implementation status](#current-implementation-status-and-limitations).

---

## 1. Overview

PolyDash treats a dashboard definition the way a compiler treats a program:

```
Configuration Input → Lexer / Parser → Semantic Analyzer → Dashboard IR → Code Generator → HTML / CSS / JS
```

Instead of loading a JSON/YAML file at runtime and hoping it is correct, PolyDash
**compiles** it: parses the configuration, analyzes it statically, produces a
Dashboard Intermediate Representation (IR), and emits production dashboard code.

## 2. Problem statement

Manually building a dashboard requires writing frontend code — markup, styling,
layout rules, wiring data to charts and widgets — even when the dashboard itself
is a fairly regular, describable artifact. Configuration-driven generation can
simplify this: a person describes *what* the dashboard contains and *how* it is
arranged, and the compiler produces the frontend code.

The hard part is that hand-written configuration files are error-prone: missing
required fields, unknown component types, duplicate IDs, wrong value types, and
structurally inconsistent layouts. Without validation, these problems can surface in the browser, far from the
mistake's source. PolyDash's intended focus is a
**compiler-focused static-analysis engine** that
validates dashboard definitions and reports problems **before code generation**,
with diagnostics tied back to the source configuration. Declarative generation,
schema validation, and source-aware validation have existing precedents; this is
a design goal, not a demonstrated novelty claim. See the
[comparison survey](docs/research/dashboard-generator-survey.md).

## 3. Goals and intended users

**Goals**

- Compile dashboard configuration files into deployable HTML/CSS/JS output.
- Support multiple configuration front-ends (starting with JSON, then YAML) that
  produce a shared located configuration for analysis into the same Dashboard IR.
- Validate dashboard definitions statically and emit precise, source-aware
  diagnostics instead of vague runtime errors.
- Run identically on Windows, Linux, and macOS.

**Intended users**

- Students and educators in compiler-design coursework (the project's origin).
- Developers who want a dashboard without hand-writing frontend code.
- Teams that want to validate and version-control dashboard definitions as data.

## 4. Input formats

| Format | Status | Notes |
|---|---|---|
| **JSON** | *Planned — first target* | Initial configuration format for the first pipeline. |
| **YAML** | *Planned — next* | Reuses the same IR and code generator; depends on an agreed component schema and IR (see roadmap). |
| **TOML** | *Possible future extension* | Under consideration; not committed. |
| **Markdown-based DSL** | *Possible future extension* | A defined Markdown syntax is being considered as a lightweight authoring format; not committed. |

All front-ends produce a shared unvalidated `LocatedConfig`. The format-independent
analyzer validates it and constructs Dashboard IR only on success; code generation
consumes that validated IR.

## 5. Output

Generated, static dashboard artifacts:

- **HTML** — dashboard structure and layout.
- **CSS** — styling and arrangement.
- **JavaScript** — emitted only where required (for example, interactive
  components that need runtime behavior).

The [proposed architecture baseline](docs/architecture.md),
[decision records](docs/adr/0001-language-runtime.md), and
[shared JSON/IR contract](docs/contracts/ir-json-shared-contract.md) describe
stage boundaries and open decisions. They are documentation proposals, not
implemented features or team-approved specifications. The
[backlog audit](docs/backlog-audit.md) records dependency and scope gaps.

## 6. Compiler pipeline and the role of each stage

| Stage | Role | Status |
|---|---|---|
| **Lexer / Parser** | Reads the configuration format, verifies syntax, and records source locations for every construct. | *Planned* |
| **Semantic Analyzer** | Validates components, required fields, types, IDs, and properties against the component schema; produces diagnostics. | *Planned* |
| **Dashboard IR** | Format-independent, validated, normalized representation of the dashboard (structure, layout, components, data bindings). | *Planned — design in progress* |
| **Code Generator** | Lowers the IR into HTML, CSS, and (where required) JavaScript. | *Planned* |

Key design property: **analysis runs before generation**. Invalid configurations
never reach the code generator.

## 7. Planned Dashboard IR

The Dashboard IR is the pivot of the whole compiler. Each frontend returns
unvalidated `LocatedConfig` with source locations. The analyzer checks structure
and meaning, then constructs validated Dashboard IR only if no errors remain.
The generator consumes that IR without rereading source text. Missing-field and
unknown-type checks therefore run before valid IR exists.

Planned shape (to be finalized in the IR/component-schema design issue):

- **`Dashboard`** — root node: title, global layout, theme, metadata (source format and version).
- **`Layout`** — arrangement nodes (e.g., grid rows/columns or regions) that hold components.
- **`Component`** — a typed widget node (e.g., metric card, chart, table, filter) with declared properties and a unique ID.
- **`DataBinding`** — where a component's data comes from, normalized away from format-specific syntax.
- **Source spans** — every IR node keeps a reference to its originating location in the source configuration, so diagnostics survive lowering.

Open decisions to be settled before implementation: exact node kinds, property
typing, how data sources are represented, and whether the IR is serialized
(JSON IR files, for testability) or kept in memory. These are tracked as
compiler-core issues in the tracker.

## 8. Planned static-analysis capabilities

The static-analysis engine validates dashboard definitions before code
generation and reports problems with source context.

**Initial checks (planned)**

1. **Missing required fields** — e.g., a component with no ID, a chart with no data source or series definition.
2. **Invalid component types** — component kinds and properties not present in the component schema.
3. **Type mismatches** — property values whose type does not match the schema (e.g., a number where a list of column names is required).
4. **Duplicate component IDs** — IDs referenced or defined more than once, so cross-references and generated code stay unambiguous.
5. **Source-aware diagnostics** — every report carries the source file and location of the offending construct, not a generic error.

**Future checks (research, not committed)**

6. **Accessibility checks** — e.g., missing titles/labels, insufficient contrast, missing alternatives for visually rendered components.
7. **Responsive-layout checks** — e.g., layouts that cannot render at narrow widths, unbalanced grids.

The accessibility and responsive checks are an *investigation* first; whether
they ship depends on the outcome of the research issue.

## 9. Proposed CLI workflow *(not implemented)*

The following is a **proposed** command-line interface. **None of these commands
exist yet** — the CLI shape, tooling, and language runtime are still undetermined.

```
polydash compile dashboard.json --out dist/        # proposed, not implemented
polydash check dashboard.yaml                      # analyze only, no generation (proposed)
polydash dashboard.json -o dist/                   # flexible input parsing (proposed)
```

Behavior goals (proposed): error diagnostics cause a nonzero exit; warnings and
info alone allow success with exit 0. Validate-only mode performs no generation.
Successful compilation writes generated assets to an output directory. Exact
options and failure statuses remain proposed in ADR 0002 and Issue #4.

## 10. Cross-platform goal

PolyDash is intended to build, run, and produce identical output on **Windows**,
**Linux**, and **macOS**. This includes a reproducible development setup,
platform-independent path handling, and CI that runs on all three operating
systems. No platform decisions have been made yet; the tooling/runtime choice
will be part of the foundation work.

## 11. Development roadmap

| Phase | Milestone | Focus |
|---|---|---|
| **Phase 1** | Project Foundation | Architecture baseline and documentation, evidence-based differentiation research, repo conventions. |
| **Phase 2** | Compiler Core | Component schema + Dashboard IR definition, JSON configuration grammar, stage-integration and error-handling contract. |
| **Phase 3** | Static Analysis | Rule interface + diagnostic format, semantic validation (required fields, types, IDs), structured diagnostics with negative tests. |
| **Phase 4** | Multi-Format Support | YAML front-end on the shared IR, JSON/YAML equivalence tests. |
| **Phase 5** | Portability and Release | Cross-platform CI (Windows/Linux/macOS), reproducible setup, first packaged release. |

Trackers for accessibility and responsive-layout analysis live in the Static
Analysis phase as an investigative issue, not a committed deliverable.

## 12. Team

| Member | Role focus | GitHub |
|---|---|---|
| **Bhavye Kathuria** | Architecture and integration | [@thebhavye](https://github.com/thebhavye) |
| **Ayush Kumar Verma** | Implementation and validation | *(account pending verification — will be added once confirmed)* |

## 13. Contribution workflow and testing expectations

- Work happens on feature branches merged into `main` through pull requests —
  no direct pushes to `main`.
- Every PR describes what changed, which issue it closes, and how it was tested.
- **Testing expectations:** compiler stages must ship with tests — parser tests
  against representative configurations, semantic-analysis tests including
  *negative* cases (invalid configs that must be rejected), and IR/code-generator
  tests. Cross-format behavior requires equivalence tests (same-meaning
  JSON/YAML → equivalent IR) once multiple front-ends exist.
- CI runs the test suite on Windows, Linux, and macOS once the CI foundation
  issue lands.
- Labels organize the backlog (`architecture`, `compiler`, `parser`,
  `validation`, `code-generation`, `testing`, `documentation`,
  `cross-platform`, `enhancement`, `good first issue`), and milestones track
  the five roadmap phases above.

## 14. Current implementation status and limitations

**Status: bootstrap.** This repository currently contains only project
documentation and a GitHub issue backlog.

**Implemented:** none — no lexer/parser, semantic analyzer, IR, code generator,
CLI, input format support, or tests exist yet.

**In progress:**
- Architecture baseline and documentation (tracked issues).
- Evidence-based research into existing dashboard generators, to keep off our
  differentiation claims honest.

**Planned (not started):**
- JSON configuration parsing → Dashboard IR → HTML/CSS/JS code generation.
- Static analysis: missing-field, component-type, property-type, duplicate-ID,
  and source-aware diagnostics.
- YAML front-end; possible TOML and Markdown-syntax front-ends.
- Cross-platform CI and a first release.

**Known limitations of the vision:** the [research draft](docs/research/dashboard-generator-survey.md)
finds prior art for declarative generation, schema validation, and source-aware
pre-render validation. PolyDash has no demonstrated novelty or diagnostic-quality
advantage yet. Issue #14 still requires teammate review. The CLI shown above is
aspirational only.
