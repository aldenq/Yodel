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
#import yodel.framedecode as framedecode


import sys
import multiprocessing as mp
incoming = mp.Queue()
globaldat.receiver_pipe, receiver_pipe_output = mp.Pipe()








def is_recipient(data,rlen):  #
    
    # print(lastMessages)
    
    frame = data[rlen+26+5:] #get data frame payload section
    pos = 0 #pos is used as a pointer to the current section of the header being decoded
    #ftype = frame[pos:pos+1]
    #print(frame)
    #print("abc1234567821A1",__name__)
    mID = frame[pos:pos + 4] #message id, the semi unique identifer to each message to avoid receiving them twice
    #print(__name__)
    #pos += 1
    #globaldat.bytesPrint(mID)
    if mID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (False)
    if mID not in globaldat.lastMessages: #check if message has already been received
        
        globaldat.lastMid = mID #set last mid to the current mid 
        # print(mID)
        globaldat.lastMessages.append(mID)
        if len(globaldat.lastMessages) > 64:
            del globaldat.lastMessages[0]

        
        #out = classes.frameStruct(frame)
        pos += 4
        namelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        
        name = frame[pos:pos + namelen].decode("utf-8")
        nameM = (name == globaldat.robotName or namelen == 0)

        pos += namelen
        gnamelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        group = frame[pos:pos + gnamelen].decode("utf-8")
        pos += gnamelen

        
        groupM = (group in globaldat.groups or gnamelen == 0)
        #if globaldat.relay == True and not (name == globaldat.robotName):
        #    relay = True

        
        relay = (globaldat.relay == True and not (name == globaldat.robotName))
            #relayFrame(frame)
        return(nameM and groupM,relay)
       
    return (False)
    # print((namelen))










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
   
    
    try:
        
        data = globaldat.s.recv(globaldat.ETH_FRAME_LEN)
        
    except:
        return (None)
    
    radiolen = globaldat.getInt(data[2:3])
    fcs = data[17]
    if fcs == 2: #if fcs flag is set then remove the fcs which is the last 4 bytes
        data = data[0:-4] 


    payload = data[radiolen+26:]
    
    pos = 0

    
    starth = (payload[pos:pos + 5])

    if starth == b"\x72\x6f\x62\x6f\x74":  # radio tap headers are stripped on external frames (non loopback)
        rdata = is_recipient(data,radiolen)
        
        if rdata:
            isr,dorelay = rdata
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
