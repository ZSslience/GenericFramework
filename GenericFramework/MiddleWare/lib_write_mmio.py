__author__ = 'kapilshx'
############################General Python Imports##############################
import sys
import utils
############################Local Python Imports################################
import lib_constants
import library
import lib_constants
from ssa import hwapi
from ssa import BasicStructs
import lib_read_mmio
################################################################################
# Function Name : write MMIO
# Parameters    : ostr, test case id, script id, loglevel, tbd
# Functionality : This code will extract the token and call read mmio
#                 and write mmio function
# Return Value :  return True on success,false otherwise
################################################################################
def write_mmio(ostr, test_case_id, script_id, loglevel="ALL", tbd="None"):
    try:
        mmio_write_token = ostr.split(" ")
        pciaddress = mmio_write_token[4]                                        #extract pciaddress from token
        offset = mmio_write_token[6]                                            #extract offset from token
        data_value =mmio_write_token[8]                                         #extract data_value from token
        result = []
        for value in [pciaddress,offset,data_value]:                            #loop to check pciaddress and offset in hex format
            result.append(mmio_value_extract(value, test_case_id, script_id,
                                             loglevel, tbd))
        if False in result:
            return False
        pciaddress,offset,data_value = result[0],result[1],result[2]            #store values from list
        bit = int(offset,lib_constants.HEX_BASE_VALUE)
        output = [(valid_data_range(bit,lib_constants.BIT_MAX_RANGE,
            lib_constants.BIT_MIN_RANGE, "Offset",test_case_id, script_id,
                                    loglevel, tbd)),
                  (valid_data_range(bit, lib_constants.BIT_MAX_RANGE,
            lib_constants.BIT_MIN_RANGE, "Data_value", test_case_id,
                                    script_id, loglevel, tbd))]
        if False in output:                                                     #function call to check offset and data_value range from 0 to 255
            return False
        if(True == read_mmio_specific(pciaddress,offset, test_case_id, script_id,
                    loglevel, tbd)):                                            #function call to read the mmio value using hw api
            pass
        else:                                                                   #if fails to read the mmio value using hw api
            library.write_log(lib_constants.LOG_FAIL,
            "FAIL: MMIO read failed for input %s" %ostr,
             test_case_id, script_id, "None","None", loglevel, tbd)
            return False

        if (True == write_mmio_specific(pciaddress, offset, data_value,
                            test_case_id, script_id,loglevel, tbd)):            #function call to write the mmio value using hw api
            pass
        else:                                                                   #if fails to write the mmio value using hw api
            library.write_log(lib_constants.LOG_FAIL,
            "FAIL: MMIO write failed for input %s" %ostr,
             test_case_id, script_id, "None","None", loglevel, tbd)
            return False

        if(True == read_mmio_specific(pciaddress,offset, test_case_id, script_id,
                    loglevel, tbd)):                                            #function call to read the mmio value using hw api to verify the write mmio value
            return True
        else:                                                                   #if fails to read the mmio value using hw api
            library.write_log(lib_constants.LOG_FAIL,
            "FAIL: Failed to Verified MMIO read for input %s" %ostr,
             test_case_id, script_id, "None","None", loglevel, tbd)
            return False
            
    except Exception as e:                                                      #if exception occurs in write mmio() funtion
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured"
            " in write_mmio due to %s"%e,test_case_id, script_id,
                          loglevel, tbd)
        return False
