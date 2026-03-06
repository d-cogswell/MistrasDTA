![](_page_0_Picture_0.jpeg)

# **APPENDIX II**

**Data File Definition for AEwin™**

This document gives the format of the AEwin data files. These files are created by the AEwin when acquiring data in AUTODUMP mode. When data is dumped to disk, a file specified by the user, with the extension .DTA (e.g., TEST0000.DTA) is created.

The data file consists of three basic types of variable length messages. These messages are (I) Products Definition Messages (II) Test Setup Messages and (III) Messages from the test. Each message has two bytes for length, 1 byte for ID (2 bytes for ID followed by 2 bytes for format version number in messages with ID41 to 44 only) and a variable length body. The messages 41-44 are special messages in that they are also included in the INI files.

Page intentionally left blank

# **PAC MESSAGE DEFINITIONS**

# **Contents**

| Section                          | Page |
|----------------------------------|------|
| 1. INTRODUCTION                  | 3    |
| 2. GENERAL MESSAGE INFORMATION   | 4    |
| 3. DETAILED MESSAGE DESCRIPTIONS | 8    |
| 4. SUMMARY                       | 32   |

Page intentionally left blank

# **PAC MESSAGE DEFINITIONS**

## **1. INTRODUCTION**

This document describes the messages used to communicate between various processes within the data acquisition and replay environment of PAC products including; SPARTAN, MISTRAS, DISP, PCI-2, PCI-8(SAMOS), and Digital AIMS ADTI. These messages may be commands and/or data depending on where they are generated within the system and where they are sent. The same types of messages are saved in the data files.

The message structure was developed for the first SPARTAN implementation to allow communication between the SPARTAN main chassis (GCC) and High End (HE), but it has been extended as our products have matured and have grown technically. Other general principals have been applied when assigning message ID numbers: the IDs from 200 to 255 were reserved for applications, ID = 0 is illegal, once an ID assigned a meaning and implemented for some product, it can only be used by a different product for the same function. By the time the second application program was designed it seemed that the 55 message ID values would quickly be used up, and therefore later application messages have added structure by using a message "subfunction" byte (e.g., 172, 42 for MI-TRA.

Once assigned, we try to avoid changing the meaning of a message ID according to where it is at a given time or which direction it is going. Thus, AE data messages always have a message ID of 1 and the Resume message has an ID of 128. Commands and messages may be built up using other messages by "sequence" or by using an new id to combine a series of messages into a "single" block. The "Start" command is actually 2 commands; a Clear Time of Test Clock command and a "Resume" command. The "Resume" command and the "Resume" message share the same message ID; user commands are sent to the GCC as 1 byte versions of message and the returned (data) message with the Time of Test confirms that the GCC has completed the requested action. So the "command" message is "hidden" from the rest of the world. Any subsequent use of the message may or may not use the time of test attached to it depending to the application. The "Resume" which is a start, normally has its time of test IGNORED (the program treats it as 0 since it follows a Clear Clock) but subsequent "Resume" messages have a new time of test which the programs can use.

This structure has been extended for the TRA products and the AEDSP software.

## **2. GENERAL MESSAGE INFORMATION**

### **Classes of Messages**

#### *(I) HARDWARE STATUS AND CONTROL Messages [[ NOT IN THE DATA FILES]]*

#### *(II) PRODUCT SPECIFIC Messages*

These are messages, only found in the data files, which have a general form but their details will vary with the products.

Product Identification Message: Identifies the Product and its Version.

Product Special Message: Test, Product specific information PRIMARILY for post test report generation but may contain configuration information.

Product Post Test Filter Description Message: While the form of this message should be the same for all the products, the details of the filter process are product specific. Similar to the setup message, THIS OUGHT TO CONTAIN ALL THE INFORMATION FOR THE FILTER AND ALSO SERVE AS THE BASE FOR ANY CODE TO SAVE OR RESTORE FILTERS FOR FUTURE USE.

#### *(III) TEST SETUP Messages*

These messages are used to set up the system hardware and the test parameters. The Test Setup messages include Test Label, Date and Time, Location Setup and the Hardware Setup Messages.

Test Label: Title or Name of the test.

Date and Time: Date and Time of Day (ASCII string) of start of test.

Location Setup: Defined in Location version data file only.

Hardware Setup: The Hardware setup message is group of setup messages.

#### *(IV) Messages from the TEST*

- (A) DATA Messages: DATA messages include AE Hit Data, Time Driven Data, Sample Data, Alarm Data and User Comment Messages.
- (B) CONTROL Messages: PAUSE, RESUME, STOP, and ABORT.

#### *(V) Synchronization and Control Messages for "external" tasks*

These include commands sent to the mGCC or AEDSP processors.

#### *(VI) Data File Messages*

Typical raw data (.DTA) files contain the following messages:

| Type | Id  | Description of Message Body  |
|------|-----|------------------------------|
| II   | 41  | Product Definition           |
| III  | 7   | Test Label                   |
| III  | 99  | Time of Day of start of test |
| III  | 44  | Location setup message       |
| III  | 42  | Hardware setup message       |
| V    | 128 | Start/Resume test            |
| IV   | 1   | AE hit data                  |
| IV   | 2   | Time Driven data             |
| IV   | 3   | Sample data                  |
| IV   | 7   | User Comment                 |
| IV   | 130 | Test Pause                   |
| IV   | 129 | Test Stop                    |
| IV   | 15  | Test Abort message           |

#### **Message Format**

Each message has two bytes for length and a body of that length of bytes. Thus the total length of the "transmission" is Length+2 bytes. The body of the message starts with a message id byte. Unfortunately it was felt that the software would be easier if the messages which "define" the file (Presently they have ID values from 40 to 49) if the ID space was an integer quantity. In fact, because the files contain messages with 1 byte id values, all the message IDs should be identified by the byte value. The legal range for an ID is 1 to 255.

Special setup files would contain only (primary) messages with 2 byte ID values for example the ".INI" files for setup of LOCAN 420, MISTRAS or SPARTAN 2000 data acquisition and replay. I would expect that we will expand this concept to at least the post test filtering programs when they have to be coded to save and restore user setup information.

The INI file contains the messages:

- 41 Product Definition
- 42 Hardware Setup
- 43 Graph Setup
- 44 Location Group Setup (even in non-location versions)
- 45 Acquisition Control
- 46 Auto Run
- 7 Test Title

and possibly:

49 Product Specific Information

In order to help the user to understand the structure of various types of messages, a set of them from the data file header will be briefly described. This should help to explain the message concept and give a good idea of the structure of a DTA or INI file.

### **ID 41 — ASCII Product Definition (With example values)**

| Field       | Byte(s)               | Notes                                         |
|-------------|-----------------------|-----------------------------------------------|
| LEN         | b1, b2                | 2 bytes                                       |
| ID          | b1= 41 (29H)<br>b2= 00 | Product Definition Message ID<br>high byte of ID (2 bytes) |
| PVERN       | b1= 200 (C8H)<br>b2= 00 | Product version number (200)<br>(2 bytes)   |
| Prod_string | "LOCAN-AT",CR,LF,"VERSION 2.00",CR,LF | ASCII Product name, CR, LF, Version number, CR, LF |

### **ID 7 — User Comments/Test Label**

| Field | Byte(s)      | Description                    |
|-------|--------------|--------------------------------|
| LEN   | b1, b2       | 2 bytes                        |
| ID    | b1=7 (07H)   | User Comments or Test Label    |
| TEXT  | b1..bn       | Text in ASCII                  |

### **ID 99 — Time and Date Of Test Start**

| Field            | Byte(s)       | Notes                          |
|------------------|---------------|--------------------------------|
| LEN              | b1, b2        | 2 bytes                        |
| ID               | b1= 99 (63H)  | Time and date of test start ID |
| "Sun Jul 03, "<br>"08:49:55 1988" | (For Example) | ASCII date string,<br>ASCII time and year string. |

### **ID 44 — Location Definition**
**(Dummy message in Non-Location version)**

| Field | Bytes        | Notes                        |
|-------|--------------|------------------------------|
| LEN   | b1, b2       | 2 bytes                      |
| ID    | b1= 44 (2CH)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes)       |

