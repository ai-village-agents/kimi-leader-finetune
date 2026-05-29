"""Smoke test: every example script runs cleanly via `python examples/<name>.py`.

Guards against the path-bootstrap regression where a demo imports
ai_village_toolkit but the repo root isn't on sys.path when run directly.

Authored by Claude Opus 4.8 (review + integration role).
"""
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = sorted(
    p for p in (REPO_ROOT / "examples").glob("*.py")
    if p.name != "__init__.py"
)


@pytest.mark.parametrize("script", EXAMPLES, ids=[p.name for p in EXAMPLES])
def test_example_runs_directly(script):
    # Run from repo root exactly as the docs instruct: python examples/<name>.py
    result = subprocess.run(
        [sys.executable, str(script.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"{script.name} failed:\n{result.stderr[-800:]}"
    )
    assert result.stdout.strip(), f"{script.name} produced no output"
