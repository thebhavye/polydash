# Dashboard generator and validation survey

Status: **Research draft**, separate from the architecture decision. Supports [Issue #14](https://github.com/thebhavye/polydash/issues/14); teammate review pending. Sources inspected 2026-10-26. This is a documentation survey, not execution/benchmark testing or an exhaustive novelty search. PolyDash has no implemented capabilities yet.

## Comparison matrix

“Not established” means the inspected sources do not prove the capability or its absence. A JSON Pointer/property path is not a source-file line/column. App builds and chart-spec compilation are distinguished from standalone dashboard HTML generation. OSS links identify the public project; licenses should be checked before reuse.

| System / primary basis | Declarative input | Validation evidence | Source-aware diagnostics | Compile vs interpret | Output/frontend | Open source |
| --- | --- | --- | --- | --- | --- | --- |
| [Dashy configuration](https://dashy.to/docs/configuring/) | YAML; UI JSON editor | Schema checker, validate-config command | File line/column contract not established | Configured app with build step and runtime settings | Web dashboard, widgets | [Yes](https://github.com/Lissy93/dashy) |
| [Evidence](https://docs.evidence.dev/) | SQL + Markdown/components | Full schema/diagnostic contract not established from overview | Not established | Builds static site; hosted product also exists | Static web data apps | [Core yes](https://github.com/evidence-dev/evidence) |
| [Visivo](https://www.visivo.io/) | YAML project definitions | JSON-schema type checking advertised | Exact file/span contract not established | Local recompilation plus query precomputation and browser interactions | Plotly charts, browser viewer, DuckDB-WASM | [Yes](https://github.com/visivo-io/visivo) |
| [Vega-Lite](https://vega.github.io/vega-lite/) | JSON chart grammar | JSON Schema published; compiler logger | Compiler logger documents messages, not source-text spans | Compiles Vega-Lite to Vega; render/export utilities | Vega specification; SVG/PNG/PDF export options | [Yes](https://github.com/vega/vega-lite) |
| [JSON Forms](https://jsonforms.io/) | JSON Schema, UI schema, data | Built-in input validation | Data validation demonstrated; config-file spans not established | Runtime declarative form rendering | React, Angular, Vue | [Yes](https://github.com/eclipsesource/jsonforms) |
| [react-jsonschema-form](https://rjsf-team.github.io/react-jsonschema-form/docs/) | JSON Schema and UI schema | Validator integration, e.g. Ajv | Raw source-text spans not established | React component renders schema at runtime | HTML forms through React | Yes, Apache 2 per documentation |
| [MkDocs](https://www.mkdocs.org/user-guide/configuration/) | YAML site config + Markdown | Required/typed config settings documented | Config-file span guarantee not established by inspected guide | Static site build | HTML/CSS/theme assets | [Yes](https://github.com/mkdocs/mkdocs) |
| [Quarto dashboards](https://quarto.org/docs/dashboards/) | Markdown/YAML metadata or notebooks | YAML metadata validation evidenced in maintainer example | Line/column range and corrective hint in maintainer example | Render to static dashboard, optional Shiny backend | HTML dashboards with chart/widget libraries | [Yes](https://github.com/quarto-dev/quarto-cli) |
| [Ajv](https://ajv.js.org/api.html) (validation tooling) | JSON Schema / JTD, data | Compiles schemas into validators | instancePath/schemaPath and keyword details, not raw file spans | Compiles validation functions, not dashboards | JS validator functions / structured errors | Open-source project; not a dashboard product |

## Findings per system and lessons

**Dashy.** YAML authoring, built-in editor validation and a schema-validation command already make “configuration plus validation” common in dashboard software. Some settings apply at runtime while documentation also describes rebuilding the app. PolyDash should offer precise, testable diagnostics rather than imply all alternatives merely hope configuration works. No negative claim about Dashy's location support follows from this page.

**Evidence.** Its open-source core authors data apps with SQL and Markdown and builds deployable static sites. This is direct prior art for dashboards as text and static publishing, although its input model differs from PolyDash's initial JSON. The overview does not establish its complete validation behavior. Lesson: distinguish authoring model from delivery artifact rather than equating different inputs with novelty.

**Visivo.** Its website describes YAML projects type-checked against JSON Schema; the repository describes a source/model/metric/insight/chart/dashboard chain, local recompilation and precomputed data used by browser interactions. This is substantial BI-as-code prior art. Its richer data infrastructure is not a feature list to copy into PolyDash. Lesson: schema validation and semantic modeling are already practiced; compare actual rule coverage and error attribution later.

**Vega-Lite.** A JSON visualization grammar compiles into Vega, so declarative input, compiler stages and intermediate specifications are not new. Its [compiler documentation](https://vega.github.io/vega-lite/usage/compile.html) provides a configurable logger and export utilities. It is not identical to a full dashboard-to-HTML compiler, and the inspected logger interface does not establish original source spans. Lesson: maintain a clean representation boundary and avoid claiming compiler architecture itself as novel.

**JSON Forms.** Schema and UI schema drive layouts, data binding, rules and validation across three frontend frameworks. It is adjacent UI generation, not standalone dashboard compilation. Lesson: separate schema semantics from renderers; evaluate reuse of established validation conventions before inventing them. The overview's runtime validation does not prove source-file attribution.

**react-jsonschema-form.** It generates React forms from JSON Schema and accepts a validator implementation and UI customization. It demonstrates that declarative UI generation and schema checks are established capabilities. Lesson: a schema table alone is not a differentiator; PolyDash must demonstrate compiler-specific behavior with representative invalid documents.

**MkDocs.** YAML configuration and Markdown become static HTML, with typed and required configuration fields documented. It is an adjacent static-site authoring pattern, not a dashboard system. Lesson: predictable builds, clear configuration errors and version-controlled authored files are baseline expectations. The configuration guide is insufficient to classify all source-location behavior.

**Quarto.** Markdown/notebooks can produce static dashboards with cards, layouts and interactive components. More importantly, a [maintainer discussion](https://github.com/orgs/quarto-dev/discussions/2433) shows metadata validation reporting the original line/column range and suggesting corrected YAML. That example directly defeats a broad claim that source-aware pre-render validation is unique. It is a historical maintainer example, not proof that every current error path has equally good locations. Lesson: test attribution through source transformations, not just raw parser offsets.

**Ajv.** Its API exposes keyword, instancePath, schemaPath, parameters and optional messages; schemas compile into reusable validator functions. These structured error conventions are useful prior art. Data paths need a parser source map before becoming file spans. Lesson: evaluate schema-validator reuse versus handwritten rules in #3; this survey does not install or select Ajv.

## Evidence-backed verdict

Schema validation, declarative rendering, dashboard/static-site builds and visualization compilation all have direct prior art above. Quarto supplies a concrete source-aware pre-render error example. Consequently **neither pre-generation validation nor source-aware diagnostics alone is a defensible novelty claim** from this surveyed set.

PolyDash's proposed focus is a small compiler-design-oriented dashboard language, beginning with JSON and then YAML, whose frontends share validated Dashboard IR and whose documented semantic rules gate HTML/CSS/JS generation. That combination is a useful engineering and teaching goal; this survey does not establish that it is unique. The educational orientation comes from PolyDash's README, not a market comparison.

A stronger differentiation argument would require implemented evidence: equal semantic IR for paired formats; accurate spans after normalization; missing-field, unknown-kind/property, type and duplicate-ID checks; deterministic structured errors; and proof that invalid input never reaches generation. Compare equivalent invalid examples against direct competitors and document their versions before asserting diagnostic-quality advantages. Absence from an overview page is not absence from a product.

## Research limits and follow-up

No surveyed package was installed or executed. Unsupported claims are marked unknown rather than “no”. Source pages can change; this is a dated review, not a compatibility promise. Two guessed Quarto documentation paths returned 404 and are not cited as evidence; the successful maintainer discussion provides the diagnostic example. The DEV Community Wisdom lookup required an unconnected account, so no community consensus is claimed. #14 remains open for peer review; architecture and implementation do not depend on a novelty finding.
