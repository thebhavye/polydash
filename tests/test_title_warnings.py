import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from polydash import check
from polydash.analyzer import analyze
from polydash.loaders import load
from polydash.schema import COMPONENTS


class TitleWarningTests(unittest.TestCase):
    def dashboard(self, components):
        return {'title': 'Sales', 'layout': {'direction': 'column'}, 'components': components}

    def component(self, kind):
        if kind == 'filter':
            return {'id': 'region', 'type': kind, 'options': ['North', 'South']}
        return {'id': 'trend', 'type': kind, 'data': {'source': 'sales.csv'}, 'series': ['revenue']}

    def test_title_cases_across_formats_and_nesting(self):
        absent = object()
        for kind, rule in [('filter', 'PD2001'), ('chart', 'PD2002')]:
            for title in (absent, '', ' \t\n', '\u2003', 'Revenue by month', ' Region ', None, 42, [], {}):
                for nested in (False, True):
                    component = self.component(kind)
                    if title is not absent:
                        component['title'] = title
                    components = [component]
                    path = '/components/0'
                    if nested:
                        components = [{'id': 'group', 'type': 'group', 'layout': {'direction': 'row'},
                                       'children': components}]
                        path += '/children/0'
                    config = self.dashboard(components)
                    results = []
                    for suffix, text in [('json', json.dumps(config, indent=2)),
                                         ('yaml', yaml.safe_dump(config, sort_keys=False))]:
                        with self.subTest(kind=kind, title=title, nested=nested, suffix=suffix):
                            result = check(text, 'test.' + suffix)
                            results.append(result)
                            expected = rule if title is absent or isinstance(title, str) and not title.strip() else (
                                None if isinstance(title, str) else 'PD1004')
                            self.assertEqual([] if expected is None else [expected],
                                             [d.rule_id for d in result.diagnostics])
                            self.assertEqual(expected != 'PD1004', result.ir is not None)
                            if result.ir:
                                self.assertEqual(config, result.ir.config)
                            if expected:
                                diagnostic = result.diagnostics[0]
                                self.assertEqual(path + '/title', diagnostic.path)
                                self.assertEqual('error' if expected == 'PD1004' else 'warning', diagnostic.severity)
                                span = diagnostic.location
                                self.assertEqual(text.splitlines()[span.line - 1], span.excerpt)
                                token = span.excerpt[span.column - 1:]
                                if title is absent:
                                    self.assertTrue(token.startswith('{') if suffix == 'json' else token.startswith('id:'))
                                elif title == '':
                                    self.assertTrue(token.startswith('""') if suffix == 'json' else token.startswith("''"))
                    self.assertEqual([{k: v for k, v in d.items() if k != 'location'} for d in results[0].structured()],
                                     [{k: v for k, v in d.items() if k != 'location'} for d in results[1].structured()])

    def test_collect_all_and_schema_suppression(self):
        config = self.dashboard([self.component('filter'), self.component('chart')])
        config['components'][1]['series'] = 42
        result = check(json.dumps(config))
        self.assertEqual(['PD1004', 'PD2001', 'PD2002'], [d.rule_id for d in result.diagnostics])
        self.assertIsNone(result.ir)
        registry = copy.deepcopy(COMPONENTS)
        del registry['filter']['properties']['title']
        self.assertEqual([], analyze(load(json.dumps(self.dashboard([self.component('filter')])), 'x.json'), registry))
        config['components'] = [{'id': 'x', 'type': 'unknown', 'title': ''}]
        self.assertEqual(['PD1001'], [d.rule_id for d in check(json.dumps(config)).diagnostics])

    def test_warning_only_cli_preserves_success_and_reports_both_formats(self):
        config = self.dashboard([self.component('filter'), self.component('chart')])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'dashboard.json'
            output = Path(directory) / 'diagnostics.json'
            path.write_text(json.dumps(config), encoding='utf-8')
            result = subprocess.run([sys.executable, '-m', 'polydash', str(path),
                                     '--diagnostics-json', str(output)], capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn('warning PD2001', result.stderr)
            self.assertIn('warning PD2002', result.stderr)
            self.assertEqual(check(path.read_text(), path.as_posix()).structured(), json.loads(output.read_text()))