The MISTRAS DTA file also includes two TRA setup messages when the wave forms are being recorded.

### **ID 173,42 — Hardware Setup**

### **ID 172,29 — Digital Filter Setup**

### **ID 42 — Hardware Setup**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 42 (2AH)<br>b2= 00 | Hardware Setup ID<br>high byte of ID (2 bytes) |
| MVERN | b1= 200 (C8H)<br>b2= 00 | Message version number<br>(0 filled) |
| | | |
| LSUB 1<br>SUBID 1<br>SUBMSG 1 | | length of submessage 1 (2 bytes)<br>submessage 1 ID ( 1 bytes),<br>submessage 1 body. |
| \| | | |
| LSUB I<br>SUBID I<br>SUBMSG I | | length of submessage I (2 bytes),<br>submessage I ID ( 1 bytes),<br>submessage I body. |
| \| | | |
| LSUB n<br>SUBID n<br>SUBMSG n | | length of submessage n ( 2 bytes),<br>submessage n ID ( 1 bytes),<br>submessage n body |

Note: Submessages are:

| Submessage                    | ID          |
|-------------------------------|-------------|
| Start of Test Setup           | ID = 100 ( 64H ) |
| Set Sampling Interval         | ID = 27 ( 1BH )  |
| Set Demand Sampling Rate      | ID = 102 ( 66H ) |
| Pulser Rate                   | ID = 133 ( 85H ) |
| Event Data Set Definition     | ID = 5 ( 05H )   |
| Demand Data Set Definition    | ID = 6 ( 06H )   |
| Group Definition              | ID = 106 ( 6AH ) |
| Alarm Definition              | ID = 28 ( 1CH )  |
| AE Filter Definition          | ID = 29 ( 1DH )  |
| Group Parametric Assignment   | ID = 110 ( 6EH ) |
| Group Settings                | ID = 111 ( 6FH ) |
| End of Group Settings         | ID = 124 ( 7CH ) |
| End of Setup                  | ID = 101 ( 65H ) |

## **3. DETAILED MESSAGE DESCRIPTIONS**

