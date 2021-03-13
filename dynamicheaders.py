import copy
import math
from typing import *

import yodel.globaldat as globaldat


def typeManagment(data: Any) -> bytearray:
    '''
    Take in any type, and turn it into a bytearray
    '''
    dtype = type(data)
    if dtype == str:
        return(bytearray(data.encode(encoding='UTF-8', errors='strict')))
    elif dtype == bytes:
        return(data)


class Flags:
    '''
    Class meant to be used in fields, is an array of bools, used to store flags about the packet.

    Args:
        lookup_table: list of strings used to map keys to bits


    
    '''
    

    def __init__(self, lookup_table:list):
        length = 1
        self.data = [0, 0, 0, 0, 0, 0, 0, 0]
        self.lookup = {}  # lookup table, maps names provided by the field onto indexes in data
        self.a = 2
        if lookup_table:  # check if lookup table is provided
            # index lookup table, check to see if a name has been provided, if
            # so create an entry in lookup dict with the key as the name and
            # the value as the index
            for i in range(len(lookup_table)):
                key = lookup_table[i]
                # checks to see if the name provided for a given matrix is
                # None, this is so that ["a",None,"b"] will only set a key for
                # index 0 and 2
                if key is not None:
                    # create dict entry with key being a name provided and the
                    # value being the index being mapped to
                    self.lookup[key] = i

    def __setitem__(self, key, value):
        if type(key) == str:
            self.data[self.lookup[key]] = value
        else:
            self.data[key] = int(value)

    def __getitem__(self, key):
        if type(key) == str:
            return(self.data[self.lookup[key]])
        return(self.data[key])

    def __bytes__(self):
        out = 0
        for i in range(8):

            val = self.data[7 - i]
            out += val * 2**i
        return(out.to_bytes(1, 'little'))
        # return(int(data,2))

    def __repr__(self):
        out = ''
        for i in range(8):
            val = str(int(self.data[i]))
            out += val
        return(out)


class Format:
    """
    formats are used to store the information needed to encode or decode data.
    eg: first 3 bytes are a string, next 5 are for an int, etc.

    Args:
    	 fields: list of field objects that will define the format
    
    	 mtype: short for message type, allows unique identifiers to be given to your format that will be sent along with the format allowing for the receiver to know what format to use to decode the message
    """


    
    
    
    

    def __init__(self, fields:List, mtype: int = 0):
        self.mtype: int = mtype  # kwargs.get("mtype", 0) #get message type
        supported_types = [int, str, bytearray, Flags]
        # dictionary that holds field data formated as field name: field value
        self.fields_dict = {}
        # fields holds the list of fields provided, still holds lots of useful
        # meta data so it is kept around
        self.fields: list = fields
        self.output: dict = {}  # dict that holds field names and values, this is so that sections on init can just copy the info from here rather than regenerating it

        if self.mtype != 0:  # when a format is created and the message type is not zero store it in the array of message types so that autoDecode can use the format
            globaldat.messages_types[self.mtype] = self

        for i in range(
                len(fields)):  # copy data over and init output with field names
            fname = fields[i].name
            self.output[fname] = 0
            self.fields_dict[fname] = fields[i]

        # self.gen_data()


