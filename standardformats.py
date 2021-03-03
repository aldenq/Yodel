from yodel.dynamicheaders import *


standard_header = [ #begins all messages
    field("mid",int,bytes=4), #message id
    field("Rname",str,bytes=255), #receiver name
    field("Gname",str,bytes = 255), #group identifier
    field("Sname",str,bytes = 255), #sender name
    field("mtype",int,bytes = 1)  #message type
]



request = [  #mtype: 1
    field("request",str,255),
]
response = [ #mtype: 2
    field("response",str,255),
]



standard_header_format = format(standard_header)

