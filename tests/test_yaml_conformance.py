"""YAML frontend conformance independent of the renderer."""
import json
import unittest
from pathlib import Path

from polydash import check


class YamlConformanceTests(unittest.TestCase):
    def test_shared_ir_examples_in_both_yaml_extensions(self):
        root = Path(__file__).parent / 'fixtures/pairs'
        for name in ('valid-minimal', 'valid-chart', 'valid-nested'):
            expected = json.loads((root / (name + '.json')).read_text(encoding='utf-8'))
            source = (root / (name + '.yaml')).read_text(encoding='utf-8')
            for suffix in ('.yaml', '.yml'):
                with self.subTest(example=name, suffix=suffix):
                    result = check(source, name + suffix)
                    self.assertIsNotNone(result.ir, result.human())
                    self.assertEqual(expected, result.ir.config)
                    self.assertEqual(name + suffix, result.ir.location(()).file)

    def test_three_syntax_failures_have_exact_locations_and_shared_shape(self):
        cases = [
            ('title: [broken\n', 2, 1, ''),
            ('title: "unterminated\n', 2, 1, ''),
            ('title: x\ntitle: y\n', 2, 1, 'title: y'),
        ]
        for text, line, column, excerpt in cases:
            with self.subTest(source=text):
                result = check(text, 'broken.yaml')
                self.assertIsNone(result.ir)
                self.assertEqual(1, len(result.diagnostics))
                diagnostic = result.structured()[0]
                self.assertEqual({'rule_id', 'severity', 'message', 'path', 'location'}, set(diagnostic))
                self.assertEqual('PD0001', diagnostic['rule_id'])
                self.assertEqual('error', diagnostic['severity'])
                self.assertTrue(diagnostic['message'])
                self.assertEqual({'file': 'broken.yaml', 'line': line, 'column': column,
                                  'excerpt': excerpt}, diagnostic['location'])
                self.assertIn(f'broken.yaml:{line}:{column}: error PD0001', result.human())

    def test_unsupported_aliases_tags_and_multidocument_have_locations(self):
        cases = [('title: &name X\n', 'PD0003', 1, 8),
                 ('title: *name\n', 'PD0003', 1, 8),
                 ('title: !!str X\n', 'PD0003', 1, 8),
                 ('---\ntitle: a\n---\ntitle: b\n', 'PD0001', 3, 1)]
        for text, rule, line, column in cases:
            with self.subTest(source=text):
                result = check(text, 'unsupported.yml')
                self.assertIsNone(result.ir)
                self.assertEqual(1, len(result.diagnostics))
                diagnostic = result.diagnostics[0]
                self.assertEqual((rule, line, column),
                                 (diagnostic.rule_id, diagnostic.location.line, diagnostic.location.column))
                self.assertEqual(text.split('\n')[line - 1], diagnostic.location.excerpt)