class Section:
    """
    sections are used to store data and the meta-data needed to encode that data.
    to get extract all of the data in a section use:
    section.fields

    sections can be encoded by using bytes(section), also,
    if a section is used in yodel.send it will automatically handle it.

    Args:
        format: format object to be used when encoding this section
    """






    def __init__(self, format: Format):
        # store format so that it can be accessed later as necessary
        self.__dict__["format"] = format
        # copy empty dict from format which has names already set
        self.__dict__["fields"] = copy.copy(format.output)
        # holds anything that comes after all fields have been filled
        self.__dict__["payload"] = b''

    def print(self):  # fancy print

        type_lookup = {
            bytearray: "Bytearray",
            int: "Int",
            Flags: "Flags",
            bytes: "bytes",
            str: "String"
        }

        for i in list(self.fields.keys()):
            name_len = len(str(i))
            space = 20

            dat_len = len(str(self.fields[i]))
            space2 = 20
            field_type = self.__dict__["format"].fields_dict[i].type

            print_type = type_lookup[field_type]
            if dat_len < space2:
                space2 = space2 - dat_len
            if name_len < space:
                space = space - name_len

            if field_type == str:
                # print rules for strings
                print(
                    f"{i}:{' '*space}\"{self.fields[i]}\"{' '*(space2 - 2)}{print_type}")
            elif field_type == int:
                # print rules for ints
                print(
                    f"{i}:{' '*space}{self.fields[i]}{' '*(space2)}{print_type}")
            elif field_type == Flags:
                # print rules for flags
                print(
                    f"{i}:{' '*space}{self.fields[i]}{' '*(space2)}{print_type}     {list(self.fields[i].lookup.keys())}")
            elif field_type == bytearray:
                print(
                    f"{i}:{' '*space}{self.fields[i]}{' '*(space2)}{print_type}")
        print(f"payload:{' '*space}{self.payload}")

    def __bytes__(self):
        return(evalBytes(self.__dict__["fields"], self.__dict__["format"], self.__dict__["payload"]))

    def __setattr__(self, name, value):
        if name != "payload":
            self.fields[name] = value
        else:
            self.__dict__["payload"] = value

    def __getattr__(self, name):
        if name != "payload":
            return(self.fields[name])
        else:
            return(self.__dict__["payload"])

    def __setitem__(self, key, value):
        self.fields[key] = value

    def __getitem__(self, key):
        return(self.fields[key])

    def __str__(self):
        return(str(self.fields))


class Field:
    '''
    A field is a section of memory meant to hold one value

    Args:
        name: name of field
        _type: data type to use in field
        bytes: when applicable this can hold the length of the field
    '''
    supported_types = [int, str, bytearray, Flags]
    def __init__(self, name: str, _type: Type, *args, bytes=0, min=0, max=0):
        bytes_len: int = bytes

        if _type == int:

            self.min = min
            self.max = max
            if bytes_len:
                self.len = bytes_len
                # signed integers are encoded using sign and magnitude
                self.min = -1 * 2**((bytes_len * 8) - 1)
                self.max = 2**((bytes_len * 8) - 1) - 1
            else:
                # when type is an int len tells us the amount of bits needed to
                # represent the possble options. when type is a str len tells
                # us the amount of bits needed to store the length of the
                # string
                self.len = math.ceil((max - min).bit_length() / 8)
            #self.len  =4
        elif _type == str or _type == bytearray:
            if bytes_len:
                max = bytes_len
            self.min = min
            self.max = max

            self.len = math.ceil((max - min).bit_length() / 8)

        elif _type == Flags:
            self.min = 0
            self.max = 0
            self.len = 1  # flags type is always one byte long
            if len(args) == 1:
                # take the array that holds the bit names
                self.lookup = args[0]
            else:
                self.lookup = False

        self.name = name  # field name
        self.type = _type  # field data type
        # self.len = math.ceil((Max-Min).bit_length()/8) #when type is an in
        # len tells us the amount of bits needed to represent the possble
        # options. when type is a str len tells us the amount of bits needed to
        # store the length of the string


