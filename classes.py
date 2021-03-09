import time


class FrameRecv:  # this is used to store messages in the stack that are recieved by the reciever thread
    def __init__(self, frame: bytearray):
        self.frame = frame  # raw message bytes
        self.time = time.time()  # time message is received


'''
class fmeta:
    ftype = 0
'''


class FrameStruct:
    relay = False
    ftype = 0
    sender = ""
    receiver = ""
    group = ""
    mid = 0
    payload = ""
    repeats = None

    def __repr__(self):
        return(self.payload)

    def __init__(self, frame: bytearray):
        self.bytes = frame


''''
class frameR:
    ftype = 0
    def __init__(self, frame, repeats):
        self.frame = frame
        self.repeats = repeats
'''
