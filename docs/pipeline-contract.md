# Pipeline integration and failure contract

Status: **Proposed long-term contract for Issue #4 review**. Based on the merged [architecture baseline](architecture.md) and [ADR 0002](adr/0002-error-handling.md). The current CLI can produce one static HTML preview through `--output`; it does not implement this proposed multi-artifact driver/writer contract. The merged Python check adapter from [PR #15](https://github.com/thebhavye/polydash/pull/15) has a different current status contract, listed below. Team review must choose the final behavior before implementation claims conformance.

## One-input data flow

The driver owns the `SourceRegistry`, file reads, format selection, sequencing, diagnostic rendering and output writes. Stages receive already-decoded data and return values without writing files. `SourceFile` carries `{sourceId, displayPath, text, format}`. Its identity and original UTF-8 decoded text remain available for excerpts. Format detection is by supported extension, with an explicit unsupported-format error; extension policy and CLI names still need #6/#10 review.

The proposal uses this sum type at each stage:

```text
StageResult<T> = Success { value: T, diagnostics: NonErrorDiagnostic[] }
               | Failure { diagnostics: NonEmptyDiagnostic[] }  // at least one error
NonErrorDiagnostic = Diagnostic(severity = warning | info)
```

Neither stage result uses `null` to ambiguously mean success. A failure has no usable downstream value. An unexpected exception is outside this type and is caught by the driver. `Diagnostic` has stable code, severity, message, optional primary location for non-source failures, optional related locations and optional hint; exact public fields/codes are owned by #3. Source-backed errors must have a primary location. The source registry derives one-based human locations and excerpts from the original text. The [v1 source-location convention](architecture.md#source-locations-and-diagnostics) uses Python Unicode code-point columns and excerpts.

| Boundary | Exact proposed payload | Caller responsibility | Callee responsibility |
| --- | --- | --- | --- |
| Driver → frontend | `SourceFile` with supported `format` | Read/decode once; register text and stable identity; do not call frontend after read/format failure | Tokenize/parse source syntax, reject structural shape errors and retain value locations. |
| Frontend → analyzer | `Success<LocatedConfig>` plus non-error parse findings | Reject frontend failure; preserve source registry and diagnostics | Validate schema and cross-node meaning; certify only valid input as downstream IR. |
| Analyzer → generator | `Success<DashboardIR>` plus accumulated non-error findings | Reject analysis failure or any error severity; validate-only mode ends here | Read format-independent validated nodes and provenance; create artifacts deterministically. |
| Generator → driver writer | `Success<GeneratedFile[]>`, each `{relativePath, content}` | Reject generation failure; check paths, stage writes and publish output | No filesystem operations and no source-text inspection. |
| All stages → diagnostic renderer | Stage diagnostics + source registry | Combine in deterministic order and render human or structured form | Rendering never changes severity, code, path or spans. |

`LocatedConfig` is a shared candidate with object/array values, logical paths and a path-to-start-location side table. It permits missing required fields so the analyzer can report them. The v1 frontend rejects wrong structural shapes and duplicate JSON keys before returning a candidate. The analyzer gates the candidate as validated `DashboardIR`; an unvalidated candidate never crosses the analyzer → generator boundary. The exact component schema, DataBinding and IR serialization are #2/#6 decisions. The generator output names/content remain code-generation work, not a commitment made here.

## Sequencing and recovery policy

1. Parse command options, read the input, decode UTF-8 and select a frontend. Usage errors or unsupported options stop before reading. Input read/decode failures stop before parsing.
2. The frontend parses one input. On syntax failure, emit the parse diagnostic(s) and stop this input. No partial `LocatedConfig` is passed onward. A parser may recover enough to report more than one syntax error, but must not analyze or generate after failure. Exact recovery bounds are a parser decision.
3. The analyzer collects independent recoverable semantic errors in one pass. A failed prerequisite suppresses dependent checks on that subtree; independent siblings continue. For example, a component with an unknown `type` gets one unknown-type finding rather than invented type-specific property findings, while later valid components remain checked. The frontend rejects non-object component shapes before this stage. If any error is found, return failure with all applicable findings, not a partial IR. Warnings/info alone return successful IR.
4. Validate-only mode renders findings and stops before generation/writes. Compile mode invokes the generator only on successful IR. A generator `Failure` from a valid IR is a compilation failure with proposed exit 4 and no writer call. Unexpected stage exceptions are internal failures handled at the driver boundary, also exit 4, with a concise message rather than a user-input rule code.
5. The driver validates each generated relative path stays inside the requested output directory and is unique before writing. It stages artifacts in that directory and publishes only after generation succeeds. Cross-file publication cannot be assumed atomic: if an output write/rename fails, report failure, clean temporary files best effort and tell the user that partial new output may exist. Do not announce successful compilation. Exact overwrite/backup policy needs CLI review; the writer must not silently present a partial build as success.

