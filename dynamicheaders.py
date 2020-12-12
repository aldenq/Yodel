import globaldat,math

        
class flags:  #class meant to be used in fields, is an array of bools, used to store flags about the packet
    # 
    #
    length = 1
    def __setitem__(self,key,value):
        if type(key) == str:
            self.data[self.lookup[key]] = value
        else:
            self.data[key] = int(value)


    def __init__(self,lookup):
        self.data = [0,0,0,0,0,0,0,0]
        self.lookup = {}
        
        if lookup:
            #print(lookup)
            for i in range(len(lookup)):
                key = lookup[i]
                if key != None:
                    self.lookup[key] = i
                    


    
    def __getitem__(self, key):
       if type(key) == str:
           return(self.data[self.lookup[key]])
       return(self.data[key])
    
    def __bytes__(self):
        out = 0
        for i in range(8):
            
            val = self.data[7-i]
            out += val*2**i
        return(out.to_bytes(1, 'little'))
        #return(int(data,2))
    
  
    def __repr__(self):
        out = ''
        #print(self.data,"self.data")
        for i in range(8):
            val = str(self.data[i])
            out += val
        return(out)
    
class format:
    supported_types = [int,str,bytearray,flags]
    def __init__(self, fields):
        self.fields_dict = {}
        self.fields = fields
        for i in range(len(fields)):
            fname = fields[i].name
            if fname in self.fields_dict:
                print("warn: header name repeat.")
            self.fields_dict[fname] = fields[i]
        #print(self.fields_dict)


        
    
class section:
    #resvd = []
    #intern = {}
    #flds = {}

    def print(self): #fancy print 
        
        type_lookup = {
"<class 'int'>":"Int",
"<class '__main__.flags'>":"Flags",
"<class '__main__.payloads'>":"Payloads",
"<class 'bytes'>":"bytes",
"<class 'str'>":"String"}
        
        for i in list(self.fields.keys()):
            name_len = len(str(i))
            space = 20

            dat_len = len(str(self.fields[i]))
            space2 = 20
            isstr = type(self.fields[i]) == str
            print_type = type_lookup[str(type(self.fields[i]))]
            if dat_len < space2:
                space2 = space2-dat_len
            if name_len < space:
                space = space - name_len
                
            
            if type(self.fields[i]) == str:    
                print(f"{i}:{' '*space}\"{self.fields[i]}\"{' '*(space2 - 2*isstr)}{print_type}") #print rules for strings
            elif type(self.fields[i]) == int:    
                print(f"{i}:{' '*space}{self.fields[i]}{' '*(space2 - 2*isstr)}{print_type}") #print rules for ints
            elif type(self.fields[i]) == flags:    
                print(f"{i}:{' '*space}{self.fields[i]}{' '*(space2 - 2*isstr)}{print_type}     {list(self.fields[i].lookup.keys())}") #print rules for flags
           
        print(f"payload:{' '*space}{self.payload}" )
    def __bytes__(self):
        return(evalBytes(self.__dict__["fields"],self.__dict__["format"],self.__dict__["payload"]))
    
    def __setattr__(self, name, value):
        #print("set", name , value)
        if name != "payload":
            self.fields[name] = value
        else:
            self.__dict__["payload"] = value
        
    
    def __getattr__(self, name):
        if name != "payload":
            return(self.fields[name])
        else:
            return(self.__dict__["payload"])
       

    def __setitem__(self,key,value):
        self.fields[key] = value
        
    def __getitem__(self, key):
       return(self.fields[key])
    
    def __str__(self):
        return(str(self.fields))

    def __init__(self,format):
        self.__dict__["format"] = format
        self.__dict__["fields"] = {}
        self.__dict__["payload"]= b''
        for i in list(format.fields_dict.keys()):
            #print(self.__dict__.keys())
            if format.fields_dict[i].type==flags: #some fields are using classes instead of data types, these need to be hard coded
                lookup  = format.fields_dict[i].lookup
                self.__dict__["fields"][i] = flags(lookup)
            
            #elif format.fields_dict[i].type==payload:
                #self.__dict__["fields"][i] = payload()
            else:
                self.__dict__["fields"][i] = 0



        
    




