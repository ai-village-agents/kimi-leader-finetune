"""Shared pytest fixtures for the Agent Coordination Toolkit integration tests.

Owner: Claude Opus 4.8 (review + integration testing).
This scaffold is intentionally lightweight; module-specific fixtures will be
added once Kimi K2.6 pushes the package skeleton and the import path is known.
"""
import sys
from pathlib import Path

import pytest

# Make the repo root importable so `import <package>` works regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the repository root."""
    return REPO_ROOT
