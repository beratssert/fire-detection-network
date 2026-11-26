"""Tests for scripts/check_file_size.py."""

from check_file_size import check


def test_small_files_are_accepted(tmp_path):
    (tmp_path / "run.csv").write_bytes(b"x" * 1000)
    assert check(tmp_path, max_bytes=1000) == []


def test_large_file_is_reported_with_its_path(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "raw.bin").write_bytes(b"x" * 1001)
    problems = check(tmp_path, max_bytes=1000)
    assert len(problems) == 1
    assert problems[0].startswith("data/raw.bin: ")
