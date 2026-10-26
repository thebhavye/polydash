# Contributing

Use a feature branch from main and open a PR. Do not push directly to main.
For stacked work, name the prerequisite PR in the description and target its
branch until it merges. Keep unrelated work in separate commits/PRs.

```sh
git switch main
git pull --ff-only
git switch -c fix/short-description
```

Write imperative commit subjects describing the behavior: `Fix duplicate ID
locations` or `Document parser error boundary`. No prefix convention is required.

## Review

Every PR needs review by the other teammate. Describe the concrete problem,
resulting behavior, linked issues and commands/results used to validate it.
Do not claim acceptance criteria are complete before their evidence exists.
An open PR is not a resolved issue. Use `Fixes #N` when merging really fulfills
the issue; use `Refs #N` for partial work or pending approvals.

Mark proposed contracts and ADRs as proposed until accepted in review. New
runtime dependencies need owner approval before merge, with the library and
version constraint written in the PR. PR #15 declares PyYAML through the optional `yaml` extra in the owner-authored
commit 664501f; base installation remains JSON-only. This choice does not
authorize adding unrelated dependencies.

## Tests and documentation

See [development setup](docs/dev-setup.md). Run `python -m unittest discover -v`.
Parser work needs valid and malformed fixtures with source positions. Semantic
rules need passing and violating fixtures plus collect-all coverage. Change a
schema expectation in schema data, not a property-specific branch in the rule.
JSON/YAML changes need paired IR and diagnostic comparisons. Future generator
work needs escaping and deterministic output checks. CI runs the full suite after installing `.[yaml]`; a missing-library regression
separately verifies base JSON-only behavior.

To change diagnostics intentionally, run `python -m tests.update_goldens`, review
the full fixture/expected-output diff and explain it in the PR. Do not regenerate
just to make a failing test green. Fixing a performance bug must preserve source
locations and diagnostics; avoid timing thresholds that depend on the machine.

[The docs index](docs/README.md) distinguishes proposed contracts from informative
research. Update that index when adding docs. Keep code examples runnable and
state when an example is only a future proposal. Bug/enhancement templates are
in `.github/ISSUE_TEMPLATE/`.

Before merging the initial conventions PR, the other teammate should confirm
that these docs alone explain how to submit a change and what tests it needs.
That onboarding confirmation is pending; it has not been asserted on their behalf.
