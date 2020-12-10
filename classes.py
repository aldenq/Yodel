

class fmeta:
    ftype = 0

class frameStruct:
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

    def __init__(self, frame):
        self.bytes = frame
        




class frameR:
    ftype = 0
    def __init__(self, frame, repeats):
        self.frame = frame
        self.repeats = repeats