__author__ = "kapilshx"

###########################General Imports######################################
import os
import platform
import string
import sys
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_tool_installation
################################################################################
# Function Name : smbios_table_type
# Parameters    : smbios_smbios_token,testcaseid, scriptid, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : Reading values from SMBIOS table which are in HEX format and
#                 either convert them to Binary or write output in HEX format
#                 to results file.
################################################################################

def smbios_table_type(smbios_token,log_file_smibos_path,test_case_id, script_id,
                               loglevel = "ALL", tbd="None"):
    try:
        convertbinary = False                                                   #flag for binary conversion
        nextrow = False
        qworddata = []                                                          #to store the hex or binary data
        smbios_token = smbios_token.upper()
        smbios_token = smbios_token.split(" ")                                  #to conert string to list
        if "BINARY" in smbios_token:                                            #to check "in binary format" is present in smbios_token
            tabletype,pos = library.extract_parameter_from_token(smbios_token,
                                                    "TYPE","IN",loglevel,tbd)
            convertbinary = True                                                #set flag convertbinary to True
        else:
            tabletype,pos = library.extract_parameter_from_token(smbios_token,
                                                    "TYPE","",loglevel,tbd)
        smbios_fp = open(log_file_smibos_path,'r')                              #to open (.rw) file in read mode
        smbios_fp_lines = smbios_fp.readlines()
        for index,item in enumerate(smbios_fp_lines):                           #loop to get the index of required hex data from log_file_smibos_path file
            if "Index" in str(item) :
                index_start = index
            elif "Undefined Value" in str(item):
                index_end = index
            else:
                pass
        row_smbios = []
        length = index_end - index_start
        for i in range(length-1):                                               #loop to all hex data to append into the finaltable
            finaltable = (((smbios_fp_lines[index_start+1].split(":")[1]).\
                           split("*")[0]).strip()).replace("-"," ")
            row_smbios.append(finaltable.split(" "))
            index_start+=1
        if 'TO' == smbios_token[3].upper() :                                    # if smbios_token[3] is equals to "to"
            data_start_bit = ' '.join(str(smbios_token[2])).split(" ")
            data_end_bit = ' '.join(str(smbios_token[4])).split(" ")
        elif 'TO' == smbios_token[4].upper():                                   # if smbios_token[4] is equals to "to"
            data_start_bit = ' '.join(str(smbios_token[3])).split(" ")
            data_end_bit = ' '.join(str(smbios_token[5])).split(" ")
        else:
            if 'BYTE' == smbios_token[1].upper() :                              # if "Byte" is present in the smbios_token
                data = ' '.join(str(smbios_token[2])).split(" ")                #convert list to string
                finaldata = []
                if 3 == len(data):                                              # if length of data is equals to 3
                    finaldata = row_smbios[int(data[0])][int(data[1])]
                    library.write_log(lib_constants.LOG_INFO,"INFO: Table type "
                    "%s data %s is %s"%(tabletype,str(smbios_token[2]),finaldata),
                            test_case_id,script_id,"None","None",loglevel,tbd)  #write info msg to log
                    finaldata = finaldata.split()
                    return finaldata
                else:
                    library.write_log(lib_constants.LOG_FAIL,"FAIL: Values to"
                        " check in table is wrong ",test_case_id,script_id,"None",
                                      "None",loglevel,tbd)                      #write info msg to log
                    return False
        smbios_list = ['A','B','C','D','E','F']
        for i in range(2):
            if str(data_start_bit[i].upper()) in smbios_list:
                newval=int((data_start_bit[i].upper()),16)
                data_start_bit =\
        [word.replace(data_start_bit[i],str(newval)) for word in data_start_bit]
            else:
                pass
        for i in range(2):
            if str(data_end_bit[i].upper()) in smbios_list:
                newval=int((data_end_bit[i].upper()),16)
                data_end_bit = \
            [word.replace(data_end_bit[i],str(newval)) for word in data_end_bit]
            else:
                pass
        if int(data_end_bit[0]) == (int(data_start_bit[0]))+1:                  # if bit range is more like - 0Ah to 18h then next row to set to 1
            nextrow = True
        else:
            pass
        if str(smbios_token[1]).isdigit():                                      # if smbios_token[1] is digit and smbios_token[2] is equals to 'byte' or 'word' or 'dword' or 'qword'
            if  'BYTE' == smbios_token[2].upper():
                rangevar = int(smbios_token[1])
            elif 'WORD' == smbios_token[2].upper():
                rangevar = 2 * int(smbios_token[1])
            elif  'DWORD' == smbios_token[2].upper():
                rangevar = 4 * int(smbios_token[1])
            elif 'QWORD' == smbios_token[2].upper():
                rangevar = 8 * int(smbios_token[1])
            else:
                library.write_log(lib_constants.LOG_FAIL,"FAIL: Invalid "
                    "grammar syntax ",test_case_id,script_id,"None","None",
                                  loglevel,tbd)                                 #write info msg to log
                return False
            if True == nextrow :                                                #if bit range is more like  - 0Ah to 18h then next row to set to 1
                finaldata1 = \
                    row_smbios[int(data_start_bit[0])][int(data_start_bit[1]):]
                for i in range(int(data_end_bit[1])+1):                         #loop to append all hew data in the given bit range
                    finaldata1.append(row_smbios[int(data_end_bit[0])][i])
                qworddata.extend(finaldata1)
            else:                                                               #if bit range is less like -  0Ah to 0Fh then next row to set to 0
                if (int(data_end_bit[1])-int(data_start_bit[1])) == rangevar-1:
                    finaldata1 = \