################################################################################
# Function Name : write_mmio_specific
# Parameters    : pci address,offset,data_value, test case id,script id,
#                 loglevel, tbd
# Functionality : This code will write the MMIO offset using hw api and return
#                 value in result
# Return Value :  return True on success,false otherwise
################################################################################
def write_mmio_specific(pciaddress, offset, data_value, test_case_id,
                        script_id, loglevel="ALL", tbd="None"):
    try:

        data_value = (bin(int(data_value,
                              lib_constants.HEX_BASE_VALUE))[2:]).zfill(8)      #convert data_value into 8 bit binary
        hw = hwapi.HWAPI()
        result = hw.HWAPIInitialize()                                           #to initialize the hwapi
        msrInfo = BasicStructs.MSRInfoBlock()
        size = lib_constants.HWAPI_DATA_ELEMENT_SIZE                            #to consider the whole 32 bit data
        data_element = BasicStructs.DataElementFactory(size)
        data_element.Data[0] = int(data_value,lib_constants.BINARY_BASE_VALUE)  #to store 8 bit binary data into data_element attribute

        result = hw.PCIMMIOWrite(int(pciaddress,lib_constants.HEX_BASE_VALUE),
                    int(offset,lib_constants.HEX_BASE_VALUE), data_element)     #function call to write the data value at given pciaddress and offset
        if False == HWAPIerror(result, test_case_id, script_id,
                               loglevel, tbd):                                  #if fails to write the data value at given pciaddress and offset
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
        "INFO: MMIO Write 8 bit data successfully for input %s %s = %s"
        %(pciaddress,offset,hex(int(data_value,lib_constants.BINARY_BASE_VALUE))),
         test_case_id, script_id, "None","None", loglevel, tbd)
            return True
    except Exception as e:                                                      #exception occurs in read_mmio_specific() function
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured"
            " in read_mmio_specific due to %s"%e,test_case_id, script_id,
                          loglevel, tbd)
        return False
###############################################################################
# Function Name : mmio_value_extract
# Parameters    : value, test case id,script id,
#                 loglevel, tbd
# Functionality : This code will extract the pciaddress and offset value
#  Return Value : return True on success,false otherwise
#############################################################################
def mmio_value_extract(value, test_case_id, script_id, loglevel="ALL",
                       tbd="None"):
    try:
        if(value.endswith('H')) or (value.endswith('h')):                       #to check if "h" or "H" is present in value string
            return('0x' + value[:-1])
        elif (value.startswith('0x') or value.startswith('0X')):                #to check if "0x" or "0X" is present in value string
            return value
        else:
            library.write_log(lib_constants.LOG_INFO,
                "%s should be in hex format"%(value),test_case_id, script_id,
                "None","None", loglevel, tbd)
            return False
    except Exception as e:                                                      #exception occurs in mmio_value_extract() function
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured"
            " in mmio_value_extract() function due to %s"%e,test_case_id,
                          script_id,loglevel, tbd)
        return False