The scope of collection is one input file. Multi-input aggregation, diagnostic caps, watch mode and streaming generation are out of scope for this contract. Diagnostic ordering is stable by stage, then each stage's documented order. #3 must settle how analysis rules register and order their findings; sorting by source alone would conflict with the currently proposed Python rule ordering. Do not deduplicate different findings that happen to share a span.

## Proposed status and output matrix

These exit statuses apply to a future compile/check CLI, **not** the existing Python check adapter. The current adapter returns 2 for usage, I/O and missing YAML, and has no generator. Ratification requires an explicit migration decision or an amendment here.

| Input / failure class | Continue? | Human output | Structured output, if requested | Proposed exit |
| --- | --- | --- | --- | --- |
| Valid input, no findings | Analyze and compile unless check-only | None | Empty diagnostics | 0 |
| Valid input, warning/info only | Compile unless check-only | All findings on stderr | Same findings, severity retained | 0 |
| Malformed JSON/YAML | Stop after frontend | Located syntax error(s) on stderr | Same diagnostics, no IR/artifacts | 1 |
| Well-formed input with one semantic error | Stop after analyzer | Located finding on stderr | Same finding, no IR/artifacts | 1 |
| Multiple independent semantic errors | Collect within analyzer, then stop | Every applicable finding in stable order | Matching list, no IR/artifacts | 1 |
| Unsupported command option / missing path | Stop before read | Usage message on stderr | No source diagnostic required | 2 |
| Generator returns `Failure` for valid IR | Stop before writer | Generation failure message, no partial artifact claim | Error record if available; no generated files | 4 |
| Input read/decode or output publication failure | Stop at failing operation | I/O message with path/operation, no fabricated source span | Error record if structured output is available | 3 |
| Unexpected parser/analyzer/generator exception | Stop immediately | Internal failure message; stack trace only in explicit debug mode | Internal error record if possible | 4 |

A structured diagnostics output write can itself fail. Report that I/O error on stderr and exit 3, even when validation found no errors or found user errors; never claim the JSON artifact was produced. Exact JSON serialization and human excerpt format remain #3's authority. Existing diagnostics collected before an output failure can still be displayed, followed by the I/O error. An internal failure should not disclose a raw traceback by default; debug behavior is a CLI design decision.

## Table-driven driver examples for future tests

| Fixture / injected failure | Expected stage calls | Findings and output | Status |
| --- | --- | --- | --- |
| `{"title":}` | frontend only | Syntax finding with source location; no IR/artifacts | 1 |
| Valid JSON syntax with component missing `id` | frontend, analyzer | One required-field finding at containing component; no generator/writer | 1 |
| Two independent missing IDs in components | frontend, analyzer | Two findings at their respective components; no generator/writer | 1 |
| Config with only a warning | frontend, analyzer, generator, writer in compile mode | Warning preserved; successful artifacts | 0 |
| Same warning in check-only mode | frontend, analyzer | Warning preserved; writer never called | 0 |
| Analyzer throws unexpectedly | frontend, analyzer | Internal failure; no generator/writer; no default traceback | 4 |
| Generator returns `Failure` for valid IR | frontend, analyzer, generator | Compilation failure; writer never called | 4 |
| Input path cannot be read | driver only | I/O message with path, no invented line/column | 3 |
| Generated artifact publication fails | frontend, analyzer, generator, writer | I/O failure, no success claim, possible partial output disclosed | 3 |

These are **contract tests to write when a driver exists**. Exact `id` requiredness and message/code are contingent on #2/#3. The examples intentionally assert stage gates and status rather than freeze unapproved component grammar.

## Open review decisions and relationship to PR #15

- **Runtime and source positions:** The merged baseline proposes adopting Python 3.10+ and the current loader's code-point line/column plus excerpts. Agree on the public location and provenance contract before treating these pseudotypes as stable APIs.
- **Shape error ownership:** the v1 adoption proposal follows PR #15: valid JSON with wrong structural shapes is rejected by the loader as PD0002. #2/#6/#3 review must confirm the boundary before treating it as final.
- **Exit codes:** PR #15's existing check adapter uses 0/1/2; this document proposes separate 3/4 for I/O/internal failures. Choose one policy before a compile CLI is implemented. There is no reason to break a working check adapter merely to match an unapproved proposal.
- **Ordering and recovery:** PR #15 orders semantic findings by rule registration and reports structural shape errors before analysis. The v1 proposal retains that ordering; #3 review must decide whether to freeze it as public behavior.
- **Output publication:** artifact paths, overwrite policy and staging are future generator/driver work. No output writer exists now; the above publication behavior is a testable proposal rather than an implemented feature.

Approval in #4 requires #1 and #2 review, plus #3/#6 consistency and teammate sign-off. Until then the proposal should not be described as finalized, and no issue is closed by this document alone.