row_smbios[int(data_start_bit[0])][int(data_start_bit[1]):int(data_end_bit[1])+1]
                    qworddata.extend(finaldata1)                                #loop to extend all hew data in the given bit range
                else:
                    library.write_log(lib_constants.LOG_FAIL,"FAIL: wrong"
                        " difference in range for type WORD in grammar ",
                        test_case_id,script_id,"None","None",loglevel,tbd)      #write info msg to log
                    return False
            return convert_binary_smbios(convertbinary,qworddata,
                    smbios_token,tabletype,script_id,test_case_id,
                                         loglevel,tbd)                          #library call to function convert_binary_smbios to convert bit from hex to binary format
        elif 'WORD' == smbios_token[1].upper():
            bit_range = 2
            return bit_range_smbios(bit_range,row_smbios,data_start_bit,
                    data_end_bit,convertbinary,qworddata,smbios_token,tabletype,
                          script_id,test_case_id,loglevel,tbd)
        elif 'DWORD' == smbios_token[1].upper():
            bit_range = 4
            return bit_range_smbios(bit_range,row_smbios,data_start_bit,
                    data_end_bit,convertbinary,qworddata,smbios_token,tabletype,
                          script_id,test_case_id,loglevel,tbd)
        elif 'QWORD' == smbios_token[1].upper():
            bit_range = 8
            return bit_range_smbios(bit_range,row_smbios,data_start_bit,
                data_end_bit,convertbinary,qworddata,smbios_token,tabletype,
                        script_id,test_case_id,loglevel,tbd)
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL: Check the "
                "grammar syntax, ex: word,dword,qword,byte",test_case_id,
                        script_id,"None","None",loglevel,tbd)                   #write fail msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
            "smbios_table_type function to %s"%e,test_case_id,script_id,
                          "None","None",loglevel,tbd)                           #write error msg to log
        return False
################################################################################
# Function Name : convert_binary_smbios
# Parameters    : convertbinary,qworddata,smbios_token,tabletype,
#                 testcaseid, scriptid, loglevel and tbd
# Return Value  : qwordstring on success, qworddata on failure
# Functionality : To convert hex velues in to binary format
################################################################################
def convert_binary_smbios(convertbinary,qworddata,smbios_token,tabletype,
                          script_id,test_case_id,loglevel = "ALL",tbd= "None"):
    try:
        qwordstring = []
        if True == convertbinary:                                               #if convertbinary flag is set to True
            for i in range (len(qworddata)):                                    #loop to convert hex data to binary format
                binary = bin(int(qworddata[i], 16))[2:]
                binary = binary.zfill(lib_constants.EIGHT)
                qwordstring.append(binary)
            if str(smbios_token[1]).isdigit():
                library.write_log(lib_constants.LOG_INFO,"INFO: Table"
                            " type %s data from %s to %s is"
    " %s"%(tabletype,str(smbios_token[3]),str(smbios_token[5]),str(qwordstring)),
                            test_case_id,script_id,"None","None",loglevel,tbd)  #write info msg to log
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO:Table type %s data "
    "from %s to %s is %s"%(tabletype,str(smbios_token[2]),str(smbios_token[4]),
                           str(qwordstring)), test_case_id, script_id,"None",
                                  "None",loglevel,tbd)                          #write info msg to log
            return qwordstring                                                  #retun the qwordstring
        else:
            if str(smbios_token[1]).isdigit():
                library.write_log(lib_constants.LOG_INFO,"INFO: Table"
                    " type %s data from %s to %s is "
    "%s"%(tabletype,str(smbios_token[3]),str(smbios_token[5]),str(qwordstring)),
                              test_case_id,script_id,"None","None",loglevel,tbd)#write info msg to log
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO:Table type %s data "
                    "from %s to %s is"
    " %s"%(tabletype,str(smbios_token[2]),str(smbios_token[4]),str(qworddata)),
                            test_case_id, script_id,"None","None",loglevel,tbd) #write info msg to log
            return qworddata                                                    #retun the qworddata
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
            "convert_binary_smbios library function to %s"%e,test_case_id,
                          script_id,"None","None",loglevel,tbd)                 #write error msg to log
        return False
################################################################################
# Function Name : bit_range_smbios
# Parameters    : bit_range,qworddata,smbios_token,tabletype,
#                 testcaseid, scriptid, loglevel and tbd
# Return Value  : qwordstring or qworddata on success, False on failure
# Functionality : To parse bit value from given bit range in 2D matrix
################################################################################
def bit_range_smbios(bit_range,row_smbios,data_start_bit,data_end_bit,
                     convertbinary,qworddata,smbios_token,tabletype,
                          script_id,test_case_id,loglevel = "ALL",tbd= "None"):
    try:
        if (bit_range-1 == (int(data_end_bit[1])-int(data_start_bit[1]))):
            for i in range(bit_range):
                finaldata_end = \
                row_smbios[int(data_start_bit[0])][int(data_start_bit[1])+i]
                qworddata.append(finaldata_end)
            return convert_binary_smbios(convertbinary,qworddata,
                smbios_token,tabletype,script_id,test_case_id,loglevel,tbd)
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL: Incorrect "
                "difference in range or length of range is not 3 for "
                "type WORD in grammar",test_case_id,script_id,"None",
                              "None",loglevel,tbd)                              #write info msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
            "convert_binary_smbios library function to %s"%e,test_case_id,
                          script_id,"None","None",loglevel,tbd)                 #write error msg to log
        return False
################################################################################