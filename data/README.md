# Data

Raw measurement data, committed unchanged. Layout:

```
data/
  nodes.csv                 node_id, role, parent_id, key_id, board serial
  runs/<run_id>/run.json    test run metadata
  runs/<run_id>/frames.csv  one row per received frame
```

Format of `<run_id>` and the columns: [data-model.md](../docs/data-model.md). Licensed under CC BY 4.0 (see the [README](../README.md#license)).
