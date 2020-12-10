from dynamicheaders import *


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

testpayload = [ #mtype: 2
    field("response",payload),
]


standard_header_format = format(standard_header)

""" 


headerobj = section(standard_header_format)
headerobj.mid = 5
headerobj.Rname = "ALden"
headerobj.Gname = "test"
headerobj.Sname = "Philo"
headerobj.mtype = 4
headerobj.payload = b'\xFF\xFF\xFF'
#headerobj.print()
headerobj.print()
print(headerobj.payload,"payloads")
print(bytes(headerobj))
#print(headerobj)

output = decode(bytes(headerobj),standard_header_format)
output[0].print() """