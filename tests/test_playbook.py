import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/playbook.py'


class PlaybookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws = Path(self.temp.name)
        (self.ws/'source.py').write_text('VALUE = 1\n')

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, action, *args):
        return subprocess.run([sys.executable, str(SCRIPT), action, '--workspace', str(self.ws), *args],
                              capture_output=True, text=True)

    def execution(self, ident='V-001', program='print("ok")', *extra):
        return self.cli('run', '--id', ident, '--requirement', 'R-001', '--track', 'source.py',
                        *extra, '--', sys.executable, '-c', program)

    def manifest(self):
        (self.ws/'manifest.json').write_text(json.dumps({'required_files': ['source.py'], 'checks': [
            {'requirement': 'R-001', 'run_id': 'V-001', 'assertion': 'Observed output'}]}))

    def audit(self):
        return self.cli('audit', '--manifest', 'manifest.json')

    def test_init_preserves_existing_files_and_supports_selected_skills(self):
        (self.ws/'AGENTS.md').write_text('existing instructions')
        self.assertEqual(self.cli('init', '--skills', 'task-intake').returncode, 0)
        note = self.ws/'.playbook/requirements.md'
        note.write_text('real work')
        self.assertEqual(self.cli('init').returncode, 0)
        self.assertEqual(note.read_text(), 'real work')
        self.assertEqual((self.ws/'AGENTS.md').read_text(), 'existing instructions')
        self.assertTrue((self.ws/'.agents/skills/task-intake/SKILL.md').is_file())
        self.assertFalse((self.ws/'.agents/skills/web-mvp').exists())

    def test_unknown_skill_rejected_before_writing(self):
        self.assertEqual(self.cli('init', '--skills', '../bad').returncode, 2)
        self.assertFalse((self.ws/'.playbook').exists())

    def test_success_has_real_output_and_hash(self):
        result = self.execution()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        log = self.ws/'.playbook/runs/V-001/output.log'
        self.assertEqual(log.read_text(), 'ok\n')
        self.assertEqual(data['log_sha256'], hashlib.sha256(log.read_bytes()).hexdigest())
        self.manifest()
        self.assertEqual(self.audit().returncode, 0)

    def test_failed_command_cannot_pass_audit(self):
        self.assertEqual(self.execution(program='raise SystemExit(7)').returncode, 7)
        self.manifest()
        self.assertEqual(self.audit().returncode, 1)

    def test_timeout_recorded_as_failure(self):
        result = self.execution('V-001', 'import time; time.sleep(10)', '--timeout', '0.1')
        self.assertEqual(result.returncode, 124)
        self.assertTrue(json.loads(result.stdout)['timed_out'])
        self.manifest()
        self.assertEqual(self.audit().returncode, 1)

    def test_missing_executable_is_recorded(self):
        result = self.cli('run', '--id', 'V-001', '--requirement', 'R-001', '--', 'no-such-command-playbook')
        self.assertEqual(result.returncode, 125)
        self.assertIn('launch_error', json.loads(result.stdout))

    def test_duplicate_id_does_not_overwrite_evidence(self):
        self.execution()
        log = self.ws/'.playbook/runs/V-001/output.log'
        before = log.read_bytes()
        self.assertEqual(self.execution(program='print("replacement")').returncode, 2)
        self.assertEqual(log.read_bytes(), before)

    def test_changed_tracked_source_rejects_old_evidence(self):
        self.execution()
        self.manifest()
        (self.ws/'source.py').write_text('VALUE = 2\n')
        result = self.audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('changed or disappeared', result.stdout)

    def test_changed_log_rejects_evidence(self):
        self.execution()
        self.manifest()
        (self.ws/'.playbook/runs/V-001/output.log').write_text('fake success')
        self.assertEqual(self.audit().returncode, 1)

    def test_empty_manifest_and_missing_required_file_fail(self):
        self.cli('init')
        self.assertEqual(self.cli('audit').returncode, 1)
        self.execution()
        self.manifest()
        (self.ws/'source.py').unlink()
        self.assertEqual(self.audit().returncode, 1)

    def test_traversal_is_rejected(self):
        result = self.cli('run', '--id', '../outside', '--requirement', 'R-001', '--', 'echo', 'bad')
        self.assertEqual(result.returncode, 2)
        (self.ws/'manifest.json').write_text(json.dumps({'required_files': ['../outside'], 'checks': []}))
        self.assertEqual(self.audit().returncode, 2)

    def test_external_symlink_cannot_receive_init_writes(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            (self.ws/'.playbook').symlink_to(elsewhere, target_is_directory=True)
            self.assertEqual(self.cli('init').returncode, 2)
            self.assertEqual(list(Path(elsewhere).iterdir()), [])

    def test_shell_metacharacters_are_literal_arguments(self):
        value = '$(touch injected); $HOME'
        result = self.cli('run', '--id', 'V-001', '--requirement', 'R-001', '--', sys.executable,
                          '-c', 'import sys; print(sys.argv[1])', value)
        self.assertEqual(result.returncode, 0)
        self.assertEqual((self.ws/'.playbook/runs/V-001/output.log').read_text().strip(), value)
        self.assertFalse((self.ws/'injected').exists())

    def test_untracked_execution_and_wrong_requirement_cannot_pass(self):
        self.cli('run', '--id', 'V-001', '--requirement', 'R-OTHER', '--', sys.executable, '-c', 'print(1)')
        self.manifest()
        result = self.audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('mismatch', result.stdout)
        self.assertIn('no tracked', result.stdout)

    def test_invalid_records_are_reported_without_traceback(self):
        (self.ws/'manifest.json').write_text('[]')
        result = self.audit()
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        self.execution()
        self.manifest()
        (self.ws/'.playbook/runs/V-001/result.json').write_text('[]')
        result = self.audit()
        self.assertEqual(result.returncode, 1)
        self.assertIn('invalid result record', result.stdout)


if __name__ == '__main__':
    unittest.main()
