# MistrasDTA
Python module to read Mistras acoustic emissions DTA files. The structure of these binary files is detailed in the an appendix of the Mistras user manual. 

# Usage
```
import MistrasDTA

# Read the binary file
rec, wfm = MistrasDTA.read_bin('cluster.DTA')

# Extract the first waveform in units of microseconds and volts
t, V = MistrasDTA.get_waveform_data(wfm[0])
```
