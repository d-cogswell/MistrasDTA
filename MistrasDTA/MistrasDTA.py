import numpy as np
from numpy.lib.recfunctions import append_fields
from datetime import datetime, timedelta
from enum import Enum
import struct
import logging


class EventType(Enum):
    """Type of event yielded by iter_events."""
    HIT = "hit"
    TD = "td"
    WFM = "wfm"


CHID_to_str = {
    1: 'RISE',
    2: 'PCNTS',
    3: 'COUN',
    4: 'ENER',
    5: 'DURATION',
    6: 'AMP',
    8: 'ASL',
    10: 'THR',
    13: 'A-FRQ',
    17: 'RMS',
    18: 'R-FRQ',
    19: 'I-FRQ',
    20: 'SIG STRENGTH',
    21: 'ABS-ENERGY',
    22: 'PARTIAL POWER',
    23: 'FRQ-C',
    24: 'P-FRQ',
    31: 'UNKNOWN',
}

CHID_byte_len = {
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 4,
    6: 1,
    8: 1,
    10: 1,
    13: 2,
    17: 2,
    18: 2,
    19: 2,
    20: 4,
    21: 4,
    22: 0,  # variable-length: partial_power_segments bytes (from MID 109)
    23: 2,
    24: 2,
    31: 2, # unclear, we have no information on CHID 31
}


def _bytes_to_RTOT(bytes):
    """Helper function to convert a 6-byte sequence to a time offset"""
    (i1, i2) = struct.unpack('<IH', bytes)
    return ((i1+2**32*i2)*.25e-6)


def _decode_td_fv(fv_bytes, demand_chid_list, partial_power_segments):
    """Decode a time-driven feature vector into a dict of named values.

    The FV is a concatenation of values for each CHID in demand_chid_list,
    using byte lengths from CHID_byte_len (CHID 22 uses partial_power_segments).
    """
    offset = 0
    values = {}
    for chid in demand_chid_list:
        name = CHID_to_str.get(chid, 'CHID_%d' % chid)
        if chid == 22:
            n = partial_power_segments
            values[name] = fv_bytes[offset:offset+n]
            offset += n
        elif chid == 17:  # RMS: uint16 / 5000
            [v] = struct.unpack_from('H', fv_bytes, offset)
            values[name] = v / 5000.0
            offset += 2
        elif chid == 21:  # ABS-ENERGY: float32 * 9.31e-4
            [v] = struct.unpack_from('f', fv_bytes, offset)
            values[name] = v * 9.31e-4
            offset += 4
        elif chid == 5:  # DURATION: int32
            [v] = struct.unpack_from('i', fv_bytes, offset)
            values[name] = v
            offset += 4
        elif chid == 20:  # SIG STRENGTH: int32 * 3.05
            [v] = struct.unpack_from('i', fv_bytes, offset)
            values[name] = v * 3.05
            offset += 4
        else:
            bl = CHID_byte_len.get(chid, 0)
            if bl == 1:
                [v] = struct.unpack_from('B', fv_bytes, offset)
            elif bl == 2:
                [v] = struct.unpack_from('H', fv_bytes, offset)
            elif bl == 4:
                [v] = struct.unpack_from('I', fv_bytes, offset)
            else:
                v = fv_bytes[offset:offset+bl]
            values[name] = v
            offset += bl
    return values


# MIDs that carry event/data records — read_config stops at these
_DATA_MIDS = frozenset({1, 2, 3, 128, 129, 130, 173})


