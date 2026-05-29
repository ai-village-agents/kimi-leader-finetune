"""Regression test: protocol validation script works when run directly."""

import subprocess
import sys
from pathlib import Path


def test_validate_protocol_direct_run():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/validate_protocol.py"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Protocol validation passed" in result.stdout
