__author__ = "sharadth"
###########################Local import#########################################
from ssa import hwapi
from ssa import BasicStructs
import library
import lib_constants
import utils
################################################################################
# Function Name : valid_hex_data
# Parameters    : Hexadecimal value
# Functionality : This code will convert Hexadecimal input in 0x format
# Return Value :  Hexadecimal value in the 0x format
################################################################################
def valid_hex_data(value):
    if value.startswith('0x') and value.endswith('h'):                          #truncate based on input of bus,device and function
       value = value[:-1]
    elif value.endswith('h'):                                                   #if value endswith h, add 0x to the prefix
        value = '0x'+value[:-1]
    elif value.startswith('0x'):
        value=value
    else:                                                                       #if value doesn't endswith h and doesn't start with 0x, add 0x to the prefix
        value= '0x'+value
    return value
################################################################################
# Function Name : extract_token()
# Parameters    : string
# Functionality : This code will convert string input in list of parameters
# Return Value :  All parameters as a string
################################################################################
def extract_token(token_org, test_case_id, script_id, log_level, tbd):
    try:
        if "negative:" in token_org.lower():
            token_org = token_org.lower().split("negative:")[1].strip()
        token = token_org.split(" ")
        print(token_org)

        bus, dev, fun, off = token[5], token[7], token[9], token[11]

        if "bit" == token[13].lower():
            s_bit, e_bit = token[14], token[14]
            data = token_org.split("=")[1].strip()
            bit_val = None
        elif "range" == token[13].lower():
            s_bit = token[14].split(":")[0]
            e_bit = token[14].split(":")[1]
            data = token_org.split("=")[1].strip()
            bit_val = None
        else:
            s_bit = None
            e_bit = None
            bit_val_lhs = token_org.lower().split("bits")[1].split("=")[
                0].split(",")
            bit_val = []
            for i in bit_val_lhs:
                bit_val.append(i.strip())
            bit_data_list = token_org.split("=")[1].strip().split(",")
            data = []
            for i in bit_data_list:
                print(i)
                data.append(i.strip().split("'")[0])
        return(bus, dev, fun, off, s_bit, e_bit,data, bit_val)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "ERROR: Exception due to %s" % e, test_case_id,
                          script_id, "HWAPI", "None", log_level, tbd)
        return False
    
################################################################################
# Function Name : valid_data_range
# Parameters    : name of parameter,value of parameter,test case id,script id,
#                 log_level,tbd
# Functionality : This code will check the input value is in range of 0 to 31
# Return Value :  True/False
################################################################################
def valid_data_range(name ,value,test_case_id,script_id,log_level,tbd):         #Dword in constant
    if (int(value, lib_constants.HEX_BASE_VALUE) > lib_constants.BDF_HIGHBIT
        or int(value, lib_constants.HEX_BASE_VALUE) < lib_constants.BDF_LOWBIT):#check if values are in range
        library.write_log(lib_constants.LOG_INFO,"INFO:%s should be in range"
                            " of 0 and 31"%name,
                            test_case_id, script_id,"None", "None",
                            log_level, tbd)
        return False
    else:
        return True
################################################################################
# Function Name : write_value
# Parameters    : name of parameter,value of parameter,test case id,script id,
#                 log_level,tbd
# Functionality : this will perform writing operation of pci bdf value
# Return Value :  New value to be written
################################################################################
def write_value(start_bit,end_bit,data,read_value,test_case_id,script_id,
                log_level,tbd):
    data_replace = []
    start_bit =lib_constants.BDF_HIGHBIT - int(start_bit)                       #start bit for masking
    end_bit = lib_constants.BDF_HIGHBIT - int(end_bit)                          #end bit for masking
    read_value_int = int(read_value,lib_constants.HEX_BASE_VALUE)               #Value read of specific bit to be written
    for i in range(start_bit,end_bit+1):                                        #Series of data to be appended.
        data_replace.append(data);
    temp_read_value = bin(read_value_int)[2:]                                   #Integrate write value from read value
    read_value = temp_read_value.zfill(32)
    list_value = list(read_value)                                               #Generate write value using list method
    list_value[start_bit:end_bit+1] = data_replace
    write_val = "".join(list_value)                                             #Final value to be written in dword format
    write_val = int(write_val,2)
    library.write_log(lib_constants.LOG_INFO,"INFO:value to be updated is %s"
                            %write_val,test_case_id, script_id,"None", "None",
                            log_level, tbd)
    return write_val