def iter_events(data, config, skip_wfm=False, include_td=False):
    """Yield (event_type, event_data) tuples from a DTA data stream.

    Call read_config(data) first to consume setup messages; this
    generator picks up where it left off.
    """
    CHID_list = config["chid_list"]
    partial_power_segments = config["partial_power_segments"]
    gain = config["gain"]
    hardware = config["waveform_hardware"]
    demand_chid_list = config["demand_chid_list"]
    demand_pid_list = config["demand_pid_list"]

    # Parametric PID order (captured from first hit that has parametrics)
    param_pids = None

    # Time-driven column metadata
    td_pid_order = None     # PID column order (from first TD record)
    td_cid_order = None     # CID column order (from first TD record)
    td_fv_keys = None       # feature names per channel (from first TD record)

    byte = data.read(2)
    while byte != b"":

            # Get the message length byte
            [LEN] = struct.unpack('<H', byte)

            # Read the message ID byte
            [b1] = struct.unpack('<B', data.read(1))
            LEN = LEN-1

            # ID 40-49 have an extra byte
            if b1 >= 40 and b1 <= 49:
                [b2] = struct.unpack('<B', data.read(1))
                LEN = LEN-1

            if b1 == 1:
                logging.info("AE Hit or Event Data")

                RTOT = _bytes_to_RTOT(data.read(6))
                LEN = LEN-6

                [CID] = struct.unpack('<B', data.read(1))
                LEN = LEN-1

                record = [RTOT, CID]

                # Look up byte length and read data values
                for CHID in CHID_list:
                    b = CHID_byte_len[CHID]

                    if CHID_to_str[CHID] == 'PARTIAL POWER':
                        v = data.read(partial_power_segments)
                        LEN = LEN - partial_power_segments
                        record.append(v)
                        continue

                    if CHID_to_str[CHID] == 'RMS':
                        [v] = struct.unpack('<H', data.read(b))
                        v = v/5000

                    # DURATION
                    elif CHID_to_str[CHID] == 'DURATION':
                        [v] = struct.unpack('<i', data.read(b))

                    # SIG STRENGTH
                    elif CHID_to_str[CHID] == 'SIG STRENGTH':
                        [v] = struct.unpack('<i', data.read(b))
                        v = v*3.05

                    # ABS-ENERGY
                    elif CHID_to_str[CHID] == 'ABS-ENERGY':
                        [v] = struct.unpack('<f', data.read(b))
                        v = v*9.31e-4

                    elif b == 1:
                        [v] = struct.unpack('<B', data.read(b))

                    elif b == 2:
                        [v] = struct.unpack('<H', data.read(b))

                    LEN = LEN-b
                    record.append(v)

                # Parametric channels: PID(u8) + VALUE(u16) repeats
                # Trailing 2 bytes are undocumented (observed: varies)
                parametrics = {}
                while LEN >= 5:  # PID(1) + VALUE(2) + trailing(2)
                    [pid] = struct.unpack('B', data.read(1))
                    [val] = struct.unpack('H', data.read(2))
                    LEN = LEN - 3
                    parametrics[pid] = val
                data.read(LEN)  # trailing bytes

                if parametrics and param_pids is None:
                    param_pids = tuple(parametrics.keys())
                    config["param_pids"] = param_pids

                for pid in (param_pids or ()):
                    record.append(parametrics.get(pid))

                yield (EventType.HIT, record)

            elif b1 in (2, 3):
                logging.info("Time-Driven Data" if b1 == 2
                             else "User-Forced Sample Data")

                RTOT = _bytes_to_RTOT(data.read(6))
                LEN = LEN-6

                # Parametric channels: PID(u8) + VALUE(u16) per demand PID
                parametrics = {}
                for _ in demand_pid_list:
                    if LEN < 3:
                        break
                    [pid] = struct.unpack('B', data.read(1))
                    [val] = struct.unpack('H', data.read(2))
                    LEN = LEN - 3
                    parametrics[pid] = val

                # Feature vector length from demand CHID list
                fv_len = 0
                for chid in demand_chid_list:
                    if chid == 22:
                        fv_len += partial_power_segments
                    else:
                        fv_len += CHID_byte_len.get(chid, 0)

                # Channel blocks: CID(u8) + FV(fv_len) repeats
                per_channel = {}
                while LEN >= 1 + fv_len and fv_len > 0:
                    [cid] = struct.unpack('B', data.read(1))
                    fv = data.read(fv_len)
                    LEN = LEN - 1 - fv_len
                    per_channel[cid] = _decode_td_fv(
                        fv, demand_chid_list, partial_power_segments)

                data.read(LEN)  # trailing bytes

                if include_td:
                    # Capture column order from first record
                    if td_pid_order is None:
                        td_pid_order = tuple(parametrics.keys())
                        config["td_pid_order"] = td_pid_order
                    if td_cid_order is None:
                        td_cid_order = tuple(sorted(per_channel.keys()))
                        config["td_cid_order"] = td_cid_order
                    if td_fv_keys is None and per_channel:
                        first_cid = next(iter(per_channel))
                        td_fv_keys = tuple(
                            per_channel[first_cid].keys())
                        config["td_fv_keys"] = td_fv_keys

                    pid_vals = [parametrics.get(p) for p in
                                (td_pid_order or ())]
                    cid_vals = []
                    for cid in (td_cid_order or ()):
                        fv_dict = per_channel.get(cid, {})
                        for key in (td_fv_keys or ()):
                            cid_vals.append(fv_dict.get(key))

                    yield (EventType.TD, [RTOT] + pid_vals + cid_vals)

            elif b1 == 128:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info(
                    "{0:.7f} Resume Test or Start Of Test".format(RTOT))
                # in our test file, this message can have an extra byte that isn't
                # described in the manual, so read it if it's there
                data.read(LEN-6)

            elif b1 == 129:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info("{0:.7f} Stop the test".format(RTOT))

            elif b1 == 130:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info("{0:.7f} Pause the test".format(RTOT))

            elif b1 == 173:
                logging.info("Digital AE Waveform Data")

                [SUBID] = struct.unpack('<B', data.read(1))
                LEN = LEN-1

                TOT = _bytes_to_RTOT(data.read(6))
                LEN = LEN-6

                [CID, ALB] = struct.unpack('<BB', data.read(2))
                LEN = LEN-2

                MaxInput = 10.0
                Gain = 10**(gain[CID]/20)
                MaxCounts = 32768.0
                AmpScaleFactor = MaxInput/(Gain*MaxCounts)

                s = np.frombuffer(data.read(LEN), dtype=np.int16)

                if not skip_wfm:
                    channel = hardware[hardware['CH'] == CID]
                    re = [TOT, CID, channel['SRATE'][0], channel['TDLY'][0],
                        (AmpScaleFactor*s).tobytes()]
                    yield (EventType.WFM, re)

            else:
                logging.debug("ID "+str(b1)+" not yet implemented!")
                data.read(LEN)

            byte = data.read(2)


