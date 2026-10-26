"""Explicit golden regeneration; always review git diff before committing."""
import json

from .test_compiler import FIXTURES, run_fixture

for path in sorted((FIXTURES / 'golden').glob('*.json')):
    if not path.name.endswith('.expected.json'):
        path.with_suffix('.expected.json').write_text(
            json.dumps(run_fixture(path).structured(), indent=2) + '\n', encoding='utf-8')
        print(path.stem)
