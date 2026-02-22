"""Tests for dependency vulnerability scanning."""

import pytest
from unittest.mock import patch, MagicMock
from app.security.dependency_check import DependencyChecker


class TestSafetyCheck:
    """Test safety check for Python dependencies."""

    @patch("subprocess.run")
    def test_safety_check_no_vulnerabilities(self, mock_run):
        """Test safety check when no vulnerabilities found."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        
        result = DependencyChecker.run_safety_check()
        
        assert result["status"] == "success"
        assert result["vulnerabilities"] == []
        assert "No vulnerabilities" in result["message"]

    @patch("subprocess.run")
    def test_safety_check_with_vulnerabilities(self, mock_run):
        """Test safety check when vulnerabilities found."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='[{"vulnerability": "CVE-2021-1234", "package": "requests"}]',
            stderr="",
        )
        
        result = DependencyChecker.run_safety_check()
        
        assert result["status"] == "warning"
        assert len(result["vulnerabilities"]) > 0

    @patch("subprocess.run")
    def test_safety_check_timeout(self, mock_run):
        """Test safety check timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("safety", 30)
        
        result = DependencyChecker.run_safety_check()
        
        assert result["status"] == "error"
        assert "timed out" in result["message"].lower()

    @patch("subprocess.run")
    def test_safety_check_not_installed(self, mock_run):
        """Test safety check when safety not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        result = DependencyChecker.run_safety_check()
        
        assert result["status"] == "error"
        assert "not installed" in result["message"].lower()

    @patch("subprocess.run")
    def test_safety_check_invalid_json(self, mock_run):
        """Test safety check with invalid JSON output."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="invalid json",
            stderr="",
        )
        
        result = DependencyChecker.run_safety_check()
        
        assert result["status"] == "error"
        assert "Failed to parse" in result["message"]


class TestBanditCheck:
    """Test bandit check for security issues."""

    @patch("subprocess.run")
    def test_bandit_check_no_issues(self, mock_run):
        """Test bandit check when no issues found."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"results": [], "metrics": {}}',
            stderr="",
        )
        
        result = DependencyChecker.run_bandit_check()
        
        assert result["status"] == "success"
        assert result["issues"] == []

    @patch("subprocess.run")
    def test_bandit_check_with_issues(self, mock_run):
        """Test bandit check when issues found."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"results": [{"issue": "Hardcoded password"}], "metrics": {}}',
            stderr="",
        )
        
        result = DependencyChecker.run_bandit_check()
        
        assert result["status"] == "warning"
        assert len(result["issues"]) > 0

    @patch("subprocess.run")
    def test_bandit_check_timeout(self, mock_run):
        """Test bandit check timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("bandit", 60)
        
        result = DependencyChecker.run_bandit_check()
        
        assert result["status"] == "error"
        assert "timed out" in result["message"].lower()

    @patch("subprocess.run")
    def test_bandit_check_not_installed(self, mock_run):
        """Test bandit check when bandit not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        result = DependencyChecker.run_bandit_check()
        
        assert result["status"] == "error"
        assert "not installed" in result["message"].lower()

    @patch("subprocess.run")
    def test_bandit_check_custom_target(self, mock_run):
        """Test bandit check with custom target path."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"results": [], "metrics": {}}',
            stderr="",
        )
        
        result = DependencyChecker.run_bandit_check(target_path="custom/path")
        
        # Verify bandit was called with custom path
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "custom/path" in call_args


