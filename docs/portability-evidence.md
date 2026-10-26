# Portability evidence and required checks (#12)

Verified 2026-10-26 against main commit `10c25663fb400452a190c7df19f9fc820b54674f`.
This is evidence for the existing test workflow, not a claim that a workflow
file configures repository protection.

## Main matrix evidence

[Main workflow run](https://github.com/thebhavye/polydash/actions/runs/40290326441) completed successfully. Each job installs
`.[yaml]`, checks dependencies, runs unittest discovery and compileall.
Fail-fast is disabled and the command sequence is shared by all matrix legs.

| Job | Result | Evidence |
| --- | --- | --- |
| Tests (macos-latest, Python 3.10) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602639) |
| Tests (windows-latest, Python 3.10) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602833) |
| Tests (ubuntu-latest, Python 3.10) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602842) |
| Tests (windows-latest, Python 3.12) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602855) |
| Tests (macos-latest, Python 3.12) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602858) |
| Tests (ubuntu-latest, Python 3.12) | success | [Job log](https://github.com/thebhavye/polydash/actions/runs/40290326441/job/121463602913) |

## Clean Linux setup verification

A fresh Python 3.12 virtual environment without system site packages was created
on Linux. From the main checkout, the following completed successfully:

```sh
python -m venv /tmp/polydash-dev
/tmp/polydash-dev/bin/python -m pip install ".[yaml]"
/tmp/polydash-dev/bin/python -m pip check
/tmp/polydash-dev/bin/python -m unittest discover -q
/tmp/polydash-dev/bin/python -m compileall -q polydash tests
```

The actual verification used a temporary workspace directory instead of /tmp.
Installation built PolyDash 0.1.0 and installed PyYAML 6.0.3. Dependency checks
passed and all 28 test methods passed. The developer setup includes Windows and
POSIX activation instructions and the Ubuntu interpreter-matched venv repair.
Windows/macOS execution is demonstrated independently by the job logs above;
these are not claims of local Windows/macOS execution in the Linux workspace.

## Required-check enforcement: administrator action remaining

The connected account reports push access but `admin: false` and
`maintain: false`. Reading main's classic branch protection returned HTTP 403,
"Resource not accessible by integration". Therefore classic protection could
not be audited or changed; do not infer that it is disabled from a denied read.
The accessible ruleset listing was empty at the time of inspection.

An administrator must inspect Settings → Rules → Rulesets (or the existing
main branch-protection rule), preserve any existing restrictions, and require
these exact test checks before merge:

- `Tests (macos-latest, Python 3.10)`
- `Tests (windows-latest, Python 3.10)`
- `Tests (ubuntu-latest, Python 3.10)`
- `Tests (windows-latest, Python 3.12)`
- `Tests (macos-latest, Python 3.12)`
- `Tests (ubuntu-latest, Python 3.12)`

Target `main`, enable enforcement, require pull requests with the other
teammate's review, and add all six checks from the completed workflow. This is
an owner checklist, not an instruction to disable administrator restrictions
or replace an existing stronger policy. Verify the saved rule is active and
record its link or read-back configuration on issue #12. A green PR alone does
not demonstrate enforcement; the administrator should confirm merge is blocked
when a required check fails or is pending.

Until that evidence is recorded, #12 remains open. This PR completes the
available setup/evidence work and deliberately uses Refs rather than Fixes.

