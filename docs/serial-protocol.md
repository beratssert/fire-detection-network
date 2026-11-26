# Serial protocol: gateway → laptop

Interface contract between the gateway firmware and the [frame logger](../gateway-logger/README.md). The gateway sends
one line per received frame over USB serial (virtual COM port, [architecture.md](architecture.md)). The details below
are open decision [D9](decisions.md); this document is completed by the pull request that decides it.

## Open

- Serial settings (baud rate and line ending).
- Line format: field order and encoding (for example, text fields or the raw frame in hex) and how RSSI, SNR and the
  authentication result are written.
- How diagnostic output of the gateway is told apart from frame lines.
- Behaviour on errors (frame too short, failed tag check, buffer overflow).
- An example line for each kind of line, which the logger tests use.