The following is a list in numeric order of the messages. Each message has the two bytes for length explicitly shown, 1 byte for ID. (Remember there are a few messages with 2 bytes for the ID field EVEN THOUGH the ID is 1 byte long. They are shown with the O BYTE in the ID field.

Notation:

| | |
|-|-|
|AM | Acquisition Module # - 'the number (of)'|
|PID|  the Parametric Channel ID|
|CID|  an AE channel ID|
|CHID|  the AE characteristic ID number (List after Message #5) b1,b2,b3,b4,...<br>bytes (least significant first)|
|V|  value|
|RTOT|  Time of test relative to the start of test|
|PVERN|  Product version number MVERN - Message version number|
|LEN|  length of a message|
|Internal|  Defined but never appear in the data file|
|Defined|  Assigned for some product(s) may appear in a data file at some later date|
|Not Used|  Reserved by PAC for future use|

#### **Setup Message Units**

| | |
|-|-|
|Threshold and Gain Units| dB |
|HDT, Rearm Time| 2 µsec |
|PDT| 1 µsec |
|Sampling Interval| 1 msec|

[Also MID 102 is in msec steps]

msec == milliseconds

µsec == microseconds

#### **Front End Filter Types (ICC filtering)**

SCSH Single Channel, Single Hit

#### **GCC or Parametric Voltage Filtering**

#### **Alarms**

| | |
|-|-|
|SCSH|Single Channel, Single Hit|
|SCTC|Single Channel, Test Cumulative|
|GTC|All Channels (Group), Test Cumulative|
| |Parametric|

### **ID 1 — AE Hit or Event Data**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=1 (01H) | AE Hit ID |
| RTOT | b1..b6 | Relative time of test |
| CID | b1 | AE Channel Number |
| | | |
| V1<br>\|<br>Vm | b1..bn<br>\|<br>b1..bx | Value of First AE Characteristic<br>as many as defined<br>Value of Last AE Characteristic |
| | | |
| PID1<br>V1<br>V2<br>V3 | b1<br>b2<br>b3<br>(b4) | Hit Parametric Channel ID<br>Parametric value (low byte)<br>Parametric value (high byte)<br>Cycle Counter MSB byte |
| \| | | |
| PIDj<br>V1<br>V2<br>V3 | b1<br>b2<br>b3<br>(b4) | Last Hit Parametric Channel ID |

### **ID 2 — "Time Driven" Sample Data**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1 = 2 (02H) | Time Driven ID |
| RTOT | b1..b6 | Relative time of test |
||||
| PID1<br>V1<br>V2<br>(V3) | b1<br>b2<br>b3<br>(b4) | First Parametric Channel ID<br>Parametric value (low byte)<br>Parametric value (high byte<br>(Cycle Counter MSB byte) |
| \| | | |
| PIDj<br>V1<br>V2<br>V3 | b1<br>b2<br>b3<br>(b4) | Last Parametric Channel ID |
| | | |
| CID | b1 | ID of the first channel in use |
| V1<br>\|<br>Vm | b1..bn<br>\|<br>b1..bx | Value of First AE Characteristic<br><br>Value of Last AE Characteristic |
| | | end of first channel |
| \| | \| | |
| CID | b1 | ID of the last channel in use |
| V1<br>\|<br>Vm | b1..bn<br>\|<br>b1..bx | Value of First AE Characteristic<br><br>Value of Last AE Characteristic |
| | | end of last channel |
||||
| | | end of Time data set |

### **ID 3 — "User Forced" Sample Data — Now also a GCC Command**

 The message body is the same as the "Time Driven" Sample Data except that the ID changes from 2 to 3. The GCC forces one after all PAUSE commands or when the user invokes the keypad function.

### **ID 4 - GCC Module Detection of Error**

**Defined for mGCC Ver. 1.53 and later.**<br>
**(V1.8+ planned to have control from H.E.)**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1 = 4 (04H) | GCC detection of error |
| Error Code | b1 | Error identification |
| Error Bytes | eb1..ebX | Error information. May be text or garbled message from ICC. |

**Error Codes**

| Code | Description |
|------|-------------|
| b1 = 1 | This is ICC-GCC transmission error. Bad CID, bad MID or bad message length. MID is part of the fifo information (1,2). Also the fifo presents a total byte count = 2 + message length. The CID can only be the ICC's low or high channel. |
| eb1...ebX | The message that was not received correctly |
||
| b1 = 2 | Internal GCC error detection: Error message displayed on LCD. {May be only in debug version.} and saved in error bytes field. |
| eb1...ebX | The text of the front panel error message. |
||
| b1 = 100 and<br>200-203 | Used by the Combustion Engineering special software. |

### **ID 5 — Event Data Set Definition**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=5 (05H) | Event Data set definition ID |
| # CHID | b1 | Number of AE characteristics |
| | | |
| V1<br>\|<br>Vm | b1<br>\|<br>b1 | Value of CHID 1<br><br>Value of CHID m (last one) |
| | | |
| # PID | b1 | Maximum number of Hit parametric |

#### **AE Characteristics Presently Defined or Planned**

| CHID Value            | Size | Item                                           |
|-----------------------|------|------------------------------------------------|
| 1                     | 2    | Rise Time of AE signal                         |
| 2                     | 2    | AE Counts to Rise Time (or "Counts to peak")   |
| 3                     | 2    | Total AE counts                                |
| 4                     | 2    | Energy counts (ASTM has another name for this) |
| 5                     | 4    | Duration                                       |
| 6                     | 1    | Amplitude                                      |
| 7                     | 1    | RMS (volts) - After both were defined, the H/W |
| 8                     | 1    | ASL (dB)<br>- design allowed only 1 at a time. |
| 9                     | 1    | Gain                                           |
| 10                    | 1    | Threshold                                      |
| 11                    | 1    | Pre-Amp Current                                |
| 12                    | 4    | Lost Hits (per channel) WAS Overlap flag       |
| 13                    | 2    | Average Frequency (kHz) (1000* [3]/[5])        |

**Tentative Assignments**

| CHID Value            | Size | Item                                           |
|-----------------------|------|------------------------------------------------|
| 14                    | 2    | Reserved (2 byte duration)                     |
| 15                    | 6    | Reserved (6 byte TOT)                          |
| 16                    | (4)  | Reserved (Vari. length TOT with Message 12)<br>(Example: Msg12 used in TI for 4 byte TOT.) |

**This is clearly a system with expansion capability, but we will need to try to do the expansion in an intelligent manner.**

### **ID 6 — Time Driven/Demand Data Set Definition**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2<br>b2 | 2 bytes<br>High byte value |
| ID | b1=6 (06H) | Demand Data Set Definition ID |
|
| # CHID | b1 | Number of AE char. in the demand data set |
| V1<br>\|<br>Vn | b1<br>\|<br>b1 | First CHID<br><br>Last CHID |
|
| # PID | b1 | Number of Parametric in user |
| V1<br>\|<br>Vn | b1<br>\|<br>b1 | First PID<br><br>Last PID |

### **ID 7 — User Comments/Test Label**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=7 (07H) | User Comments or Test Label |
|  | b1..bn | Text in ASCII |

### **ID 8 — Message for Continued File  TYPE A**

**This one is at the END of the file and indicates that there was more data when space ran out on the disk.**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=8 (08H) | File continuation |
|  | b1..b8 | Time & Date of continuation in DOS format so that 'gaps' in time in the continuation can be detected. {CX,DX of DOS Time, CX,DX of DOS Date INT 21 DOS calls.} |

### **ID 8 — Message for Continued File TYPE B**

**Appears only at the beginning of a file and indicates that the file is NOT the start of a test.**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=8 (08H) | File continuation |
|  | b1..b8 | Time of continuation in DOS format exactly the same as written at the end of the preceding file. |

**{complete setup record from the first file of the test}**

**This is all the messages up to the "Start Test Command" which were written at the beginning of the first file. If that file were to be unavailable, then this allows this file to be analyzed.**

### **ID 9/ID 10 — Not Used**

### **ID 11 — Reset Absolute Time Clock**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=11 (0BH) | Reset Absolute Time Clock |

### **ID 12 — Define the Size of the Clock Base ("Tick") Reserved**

### **ID 13/ID 14 — Not Defined**

### **ID 15 — Abort Data Acquisition**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=15(0FH) | Abort data acquisition/transfer ID |
| RTOT | b1..b6 | Relative time of test |

### **ID 16 — Alarm Data**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1=16(10H) | Alarm message ID |
| RTOT | b1..b6 | Relative time of test |
| Level | b1 | 0 = warning, 1 = trip [C.E. 16,17] |
| AID | b1 | Alarm ID |
| CID | b1 | Channel number that generated the alarm (0 if time alarm (C.E.)) |
| V | b1..b4 | Value of the alarm (LSB) |

### **ID 17 — Reserved**

### **ID 18 — Reserved**

### **ID 19 — Reserved**

### **ID 20 — Reserved for Recording Pre-amp Gain**

**TRA 212 uses this as a sub-function code.**

### **ID 21 — Reserved**

### **ID 22 — Set Threshold**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 22 (16H) | Set threshold value (dB) ID |
| CID | b1 | Which channel |
| V | b1 | byte value for threshold<br>(MSBit = 1 float, = 0 fix) |
| FLAGS | b1 | Unknown flags/mode (observed: 0x06) |

### **ID 23 — Set Gain**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 23 (17H) | Set gain value (dB) ID |
| CID | b1 | Which channel |
| V | b1 | 1 byte value for gain |
| FLAGS | b1 | Unknown flags/mode (observed: 0x14 = 20) |

### **ID 24 — Set Hit Definition Time**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 24 (18H) | Set Hit Definition Time (mS) ID |
| CID | b1 | Which channel |
| V | b1 | low byte value |
| V | b2 | high byte value in steps of 2 mS |

### **ID 25 — Set Hit Lockout Time**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 25 (19H) | Set Hit Lockout Time (mS) ID |
| CID | b1 | Which channel |
| V | b1 | low byte value |
| V | b2 | high byte value in steps of 2 mS |

### **ID 26 — Set Peak Definition Time**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 26 (1AH) | Set Peak Definition Time (mS) ID |
| CID | b1 | Which channel |
| V | b1 | low byte value |
|  | b2 | high byte value in steps of 1 mS |

### **ID 27 — Set the Sampling Interval**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 27 (1BH) | Set the sampling interval (mS) ID |
| V | b1 | low byte value |
| V | b2 | high byte value in steps of 1 mS |

### ### **ID 28 — Alarm Definition**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 28 (1CH) | Alarm definition ID |
| j | b1 | Number of alarm definition sent |
|(below repeats j times)|
| Alarm # | b1 | Which one is being defined |
| CID | b1 | Which channel |
| Type code | b1 | Type of alarm |
| CHID # | b1 | AE characteristic used |
| Level 1 | b1..b4 | Warning level |
| Level 2 | b1..b4 | Trip level |

### **ID 29 — AE Filter Definition**

| LEN       | b1, b2       | 2 bytes                           |         |
|-----------|--------------|-----------------------------------|---------|
| ID        | b1= 29 (1DH) | AE filter definition ID           |         |
| k         | b1           | Number of filter definitions sent |         |
| (below repeats k times) |
| Filter #  | b1           | Which one is being defined        |         |
| CID       | b1           | Which channel                     |         |
| Type code | b1           | Type of filter (scsh only)        |         |
| CHID #    | b1           | AE characteristic used            |         |
| Level 1   | b1..b4           | Low level                         |         |
| Level 2   | b1..b4           | High level                        |         |

### **ID 30 — Delta-T AE Filter Definition**

(INI and DTA, AEDSP board)

| Field   | Bytes   | Description                                      |
|---------|---------|--------------------------------------------------|
| LEN     | b1, b2  | 2 bytes                                          |
| ID      | b1 = 30 | Location definition ID                           |
| FS      | b1        | # of filter definitions to follow         |
|(below repeats FS times)
| FID     |         | 1 byte Delta-T filter ID number                  |
| BDID    | b1        | Board number (2 channels per board)<br>0 = all boards<br>1 = first board (channels 1,2)<br>2 = second board (channels 3,4), etc              |
| TYPE    | b1        | type of delta‑T = accept events (hit pairs) with delta‑T between LOW and HIGH<br>reject other events<br>Only one type presently defined                  |
| INDHITS | b1        | independent hit control<br>0 = reject independent hits (delta‑T over CAL)<br>1 = accept independent hits                      |
| LOW     | b1..b4        | Low level in usec (signed long integer)  |
| HIGH    | b1..b4        | High level in usec (signed long integer) |
| EDT     | b1..b4        | Calibration time in usec (unsigned long) |

### **ID 31 — Reserved**

### **ID 32 — Reserved**

### **ID 33 — Reserved**

### **ID 34 — Reserved**

### **ID 35 — Reserved**

### **ID 36 — Reserved**

### **ID 37 - INI Write Protect Password**

**(INI file)**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1 = 37 | Location definition ID |
| MVERN |  | 1 byte  = Message version*100 e.g., V1.00=100 |
| TOT |  | 6 bytes  (least significant first) Time of hit |
| SZPW |  | n bytes  Zero terminated string |

### **ID 38 - Test Information**

**(INI and DTA files)**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | 1, b2 | 2 bytes |
| ID | 1 = 38 | Location definition ID |
| MVERN |  | 1 byte  = Message version*100 e.g., V1.00=100 |
| ENEDIT |  | 1 byte  Enable edit of title fields |
| EDISPF9 |  | 1 byte  Enable display of test info.at start of test |
| ZTITLE |  | n bytes  Zero terminated string title |
| SZFIELD |  | n bytes  Zero terminated string field |

**These two fields repeat for the duration of the message. If there is no entry, the field will be 1 '0' byte as a placeholder.**

### **ID 39 — Reserved**

**(Not Implemented)**

### **ID 40 — Reserved**

**(Not Implemented)**

### **ID 41 — Product Definition Message**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 41 (29H)<br>b2= 00 | ASCII Product Definition ID<br>high byte of ID (2 bytes) |
| PVERN | b1= pv#<br>b2= 00 | Product version number (2 bytes)<br>MESSAGE FORMAT=100*Product ID ONLY FOR THIS ONE |
| TEXT | a1..an | ASCII Product name, CR, LF, Version number, CR, LF|

### **ID 42 — Hardware Setup**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1 = 42 (2AH)<br>b2 = 00 | Hardware Setup ID<br>high byte of ID (2 bytes) |
| MVERN | b1 = fv#<br>b2= 00 | Message version number (2 bytes)<br>(200. at the present) |
| | | |
| LSUB 1<br>SUBID 1<br>SUBMSG 1 | | length of submessage 1 (2 bytes),<br>submessage 1 ID ( 1 bytes),<br>submessage 1 body |
| \| | | |
| LSUB I<br>SUBID I<br>SUBMSG I | | length of submessage I (2 bytes),<br>submessage I ID ( 1 bytes),<br>submessage I body |
| \| | | |
| LSUB n<br>SUBID n<br>SUBMSG n | | length of submessage n (2 bytes),<br>submessage n ID ( 1 bytes),<br>submessage n body. |

**Note: Submessages are:**

| Submessage | ID |
|------------|----|
| Start of Test | ID = 100 ( 64H ) |
| Set Sampling Interval | ID = 27 ( 1BH ) |
| Set Demand Sampling Rate | ID = 102 ( 66H ) |
| Pulser Rate | ID = 133 ( 85H ) |
| Event Data Set Definition | ID = 5 ( 05H ) |
| Demand Data Set Definition | ID = 6 ( 06H ) |
| Group Definition | ID = 106 ( 6AH ) |
| Alarm Definition | ID = 28 ( 1CH ) |
| AE Filter Definition | ID = 29 ( 1DH ) |
| Group Parametric Assignment | ID = 110 ( 6EH ) |
| Group Settings | ID = 111 ( 6FH ) |
| End of Group Settings | ID = 124 ( 7CH ) |
| End of Setup | ID = 101 ( 65H ) |

### **ID 43 — Graph Definition**

**(*.INI file only)**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 43 (2BH)<br>b2= 00 | Graph Definition ID<br>high byte of ID (2 bytes) |
| MVERN | b1= fv#<br>b2= 00 | Message version number (2 bytes ) |
| Product Specific Information | | |

### **ID 44 — Location Definition**

**(if found in a non-location data file, length is 1 or 2).**

| Field | Bytes | Notes |
|-------|-------|-------|
| LEN | b1, b2 | 2 bytes |
| ID | b1= 44 (2CH)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes) |
| MVERN | b1= 200 (C8H)<br>b2= 00 | Message version number (2 bytes ) |
| Product Specific Information | | |

### **ID 45 — Acquisition Control Information**

**(in the Multichannel AT products, "F8" information)**

| Field                        | Bytes                  | Notes                                        |
|------------------------------|------------------------|----------------------------------------------|
| LEN                          | b1, b2                 | 2 bytes                                      |
| ID                           | b1= 45 (2DH)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes) |
| MVERN                        | b1= fv#<br>b2= 00      | Message version number (2 bytes)             |
| Product Specific Information |                        |                                              |

### **ID 46 — Autorun Message — "Command" for Acquisition Program —**

**(Product specific information)**

| Field                        | Bytes                  | Notes                                        |
|------------------------------|------------------------|----------------------------------------------|
| LEN                          | b1, b2                 | 2 bytes                                      |
| ID                           | b1= 46 (2EH)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes) |
| MVERN                        | b1= fv#<br>b2= 00      | Message version number (2 bytes)             |
| Product Specific Information |                        |                                              |

