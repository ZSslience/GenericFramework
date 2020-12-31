__author__ = 'nareshgx'
############################General Python Imports##############################
import os
############################Local Python Imports################################
import library
import utils
import lib_constants
import os.path
import codecs

################################################################################
# Function Name : lib_read_pci_offset
# Parameters    : Step , offset, token is string, TC_id is test case id,
#                   script_id is script number
# Return Value  : Offset value if success else return None in fail
# Purpose       : To read pci offset values
# Target        : SUT
# Syntax        : Parse PCI dump from step <num> log for offset <alp_num>
################################################################################
def lib_read_pci_offset(step, offset, tc_id, script_id, log_level, tbd):
    offset_list_value = []                                                      # empty offset value list declaration
    val_from_step = utils.read_from_Resultfile(int(step))                       # get step from result.ini file using read_from_resultfile library
    try:
        if os.path.isfile(val_from_step) and os.path.getsize(val_from_step) > 0:
            with codecs.open(val_from_step,'r',encoding='utf8') as reader:      # get read handler using utf-8 encoding
                for line in reader:
                    if "" != line and ":" in line and "Device" not in line and \
                                    "Invalid" not in line:
                        line = line.split(":")[1].split("*")[0].strip()         # strip all the unwanted strings and symbols
                        offset_val_first_8_bit,offset_val_second_8_bit = \
                            line.strip().split("-")
                        offset_list_value.extend(offset_val_first_8_bit.split
                                                 (" "))                         # add each line 1st 8-bit to list
                        offset_list_value.extend(offset_val_second_8_bit.split
                                                 (" "))                         # add each line 2nd 8-bit to list
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: No result file to"  # if result.ini file doesn't contain valid file then else block will be executed
                        " parse",tc_id,script_id,"None","None",log_level,tbd)
            return None                                                         #return None
        try:
            offset_val = offset_list_value[int(offset, 16)]                     # read required offset value
            library.write_log(lib_constants.LOG_INFO,"INFO: PCI read value for "
            "offset '%s' is '%s'"%(offset, offset_val),tc_id,script_id,
                              "None","None",log_level,tbd)
            return offset_val                                                   # return offset value
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"Error: Unable to Execute"# if offset id is more than 255 then exception will be thrown
            " due to invalid offset id.",tc_id,script_id,"None","None",
                              log_level, tbd)
            return None                                                         #return None if exception found
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"Error: Unable to Execute"    # if result.ini doesn't contain the valid file then exception
            "'%s'"%e,tc_id,script_id,"None","None",
                              log_level, tbd)
        return None                                                             #return None if exception found
