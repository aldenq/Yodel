import socket
import time
import os
import subprocess, random
from queue import LifoQueue
import threading
import yodel.globaldat as globaldat
from yodel.config import *
from yodel.framegen import *
from yodel.classes import *
import yodel.framedecode as  framedecode
from yodel.dynamicheaders import *
import yodel.standardformats

# iface="wlp3s0"
# nmcli device set wlp3s0 managed no
# sudo ip link set wlp3s0 down
# sudo iwconfig wlp3s0 mode Monitor
# sudo ip link set wlp3s0 up
outgoing_data = section(standardformats.standard_header_format)
incoming_data = section(standardformats.standard_header_format)

class frameRecv:
    def __init__(self, frame):
        self.frame = frame
        self.time = time.time()






# sudo iw dev wlp3s0 set channel 1 HT20

# nmcli device set wlp3s0 managed no && sudo ip link set wlp3s0 down && sudo iwconfig wlp3s0 mode Monitor && sudo ip link set wlp3s0 up




####
# end of auto configurator
####


# print(payload,group,name)

def setupThreads():
    global sendert,receivert
    sendert = threading.Thread(target=sender, args=(),daemon=True)
    receivert = threading.Thread(target=receiver, args=(), daemon=True)
    receivert.start()
    sendert.start()
    #print("test")

def startRadio(interf): #all functions needed to initiate radios 
    
    autoConf(interf)
    setInterface(interf)
    setupThreads()




def sendData(packet, current_iface, repeats):
    ftype = b'\x08\x00'
    dur = b'\x00\x00'
    src = b'\x08\x00\x27\x8e\x75\x44'

    dst = b'\xff\xff\xff\xff\xff\xff'  # broadcast address is used to stop certain drivers retransmitting frames
    bssid = src
    sn = (random.randint(0, 4096)) #semi unique id, annoyingly not usable due to lack of bits for this application. 
    sn = sn << 4
    seq = sn.to_bytes(4, 'little')

    header80211 = ftype + dur + dst + src + bssid + seq

    #print(len(header80211))
    data = globaldat.radiotap + header80211 + b"\x72\x6f\x62\x6f\x74"+packet #attach radiotap headers, 80211 headers and yodel payload 
    #print(data,"radaa")
    for i in range(repeats):
        # print(data)
        # print(len(data))

        globaldat.s.send(data)




def relayFrame(frame):
    header = b"\x72\x6f\x62\x6f\x74" 
    if globaldat.relay == True:
        # print(frame)
        sendData(header + frame, globaldat.iface, globaldat.maxRelay)






def listenrecv():
    #print("a")
    try:
        data = globaldat.s.recv(globaldat.ETH_FRAME_LEN)
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
    starth2 = (payload[pos + 16:pos + 5 + 16])

    
    if starth2 == b"\x72\x6f\x62\x6f\x74":  # radio tap headers are included on local frames
        #print("passed0")
        rdata = framedecode.is_recipient(data[16:],0)
        #print(data,"payload")
        
        if rdata:
            isr,dorelay = rdata
            #print(payload[21:],isr,dorelay,"data")
            if dorelay:
                relayFrame(payload[21:]) #16+5
            if isr:
                return(payload[21:])    
        
    if starth == b"\x72\x6f\x62\x6f\x74":  # radio tap headers are stripped on external frames (non loopback)
        #print("passed1")
        #print(payload,"payload")

        rdata = framedecode.is_recipient(data,radiolen)
        
        #print(rdata)
        if rdata:
            isr,dorelay = rdata
            #print(payload[21:],isr,dorelay,"data")
            if dorelay:
                relayFrame(payload[5:]) #16+5
            if isr:
                return(payload[5:])    
        
    return(None)


outgoing = LifoQueue(maxsize=64) #stores pending outgoing messages, will be emptied by threaded sender
incoming = LifoQueue(maxsize=16) #stores pending incoming messages, filled by threaded application, when listen is called the oldest frame still be stored is returned


def send(payload, **kwargs):
    global outgoing,outgoing_data
    
    name = kwargs.get("name", '')
    group = kwargs.get("group", '')
    mtype = kwargs.get("type", '')
    #fframe = formPacket(name, group, payload)
    #fill in fields for outgoing_data structure
    if name:
        outgoing_data.Rname = name
    else:
        outgoing_data.Rname = ""
    if group:
        outgoing_data.Gname = group
    else:
        outgoing_data.Gname = ""
    if mtype:
        outgoing_data.type = mtype
    else:
        outgoing_data.type = ""
    outgoing_data.Sname = globaldat.robotName
    outgoing_data.mid = random.randint(0,4294967296)
    outgoing_data.payload = typeManagment(payload)
    fframe = bytes(outgoing_data) #get bytes
    #print(fframe)
    oframe = classes.frameStruct(fframe)
    oframe.repeats=globaldat.totalsends
    outgoing.put(oframe)
    # sendData(fframe,iface,totalsends)


def sender():
    #print("s")
    global outgoing

    while True:

        if not outgoing.empty():

            frame = outgoing.get()

            reps = frame.repeats
            dat = frame.bytes
            sendData(dat, globaldat.iface, reps)
            # print(frame)






def listen():
    global incoming
    if not incoming.empty():    
        frame = incoming.get()
        data = frame.frame
        data = decode(data,standardformats.standard_header_format) #this is bad/slow, fix later ###################################################################################################
        return(data)
    else:
        return(None)

def receiver():
    global incoming

    while True:
        dat = listenrecv()
        if dat != None:
            formatted = frameRecv(dat)

            incoming.put(formatted)

            if incoming.full():
                incoming.get()







# print(payload)
