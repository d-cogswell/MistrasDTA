import numpy as np
from numpy.lib.recfunctions import append_fields
from datetime import datetime, timedelta
import struct
import logging

def read(file):

    #Get data
    AE_events=np.array(np.loadtxt(file,skiprows=8))

    #Get fields from 8th line of file
    f=open(file,'r')

    for line_num in range(1,9):
        line=f.readline()
        if line_num==8:
            fields_str=line

    f.close()

    #Add field names for the columns
    rec=np.core.records.fromrecords(AE_events,names=fields_str.split())

    return(rec)

def start_time(file):

    #Get date from 6th line of file
    f=open(file,'r')
    
    for line_num in range(1,7):
        line=f.readline()
        if line_num==6:
            date=line

    f.close()

    return(datetime.strptime(date,'%a %b %d %H:%M:%S %Y\n'))

CHID_to_str={
    1:'RISE',
    3:'COUN',
    4:'ENER',
    5:'DURATION',
    6:'AMP',
    21:'ABS-ENERGY',
    23:'FRQ-C',
    24:'P-FRQ'}

CHID_byte_len={
    1:2,
    3:2,
    4:2,
    5:4,
    6:1,
    21:4,
    23:2,
    24:2}

#Convert 6-byte sequence to a time offset
def bytes_to_RTOT(bytes):
    (i1,i2)=struct.unpack('IH',bytes)
    return((i1+2**32*i2)*.25e-6)


