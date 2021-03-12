import os
import socket
import subprocess
import sys
import yodel.globaldat as globaldat
from typing import *


def setting_update(setting, value):
    """
    modifies settings based on the contents of pipe

    @param setting: setting that is to be modified

    @param value: what that setting should be set to

    """

    if setting == "name":  # change name
        globaldat.robotName = value
    elif setting == "add_group":  # add to new group
        globaldat.groups.append(value)
    elif setting == "del_group":  # delete group
        deleteGroup(value)
    elif setting == "clr_group":  # clear groups
        globaldat.groups = []
    elif setting == "exit":  # exit
        print("exit sender")

        sys.exit()


def send_to_receiver(data: list) -> NoReturn:
    """some settings changes require data to be sent to a thread this function


    @params data: list that holds a setting and what value it should be changed to, eg: ["name","tester"]

    """

    globaldat.receiver_pipe.send(data)


def send_to_sender(data):
    """

    some settings changes require data to be sent to sender thread this function takes care of that

    @params data: list that holds a setting and what value it should be changed to, eg: ["name","tester"]
    """

    globaldat.sender_pipe.send(data)


def setRepeats(num: int) -> NoReturn:
    """ control amount of times a message is repeated during a send

    @params num: number of time messages should be repeated, larger value means better reliability with reduce bandwidth

    """

    globaldat.totalsends = num


def toggleRelay(state: bool) -> NoReturn:
    """ enable relaying of messages to allow extended range for other robots

    @params state: True:relay on, False: relay off
    """

    globaldat.relay = state


def initPolyNodelYodel():
    enableRelay(True)


def setName(name) -> NoReturn:
    """
    set or change the name of your robot

    @params name: name of robot
    """

    globaldat.robotName = name
    send_to_receiver(["name", name])  # send name change to other threads
    send_to_sender(["name", name])


def getName() -> str:
    """
    returns the name of your robot
    """
    return (globaldat.robotName)


def addGroup(group):
    """
    add robot to a new group

    @params group: name of group to add robot to

    """
    globaldat.groups.append(group)
    send_to_receiver(["add_group", group])
    send_to_sender(["add_group", group])


def deleteGroup(group) -> NoReturn:
    """
    remove robot from specifed group


    @params group: name of group you want to leave
    """

    if group in globaldat.groups:
        loc = globaldat.groups.index(group)
        del globaldat.groups[loc]
    send_to_receiver(["del_group", group])
    send_to_sender(["del_group", group])


def getGroups() -> list:
    """
    get list of groups robot is a member of


    """
    return (globaldat.groups)


def clearGroups() -> NoReturn:
    """
    remove robot from all groups
    """
    globaldat.groups = []
    send_to_receiver(["clr_group", False])
    send_to_sender(["clr_group", False])


def setInterface(interface: str) -> NoReturn:
    """
    set the interface used by the robot and initates the socket.

    @params interface: name of wifi interface that will be used
    """
    globaldat.iface = interface
    globaldat.s = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.htons(3))
    globaldat.s.bind((interface, 0))


def setChannel(channel) -> NoReturn:
    """
    set the channel for the interface, some drivers only work with iw, some only work with iwconfig so both are included

    """
    os.system(f"sudo iw dev {globaldat.iface} set channel {channel}")
    os.system(f"sudo iwconfig {globaldat.iface} channel {channel}")


def setPower(txdBm) -> NoReturn:
    """
    set the transmit power of wifi interface
    3500 is not necessarily a legal or safe power level for your hardware,
    the limiter is just to marginally decrease the odds of causing problems.

    @params txdBm: transmit power in dBm
    """
    if txdBm > 3500:
        txdBm = 3500
        print("power level is set too high")
    os.system(f"sudo iw dev {globaldat.iface} set txpower fixed {txdBm}")


####
# end of settings managment
####


####
# auto configurator
####

def command(cmd) -> str:
    """
    run a command, get the output
    basic time saver, not generally applicable to all linux cmds


    @params cmd: command being ran
    """
    cmda = cmd.split(" ")
    print(cmda)
    result = subprocess.run(cmda, stdout=subprocess.PIPE)
    return (result.stdout.decode("utf-8"))


def enableMonitor(interface) -> NoReturn:
    """ auto configure monitor mode on interface
        it's ok for this to raise errors

    @params interface: wifi interface being used
    """
    os.system(f"sudo rfkill unblock wifi; sudo rfkill unblock all")
    os.system(f"nmcli device set {interface} managed no")
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo iwconfig {interface} mode Monitor")
    os.system(f"sudo ip link set {interface} up")


def isMonitor(interface):
    """
    get if interface is in monitor mode, is lazy but only has to run a couple times and only during setup
    (re-work with ioctl)

    @params interface: interface being used
    """
    a = (command(f"iwconfig {interface}"))
    mode = (a.find("Mode:Monitor"))
    if mode != -1:
        return (True)


def autoConf(interface) -> NoReturn:
    """
    auto configure wifi interface

    @params interface: name of wifi interface being used

    """

    if not isMonitor(interface):  # first try to set it to monitor mode
        enableMonitor(interface)
    if not isMonitor(interface):  # if set fails let the user know
        print("monitor mode is not available, please select a different interface or try a new driver")
