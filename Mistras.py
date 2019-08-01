import numpy as np
from datetime import datetime
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
    23:'FRQ-C',
    24:'P-FRQ'}

CHID_byte_len={
    1:2,
    3:2,
    4:2,
    5:4,
    6:1,
    23:2,
    24:2}

#Hardware setup submessage ids
submessages=[100,27,102,133,5,6,106,28,29,110,111,124,101,103]

def read_bin(file,msg_id=None):
    #Array to hold AE hit records
    rec=[]

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

            #AE Hit or Event Data
            if b1==1:
                logging.info("AE Hit or Event Data")
                
                (i1,i2)=struct.unpack('IH',data.read(6))
                LEN=LEN-6
                RTOT=(i1+2**32*i2)*.25e-6

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
                    elif b==4:
                        [v]=struct.unpack('i',data.read(b))
                    
                    LEN=LEN-b
                    record.append(v)
                    # print('\t'+CHID_to_str[CHID]+':',v)

                rec.append(record)
                data.read(LEN)
            
            #"Time Driven" Sample Data
            elif b1==2:
                logging.info("Time Driven Sample Data")
                data.read(LEN)
                        
            elif (b1==6):
                logging.info("Time driven/Demand Data Set Definition")
                data.read(LEN)

            #User Comments/Test Label
            elif (b1==7):
                logging.info("User Comments/Test Label:")
                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                print("\t",m.decode("ascii").strip('\x00'))

            #ASCII Product definition
            elif b1==41:
                logging.info("ASCII Product Definition:")

                #PVERN
                data.read(2)
                LEN=LEN-2

                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                logging.info(m[:-3].decode('ascii'))
            
            #Hardware Setup
            elif b1==42:
                logging.info("Hardware Setup")

                #MVERN
                data.read(2)
                LEN=LEN-2

                #Peek at the SUBID
                LSUB,SUBID=struct.unpack('HB',data.read(3))
                data.seek(-3,1)

                while SUBID in submessages:
                    LSUB,SUBID=struct.unpack('HB',data.read(3))
                    LSUB=LSUB-1
                    logging.info("\tSUBID: "+str(SUBID))

                    #Event Data Set Definition
                    if SUBID==5:
                        logging.info("\tEvent Data Set Definition")
                        
                        #Number of AE characteristics
                        [CHID]=struct.unpack('B',data.read(1))
                        LSUB=LSUB-1
                        LEN=LEN-1

                        #read CHID values
                        CHID_list=struct.unpack(str(CHID)+'B',data.read(CHID))
                        LSUB=LSUB-CHID
                        LEN=LEN-CHID
                        
                    data.read(LSUB)
                    LEN=LEN-LSUB

                    #Peek at the next SUBID
                    LSUB,SUBID=struct.unpack('HB',data.read(3))
                    data.seek(-3,1)

                data.read(LEN)
                
            #Time and Date of Test Start
            elif b1==99:
                logging.info("Time and Date of Test Start:")
                [m]=struct.unpack(str(LEN)+'s',data.read(LEN))
                m=m.decode("ascii").strip('\x00')
                logging.info("\t"+m)
                if msg_id==b1:
                    return(m)
                
            #End of Group Setting
            elif b1==124:
                logging.info("End of Group Setting")
                data.read(LEN)

            #Resume Test or Start Of Test
            elif b1==128:
                logging.info("Resume Test or Start Of Test")
                data.read(LEN)

            #Stop the Test
            elif b1==129:
                logging.info("Stop the test")
                data.read(LEN)

            #Pause the Test
            elif b1==130:
                logging.info("Pause the test")
                data.read(LEN)

            #Digial AE Waveform Data
            elif b1==173:
                logging.info("Digital AE Waveform Data")
                data.read(LEN)

            else:
                logging.info("ID "+str(b1)+" not yet implemented!")
                data.read(LEN)
            
            byte=data.read(2)


    #Convert numpy array and add record names
    return(np.core.records.fromrecords(rec,names=['SSSSSSSS.mmmuuun','CH']+[CHID_to_str[i] for i in CHID_list]))


def start_time_bin(file):
    return(datetime.strptime(read_bin(file,99),'%a %b %d %H:%M:%S %Y\n'))