################################################################################
# Function Name : write_value
# Parameters    : name of parameter,value of parameter,test case id,script id,
#                 log_level,tbd
# Functionality : this will perform writing operation of pci bdf value
# Return Value :  New value to be written
################################################################################
def write_multibit_value(multibit,data,read_value,test_case_id,script_id,
                log_level,tbd):
    read_value_int = int(read_value,lib_constants.HEX_BASE_VALUE)               #Value read of specific bit to be written
    temp_read_value = bin(read_value_int)[2:]                                   #Integrate write value from read value
    read_value = temp_read_value.zfill(32)
    list_value = list(read_value)                                               #Generate write value using list method
    for i in multibit:
        list_value[31-int(i,lib_constants.DECIMAL_BASE_VALUE)] = (data[0])      #Multibit data to be appended.
    write_val = "".join(list_value)                                             #Final value to be written in dword format
    write_val = int(write_val,2)
    library.write_log(lib_constants.LOG_INFO,"INFO:value to be updated is %s"
                            %write_val,test_case_id, script_id,"None", "None",
                            log_level, tbd)
    return write_val

################################################################################
# Function Name : read_bdf
# Parameters    : name of parameter,value of parameter,test case id,script id,
#                 log_level,tbd
# Functionality : This will read the PCI BDF value
# Return Value :  Returns the read value
################################################################################
def read_bdf(pciaddress,offset,test_case_id,script_id,log_level,tbd):
    endbit = lib_constants.BDF_HIGHBIT                                          #bdf High bit
    startbit = lib_constants.BDF_LOWBIT                                         #Bdf low bit
    bitvalid = True
    data_len = 32
    data_element = BasicStructs.DataElementFactory(data_len)
    data_element.Size = data_len
    muloffset = int(offset, lib_constants.HEX_BASE_VALUE) % 4                   #get the remainder of the muloffset after dividing it with 4 which are the extra bits
    hw = hwapi.HWAPI()
    hw.HWAPIInitialize()
    if 0 == muloffset:                                                          #checking offset is multiple of 4
        offset=int(offset, lib_constants.HEX_BASE_VALUE)                        #if its multiple of 4 just call pciread of hwapi and interpret data
        result = hw.PCIRead(pciaddress, offset, data_element)                   #do a pciread with address offset and dataelement
        uvalue = (data_element.Data[3] << 24)+(data_element.Data[2] << 16) + \
           (data_element.Data[1] << 8) + data_element.Data[0]

        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_INFO,
            "INFO:BDF call returned error",test_case_id, script_id,"HWAPI",
                              "None", log_level, tbd)
            return "false"

    else:                                                                       #if its not multiple of 4 do appropitate masking of data consider width of 32 bit and we have to read the two offsets and merge
        offset = int(offset, lib_constants.HEX_BASE_VALUE) - muloffset          #get offset after substracting the muloffset
        result = hw.PCIRead(pciaddress, offset, data_element)                   #do a pciread with pciadress offset and dataelement
        if (result != BasicStructs.eUserErrorCode["eNoError"]):
            library.write_log(lib_constants.LOG_INFO,
                "INFO:BDF call returned error",test_case_id, script_id,
                "HWAPI","None",log_level, tbd)
            return "false"

        if 1 == muloffset:                                                      #muloffset is 1 then store 0 in the last bit
            data_element.Data[0] = data_element.Data[1]
            data_element.Data[1] = data_element.Data[2]
            data_element.Data[2] = data_element.Data[3]
            data_element.Data[3] = 0x00

        elif 2 == muloffset:                                                    #muloffset is 2 then 0 in last two bit
            data_element.Data[0] = data_element.Data[2]
            data_element.Data[1] = data_element.Data[3]
            data_element.Data[2] = 0x00
            data_element.Data[3] = 0x00

        else:                                                                   #else store 0 in last three bits
            data_element.Data[0] = data_element.Data[3]
            data_element.Data[1] = 0x00
            data_element.Data[2] = 0x00
            data_element.Data[3] = 0x00

        uvalue1 = (data_element.Data[3] << 24) + (data_element.Data[2] << 16) +\
           (data_element.Data[1] << 8) + data_element.Data[0]

        offset += 4                                                             #increment offset  by 4
        result = hw.PCIRead(pciaddress, offset, data_element)
        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_INFO,
                "INFO:BDF call returned error",test_case_id, script_id,"None",
                "None", log_level, tbd)
            return "false"
        if 1 == muloffset:                                                      #if muloffset is 1 store 0 in last 3 bits
            data_element.Data[3] = data_element.Data[0]
            data_element.Data[0] = 0x00
            data_element.Data[1] = 0x00
            data_element.Data[2] = 0x00
        elif 2 == muloffset:                                                    #if muloffset is 2 store 0 in last 2 bits
            data_element.Data[3] = data_element.Data[1]
            data_element.Data[2] = data_element.Data[0]
            data_element.Data[0] = 0x00
            data_element.Data[1] = 0x00
        else:                                                                   #else store 0 in lst bit
            data_element.Data[3] = data_element.Data[0]
            temp = data_element.Data[2]
            data_element.Data[2] = data_element.Data[1]
            data_element.Data[1] = temp
            data_element.Data[0] = 0x00

        uvalue2 = (data_element.Data[3] << 24) + (data_element.Data[2] << 16) +\
           (data_element.Data[1] << 8) + data_element.Data[0]                   #get uvalue
        uvalue = uvalue1|uvalue2
        
    if True == bitvalid:                                                        #if bitvalid is true
        if(startbit == endbit):
            mask = (1 << int(startbit))                                         #leftshift 1 bit for endbit
            finalresult = ((int(uvalue) & mask))>>int(startbit)
        else:
            mask = (1 <<(int(endbit)-int(startbit)+1)) - 1                      #calculate the mask by left shift 1 from the difference of startbit and endbit+1 and then substract 1 from the result
            finalresult = (int(uvalue) >> int(startbit)) & mask
        hex_result = "0x"+hex(finalresult)[2:].strip('L').upper()
        library.write_log(lib_constants.LOG_INFO,                               #startbit should be grater than endbit
        "INFO:Pci bdf value read is %s"%hex_result, test_case_id,script_id,
                          "HWAPI", "None",log_level, tbd)
        return hex_result
