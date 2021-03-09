import subprocess
import random
import os
import time
import socket
import sys
import threading
from queue import LifoQueue
import multiprocessing as mp
import time

import yodel.globaldat as globaldat
from yodel.config import *
from yodel.classes import *
from .dynamicheaders import *
import yodel.standardformats as standardformats
from .sender import send, sender, sendData, sender_pipe_output
from .receiver import listen, receiver, receiver_pipe_output, incoming

import atexit


@atexit.register
def on_exit():  # was having issues getting built in daemon threads working, this is simple fix
    #print("exiting 21")
    # give threads a moment to finish up what they are doing
    time.sleep(globaldat.socketCloseTime)
    send_to_receiver(["exit", 0])
    send_to_sender(["exit", 0])
# print(framedecode.__file__)
# iface="wlp3s0"
# nmcli device set wlp3s0 managed no
# sudo ip link set wlp3s0 down
# sudo iwconfig wlp3s0 mode Monitor
# sudo ip link set wlp3s0 up
# print(__name__=="yodel.yodelmain")


# sudo iw dev wlp3s0 set channel 1 HT20

# nmcli device set wlp3s0 managed no && sudo ip link set wlp3s0 down &&
# sudo iwconfig wlp3s0 mode Monitor && sudo ip link set wlp3s0 up


####
# end of auto configurator
####


# print(payload,group,name)


####
# thread setup and managment
####


def setupThreads():

    global sendert, receivert, outgoing, incoming
    # print("startingt")

    sendert = mp.Process(
        target=sender,
        args=(
            globaldat.outgoing,
            sender_pipe_output,
        ))
    sendert.daemon = True
    sendert.start()
    # print("startingt2")
    receivert = mp.Process(
        target=receiver, args=(
            incoming, receiver_pipe_output,))
    receivert.daemon = True
    receivert.start()
    #print("threads started")


def startRadio(interf):  # all functions needed to initiate radios

    autoConf(interf)
    setInterface(interf)
    setupThreads()


def restartThreads():

    send_to_receiver(["exit", 0])
    send_to_sender(["exit", 0])
    globaldat.receiver_pipe, receiver_pipe_output = mp.Pipe()
    globaldat.sender_pipe, sender_pipe_output = mp.Pipe()
    setupThreads()
