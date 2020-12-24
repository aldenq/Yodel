import yodel.globaldat as globaldat
import yodel.classes as classes

def is_recipient(data,rlen):  #
    
    # print(lastMessages)
    
    frame = data[rlen+26+5:] #get data frame payload section
    pos = 0 #pos is used as a pointer to the current section of the header being decoded
    #ftype = frame[pos:pos+1]
    #print(frame)
    #print("abc1234567821A1",__name__)
    mID = frame[pos:pos + 4] #message id, the semi unique identifer to each message to avoid receiving them twice
    #print(__name__)
    #pos += 1
    #globaldat.bytesPrint(mID)
    if mID == globaldat.lastMid:  # since messages are repeated a lot it is worth saving the previous message id so that the array does not need to be fully indexed
        return (False)
    if mID not in globaldat.lastMessages: #check if message has already been received
        
        globaldat.lastMid = mID #set last mid to the current mid 
        # print(mID)
        globaldat.lastMessages.append(mID)
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