################################################################################
# Function Name : write_pci_bdf
# Parameters    : token,test case id,script id,log_level,tbd
# Functionality : This will write the PCI BDF value
# Return Value :  Returns the true if successfully written
################################################################################
def write_pci_bdf(token, test_case_id,script_id, log_level, tbd):

    bus_value,device_value,fun_value,offset_value,start_bit_value,\
    end_bit_value,data,bitval = extract_token(token,test_case_id,
                                       script_id,log_level,tbd)                 #extract values from token

    bus_value = valid_hex_data(bus_value)                                       #bus number converted to 0xformat
    device_value = valid_hex_data(device_value)                                 #device number converted to 0xformat
    fun_value = valid_hex_data(fun_value)                                       #function number converted to 0xformat
    offset_value = valid_hex_data(offset_value)                                 #offset converted to 0xformat
    library.write_log(lib_constants.LOG_INFO,                                   #startbit should be grater than endbit
        "INFO:Bdf value to be changed is Bus value:%s, Device value:%s, func "
        "value:%s, offset value:%s"%(bus_value,device_value,fun_value,
                                     offset_value), test_case_id,script_id,
                      "HWAPI", "None",log_level, tbd)

    if bitval:                                                                  #Checks if bit value is not None
        if len(bitval) == len(data):                                            #Checks if each bit has its value to be written
            pass
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING:length of "
                              "Multi bit and data value are not same",
                              test_case_id, script_id, "HWAPI", "None",
                              log_level, tbd)
    else:
        if (int(start_bit_value) not in list(range(lib_constants.BDF_LOWBIT,
                                              lib_constants.BDF_HIGHBIT))) \
                or (int(end_bit_value) not in list(range(lib_constants.BDF_LOWBIT,
                                                    lib_constants.BDF_HIGHBIT)))\
                    or (int(start_bit_value) < int(end_bit_value)):             #if startbit and endbit are not between 0 and 8
            library.write_log(lib_constants.LOG_INFO,                           #startbit should be grater than endbit
            "INFO:Given Bit value should be in range of 0 and 31 and endbit "
            "should be greater than startbit", test_case_id, script_id,"HWAPI",
                              "None",log_level, tbd)

            return False
        else:
            pass

    if(int(offset_value, lib_constants.HEX_BASE_VALUE) >
        lib_constants.BIT_MAX_RANGE or
            int(offset_value, lib_constants.HEX_BASE_VALUE) <
               lib_constants.BIT_MIN_RANGE):                                    #if ofsset is not between 0 and 255
            library.write_log(lib_constants.LOG_INFO,"INFO: Offset value should"
                " be in range of 0 and 255",test_case_id, script_id,
                    "HWAPI","None", log_level, tbd)

            return False

    hw = hwapi.HWAPI()                                                          #calling hwapi module
    hw.HWAPIInitialize()                                                        #initializing hwapi module
    pciaddress = BasicStructs.PCIConfAddr(int(bus_value,                        #making a structure of bus, dev,fun values
                                              lib_constants.HEX_BASE_VALUE),
                                          int(device_value,
                                              lib_constants.HEX_BASE_VALUE),
                                          int(fun_value,
                                              lib_constants.HEX_BASE_VALUE), 0)
    read_value = read_bdf(pciaddress,offset_value,                              #read initial value
                          test_case_id,script_id,log_level,tbd)
    if bitval:
        write_data = write_multibit_value(bitval,data,read_value,test_case_id,
                                          script_id,log_level,tbd)
    else:
        write_data = write_value(start_bit_value,end_bit_value,data,read_value, #Generate the value to be written on pci bdf
                             test_case_id,script_id,log_level,tbd)
    data_element = BasicStructs.DataElementFactory(lib_constants.               #Buffer of size Dword
                                                   HWAPI_DATA_ELEMENT_SIZE)
    data_element.Data[0] = (write_data & 0xff)                                  #assign value in Buffer of hwapi as single byte
    data_element.Data[1] = (write_data >> 8) & 0xff
    data_element.Data[2] = (write_data >> 16)& 0xff
    data_element.Data[3] = (write_data >> 24)& 0xff
    data_element.Size = lib_constants.HWAPI_DATA_ELEMENT_SIZE                   #Size of buffer to be written

    result = hw.PCIWrite(pciaddress, int(offset_value,
        lib_constants.HEX_BASE_VALUE), data_element)                            #Write Pci BDF
                                                                                #write pci bdf value, result = 1 if pass

    if result != BasicStructs.eUserErrorCode["eNoError"]:                       #If writing pci bdf value fails eNoError will not come.
        library.write_log(lib_constants.LOG_INFO,
        "INFO:BDF call returned error",test_case_id, script_id,"HWAPI",
                          "None", log_level, tbd)
        return False
    else:

        new_val = read_bdf(pciaddress, offset_value, test_case_id, script_id,
              log_level, tbd)

        if write_data != int(new_val, 16):
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                             "verify BDF wrritten data", test_case_id,
                              script_id, "HWAPI", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,                               #Write Pci BDF done successsfully
                "INFO: BDF VALUE %s written successfully"%str(write_data),
                              test_case_id, script_id, "HWAPI","None",log_level,tbd)
            return True
################################################################################