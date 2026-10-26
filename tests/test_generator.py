import json
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
        self.assertEqual(generate_html(json_result.ir), generate_html(yaml_result.ir))


if __name__ == "__main__":
    unittest.main()
