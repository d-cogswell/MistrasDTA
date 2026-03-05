import numpy as np
import MistrasDTA


def test_MistrasDTA(dta_file, ref_file):
    rec, wfm = MistrasDTA.read_bin(dta_file)
    ref = np.load(ref_file, allow_pickle=True)

    # Do not compare TIMESTAMP, it's affected by timezone
    if hasattr(rec, 'dtype'):
        rec = np.lib.recfunctions.drop_fields(rec, "TIMESTAMP")
    rec_ref = ref["rec"]
    if hasattr(rec_ref, 'dtype') and rec_ref.dtype.names and "TIMESTAMP" in rec_ref.dtype.names:
        rec_ref = np.lib.recfunctions.drop_fields(rec_ref, "TIMESTAMP")

    np.testing.assert_array_equal(rec, rec_ref)
    np.testing.assert_array_equal(wfm, ref["wfm"])
