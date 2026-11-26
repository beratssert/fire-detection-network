# Keys and secrets

The repository is meant to be public. Anything that is committed, attached to a release or uploaded as a CI artifact has
to be treated as public. The design of the keys is described in [frame-format.md](frame-format.md#security-fields).

## Rules

1. **One place.** Real keys, tokens and every file generated from them live only in the folder `secrets/` of a local
   clone. Git ignores it. It does not exist after cloning; create it when needed.
2. **No real key in the source.** Code reads keys from a file in `secrets/` or from data written to the board. What the
   repository may contain is a template with all-zero keys, with `.example` in its name (for example `keys.example.h`).
3. **No binary with a real key leaves the team.** A key that is compiled into a firmware image can be read from that
   image. CI builds firmware only with the all-zero template. Binaries built with real keys are not attached to
   releases, CI artifacts, issues or chats.
4. **No key in measurement data or logs.** `data/` stores the `key_id`, never the key. The logger does not print keys.
5. **No key by chat or e-mail.** Share the master key through a password manager or hand it over in person.
6. **Test keys are not real keys.** Unit tests use published test vectors or values made for the test. Such a value is
   never loaded onto a board that is used for measurements.

## Creating a master key

From the repository root, after `bash scripts/setup.sh` (use `.venv/Scripts/python.exe` on Windows):

```bash
mkdir -p secrets
.venv/bin/python -c "import secrets; open('secrets/master.key', 'x').write(secrets.token_hex(32))"
```

The command refuses to overwrite an existing key.

## If a key was committed or published

Deleting the file or rewriting the history is not enough, because copies may already exist.

1. Create a new master key and derive new node keys.
2. Load the new keys onto every board and the gateway.
3. Revoke a leaked token at the service that issued it.
4. Tell the team, and note which test runs used the old key.

## What the automatic checks do

| Protection | When | Limit |
|---|---|---|
| `.gitignore` | `git add` | only known file names; `git add -f` overrides it |
| `scripts/check_secrets.py` | pre-commit hook (staged files); pre-push hook (every new commit, also those made by rebase, cherry-pick or `--no-verify`); CI | reserved file names, private keys, some token formats and keys written as hex text or byte arrays next to a name containing *key*, *secret* or *master* |
| gitleaks | CI, after the push | pattern based |

None of them finds every secret (for example a key with an unrelated variable name or in base64). Look at
`git diff --staged` before committing. For a false alarm, put `secret-scan: allow` on the reported line.

The check also rejects source files with reserved names such as `keys.c`; name code by what it does, for example
`key_derivation.c`.

## Open decisions (WP3)

- Key derivation function.
- How node keys get onto the boards and the gateway without being part of a published binary.
- Read protection of the boards. Read the reference manual before changing option bytes: some protection levels cannot
  be undone.
