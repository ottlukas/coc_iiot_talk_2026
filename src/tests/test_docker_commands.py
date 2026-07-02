"""
Unit tests for Docker command execution and CLI configuration detection.
"""

import unittest
from unittest.mock import patch, Mock
import subprocess
from ..exporter.docker_utils import (
    find_docker_compose_cli,
    run_docker_command,
)
from ..exporter.decktape_exporter import get_decktape_connection_settings

class TestDockerCommands(unittest.TestCase):
    @patch("exporter.docker_utils.shutil.which")
    @patch("exporter.docker_utils.subprocess.run")
    def test_find_docker_compose_cli_v2(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/docker"
        
        # Mocking "docker compose version" to succeed
        mock_res = Mock()
        mock_res.returncode = 0
        mock_run.return_value = mock_res
        
        cmd, is_v2 = find_docker_compose_cli()
        
        self.assertTrue(is_v2)
        self.assertEqual(cmd, ["/usr/bin/docker", "compose"])

    @patch("exporter.docker_utils.shutil.which")
    @patch("exporter.docker_utils.subprocess.run")
    def test_find_docker_compose_cli_v1(self, mock_run, mock_which):
        # First call (docker compose version) fails with CalledProcessError
        # Second call (docker-compose version) succeeds
        mock_which.side_effect = lambda x: "/usr/bin/docker-compose" if x == "docker-compose" else "/usr/bin/docker"
        
        mock_res_v2 = Mock()
        mock_res_v2.returncode = 1
        
        mock_res_v1 = Mock()
        mock_res_v1.returncode = 0
        
        mock_run.side_effect = [mock_res_v2, mock_res_v1]
        
        cmd, is_v2 = find_docker_compose_cli()
        
        self.assertFalse(is_v2)
        self.assertEqual(cmd, ["/usr/bin/docker-compose"])

    @patch("exporter.docker_utils.subprocess.run")
    def test_run_docker_command_success(self, mock_run):
        mock_res = Mock()
        mock_res.returncode = 0
        mock_res.stdout = "Successful Docker Run"
        mock_res.stderr = ""
        mock_run.return_value = mock_res
        
        res = run_docker_command(["docker", "ps"])
        
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(res.stdout, "Successful Docker Run")
        self.assertEqual(res.stderr, "")

    @patch("exporter.docker_utils.subprocess.run")
    def test_run_docker_command_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(["docker"], timeout=5, output="partial stdout", stderr="partial stderr")
        
        res = run_docker_command(["docker", "run"], timeout=5)
        
        self.assertEqual(res.exit_code, -1)
        self.assertIn("partial stdout", res.stdout)
        self.assertIn("Command timed out after 5 seconds", res.stderr)

    @patch("exporter.decktape_exporter.platform.system")
    def test_get_decktape_connection_settings_linux(self, mock_system):
        mock_system.return_value = "Linux"
        url, docker_args = get_decktape_connection_settings(4200)
        
        self.assertEqual(url, "http://127.0.0.1:4200/presentation.html")
        self.assertEqual(docker_args, ["--network", "host"])

    @patch("exporter.decktape_exporter.platform.system")
    def test_get_decktape_connection_settings_windows(self, mock_system):
        mock_system.return_value = "Windows"
        url, docker_args = get_decktape_connection_settings(4200)
        
        self.assertEqual(url, "http://host.docker.internal:4200/presentation.html")
        self.assertEqual(docker_args, ["--add-host", "host.docker.internal:host-gateway"])

if __name__ == "__main__":
    unittest.main()
