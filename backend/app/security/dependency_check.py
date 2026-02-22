"""Dependency vulnerability scanning."""

import subprocess
import json
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DependencyChecker:
    """Check dependencies for known vulnerabilities."""

    @staticmethod
    def run_safety_check() -> Dict[str, Any]:
        """Run safety check for Python dependencies."""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "vulnerabilities": [],
                    "message": "No vulnerabilities found",
                }

            try:
                data = json.loads(result.stdout)
                vulnerabilities = data if isinstance(data, list) else data.get("vulnerabilities", [])
                return {
                    "status": "warning",
                    "vulnerabilities": vulnerabilities,
                    "message": f"Found {len(vulnerabilities)} vulnerabilities",
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "vulnerabilities": [],
                    "message": "Failed to parse safety output",
                    "raw_output": result.stdout,
                }
        except subprocess.TimeoutExpired:
            logger.error("Safety check timed out")
            return {
                "status": "error",
                "vulnerabilities": [],
                "message": "Safety check timed out",
            }
        except FileNotFoundError:
            logger.error("Safety not installed")
            return {
                "status": "error",
                "vulnerabilities": [],
                "message": "Safety not installed. Run: pip install safety",
            }
        except Exception as e:
            logger.error(f"Error running safety check: {e}")
            return {
                "status": "error",
                "vulnerabilities": [],
                "message": f"Error running safety check: {str(e)}",
            }

    @staticmethod
    def run_bandit_check(target_path: str = "app") -> Dict[str, Any]:
        """Run bandit check for security issues in code."""
        try:
            result = subprocess.run(
                ["bandit", "-r", target_path, "-f", "json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            try:
                data = json.loads(result.stdout)
                issues = data.get("results", [])
                return {
                    "status": "success" if result.returncode == 0 else "warning",
                    "issues": issues,
                    "message": f"Found {len(issues)} security issues",
                    "metrics": data.get("metrics", {}),
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "issues": [],
                    "message": "Failed to parse bandit output",
                    "raw_output": result.stdout,
                }
        except subprocess.TimeoutExpired:
            logger.error("Bandit check timed out")
            return {
                "status": "error",
                "issues": [],
                "message": "Bandit check timed out",
            }
        except FileNotFoundError:
            logger.error("Bandit not installed")
            return {
                "status": "error",
                "issues": [],
                "message": "Bandit not installed. Run: pip install bandit",
            }
        except Exception as e:
            logger.error(f"Error running bandit check: {e}")
            return {
                "status": "error",
                "issues": [],
                "message": f"Error running bandit check: {str(e)}",
            }

    @staticmethod
    def run_detect_secrets_check(target_path: str = "app") -> Dict[str, Any]:
        """Run detect-secrets check for hardcoded secrets."""
        try:
            result = subprocess.run(
                ["detect-secrets", "scan", target_path, "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            try:
                data = json.loads(result.stdout)
                results = data.get("results", {})
                secret_count = sum(len(v) for v in results.values())

                return {
                    "status": "success" if secret_count == 0 else "warning",
                    "secrets_found": secret_count,
                    "results": results,
                    "message": f"Found {secret_count} potential secrets",
                }
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "secrets_found": 0,
                    "results": {},
                    "message": "Failed to parse detect-secrets output",
                    "raw_output": result.stdout,
                }
        except subprocess.TimeoutExpired:
            logger.error("Detect-secrets check timed out")
            return {
                "status": "error",
                "secrets_found": 0,
                "results": {},
                "message": "Detect-secrets check timed out",
            }
        except FileNotFoundError:
            logger.error("Detect-secrets not installed")
            return {
                "status": "error",
                "secrets_found": 0,
                "results": {},
                "message": "Detect-secrets not installed. Run: pip install detect-secrets",
            }
        except Exception as e:
            logger.error(f"Error running detect-secrets check: {e}")
            return {
                "status": "error",
                "secrets_found": 0,
                "results": {},
                "message": f"Error running detect-secrets check: {str(e)}",
            }

    @staticmethod
    def run_all_checks() -> Dict[str, Any]:
        """Run all security checks."""
        return {
            "safety": DependencyChecker.run_safety_check(),
            "bandit": DependencyChecker.run_bandit_check(),
            "detect_secrets": DependencyChecker.run_detect_secrets_check(),
        }
