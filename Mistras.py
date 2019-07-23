import numpy as np
from datetime import datetime

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

    return(datetime.strptime(date,'%c\n'))