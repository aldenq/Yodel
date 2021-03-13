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
from typing import *

# setup for communication with sender thread
# print("init")
globaldat.sender_pipe, sender_pipe_output = mp.Pipe()
globaldat.outgoing = mp.Queue()
#####


# template that gets filled whenever send is called. this is to avoid
# having to generate a new class object every time send is called
outgoing_data = Section(standardformats.standard_header_format)
exiting = False
exist_start = 0


def sendData(packet: FrameStruct, repeats: int) -> NoReturn:
    """
    Generate 80211 header and send completed data

    Args:
     	packet: framestruct that holds raw outgoing data as well and info about how it should be sent

     	repeats: number of times message should be sent
    """
    ftype = b'\x08\x00'
    dur = b'\x00\x00'
    # random hex stream, could be used as additional space of bits
    src = b'\x08\x00\x27\x8e\x75\x44'
    # broadcast address is used to stop certain drivers retransmitting frames
    dst = b'\xff\xff\xff\xff\xff\xff'
    bssid = src
    # semi unique id, annoyingly not usable due to lack of bits for this appli
    sn = (random.randint(0, 4096))
    sn = sn << 4
    seq = sn.to_bytes(4, 'little')

    # generate 80211 header
    header80211 = ftype + dur + dst + src + bssid + seq

    # combine header with other data to create valid frame
    data = globaldat.RADIO_TAP + header80211 + b"\x72\x6f\x62\x6f\x74" + \
        packet  # attach radiotap headers, 80211 headers and yodel payload

    for i in range(repeats):  # re-transmmit message a couple times
        globaldat.yodelSocket.send(data)  # send the data


def send(payload: any, name: str = "", group: str = "") -> NoReturn:
    """
    take in payload and generate additional data needed to be complient with yodel standard header and add it to the stack for the thread to access.

    Args:
        payload: data being sent

        name: name of recipient

        group: group of recipient
    """

    global outgoing, outgoing_data

    # name = kwargs.get("name", '')    #receiver name
    # group = kwargs.get("group", '')  #receiver group
    mtype = 0  # kwargs.get("type", '')   #message type

    if isinstance(
            payload, Section):  # if type is a section than it can be processed automatically
        mtype = payload.format.mtype
        payload = bytes(payload)

    if name:  # check for a provided receiver name otherwise make it blank
        outgoing_data.Rname = name
    else:
        outgoing_data.Rname = ""

    if group:  # check for a provided receiving group, otherwise make it blank
        outgoing_data.Gname = group
    else:
        outgoing_data.Gname = ""

    # set the Sender name for the outgoing data to be equal to the robots name
    outgoing_data.Sname = globaldat.robotName
    # generate random indetifier for the message
    outgoing_data.mid = random.randint(-2147483648, 2147483647)
    # take the payload and convert it to bytes
    outgoing_data.payload = typeManagment(payload)
    outgoing_data.mtype = mtype

    encoded_frame = bytes(outgoing_data)  # get bytes
    # create object that holds raw bytes as well as data about how it should
    # be sent
    outgoing_frame = FrameStruct(encoded_frame)
    outgoing_frame.repeats = globaldat.totalsends
    # push data onto stack so that sender thread can access and send off frame
    globaldat.outgoing.put(outgoing_frame)


def sender(outgoing: mp.Queue, pipe: mp.Pipe) -> NoReturn:  # thread that manages sending out data
    """
    create thread to manage sending data from outgoing stack
    
    Args:
    	 outgoing: queue that holds all messages being sent

    	 pipe: used to send settings updates and other status updates from main to this thread

    """
    while True:
        if pipe.poll(
                0):  # check for any new settings updates or other instructions from the main thread

            settings = pipe.recv()  # if there are any then receive them
            # use these as inputs to the settings update function
            setting_update(settings[0], settings[1])
        frame = outgoing.get()  # wait for data in stack to be sent (is blocking)
        sendData(frame.bytes, frame.repeats)
