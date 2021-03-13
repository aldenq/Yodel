"""
this file defines some of the formats used internally for wrapping various types of messages the user might send



"""



from yodel.dynamicheaders import *


standard_header = [  # begins all messages
    Field("mid", int, bytes=4),  # message id
    Field("Rname", str, bytes=255),  # receiver name
    Field("Gname", str, bytes=255),  # group identifier
    Field("Sname", str, bytes=255),  # sender name
    Field("mtype", int, bytes=1)  # message type
]


request = [  # mtype: 1
    Field("request", str, 255),
]
response = [  # mtype: 2
    Field("response", str, 255),
]


standard_header_format = Format(standard_header)
