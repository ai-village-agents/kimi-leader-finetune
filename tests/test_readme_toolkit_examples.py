"""Execute README_TOOLKIT.md Python examples to prevent docs/API drift."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


def test_readme_toolkit_python_examples_run(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    readme = repo_root / "README_TOOLKIT.md"
    blocks = re.findall(r"```python\n(.*?)\n```", readme.read_text(), re.S)
    assert blocks, "README_TOOLKIT.md should contain Python examples"

    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )

    for idx, code in enumerate(blocks, start=1):
        script = tmp_path / f"readme_block_{idx}.py"
        script.write_text(code)
        subprocess.run(
            [sys.executable, str(script)],
            cwd=repo_root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
