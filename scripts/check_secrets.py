#!/usr/bin/env python3
"""Reject files and lines that look like secrets (see docs/key-management.md).

Usage: check_secrets.py [DIRECTORY]. Checks DIRECTORY, by default the directory above this script: in a git clone every
file that is tracked or could be added (ignored files are skipped), otherwise every file except build and environment
folders. The git hooks check an export of the files to be committed and set CHECK_EXPORT=1, so that every file of the
export is checked, also in folders such as build/. This is a safety net for
common mistakes, not a proof that no secret is present. A false alarm in a source file (for example a published test
vector) is silenced with the comment "secret-scan: allow" on the line where the reported text starts.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ALLOW_MARKER = "secret-scan: allow"
SKIP_DIRS = {".git", ".venv", "venv", "env", "build", "__pycache__", ".pytest_cache", ".ruff_cache"}
# Larger files are rejected by check_file_size.py, so every file that may be committed is scanned.
MAX_FILE_BYTES = 5 * 1024 * 1024
UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")

FORBIDDEN_NAMES = (
    r".*\.(key|pem|p12|pfx)",
    r"\.env(\..*)?|.*\.env",
    r"id_(rsa|dsa|ecdsa|ed25519)",
    r"(keys?|secrets?|((master|node|device)[-_]?keys?))\.(h|c|txt|json|csv|bin|hex|ya?ml|toml|ini)",
    r"secrets\..*",
)

# The look-behind lets a match start only at the start of an identifier; without it a long word takes quadratic time.
KEY_NAME = r"(?<![A-Za-z0-9_])[A-Za-z0-9_]*(?:key|secret|master)[A-Za-z0-9_]*"
CONTENT_RULES = (
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("access token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16})\b")),
    (
        "hard-coded key (hex text)",
        re.compile(
            KEY_NAME + r"""["']?(?:\s*\[[^\]\n]*\])*\s*(?:[=:]\s*|\s+)(?:bytes\.fromhex\(\s*|b)?"""
            r"""["'](?P<value>[0-9a-f]{32,})["']""",
            re.IGNORECASE,
        ),
    ),
    (
        "hard-coded key (byte array)",
        re.compile(
            KEY_NAME + r"(?:\s*\[[^\]]*\])*\s*=\s*[{\[(]\s*(?P<value>(?:0x[0-9a-f]{1,2}\s*,\s*){7,}"
            r"(?:0x[0-9a-f]{1,2})?)",
            re.IGNORECASE,
        ),
    ),
)


def forbidden_name(path):
    """Return True if a file with this repository path must never be committed."""
    parts = path.lower().split("/")
    name = parts[-1]
    if "secrets" in parts[:-1]:
        return True
    if ".example" in name:
        return False
    return any(re.fullmatch(pattern, name) for pattern in FORBIDDEN_NAMES)


def is_placeholder(value):
    """All-zero values are allowed, for example in keys.example.h."""
    return set(re.sub(r"0x|[\s,]", "", value.lower())) <= {"0"}


def findings_in_text(text):
    """Yield (line number, rule name) for every suspicious place. The secret itself is never returned."""
    lines = text.split("\n")
    for rule, pattern in CONTENT_RULES:
        for match in pattern.finditer(text):
            value = match.groupdict().get("value")
            if value is not None and is_placeholder(value):
                continue
            number = text.count("\n", 0, match.start()) + 1
            if ALLOW_MARKER not in lines[number - 1]:
                yield number, rule


def repository_files(root, every_file=False):
    """Paths relative to root. every_file: root is an export of tracked files, so no folder is skipped."""
    if (root / ".git").exists():
        command = ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
        output = subprocess.run(command, check=True, capture_output=True).stdout
        return sorted(set(filter(None, output.decode("utf-8").split("\0"))))
    found = []
    for directory, subdirs, names in os.walk(root):
        if not every_file:
            subdirs[:] = [d for d in subdirs if d not in SKIP_DIRS]
        found += [(Path(directory) / n).relative_to(root).as_posix() for n in names]
    return sorted(found)


def decode(data):
    """Text of a file, or None for a binary file. UTF-16 text (with a byte order mark) is decoded too."""
    if data.startswith(UTF16_BOMS):
        return data.decode("utf-16", errors="replace")
    if b"\0" in data:
        return None
    return data.decode("utf-8", errors="replace")


def check(root, every_file=False):
    problems = []
    for relative in repository_files(root, every_file):
        file = root / relative
        if not file.is_file():
            continue
        if forbidden_name(relative):
            problems.append(f"{relative}: this file name is reserved for secrets")
            continue
        if file.stat().st_size > MAX_FILE_BYTES:
            continue
        text = decode(file.read_bytes())
        if text is None:
            continue
        problems += [f"{relative}:{number}: possible {rule}" for number, rule in findings_in_text(text)]
    return problems


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems = check(root.resolve(), every_file=os.environ.get("CHECK_EXPORT") == "1")
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print("Secret check failed. See docs/key-management.md.", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
