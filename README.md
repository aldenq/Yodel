# Yodel
raspberry pi mesh networking and rc control with wifi hardware

Documentation:

Radio Configuration:

  yodel.setInterface(str)
  
    set the interface that yodel should operate on, will auto configure that interface.
    interfaces need to support monitor mode and packet injection. 
    
  yodel.setChannel(int):
    
    set what radio channel is being used.
    https://en.wikipedia.org/wiki/List_of_WLAN_channels
    using something in the 2.4ghz (channels 1-11) band will give best results.
    
  yodel.setPower(int (dBm))
    
    set transmission power, using this may damage your wifi hardware. wifi interfaces usually sit somewhere between 2000dbm and 3000dbm. currently a limit of 3500 dBm is hardcoded to reduce odds of damaging hardware. this is hardcoded around line 70 in config.py. check local laws before adjusting your interfaces power.   


Sending and Receiving:

  yodel.listen()
  
    returns for messages sent to your robot. actual receiving is being taken care of by another thread so yodel.listen is non blocking.

  yodel.send(bytearray/int/string, name=str, group = str)
  
    send data defined by first parameter to a robot with a given name and/or who is a member group
    
    examples:
    yodel.send("Hello Yodler", name="Yodler")
    yodel.send("Hello group of Yodlers", group="Yodlers")
    yodel.send("Hello Yodler who is a member of the the group of yodlers", name="Yodler", group="Yodlers")
Mesh Networking:

  yodel.enableRelay(bool)
  
    enable or disable mesh networking.
    True: mesh networking is enabled
    False: mesh networking is disabled
  
    
  










yodel.setRepeats(int)
  
  set retransmission count

yodel.setName(str)

  set robot name used when receiving messages

yodel.getName()

  returns the current name
  
GROUP MANAGMENT:

  yodel.addGroup()

    Add robot to new group

  yodel.deleteGroup(str)

    Leave group defined by str

  yodel.getGroups()
  
    Get a list containing all groups the robot is a member of

  yodel.clearGroups()
  
    Leave all groups



