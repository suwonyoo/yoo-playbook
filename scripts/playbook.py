#!/usr/bin/env python3
"""Local preparation helpers. No network client, AI calls or automatic submission."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def inside(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError(f'relative path required: {relative}')
    target = (root / p).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f'path escapes workspace: {relative}')
    return target


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def safe_copy(source, target):
    if target.exists() or target.is_symlink():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as dest:
        dest.write(source.read_bytes())
    return True


def initialize(args, workspace):
    available = {p.name: p for p in (ROOT / '.agents/skills').iterdir() if p.is_dir()}
    requested = args.skills or []
    unknown = set(requested) - available.keys()
    if unknown:
        raise ValueError('unknown skills: ' + ', '.join(sorted(unknown)))
    created, kept = [], []
    mappings = [(p, Path('.playbook') / p.name) for p in (ROOT / 'templates').glob('*') if p.is_file()]
    mappings += [(ROOT / 'START_HERE.md', Path('.playbook/START.md'))]
    for name, folder in available.items():
        for p in folder.rglob('*'):
            if p.is_file():
                mappings.append((p, Path('.playbook/skills') / name / p.relative_to(folder)))
                if name in requested:
                    mappings.append((p, Path('.agents/skills') / name / p.relative_to(folder)))
    for name in ['harness.md', 'rules-and-assumptions.md', 'web-playbook.md', 'data-playbook.md', 'troubleshooting.md', 'prompts.md']:
        p = ROOT / 'docs' / name
        mappings.append((p, Path('.playbook/docs') / p.name))
    for source, relative in mappings:
        target = inside(workspace, relative)
        if str(relative) == '.playbook/START.md' and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x') as stream:
                stream.write(source.read_text().replace('.agents/skills/', 'skills/'))
            created.append(str(relative))
            continue
        result = created if safe_copy(source, target) else kept
        result.append(str(relative))
    emit({'created': created, 'kept_existing': kept, 'next': 'Read .playbook/START.md; adapt manifest.json to the actual assignment.'})
    return 0


def doctor(args, workspace):
    emit({'workspace': str(workspace), 'python': sys.version.split()[0],
          'tools': {name: bool(shutil.which(name)) for name in ['git', 'codex', 'node', 'npm', 'python3', 'curl']},
          'project_files': [n for n in ['README.md', 'AGENTS.md', 'package.json', 'pyproject.toml', 'requirements.txt'] if (workspace/n).is_file()],
          'note': 'Availability only. No auth, environment variables, package installation or network checks.'})
    return 0


def run(args, workspace):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', args.id):
        raise ValueError('id must be 1-64 letters, digits, underscore or hyphen')
    if args.timeout <= 0:
        raise ValueError('timeout must be positive')
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        raise ValueError('command required after --')
    tracked = {}
    for item in args.track:
        path = inside(workspace, item)
        if not path.is_file():
            raise ValueError(f'track must name an existing file: {item}')
        tracked[item] = digest(path)
    folder = inside(workspace, Path('.playbook/runs') / args.id)
    folder.mkdir(parents=True, exist_ok=False)
    log = folder/'output.log'
    record = {'id': args.id, 'requirement': args.requirement, 'command': command,
              'started_at': stamp(), 'cwd': str(workspace), 'tracked_before': tracked,
              'timeout_seconds': args.timeout, 'timed_out': False,
              'evidence_scope': 'Process exit and captured output; semantic correctness requires inspection.'}
    start = time.monotonic()
    process = None
    code = 125
    interrupted = False
    try:
        with log.open('xb') as output:
            try:
                process = subprocess.Popen(command, cwd=workspace, stdout=output, stderr=subprocess.STDOUT,
                                           start_new_session=(os.name == 'posix'))
                code = process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                record['timed_out'] = True
                code = 124
            except KeyboardInterrupt:
                interrupted = True
                code = 130
            except OSError as exc:
                record['launch_error'] = str(exc)
                output.write((str(exc)+'\n').encode('utf-8'))
            finally:
                if process is not None and process.poll() is None:
                    if os.name == 'posix':
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    else:
                        process.kill()
                    process.wait()
    finally:
        record.update({'exit_code': code, 'interrupted': interrupted, 'finished_at': stamp(),
                       'duration_seconds': round(time.monotonic()-start, 3),
                       'log_sha256': digest(log) if log.exists() else None})
        (folder/'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    emit(record)
    return code if 0 <= code <= 255 else 1


def audit(args, workspace):
    manifest = json.loads(inside(workspace, args.manifest).read_text())
    if not isinstance(manifest, dict):
        raise ValueError('manifest must be a JSON object')
    errors, warnings = [], []
    files = manifest.get('required_files')
    checks = manifest.get('checks')
    if not isinstance(files, list) or not files:
        errors.append('required_files must be a nonempty list from the actual assignment')
        files = []
    if not isinstance(checks, list) or not checks:
        errors.append('checks must be a nonempty list of requirement/evidence mappings')
        checks = []
    for item in files:
        p = inside(workspace, item)
        if not p.is_file() or p.stat().st_size == 0:
            errors.append(f'missing or empty required file: {item}')
    for check in checks:
        if not isinstance(check, dict):
            errors.append('each check must be an object')
            continue
        rid = check.get('run_id', '')
        req = check.get('requirement', '')
        if not isinstance(rid, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', rid):
            errors.append(f'invalid run_id: {rid}')
            continue
        if not isinstance(req, str) or not req.strip() or not str(check.get('assertion', '')).strip():
            errors.append(f'{rid}: requirement and assertion are required')
        result = inside(workspace, Path('.playbook/runs') / rid / 'result.json')
        if not result.is_file():
            errors.append(f'{rid}: no recorded execution')
            continue
        data = json.loads(result.read_text())
        if not isinstance(data, dict):
            errors.append(f'{rid}: invalid result record')
            continue
        if data.get('id') != rid or data.get('requirement') != req:
            errors.append(f'{rid}: requirement/id mismatch')
        if data.get('exit_code') != 0 or data.get('timed_out') or data.get('interrupted'):
            errors.append(f'{rid}: command did not complete successfully')
        log = inside(workspace, Path('.playbook/runs') / rid / 'output.log')
        if not log.is_file() or digest(log) != data.get('log_sha256'):
            errors.append(f'{rid}: missing or changed output log')
        tracked = data.get('tracked_before')
        if not isinstance(tracked, dict) or not tracked:
            errors.append(f'{rid}: no tracked input/source files; rerun with --track')
            tracked = {}
        for name, old_hash in tracked.items():
            current = inside(workspace, name)
            if not current.is_file() or digest(current) != old_hash:
                errors.append(f'{rid}: tracked file changed or disappeared: {name}')
    warnings.append('Only listed files are tracked. Inspect assertions, manual UI checks, data scope and untracked dependencies yourself.')
    emit({'status': 'NEEDS_ATTENTION' if errors else 'RECORDED_CHECKS_OK', 'errors': errors,
          'warnings': warnings, 'meaning': 'Not an official submission validator, security attestation, or proof that all requirements are satisfied.'})
    return 1 if errors else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    for name, fn in [('init', initialize), ('doctor', doctor), ('run', run), ('audit', audit)]:
        p = subs.add_parser(name)
        p.add_argument('--workspace', default='.')
        p.set_defaults(fn=fn)
        if name == 'init':
            p.add_argument('--skills', nargs='*')
        if name == 'run':
            p.add_argument('--id', required=True)
            p.add_argument('--requirement', required=True)
            p.add_argument('--track', action='append', default=[])
            p.add_argument('--timeout', type=float, default=120)
            p.add_argument('command', nargs=argparse.REMAINDER)
        if name == 'audit':
            p.add_argument('--manifest', default='.playbook/manifest.json')
    args = parser.parse_args(argv)
    workspace = Path(args.workspace).resolve()
    try:
        if not workspace.is_dir():
            raise ValueError('workspace must already exist')
        return args.fn(args, workspace)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