def read_config(data):
    """Read configuration messages from an open DTA file handle.

    Consumes setup messages and returns when the first data message
    is encountered.  The stream is rewound so the next read starts
    at that data message.
    """

    # Array to hold AE hardware settings
    hardware = []

    # Dictionary to hold gain settings
    gain = {}

    # Default list of characteristics
    CHID_list = []

    # Number of partial power segments (set by MID 109 or SubID 109)
    partial_power_segments = 0

    # Hardware config state (populated by MID 42 SubIDs)
    threshold = {}      # CID -> threshold dB (SubID 22)
    hdt = {}            # CID -> hit definition time µs (SubID 24)
    hlt = {}            # CID -> hit lockout time µs (SubID 25)
    pdt = {}            # CID -> peak definition time µs (SubID 26)
    sampling_interval_ms = None  # global sampling interval (SubID 27)
    demand_rate_ms = None        # demand sampling rate (SubID 102)

    # ASCII metadata
    product_name = None   # from MID 41
    user_comment = None   # from MID 7

    # Time-driven / demand data (MID 2/3)
    demand_chid_list = ()   # from SubID 6
    demand_pid_list = ()    # from SubID 6

    test_start_time = None

    while True:
            pos = data.tell()
            byte = data.read(2)
            if byte == b"":
                break

            # Get the message length byte
            [LEN] = struct.unpack('<H', byte)

            # Read the message ID byte
            [b1] = struct.unpack('<B', data.read(1))
            LEN = LEN-1

            if b1 in _DATA_MIDS:
                data.seek(pos)
                break

            # ID 40-49 have an extra byte
            if b1 >= 40 and b1 <= 49:
                [b2] = struct.unpack('<B', data.read(1))
                LEN = LEN-1

            if b1 == 7:
                logging.info("User Comments/Test Label:")
                [m] = struct.unpack('<{0}s'.format(LEN), data.read(LEN))
                logging.info(m.decode("ascii").strip('\x00'))

            elif b1 == 8:
                logging.info("Message for Continued File")

                # Time of continuation
                data.read(8)

                # The rest of the mssage contains a setup record,
                # reset LEN and process as a new message
                LEN = 0

            elif b1 == 41:
                logging.info("ASCII Product Definition:")

                # PVERN
                data.read(2)
                LEN = LEN-2

                [m] = struct.unpack(str(LEN)+'s', data.read(LEN))
                product_name = m[:-3].decode('ascii')
                logging.info(product_name)

            elif b1 == 42:
                logging.info("Hardware Setup")

                # MVERN
                data.read(2)
                LEN = LEN-2

                # SUBID
                while LEN > 0:
                    [LSUB] = struct.unpack('<H', data.read(2))
                    LEN = LEN-LSUB

                    [SUBID] = struct.unpack('<B', data.read(1))
                    LSUB = LSUB-1

                    if SUBID == 5:
                        logging.info("\tEvent Data Set Definition")

                        # Number of AE characteristics
                        [CHID] = struct.unpack('<B', data.read(1))
                        LSUB = LSUB-1

                        # read CHID values
                        CHID_list = struct.unpack(
                            '<{0}B'.format(CHID), data.read(CHID))
                        LSUB = LSUB-CHID

                    elif SUBID == 6:
                        logging.info("\tDemand Data Set Definition")
                        [N_CHID] = struct.unpack('B', data.read(1))
                        LSUB = LSUB-1
                        demand_chid_list = struct.unpack(
                            str(N_CHID)+'B', data.read(N_CHID))
                        LSUB = LSUB-N_CHID
                        [N_PID] = struct.unpack('B', data.read(1))
                        LSUB = LSUB-1
                        demand_pid_list = struct.unpack(
                            str(N_PID)+'B', data.read(N_PID))
                        LSUB = LSUB-N_PID

                    elif SUBID == 22:
                        logging.info("\tSet Threshold")
                        CID, V, _flags = struct.unpack('BBB', data.read(3))
                        threshold[CID] = V
                        LSUB = LSUB-3

                    elif SUBID == 23:
                        logging.info("\tSet Gain")
                        CID, V = struct.unpack('<BB', data.read(2))
                        gain[CID] = V
                        LSUB = LSUB-2

                    elif SUBID == 24:
                        logging.info("\tSet HDT")
                        CID = struct.unpack('B', data.read(1))[0]
                        [V] = struct.unpack('H', data.read(2))
                        hdt[CID] = V * 2  # steps of 2 µs
                        LSUB = LSUB-3

                    elif SUBID == 25:
                        logging.info("\tSet HLT")
                        CID = struct.unpack('B', data.read(1))[0]
                        [V] = struct.unpack('H', data.read(2))
                        hlt[CID] = V * 2  # steps of 2 µs
                        LSUB = LSUB-3

                    elif SUBID == 26:
                        logging.info("\tSet PDT")
                        CID = struct.unpack('B', data.read(1))[0]
                        [V] = struct.unpack('H', data.read(2))
                        pdt[CID] = V  # already in µs
                        LSUB = LSUB-3

                    elif SUBID == 27:
                        logging.info("\tSet Sampling Interval")
                        [V] = struct.unpack('H', data.read(2))
                        sampling_interval_ms = V
                        LSUB = LSUB-2

                    elif SUBID == 102:
                        logging.info("\tSet Demand Rate")
                        [V] = struct.unpack('H', data.read(2))
                        demand_rate_ms = V
                        LSUB = LSUB-2

                    elif SUBID == 173:
                        [SUBID2] = struct.unpack('<B', data.read(1))
                        LSUB = LSUB-1

                        if SUBID2 == 42:
                            logging.info("\t173,42 Hardware Setup")

                            [MVERN, b2, ADT, SETS, SLEN, CHID, HLK,
                             SRATE, TMODE, TSRC, TDLY, MXIN, THRD] = \
                                struct.unpack(
                                    '<BBBBxHBH2xHHHhHH', data.read(24))
                            LSUB = LSUB-24

                            hardware.append([CHID, 1000*SRATE, TDLY])

                    elif SUBID == 109:
                        # Partial Power Setup (embedded in MID 42)
                        data.read(1)  # SEGMENT_TYPE
                        LSUB = LSUB - 1
                        [n_seg] = struct.unpack('H', data.read(2))
                        LSUB = LSUB - 2
                        partial_power_segments = n_seg

                    else:
                        logging.debug(
                            "\tSUBID {0} not yet implemented!".format(SUBID))

                    data.read(LSUB)

                # Convert hardware settings to record array
                hardware = np.rec.fromrecords(
                    hardware, names=['CH', 'SRATE', 'TDLY'])

            elif b1 == 99:
                logging.info("Time and Date of Test Start:")
                [m] = struct.unpack('<{0}s'.format(LEN), data.read(LEN))
                m = m.decode("ascii").strip('\x00')
                logging.info(m)
                test_start_time = datetime.strptime(
                    m, '%a %b %d %H:%M:%S %Y\n')

            else:
                logging.debug("ID "+str(b1)+" not yet implemented!")
                data.read(LEN)

    return {
        "test_start_time": test_start_time,
        "product_name": product_name,
        "user_comment": user_comment,
        "chid_list": CHID_list,
        "gain": dict(gain),
        "threshold": dict(threshold),
        "hdt": dict(hdt),
        "hlt": dict(hlt),
        "pdt": dict(pdt),
        "sampling_interval_ms": sampling_interval_ms,
        "demand_rate_ms": demand_rate_ms,
        "demand_chid_list": demand_chid_list,
        "demand_pid_list": demand_pid_list,
        "partial_power_segments": partial_power_segments,
        "waveform_hardware": hardware,
    }


