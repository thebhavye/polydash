# Issue review and remaining acceptance criteria

Reviewed 2026-10-26: issues #1–#14, PR #15 at `19f3b81` and PR #16 at `68abacc`.
Neither open PR is a merged resolution. This follow-up supplies contribution
conventions and the #13 research spike; it does not rewrite Bhavye's proposal.

## Evidence

- Local `python -m unittest discover -v`: all 18 methods pass, including 36
  structured goldens, 29 malformed-input fixtures and seven paired configs.
- The PR #15 source-location finding is fixed in `3791682`. A 2,000-component
  dashboard improved from 3.208s to 0.033s locally; 8,000 took 0.154s. These are
  measurements, not portable performance guarantees or test thresholds.
- Owner-authored `664501f` adds the optional YAML extra and excessive-nesting
  rejection; `19f3b81` supplies supported CI action versions. These concurrent
  changes were retained and tested, not overwritten by a competing setup.
- [Run 40285073940](https://github.com/thebhavye/polydash/actions/runs/40285073940)
  has six successful jobs: Ubuntu/Windows/macOS × Python 3.10/3.12. Each installs
  `.[yaml]`, checks dependencies, runs tests and compileall. This is PR evidence;
  it is not a green-main run or proof of required branch checks.
- Review comments on PR #16 request reconciliation of runtime, source units,
  shape classification, diagnostics and overlapping documentation. Existing
  README consistency feedback remains applicable.

## Every original issue

| Issue | Deliverable/evidence | What remains before resolution |
| --- | --- | --- |
| [#1](https://github.com/thebhavye/polydash/issues/1) architecture | PR #16 has stages/interfaces and three proposed ADRs; teammate review posted | Author addresses review and reconciles the implementation baseline; merge |
| [#2](https://github.com/thebhavye/polydash/issues/2) IR/schema | PR #15 has schema.py, ir.md, three shared conformance examples; #16 proposes a different located-input/typed-IR boundary | Joint choice on runtime, representation, spans and grammar before approval |
| [#3](https://github.com/thebhavye/polydash/issues/3) rules/diagnostics | PR #15 has stable IDs, schema walker and exact human/JSON example; #16 proposes a different diagnostic model/order | Agree authoritative rule/source/output contract and record owner/peer review |
| [#4](https://github.com/thebhavye/polydash/issues/4) pipeline | PR #16 architecture/ADR describes stage results and failure scenarios | Finalize current-versus-target APIs and exit codes; #15 currently groups usage/I/O/dependency as 2, whereas #16 proposes distinct statuses |
| [#5](https://github.com/thebhavye/polydash/issues/5) conventions | This follow-up adds CONTRIBUTING, authority-indexed docs, two issue templates and editor/build ignores | Other teammate confirms self-serve onboarding in review; merge |
| [#6](https://github.com/thebhavye/polydash/issues/6) JSON grammar | PR #15 grammar and valid/malformed fixture inventory | Settle updated issue's semantic-shape proposal versus existing parse-level PD0002; reconcile with #2/#3/#4 |
| [#7](https://github.com/thebhavye/polydash/issues/7) first-wave rules | PR #15 required/kind/property/type fixtures and collect-all golden | Approve shared contracts and merge; no parser/generator rewrite is assumed |
| [#8](https://github.com/thebhavye/polydash/issues/8) IDs/types | PR #15 reports all two/three/nested collisions and tests every current property type; extension test proves schema-driven behavior | Review contracts, ID policy and coverage; merge |
| [#9](https://github.com/thebhavye/polydash/issues/9) diagnostics/goldens | PR #15 structured artifact, human output, 36 goldens and explicit regeneration | Agree diagnostic contract, review golden changes, merge |
| [#10](https://github.com/thebhavye/polydash/issues/10) YAML | PR #15 shared loaders/analyzer, subset docs, optional extra added in owner commit, located parse failures | Joint prerequisite contracts and merge; generator remains absent and is not silently supplied by this issue |
| [#11](https://github.com/thebhavye/polydash/issues/11) equivalence | PR #15 has five valid/two invalid pairs with canonical IR/diagnostic diffs, now exercised in CI | Approve equivalence/IR meaning and merge |
| [#12](https://github.com/thebhavye/polydash/issues/12) portability | PR #15 full six-job green matrix and development setup | Green run after merge on main; administrator configures required checks; no claim that workflow YAML enables protection |
| [#13](https://github.com/thebhavye/polydash/issues/13) spike | This follow-up has separate a11y/responsive findings, prior-art verdicts, three proposals with examples and explicit limits | Review and merge research; triage #17/#18 rather than adding unapproved analyzer rules |
| [#14](https://github.com/thebhavye/polydash/issues/14) survey | PR #16 has nine systems, primary links and an honest verdict; this README links it | Author resolves the review comments; peer-reviewed research and reconciled README merge |

The new [#17](https://github.com/thebhavye/polydash/issues/17) and
[#18](https://github.com/thebhavye/polydash/issues/18) are the two proposal issues
requested by the #13 spike. They have fixture pairs and estimates, and await
maintainer accept/reject decisions. They are not implemented rules or automatic
extensions of the original fourteen issues.

## Joint decisions to make once

PR #15 uses Python, code-point start locations, parse-level structural checking,
value anchors, rule/traversal order and a tree/source-map IR. PR #16 proposes
TypeScript, UTF-16 ranges, semantic-level shape checking, key anchors, source
ordering and typed validated IR after a separate located-value tree. Both are
reviewable proposals; they are not interchangeable descriptions of the same
implementation. Confirm which choices are retained before changing code/goldens.
Do not turn this review into an unapproved language rewrite or mark proposed
ADRs accepted without the teammates' agreement.
