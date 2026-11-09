import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import common  # noqa: E402

SAMPLE = ("kamb", "bfi10", "ratswd_ges1", "sorgfalt")


def git(root: Path, *args: str) -> str:
    run = subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.org", "-c",
                          "commit.gpgsign=false", *args], cwd=root, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    return run.stdout


@pytest.fixture
def catalogue(tmp_path, monkeypatch) -> Path:
    """A small copy of the catalogue (schema, examples, a few constructs) the tests may change."""
    root = tmp_path / "cat"
    for folder in ("schema", "examples"):
        shutil.copytree(ROOT / folder, root / folder)
    (root / "families").mkdir()
    for key in SAMPLE:
        shutil.copytree(ROOT / "constructs" / key, root / "constructs" / key)
    monkeypatch.setattr(common, "SCHEMA", root / "schema")
    return root


@pytest.fixture
def repo(catalogue) -> Path:
    """The small catalogue as a git repository with one commit on main."""
    git(catalogue, "init", "-q", "-b", "main")
    git(catalogue, "add", "-A")
    git(catalogue, "commit", "-q", "-m", "base")
    return catalogue


def edit_yaml(path: Path, change):
    data = common.load_yaml(path)
    change(data)
    path.write_text(common.dump_yaml(data), encoding="utf-8")
