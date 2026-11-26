"""Tests for scripts/check_secrets.py. Secret-like samples are built at run time, so this file contains none."""

import pytest
from check_secrets import ALLOW_MARKER, check, findings_in_text, forbidden_name

HEX_KEY = "0123456789abcdef" * 4
BYTES = ", ".join(f"0x{i:02x}" for i in range(1, 33))
ZEROS = ", ".join(["0x00"] * 32)


@pytest.mark.parametrize(
    "path",
    [
        "secrets/anything.txt",
        "firmware/secrets/node1.bin",
        ".env",
        ".env.local",
        "prod.env",
        "firmware/Core/Inc/keys.h",
        "firmware/Core/Src/keys.c",
        "keys.json",
        "node_keys.h",
        "data/node_keys.csv",
        "master-key.txt",
        "masterkey.h",
        "secret.h",
        "secrets.json",
        "id_rsa",
        "server.pem",
        "node.key",
    ],
)
def test_secret_file_names_are_rejected(path):
    assert forbidden_name(path)


@pytest.mark.parametrize(
    "path",
    [
        ".env.example",
        "firmware/Core/Inc/keys.example.h",
        "analysis/master_key_derivation.py",
        "firmware/Core/Src/key_derivation.c",
        "docs/key-management.md",
        "scripts/check_secrets.py",
        "data/nodes.csv",
    ],
)
def test_ordinary_file_names_are_accepted(path):
    assert not forbidden_name(path)


@pytest.mark.parametrize(
    "text",
    [
        f"static const uint8_t MASTER_KEY[32] = {{{BYTES}}};",
        f"uint8_t node_key[] =\n{{\n    {BYTES}\n}};",
        f'#define MASTER_KEY "{HEX_KEY}"',
        f'master_key = bytes.fromhex("{HEX_KEY}")',
        f'{{"master_key": "{HEX_KEY}"}}',
        "-----BEGIN " + "PRIVATE KEY-----",
        "token: " + "ghp_" + "a" * 36,
    ],
)
def test_hard_coded_secrets_are_found(text):
    assert list(findings_in_text(text))


@pytest.mark.parametrize(
    "text",
    [
        f"static const uint8_t MASTER_KEY[32] = {{{ZEROS}}};",
        f'#define MASTER_KEY "{"0" * 64}"',
        f"static const uint8_t SYNC_TABLE[32] = {{{BYTES}}};",
        f'commit = "{HEX_KEY}"',
        'key_id = "node-01"',
        f"static const uint8_t TEST_KEY[32] = {{ /* {ALLOW_MARKER} */ {BYTES}}};",
        f"static const uint8_t TEST_KEY[32] = {{{BYTES}}}; // {ALLOW_MARKER}",
    ],
)
def test_harmless_lines_are_accepted(text):
    assert not list(findings_in_text(text))


def test_report_names_the_place_but_not_the_secret(tmp_path):
    (tmp_path / "config.h").write_text(f'\n#define NODE_KEY "{HEX_KEY}"\n', encoding="utf-8")
    problems = check(tmp_path)
    assert problems == ["config.h:2: possible hard-coded key (hex text)"]


def test_export_mode_checks_build_and_environment_folders(tmp_path):
    for folder in ("firmware/build", "env", "venv"):
        (tmp_path / folder).mkdir(parents=True)
        (tmp_path / folder / "config.h").write_text(f'#define NODE_KEY "{HEX_KEY}"\n', encoding="utf-8")
    assert check(tmp_path) == []
    assert len(check(tmp_path, every_file=True)) == 3


def test_utf16_text_is_checked(tmp_path):
    (tmp_path / "config.h").write_bytes(f'#define NODE_KEY "{HEX_KEY}"\n'.encode("utf-16"))
    assert check(tmp_path) == ["config.h:1: possible hard-coded key (hex text)"]


def test_large_text_file_below_the_size_limit_is_checked(tmp_path):
    (tmp_path / "log.txt").write_text("a" * 3_000_000 + f'\n#define NODE_KEY "{HEX_KEY}"\n', encoding="utf-8")
    assert check(tmp_path) == ["log.txt:2: possible hard-coded key (hex text)"]
