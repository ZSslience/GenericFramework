__author__ = 'nareshgx / Sharadth'
############################General Python Imports##############################
import os
import string
import sys
############################Local Python Imports################################
import library
import lib_constants
import utils
import re
import lib_conversion_of_numerical_format
################################################################################
# Function Name : read_binary_output
# Parameters    : tc_id, script_id, token, log_level="ALL", tbd=None
# Return Value  : binary bit value or None
# Purpose       : To Read the value of bit[<num>:<num>] from step <num>
# Target        : SUT
# Syntax        : Read the value of bit[<num>:<num>] from step <num>
################################################################################

def read_binary_output(tc_id, script_id, token, log_level="ALL", tbd=None):
    start_bit = ""
    end_bit = ""
    step = ""
    binary_bit= []
    match = re.search(r"(bit|bits).(\d+):(\d+).*?from.*?(\d+)", token)          # get step and offset value using regex
    if match != None:                                                           # check for param numbers if 3
        group,start_bit, end_bit, step = list(match.groups())
        start_bit = int(start_bit)
        step = int(step)
        end_bit = int(end_bit)
    else:
        match = re.search(r"(bit|bits).(\d+).*?from.*?(\d+)", token)            # check for param number if 2
        group,start_bit, step = list(match.groups())
        start_bit = int(start_bit)
        step = int(step)
    b_val = utils.read_from_Resultfile(step)                                    # get step from result.ini file using read_from_resultfile library
    if "C:\\Automation\\scripts\\" in b_val:
        file = b_val.split("//")[-1]
        with open(file,"r") as f:
            b_val = f.readlines()[0]
            b_val = b_val.strip()
    if "h" in b_val or "0x" in b_val:
        offset_bin_value = lib_conversion_of_numerical_format.\
            hexa_to_binary(b_val)                                               # convert hex to binary using lib
        offset_bin_value = offset_bin_value.replace("b", '').replace("'","")
        offset_bin_value = offset_bin_value.zfill(64)
    elif 'b' in b_val:
        b_val = b_val.replace("b", '').replace("'","")
        offset_bin_value = b_val.zfill(64)                                      # Fill binary output to 64bit
    offset_bin_value = (offset_bin_value[::-1])
    if start_bit != "" and end_bit != "" and len(offset_bin_value) >= start_bit:# if all required values are non zero
        if start_bit > end_bit:                                                 # check for bit order if higher to lower then this block will be executed
            while(end_bit <= start_bit):
                if end_bit == start_bit:                                        # check for endbit required and break
                    binary_bit.append(offset_bin_value[end_bit])
                    break
                else:
                    binary_bit.append(offset_bin_value[end_bit])
                    end_bit = end_bit + 1                                       # if still bits are presnt to fetch then continue
            binary_bit = binary_bit[::-1]                                       # reverse the bit array
            binary_bit = "".join(binary_bit)                                    # join to get the output as sting
            return binary_bit+"'b"
        elif start_bit < end_bit:                                               # if bit order is lower to higher then this block will be executed
            while(end_bit >= start_bit):
                if start_bit == end_bit:                                        # check for endbit required and break
                    binary_bit.append(offset_bin_value[start_bit])
                    break
                else:
                    binary_bit.append(offset_bin_value[start_bit])
                    start_bit = start_bit+1
            binary_bit = "".join(binary_bit)
            return binary_bit+"'b"
        else:
            return None
    elif start_bit != "" and len(offset_bin_value) >= start_bit:                # if only one bit is required then executed this block
            binary_bit = offset_bin_value[start_bit]
            return binary_bit+"'b"
    else:
        binary_bit = None
        library.write_log(lib_constants.LOG_INFO,"INFO: Required bit no. "
                                                 "is out of offset Value"       # if offset doesn't contain required bit then result will be fail
            ,tc_id,script_id,"None","None",log_level, tbd)
        return None
