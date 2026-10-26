# Backlog audit

Snapshot: 2026-10-26. All issues #1-#14 open, no PRs. Reviewed complete issue bodies, assignments, labels, milestones and native #2/#6 dependency lists (both empty: the cycle was in prose). No duplicate issues or milestones created.

Five milestones match README phases: Project Foundation (#1/#5/#14), Compiler Core (#2/#4/#6), Static Analysis (#3/#7-#9/#13), Multi-Format Support (#10/#11), Portability and Release (#12). Milestone IDs do not encode phase order. Existing labels include architecture, compiler, parser, validation, code-generation, testing, documentation, cross-platform and accessibility, plus general GitHub labels.

| Issue | Original prerequisites | Finding / recommendation |
| --- | --- | --- |
| #1 architecture | None | This baseline needs teammate review. |
| #2 IR/schema | #1, #6 | Remove #6 closure blocker; joint shared-contract review. |
| #3 rules/diagnostics | #2 | Rules need unvalidated values/context to detect missing fields before valid IR exists. |
| #4 integration/errors | #1, #2 | Finalize interfaces and ADR 0002; coordinate with #3. |
| #5 conventions | None stated | Independent docs work; outside this PR's deliverables. |
| #6 grammar | #2 | Depend on #1 and joint #2 review; agree syntax/shape boundary. |
| #7 validation | #2, #3, #6 | Needs parsed input; no parser implementation issue currently delivers it. |
| #8 IDs/types | #7 | Type checks overlap #7; propose #7 owns initial schema-driven checks, #8 adds IDs and broader type coverage. Needs agreement. |
| #9 diagnostic goldens | #3, #7, #8 | Can test through APIs before CLI; does not deliver a complete generator. |
| #10 YAML | #2, #6, #9 | Also needs working JSON parse/analyze/generate path; #9 alone does not supply it. |
| #11 equivalence | #10, #2 | Exclude provenance from semantic IR; compare rule IDs/logical paths and verify per-format spans separately. |
| #12 CI/setup | None stated | Toolchain is a practical prerequisite; introduce CI once tests exist, even before release. |
| #13 a11y/responsive | #3 | Research only, not initial feature promises. |
| #14 survey | None stated | Separate evidence document; teammate review still required. |

## Conflicts and missing decisions

1. #2/#6 form a completion cycle; use the [joint contract](contracts/ir-json-shared-contract.md) and update tracker dependency prose consistently.
2. #6 makes valid JSON with wrong shapes parse-level; architecture proposes semantic classification. Explicit proposed amendment, not a settled decision.
3. #3 suggests IR-only rules while #7 detects missing/invalid structures. Shared unvalidated analysis context resolves the design contradiction without exposing partial valid IR.
4. JSON parser implementation, IR construction, CLI/driver, HTML/CSS/JS generation and packaging have no explicit delivery issues. Specification issues do not implement these. Maintainers should triage after agreement; no new issues created here.
5. #7/#8 overlap and #10's working-pipeline assumption require scope agreement.
6. Some bodies call Ayush unassigned, while current GitHub assignments include goodchanges (display name Ayush Kumar Verma). This audit does not independently establish identity or change assignments/README identity claims.

Proposals are not team approval; draft documents do not close issues. Recommended next work: joint #2/#6 specification after #1 review, preserving both acceptance criteria.
