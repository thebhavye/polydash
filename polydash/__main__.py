"""Validate configurations and optionally render a static HTML preview."""
import argparse
import json
import sys
from pathlib import Path

from . import check
from .generator import generate_html


def main():
    parser = argparse.ArgumentParser(description="Validate a PolyDash JSON/YAML configuration")
    parser.add_argument("file", type=Path)
    parser.add_argument("--diagnostics-json", type=Path, help="Write structured diagnostics alongside stderr output")
    parser.add_argument("--output", type=Path, help="Write a self-contained HTML dashboard preview after validation")
    args = parser.parse_args()
    try:
        result = check(args.file.read_text(encoding="utf-8"), args.file.as_posix())
    except (OSError, UnicodeError) as error:
        parser.exit(2, f"polydash: {error}\n")
    except ModuleNotFoundError as error:
        if error.name != "yaml":
            raise
        parser.exit(2, 'polydash: YAML support is optional; install it with: python -m pip install "polydash[yaml]"\n')
    if result.diagnostics:
        print(result.human(), file=sys.stderr)
    if args.diagnostics_json:
        try:
            args.diagnostics_json.write_text(json.dumps(result.structured(), indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            parser.exit(2, f"polydash: {error}\n")
    if args.output and result.ir is not None:
        try:
            args.output.write_text(generate_html(result.ir), encoding="utf-8")
        except OSError as error:
            parser.exit(2, f"polydash: {error}\n")
    return int(any(d.severity == "error" for d in result.diagnostics))


if __name__ == "__main__":
    sys.exit(main())
