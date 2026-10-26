# Documentation index

Use [README](../README.md) for current capabilities and [CONTRIBUTING](../CONTRIBUTING.md) for branch, PR, review and test conventions. This index describes the files on this branch, which is stacked on the unmerged [PR #15](https://github.com/thebhavye/polydash/pull/15).

## Authority

**Workflow guidance** defines how to contribute. **Implementation contract, pending review** describes this branch's Python implementation and fixtures; it does not mean a team design decision was approved. **Proposed target** describes an unmerged architecture option. **Informative** explains evidence or examples rather than defining accepted input. Source, tests and documentation should agree; report contradictions for review instead of assuming a proposal supersedes implemented behavior.

| Artifact | Purpose | Authority / status |
| --- | --- | --- |
| [README](../README.md) | Current feature/status summary and check adapter usage | Informative; code and fixtures establish implemented behavior. |
| [Contributing](../CONTRIBUTING.md) | Branches, commits, PRs, teammate review and required tests | Workflow guidance proposed by issue #5. |
| [Portability evidence](portability-evidence.md) | Verified main matrix, clean Linux setup and required-check admin checklist | Informative evidence for #12; enforcement still requires an administrator. |
| [Development setup](dev-setup.md) | Clean Python environment, installation and test commands | Operational guidance; platform CI verifies commands. |
| [IR and component schema](ir.md) | Shared tree, component properties, source map and conformance examples | Implementation contract, pending #2 owner review. |
| [JSON grammar](json-grammar.md) | Accepted syntax/shapes, semantic boundary and fixture inventory | Implementation contract, pending #6 joint review. |
| [Validation and diagnostics](validation-rules.md) | Rule invocation, IDs, severities, human/structured output, golden examples | Implementation contract, pending #3 owner review. |
| [YAML subset](yaml-support.md) | Optional dependency, scalar resolution and rejected constructs | Implementation contract; YAML is available only with the extra. |
| [Equivalence tests](equivalence-tests.md) | Equality rules and adding paired fixtures | Test contract proposed for #11. |
| [Accessibility/responsive spike](research/a11y-responsive-spike.md) | Static versus render-time findings, proposed rules, prior art and limitations | Informative research for #13; title warnings implemented separately in #21. |
| [Issue review](issue-review.md) | Evidence and open acceptance criteria for #1–#14 | Informative dated review, not issue closure. |
| [Bug template](../.github/ISSUE_TEMPLATE/bug_report.md) | Reproduction and expected/actual diagnostics | Contributor workflow template. |
| [Enhancement / validation template](../.github/ISSUE_TEMPLATE/enhancement.md) | Scope, dependencies, decisions and test expectations | Contributor workflow template. |
| [PR template](../.github/pull_request_template.md) | Change explanation, issue links and verification | Contributor workflow template. |

## Parallel architecture proposal

[PR #16](https://github.com/thebhavye/polydash/pull/16) contains the following documents. They are linked through GitHub because they are not present on this branch. They remain proposed; this index does not accept them or claim they are merged.

| Proposed artifact in PR #16 | Purpose |
| --- | --- |
| [Architecture](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/architecture.md) | Target stages/interfaces, located values, validated IR, portability and differences from PR #15. |
| [ADR 0001](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/adr/0001-language-runtime.md) | Runtime comparison; TypeScript/Node proposal conflicts with PR #15's Python and needs agreement. |
| [ADR 0002](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/adr/0002-error-handling.md) | Proposed error collection and exit statuses. |
| [ADR 0003](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/adr/0003-ir-representation.md) | Proposed validated IR and test serialization. |
| [Joint IR/JSON contract](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/contracts/ir-json-shared-contract.md) | #2/#6 coordination, cycle resolution and open vocabulary decisions. |
| [Backlog audit](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/backlog-audit.md) | Dated informative dependency/scope findings. |
| [Generator survey](https://github.com/thebhavye/polydash/blob/codex/architecture-baseline/docs/research/dashboard-generator-survey.md) | Informative research; no unsupported novelty claim. |

Before both PRs merge, reconcile runtime, provenance units, IR representation, shape-error ownership and exit codes. Convert these external branch links to local links when those documents land; do not create duplicate competing specs. No document is designated an approved normative architecture while those decisions remain open.

## Future documents

Issue #4 owns a final stage integration/error contract, which is not yet present here. The #13 research spike is linked above; its proposals do not implement new checks. CI/setup work is tracked by #12; a workflow alone does not satisfy all its acceptance criteria.

Documentation changes should preserve clear status labels, use relative links for existing repository files, identify the owner issue and keep examples consistent with fixtures. Record decisions and their rationale in ADRs marked proposed until reviewed; avoid describing planned features as implemented.
