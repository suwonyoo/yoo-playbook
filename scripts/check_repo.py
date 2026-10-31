#!/usr/bin/env python3
"""Check self-contained links, skill metadata and pinned research catalog."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
errors = []
skills = sorted((root/'.agents/skills').glob('*/SKILL.md'))
names = set()
for path in skills:
    text = path.read_text()
    match = re.match(r'---\nname: ([a-z0-9-]+)\ndescription: (.+)\n---\n', text)
    if not match or match[1] != path.parent.name:
        errors.append(f'invalid metadata: {path.relative_to(root)}')
        continue
    if match[1] in names:
        errors.append(f'duplicate skill name: {match[1]}')
    names.add(match[1])
for path in root.rglob('*.md'):
    if '.git' in path.parts or '.playbook' in path.parts:
        continue
    text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    for target in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)', text):
        if target.startswith(('https://', 'http://', '#', 'mailto:')):
            continue
        file = unquote(target.split('#')[0])
        if not (path.parent/file).exists():
            errors.append(f'broken link: {path.relative_to(root)} -> {target}')
catalog = json.loads((root/'sources/catalog.json').read_text())
for source in catalog['repositories']:
    if not re.fullmatch(r'[a-f0-9]{40}', source['commit']):
        errors.append(f'unpinned source: {source["repository"]}')
    if not source['reviewed_paths'] or not source['decision']:
        errors.append(f'unreviewed source entry: {source["repository"]}')
print(json.dumps({'skills': len(skills), 'sources': len(catalog['repositories']), 'errors': errors}, ensure_ascii=False, indent=2))
sys.exit(bool(errors))