### **ID 47 — Reserved**

### **ID 48 — Filtered File Information**

| Field        | Bytes                  | Notes                                                                                   |
|--------------|------------------------|-----------------------------------------------------------------------------------------|
| LEN          | b1, b2                 | 2 bytes                                                                                 |
| ID           | b1= 48 (30H)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes)                                     |
| MVERN        | b1= fv#<br>b2= 00      | Message version number (2 bytes)                                                        |
| Text follows |                        | Product specific subkeys & maybe some product<br>specific keys (see Appendix A, Part 1) |

### **ID 49 — Special Product Specific Information**

| Field                        | Bytes                  | Notes                                        |
|------------------------------|------------------------|----------------------------------------------|
| LEN                          | b1, b2                 | 2 bytes                                      |
| ID                           | b1= 49 (31H)<br>b2= 00 | Location Definition ID<br>high byte of ID (2 bytes) |
| MVERN                        | b1= fv#<br>b2= 00      | Message version number (2 bytes)             |
| Product Specific Information |                        |                                              |

Note: Messages from 50 to 53 are defined in some versions of LOCAN AT software. These messages will not be supported in LOCAN AT version 2.00 and higher.

### **ID 50 — Reserved**

### **ID 51 — Reserved**

### **ID 52 — Reserved**

