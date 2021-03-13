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
from typing import *


import sys
import multiprocessing as mp
incoming = mp.Queue()
globaldat.receiver_pipe, receiver_pipe_output = mp.Pipe()


# check to see if a given message is intended for this computer, either to
# receive or to relay
def is_recipient(
        data: bytearray, radiotap_header_length: int) -> Union[bool, Tuple[bool, bool]]:
    """
    check to see if a given message is intended for this computer and if the message should be relayed


    Args:
    	 data: raw bytes for incoming message

    	 radiotap_header_length: length of radiotap header, the header is skipped over because it does not hold yodel data.
    """

    # get data frame payload section
    frame = data[radiotap_header_length + 26 + 5:]
    pos = 0  # pos is used as a pointer to the current section of the header being decoded

    """
     message id, the semi unique identifer to each message to avoid receiving
     them twice
    """
    message_ID = frame[pos:pos + 4]
    if message_ID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (False)

    if message_ID not in globaldat.lastMessages:  # check if message has already been received

        globaldat.lastMid = message_ID  # set last mid to the current mid
        globaldat.lastMessages.append(message_ID)
        if len(globaldat.lastMessages) > 64:
            del globaldat.lastMessages[0]

        pos += 4
        namelen = globaldat.getInt(frame[pos:pos + 1])  # get length of name
        pos += 1

        name = frame[pos:pos + namelen].decode("utf-8")
        nameM = (name == globaldat.robotName or namelen == 0)

        pos += namelen
        gnamelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        group = frame[pos:pos + gnamelen].decode("utf-8")
        pos += gnamelen

        groupM = (group in globaldat.groups or gnamelen == 0)

        relay = (globaldat.relay == True and not (name == globaldat.robotName))

        return(nameM and groupM, relay)

    return (False)


def relayFrame(frame: bytearray) -> NoReturn:
    """
    used to allow receiver thread to relay messages back out

    Args:
    	 frame: bytes of message being relayed

    """

    header = b"\x72\x6f\x62\x6f\x74"  # yodel identifier
    if globaldat.relay == True:  # check if relay is enabled

        # format and pass data to sender thread
        sendData(header + frame, globaldat.maxRelay)


def listenrecv(pipe: mp.Pipe) -> bytearray:
    """
    listen for yodel messages, check if the are meant for this computer and if so receive them

    Args:
    	 pipe: same pipe as in receiver, used to check for settings updates
    """

    try:

        data = globaldat.yodelSocket.recv(globaldat.ETH_FRAME_LEN)

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
        
        # additionally check for settings change if any yodel data is captured
        # to see if anything important has changed
        settings_check(pipe)
        rdata = is_recipient(data, radiolen)

        if rdata:
            isr, dorelay = rdata
            if dorelay:
                relayFrame(payload[5:])
            if isr:

                return(payload[5:])

    return(None)


def settings_check(pipe) -> NoReturn:
    """ reads from pipe to detect settings updates

    Args:
    	 pipe: same settings pipe as used in receiver
    """
    if pipe.poll(0):  # check for new data in pipe
        settings = pipe.recv()  # get data
        #print(settings,"setting update")
        setting_update(settings[0], settings[1])  # change settings accordingly


def listen() -> Section:
    """
    used to listen for data being sent to your robot, is non-blocking

    Returns:
        yodel.Section: contains any received message which is accessible through the .payload attribute, also contain meta data about the message 
    """
    global incoming
    try:  # make specific error
        frame = incoming.get(False)
        data = frame.frame  # take bytes from message
        # take bytes and extract header info
        data = decode(data, standardformats.standard_header_format)
        return(data)
    except BaseException:

        return(None)


def receiver(incoming: mp.Queue, pipe: mp.Pipe) -> NoReturn:
    """
    this is the main function in the reciever thread. this checks for new messages and stores them into the stack so that main thread can access them
    this also checks for settings updates and acts on them


    Args:
    	 incoming: queue that main thread reads from to receive new messages

    	 pipe: settings updates
    """
    globaldat.yodelSocket.settimeout(.1)
    while True:

        settings_check(pipe)  # check for settings updates
        dat = listenrecv(pipe)

        if dat is not None:
            formatted = FrameRecv(dat)

            incoming.put(formatted)

            if incoming.full():
                incoming.get()
