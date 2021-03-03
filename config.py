import os
import socket
import subprocess

import yodel.globaldat as globaldat

def send_to_receiver(data): #some settings changes require data to be sent to a thread this function takes care of that
    globaldat.receiver_pipe.send(data)


def send_to_sender(data): #some settings changes require data to be sent to a thread this function takes care of that
    globaldat.sender_pipe.send(data)
####
# settings managment
####
def setRepeats(num):  # control amount of times a message is repeated during a send
    #global totalsends
    globaldat.totalsends = num
    

def enableRelay(state):
    #global relay
    globaldat.relay = state


def disableRelay():
    #global relay
    globaldat.relay = False


def initPolyNodelYodel():
    enableRelay(True)

def setName(name):
    globaldat.robotName = name
    send_to_receiver(["name",name])
    send_to_sender(["name",name])
def getName():
    return (globaldat.robotName)


def addGroup(group):
    #global groups
    globaldat.groups.append(group)
    send_to_receiver(["add_group",group])
    send_to_sender(["add_group",group])
def deleteGroup(group):
    global groups
    if group in groups:
        loc = groups.index(group)
        del groups[loc]
    send_to_receiver(["del_group",group])
    send_to_sender(["del_group",group])

def getGroups():
    return (groups)


def clearGroups():
    global groups
    groups = []
    send_to_receiver(["clr_group",False])
    send_to_sender(["clr_group",False])

def setInterface(interf):
    #global iface, s
    globaldat.iface = interf
    globaldat.s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    globaldat.s.bind((interf, 0))
    #s.settimeout(0.1)


def setChannel(channel):  # set the channel for the interface, some drivers only work with iw, some only work with iwconfig so both are included
    os.system(f"sudo iw dev {globaldat.iface} set channel {channel}")
    os.system(f"sudo iwconfig {globaldat.iface} channel {channel}")


def setPower(txdBm):
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

def command(cmd):  # basic time saver, not generally applicable to all linux cmds
    cmda = cmd.split(" ")
    print(cmda)
    result = subprocess.run(cmda, stdout=subprocess.PIPE)
    return (result.stdout.decode("utf-8"))


def enableMonitor(interf):  # auto configure monitor mode on interface
    os.system(f"sudo rfkill unblock wifi; sudo rfkill unblock all")
    os.system(f"nmcli device set {interf} managed no")
    os.system(f"sudo ip link set {interf} down")
    os.system(f"sudo iwconfig {interf} mode Monitor")   
    os.system(f"sudo ip link set {interf} up")


def isMonitor(interf):  # get if interface is in monitor mode, is lazy but only has to run a couple times and only during setup
    a = (command(f"iwconfig {interf}"))
    mode = (a.find("Mode:Monitor"))
    if mode != -1:
        return (True)




def autoConf(interf):
    if not isMonitor(interf):
        enableMonitor(interf)
    if not isMonitor(interf):
        print("monitor mode is not available, please select a different interface or try a new driver")