### **ID 53 — Reserved**

### **ID 54 to ID 98 — Not Used**

**(See 59 (V1.8) and C.E. specific MIDs)**

### **ID 59 — Turn Off Alarm Command from HE to mGCC**

**(Version 1.8 supports this.)**

| Field | Bytes        | Notes          |
|-------|--------------|----------------|
| LEN   | b1, b2       | 2 bytes        |
| ID    | b1= 59 (3BH) | Turn off alarm |

### **ID 99 — Time and Date of Test Start**

| Field                        | Bytes        | Notes                              |
|------------------------------|--------------|------------------------------------|
| LEN                          | b1, b2       | 2 bytes                            |
| ID                           | b1= 99 (63H) | Time and date of test start ID     |
| "Sun Jul 03, "<br>"08:49:55 1988"| (For Example) |              ASCII date string,<br>ASCII time and year string.        |

### **ID 100 — Begin Setup**

| Field | Bytes         | Notes          |
|-------|---------------|----------------|
| LEN   | b1, b2        | 2 bytes        |
| ID    | b1= 100 (64H) | Begin Setup ID |

### **ID 101 — End of Setup**

| Field | Bytes         | Notes           |
|-------|---------------|-----------------|
| LEN   | b1, b2        | 2 bytes         |
| ID    | b1= 101 (65H) | End of Setup ID |

### **ID 102 — Set Demand Sampling Rate**

| Field | Bytes         | Notes                                              |
|-------|---------------|----------------------------------------------------|
| LEN   | b1, b2        | 2 bytes                                            |
| ID    | b1= 102 (66H) | Set Demand Sampling Rate ID                        |
| V     |               | Multiple of Parametric Sampling Rate)              |

### **ID 103 to ID 105 (Not Used)**

### **ID 106 — Define a Group**

| Field  | Bytes         | Notes                            |
|--------|---------------|----------------------------------|
| LEN    | b1, b2        | 2 bytes                          |
| ID     | b1= 106 (6AH) | Define a group ID                |
| Grp #  | b1            | Which group                      |
| # CHNs | b1            | How many channel IDs in list     |
|
| CHID1  | b1            | First channel id                 |
| \|     |               |                                  |
| CHIDn  | b1            | Last channel                     |

### **ID 107 — Reserved**

### **ID 108 and 109 — Not Used**

### **ID 110 — Group Parametrics Assignment**

| Field  | Bytes         | Notes                             |
|--------|---------------|-----------------------------------|
| LEN    | b1, b2        | 2 bytes                           |
| ID     | b1= 110 (6EH) | Group parametrics assignment ID   |
| # PIDs |               | Number of PIDs to follow          |
|
| PID1   | b1            | First PID                         |
| \|     |               |                                   |
| PIDm   | b1            | Last PID                          |

### **ID 111 — Group Settings**

