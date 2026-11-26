# Frame format

Every frame has 27 bytes:

| Field | Size | Notes |
|---|---|---|
| node ID | 2 B | identifies the sending node |
| epoch (low byte) | 1 B | the receiver rebuilds the full epoch |
| counter | 4 B | increases with every frame of a node |
| data | 12 B | message type and readings; the byte layout is fixed in WP1 |
| authentication tag | 8 B | AES-256-CCM |

At SF7 (125 kHz bandwidth) the airtime of this frame is 66.8 ms; without the tag (19 B) it is 51.5 ms (preliminary
model, [`poster/results/security.csv`](../poster/results/security.csv)). Hypothesis 3 tests this on the hardware.

## Security fields

- **Keys:** each node key is derived from a master key and the node ID. The master key stays on the laptop.
- **Cipher:** AES-256 in CCM mode with an 8-byte tag. If the hardware AES unit of the STM32WLE5 does not support CCM
  as needed, a software implementation is used and its cost is reported separately.
- **Nonce (9 B):** counter (4 B) ‖ epoch (3 B) ‖ node ID (2 B). The counter is kept in RAM; at every start-up the node
  writes epoch + 1 to non-volatile memory before its first frame, so a nonce should not repeat after a power loss.
- **Replay protection:** the gateway keeps the highest counter per node and epoch and rejects old or repeated counters.

## Open

Interface contract between the firmware and the logger. These points are open decisions in [decisions.md](decisions.md)
and are filled in here by the pull request that decides them:

- byte layout and byte order of the data field (D4);
- bytes authenticated as associated data (D5);
- key derivation (D6) and the synchronisation beacon (D8);
- shared test vectors for encoding and authentication (D10).
