[![release](https://img.shields.io/github/v/release/d-cogswell/MistrasDTA)](https://github.com/d-cogswell/MistrasDTA/releases)
[![NewareNDA regression tests](https://github.com/d-cogswell/MistrasDTA/actions/workflows/tests.yml/badge.svg)](https://github.com/d-cogswell/MistrasDTA/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/d-cogswell/MistrasDTA/badge.svg?branch=development)](https://coveralls.io/github/d-cogswell/MistrasDTA?branch=development)

# MistrasDTA
Python module to read acoustic emissions hit data and waveforms from Mistras DTA files. The structure of these binary files is detailed in Appendix II of the Mistras user manual.

This is forked from https://github.com/d-cogswell/MistrasDTA to add a few features I needed for a project, primarily support for CHID 22 and 31 and export of TD data.

# Additions
The following features were added to support additional use cases:

- **Time-driven (demand) data**: Parametric channels sampled at fixed intervals are now captured via `include_td=True`
- **Hardware configuration**: Gain, threshold, HDT/HLT/PDT timing, and sampling rates available via `include_config=True`
- **Multi-file support**: `read_bin()` and `iter_bin()` accept a list of files and handle continuations seamlessly
- **Streaming iterator**: `iter_bin()` yields `(type, record)` tuples for memory-efficient processing of large files
- **Spec docs**: `docs/SPEC.md` is the Mistras Appendix II converted to markdown for easier LM ingestion

# Installation
MistrasDTA can be installed from PyPI with the following command:
```
python -m pip install MistrasDTA
```

# Usage
Read the hit summary table from a DTA file:
```
import MistrasDTA
rec, _ = MistrasDTA.read_bin('cluster.DTA', skip_wfm=True)

```

Read hit summary and waveform data from a DTA:
```
import MistrasDTA
from numpy.lib.recfunctions import join_by

# Read the binary file and join summary and waveform tables
rec, wfm = MistrasDTA.read_bin('cluster.DTA')
merged = join_by(['SSSSSSSS.mmmuuun', 'CH'], rec, wfm)

# Extract the first waveform in units of microseconds and volts
t, V = MistrasDTA.get_waveform_data(merged[0])
```

Read time-driven (demand) data and hardware configuration (dict):
```
rec, wfm, td, config = MistrasDTA.read_bin('cluster.DTA', include_td=True, include_config=True)
```

Stream events from a large file without loading everything into memory:
```
for ev_type, record in MistrasDTA.iter_bin('large_file.DTA'):
    if ev_type == "hit":
        print(record[0], record[1])  # RTOT, CID
```