def read_bin(file,msg_id=None):
    #Array to hold AE hit records
    rec=[]

    #Array to hold waveforms
    wfm=[]

    #Array to hold AE hardware settings
    hardware=[]

    #Dictionary to hold gain settings
    gain={}

    #Default list of characteristics
    CHID_list=[]

    with open(file,"rb") as data:
        byte=data.read(2)
        while byte!=b"":

            #Get the message length byte
            [LEN]=struct.unpack('H', byte)

            #Read the message ID byte
            [b1]=struct.unpack('B', data.read(1))
            LEN=LEN-1

            #ID 40-49 have an extra byte
            if b1>=40 and b1<=49:
                [b2]=struct.unpack('B', data.read(1))
                LEN=LEN-1

            if b1==1:
                logging.info("AE Hit or Event Data")
                
                RTOT=bytes_to_RTOT(data.read(6))
                LEN=LEN-6

                [CID]=struct.unpack('B',data.read(1))
                LEN=LEN-1

                record=[RTOT,CID]

                #Look up byte length and read data values
                for CHID in CHID_list:
                    b=CHID_byte_len[CHID]
                    if b==1:
                        [v]=struct.unpack('B',data.read(b))
                    elif b==2:
                        [v]=struct.unpack('H',data.read(b))
                    
                    #DURATION
                    elif CHID_to_str[CHID]=='DURATION':
                        [v]=struct.unpack('i',data.read(b))

                    #ABS-ENERGY
                    elif CHID_to_str[CHID]=='ABS-ENERGY':
                        [v]=struct.unpack('f',data.read(b))
                        v=v*9.31e-4
                    
                    LEN=LEN-b
                    record.append(v)

                rec.append(record)
                data.read(LEN)
            
            elif b1==2:
                logging.info("Time Driven Sample Data")
                data.read(LEN)
                        
            elif b1==6:
                logging.info("Time driven/Demand Data Set Definition")
                data.read(LEN)

            elif b1==7:
                logging.info("User Comments/Test Label:")
                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                print("\t",m.decode("ascii").strip('\x00'))

            elif b1==41:
                logging.info("ASCII Product Definition:")

                #PVERN
                data.read(2)
                LEN=LEN-2

                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                logging.info(m[:-3].decode('ascii'))
            
            elif b1==42:
                logging.info("Hardware Setup")

                #MVERN
                data.read(2)
                LEN=LEN-2

                #SUBID
                while LEN>0:
                    [LSUB]=struct.unpack('H',data.read(2))
                    LEN=LEN-LSUB

                    [SUBID]=struct.unpack('B',data.read(1))
                    LSUB=LSUB-1

                    if SUBID==5:
                        logging.info("\tEvent Data Set Definition")
                        
                        #Number of AE characteristics
                        [CHID]=struct.unpack('B',data.read(1))
                        LSUB=LSUB-1

                        #read CHID values
                        CHID_list=struct.unpack(str(CHID)+'B',data.read(CHID))
                        LSUB=LSUB-CHID

                    elif SUBID==23:
                        logging.info("\tSet Gain")
                        CID,V=struct.unpack('BB',data.read(2))
                        gain[CID]=V
                        LSUB=LSUB-2

                    elif SUBID==173:
                        [SUBID2]=struct.unpack('B', data.read(1))
                        LSUB=LSUB-1

                        if SUBID2==42:
                            logging.info("\t173,42 Hardware Setup")

                            MVERN=struct.unpack('BB',data.read(2))
                            LSUB=LSUB-2

                            #ADT
                            data.read(1)
                            LSUB=LSUB-1

                            SETS=struct.unpack('BB',data.read(2))
                            LSUB=LSUB-2

                            [SLEN]=struct.unpack('H',data.read(2))
                            LSUB=LSUB-2

                            [CHID]=struct.unpack('B',data.read(1))
                            LSUB=LSUB-1

                            [HLK]=struct.unpack('H',data.read(2))
                            LSUB=LSUB-2

                            #HITS
                            data.read(2)
                            LSUB=LSUB-2

                            [SRATE]=struct.unpack('H',data.read(2))
                            LSUB=LSUB-2

                            #TMODE
                            data.read(2)
                            LSUB=LSUB-2

                            #TSRC
                            data.read(2)
                            LSUB=LSUB-2

                            [TDLY]=struct.unpack('B',data.read(1))
                            LSUB=LSUB-1

                            #MXIN
                            data.read(2)
                            LSUB=LSUB-2

                            #THRD
                            data.read(2)
                            LSUB=LSUB-2

                            hardware.append([CHID,1000*SRATE,TDLY])

                    else:
                        logging.info("\tSUBID "+str(SUBID)+" not yet implemented!")

                        
                    data.read(LSUB)
            
                #Convert hardware settings to record array
                hardware=np.core.records.fromrecords(hardware,names=['CH','SRATE','TDLY'])
                
            elif b1==99:
                logging.info("Time and Date of Test Start:")
                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                m=m.decode("ascii").strip('\x00')
                logging.info("\t"+m)
                test_start_time=datetime.strptime(m,'%a %b %d %H:%M:%S %Y\n')
                if msg_id==b1:
                    return(m)
                
            elif b1==124:
                logging.info("End of Group Setting")
                data.read(LEN)

            elif b1==128:
                logging.info("Resume Test or Start Of Test")
                data.read(LEN)

            elif b1==129:
                logging.info("Stop the test")
                RTOT=bytes_to_RTOT(data.read(6))
                LEN=LEN-6
                logging.info("\tRTOT: "+str(RTOT))
                data.read(LEN)
                if msg_id==b1:
                    return(RTOT)

            elif b1==130:
                logging.info("Pause the test")
                data.read(LEN)

            elif b1==173:
                logging.info("Digital AE Waveform Data")

                [SUBID]=struct.unpack('B',data.read(1))
                LEN=LEN-1

                TOT=bytes_to_RTOT(data.read(6))
                LEN=LEN-6

                [CID]=struct.unpack('B',data.read(1))
                LEN=LEN-1

                #ALB
                data.read(1)
                LEN=LEN-1

                MaxInput=10.0
                Gain=10**(gain[CID]/20)
                MaxCounts=32768.0
                AmpScaleFactor=MaxInput/(Gain*MaxCounts)
                
                s=struct.unpack(str(int(LEN/2))+'h',data.read(LEN))
                LEN=0

                #Append waveform to wfm with data stored as a byte string
                channel=hardware[hardware['CH']==CID]
                re=[TOT,CID,channel['SRATE'][0],channel['TDLY'][0],(AmpScaleFactor*np.array(s)).tobytes()]
                wfm.append(re)

                data.read(LEN)

            else:
                logging.info("ID "+str(b1)+" not yet implemented!")
                data.read(LEN)
            
            byte=data.read(2)


    #Convert numpy array and add record names
    if rec:
        rec=np.core.records.fromrecords(rec,names=['SSSSSSSS.mmmuuun','CH']+[CHID_to_str[i] for i in CHID_list])
    if wfm:
        wfm=np.core.records.fromrecords(wfm,names=['SSSSSSSS.mmmuuun','CH','SRATE','TDLY','WAVEFORM'])

    #Append a Unix timestamp field
    timestamp=[
        (test_start_time + timedelta(seconds=t)).timestamp() 
        for t in rec['SSSSSSSS.mmmuuun']]
    rec=append_fields(rec, 'TIMESTAMP', timestamp, usemask=False, asrecarray=True)

    return(rec,wfm)


def start_time_bin(file):
    return(datetime.strptime(read_bin(file,99),'%a %b %d %H:%M:%S %Y\n'))


def plot_waveform(wfm_row,ax):
    wfm=np.frombuffer(wfm_row['WAVEFORM'])
    srate=wfm_row['SRATE']
    tdly=wfm_row['TDLY']
    
    ax.plot(1e6*(np.array(range(len(wfm))))/srate-tdly,wfm)
    ax.set_xlabel('time (us)')
    ax.set_ylabel('votlage (V)')
