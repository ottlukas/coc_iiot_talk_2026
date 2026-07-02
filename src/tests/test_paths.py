"""
Unit tests for path resolution and Docker volume path formatting.
"""

import unittest
from pathlib import Path
from export_presentation import resolve_path, ROOT_DIR
from ..exporter.docker_utils import format_docker_volume_path

class TestPaths(unittest.TestCase):
    def test_resolve_path_absolute(self):
        abs_path = Path("/some/absolute/path").resolve()
        res = resolve_path(str(abs_path))
        self.assertEqual(res, abs_path)

    def test_resolve_path_relative_fallback(self):
        # Path not in CWD, should fall back to relative to ROOT_DIR
        res = resolve_path("docs/presentation.adoc")
        expected = (ROOT_DIR / "docs/presentation.adoc").resolve()
        self.assertEqual(res, expected)

    def test_format_docker_volume_path(self):
        # Verifies that it converts backslashes to forward slashes and resolves path
        p = Path("docs/../docs/theme/apache.css")
        formatted = format_docker_volume_path(p)
        self.assertNotIn("\\", formatted)
        self.assertIn("/", formatted)
        self.assertTrue(Path(formatted).is_file())

if __name__ == "__main__":
    unittest.main()
