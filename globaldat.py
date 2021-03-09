import multiprocessing
from multiprocessing import Pipe
from multiprocessing.queues import Queue
from socket import socket
from typing import *

lastMessages: List[int] = []
# iface = "wlx000f600a2d3e"
iface: str = ""  # interface name, set during runtime
robotName: str = ""  # robot name, set by setName during runtime
groups: List[str] = [""]  # list of groups bot is a part of
delay: int = 0
ETH_P_ALL: int = 3
ETH_FRAME_LEN: int = 1514  # Max. octets in frame sans FCS
relay: bool = False
maxRelay: int = 5
totalsends: int = 10
radiotap: bytearray = b"\x00\x00\x22\x00\xae\x40\x00\xa0\x20\x08\x00\xa0\x20\x08\x00\x00\x00\x10\x10\x02\x6c\x09\xa0\x00\xb0\x00\x64\x00\x00\x00\x00\x00\x00\x01"
lastMid: int = 0  # message ID of last message recieved

s: socket = None
debug: bool = True
sendert: multiprocessing.Process = None
receivert: multiprocessing.Process = None
receiver_pipe: Pipe = None
sender_pipe: Pipe = None
outgoing: Queue = None

messages_types: List[int] = [0] * 256
# how much time in seconds the threads have to finish what they are doing
# once the program ends
socketCloseTime: float = .1


def getInt(bytea: bytearray) -> int:
    return (int.from_bytes(bytea, byteorder='little'))


def bytesPrint(x: bytearray) -> NoReturn:
    print(''.join(r'\x' + hex(letter)[2:] for letter in x))