| Field    | Bytes  | Notes                                |
|----------|--------|--------------------------------------|
| LEN      | b1, b2 | 2 bytes                              |
| ID       | b1= 111 | Group settings ID                   |
| j        |        | Number of group messages             |
|
| [body 1] |        | Body of first message (ID # = 22-26) |
| \|       |        |                                      |
| [body j] |        | Last body                            |

### **ID 112 to ID 123 — Not Used**

### **ID 124 — End of Group Setting**

| Field | Bytes         | Notes                   |
|-------|---------------|-------------------------|
| LEN   | b1, b2        | 2 bytes                 |
| ID    | b1= 124 (7CH) | End of group message ID |

### **ID 125 — Internal**

### **ID 126 — Internal**

### **ID 127 — Internal**

### **ID 128 — Resume Test or Start Of Test**

**(Test Start only when the Clear Clock was sent after Legal Setup and no intervening Resume, Stop nor Pause was sent. Normally the HE sends the messages sequentially.)**

| Field            | Bytes                  | Notes                                                                                                   |
|------------------|------------------------|---------------------------------------------------------------------------------------------------------|
| LEN              | b1, b2                 | 2 bytes                                                                                                 |
| ID               | b1= 128 (80H)          | Resume/start a test ID                                                                                  |
| {End of command} |                        |                                                                                                         |
| RTOT             | b1..b6   | Relative time of test added when message is built from the command.<br>ALSO FOR STOP AND PAUSE messages |

### **ID 129 — Stop the Test**

| Field            | Bytes                       | Notes                 |
|------------------|-----------------------------|-----------------------|
| LEN              | b1, b2                      | 2 bytes               |
| ID               | b1= 129 (81H)               | Stop the test ID      |
| {End of Command} |                             |                       |
| RTOT             | b1..b6 | Relative time of test |

### **ID 130 — Pause the Test**

| Field            | Bytes                       | Notes                 |
|------------------|-----------------------------|-----------------------|
| LEN              | b1, b2                      | 2 bytes               |
| ID               | b1= 130 (82H)               | Pause the test ID     |
| {End of Command} |                             |                       |
| RTOT             | b1..b6 | Relative time of test |

### **ID 131 — Configuration Status/Report**

**(Response to Command Mess. 132) NEW definition for PAC Bus 488 Inquire/Report (BOEING)**

| Field      | Bytes              | Notes                                |
|------------|--------------------|--------------------------------------|
| LEN        | b1, b2           | Length of body                       |
| Message ID | b1= 131 (H)        | MID byte                             |
| Prod ID or version | a1..a4                 | ASCII Prod ID code          |
| Prod Ver   | b1, b2                 | Product Version Number (16 bits)     |

**Product specific information follows**

**SPARTAN mGCC Response in version 1.8 is shown below**

| Field | Bytes              | Notes                                            |
|-------|--------------------|--------------------------------------------------|
| LEN   | b1, b2             | 2 bytes                                          |
| ID    | b1= 131            | Status report message ID                         |
|       | b1..b4                 | GCC version string (e.g., V1.8)                  |
|       | b1,b2                 | GCC version number (e.g., 180)                   |
|       | b1..b4                 | ICC version string (e.g., 2.11 or MIX)           |
| STAT  | b1                 | Test state code                                  |
| AECH  | b1                 | Number of active AE channels(=number of bytes to follow) |
|
|       | b1                 | number of first active channel                   |
|       | \|                 |                                                  |
|       | bn                 | number of last active channel                    |
|
| PCH   | b1                 | Number of active parametric channels<br>(= 4 for mGCC, 8 for PACbus)                     |

**The GCC valid states are 0 through 7:**

| State | Description    |
|-------|----------------|
| 0     | Power Up       |
| 1     | In Setup       |
| 2     | Setup Done     |
| 3     | T.O.T cleared  |
| 4     | Active(Acq.)   |
| 5     | Waiting        |
| 6     | Test Paused    |
| 7     | Stopped        |

### **ID 132 — Status Report**

**(Command HE ® GCC) {C.E. only}**

### **ID 133 — Pulser Rate**

| Field | Bytes          | Notes                              |
|-------|----------------|------------------------------------|
| LEN   | b1, b2         | 2 bytes                            |
| ID    | b1= 133 (85H)  | Pulser rate in milliseconds ID     |
| v     | b1<br>b2       | low byte of rate<br>high byte of rate |

### **ID 134 — Reserved**

### **ID 135 — Reserved**

### **ID 136 — Analog Filter Definition**

**(INI and DTA files only, AEDSP software)**

| Field    | Bytes    | Notes                                    |
|----------|----------|------------------------------------------|
| LEN      | b1, b2   | 2 bytes                                  |
| ID       | b1= 136  |                                          |
| AFID     | b1       | First analog multi‑filter ID number      |
|
| HFS      | b1       | k = # of high‑pass filters to follow     |
| HPF1     | b2       | First high‑pass cutoff frequency, in kHz |
| \|       |          |                                          |
| HPFk     | b2       | Last high‑pass cutoff frequency, in kHz  |
|
| LFS      | b1       | n = # of low‑pass filters to follow      |
| LPF1     | b2       | First low‑pass cutoff frequency, in kHz  |
| \|       |          |                                          |
| LPFn     | b2       | Last low‑pass cutoff frequency, in kHz   |

Repeat above for as many different multi-filters as need to be defined

NOTE: one multi-filter is produced by the combination of available filters on a plug-in filter module with the fixed filters on the underlying board (e.g., AEDSP-32/16), if selections exist to bypass the plug-in filter.

Presently, only one combination is available. In the future, different options for plug-in and on-board filters may become available and will be described, per channel, in a modified configuration report message. At that point, the software will process the configuration report, determine all possible combinations, and generate this message.

| EXAMPLE: Use this for first version of the code |          |
|-------------------------------------------------|----------|
| LEN                                             | 20       |
| ID                                              | 136      |
| AFID                                            | 1        |
|
| HFS                                             | 4        |
| HPF1                                            | 10 kHz   |
| HPF2                                            | 20 kHz   |
| HPF3                                            | 100 kHz  |
| HPF4                                            | 200 kHz  |
|
| LFS                                             | 4        |
| LPF1                                            | 1200 kHz |
| LPF2                                            | 100 kHz  |
| LPF3                                            | 200 kHz  |
| LPF4                                            | 400 kHz  |

### **ID 137 — Analog Filter Selection**

**(INI and DTA files, AEDSP board)**

| Field         | Bytes    | Notes                                                                        |
|---------------|----------|------------------------------------------------------------------------------|
| LEN           | b1, b2   | 2 bytes                                                                      |
| ID            | b1= 137  |                                                                              |
| CID           |          | 1 byte<br>Channel number, if 0 then all channels                             |
| AFID          |          | 1 byte<br>Multi-filter ID type number, must<br>be one defined with message 136 |
| +             |          |                                                                              |
| Highpass code |          | 1 byte<br>0-15, in the order that is defined<br>for the plug‑in filter       |
| Lowpass code  |          | 1 byte<br>0-15, in the order that is defined<br>for the plug‑in filter       |

**NOTE:** the AFID number is ignored by the AEDSP board, which will just take the highpass and lowpass selection codes and set the plug-in filter control lines to these codes.

### **ID 138 — Analog Parametric Setup**

**(INI and DTA files, AEDSP board)**

| Field       | Bytes  | Notes                                                                      |
|-------------|--------|----------------------------------------------------------------------------|
| LEN         | b1, b2 | 2 bytes                                                                    |
| CID         |        | 1 byte<br>Channel number, if 0 then all channels                           |
| Gain code   |        | 1 byte<br>0 = x 1<br>1 = x 10<br>2 = x 100<br>3 = x 1000                   |
| Filter code |        | 1 byte<br>0 = no filter<br>1 = filter ON                                   |

### **ID 139 — Cycle Counter Analog Setup**

**(INI and DTA files, AEDSP board)**

| Field     | Bytes  | Notes                                                                                                    |
|-----------|--------|----------------------------------------------------------------------------------------------------------|
| LEN       | b1, b2 | 2 bytes                                                                                                  |
| CID       |        | 1 byte<br>Channel number, for future expansion                                                           |
| Threshold |        | 2 bytes<br>Threshold in millivolts<br>Range : -5080 to 5120                                              |
| Source    |        | 1 byte<br>0 = parametric 1<br>1 = filtered parametric 1<br>2 = parametric 2<br>3 = filtered parametric 2 |

### **ID 140–ID 170 (Not defined)**

### **ID 171 — TRA Messages (TRA2.5)**

### **ID 171 — TRA Messages 1(TRA212)**

### **ID 172.29 — Digital AE Data Filter Definition**

**(INI and DTA, AEDSP board)**

| Field  | Bytes    | Notes         |
|--------|----------|---------------|
| LEN    | b1, b2   | 2 bytes       |
| ID     | b1= 172  | Message ID (PDF shows 173; likely typo)    |
| Sub-ID | b1= 29   | Submessage ID |

**Exact copy of the body of ID 29 message (AE filter definition):**

| Field | Bytes   | Notes                                                                                                                                                       |
|-------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FS    | 1 byte  | # of filter definitions to follow                                                                                                                           |
| FID   | 1 byte  | Waveform filter ID number                                                                                                                                   |
| CID   | 1 byte  | Channel number                                                                                                                                              |
| TYPE  | 1 byte  | Type of filter operation<br>1 = SCSH (single channel, single hit)<br>Only one type presently defined                                                        |
| CHID  | 1 byte  | AE characteristic<br>0 = none (reject all waveforms)<br>1 = risetime, 2 = counts to peak,<br>3 = counts, 4 = ICC energy<br>5 = duration, 6 = amplitude<br>13 = average frequency |
| LOW   | 4 bytes | Low level in msec (signed long integer)                                                                                                                     |
| HIGH  | 4 bytes | High level in msec (signed long integer)<br>FS times                                                                                                        |

**Will determine which hits are eligible to be recorded as waveforms**

**To block all waveforms, the AE characteristic (CHID) is set to 0 and the LOW and HIGH limits are also set to 0.**

### **ID 172.42 — Hardware setup**

| Field       | Bytes            | Notes                                                                    |
|-------------|------------------|--------------------------------------------------------------------------|
| LEN         | b1, b2           | 2 bytes                                                                  |
| ID          | b1= 172 (ACH)    | Message ID                                                               |
| Sub-ID      | b1= 42 (2AH)     | Message sub-ID                                                           |
| MVERN       | b1= 100<br>b2= 0 | Message version number, 100 is V 1.00                                    |
| ADT         | b1               | A/D converter data type<br>2 = 16 bit signed (only type currently defined for MI-TRA) |
| SETS        | b1= n<br>b2      | Number of TRA channels (setups)                                          |
| SLEN        | b1<br>b2         | Size of hardware setup, in bytes                                         |
| TRA setup 1 |                  |                                                                          |
| CHID        | b1               | Channel ID. If 0, setup for all channels                                 |
| HLK         | b1<br>b2         | Hit length, in K samples (K = 1024)                                      |
| HITS        | b1<br>b2         | Not used for MI-TRA.                                                     |
| SRATE       | b1<br>b2         | Sampling rate, in kHz (uint16)<br>(8000, 4000, 2000, 1000, 500, 200, 100)        |
| TMODE       | b1<br>b2         | Trigger mode (2 bytes)<br>b1 = trigger mode<br>b2 = 0 means "individual"                                           |
| TSRC        | b1<br>b2         | Trigger source (2 bytes)<br>b1 = trigger source<br>b2 = 1 means "digital"                                                           |
| TDLY        | b1<br>b2         | Trigger delay in samples (int16)<br>Negative value = pretrigger        |
| MXIN        | b1<br>b2         | Maximum input voltage (uint16)<br>10 = 10 Volts, only one for AEDSP              |
| THRD        | b1<br>b2         | Trigger threshold in dBae (uint16)                                                |
| TRA setup 2 |                  |                                                                          |
| \|          |                  | As many setups as necessary                                              |
| TRA setup n |                  |                                                                          |

### **ID 172.134 — Reserved**

### **ID 173.1 — Digital AE Waveform Data**

**(DTA file, AEDSP board)**

| Field  | Bytes    | Notes                                                                     |
|--------|----------|---------------------------------------------------------------------------|
| LEN    | b1, b2   | 2 bytes                                                                   |
| ID     | b1= 173  | Message ID                                                                |
| Sub-ID | b1= 1    | Submessage ID                                                             |
| TOT    | b1..b6   | time of hit                             |
| CID    | b1       | Channel number                                                  |
| ALB    | b1       | Alignment byte (dummy)                                          |
|
| N      | b1,b2    | Number of 16-bit samples following                             |
| s1     | b1,b2    | First sample of waveform                                       |
| \|     |          |                                                                           |
| sN     | b1,b2    | Last sample                                                    |
|
| AEF    | many bytes         | Copy of part of message 1 after CID<br>(AE features and TD data) |

### **ID 173.3 — Digital AE Power Spectrum Data (AEDSP board)**

**(Reserved for external use)**

### **ID 174 to ID 196 — Not defined**

### **ID 197 IDBVALSCRN — Screen Template for Display of Improved b-Value data**

| Field | Bytes  | Notes                                                      |
|-------|--------|------------------------------------------------------------|
| LEN   | b1, b2 | 2 bytes                                                    |
| ID    | b1     | Message ID byte                                            |
| VID   | b1     | Version of the current message                             |
| b1    |        | TRUE/FALSE flag Controls which event plot is shown         |
| b2    |        | not used                                                   |
| \|    |        |                                                            |
| bn    |        | struct graph_def array defines the special graphs          |

### **ID 198 IBVALCALC — Improved b-Value Calculation Definition**

| Field | Bytes  | Notes                                                                                                |
|-------|--------|------------------------------------------------------------------------------------------------------|
| LEN   | b1, b2 | 2 bytes                                                                                              |
| ID    | b1     | Message ID byte                                                                                      |
| VID   | b1     | Version of the current message                                                                       |
| b1    |        | First byte of the information which contains<br>the user setting to control the b-value<br>calculations. |
| \|    |        |                                                                                                      |
| bn    |        |                                                                                                      |

### **ID 199 — Internal**

### **ID 200–ID 254 — Reserved for Application Programs**

**(See MID = 211)**

### **ID 211 — Time Mark [Command] ® mGCC**

**(Lets the user make a time mark in the data set to indicate when some special action or external event occurs.)**

### **ID 211 — (Extended) Time Mark Message(s) (Time Stamp)**

| Field | Bytes           | Notes                                    |
|-------|-----------------|------------------------------------------|
| LEN   | b1, b2          | 2 bytes                                  |
| ID    | b1= 211 (D3H)   | Time mark ID                             |
| RTOT  | b1..bn | Relative time of test<br>(n = 6 if MONPAC, SPARTAN,<br>(n = 4 if TRANSPORTATION)* |

**IF LEN = (5 or) 7**, then the 211 message is a plain time mark message.

**IF LEN >7**, then it is a SPARTAN-AT style Extended time mark. Version 1.54 and higher of the mGCC will send to the high end gain and threshold changes with the Time Of Test stamp.

**Extended message:**

```
Len = 7 + total length of the appended message.
Body of 211 message (7 bytes)
Len of appended message Body length (2 bytes)
Body of appended message {Total is 2+Body}
```

The "unnecessary" length of the appended message is so that appended message can be processed as though it didn't have a time stamp (i.e. skip the first 9 bytes and pass the rest onto the message processing for appropriate message type).

**\*NOTE:** The Transportation Instrument does not have extended messages.

# **ID 220 & ID 221 — Reserved for Boeing Programs**

```
NOTE: Short Hand W == Word, DW == Double Word, TW == Triple Word 
  W1 Length of Message
  B Message ID = 206
  W SubFunction Code [0-8]
  X subfunction body
   _____________________________
   SubFunction 0: Velocity conversion Factor
   DW Value
   SubFunction 1: Display Limits
   DW Value {Horiz. Low Lim}
   DW Value {Horiz. High Lim}
   DW Value {Vert. Low Lim}
   DW Value {Vert. High Lim}
  Opt.[ DW Value {Depth Low Lim}
   DW Value {Depth High Lim} 
   ]
   SubFunction 2: Sensor Position
   DW Horiz. Value
   DW Vert. Value
  Opt.[ DW Depth Value
   ]
   SubFunction 3: Event Data
   W +1 Start -1 Stop
   SubFunction 4: Channel Timing
   W CID (Channel ID)
   TW 6 byte Time
   W Time to Peak
   SubFunction 5: Turns ON/OFF S100 Data Display
   W 1 == ON , else OFF
   SubFunction 6: Special 3-D algorithm control values
   SubFunction 7: Special 3-D setup Command to Draw
   Either (1) All Sensors or (2) Last one
   SubFunction 8: Use Rise Time in 3-D location calculate
   W 1==Yes, 0==No
```

### **ID 255 — Reserved**

## 4. SUMMARY:

### Condensed System Messages & Commands

| Id      | Description                                                       |
|---------|-------------------------------------------------------------------|
| 1       | AE hit/Event Data                                                 |
| 2       | Time Demand Data                                                  |
| 3       | Sample/Last Time Demand Data                                      |
| 4       | GCC detected an error condition.                                  |  |
| 5       | Hit Data Set Definition                                           |  |
| 6       | Time driven/Demand Data Set Definition                            |  |
| 7       | User Comments/Test Label                                          |  |
| 8       | Continued File Mark                                               |  |
| 9–10    | Not Used                                                          |  |
| 11      | Reset Real Time Clock                                             |  |
| 12      | Reserved                                                          |  |
| 13–14   | Not Used                                                          |  |
| 15      | Abort acquisition/transfer                                        |  |
| 16      | Alarm Data                                                        |  |
| 17      | Reserved                                                          |  |
| 18      | ICC self test (Internal)                                          |  |
| 19      | Single ICC Reset (Internal)                                       |  |
| 20      | {Reserved for pre-amp gain}                                       |  |
| 21      | (AST messages)                                                    |  |
| 22      | Set Threshold                                                     |  |
| 23      | Set Gain                                                          |  |
| 24      | Set Hit Definition Time                                           |  |
| 25      | Set Hit Lockout Time                                              |  |
| 26      | Set Peak Definition Time                                          |  |
| 27      | Set Parametric Sampling Time                                      |  |
| 28      | Alarm Definition                                                  |  |
| 29      | Filter Definition                                                 |
| 30      | AEDSP Delta-T AE Filter Definition                                |
| 31      | Reserved                                                          |
| 32      | High end Alarm Detected (Internal)                                |
| 33–36   | Reserved                                                          |
| 37      | INI Write-Protect Password                                        |
| 38      | Test Info                                                         |
| 39–40   | Reserved                                                          |
| 41      | ASCII Product Definition                                          |
| 42      | Hardware Setup                                                    |
| 43      | Graph setup ( *.ini file Only)                                    |
| 44      | Location Setup                                                    |
| 45      | Acquisition Control Information                                   |
| 46      | Auto Run Message                                                  |
| 47      | Reserved                                                          |
| 48      | Post Filter Definition and Information                            |
| 49      | Product Specific Setup & Configuration Information                |
| 50      | Reserved                                                          |
| 51      | Reserved                                                          |
| 52      | Reserved                                                          |
| 53      | Reserved                                                          |
| 54–58   | Not Used                                                          |
| 59      | Ignore Alarm - HE command to mGCC                                 |
| 60–98   | Not Used                                                          |
| 99      | Time and Date of Test Start                                       |
| 100     | Begin setup                                                       |
| 101     | End Setup                                                         |
| 102     | Set Demand Data Sampling Rate                                     |
| 103–105 | Not Used                                                          |
| 106     | Begin a Group Setup                                               |
| 107     | Reserved                                                          |
| 108–109 | Not Used                                                          |
| 110     | Define Group Parametric Channels                                  |
| 111     | Group Parametric Settings (msgs 22-26)                            |
| 112–123 | Not Used                                                          |
| 124     | End of Current Group Setup                                        |
| 125     | Internal                                                          |
| 126     | Internal                                                          |
| 127     | Internal                                                          |
| 128     | Begin Test                                                        |
| 129     | Stop Test                                                         |
| 130     | Pause Test                                                        |
| 131     | Configuration report [PRODUCT SPECIFIC]                           |
| 132     | Status report [PRODUCT SPECIFIC]                                  |
| 133     | Pulser Rate                                                       |
| 134     | Reserved                                                          |
| 135     | Reserved                                                          |
| 136     | Analog Filter Definition (INI and DTA Files only, AEDSP software) |
| 137     | Analog Filter Selection (INI and DTA Files only, AEDSP board)     |
| 138     | Analog Parametric Setup (INI and DTA Files only, AEDSP board)     |
| 139     | Cycle Counter Analog Setup (INI and DTA Files only, AEDSP board)  |
| 140–170 | Not Used                                                          |
| 171     | TRA2.5                                                            |
| 172     | TRA212                                                            |
| 173     | AEDSP waveform recording                                          |
| 174–196 | Not Used                                                          |
| 197     | Screen template for display of improved b-value data              |
| 198     | Improved b-value calculation definition                           |
| 199     | Internal                                                          |
| 200–203 | Not Used                                                          |
| 204–210 | Reserved                                                          |
| 211     | Time Mark (also in the MONPAC and Transportation Instrument)      |
| 220-221 | Reserved {Boeing}                                                 |
| 222-254 | Not defined                                                       |
| 255     | Reserved                                                          |

---
