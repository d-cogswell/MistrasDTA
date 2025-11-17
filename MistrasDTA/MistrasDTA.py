import numpy as np
from numpy.lib.recfunctions import append_fields
from datetime import datetime, timedelta
import struct
import logging


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
    23: 'FRQ-C',
    24: 'P-FRQ'}

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
    23: 2,
    24: 2}


def _bytes_to_RTOT(bytes):
    """Helper function to convert a 6-byte sequence to a time offset"""
    (i1, i2) = struct.unpack('IH', bytes)
    return ((i1+2**32*i2)*.25e-6)


def read_bin(file, skip_wfm=False):
    """Function to read binary AEWin data files. The file structure schema is
    described in Appendix II of the Mistras User's Manual.

    Args:
        file (str): name of a .DTA file to read
        skip_wfm (bool): do not return waveforms if True
    Returns:
        rec (numpy.recarray): table of acoustic hits
        wfm (numpy.recarray): table containing any saved waveforms
    """

    # Array to hold AE hit records
    rec = []

    # Array to hold waveforms
    wfm = []

    # Array to hold AE hardware settings
    hardware = []

    # Dictionary to hold gain settings
    gain = {}

    # Default list of characteristics
    CHID_list = []

    with open(file, "rb") as data:
        byte = data.read(2)
        while byte != b"":

            # Get the message length byte
            [LEN] = struct.unpack('H', byte)

            # Read the message ID byte
            [b1] = struct.unpack('B', data.read(1))
            LEN = LEN-1

            # ID 40-49 have an extra byte
            if b1 >= 40 and b1 <= 49:
                [b2] = struct.unpack('B', data.read(1))
                LEN = LEN-1

            if b1 == 1:
                logging.info("AE Hit or Event Data")

                RTOT = _bytes_to_RTOT(data.read(6))
                LEN = LEN-6

                [CID] = struct.unpack('B', data.read(1))
                LEN = LEN-1

                record = [RTOT, CID]

                # Look up byte length and read data values
                for CHID in CHID_list:
                    b = CHID_byte_len[CHID]

                    if CHID_to_str[CHID] == 'RMS':
                        [v] = struct.unpack('H', data.read(b))
                        v = v/5000

                    # DURATION
                    elif CHID_to_str[CHID] == 'DURATION':
                        [v] = struct.unpack('i', data.read(b))

                    # SIG STRENGTH
                    elif CHID_to_str[CHID] == 'SIG STRENGTH':
                        [v] = struct.unpack('i', data.read(b))
                        v = v*3.05

                    # ABS-ENERGY
                    elif CHID_to_str[CHID] == 'ABS-ENERGY':
                        [v] = struct.unpack('f', data.read(b))
                        v = v*9.31e-4

                    elif b == 1:
                        [v] = struct.unpack('B', data.read(b))

                    elif b == 2:
                        [v] = struct.unpack('H', data.read(b))

                    LEN = LEN-b
                    record.append(v)

                # Parmetric channels
                data.read(LEN)

                rec.append(record)

            elif b1 == 7:
                logging.info("User Comments/Test Label:")
                [m] = struct.unpack(str(LEN)+'s', data.read(LEN))
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
                logging.info(m[:-3].decode('ascii'))

            elif b1 == 42:
                logging.info("Hardware Setup")

                # MVERN
                data.read(2)
                LEN = LEN-2

                # SUBID
                while LEN > 0:
                    [LSUB] = struct.unpack('H', data.read(2))
                    LEN = LEN-LSUB

                    [SUBID] = struct.unpack('B', data.read(1))
                    LSUB = LSUB-1

                    if SUBID == 5:
                        logging.info("\tEvent Data Set Definition")

                        # Number of AE characteristics
                        [CHID] = struct.unpack('B', data.read(1))
                        LSUB = LSUB-1

                        # read CHID values
                        CHID_list = struct.unpack(
                            str(CHID)+'B', data.read(CHID))
                        LSUB = LSUB-CHID

                    elif SUBID == 23:
                        logging.info("\tSet Gain")
                        CID, V = struct.unpack('BB', data.read(2))
                        gain[CID] = V
                        LSUB = LSUB-2

                    elif SUBID == 173:
                        [SUBID2] = struct.unpack('B', data.read(1))
                        LSUB = LSUB-1

                        if SUBID2 == 42:
                            logging.info("\t173,42 Hardware Setup")

                            [MVERN, b2] = struct.unpack('BB', data.read(2))
                            LSUB = LSUB-2

                            # ADT
                            data.read(1)
                            LSUB = LSUB-1

                            [SETS, b2] = struct.unpack('BB', data.read(2))
                            LSUB = LSUB-2

                            [SLEN] = struct.unpack('H', data.read(2))
                            LSUB = LSUB-2

                            [CHID] = struct.unpack('B', data.read(1))
                            LSUB = LSUB-1

                            [HLK] = struct.unpack('H', data.read(2))
                            LSUB = LSUB-2

                            # HITS
                            data.read(2)
                            LSUB = LSUB-2

                            [SRATE] = struct.unpack('H', data.read(2))
                            LSUB = LSUB-2

                            # TMODE
                            data.read(2)
                            LSUB = LSUB-2

                            # TSRC
                            data.read(2)
                            LSUB = LSUB-2

                            [TDLY] = struct.unpack('h', data.read(2))
                            LSUB = LSUB-2

                            # MXIN
                            data.read(2)
                            LSUB = LSUB-2

                            # THRD
                            data.read(2)
                            LSUB = LSUB-2

                            hardware.append([CHID, 1000*SRATE, TDLY])

                    else:
                        logging.debug(
                            "\tSUBID {0} not yet implemented!".format(SUBID))

                    data.read(LSUB)

                # Convert hardware settings to record array
                hardware = np.rec.fromrecords(
                    hardware, names=['CH', 'SRATE', 'TDLY'])

            elif b1 == 99:
                logging.info("Time and Date of Test Start:")
                [m] = struct.unpack(str(LEN)+'s', data.read(LEN))
                m = m.decode("ascii").strip('\x00')
                logging.info(m)
                test_start_time = datetime.strptime(
                    m, '%a %b %d %H:%M:%S %Y\n')

            elif b1 == 128:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info(
                    "{0:.7f} Resume Test or Start Of Test".format(RTOT))

            elif b1 == 129:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info("{0:.7f} Stop the test".format(RTOT))

            elif b1 == 130:
                RTOT = _bytes_to_RTOT(data.read(6))
                logging.info("{0:.7f} Pause the test".format(RTOT))

            elif b1 == 173:
                logging.info("Digital AE Waveform Data")

                [SUBID] = struct.unpack('B', data.read(1))
                LEN = LEN-1

                TOT = _bytes_to_RTOT(data.read(6))
                LEN = LEN-6

                [CID] = struct.unpack('B', data.read(1))
                LEN = LEN-1

                # ALB
                data.read(1)
                LEN = LEN-1

                MaxInput = 10.0
                Gain = 10**(gain[CID]/20)
                MaxCounts = 32768.0
                AmpScaleFactor = MaxInput/(Gain*MaxCounts)

                s = struct.unpack(str(int(LEN/2))+'h', data.read(LEN))

                # Append waveform to wfm with data stored as a byte string
                if not skip_wfm:
                    channel = hardware[hardware['CH'] == CID]
                    re = [TOT, CID, channel['SRATE'][0], channel['TDLY']
                          [0], (AmpScaleFactor*np.array(s)).tobytes()]
                    wfm.append(re)

            else:
                logging.debug("ID "+str(b1)+" not yet implemented!")
                data.read(LEN)

            byte = data.read(2)

    # Convert numpy array and add record names
    # fromrecords() fails on an empty list
    if rec:
        rec = np.rec.fromrecords(
            rec,
            names=['SSSSSSSS.mmmuuun', 'CH']
            + [CHID_to_str[i] for i in CHID_list])

        # Append a Unix timestamp field
        timestamp = [
            (test_start_time + timedelta(seconds=t)).timestamp()
            for t in rec['SSSSSSSS.mmmuuun']]
        rec = append_fields(rec, 'TIMESTAMP', timestamp,
                            usemask=False, asrecarray=True)

    if wfm:
        wfm = np.rec.fromrecords(
            wfm, names=['SSSSSSSS.mmmuuun', 'CH', 'SRATE', 'TDLY', 'WAVEFORM'])

    return rec, wfm


def get_waveform_data(wfm_row):
    """Returns time and voltage from a row of the wfm recarray"""
    V = np.frombuffer(wfm_row['WAVEFORM'])
    t = 1e6*(np.arange(0, len(V))+wfm_row['TDLY'])/wfm_row['SRATE']
    return t, V
