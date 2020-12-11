


lastMessages = []
# iface = "wlx000f600a2d3e"
iface = ""  # interface name, set during runtime
robotName = ""  # robot name, set by setName during runtime
groups = [""]  # list of groups bot is a part of

ETH_P_ALL = 3
ETH_FRAME_LEN = 1514  # Max. octets in frame sans FCS
relay = False
maxRelay = 5
totalsends = 10
radiotap = b"\x00\x00\x22\x00\xae\x40\x00\xa0\x20\x08\x00\xa0\x20\x08\x00\x00\x00\x10\x10\x02\x6c\x09\xa0\x00\xb0\x00\x64\x00\x00\x00\x00\x00\x00\x01"
lastMid = 0  # message ID of last message recieved
print("starting")
s = False
debug = True
sendert = 0
receivert = 0

def getInt(bytea):
    #print(bytea,"byteea")
    return (int.from_bytes(bytea, byteorder='little'))


def bytesPrint(x):
    print(''.join(r'\x' + hex(letter)[2:] for letter in x))