def decode(data: bytearray, encoding: Format) -> Section:
    '''
    Returns list of all field names

    Args:
        data: bytearray of data that you want to decode

        encoding: format object to be used as the decoding rules
    '''
    fnames = list(encoding.fields_dict.keys())
    output = Section(encoding)  # generate new section object to store output
    cpos = 0  # current position, sort of a pointer to the bytearray
    for field in range(len(fnames)):
        fname = fnames[field]  # field name
        fieldobj = encoding.fields_dict[fname]
        ftype = fieldobj.type  # data type of the field
        flen = fieldobj.len  # field length
        # take the next n bytes where n is the length of the field
        fdata = data[cpos:cpos + flen]
        cpos += flen  # incriment the current position by the length of the field
        fmin = fieldobj.min  # min field value

        # all data types need their own custom decoding scheme

        if ftype == str:
            # get the size of the string by taking the first flen bytes and
            # converting them to an int
            strlen = globaldat.getInt(fdata)
            strlen += fmin
            # return the next n bytes where n is the length of the string
            # defined by strlen
            strdat = data[cpos:cpos + strlen]
            cpos += strlen  # move current position forward by the length of the string
            output[fname] = strdat.decode("utf-8")  # decode bytes as utf-8

        elif ftype == bytearray:
            # get the size of the bytearray by taking the first flen bytes and
            # converting them to an int
            bytelen = globaldat.getInt(fdata)
            bytelen += fmin
            # return the next n bytes where n is the length of the string
            # defined by bytelen
            strdat = data[cpos:cpos + bytelen]
            cpos += bytelen  # move current position by the length of the byte array
            # move the raw bytes into the appropriate place in the class
            output[fname] = strdat

        elif ftype == int:
            fout = globaldat.getInt(fdata)
            fout += fmin
            output[fname] = fout

        elif ftype == Flags:
            output[fname] = Flags([])
            # because this is python the only way to turn a byte into a list of
            # bits is to first convert it to an int, convert it to a utf-8
            # encoded string of bits, and split that list, than convert all the
            # terms into ints and return that as a list
            fout = list(bin(globaldat.getInt(fdata))[2:])
            fout = list(map(int, fout))
            # add appropriate 0 padding depedning on the length
            fout = [0] * (8 - len(fout)) + fout

            output[fname].data = fout

    output.payload = data[cpos:]
    return(output)


def evalBytes(field_dict: dict, format: Format,
              payload: bytearray) -> bytearray:
    '''
    Used in the __bytes__ method in the section class. Is used to return the
    bytes based on the field dict.

    Args:
        field_dict: a dictionary where the keys are field names, and the
        values are the values of those fields

        format: format object to be used when encoding data

        payload: any data that should be added on after the section has been formatted

    '''

    out = b''  # output is bytearray
    for i in format.fields_dict.keys():
        field_data = field_dict[i]

        format_field = format.fields_dict[i]  # take the field from the format
        field_type = format_field.type  # get the expected data type of the field
        #fmax = format_field.max
        # min length(when refering to bytearray or string)/ value(when refering
        # to an int)
        fmin = format_field.min
        flen = format_field.len  # length in bytes of field

        if field_type == type(
                field_data):  # check if the expected data type matches the actual type

            if field_type == int:
                # the amount of bytes for the int is included in the standard
                # so it does not need to be added to the output
                field_data -= format_field.min

                out += field_data.to_bytes(flen, 'little')

            elif field_type == Flags:  # flags are always 1 byte
                out += bytes(field_data)

            elif field_type == str:
                field_len = len(field_data)
                field_len -= fmin  # minimum length is subtracted because the reciever will add the min back before reading the bytes

                # for string the length of the string first needs to be added
                # as an int before the string data
                out += field_len.to_bytes(flen, 'little')

                # strings are encoded as a utf-8 string
                out += bytearray(field_data.encode(encoding='UTF-8',
                                                   errors='strict'))

            elif field_type == bytearray:
                field_len = len(field_data)
                field_len -= fmin
                # like strings, with byte arrays the length is added prior to
                # the data
                out += field_len.to_bytes(flen, 'little')
                out += field_data

            pass
    out += payload
    return(out)


def autoDecode(data: Section) -> Union[Section, bytearray]:
    '''
    automatically decodes the payload section of a given section, for this to work the format must be defined earlier on. 

    Args: 
    	data: Section a section to decode automatically
    @returns either a Section containing the formatted values of 'data', or data's payload
    '''
    mtype = data.mtype
    if mtype != 0:
        byte_data = data.payload
        return(decode(byte_data, globaldat.messages_types[mtype]))
    else:
        return(data.payload)
