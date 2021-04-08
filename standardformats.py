"""
this file defines some of the formats used internally for wrapping various types of messages the user might send

                 Anatomy of Standard Yodel Header

1 message ID: unique number, used to stop the same
  message being received more than once: 4 byte signed int

2 length of receiver name: 1 byte uint

3 receiver name: name of robot who should receiver
  this message: Length-prefixed string

4 length of Receiver group name: 1 byte uint

5 Receiver group name: group which the receiver
  is a member of

6 Sender Name Length: 1 byte uint

7 Sender Name: Name of sender: Length-prefixed string

8 message type: for the sake of informing the message decoder, stores
  a number which corrosponds to a known format defined by the user:
  1 byte signed int


┌────┬─┬──────┬─┬──────┬─┬───────┬─┐
│1   │2│3     │4│5     │6│7      │8│
└────┴─┴──────┴─┴──────┴─┴───────┴─┘

"""



from yodel.dynamicheaders import *


standard_header = [  #yodel standard header, begins all messages
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
