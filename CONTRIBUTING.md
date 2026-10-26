# Contributing to PolyDash

Start with [README](README.md) for implemented scope, the [documentation index](docs/README.md) for document authority and pending proposals, and [development setup](docs/dev-setup.md) for installation. This branch includes the implementation proposed in PR #15; it does not imply that PR is merged or architecture decisions are approved.

## Start a change

1. Find the existing issue and related PRs. Check dependencies and acceptance criteria before coding; do not duplicate issues or milestones. Ask for clarification in the issue when requirements conflict, and document a proposed resolution rather than silently choosing incompatible contracts.
2. Start from an updated main after prerequisites merge. Use a feature branch, normally `codex/<short-description>` for Codex changes. Never push directly to main.
3. Keep one reviewable concern per PR. If a prerequisite is still an open PR, a stacked branch may start from its head; target that prerequisite branch and identify the dependency in the PR. After it merges, retarget the child PR to main and inspect the diff again. Do not merge a prerequisite merely to unblock your branch.
4. Update the relevant docs and fixtures with behavior changes. Mark unresolved architecture decisions **proposed**. Dependency additions need explicit owner review; check existing packages before adding one. A YAML implementation must follow the documented supported subset and shared semantics.

Example once the needed base is on main:

```sh
git switch main
git pull --ff-only
git switch -c codex/describe-change
```

Commit small, coherent changes. Prefer messages such as `docs: explain diagnostics`, `fix: reject duplicate IDs`, `test: cover malformed input` or `ci: test supported platforms`. Do not commit environments, credentials, generated build products or unrelated changes. Inspect `git status` and the diff before staging.

## Tests to include

| Change | Required evidence |
| --- | --- |
| Parser / loader | Valid and rejected inputs, exact source positions, syntax/shape boundary and documented unsupported constructs. |
| Semantic rule / schema | Positive and negative cases, structured rule IDs/locations, multiple findings where recovery matters. |
| IR / generator, when present | Representation or output comparisons, deterministic results, escaping and invalid-input generation gate where applicable. No generator exists yet. |
| Multiple frontends | Same-meaning JSON/YAML pairs, equivalent IR/diagnostics, independently correct source spans. |
| CLI / I/O | Exit status, human and structured diagnostics, no traceback for expected invalid input. |
| Documentation only | Relative links/anchors, examples and status claims checked; explain why executable tests do not apply. |

Install development dependencies and run from the repository root in a fresh virtual environment when changing setup or dependencies:

```sh
python -m pip install ".[yaml]"
python -m pip check
python -m unittest discover -v
python -m compileall -q polydash tests
git diff --check
```

See the setup guide for environment creation and Windows/Linux/macOS commands. The full suite requires the declared YAML extra; a JSON-only install is insufficient for all tests. Existing golden assertions are part of unittest discovery. Regenerate with `python -m tests.update_goldens` only for intentional changes, then review every changed expected diagnostic. Do not replace failing goldens merely to make a test pass.

CI runs the same suite on Windows, Linux and macOS with Python 3.10 and 3.12. Review all matrix results; a local pass does not establish portability. Branch protection is not configured by a workflow file; issue #12 tracks remaining enforcement and main-branch evidence.

## Open and review a PR

Describe the problem, final behavior, linked issue(s), test commands/results and unresolved design questions. Use `Refs #N` for partial work or pending approval; use `Fixes #N` only when all applicable acceptance criteria will be met on merge. Explain any new dependency, behavior change or supported-input change. The PR template supplies a short checklist.

Every PR requires review by the other teammate before merge. Reviewers should be able to understand the change from the diff and repository docs without reading chat history. Do not guess a teammate's GitHub username or change assignments without verification. Ask the verified reviewer to check relevant contracts and test evidence; authors should address feedback and rerun affected checks after changes. An automated review does not substitute for teammate approval.

For documentation/convention changes, ask the other teammate to confirm that they can (a) start and submit a change and (b) determine its required tests using these docs alone. Record that confirmation before treating issue #5's onboarding criterion as complete.

Merge only after the required review and checks, and after conflicting prerequisite decisions are resolved. Creating a PR does not authorize merging it. Keep issue status honest: proposed designs, incomplete acceptance criteria and blocked prerequisites must remain visible.
