"""Tests of the commit message check and, end to end in throw-away repositories, of the pre-push hook.

The pre-commit hook is not installed there: it would run these tests again. The pre-commit hook sets SKIP_HOOK_TESTS=1
when a commit does not change .githooks/ or scripts/, because these tests take a few seconds; CI always runs them.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("SKIP_HOOK_TESTS") == "1", reason="hooks and scripts unchanged")

REPO = Path(__file__).resolve().parents[2]
BASH = shutil.which("bash")  # on Windows the bash of Git for Windows, which comes first in PATH in Git Bash
HEX_KEY = "0123456789abcdef" * 4
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CHECK_EXPORT"}
ENV.update(
    PYTHON=sys.executable,
    GIT_AUTHOR_NAME="t",
    GIT_AUTHOR_EMAIL="t@users.noreply.github.com",
    GIT_COMMITTER_NAME="t",
    GIT_COMMITTER_EMAIL="t@users.noreply.github.com",
    GIT_CONFIG_GLOBAL=os.devnull,
    GIT_CONFIG_NOSYSTEM="1",
)


def run(*args, cwd, check=True):
    return subprocess.run(args, cwd=cwd, env=ENV, check=check, capture_output=True, text=True)


def check_message(*args):
    return run(BASH, str(REPO / "scripts" / "check-commit-msg.sh"), *args, cwd=REPO, check=False)


@pytest.mark.parametrize("message", ["[DOCS] Fix typo", "fixup! [DOCS] Fix typo", "squash! [WP1] Send frame"])
def test_local_check_accepts_valid_and_fixup_messages(message):
    assert check_message("--allow-fixup", message).returncode == 0


def test_local_check_rejects_untagged_message():
    assert check_message("--allow-fixup", "Fix typo").returncode != 0


@pytest.mark.parametrize("message", ["fixup! [DOCS] Fix typo", "amend! [DOCS] Fix typo"])
def test_ci_check_rejects_fixup(message):
    result = check_message(message)
    assert result.returncode != 0
    assert "autosquash" in result.stderr


@pytest.fixture(scope="module")
def template(tmp_path_factory):
    """A clone with the pre-push hook, one commit that is not pushed yet and an empty bare repository as "origin"."""
    base = tmp_path_factory.mktemp("template")
    work = base / "work"
    run("git", "init", "-q", "--bare", "remote.git", cwd=base)
    run("git", "init", "-q", "work", cwd=base)
    shutil.copytree(REPO / "scripts", work / "scripts", ignore=shutil.ignore_patterns("__pycache__", "tests"))
    (work / ".hooks").mkdir()
    shutil.copy2(REPO / ".githooks" / "pre-push", work / ".hooks" / "pre-push")
    for command in (
        ("git", "config", "core.hooksPath", ".hooks"),
        ("git", "config", "core.autocrlf", "false"),
        ("git", "remote", "add", "origin", "../remote.git"),
        ("git", "add", "scripts"),
        ("git", "commit", "-q", "-m", "[CI] Add scripts"),
    ):
        run(*command, cwd=work)
    return base


@pytest.fixture
def repo(template, tmp_path):
    shutil.copytree(template, tmp_path, dirs_exist_ok=True)
    work = tmp_path / "work"

    def git(*args, check=True):
        return run("git", *args, cwd=work, check=check)

    git.work = work
    return git


def commit_file(git, path, content, message):
    file = git.work / path
    file.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        file.write_bytes(content)
    else:
        file.write_text(content, encoding="utf-8")
    git("add", "-f", path)
    git("commit", "-q", "--no-verify", "-m", message)


def push(git, *options):
    return git("push", "-q", *options, "origin", "HEAD:refs/heads/main", check=False)


def test_pre_push_accepts_clean_commits(repo):
    commit_file(repo, "docs/a.md", "text\n", "[DOCS] Add a")
    assert push(repo).returncode == 0


def test_pre_push_finds_key_that_a_later_commit_removed(repo):
    commit_file(repo, "config.h", f'#define NODE_KEY "{HEX_KEY}"\n', "[WP3] Add key")
    commit_file(repo, "config.h", "#define NODE_KEY_FILE 1\n", "[WP3] Remove key")
    result = push(repo)
    assert result.returncode != 0
    assert "[WP3] Add key" in result.stderr
    assert HEX_KEY not in result.stderr


def test_pre_push_rejects_reserved_name_and_large_file(repo):
    commit_file(repo, "secrets/node1.txt", "x\n", "[WP3] Add node key")
    commit_file(repo, "data/raw.bin", b"\0" * (5 * 1024 * 1024 + 1), "[DATA] Add raw file")
    result = push(repo)
    assert result.returncode != 0
    assert "secrets/node1.txt" in result.stderr
    assert "data/raw.bin" in result.stderr


def test_pre_push_checks_only_commits_that_the_remote_lacks(repo):
    commit_file(repo, "secrets/node1.txt", "x\n", "[WP3] Add node key")
    assert push(repo, "--no-verify").returncode == 0
    commit_file(repo, "docs/a.md", "text\n", "[DOCS] Add a")
    assert push(repo).returncode == 0


def test_pre_push_checks_build_folders(repo):
    commit_file(repo, "firmware/build/config.h", f'#define NODE_KEY "{HEX_KEY}"\n', "[WP3] Add generated config")
    result = push(repo)
    assert result.returncode != 0
    assert "firmware/build/config.h" in result.stderr


def test_pre_push_stops_when_a_check_cannot_run(repo):
    """An unknown commit makes git rev-list fail; the hook must stop the push instead of letting it through."""
    line = f"refs/heads/main {'a' * 40} refs/heads/main {'0' * 40}\n"
    hook = str(repo.work / ".hooks" / "pre-push")
    result = subprocess.run(
        [BASH, hook, "origin", "../remote.git"], cwd=repo.work, env=ENV, input=line, capture_output=True, text=True
    )
    assert result.returncode != 0


def check_frozen(git, base):
    return run(BASH, "scripts/check-frozen.sh", base, "HEAD", cwd=git.work, check=False)


def test_frozen_check_accepts_new_test_run(repo):
    commit_file(repo, "poster/params.py", "x = 1\n", "[MODEL] Add archive")
    commit_file(repo, "data/runs/r1/frames.csv", "a\n", "[DATA] Add run 1")
    base = repo("rev-parse", "HEAD").stdout.strip()
    commit_file(repo, "data/runs/r2/frames.csv", "a\n", "[DATA] Add run 2")
    assert check_frozen(repo, base).returncode == 0


@pytest.mark.parametrize("path", ["poster/params.py", "data/runs/r1/frames.csv"])
def test_frozen_check_rejects_changed_archive_or_raw_data(repo, path):
    commit_file(repo, "poster/params.py", "x = 1\n", "[MODEL] Add archive")
    commit_file(repo, "data/runs/r1/frames.csv", "a\n", "[DATA] Add run 1")
    base = repo("rev-parse", "HEAD").stdout.strip()
    commit_file(repo, path, "changed\n", "[DATA] Change a frozen file")
    result = check_frozen(repo, base)
    assert result.returncode != 0
    assert path in result.stderr
