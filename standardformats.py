from yodel.dynamicheaders import *


standard_header = [ #begins all messages
    field("mid",int,4294967296), #message id
    field("Rname",str,255), #receiver name
    field("Gname",str,255), #group identifier
    field("Sname",str,255), #sender name
    field("mtype",int,255)  #message type
]



request = [  #mtype: 1
    field("request",str,255),
]
response = [ #mtype: 2
    field("response",str,255),
]



standard_header_format = format(standard_header)

