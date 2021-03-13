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
from typing import *

import atexit


@atexit.register
def on_exit() -> NoReturn:
    """
     was having issues getting built in daemon threads working, this is simple fix, also allows for more advanced exit behavior
    """
    # give threads a moment to finish up what they are doing
    time.sleep(globaldat.SOCKET_CLOSE_TIME)
    send_to_receiver(["exit", 0])
    send_to_sender(["exit", 0])


# iface="wlp3s0"
# nmcli device set wlp3s0 managed no
# sudo ip link set wlp3s0 down
# sudo iwconfig wlp3s0 mode Monitor
# sudo ip link set wlp3s0 up
# sudo iw dev wlp3s0 set channel 1 HT20
# nmcli device set wlp3s0 managed no && sudo ip link set wlp3s0 down &&
# sudo iwconfig wlp3s0 mode Monitor && sudo ip link set wlp3s0 up


####
# thread setup and managment
####


def setupThreads() -> NoReturn:
    """
    setup sender and receiver threads

    """
    global sender_thread, receiver_thread, outgoing, incoming

    sender_thread = mp.Process(
        target=sender,
        args=(
            globaldat.outgoing,
            sender_pipe_output,
        ))
    sender_thread.daemon = True
    sender_thread.start()

    receiver_thread = mp.Process(
        target=receiver, args=(
            incoming, receiver_pipe_output,))
    receiver_thread.daemon = True
    receiver_thread.start()


def startRadio(interface: str) -> NoReturn:  # all functions needed to initiate radios
    """
    automatically setups wireless interface to work with yodel. also setups up sender and receiver threads.

    Args:
    	 interface: interface to be used with yodel
    """
    autoConf(interface)
    setInterface(interface)
    setupThreads()


def restartThreads() -> NoReturn:
    """
    used to restart the sender and receiver threads if something breaks
    """
    send_to_receiver(["exit", 0])
    send_to_sender(["exit", 0])
    globaldat.receiver_pipe, receiver_pipe_output = mp.Pipe()
    globaldat.sender_pipe, sender_pipe_output = mp.Pipe()
    setupThreads()
