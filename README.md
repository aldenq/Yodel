# Yodel
raspberry pi mesh networking and rc control with wifi hardware

## Documentation:

### RADIO CONFIGURATION:

  #### yodel.setInterface(str)
  
    set the interface that yodel should operate on, will auto configure that interface.
    interfaces need to support monitor mode and packet injection. 
    (a list of valid interfaces can be found by using the "iw dev" command)
  #### yodel.setChannel(int):
    
    set what radio channel is being used.
    https://en.wikipedia.org/wiki/List_of_WLAN_channels
    using something in the 2.4ghz band (channels 1-11) will give best results.
    some leakage between channels will occur, in other words, if you are sending on channel 1  
    some of your messages can still be picked up by a robot listening on channel 2
    increasing the distrance between the channels will reduce this.
  #### yodel.setPower(int (dBm))
    
    set transmission power, using this may damage your wifi hardware.
    wifi interfaces usually sit somewhere between 2000dbm and 3000dbm.
    currently a limit of 3500 dBm is hardcoded to reduce odds of damaging hardware.
    this is hardcoded around line 70 in config.py.
   ** check local laws before adjusting your interfaces power. **


### SENDING AND RECEIVING:

  #### yodel.listen()
  
    returns messages sent to your robot.
    actual receiving is being taken care of by another thread so yodel.listen is non blocking.

  #### yodel.send(bytearray/int/string, name=str, group = str)
  
    send data defined by first parameter to a robot with a given name and/or who is a member group
    
    examples:
    yodel.send("Hello Yodler", name="Yodler")
    yodel.send("Hello group of Yodlers", group="Yodlers")
    yodel.send("Hello Yodler who is a member of the the group of yodlers", name="Yodler", group="Yodlers")
### MESH NETWORKING:

  #### yodel.enableRelay(bool)
  
    enable or disable mesh networking.
    True: mesh networking is enabled
    False: mesh networking is disabled
    mesh networking is disabled by default.

  
### GROUP MANAGMENT:

  #### yodel.addGroup(str)

    Add robot to new group defined by str

  #### yodel.deleteGroup(str)

    Leave group defined by str

  #### yodel.getGroups()
  
    Get a list containing all groups the robot is a member of

  #### yodel.clearGroups()
  
    Leave all groups

    
### GENERAL:

  #### yodel.setRepeats(int)

    set retransmission count

  #### yodel.setName(str)

    set robot name used when receiving messages

  #### yodel.getName()

    returns the current name

# Example Code

## Sender
``` python
import yodel
from time import sleep

yodel.startRadio("wlx00c0caa5efb2") #initiate radio on interface wlx00c0caa5efb2 (the interface name will differ on your system)

while True:

    yodel.send("this is a message", name="listener",group="group_of_robots") #send data to robots named "listener" who are a member of group_of_robots
    sleep(0.1) #sleep for .1 seconds(this is also just here as a convience)
    
```


## Receiver
``` python


import yodel
from time import sleep

yodel.startRadio("wlx00c0caa5efb2") #initiate radio on interface wlx00c0caa5efb2 (the interface name will differ on your system)
yodel.setName("listener")  #set the robot's name to listener
yodel.addGroup("group_of_robots")  #add robot to the group "group_of_robots"


while True:

    sleep(0.1) #sleep for .1 seconds, this is just a convience
    data = yodel.listen() #listen for all data sent to robots named "listener" and/or who are a member of "group_of_robots"
    if data: 
        print(data.payload) #if data is found print it


