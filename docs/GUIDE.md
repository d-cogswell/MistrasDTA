# Purpose

Byte-accurate, **spec-driven** parsing guide for AEwin/MISTRAS `.DTA` files intended for implementation with Python `struct.unpack`. No heuristics. Every branch must be explicit and triggered only by on-disk bytes or a caller-provided configuration flag.

Sources incorporated:

* Appendix II (rev 1) PAC message definitions (incl. page 28–29 screenshots)
* AE feature scaling doc (AEwin 32-bit)
* Your `SPEC.md` translation (used for cross-check)
* Empirical behavior implied by the reference reader (not authoritative; used only to motivate compatibility branches)

---

# 0. Global conventions

## 0.1 Endianness

All multi-byte integers in these specs are **little-endian** (LSB first) unless explicitly stated otherwise.

## 0.2 File structure: concatenated messages

The file is a stream of messages, each encoded as:

* `LEN` : `uint16_le` — number of bytes in `BODY`
* `BODY`: `bytes[LEN]`

Total bytes consumed per message = `2 + LEN`.

### 0.2.1 Normal message IDs

Normally, `BODY[0]` is the **1-byte Message ID**:

* `MID : uint8` (1..255)

### 0.2.2 “Extra 0 byte” for some IDs 40–49

For IDs in the **40–49 range**, many files encode the ID as two bytes: `MID:uint8` then an extra `0x00` byte.

**Deterministic rule:**

* If first byte `MID` is in `[40..49]`, read one more byte `MID_PAD:uint8` and require `MID_PAD == 0x00`.

> Note: Appendix II also discusses 41–44 having additional *version* fields; keep those per-message.

---

# 1. Primitive types

* `uint8`  : 1 byte
* `uint16_le` / `int16_le`: 2 bytes
* `uint32_le` / `int32_le`: 4 bytes
* `float32_le`: 4 bytes IEEE-754
* `bytes[n]`: raw bytes
* `zstr`: zero-terminated byte string within remaining message bytes

## 1.1 6-byte time fields

### 1.1.1 `RTOT` and `TOT`

Both are encoded as 6 bytes, LSB first. Treat as `uint48_le` (compose into Python `int`).

---

# 2. Stateful definitions that affect parsing

## 2.1 AE feature sizes and types (CHID)

### 2.1.1 Fixed-width CHID mapping

These are the **canonical** sizes/types to use when parsing AE feature lists (MID 1, and AEF extension in 173,1).

| CHID | Size | Unpack type  | Meaning                  |
| ---: | ---: | ------------ | ------------------------ |
|    1 |    2 | `uint16_le`  | Rise time                |
|    2 |    2 | `uint16_le`  | Counts to peak           |
|    3 |    2 | `uint16_le`  | Counts                   |
|    4 |    2 | `uint16_le`  | Energy counts            |
|    5 |    4 | `uint32_le`  | Duration                 |
|    6 |    1 | `uint8`      | Amplitude (dB)           |
|    7 |    1 | `uint8`      | RMS8 (obsolete)          |
|    8 |    1 | `uint8`      | ASL (dB)                 |
|    9 |    1 | `uint8`      | Gain                     |
|   10 |    1 | `uint8`      | Threshold                |
|   11 |    1 | `uint8`      | Pre-Amp current          |
|   12 |    4 | `uint32_le`  | Lost hits                |
|   13 |    2 | `uint16_le`  | Avg frequency (kHz)      |
|   17 |    2 | `uint16_le`  | RMS16 (scaled)           |
|   18 |    2 | `uint16_le`  | Reverberation freq (kHz) |
|   19 |    2 | `uint16_le`  | Initiation freq (kHz)    |
|   20 |    4 | `uint32_le`  | Signal strength (scaled) |
|   21 |    4 | `float32_le` | Absolute energy (scaled) |
|   23 |    2 | `uint16_le`  | Frequency centroid (kHz) |
|   24 |    2 | `uint16_le`  | Frequency peak (kHz)     |

### 2.1.2 Variable-width CHID 22 (Partial power)

CHID 22 has **dynamic width**: it is `N_SEG` bytes (1 byte per segment). `N_SEG` is defined by MID 109.

State:

* `partial_power_segment_count: int` (default 0 until MID 109 seen)

Rule:

* If CHID 22 appears in a feature list and `partial_power_segment_count` is not known (or 0 when it should be >0), the reader must **error or defer parsing** (no guessing).

## 2.2 MID 5 defines Event/Hit feature list

State:

* `event_chids: List[uint8]` (ordered)
* `event_max_hit_pid_count: uint8` (upper bound; layout still parses “until message end”)

## 2.3 MID 6 defines Time-driven/Demand sample set

State:

* `demand_chids: List[uint8]` (ordered)
* `demand_pids:  List[uint8]` (ordered)

## 2.4 Optional parametric extra byte V3

Appendix II shows an optional `(V3)` “Cycle Counter MSB byte” in parametric sample entries, but provides no on-disk flag.

**Non-heuristic strategy:** require an explicit reader configuration flag:

* `include_cycle_counter_msb: bool`

Parametric entry layout:

* If `False`: `PID:uint8 + VALUE:uint16_le`
* If `True` : `PID:uint8 + VALUE:uint16_le + V3:uint8`

---

# 3. Message definitions

Offsets are relative to start of `BODY`.

## 3.1 MID 1 — AE Hit / Event Data

BODY:

1. `MID:uint8 == 1`
2. `RTOT: bytes[6]`
3. `CID:uint8`
4. `AE_FEATURES`: for each `CHID` in `event_chids` (MID 5 order):

   * If `CHID==22`: read `partial_power_segment_count` bytes as `uint8[N_SEG]`
   * Else: read fixed width from §2.1.1
5. `HIT_PARAMETRICS`: repeat until end of message:

   * `PID:uint8`
   * `VALUE:uint16_le`
   * if configured: `V3:uint8`

## 3.2 MID 2 — Time-driven sample data

BODY:

1. `MID:uint8 == 2`
2. `RTOT: bytes[6]`
3. `PARAMETRICS`: for each PID in `demand_pids` (in order):

   * `PID:uint8` (must match expected)
   * `VALUE:uint16_le`
   * if configured: `V3:uint8`
4. `CHANNEL_BLOCKS`: repeat until end:

   * `CID:uint8`
   * for each `CHID` in `demand_chids`:

     * parse per §2.1 (CHID 22 rule still applies if ever used)

## 3.3 MID 3 — User-forced sample data

Same as MID 2 except `MID==3`.

## 3.4 MID 4 — Error

BODY:

* `MID:uint8==4`
* `ERROR_CODE:uint8`
* `ERROR_BYTES: remaining`

## 3.5 MID 5 — Event data set definition

BODY:

* `MID:uint8==5`
* `N_CHID:uint8`
* `CHIDS:uint8[N_CHID]` (store as `event_chids`)
* `MAX_HIT_PID:uint8` (store)

## 3.6 MID 6 — Demand/Time-driven data set definition

BODY:

* `MID:uint8==6`
* `N_CHID:uint8`
* `CHIDS:uint8[N_CHID]` (store as `demand_chids`)
* `N_PID:uint8`
* `PIDS:uint8[N_PID]` (store as `demand_pids`)

## 3.7 MID 7 — User comments / label

BODY:

* `MID:uint8==7`
* `TEXT: bytes[LEN-1]` (ASCII, may contain NUL)

## 3.8 MID 8 — Continued file marker

BODY:

* `MID:uint8==8`
* `DOS_TIME_DATE: bytes[8]`
* `REMAINDER: bytes[...]`

Branch:

* If `REMAINDER` empty: Type A marker.
* Else: Type B contains an embedded message stream (same envelope `uint16_le LEN + BODY`) representing the setup record from the start of the test.

## 3.9 MID 11 — Reset absolute time clock

BODY: `MID:uint8==11` only.

## 3.10 MID 15 — Abort acquisition

BODY:

* `MID:uint8==15`
* `RTOT: bytes[6]`

## 3.11 MID 16 — Alarm

BODY:

* `MID:uint8==16`
* `RTOT: bytes[6]`
* `LEVEL:uint8`
* `AID:uint8`
* `CID:uint8`
* `VALUE:uint32_le`

## 3.12 MID 22–27 — Setup scalars