def read_bin(files, skip_wfm=False, include_td=False, include_config=False):
    """Function to read binary AEWin data files. The file structure schema is
    described in Appendix II of the Mistras User's Manual.

    Args:
        files (str or list): path to a .DTA file, or list of paths for
            continuation files (state is shared across files)
        skip_wfm (bool): do not return waveforms if True
        include_td (bool): if True, return a td recarray of time-driven data
        include_config (bool): if True, return a config dict as last element
    Returns:
        rec (numpy.recarray): table of acoustic hits
        wfm (numpy.recarray): table containing any saved waveforms
        td (numpy.recarray): time-driven data (only when include_td=True)
        config (dict): hardware configuration (only when include_config=True)
    """

    # Normalise to a list of paths
    if isinstance(files, str):
        files = [files]

    # Array to hold AE hit records
    rec = []

    # Array to hold waveforms
    wfm = []

    # Time-driven record rows
    td = []

    config = None

    for file in files:
        with open(file, "rb") as data:
            if config is None:
                config = read_config(data)

            for event_type, event_data in iter_events(data, config, include_td=include_td, skip_wfm=skip_wfm):
                if event_type is EventType.HIT:
                    rec.append(event_data)
                elif event_type is EventType.TD:
                    td.append(event_data)
                elif event_type is EventType.WFM:
                    wfm.append(event_data)

    test_start_time = config["test_start_time"]
    CHID_list = config["chid_list"]
    param_pids = config.pop("param_pids", None)
    td_pid_order = config.pop("td_pid_order", None)
    td_cid_order = config.pop("td_cid_order", None)
    td_fv_keys = config.pop("td_fv_keys", None)

    # Convert numpy array and add record names
    # fromrecords() fails on an empty list
    if rec:
        param_names = ['PARAM_%d' % p for p in (param_pids or ())]
        rec = np.rec.fromrecords(
            rec,
            names=['SSSSSSSS.mmmuuun', 'CH']
            + [CHID_to_str[i] for i in CHID_list]
            + param_names)

        # Append a Unix timestamp field
        timestamp = [
            (test_start_time + timedelta(seconds=t)).timestamp()
            for t in rec['SSSSSSSS.mmmuuun']]
        rec = append_fields(rec, 'TIMESTAMP', timestamp,
                            usemask=False, asrecarray=True)

    if wfm:
        wfm = np.rec.fromrecords(
            wfm, names=['SSSSSSSS.mmmuuun', 'CH', 'SRATE', 'TDLY', 'WAVEFORM'])

    if include_td and td:
        pid_cols = ['PID_%d' % p for p in (td_pid_order or ())]
        cid_cols = []
        if td_cid_order is not None and td_fv_keys is not None:
            for cid in td_cid_order:
                for key in td_fv_keys:
                    cid_cols.append('CID%d_%s' % (cid, key))
        td = np.rec.fromrecords(
            td, names=['SSSSSSSS.mmmuuun'] + pid_cols + cid_cols)

    result = (rec, wfm)
    if include_td:
        result += (td,)
    if include_config:
        result += (config,)
    return result


def get_waveform_data(wfm_row):
    """Returns time and voltage from a row of the wfm recarray"""
    V = np.frombuffer(wfm_row['WAVEFORM'])
    t = 1e6*(np.arange(0, len(V))+wfm_row['TDLY'])/wfm_row['SRATE']
    return t, V
