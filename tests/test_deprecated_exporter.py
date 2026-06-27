"""
Unit tests for deprecated export_to_pdf.py delegation logic.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

# Import the wrapper module
import scripts.export_to_pdf as deprecated_exporter

class TestDeprecatedExporter(unittest.TestCase):
    @patch("scripts.export_to_pdf.subprocess.run")
    def test_delegation(self, mock_run):
        mock_run.return_value = Mock(returncode=0)
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['scripts/export_to_pdf.py', 'docs/presentation.adoc', '--output', 'output/presentation.pdf']):
            with self.assertRaises(SystemExit) as ctx:
                deprecated_exporter.main()
                
            self.assertEqual(ctx.exception.code, 0)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertIn("export_presentation.py", args[1])
            self.assertIn("--source", args)
            self.assertIn("docs/presentation.adoc", args)

if __name__ == "__main__":
    unittest.main()
