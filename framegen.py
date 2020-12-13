import random
import yodel.globaldat as globaldat
import yodel.classes as classes
import yodel.standardformats as standardformats
def typeManagment(data):
    dtype = type(data)
    if dtype == str:
        return(bytearray(data.encode(encoding='UTF-8', errors='strict')))
    elif dtype == bytes:
        return(data) 


