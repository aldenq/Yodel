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


# check to see if a given message is intended for this computer, either to
# receive or to relay
def is_recipient(data, rlen):

    # print(lastMessages)

    frame = data[rlen + 26 + 5:]  # get data frame payload section
    pos = 0  # pos is used as a pointer to the current section of the header being decoded
    #ftype = frame[pos:pos+1]
    # print(frame)
    # print("abc1234567821A1",__name__)
    # message id, the semi unique identifer to each message to avoid receiving
    # them twice
    mID = frame[pos:pos + 4]
    # print(__name__)
    #pos += 1
    # globaldat.bytesPrint(mID)
    if mID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (False)
    if mID not in globaldat.lastMessages:  # check if message has already been received

        globaldat.lastMid = mID  # set last mid to the current mid
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
        # if globaldat.relay == True and not (name == globaldat.robotName):
        #    relay = True

        # print(nameM,groupM,name,group,globaldat.groups)
        relay = (globaldat.relay == True and not (name == globaldat.robotName))
        # relayFrame(frame)
        return(nameM and groupM, relay)

    return (False)
    # print((namelen))


# settings handlers for handeling setting changes made by main thread,
# should mirror function in sender.py
def setting_update(setting, value):

    if setting == "name":
        globaldat.robotName = value
    elif setting == "add_group":
        print("groups", value)
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
        # this probably will not work? depends on if this is in thread
        sendData(header + frame, globaldat.iface, globaldat.maxRelay)


def listenrecv(pipe):

    try:

        data = globaldat.s.recv(globaldat.ETH_FRAME_LEN)

    except BaseException:
        return (None)

    radiolen = globaldat.getInt(data[2:3])
    fcs = data[17]  # fcs status flag is stored at byte 17
    if fcs == 2:  # if fcs flag is set then remove the fcs which is the last 4 bytes
        data = data[0:-4]

    payload = data[radiolen + 26:]

    pos = 0

    starth = (payload[pos:pos + 5])

    # radio tap headers are stripped on external frames (non loopback)
    if starth == b"\x72\x6f\x62\x6f\x74":
        # print("check")
        # additionally check for settings change if any yodel data is captured
        # to see if anything important has changed
        settings_check(pipe)
        rdata = is_recipient(data, radiolen)
        # print("a")
        if rdata:
            isr, dorelay = rdata
            if dorelay:
                relayFrame(payload[5:])  # 16+5
            if isr:
                # print(payload)
                return(payload[5:])

    return(None)


def settings_check(pipe):
    if pipe.poll(0):  # check for new data in pipe
        settings = pipe.recv()  # get data
        #print(settings,"setting update")
        setting_update(settings[0], settings[1])  # change settings accordingly


def listen():
    global incoming
    try:  # make specific error
        frame = incoming.get(False)
        data = frame.frame  # take bytes from message
        # take bytes and extract header info
        data = decode(data, standardformats.standard_header_format)
        return(data)
    except BaseException:
        # print("nothing",__name__)
        return(None)


def receiver(incoming, pipe):
    """
    this is the main function in the reciever thread. this checks for new messages and stores them into the stack so that main thread can access them
    this also checks for settings updates and acts on them


    """
    globaldat.s.settimeout(.1)
    while True:
        # print("new")

        settings_check(pipe)  # check for settings updates
        dat = listenrecv(pipe)

        if dat is not None:
            formatted = FrameRecv(dat)

            incoming.put(formatted)

            if incoming.full():
                incoming.get()


# print(payload)
