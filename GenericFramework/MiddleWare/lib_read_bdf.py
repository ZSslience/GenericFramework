__author__ = r'pkolla/selvax'

# General Python Imports
import io
import os
import shutil
import sys
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_run_command
from ssa import hwapi
from ssa import BasicStructs

################################################################################
# Function Name : valid_hex_data
# Parameters    : Hexadecimal value
# Functionality : This code will convert Hexadecimal input in 0x format
# Return Value  : Hexadecimal value in the 0x format
################################################################################


def valid_hex_data(value):
    
    try:
        if value.startswith('0x') and value.endswith('h'):                      # Truncate based on input of bus,device and function
            value = value[:-1]
        elif value.endswith('h'):                                               # If value endswith h, add 0x to the prefix
            value = '0x' + value[:-1]
        elif value.startswith('0x'):
            value = value
        else:                                                                   # If value doesn't endswith h and doesn't start with 0x, add 0x to the prefix
            value = '0x' + value
        
        return value
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, 
                          "None", "None", "None", "None", "None", "None")
        return False

################################################################################
# Function Name : valid_data_range
# Parameters    : name, value, test_case_id, script id, log_level,tbd
#                 log_level,tbd
# Functionality : This code will check the input value is in range of 0 to 31
# Return Value  : True/False
################################################################################


def valid_data_range(name, value, test_case_id, script_id, log_level="ALL",
                     tbd=None):

    try:
        if int(value, 16) > 31 or int(value, 16) < 0:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s should "
                              "be in range of 0 and 31" % name, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : read bdf
# Parameters    : busnum, devicenum, functionnum, offset, startbit, enfbit,
#                 test_case_id, script id, log_level, tbd
# Functionality : This code will read the BDF offset using hw api and return
#                 value in result
# Return Value  : result value/false
################################################################################


