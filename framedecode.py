import globaldat
import classes
"""
def processFrame(data):  #
    
    # print(lastMessages)
    
    frame = data[49:] #get data frame payload section
    pos = 0 #pos is used as a pointer to the current section of the header being decoded
    ftype = frame[pos:pos+1]
    
    pos += 1
    mID = frame[pos:pos + 4] #message id, the semi unique identifer to each message to avoid receiving them twice
    
    if mID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (None)
    if str(mID) not in globaldat.lastMessages: #check if message has already been received
        
        globaldat.lastMid = mID #set last mid to the current mid 
        # print(mID)
        globaldat.lastMessages.append(str(mID))
        if len(globaldat.lastMessages) > 64:
            del globaldat.lastMessages[0]

       
        out = classes.frameStruct(frame)
        pos += 4
        namelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1

        name = frame[pos:pos + namelen].decode("utf-8")
        nameM = (name == globaldat.robotName or namelen == 0)

        pos += namelen
        gnamelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        group = frame[pos:pos + gnamelen].decode("utf-8")
        pos += gnamelen

        senderlen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        sender = frame[pos:pos + senderlen].decode("utf-8")

        groupM = (group in globaldat.groups or gnamelen == 0)
        if globaldat.relay == True and not (name == globaldat.robotName):
            out.relay = True
            #relayFrame(frame)

        if nameM and groupM:
            payl = frame[pos:]
            out = classes.frameStruct(frame)
            out.ftype=ftype
            out.sender=sender
            out.mid=mID
            out.group = group
            out.receiver = name
            out.payload = payl.decode("utf-8")
            out.relay = (namelen==0) & groupM

        return (out)
    return(None)
    # print((namelen))
"""
def is_recipient(data):  #
    
    # print(lastMessages)
    
    frame = data[49:] #get data frame payload section
    pos = 0 #pos is used as a pointer to the current section of the header being decoded
    #ftype = frame[pos:pos+1]
    
    pos += 1
    mID = frame[pos:pos + 4] #message id, the semi unique identifer to each message to avoid receiving them twice
    
    if mID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (None)
    if str(mID) not in globaldat.lastMessages: #check if message has already been received
        
        globaldat.lastMid = mID #set last mid to the current mid 
        # print(mID)
        globaldat.lastMessages.append(str(mID))
        if len(globaldat.lastMessages) > 64:
            del globaldat.lastMessages[0]

       
        #out = classes.frameStruct(frame)
        pos += 4
        namelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1

        name = frame[pos:pos + namelen].decode("utf-8")
        nameM = (name == globaldat.robotName or namelen == 0)

        pos += namelen
        gnamelen = globaldat.getInt(frame[pos:pos + 1])
        pos += 1
        group = frame[pos:pos + gnamelen].decode("utf-8")
        pos += gnamelen

        
        groupM = (group in globaldat.groups or gnamelen == 0)
        #if globaldat.relay == True and not (name == globaldat.robotName):
        #    relay = True
        relay = (globaldat.relay == True and not (name == globaldat.robotName))
            #relayFrame(frame)
        return(nameM and groupM,relay)
       
    return (False)
    # print((namelen))