class TestDetectSecretsCheck:
    """Test detect-secrets check for hardcoded secrets."""

    @patch("subprocess.run")
    def test_detect_secrets_no_secrets(self, mock_run):
        """Test detect-secrets when no secrets found."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"results": {}}',
            stderr="",
        )
        
        result = DependencyChecker.run_detect_secrets_check()
        
        assert result["status"] == "success"
        assert result["secrets_found"] == 0

    @patch("subprocess.run")
    def test_detect_secrets_with_secrets(self, mock_run):
        """Test detect-secrets when secrets found."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"results": {"app/config.py": [{"type": "AWS Key"}]}}',
            stderr="",
        )
        
        result = DependencyChecker.run_detect_secrets_check()
        
        assert result["status"] == "warning"
        assert result["secrets_found"] > 0

    @patch("subprocess.run")
    def test_detect_secrets_timeout(self, mock_run):
        """Test detect-secrets timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("detect-secrets", 60)
        
        result = DependencyChecker.run_detect_secrets_check()
        
        assert result["status"] == "error"
        assert "timed out" in result["message"].lower()

    @patch("subprocess.run")
    def test_detect_secrets_not_installed(self, mock_run):
        """Test detect-secrets when not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        result = DependencyChecker.run_detect_secrets_check()
        
        assert result["status"] == "error"
        assert "not installed" in result["message"].lower()

    @patch("subprocess.run")
    def test_detect_secrets_multiple_secrets(self, mock_run):
        """Test detect-secrets with multiple secrets."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='{"results": {"app/config.py": [{"type": "AWS Key"}, {"type": "Private Key"}], "app/main.py": [{"type": "API Key"}]}}',
            stderr="",
        )
        
        result = DependencyChecker.run_detect_secrets_check()
        
        assert result["secrets_found"] == 3


class TestRunAllChecks:
    """Test running all security checks."""

    @patch("app.security.dependency_check.DependencyChecker.run_safety_check")
    @patch("app.security.dependency_check.DependencyChecker.run_bandit_check")
    @patch("app.security.dependency_check.DependencyChecker.run_detect_secrets_check")
    def test_run_all_checks(self, mock_detect, mock_bandit, mock_safety):
        """Test running all checks together."""
        mock_safety.return_value = {"status": "success", "vulnerabilities": []}
        mock_bandit.return_value = {"status": "success", "issues": []}
        mock_detect.return_value = {"status": "success", "secrets_found": 0}
        
        result = DependencyChecker.run_all_checks()
        
        assert "safety" in result
        assert "bandit" in result
        assert "detect_secrets" in result
        assert result["safety"]["status"] == "success"
        assert result["bandit"]["status"] == "success"
        assert result["detect_secrets"]["status"] == "success"

    @patch("app.security.dependency_check.DependencyChecker.run_safety_check")
    @patch("app.security.dependency_check.DependencyChecker.run_bandit_check")
    @patch("app.security.dependency_check.DependencyChecker.run_detect_secrets_check")
    def test_run_all_checks_with_issues(self, mock_detect, mock_bandit, mock_safety):
        """Test running all checks when issues found."""
        mock_safety.return_value = {"status": "warning", "vulnerabilities": [{"id": "1"}]}
        mock_bandit.return_value = {"status": "warning", "issues": [{"issue": "test"}]}
        mock_detect.return_value = {"status": "warning", "secrets_found": 1}
        
        result = DependencyChecker.run_all_checks()
        
        assert result["safety"]["status"] == "warning"
        assert result["bandit"]["status"] == "warning"
        assert result["detect_secrets"]["status"] == "warning"


class TestDependencyCheckIntegration:
    """Integration tests for dependency checking."""

    def test_dependency_checker_methods_exist(self):
        """Test that all required methods exist."""
        assert hasattr(DependencyChecker, "run_safety_check")
        assert hasattr(DependencyChecker, "run_bandit_check")
        assert hasattr(DependencyChecker, "run_detect_secrets_check")
        assert hasattr(DependencyChecker, "run_all_checks")

    def test_dependency_checker_methods_are_static(self):
        """Test that methods are static."""
        assert callable(DependencyChecker.run_safety_check)
        assert callable(DependencyChecker.run_bandit_check)
        assert callable(DependencyChecker.run_detect_secrets_check)
        assert callable(DependencyChecker.run_all_checks)

    @patch("subprocess.run")
    def test_error_handling_consistency(self, mock_run):
        """Test that error handling is consistent across methods."""
        mock_run.side_effect = Exception("Test error")
        
        safety_result = DependencyChecker.run_safety_check()
        bandit_result = DependencyChecker.run_bandit_check()
        detect_result = DependencyChecker.run_detect_secrets_check()
        
        # All should have error status
        assert safety_result["status"] == "error"
        assert bandit_result["status"] == "error"
        assert detect_result["status"] == "error"
