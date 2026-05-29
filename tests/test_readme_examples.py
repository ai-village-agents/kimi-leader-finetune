"""Regression test: every ```python block in README_TOOLKIT.md must actually run.

This guards against documentation drifting away from the real public API
(e.g. wrong constructor kwargs or renamed methods in copy-paste examples).
"""
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_README = _REPO_ROOT / "README_TOOLKIT.md"

_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _extract_python_blocks(text: str):
    return [m.group(1) for m in _BLOCK_RE.finditer(text)]


def test_readme_has_python_examples():
    blocks = _extract_python_blocks(_README.read_text(encoding="utf-8"))
    assert len(blocks) >= 5, f"expected >=5 python examples, found {len(blocks)}"


def test_readme_python_examples_execute():
    blocks = _extract_python_blocks(_README.read_text(encoding="utf-8"))
    script = "\n".join(blocks)
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        "A README_TOOLKIT.md python example failed to run:\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
