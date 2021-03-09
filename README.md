# Yodel
Yodel is a python library that uses WIFI hardware for remote control purposes. Because it does not rely on wifi hotspots it has a far greater range than simple wifi based remote control solutions at the cost of bandwidth. Yodel is it's own protocol that sits under 80211. Yodel was designed specifically with Raspberry PI robotics in mind however it should work with any linux computer with an appropriate wifi interface.



## Thanks to:
    Phil0nator: for helping with maintaining code readabiltiy



## Setup and Config:
yodel is available through pip, use:

sudo pip3 install yodelnet


Next, you will need a system with a WIFI interface on it that supports Monitor mode and packet injection, if your built in card does not support it look for a USB wifi dongle that supports monitor mode and packet injection. 
I have had a lot of luck with:https://www.amazon.com/Wifi-Antenna-Raspberry-Pi-Instructions/dp/B00H95C0A2/ but many others exist that will work.
when looking for a wifi dongle it only needs to support 2.4ghz, i would also recommend getting one with an external antenna to improve range. 
Once you have a supported wifi interface on your system, for the most part are good to go, you probably want 2 computers with supported hardware as without this you will only be able to talk with yourself. 
You will need to get the interface id for the wifi interface you would like to use, this can be done with the "iw dev" command. 
this will be needed in the "yodel.startRadio" function call in your code.
## Misc Info:
  programs using yodel need to be ran as root. 
  
  the internal WIFI antenna inside raspberry pi's are not combatible without a chunk of work, it appears to be a driver issue, if you want to look into 
  getting Yodel working on the internal WIFI interface google "patching raspberry pi wifi drivers for monitor mode and packet injection"(ping me if you get this working). I would reccomend just buying a cheap USB Dongle such as the one above.

 if you are having any problems related to unreliable or no data coming through check the channels on both devices
## Documentation:

### RADIO CONFIGURATION:

  #### yodel.startRadio(str)
  
    set the interface that yodel should operate on, will auto configure that interface.
    interfaces need to support monitor mode and packet injection. 
    (a list of valid interfaces can be found by using the "iw dev" command)
  #### yodel.setChannel(int)
    
    set what radio channel is being used.
    https://en.wikipedia.org/wiki/List_of_WLAN_channels
    using something in the 2.4ghz band (channels 1-11) will give best results.
    some leakage between channels will occur, in other words, if you are sending on channel 1  
    some of your messages can still be picked up by a robot listening on channel 2
    increasing the distance between the channels will reduce this.
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

  
### GROUP MANAGEMENT:

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
### DATA MANAGMENT:
  yodel.send() only takes in bytearrays, strings and integers. This is great for most simple uses but to send more complicated data sets say one int followed by 3 strings you would need to create your own encoding and decoding scheme. yodel has a built in encoding and decoding scheme. three main structures exist and a couple functions exist to faciliate this. 

first, some example code to ground this:

``` python
lighting_header = [
    
    yodel.Field("lights",yodel.Flags,["red","green","yellow"])
    
]
lighting_format = yodel.Format(lighting_header)


lighting_data = yodel.Section(lighting_format)


lighting_data.lights["red"] = True
```

  #### yodel.Field()
    defines a data field, fields are used to create larger structs, the exact parameters you will have to provide depend on the field type you use
    here are some examples:
    yodel.field("distance",int,bytes=2)
    yodel.field("name",str,bytes=50)
    yodel.field("misc_data",bytearray,bytes=20)
     yodel.field("misc_data",yodel.flags) 


  #### yodel.Format(field list)
    this function takes in a list of fields and converts it into a format object, this format object can later be used to decode incoming bytes or create 
    and store new data in the selected format.


  #### yodel.Section(format)
    sections are empty objects with attributes for each field in the provided format. they are designed to be filled with data and then sent via yodel.send.
    





# Example Code

## Sender
``` python
import yodel
from time import sleep

yodel.startRadio("wlx00c0caa5efb2") #initiate radio on interface wlx00c0caa5efb2 (the interface name will differ on your system)
yodel.setChannel(5)
while True:

    yodel.send("this is a message", name="listener",group="group_of_robots") #send data to robots named "listener" who are a member of group_of_robots
    sleep(0.1) #sleep for .1 seconds(this is also just here as a convenience)
    
```


## Receiver
``` python


import yodel
from time import sleep

yodel.startRadio("wlx00c0caa5efb2") #initiate radio on interface wlx00c0caa5efb2 (the interface name will differ on your system)
yodel.setName("listener")  #set the robot's name to listener
yodel.addGroup("group_of_robots")  #add robot to the group "group_of_robots"
yodel.setChannel(5)

while True:

    sleep(0.1) #sleep for .1 seconds, this is just a convenience
    data = yodel.listen() #listen for all data sent to robots named "listener" and/or who are a member of "group_of_robots"
    if data: 
        print(data.payload) #if data is found print it