* 22 Set Threshold: `MID(1) + CID(1) + THRESH:uint8` (MSB indicates float/fix)
* 23 Set Gain: `MID + CID + GAIN:uint8`
* 24 HDT: `MID + CID + HDT:uint16_le`
* 25 HLK: `MID + CID + HLK:uint16_le`
* 26 PDT: `MID + CID + PDT:uint16_le`
* 27 Sampling interval: `MID + SAMPLING:uint16_le`

## 3.13 MID 28 — Alarm definition

BODY:

* `MID:uint8==28`
* `J:uint8`
* repeat J:

  * `ALARM_NUM:uint8`
  * `CID:uint8`
  * `TYPE_CODE:uint8`
  * `CHID:uint8`
  * `LEVEL1:uint32_le`
  * `LEVEL2:uint32_le`

## 3.14 MID 29 — AE filter definition (SCSH)

BODY:

* `MID:uint8==29`
* `K:uint8`
* repeat K:

  * `FILTER_NUM:uint8`
  * `CID:uint8`
  * `TYPE_CODE:uint8`
  * `CHID:uint8`
  * `LOW:uint32_le`
  * `HIGH:uint32_le`

## 3.15 MID 30 — Delta-T filter definition

BODY:

* `MID:uint8==30`
* `FS:uint8`
* repeat FS:

  * `FID:uint8`
  * `BDID:uint8`
  * `TYPE:uint8`
  * `INDHITS:uint8`
  * `LOW:int32_le`
  * `HIGH:int32_le`
  * `EDT:uint32_le`

## 3.16 MID 37 — INI password

BODY:

* `MID:uint8==37`
* `MVERN:uint8`
* `TOT: bytes[6]`
* `PASSWORD:zstr`

## 3.17 MID 38 — Test information

BODY:

* `MID:uint8==38`
* `MVERN:uint8`
* `ENEDIT:uint8`
* `EDISPF9:uint8`
* Repeated pairs of `ZTITLE:zstr` then `SZFIELD:zstr` until end.

## 3.18 IDs 41–49 (file-defining/product-specific) with ID pad

These often appear as `MID` then `0x00` pad (see §0.2.2). After that:

* MID 41: `PVERN:uint16_le` + `ASCII: remaining`
* MID 42: `MVERN:uint16_le` + submessage stream (`LSUB:uint16_le + SUBPAYLOAD[LSUB]`) where `SUBPAYLOAD[0]=SUBID`.
* MID 43,44,45,46,48,49: `MVERN:uint16_le` + product-specific payload.

Special case MID 44 dummy:

* In non-location files, MID 44 may appear with `LEN==1` or `LEN==2` (dummy bytes). Parse and ignore.

## 3.19 MID 59, 99, 100, 101, 102, 106, 110, 111, 124, 128, 129, 130, 131, 133

Implement per Appendix II as previously translated; only additions here:

### MID 109 — Partial power setup

Required for CHID 22 parsing.
BODY:

* `MID:uint8==109`
* `SEGMENT_TYPE:uint8` (typically 0)
* `N_SEG:uint16_le` (store as `partial_power_segment_count`)
* `RSV1:uint16_le` (often 1)
* `RSV2:uint16_le` (often 1)
* repeat `N_SEG`:

  * `SEG_NUM:uint16_le`
  * `SEG_START:uint16_le`
  * `SEG_END:uint16_le`
* `TP_N_SEG:uint16_le`
* `TP_SEG_NUM:uint16_le`
* `TP_SEG_START:uint16_le`
* `TP_SEG_END:uint16_le`

---

# 4. AEDSP/TRA “extended” messages with Sub-ID

## 4.1 Digital AE waveform data — MID 173, SubID 1

BODY:

