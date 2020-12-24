# this file deals with the setup and interaction with the receiver thread
# interaction is done through a pipeline and a stack
# the stack is used to store the bytes of messages sent to this robot
# the pipline is used to give other instructions to the thread, things like settings updates
# both the stack and pipeline are one way, the stack is used only for sending back data to the main thread, the pipeline is used only for sending instructions to the reciever thread
#

from .sender import sendData
import yodel.globaldat as globaldat
from .classes import *
import yodel.standardformats as standardformats
from .dynamicheaders import *
from yodel.config import *
import yodel.framedecode as framedecode


import sys
import multiprocessing as mp
incoming = mp.Queue()
globaldat.receiver_pipe, receiver_pipe_output = mp.Pipe()


def setting_update(setting,value):
    
    if setting == "name":
        globaldat.robotName = value
    elif setting == "add_group":
        globaldat.groups.append(value)
    elif setting == "del_group":
        deleteGroup(value)
    elif setting == "clr_group":
        clearGroups()
    elif setting == "exit":
        print("exiting")
        sys.exit()

def relayFrame(frame):
    header = b"\x72\x6f\x62\x6f\x74" 
    if globaldat.relay == True:
        # print(frame)
        sendData(header + frame, globaldat.iface, globaldat.maxRelay)






def listenrecv():
    #print("a")
    
    try:
        
        data = globaldat.s.recv(globaldat.ETH_FRAME_LEN)
        #print(data)
    except:
        return (None)
    
    radiolen = globaldat.getInt(data[2:3])
    fcs = data[17]
    if fcs == 2: #if fcs flag is set then remove the fcs which is the last 4 bytes
        data = data[0:-4] 
    #print(fcs)
   
    
    #print(radiolen,"rlen")

    payload = data[radiolen+26:]
    
    pos = 0

    
    starth = (payload[pos:pos + 5])
    #starth2 = (payload[pos + 16:pos + 5 + 16])

    
    #if starth2 == b"\x72\x6f\x62\x6f\x74":  # radio tap headers are included on local frames
        #print("passed0")
    #    rdata = framedecode.is_recipient(data[16:],0)
        #print(data,"payload")
        
    #    if rdata:
    #        isr,dorelay = rdata
            #print(payload[21:],isr,dorelay,"data")
    #        if dorelay:
    #            relayFrame(payload[21:]) #16+5
    #        if isr:
    #            return(payload[21:])    
    #print("abcdef")        
    if starth == b"\x72\x6f\x62\x6f\x74":  # radio tap headers are stripped on external frames (non loopback)
        #print("passed1")
        #print(payload,"payload")
        
        rdata = framedecode.is_recipient(data,radiolen)
        
        #print(rdata)
        if rdata:
            isr,dorelay = rdata
            #print(payload[21:],isr,dorelay,"data")
            #print(rdata)
            if dorelay:
                relayFrame(payload[5:]) #16+5
            if isr:
               
                return(payload[5:])    
        
    return(None)










def listen():
    global incoming
    try: 
        frame = incoming.get(False)
        data = frame.frame
        data = decode(data,standardformats.standard_header_format) #this is bad/slow, fix later ###################################################################################################
        return(data)
    except:
        #print("nothing",__name__)
        return(None)

def receiver(incoming,pipe):
    #global incoming
    #print(__name__,"receiver")
    globaldat.s.settimeout(.1)
    while True:
        
        if pipe.poll(0):
            settings = pipe.recv()
            setting_update(settings[0],settings[1])


        dat = listenrecv()
        
        #print(dat)
        if dat != None:
            formatted = frameRecv(dat)
            
            incoming.put(formatted)

            if incoming.full():
                incoming.get()







# print(payload)
