# MistrasDTA Parser — Gap Analysis

**Date:** January 30, 2026

---

## MID 1 — AE Hit Data

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| V3 (Cycle Counter MSB) | u8 optional | Not read (spec shows as conditional) |
| Trailer | 2 bytes | Discarded (undocumented) |

**CHID gaps:** 7 (RMS 8-bit, scale /20.0), 9, 11, 12, 14, 15, 16 not in lookup tables — will misalign if present.

---

## MID 2 — Time-Driven Sample Data

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| V3 (Cycle Counter MSB) | u8 optional | Not read |

**Scaling gap:** CHID 20 (SIG STRENGTH) not scaled ×3.05 in time-driven FV decode.

---

## MID 3 — User-Forced Sample Data

**Status:** Partial (same as MID 2)

---

## MID 4 — GCC Error Detection

**Status:** Not Implemented

---

## MID 8 — Continued File

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| DOS_TIME_DATE | 8 bytes | Discarded |
| REMAINDER | embedded setup | Discarded (not parsed recursively) |

---

## MID 11 — Reset Absolute Time

**Status:** Not Implemented (silently skipped, 0-byte payload)

---

## MID 15 — Abort Data Acquisition

**Status:** Not Implemented

---

## MID 16 — Alarm Data

**Status:** Not Implemented

---

## MID 41 — Product Definition

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| PVERN | u16 | Discarded |

---

## MID 42 — Hardware Setup

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| MVERN | u16 | Discarded |

### SubID 5 — Event Data Set Definition

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| MAX_HIT_PID | u8 | Discarded |

### SubID 19

**Status:** Not Implemented (no spec)

### SubID 20

**Status:** Not Implemented (reserved for Pre-amp Gain)

### SubID 22 — Set Threshold

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| FLAGS | u8 | Discarded (observed: 0x06) |

### SubID 23 — Set Gain

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| FLAGS | u8 | Discarded (observed: 0x14) |

### SubID 28 — Alarm Definition

**Status:** Not Implemented (spec available)

### SubID 29 — AE Filter Definition

**Status:** Not Implemented (spec available)

### SubID 30 — Delta-T Filter Definition

**Status:** Not Implemented (spec available)

### SubID 33

**Status:** Not Implemented (reserved)

### SubID 100 — Begin Setup

**Status:** Not Implemented (marker only)

### SubID 101 — End of Setup

**Status:** Not Implemented (marker only)

### SubID 102 — Set Demand Sampling Rate

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| PAD | u16 | Discarded |

### SubID 103

**Status:** Not Implemented (no spec)

### SubID 106 — Group Definition

**Status:** Not Implemented (spec available)

### SubID 109 — Partial Power Setup

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| SEGMENT_TYPE | u8 | Discarded |
| PAD | 3 bytes | Discarded |
| BANDS | N_SEG × 8 bytes | Discarded (frequency band defs) |

### SubID 110 — Group Parametric Assignment

**Status:** Not Implemented (spec available)

### SubID 111 — Group Settings

**Status:** Not Implemented (spec available, wraps bodies of IDs 22-26)

### SubID 115

**Status:** Not Implemented (no spec)

### SubID 124 — End of Group Settings

**Status:** Not Implemented (marker only)

### SubID 133 — Pulser Rate

**Status:** Not Implemented (spec available)

### SubID 136 — Analog Filter Definition

**Status:** Not Implemented (spec available)

### SubID 137 — Analog Filter Selection

**Status:** Not Implemented (spec available)

### SubID 138 — Analog Parametric Setup

**Status:** Not Implemented (spec available)

### SubID 139 — Cycle Counter Setup

**Status:** Not Implemented (spec available)

### SubID 146

**Status:** Not Implemented (no spec)

### SubID 148

**Status:** Not Implemented (no spec, 4370 bytes observed)

### SubID 151

**Status:** Not Implemented (no spec)

### SubID 154

**Status:** Not Implemented (no spec)

### SubID 172 — Digital Filter Setup

**Status:** Not Implemented (body unspecified)

### SubID 173 — TRA Setup Container

**Status:** Partial (only SubID2=42 decoded)

#### SubID 173.42 — TRA Hardware Setup

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| MVERN | u16 | Discarded |
| ADT | u8 | Discarded (A/D data type) |
| SETS | u8 | Discarded |
| SETS_PAD | u8 | Discarded |
| SLEN | u16 | Discarded |
| HLK | u16 | Discarded (hit lockout) |
| HITS | u16 | Discarded |
| TMODE | u16 | Discarded (trigger mode) |
| TSRC | u16 | Discarded (trigger source) |
| MXIN | u16 | Discarded (max input voltage) |
| THRD | u16 | Discarded (trigger threshold) |

### SubID 176

**Status:** Not Implemented (no spec)

---

## MID 43 — Graph Definition

**Status:** Not Implemented (INI file only per spec)

---

## MID 44 — Location Definition

**Status:** Not Implemented

---

## MID 45 — Acquisition Control

**Status:** Not Implemented (spec available)

---

## MID 46 — Autorun Message

**Status:** Not Implemented (spec available)

---

## MID 48 — Filtered File Information

**Status:** Not Implemented (spec available)

---

## MID 49 — Product Specific Information

**Status:** Not Implemented (spec available)

---

## MID 109 — Partial Power Setup (standalone)

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| SEGMENT_TYPE | u8 | Discarded |
| RSV1, RSV2 | 2×u16 | Discarded |
| Segment definitions | N_SEG × 8 bytes | Discarded |

---

## MID 116

**Status:** Not Implemented (no spec, 12–7187 bytes observed)

---

## MID 128 — Resume / Start Test

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| RTOT | 6 bytes | Discarded (control event time) |
| STATUS | u8 | Discarded (undocumented, observed: 0x01) |

---

## MID 129 — Stop Test

**Status:** Partial (same as MID 128)

---

## MID 130 — Pause Test

**Status:** Partial (same as MID 128)

---

## MID 131 — Configuration Status/Report

**Status:** Not Implemented (spec available)

---

## MID 132 — Status Report

**Status:** Not Implemented (spec available)

---

## MID 171 — TRA Messages

**Status:** Not Implemented (spec available, multiple versions)

---

## MID 172 — Digital AE Filter/Setup

**Status:** Not Implemented (SubIDs 29, 42 have spec)

---

## MID 173 — AEDSP/TRA Extended Messages

**Status:** Partial (only SubID 1 decoded)

### SubID 1 — Digital AE Waveform Data

**Status:** Partial

| Field | Type | Gap |
|-------|------|-----|
| ALB | u8 | Discarded (alignment byte) |
| N | u16 | **Not read** (spec shows sample count before samples) |
| AEF | variable | **Not read** (spec shows AE features appended after samples) |

**Note:** Code assumes all remaining bytes after ALB are samples.

### SubID 3 — Power Spectrum Data

**Status:** Not Implemented

### SubID 29 — Digital Filter Setup

**Status:** Not Implemented

### SubID 42 — Hardware Setup

**Status:** Not Implemented

---

## MID 211 — Time Mark

**Status:** Not Implemented
