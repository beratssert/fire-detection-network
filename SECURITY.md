# Security

This repository holds a research prototype, not a product. Its security layer (authenticated AES-256-CCM frames,
replay protection) is one of the subjects under test, so reports of weaknesses are welcome.

## Reporting a vulnerability

Please do not open a public issue. Use **Report a vulnerability** on the repository's **Security** tab (GitHub private
vulnerability reporting). We answer as soon as we can; this is a student project without a guaranteed response time.

## Scope

- The code and documents on the `main` branch.
- Keys are never part of the repository ([docs/key-management.md](docs/key-management.md)). If you find what looks
  like a real key or token, report it in the same way; do not use it.
