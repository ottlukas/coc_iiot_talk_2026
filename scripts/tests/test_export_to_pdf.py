import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.export_to_pdf import (
    infer_output_pdf_path,
    main,
    run_puppeteer_export,
    validate_input_file,
)


class TestExportToPdf(unittest.TestCase):
    def test_infer_output_pdf_path(self):
        output_path = infer_output_pdf_path('docs/presentation.adoc')
        self.assertEqual(
            output_path,
            Path(__file__).resolve().parents[2] / 'docs' / 'exports' / 'presentation.pdf',
        )

    def test_missing_input_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            validate_input_file(Path('docs/nonexistent.adoc'))

    @mock.patch('scripts.export_to_pdf.run_puppeteer_export')
    def test_valid_input_calls_puppeteer_helper(self, mock_export):
        with tempfile.TemporaryDirectory() as tmpdir:
            adoc_path = Path(tmpdir) / 'presentation.adoc'
            output_dir = Path(tmpdir) / 'docs' / 'exports'
            output_pdf = output_dir / 'presentation.pdf'
            adoc_path.parent.mkdir(parents=True, exist_ok=True)
            adoc_path.write_text('= Test Presentation')

            def create_output(path, url='http://localhost:4200'):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('%PDF-1.4')

            mock_export.side_effect = create_output
            result = main([str(adoc_path), '--output', str(output_pdf)])

            self.assertEqual(result, 0)
            mock_export.assert_called_once_with(output_pdf, 'http://localhost:4200')
            self.assertTrue(output_pdf.exists())

    @mock.patch('scripts.export_to_pdf.run_puppeteer_export')
    def test_invalid_output_directory_created(self, mock_export):
        with tempfile.TemporaryDirectory() as tmpdir:
            adoc_path = Path(tmpdir) / 'presentation.adoc'
            adoc_path.write_text('= Test Presentation')
            output_pdf = Path(tmpdir) / 'docs' / 'exports' / 'presentation.pdf'
            self.assertFalse(output_pdf.parent.exists())

            def create_output(path, url='http://localhost:4200'):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('%PDF-1.4')

            mock_export.side_effect = create_output
            main([str(adoc_path), '--output', str(output_pdf)])

            self.assertTrue(output_pdf.parent.exists())
            mock_export.assert_called_once_with(output_pdf, 'http://localhost:4200')

    @mock.patch('scripts.export_to_pdf.run_puppeteer_export')
    def test_relative_input_path_works_from_subdirectory(self, mock_export):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / 'repo'
            scripts_dir = repo_root / 'scripts'
            docs_dir = repo_root / 'docs'
            venv_dir = repo_root / '.venv'
            scripts_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)
            venv_dir.mkdir(parents=True)

            adoc_path = docs_dir / 'presentation.adoc'
            adoc_path.write_text('= Test Presentation')

            helper_script = scripts_dir / 'puppeteer_export.js'
            helper_script.write_text('')

            with mock.patch('scripts.export_to_pdf.ROOT_DIR', repo_root):
                with mock.patch('scripts.export_to_pdf.HELPER_SCRIPT', helper_script):
                    def create_output(path, url='http://localhost:4200'):
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text('%PDF-1.4')

                    mock_export.side_effect = create_output
                    current_dir = Path.cwd()
                    os.chdir(venv_dir)
                    try:
                        result = main(['../docs/presentation.adoc'])
                    finally:
                        os.chdir(current_dir)

            self.assertEqual(result, 0)
            expected_output = repo_root / 'docs' / 'exports' / 'presentation.pdf'
            mock_export.assert_called_once_with(expected_output, 'http://localhost:4200')
            self.assertTrue(expected_output.exists())

    @mock.patch('scripts.export_to_pdf.urllib.request.urlopen')
    @mock.patch('scripts.export_to_pdf.find_running_presentation_container', return_value=('container-id', True))
    @mock.patch('scripts.export_to_pdf.find_docker_cli', return_value=(['docker', 'compose'], True))
    @mock.patch('scripts.export_to_pdf.subprocess.run')
    def test_run_puppeteer_export_uses_docker_compose(self, mock_run, mock_find_cli, mock_find_container, mock_urlopen):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            helper_script = repo_root / 'scripts' / 'puppeteer_export.js'
            docs_dir = repo_root / 'docs'
            output_pdf = docs_dir / 'exports' / 'presentation.pdf'
            helper_script.parent.mkdir(parents=True, exist_ok=True)
            helper_script.write_text('')
            docs_dir.mkdir(parents=True, exist_ok=True)

            mock_urlopen.return_value.__enter__.return_value.status = 200
            with mock.patch('scripts.export_to_pdf.HELPER_SCRIPT', helper_script):
                with mock.patch('scripts.export_to_pdf.ROOT_DIR', repo_root):
                    with mock.patch('scripts.export_to_pdf.COMPOSE_FILE', repo_root / 'docker' / 'dev' / 'docker-compose.yml'):
                        mock_run.return_value = mock.Mock(returncode=0)
                        run_puppeteer_export(output_pdf, url='http://localhost:4200')

            mock_run.assert_called_once()
            command = mock_run.call_args[0][0]
            self.assertEqual(command[:5], ['docker', 'compose', '-f', str(repo_root / 'docker' / 'dev' / 'docker-compose.yml'), 'exec'])
            self.assertIn('node', command)
            self.assertIn('--url', command)
            self.assertIn('http://localhost:4200', command)
            self.assertIn('--output', command)
            self.assertIn(str(Path('/app/docs/exports/presentation.pdf')), command)

    @mock.patch('scripts.export_to_pdf.urllib.request.urlopen')
    @mock.patch('scripts.export_to_pdf.find_docker_cli', side_effect=RuntimeError('Docker is not available.'))
    def test_run_puppeteer_export_fails_when_docker_unavailable(self, mock_find_cli, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.status = 200
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = Path(tmpdir) / 'docs' / 'exports' / 'presentation.pdf'
            with self.assertRaises(RuntimeError) as ctx:
                run_puppeteer_export(output_pdf, url='http://localhost:4200')

        self.assertIn('Docker is not available', str(ctx.exception))

    def test_main_fails_when_output_file_not_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            adoc_path = Path(tmpdir) / 'presentation.adoc'
            adoc_path.write_text('= Test Presentation')
            output_pdf = Path(tmpdir) / 'docs' / 'exports' / 'presentation.pdf'

            with mock.patch('scripts.export_to_pdf.run_puppeteer_export'):
                with self.assertRaises(RuntimeError) as ctx:
                    main([str(adoc_path), '--output', str(output_pdf)])

            self.assertIn('Export did not create the expected PDF file', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
