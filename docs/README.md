# Documentation index

Proposed normative documents describe a contract awaiting joint review. They do
not become approved just because a prototype follows them. Informative documents
supply evidence or instructions, without adding schema requirements.

## This branch / PR #15

| Document | Authority and purpose |
| --- | --- |
| [IR/schema](ir.md) | Proposed normative: Python prototype representation and component table (#2) |
| [Validation/diagnostics](validation-rules.md) | Proposed normative: rule IDs, source locations and exact outputs (#3) |
| [JSON grammar](json-grammar.md) | Proposed normative: implemented grammar and parse/semantic boundary (#6) |
| [YAML support](yaml-support.md) | Proposed normative: subset, optional extra, rejected constructs (#10) |
| [Equivalence tests](equivalence-tests.md) | Proposed normative: canonical IR and diagnostic comparison (#11) |
| [Development setup](dev-setup.md) | Informative: fresh environment, installation, tests and CI (#12) |
| [Accessibility/responsive spike](research/a11y-responsive-spike.md) | Informative: proposed checks and prior art; no new rules (#13) |
| [Issue review](issue-review.md) | Informative: issue-by-issue evidence and unresolved criteria |
| [Contribution guide](../CONTRIBUTING.md) | Proposed normative: branch/review/commit/test expectations (#5) |
| [Bug template](../.github/ISSUE_TEMPLATE/bug.md) / [enhancement template](../.github/ISSUE_TEMPLATE/enhancement.md) | Informative: issue prompts |
| [CI workflow](../.github/workflows/tests.yml) | Executable test matrix; branch protection is separate |

## Architecture proposal in PR #16 (not merged here)

The following are separate proposals at reviewed commit `68abacc`. Their links
point to that branch's files, not nonexistent files in this branch. Reconcile
the runtime, shape boundary, spans, diagnostic model/order and overlapping
README changes before treating both PRs as one agreed contract.

| Document | Authority and purpose |
| --- | --- |
| [Architecture](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/architecture.md) | Proposed normative: located unvalidated input → analysis → validated IR (#1) |
| [ADR 0001](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/adr/0001-language-runtime.md) | Proposed normative: TypeScript/Node alternative; not an accepted rewrite decision |
| [ADR 0002](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/adr/0002-error-handling.md) | Proposed normative: collect/abort policy and candidate exit codes (#4) |
| [ADR 0003](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/adr/0003-ir-representation.md) | Proposed normative: validated typed IR and test projection |
| [Shared JSON/IR contract](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/contracts/ir-json-shared-contract.md) | Proposed normative: co-design and unresolved shape amendment (#2/#6) |
| [Backlog audit](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/backlog-audit.md) | Informative: earlier snapshot before the implementation PR |
| [Nine-system survey](https://github.com/thebhavye/polydash/blob/68abacca4f29897e37d385c817a30cf950299000/docs/research/dashboard-generator-survey.md) | Informative: prior art and limits on novelty claims (#14) |

After merge/reconciliation, replace the cross-PR links with local links and
update authority levels only when acceptance is recorded in review.
