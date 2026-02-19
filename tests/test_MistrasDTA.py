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


def test_include_config(dta_file, ref_file):
    """include_config=True returns a 3-tuple with a well-formed config dict."""
    result = MistrasDTA.read_bin(dta_file, include_config=True)
    assert len(result) == 3
    rec, wfm, config = result

    # All expected keys present
    expected_keys = {
        "test_start_time", "product_name", "user_comment", "chid_list",
        "gain", "threshold", "hdt", "hlt", "pdt",
        "sampling_interval_ms", "demand_rate_ms",
        "partial_power_segments", "waveform_hardware",
    }
    assert set(config.keys()) == expected_keys

    # Gain, threshold, timing dicts are per-channel
    assert isinstance(config["gain"], dict)
    assert isinstance(config["threshold"], dict)
    assert isinstance(config["hdt"], dict)

    # waveform_hardware is a recarray with expected columns
    hw = config["waveform_hardware"]
    assert hasattr(hw, 'dtype')
    assert set(hw.dtype.names) >= {"CH", "SRATE", "TDLY"}
