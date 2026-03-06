# Test Data Manifest

## DTA Files (`tests/dta/`)

| File | Channels | CHIDs | Parametrics | MID Types | Notes |
|------|----------|-------|-------------|-----------|-------|
| `210527-CH1-15.DTA` | 1 | Standard (no CHID 22/31) | None | 1, 173 | Single-channel hits + waveforms |
| `260114-4ch-1para.DTA` | 4 | Includes CHID 22, 31 | 1 parametric | 2, 173 | Time-driven data only (no MID 1 hits), partial power segments |

## Reference Files (`tests/reference/`)

Each `.npz` contains `rec` and `wfm` arrays matching the expected output of `read_bin()` for the corresponding DTA file. TIMESTAMP fields are excluded from comparison (timezone-dependent).
