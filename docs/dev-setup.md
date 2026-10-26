# Clean development setup

Python 3.10+ is required; CI exercises 3.10 and 3.12. Run commands from the repository root. Create a fresh environment without system site packages:

On Debian/Ubuntu installations using the system Python, the `venv` module may
be present while `ensurepip` is missing. If `python3 -m venv .venv` reports that
the environment could not be created because `ensurepip` is unavailable,
install the distribution's Python `venv` package matching that interpreter
(the error names the package, for example `python3.12-venv`), then retry.
Some distributions also expose system Python as `python3` without a `python`
alias; use `python3 -m venv .venv` in that case. After activating the venv,
`python` refers to the environment interpreter. GitHub Actions uses
`setup-python`, which already provides a working venv/pip.

```sh
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```sh
. .venv/bin/activate
```

Activation is optional: Windows can invoke `.venv\Scripts\python.exe` directly; Linux/macOS can use `.venv/bin/python`.

Install the package and declared YAML extra, check dependencies, then run the documented test command:

```sh
python -m pip install ".[yaml]"
python -m pip check
python -m unittest discover -v
python -m compileall -q polydash tests
```

For JSON-only usage, install `.` without the extra. YAML requires the extra and the full suite deliberately exercises YAML, so install `.[yaml]` for development. No manual global PyYAML installation is needed. The missing-extra regression uses `python -S` to verify JSON still works without third-party site packages and YAML gives an actionable installation hint.

The suite includes structured diagnostic goldens and deep JSON/YAML rejection without tracebacks. Regenerate goldens only for intentional behavior changes using `python -m tests.update_goldens`; review fixture diffs before committing.

## Portability tracking (#12)

`.github/workflows/tests.yml` installs the package with YAML support in each fresh runner and executes the same commands on Ubuntu, Windows and macOS, with fail-fast disabled. Tests use temporary paths and the active interpreter. No packaging/deployment jobs are added.

Earlier verification used an isolated Windows Python 3.12 venv. A fresh Linux
venv run is recorded in the portability evidence below; macOS verification comes
from the linked CI jobs. Do not infer successful runs from workflow configuration
alone. Issue #12 stays open until its review, green-main and required-check acceptance criteria are satisfied. Repository branch-protection settings are not changed by this workflow.

## Verified setup and remaining enforcement

The [portability evidence](portability-evidence.md) records the six successful
main-branch jobs and a fresh Linux venv install/dependency/test run. It also
lists exact check names and the administrator steps needed for merge enforcement.
The current collaborator account cannot inspect classic branch protection
(HTTP 403) or configure it; this is an explicit remaining #12 requirement,
not a setup step that the test workflow completes automatically.

For just the structured diagnostic corpus, run:

```sh
python -m unittest tests.test_compiler.CompilerTests.test_goldens -v
```