class field:  #used to create new fields, a field being a section of memory meant to hold one value
    def __init__(self,Name,Type,*args):
        if Type==int or Type == str:
            #min/max: when type is an integer min refers to the smallest possible integer and max refers to the largest
            #when type is a string or byte array than min refers to the shortest possible str and max refers to the longest possible
            if len(args) == 2:
                Min,Max = args
            if len(args) == 1:
                Max = args[0] #if only one number is given it is assumed to be the max length/ int size and the min is assumed to be zero
                Min = 0

        
            self.min = Min
            self.max = Max
            self.len = math.ceil((Max-Min).bit_length()/8) #when type is an int len tells us the amount of bits needed to represent the possble options. when type is a str len tells us the amount of bits needed to store the length of the string
        elif Type == flags:
                self.min= 0
                self.max = 0
                self.len = 1 #flags type is always one byte long
                if len(args) == 1:
                    self.lookup = args[0]
                else:
                    self.lookup = False
                
       
        self.name = Name #field name
        self.type = Type #field data type
        #self.len = math.ceil((Max-Min).bit_length()/8) #when type is an in len tells us the amount of bits needed to represent the possble options. when type is a str len tells us the amount of bits needed to store the length of the string
        
def decode(data,encoding):
    fnames = list(encoding.fields_dict.keys()) #returns list of all field names
    output = section(encoding) #generate new section object to store output
    cpos = 0 #current position, sort of a pointer to the bytearray
    for field in range(len(fnames)):
        fname = fnames[field] #field name
        fieldobj = encoding.fields_dict[fname]
        ftype = fieldobj.type #data type of the field
        flen = fieldobj.len #field length
        fdata = data[cpos:cpos+flen] #take the next n bytes where n is the length of the field
        cpos += flen #incriment the current position by the length of the field
        fmin = fieldobj.min #min field value
        
        #all data types need their own custom decoding scheme
        
        if ftype == str:
            strlen = globaldat.getInt(fdata) #get the size of the string by taking the first flen bytes and converting them to an int
            strlen += fmin
            strdat = data[cpos:cpos+strlen] #return the next n bytes where n is the length of the string defined by strlen
            cpos += strlen #move current position forward by the length of the string
            output[fname] = strdat.decode("utf-8") #decode bytes as utf-8
            
            
        elif ftype == bytearray:
            bytelen = globaldat.getInt(fdata) #get the size of the bytearray by taking the first flen bytes and converting them to an int
            bytelen += fmin
            strdat = data[cpos:cpos+bytelen] #return the next n bytes where n is the length of the string defined by bytelen
            cpos += bytelen #move current position by the length of the byte array
            output[fname] = strdat #move the raw bytes into the appropriate place in the class
            
            
        elif ftype == int:
            fout = globaldat.getInt(fdata)
            fout += fmin
            output[fname] = fout
            
        elif ftype == flags: 
            
            fout = list(bin(globaldat.getInt(fdata))[2:]) #because this is python the only way to turn a byte into a list of bytes is to first convert it to an int, convert it to a utf-8 encoded string of bits, and split that list, than convert all the terms into ints and return that as a list
            fout= list(map(int,fout))
            fout = [0]*(8-len(fout)) + fout #add appropriate 0 padding depedning on the length
            
            output[fname].data =fout
            
        
                    
            
            
        
    output.payload = data[cpos:]      
    return(output)
        
        

            
def evalBytes(field_dict, format,payload): #used in the __bytes__ method in the section class. is used to return the bytes based on the field dict.
    #field_dict is a dictionary where the keys are field names, and the values are the values of those fields
    
    out = b'' #output is bytearray
    for i in format.fields_dict.keys():
        field_data = field_dict[i]
        format_field = format.fields_dict[i]  #take the field from the format
        field_type = format_field.type #get the expected data type of the field
        
        #fmax = format_field.max 
        fmin = format_field.min #min length(when refering to bytearray or string)/ value(when refering to an int)
        flen = format_field.len #length in bytes of field
            
        if field_type == type(field_data): #check if the expected data type matches the actual type
            
            if field_type == int:
                #the amount of bytes for the int is included in the standard so it does not need to be added to the output
                
                field_data -= format_field.min
                out += field_data.to_bytes(flen, 'little')
               
            elif field_type == flags: #flags are always 1 byte
                out += bytes(field_data)
                
            elif field_type == str: 
                field_len = len(field_data)
                field_len -= fmin #minimum length is subtracted because the reciever will add the min back before reading the bytes
                out += field_len.to_bytes(flen, 'little') #for string the length of the string first needs to be added as an int before the string data
                out += bytearray(field_data.encode(encoding='UTF-8', errors='strict')) #strings are encoded as a utf-8 string
                
            elif field_type == bytearray:
                field_len = len(field_data)
                field_len -= fmin
                out += field_len.to_bytes(flen, 'little') #like strings, with byte arrays the length is added prior to the data
                out += field_data
            

          
                



            
            pass
        else:
            print("bad",field_data,field_type,i)
    out += payload        
    return(out)






        
