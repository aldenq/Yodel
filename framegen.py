import random
import globaldat
import classes
import standardformats
def typeManagment(data):
    dtype = type(data)
    if dtype == str:
        return(bytearray(data.encode(encoding='UTF-8', errors='strict')))
    elif dtype == bytes:
        return(data) 




def formPacket(tname, tgroup, data):
    identifier = "robot"
    tgroupB = bytearray(tgroup.encode(encoding='UTF-8', errors='strict'))
    tnameB = bytearray(tname.encode(encoding='UTF-8', errors='strict'))
    senderB = bytearray(globaldat.robotName.encode(encoding='UTF-8', errors='strict'))
    identifier = bytearray(identifier.encode(encoding='UTF-8', errors='strict'))
    frame_type = 0
    frame_typeB =  frame_type.to_bytes(1,'little')
    #dataB = bytearray(data.encode(encoding='UTF-8', errors='strict'))
    dataB = typeManagment(data)
    #buffer = 0
    namelen = len(tname)
    grouplen = len(tgroup)
    senderlen = len(sender)
    if namelen > 255 or grouplen > 255:
        raise NameTooLong
    mid = random.randint(0, 4294967295)
    globaldat.lastMessages.append(mid)
    mid = mid.to_bytes(4, 'little')
    output = identifier  # message type: 5 bytes
    output += frame_typeB
    output += mid  # message id: 4 bytes
    output += namelen.to_bytes(1, 'little')  # name length: 1 byte
    output += tnameB  # add bytes for actuall name, length determined by namelen
    output += grouplen.to_bytes(1, 'little')  # group name length: 1 byte
    output += tgroupB  # add bytes for actuall group name, length determined by grouplen
    output += senderlen.to_bytes(1,'little')
    output += senderB


    output += dataB  # add data bytes, they go until the end of the frame so no length is needed
    #oframe = classes.frameStruct()
    return (output)