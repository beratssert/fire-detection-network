#!/usr/bin/env python3
"""Reject files larger than MAX_FILE_BYTES (check_secrets.py). A large file stays in the history after deletion.

Usage: check_file_size.py [DIRECTORY]. Checks the same files as check_secrets.py, also with CHECK_EXPORT=1. If a
measurement really needs a larger file, raise the limit in a reviewed pull request instead of skipping the check.
"""

import os
import sys
from pathlib import Path

from check_secrets import MAX_FILE_BYTES, repository_files


def check(root, max_bytes=MAX_FILE_BYTES, every_file=False):
    problems = []
    for relative in repository_files(root, every_file):
        file = root / relative
        if file.is_file() and not file.is_symlink() and file.stat().st_size > max_bytes:
            size = file.stat().st_size / (1024 * 1024)
            problems.append(f"{relative}: {size:.1f} MiB is larger than the limit of {max_bytes / (1024 * 1024):g} MiB")
    return problems


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems = check(root.resolve(), every_file=os.environ.get("CHECK_EXPORT") == "1")
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print("File size check failed (scripts/check_file_size.py).", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