1. `MID:uint8==173`
2. `SUBID:uint8==1`
3. `TOT: bytes[6]`
4. `CID:uint8`
5. `ALB:uint8` (alignment/dummy)
6. `N:uint16_le` (# of int16 samples)
7. `SAMPLES:int16_le[N]`
8. `AEF: remaining bytes (may be 0)`

If `AEF` present: it is “copy of part of MID 1 after CID (AE features + TD data)”. Deterministic parse option:

* Treat `AEF` as a buffer and parse `AE_FEATURES` then `HIT_PARAMETRICS` exactly as MID 1 step (4)–(5), using current state (`event_chids`, CHID 22 rules, V3 flag).

> IMPORTANT: Do not do what the reference reader does (read all remaining bytes as samples). Use `N` to bound samples.

## 4.2 Digital AE power spectrum — MID 173, SubID 3

Reserved; parse payload as raw bytes.

## 4.3 Digital AE data filter definition — **MID 173, SubID 29**

This is labeled “ID 172,29” in the section heading, but the on-wire ID byte is shown as **173**. Treat **173,29** as authoritative.

BODY:

* `MID:uint8==173`
* `SUBID:uint8==29`
* then an “exact copy” of the *body* of MID 29, except with signed limits in msec:

  * `FS:uint8`
  * repeat FS:

    * `FID:uint8`
    * `CID:uint8`
    * `TYPE:uint8` (1=SCSH)
    * `CHID:uint8` (0 rejects all waveforms)
    * `LOW:int32_le` (msec)
    * `HIGH:int32_le` (msec)

## 4.4 TRA hardware setup — MID 172, SubID 42

BODY:

* `MID:uint8==172`
* `SUBID:uint8==42`
* `MVERN:uint16_le` (100 means v1.00)
* `ADT:uint8` (A/D converter data type; 2=16-bit signed)
* `SETS:uint8` (number of TRA channel setups)
* `SETS_PAD:uint8` (present in some tables; keep as raw/unused)
* `SLEN:uint16_le` (size of each setup in bytes)
* Then `SETS` repetitions of a setup struct (most fields are 2 bytes):

  * `CHID:uint16_le` (0 means applies to all channels)
  * `HLK:uint16_le`
  * `HITS:uint16_le`
  * `SRATE:uint16_le`
  * `TMODE:uint16_le`
  * `TSRC:uint16_le` (TSRC.b2 may carry “1=digital”)
  * `TDLY:int16_le` (negative pretrigger)
  * `MXIN:uint16_le`
  * `THRD:uint16_le`

## 4.5 Compatibility: “173,42 hardware setup” observed in the wild

Some MISTRAS workflows embed a TRA hardware setup using `MID==173` and `SUBID==42` (often inside other containers).

**Non-heuristic compatibility rule:**

* If `MID==173` and `SUBID==42`, parse the remainder with the **same layout as 172,42** (§4.4), except that the leading bytes are `173,42`.

---

# 5. Message 42 submessage stream (hardware setup container)

MID 42 contains submessages encoded as:

* `LSUB:uint16_le`
* `SUBPAYLOAD: bytes[LSUB]`
* Inside `SUBPAYLOAD`:

  * `SUBID:uint8`
  * `SUBBODY: bytes[LSUB-1]`

SubIDs include: 100, 27, 102, 133, 5, 6, 106, 28, 29, 110, 111, 124, 101.

If vendor-specific `SUBID==173` appears inside MID 42, treat its `SUBBODY` as:

* `SUBID2:uint8`
* then payload for that `SUBID2` (e.g., `SUBID2==42` parse as §4.4 with a `173,42` header already consumed).

---

# 6. MID 211 — Time mark and extended time mark

Implement per Appendix II. Length-based branch:

* `LEN==5`: RTOT is 4 bytes
* `LEN==7`: RTOT is 6 bytes
* `LEN>7`: extended, includes appended embedded message (itself a `uint16_le LEN + BODY` block)

---

# 7. Known ambiguity list (current)

1. Optional parametric extra byte `(V3)` in parametric entries: requires config flag.
2. MID 102 size/semantics: underspecified.
3. TRA 172,42 exact packing around ADT/SETS padding varies in documentation; keep byte-accurate by consuming exactly what the message provides using `SLEN` and `SETS`.
4. “172,29” heading vs “173,29” table: treat on-wire `173,29` as authoritative; optional strict mode may reject any `172,29` if ever encountered.

---

# 8. Implementation checklist for an AI coding agent

* Implement a streaming reader: read `LEN`, then read `BODY`.
* Dispatch by `MID` with the `[40..49]` pad rule.
* Maintain state for MID 5, MID 6, MID 109.
* For MID 1 and AEF parsing: require `event_chids` to be known; CHID 22 requires MID 109.
* For MID 173,1: always respect `N` to bound sample bytes; parse `AEF` separately.
* For any unrecognized ID/subID: store raw payload and advance exactly `LEN` bytes.
