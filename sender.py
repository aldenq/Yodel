# this file deals with the setup and interaction with the sender thread
# interaction is done through a pipeline and a stack
# the stack is used to give the sender thread data to send out
# the pipline is used to give other instructions to the thread, things like settings updates
# both the stack and the pipeline are assumed to be one-way, that being from the main thread to the sender thread
#

import multiprocessing as mp
import yodel.standardformats as standardformats
from .dynamicheaders import *
import random
from .classes import *
from yodel.config import *
import sys
import yodel.globaldat as globaldat
from yodel.config import *


#####setup for communication with sender thread
globaldat.sender_pipe, sender_pipe_output = mp.Pipe() 
globaldat.outgoing = mp.Queue()
#####


#####template that gets filled whenever send is called. this is to avoid having to generate a new class object every time send is called
outgoing_data = section(standardformats.standard_header_format)

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
        print("exit sender")
        sys.exit()




def sendData(packet, current_iface, repeats):
    ########
    #generate 80211 header
    ########
    ftype = b'\x08\x00'
    dur = b'\x00\x00'
    src = b'\x08\x00\x27\x8e\x75\x44'  #random hex stream, could be used as additional space of bits

    dst = b'\xff\xff\xff\xff\xff\xff'  # broadcast address is used to stop certain drivers retransmitting frames
    bssid = src
    sn = (random.randint(0, 4096)) #semi unique id, annoyingly not usable due to lack of bits for this application. 
    sn = sn << 4
    seq = sn.to_bytes(4, 'little')

    
    header80211 = ftype + dur + dst + src + bssid + seq

    ##########

    data = globaldat.radiotap + header80211 + b"\x72\x6f\x62\x6f\x74"+packet #attach radiotap headers, 80211 headers and yodel payload 

    
    for i in range(repeats): #re-transmmit message a couple times
   
        globaldat.s.send(data) #send the data



def send(payload, **kwargs):
    global outgoing,outgoing_data


    name = kwargs.get("name", '')    #receiver name
    group = kwargs.get("group", '')  #receiver group
    mtype = kwargs.get("type", '')   #message type
  
    if type(payload) == section: #if type is a section than it can be processed automatically 
        mtype = payload.format.mtype
        payload= bytes(payload)
        
    if name: #check for a provided receiver name otherwise make it blank
        outgoing_data.Rname = name
    else:
        outgoing_data.Rname = ""


    if group: #check for a provided receiving group, otherwise make it blank
        outgoing_data.Gname = group
    else:
        outgoing_data.Gname = ""


    if mtype: #check if a message type has been selected
        outgoing_data.mtype = mtype
    else:
        outgoing_data.mtype = 0


    outgoing_data.Sname = globaldat.robotName #set the Sender name for the outgoing data to be equal to the robots name
    outgoing_data.mid = random.randint(0,4294967296) #generate random indetifier for the message 
    outgoing_data.payload = typeManagment(payload)  #take the payload and convert it to bytes

    fframe = bytes(outgoing_data) #get bytes
    
    oframe = frameStruct(fframe)
    oframe.repeats=globaldat.totalsends
    #print(__name__ == )
    #outgoing_data.print()
    globaldat.outgoing.put(oframe)
    # sendData(fframe,iface,totalsends)


def sender(outgoing,pipe): #thread that manages sending out data
   
    while True:
        #print("test1")
        if pipe.poll(0): #check for any new settings updates or other instructions from the main thread
            #print("data received")
            settings = pipe.recv() #if there are any then receive them
            setting_update(settings[0],settings[1]) #use these as inputs to the settings update function
        

        frame = outgoing.get() #wait for data in stack to be sent (is blocking)

        reps = frame.repeats
        dat = frame.bytes
        sendData(dat, globaldat.iface, reps)
        #print(frame)
