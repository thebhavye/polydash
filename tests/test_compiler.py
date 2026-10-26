import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from polydash import check
from polydash.analyzer import analyze
from polydash.loaders import load
from polydash.schema import COMPONENTS

FIXTURES = Path(__file__).parent / 'fixtures'


def run_fixture(path):
    return check(path.read_text(encoding='utf-8'), path.relative_to(FIXTURES).as_posix())


def canonical_ir(ir):
    # Source spans are the only ignored distinction; array order and values stay intact.
    return json.loads(json.dumps(ir.config, sort_keys=True))


def canonical_diagnostics(result):
    return [{k: v for k, v in item.items() if k != 'location'} for item in result.structured()]


class CompilerTests(unittest.TestCase):
    maxDiff = None

    def test_goldens(self):
        for path in sorted((FIXTURES / 'golden').glob('*.json')):
            if path.name.endswith('.expected.json'):
                continue
            with self.subTest(fixture=path.name):
                expected = json.loads(path.with_suffix('.expected.json').read_text())
                result = run_fixture(path)
                self.assertEqual(expected, result.structured())
                self.assertEqual(path.name.startswith('valid-'), result.ir is not None)
                for diagnostic in result.diagnostics:
                    self.assertIn(diagnostic.rule_id, result.human())
                    self.assertGreaterEqual(diagnostic.location.line, 1)
                    self.assertGreaterEqual(diagnostic.location.column, 1)
                    self.assertTrue(diagnostic.location.excerpt)

    def test_equivalence(self):
        for json_path in sorted((FIXTURES / 'pairs').glob('*.json')):
            with self.subTest(pair=json_path.stem):
                yaml_path = json_path.with_suffix('.yaml')
                left, right = run_fixture(json_path), run_fixture(yaml_path)
                self.assertEqual(canonical_ir(load(json_path.read_text(), str(json_path))),
                                 canonical_ir(load(yaml_path.read_text(), str(yaml_path))),
                                 'Canonical JSON/YAML IR differs (diff below)')
                self.assertEqual(canonical_diagnostics(left), canonical_diagnostics(right),
                                 'JSON/YAML diagnostics differ at logical paths (diff below)')
                self.assertEqual(left.ir is None, right.ir is None)
                if json_path.name.startswith('valid-'):
                    self.assertEqual([], left.structured())
                else:
                    self.assertTrue(left.diagnostics)

    def test_parse_rejections(self):
        shape_names = {'root-array', 'layout-array', 'components-object', 'component-scalar',
                       'children-object', 'layout-null'}
        yaml_unsupported = {'anchor', 'alias', 'tag', 'timestamp', 'set', 'complex-key',
                            'non-string-key', 'nonfinite', 'merge'}
        for path in sorted((FIXTURES / 'parse').iterdir()):
            with self.subTest(fixture=path.name):
                result = run_fixture(path)
                expected = 'PD0001'
                if path.suffix == '.json' and path.stem in shape_names:
                    expected = 'PD0002'
                elif path.suffix == '.yaml' and path.stem in yaml_unsupported:
                    expected = 'PD0003'
                elif path.suffix == '.yaml' and path.stem == 'empty':
                    expected = 'PD0002'
                self.assertIsNone(result.ir)
                self.assertEqual([expected], [d.rule_id for d in result.diagnostics])
                location = result.diagnostics[0].location
                lines = path.read_text().split('\n')
                self.assertGreaterEqual(location.column, 1)
                self.assertEqual(lines[location.line - 1].rstrip('\r'), location.excerpt)

    def test_duplicate_reports_every_occurrence(self):
        for name, count in [('duplicate-two', 2), ('duplicate-three', 3), ('duplicate-nested', 2)]:
            result = run_fixture(FIXTURES / 'golden' / (name + '.json'))
            duplicates = [d for d in result.diagnostics if d.rule_id == 'PD1005']
            self.assertEqual(count, len(duplicates))
            self.assertEqual(count, len({d.location.line for d in duplicates}))
        self.assertEqual([], run_fixture(FIXTURES / 'golden/valid-unique-case-space.json').structured())

    def test_schema_extension_needs_no_rule_change(self):
        registry = copy.deepcopy(COMPONENTS)
        registry['metric']['properties']['enabled'] = {'type': 'boolean'}
        text = '{"title":"x","layout":{"direction":"row"},"components":[{"id":"x","type":"metric","value":1,"enabled":3}]}'
        diagnostics = analyze(load(text, 'test.json'), registry)
        self.assertEqual(['PD1004'], [d.rule_id for d in diagnostics])
        self.assertEqual('/components/0/enabled', diagnostics[0].path)

    def test_locations_handle_escaped_keys_unicode_and_crlf(self):
        text = '{\r\n  "title":"✓",\r\n  "layout":{"direction":"row"},\r\n  "components":[],\r\n  "a/b~c": 1\r\n}'
        diagnostic = check(text).diagnostics[0]
        self.assertEqual('/a~1b~0c', diagnostic.path)
        self.assertEqual((5, 12), (diagnostic.location.line, diagnostic.location.column))

    def test_yml_and_extension_dispatch(self):
        path = FIXTURES / 'pairs/valid-minimal.yaml'
        self.assertEqual([], check(path.read_text(), 'dashboard.YML').structured())
        self.assertEqual('PD0003', check('{}', 'dashboard.toml').diagnostics[0].rule_id)

    def test_cli_writes_both_formats_and_exit_status(self):
        for fixture, expected_exit in [('missing-id', 1), ('syntax', 1), ('valid-minimal', 0)]:
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / 'diagnostics.json'
                path = FIXTURES / 'golden' / (fixture + '.json')
                result = subprocess.run([sys.executable, '-m', 'polydash', str(path),
                                         '--diagnostics-json', str(output)], capture_output=True, text=True)
                self.assertEqual(expected_exit, result.returncode, result.stderr)
                expected = check(path.read_text(), path.as_posix()).structured()
                self.assertEqual(expected, json.loads(output.read_text()))
                self.assertEqual(bool(expected), bool(result.stderr))

    def test_stdlib_only_json_and_missing_yaml_dependency(self):
        for filename, status in [('valid-minimal.json', 0), ('valid-minimal.yaml', 2)]:
            path = FIXTURES / 'pairs' / filename
            result = subprocess.run([sys.executable, '-S', '-m', 'polydash', str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(status, result.returncode, result.stderr)
            if status:
                self.assertIn('dependency approval is pending', result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_conformance_ir_preserves_every_input_value(self):
        for path in (FIXTURES / 'pairs').glob('valid-*.json'):
            with self.subTest(fixture=path.name):
                self.assertEqual(json.loads(path.read_text()), run_fixture(path).ir.config)

    def test_documented_diagnostic_example(self):
        text = '{"layout":{"direction":"row"},"components":[]}'
        result = check(text, 'broken.json')
        self.assertEqual([{'rule_id': 'PD1003', 'severity': 'error',
                           'message': "Missing required field 'title'", 'path': '/title',
                           'location': {'file': 'broken.json', 'line': 1, 'column': 1, 'excerpt': text}}],
                         result.structured())
        self.assertEqual("broken.json:1:1: error PD1003: Missing required field 'title'\n" + text + "\n^",
                         result.human())

    def test_yaml_diagnostics_exact_positions(self):
        cases = [
            ('title: [broken\n', 'PD0001', 2, 1),
            ('title: x\ntitle: y\n', 'PD0001', 2, 1),
            ('title: &a x\n', 'PD0003', 1, 8),
            ('---\ntitle: a\n---\ntitle: b\n', 'PD0001', 3, 1),
            ('title: x\nlayout: {direction: row}\ncomponents:\n- id: x\n  type: metric\n  value: wrong\n',
             'PD1004', 6, 10),
        ]
        for text, rule, line, column in cases:
            with self.subTest(text=text):
                diagnostic = check(text, 'dashboard.yaml').diagnostics[0]
                self.assertEqual((rule, line, column),
                                 (diagnostic.rule_id, diagnostic.location.line, diagnostic.location.column))

    def test_yaml_implicit_types_and_multiline_strings(self):
        text = 'title: |\n  Sales\n  Overview\nlayout: {direction: row}\ncomponents:\n- {id: x, type: metric, value: 0x10}\n- {id: y, type: filter, options: ["on"], multiple: yes}\n'
        result = check(text, 'dashboard.yaml')
        self.assertEqual([], result.structured())
        self.assertEqual('Sales\nOverview\n', result.ir.config['title'])
        self.assertEqual(16, result.ir.config['components'][0]['value'])
        self.assertIs(True, result.ir.config['components'][1]['multiple'])

    def test_cli_io_errors(self):
        result = subprocess.run([sys.executable, '-m', 'polydash', 'missing.json'], capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
