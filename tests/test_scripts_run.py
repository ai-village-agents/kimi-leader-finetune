"""Regression tests for direct-run scripts."""

import subprocess
import sys
from pathlib import Path


def test_validate_toolkit_runs_as_script():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/validate_toolkit.py"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=True,
    )
    assert "All validations passed" in result.stdout
