# Firmware

Node, relay and gateway firmware for the Seeed Wio-E5 mini (STM32WLE5JC). One firmware for all boards; the role is set
by configuration.

| Module | Purpose | Work package |
|---|---|---|
| radio | LoRa transmit/receive with the STM32WL sub-GHz radio | WP1 |
| frame | 7 B header + 12 B data + 8 B tag ([frame format](../docs/frame-format.md)) | WP1 |
| sensors | temperature/humidity and gas/VOC sensors | WP1 |
| gateway | add RSSI/SNR, one line per frame over USB serial | WP1 |
| routing | synchronous listen slots, relaying over at least two hops, duty-cycle accounting | WP2 |
| security | key derivation, AES-256-CCM, nonce, replay window, epoch in non-volatile memory | WP3 |

Toolchain: STM32CubeIDE with the STM32CubeWL package; flashing and debugging over an ST-LINK/V2 (SWD).
Logic that does not touch the hardware (frame encoding, nonce, replay window, duty-cycle accounting, airtime) is unit
tested on the host. Build and test instructions are added together with the first code.