################################################################################
# Function Name : read_mmio_specific
# Parameters    : pci address,offset, test case id,script id,
#                 loglevel, tbd
# Functionality : This code will read the MMIO offset using hw api
# Return Value :  return True on success,false otherwise
################################################################################
def read_mmio_specific(pciaddress, offset, test_case_id, script_id,
                       loglevel="ALL", tbd="None"):
    try:
        hw = hwapi.HWAPI()                                                      #hwapi call
        result = hw.HWAPIInitialize()                                           #initialise the hwapi
        data_len = lib_constants.HWAPI_DATA_ELEMENT_SIZE
        data_element = BasicStructs.DataElementFactory(data_len)                #get data element from basicstructs dataelementfactory function
        data_element.Size = data_len
        muloffset = int(offset, lib_constants.HEX_BASE_VALUE) % 4               #converting to integer and getting the extra bits that will remain after converting to byte
                                                                                #checking offset is multiple of 4
        if 0 == muloffset:
                                                                                #if its multiple of 4 just call pciread of hwapi and interpret data
            result = hw.PCIMMIORead(int(pciaddress,lib_constants.HEX_BASE_VALUE)
                    , int(offset,lib_constants.HEX_BASE_VALUE), data_element)   #store PCIMMIORead call function return value in result
                                                                                #removing last 3 byte from the dataword
            uvalue = valueofbit(data_element)
            if False == HWAPIerror(result, test_case_id, script_id,
                                   loglevel, tbd):
                return False
        else:                                                                   #if its not multiple of 4 do appropitate masking of data consider width of 32 bit and we have to read the two offsets and merge
            offset = int(offset, lib_constants.HEX_BASE_VALUE) - muloffset      #converting from hexadecimal to integer and then substracting the muloffset
            result = hw.PCIMMIORead(pciaddress, offset, data_element)
            HWAPIerror(result, test_case_id, script_id,
                       loglevel, tbd)
            if 1 == muloffset:
                data_element.Data[0] = data_element.Data[1]                     #when muloffset is 1 put defa
                data_element.Data[1] = data_element.Data[2]
                data_element.Data[2] = data_element.Data[3]
                data_element.Data[3] = 0x00
            elif 2 == muloffset:
                data_element.Data[0] = data_element.Data[2]                     #muloffset is 2
                data_element.Data[1] = data_element.Data[3]
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00
            else:
                data_element.Data[0] = data_element.Data[3]                     #else muloffset is 0
                data_element.Data[1] = 0x00
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00

                uvalue_first = valueofbit(data_element)
                offset += 4                                                     #increment offset by 4
                result = hw.PCIMMIORead(pciaddress, offset, data_element)

                if False == HWAPIerror(result, test_case_id, script_id,
                                       loglevel, tbd):
                    return False

                if 1 == muloffset:                                              #muloffset equals 1
                    data_element.Data[3] = data_element.Data[0]
                    data_element.Data[0] = 0x00
                    data_element.Data[1] = 0x00
                    data_element.Data[2] = 0x00
                elif 2 == muloffset:
                    data_element.Data[3] = data_element.Data[1]                 #muloffset equals 2
                    data_element.Data[2] = data_element.Data[0]
                    data_element.Data[0] = 0x00
                    data_element.Data[1] = 0x00
                else:                                                           #else condition
                    data_element.Data[3] = data_element.Data[0]
                    temp = data_element.Data[2]
                    data_element.Data[2] = data_element.Data[1]
                    data_element.Data[1] = temp
                    data_element.Data[0] = 0x00

                uvalue_second = valueofbit(data_element)
                uvalue = uvalue_first | uvalue_second
        startbit,endbit = lib_constants.HWAPI_STARTBIT, lib_constants.HWAPI_ENDBIT
        mask = (1 << (int(endbit) - int(startbit) + 1)) - 1
        finalresult = (int(uvalue) >> int(startbit)) & mask                     #final result after masking the startbit and endbit
        library.write_log(lib_constants.LOG_INFO,
        "INFO: MMIO read 8 bit data successfully for input %s %s = %s"
        %(pciaddress,offset,(hex(finalresult).strip('L'))),
         test_case_id, script_id, "None","None", loglevel, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured"
            " in read_mmio_specific() function due to %s"%e,test_case_id,
                          script_id,loglevel, tbd)
        return False
################################################################################
# Function Name : valueofbit
# Parameters    : ualue
# Functionality : This code return value
# Return Value :  False
################################################################################
def valueofbit(data_element):
    uvalue = (data_element.Data[3] << 24) + (data_element.Data[2]<< 16)\
             + (data_element.Data[1] << 8) + data_element.Data[0]               # to put data into 32 format using shifting
    return uvalue
################################################################################
# Function Name : valid_data_range
# Parameters    : name of parameter,low bit, high bit, bittype
# Functionality : This code will check the input value is in given range
# Return Value :  True/False
################################################################################
def valid_data_range(bit,high,low,bittype,test_case_id, script_id,
                     loglevel="ALL", tbd="None"):
    if(int(bit)>high or int(bit)<low ):                                         #if startbit is more than 31 and less than 0 return string false
        library.write_log(lib_constants.LOG_INFO,
        "INFO: %s should be in range %s and %s"%(bittype,low,high),test_case_id,
                          script_id,"None","None", loglevel, tbd)
        utils.write_to_Resultfile("FAIL",script_id)
        return False
################################################################################
# Function Name : HWAPIerror
# Parameters    : None
# Functionality : This code return False if conditions met
# Return Value :  False
################################################################################
def HWAPIerror(result, test_case_id, script_id, loglevel="ALL", tbd="None"):
    if (result != BasicStructs.eUserErrorCode["eNoError"]):                     #Error code to handle hwapi exception
        library.write_log(lib_constants.LOG_INFO,"INFO:MMIO call returned"
            " error",test_case_id,script_id, "None","None", loglevel, tbd)
        utils.write_to_Resultfile("FAIL",script_id)
        return False
################################################################################
