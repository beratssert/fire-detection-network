# Gateway logger

Laptop-side Python program: reads the gateway board over USB serial, adds a laptop time stamp, decodes every frame and
writes one row per frame to `data/runs/<run_id>/frames.csv`, plus the run metadata (`run.json`).
The serial port is a command-line parameter, because its name differs between systems (for example `COM3` on Windows,
`/dev/ttyACM0` or `/dev/ttyUSB0` on Linux, `/dev/cu.*` on macOS). Paths are built with `pathlib`.

See [data-model.md](../docs/data-model.md).
