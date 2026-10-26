import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from polydash import check
from polydash.generator import generate_html


ROOT = Path(__file__).resolve().parents[1]


class HtmlPrototypeTests(unittest.TestCase):
    def test_valid_dashboard_renders_components_and_escapes_source_text(self):
        config = {
            "title": "Sales <script>alert(1)</script>",
            "layout": {"direction": "row"},
            "components": [
                {"id": "revenue", "type": "metric", "title": "Revenue", "value": 42, "unit": "USD"},
                {"id": "region", "type": "filter", "title": "Region", "options": ["North", "<img src=x>"]},
                {"id": "details", "type": "table", "data": {"source": "demo.csv"},
                 "columns": ["Q1", "Q2"], "rows": [[1, 2]]},
                {"id": "trend", "type": "chart", "title": "Trend",
                 "data": {"source": "sales.csv"}, "series": ["revenue"]},
            ],
        }
        result = check(json.dumps(config))
        self.assertIsNotNone(result.ir, result.human())
        html = generate_html(result.ir)
        self.assertIn("42", html)
        self.assertIn("<table>", html)
        self.assertIn("<select>", html)
        self.assertIn("Chart data is not loaded", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img src=x&gt;", html)
        self.assertNotIn("<script>", html)

    def test_cli_writes_html_only_for_valid_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dashboard.html"
            valid = ROOT / "tests/fixtures/pairs/valid-all-properties.json"
            run = subprocess.run([sys.executable, "-m", "polydash", str(valid),
                                  "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(output.read_text(encoding="utf-8").startswith("<!doctype html>"))

            output.unlink()
            invalid = ROOT / "tests/fixtures/golden/missing-id.json"
            run = subprocess.run([sys.executable, "-m", "polydash", str(invalid),
                                  "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertFalse(output.exists())

    def test_json_and_yaml_render_identically(self):
        try:
            import yaml  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("Optional PyYAML extra is unavailable")
        base = ROOT / "tests/fixtures/pairs/valid-nested"
        json_result = check(base.with_suffix(".json").read_text(encoding="utf-8"), "dashboard.json")
        yaml_result = check(base.with_suffix(".yaml").read_text(encoding="utf-8"), "dashboard.yaml")
        self.assertIsNotNone(json_result.ir, json_result.human())
        self.assertIsNotNone(yaml_result.ir, yaml_result.human())
        html = generate_html(json_result.ir)
        self.assertEqual(html, generate_html(yaml_result.ir))
        self.assertIn('class="card group"', html)
        self.assertIn("North", html)

    def test_warning_does_not_block_html_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "warning.json"
            output = Path(temporary) / "preview.html"
            source.write_text(json.dumps({
                "title": "Warning demo", "layout": {"direction": "column"},
                "components": [{"id": "region", "type": "filter", "options": ["North"]}],
            }), encoding="utf-8")
            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PD2001", run.stderr)
            self.assertIn("<select>", output.read_text(encoding="utf-8"))

    def test_output_cannot_replace_source_or_diagnostics(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            source_bytes = (ROOT / "tests/fixtures/pairs/valid-minimal.json").read_bytes()
            source.write_bytes(source_bytes)

            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--output", str(source)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn("same file", run.stderr)
            self.assertEqual(source.read_bytes(), source_bytes)

            diagnostics = Path(temporary) / "diagnostics.json"
            diagnostics.write_text("keep me", encoding="utf-8")
            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--diagnostics-json", str(diagnostics), "--output", str(diagnostics)],
                                 cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(diagnostics.read_text(encoding="utf-8"), "keep me")
            self.assertEqual(source.read_bytes(), source_bytes)

            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--diagnostics-json", str(source)],
                                 cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(source.read_bytes(), source_bytes)

    def test_existing_hardlink_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            source_bytes = (ROOT / "tests/fixtures/pairs/valid-minimal.json").read_bytes()
            source.write_bytes(source_bytes)
            alias = Path(temporary) / "alias.html"
            try:
                os.link(source, alias)
            except OSError as error:
                self.skipTest(f"Hard links unavailable: {error}")
            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--output", str(alias)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(alias.read_bytes(), source_bytes)

    def test_symlink_loop_reports_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            source.write_bytes((ROOT / "tests/fixtures/pairs/valid-minimal.json").read_bytes())
            loop = Path(temporary) / "loop.html"
            try:
                loop.symlink_to(loop)
            except OSError as error:
                self.skipTest(f"Symlinks unavailable: {error}")
            run = subprocess.run([sys.executable, "-m", "polydash", str(source),
                                  "--output", str(loop)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn("cannot inspect output paths", run.stderr)
            self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