def readbdf(token, test_case_id, script_id, log_level="ALL", tbd="None"):

    try:
        busnum, devicenum, functionnum, offset, startbit, endbit = \
            '', '', '', '', '', ''                                              # Initializing the variables with empty string

        if "wos" in token.lower():
            token = ((token.lower()).split("in")[0]).strip()

        tokenlist = token.lower().split()                                       # Converting ostr to list
        token_length = len(tokenlist)
        busnum = tokenlist[5]                                                   # Extracting the busnum,devicenum,functionnum,offset,startbit,endbit from tokenlist
        devicenum = tokenlist[7]
        functionnum = tokenlist[9]
        offset = tokenlist[11]
        bitvalid = "true"

        if 12 == token_length:
            startbit, endbit = "0", "31"
            bitvalid = "false"                                                  # This flag indicates to read the full
        elif 'bit' in token:                                                    # If only bit is specified e.g 1A0h [32]
            startbit, endbit = tokenlist[14].split(":")[0],\
                               tokenlist[14].split(":")[0]
        elif 'range' in token:                                                  # If only bit is specified e.g 1A0h [32]
            startbit, endbit = tokenlist[14].split(":")[0],\
                               tokenlist[14].split(":")[1]

        elif token_length > 15:                                                 # If bit ranges is specified e.g 1A0h [32:30]
            startbit, endbit = tokenlist[14].split(":")[1],\
                               tokenlist[14].split(":")[0]
        else:
            return False

        hw = hwapi.HWAPI()                                                      # Initialize HWAPI
        result = hw.HWAPIInitialize()
        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: PCIRead"
                              "returned error code", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        busnum = valid_hex_data(busnum)                                         # Bus number converted to 0xformat
        devicenum = valid_hex_data(devicenum)                                   # Device number converted to 0xformat
        functionnum = valid_hex_data(functionnum)                               # Function number converted to 0xformat
        offset = valid_hex_data(offset)                                         # Offset converted to 0xformat

        if valid_data_range("BUS", busnum, test_case_id, script_id, log_level,
                            tbd) and \
           valid_data_range("DEVICE", devicenum, test_case_id, script_id,
                            log_level, tbd) and \
           valid_data_range("FUNCTION", functionnum, test_case_id, script_id,
                            log_level, tbd):
            pass
        else:
            return False

        if int(startbit) not in list(range(0,32)) or \
           int(endbit) not in list(range(0,32)) or int(startbit) > int(endbit):
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Given Bit "
                              "value should be in range of 0 and 31 and endbit "
                              "should be greater than startbit", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        if int(offset, 16) > 255 or int(offset, 16) < 0:                        # If offset is not between 0 and 255
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Offset "
                              "value should be in range of 0 and 255",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        data_len = 32                                                           # Initialized to 32 but make sure modify /input this value as part of grammar if your range is out than 256 bytes
        pciaddress = BasicStructs.PCIConfAddr(int(busnum, 16),
                                              int(devicenum, 16),
                                              int(functionnum, 16), 0)

        data_element = BasicStructs.DataElementFactory(data_len)
        data_element.Size = data_len
        muloffset = int(offset, 16) % 4                                         # Get the remainder of the muloffset after dividing it with 4 which are the extra bits, checking offset is multiple of 4

        if 0 == muloffset:
            offset = int(offset, 16)                                            # If its multiple of 4 just call pciread of hwapi and interpret data
            result = hw.PCIRead(pciaddress, offset, data_element)               # Do a pciread with address offset and data element
            uvalue = (data_element.Data[3] << 24) + \
                (data_element.Data[2] << 16) + (data_element.Data[1] << 8) + \
                data_element.Data[0]

            if result != BasicStructs.eUserErrorCode["eNoError"]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: BDF "
                                  "call returned error", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:                                                                   # If its not multiple of 4 do appropitate masking of data consider width of 32 bit and we have to read the two offsets and merge
            offset = int(offset, 16) - muloffset                                # Get offset after substracting the muloffset
            result = hw.PCIRead(pciaddress, offset, data_element)               # Do a pciread with pciadress offset and dataelement

            if result != BasicStructs.eUserErrorCode["eNoError"]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: BDF "
                                  "call returned error", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            if 1 == muloffset:                                                  # Muloffset is 1 then store 0 in the last bit
                data_element.Data[0] = data_element.Data[1]
                data_element.Data[1] = data_element.Data[2]
                data_element.Data[2] = data_element.Data[3]
                data_element.Data[3] = 0x00
            elif 2 == muloffset:                                                # Muloffset is 2 then 0 in last two bit
                data_element.Data[0] = data_element.Data[2]
                data_element.Data[1] = data_element.Data[3]
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00
            else:                                                               # Else store 0 in last three bits
                data_element.Data[0] = data_element.Data[3]
                data_element.Data[1] = 0x00
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00

            uvalue1 = (data_element.Data[3] << 24) + \
                (data_element.Data[2] << 16) + (data_element.Data[1] << 8) + \
                data_element.Data[0]

            offset += 4                                                         # Increment offset  by 4
            result = hw.PCIRead(pciaddress, offset, data_element)

            if result != BasicStructs.eUserErrorCode["eNoError"]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: BDF "
                                  "call returned error", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            if 1 == muloffset:                                                  # If muloffset is 1 store 0 in last 3 bits
                data_element.Data[3] = data_element.Data[0]
                data_element.Data[0] = 0x00
                data_element.Data[1] = 0x00
                data_element.Data[2] = 0x00
            elif 2 == muloffset:                                                # If muloffset is 2 store 0 in last 2 bits
                data_element.Data[3] = data_element.Data[1]
                data_element.Data[2] = data_element.Data[0]
                data_element.Data[0] = 0x00
                data_element.Data[1] = 0x00
            else:                                                               # Else store 0 in lst bit
                data_element.Data[3] = data_element.Data[0]
                temp = data_element.Data[2]
                data_element.Data[2] = data_element.Data[1]
                data_element.Data[1] = temp
                data_element.Data[0] = 0x00

            uvalue2 = (data_element.Data[3] << 24) + \
                (data_element.Data[2] << 16) + (data_element.Data[1] << 8) + \
                data_element.Data[0]
            uvalue = uvalue1|uvalue2

        if "true" == bitvalid:                                                  # If bitvalid is true
            if startbit == endbit:
                mask = 1 << int(startbit)                                       # Leftshift 1 bit for endbit
                finalresult = ((int(uvalue) & mask)) >> int(startbit)
            else:
                mask = (1 << (int(endbit) - int(startbit) + 1)) - 1             # Calculate the mask by left shift 1 from the difference of startbit and endbit+1 and then substract 1 from the result
                finalresult = (int(uvalue) >> int(startbit)) & mask

            hex_result = "0x" + hex(finalresult)[2:].strip('L').upper()

            library.write_log(lib_constants.LOG_INFO, "INFO: The BDF value "
                              "for BUS: %s DEVICE: %s FUNCTION: %s OFFSET: %s "
                              "bits [%s: %s] is %s"
                              % (str(busnum), str(devicenum), str(functionnum),
                                 str(offset), str(endbit), str(startbit),
                                 str(hex_result)), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            utils.write_to_Resultfile(hex(finalresult)[2:].strip('L') + "'h",
                                      script_id)
            return "True"
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: The BDF value "
                              "for BUS: %s DEVICE: %s FUNCTION: %s OFFSET: %s "
                              "is %s" % (str(busnum), str(devicenum),
                                         str(functionnum), str(offset),
                                         str('0x' + hex(uvalue)[2:].strip('L'))
                                         .upper()), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            utils.write_to_Resultfile(hex(uvalue)[2:].strip('L') + "'h",
                                      script_id)
            return "True"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : create_nsh_file
# Parameters    : token, test_case_id, script_id, log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : To create startup.nsh file
################################################################################


def create_nsh_file(token, test_case_id, script_id, log_level="ALL",
                    tbd=None):                                                  # Function to generate .nsh fle

    try:
        bdf_values = token.split()
        bus = bdf_values[2].split('x')[1]
        device = bdf_values[3].split('x')[1]
        function = bdf_values[4].split('x')[1]

        read_bdf_cmd = "pci " + bus + " " + device + " " + function + \
            " > BDF_log.txt"                                                    # Command to run in efishell to get ec register value

        f = open("startup.nsh", 'w')                                            # Creating .nsh file
        f.write("bcfg boot mv 01 00" + '\n')
        f.write('fs0:' + '\n')
        f.write(read_bdf_cmd + '\n')
        f.write("reset")
        f.close()                                                               # File closing after writing to file
        nsh1_size = os.path.getsize("startup.nsh")

        if '0' == nsh1_size:                                                    # Check for startup nsh file sizes and return false if size is 0
            library.write_log(lib_constants.LOG_WARNING, "WARNING: .nsh file "
                              "is not generated properly", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: .nsh file is "
                              "successfully created", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : create_sdrive_copy_files
# Parameters    : token,test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : create S drive and To copy necessary tool and files to S drive
################################################################################


def create_sdrive_copy_files(token, test_case_id, script_id, log_level="ALL",
                             tbd="None"):                                       # Function to create the logical drive and copy the files and tool to s drive

    try:
        gensdrive_create = \
            lib_run_command.create_logical_drive('S', test_case_id, script_id,
                                                 log_level, tbd)                # Function to create logical drive

        if gensdrive_create is True:
            library.write_log(lib_constants.LOG_INFO, "INFO: Logical Drive is "
                              "created", test_case_id, script_id, "None",
                              "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "create logical s drive unable create",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        result = create_nsh_file(token, test_case_id, script_id, log_level, tbd)

        if result:
            cwd = lib_constants.SCRIPTDIR                                       # Script dir path
            os.chdir(cwd)

            if os.path.exists('S:\\'):                                          # Check for new logical drive path existance
                if os.path.exists("S:\BDF_log.txt"):                            # Delete the old log file if already exists
                    os.remove("S:\BDF_log.txt")

                if os.path.exists("S:\startup.nsh"):
                    os.remove("S:\startup.nsh")                                 # Delete the startup file if already exists

                time.sleep(lib_constants.FIVE_SECONDS)                          # Sleep for 5 seconds
                shutil.copy("startup.nsh", "S:\\\\")                            # Copy startup nsh to current working directory

                if os.path.exists(cwd + "\subscript.nsh"):
                    time.sleep(lib_constants.FIVE_SECONDS)                      # Sleep for 5 seconds
                    shutil.copy("subscript.nsh", "S:\\\\")

            library.write_log(lib_constants.LOG_INFO, "INFO: files copied to "
                              "S drive successfully", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: files "
                              "didn't copied to S drive", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : read_bdf_register
# Parameters    : token, test_case_id, script_id, log_level, tbd
# Return Value  : Return register offset & value on success and False on failure
# Functionality : mount the s drive and read ec date from the log
################################################################################


def read_bdf_value(token, test_case_id, script_id, log_level="ALL",
                   tbd="None"):                                                 # Function to read the ec value from the log

    try:
        offset = token.split(" ")[5].split("x")[1]
        line_offset = "000000" + offset[0] + "0"

        try:
            value_offset = int(offset[1], 16)
        except:
            value_offset = int(offset[1])

        gensdrive_create = lib_run_command. \
            create_logical_drive('S', test_case_id, script_id, log_level, tbd)  # Function to create logical drive

        if gensdrive_create is True:
            library.write_log(lib_constants.LOG_INFO, "INFO: Logical Drive is "
                              "created", test_case_id, script_id, "None",
                              "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "create Logical Drive", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

    try:
        log_file = test_case_id + "-" + script_id.split("-")[3][0] + ".txt"

        if os.path.exists(log_file):
            os.remove(log_file)

        shutil.copy2("S:\BDF_log.txt", log_file)                                # Copy the log file from logical drive to script folder

        library.write_log(lib_constants.LOG_INFO, "INFO: log file found ",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)

        with io.open(log_file, "r", encoding='utf-16-le') as file:              # Parsing the log for register value
            for line in file:
                if line_offset in line:
                    line = line.strip()
                    if value_offset < 6:
                        bdf_reg_val = line.split(" ")[value_offset + 1]
                    elif value_offset > 8:
                        bdf_reg_val = line.split(" ")[value_offset]
                    elif value_offset == 7:
                        bdf_reg_val = \
                            line.split(" ")[value_offset + 1].split("-")[0]
                    elif value_offset == 8:
                        bdf_reg_val = \
                            line.split(" ")[value_offset].split("-")[1]

        int_val_reg = int(bdf_reg_val, 16)

        if "[" and "]" in token:                                                # If there is a range in token
            bit_range = token[token.index("[") + 1: token.index("]")]
            if 1 != len( bit_range):                                            # If the range is not a single bit read get the binry value in the range
                start_bit = bit_range[0]
                end_bit = bit_range[-1]
                bin_value = ""
                offt = "0x" + offset + " [" + start_bit + " : " + end_bit + "]"

                for bits in reversed(list(range(int(start_bit), int(end_bit) + 1))):
                    if 0 != int_val_reg & (1 << bits):
                        bin_value += "1"
                    else:
                        bin_value += "0"

                return offt, bin_value + "'b"
        else:                                                                   # If the range is a single bit read get the binary value of that bit
            try:
                bit = int(token.split(" ")[6])
                offt = "0x" + offset + " [" + str(bit) + "]"

                if 0 != int_val_reg & (1 << bit):
                    return offt, "1'b"
                else:
                    return offt, "0'b"
            except :
                offt = "0x" +offset
                return offt, bdf_reg_val + "'h"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
