__author__ = r'pkolla\tnaidux'

# General Python Imports
import sys
from ssa import hwapi
from ssa import BasicStructs

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : Hexaconv
# Parameters    : None
# Functionality : This code will convert given input into Hexadecimal and
#                 remove last char
# Return Value  : Hexadecimal value in the 0x format
################################################################################


def Hexaconv(bin_pciaddress):

    try:
        pciaddress = int(bin_pciaddress,2)                                      # Convert to integer
        pciaddress = hex(pciaddress)                                            # Reconvert to hexadecimal
        return pciaddress
    except Exception as e:
        return e


################################################################################
# Function Name : valid_data_range
# Parameters    : name of parameter,low bit, high bit, bittype
# Functionality : This code will check the input value is in given range
# Return Value  : True/False
################################################################################


def valid_data_range(bit, high, low, bittype, test_case_id, script_id,
                     log_level, tbd):

    try:
        if (int(bit) > high) or (int(bit) < low):                               # If startbit is more than 31 and less than 0 return string false
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s should "
                              "be in range %s and %s" % (bittype, low, high),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        return e

################################################################################
# Function Name : HWAPIerror
# Parameters    : None
# Functionality : This code return False if conditions met
# Return Value :  False
################################################################################


def HWAPIerror(result, test_case_id, script_id, log_level, tbd):

    try:
        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: MMIO call "
                              "returned error", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        return e

################################################################################
# Function Name : valueofbit
# Parameters    : ualue
# Functionality : This code return value
# Return Value :  False
################################################################################


def valueofbit(data_element):
    try:
        uvalue = (data_element.Data[3] << 24) + (data_element.Data[2] << 16) + \
            (data_element.Data[1] << 8) + data_element.Data[0]
        return uvalue
    except Exception as e:
        return e

################################################################################
# Function Name : read_mmio
# Parameters    : original_string, test_case_id, script_id, log_level, tbd
# Functionality : This code will read the MMIO offset using hw api and return
#                 value in result
# Return Value :  result value/false
################################################################################


def read_mmio(pciaddress, offset, startbit, endbit, data_value, test_case_id,
              script_id, log_level="ALL", tbd="None"):

    try:
        if "STEP" in pciaddress.upper():                                        # If step in token
            stepno = pciaddress.split(" ")[-1]
            bin_pciaddress = utils.read_from_Resultfile(int(stepno)).upper()    # Read from result file

            if "'B" in bin_pciaddress:                                          # If B in binary output
                bin_pciaddress = bin_pciaddress.replace("'B", "")               # Remove B
                pciaddress = Hexaconv(bin_pciaddress)
            elif "'H" in bin_pciaddress.upper():                                # If H in binary output
                bin_pciaddress = bin_pciaddress.upper().replace("'H", "")       # Remove H
                pciaddress = bin_pciaddress
            else:
                pciaddress = bin_pciaddress

        if offset.endswith('H') or offset.endswith('h'):
            offset = offset[:-1]

        if pciaddress.endswith('H') or pciaddress.endswith('h'):
            pciaddress = pciaddress[:-1]

        hw = hwapi.HWAPI()                                                      # Hwapi call
        result = hw.HWAPIInitialize()                                           # Initialise the hwapi

        if pciaddress.startswith('0x') and pciaddress.endswith('h'):            # Trunkate based on input
            pciaddress = pciaddress[:-1]                                        # Remove the last element from pci address

        if pciaddress.endswith('h'):
            pciaddress = '0x' + pciaddress[:-1]                                 # Prefix 0x if pciaddress ends with h and remove h

        if "CONFIG" in data_value:                                             # Check if it is a config var and retrieve its value from config.ini
            (config, section, key) = data_value.split("-")
            data_value = str(utils.ReadConfig(section, key))
            if "FAIL" in data_value:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Config Entry under %s"
                                  " is not updated" % section,
                                  test_case_id,
                                  script_id, "None", "None", log_level,
                                  tbd)                                          # Writing log warning message to the log file
                hw.HWAPITerminate()
                return False

        if "'b" in data_value:
            data_value = data_value.replace("'b", "")
            data_value = int(data_value, 2)
        elif "'B" in data_value:
            data_value = data_value.replace("'B", "")
            data_value = int(data_value, 2)
        elif "'h" in data_value or "0x" in data_value or "0X" in data_value:
            data_value = data_value.replace("'h", "")
            data_value = int(data_value, 16)
        elif "'d" in data_value:
            data_value = int(round(float(data_value.replace("'d", ""))))
        else:
            try:
                data_value = int(round(float(data_value)))
            except:
                data_value = data_value

        bitvalid = False

        if startbit and endbit:
            bitvalid = True

        data_len = 32

        valid_data_range(startbit, 31, 0, 'Startbit', test_case_id, script_id,
                         log_level, tbd)
        valid_data_range(endbit, 31, 0, 'Endbit', test_case_id, script_id,
                         log_level, tbd)

        if (int(endbit) > 31) or (int(endbit) < 0):                             # If endbit is more than 31 and less than 0 return string false
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Endbit "
                              "should be in range 0 and 31", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            hw.HWAPITerminate()
            return False

        if int(startbit) > int(endbit):                                         # If startbit is less than endbit return string false
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Startbit "
                              "should be less than Endbit", test_case_id,
                              script_id, "None","None", log_level, tbd)
            hw.HWAPITerminate()
            return False

        bit = int(offset, 16)
        valid_data_range(bit, 255, 0, 'Offset', test_case_id, script_id,
                         log_level, tbd)

        data_element = BasicStructs.DataElementFactory(data_len)                # Get data element from basicstructs dataelementfactory function
        data_element.Size = data_len
        muloffset = int(offset, 16) % 4                                         # Converting to integer and getting the extra bits that will remain after converting to byte checking offset is multiple of 4

        if 0 == muloffset:                                                      # If its multiple of 4 just call pciread of hwapi and interpret data
            result = hw.PCIMMIORead(int(pciaddress, 16), int(offset, 16),
                                    data_element)                               # Store PCIMMIORead call function return value in result
            uvalue = valueofbit(data_element)
            HWAPIerror(result, test_case_id, script_id, log_level, tbd)
        else:                                                                   # If its not multiple of 4 do appropitate masking of data consider width of 32 bit and we have to read the two offsets and merge
            offset = int(offset, 16) - muloffset                                # Converting from hexadecimal to integer and then substracting the muloffset
            result = hw.PCIMMIORead(int(pciaddress, 16), int(str(offset), 16),
                                    data_element)
            HWAPIerror(result, test_case_id, script_id, log_level, tbd)

            if 1 == muloffset:
                data_element.Data[0] = data_element.Data[1]                     # When muloffset is 1 put defa
                data_element.Data[1] = data_element.Data[2]
                data_element.Data[2] = data_element.Data[3]
                data_element.Data[3] = 0x00
            elif 2 == muloffset:
                data_element.Data[0] = data_element.Data[2]                     # Muloffset is 2
                data_element.Data[1] = data_element.Data[3]
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00
            else:
                data_element.Data[0] = data_element.Data[3]                     # Muloffset is 0
                data_element.Data[1] = 0x00
                data_element.Data[2] = 0x00
                data_element.Data[3] = 0x00

            uvalue1 = valueofbit(data_element)
            offset += 4                                                         # Increment offset by 4

            result = hw.PCIMMIORead(int(pciaddress, 16), int(str(offset), 16),
                                    data_element)
            HWAPIerror(result, test_case_id, script_id, log_level, tbd)

            if 1 == muloffset:                                                  # Muloffset equals 1
                data_element.Data[3] = data_element.Data[0]
                data_element.Data[0] = 0x00
                data_element.Data[1] = 0x00
                data_element.Data[2] = 0x00
            elif 2 == muloffset:
                data_element.Data[3] = data_element.Data[1]                     # Muloffset equals 2
                data_element.Data[2] = data_element.Data[0]
                data_element.Data[0] = 0x00
                data_element.Data[1] = 0x00
            else:
                data_element.Data[3] = data_element.Data[0]
                temp = data_element.Data[2]
                data_element.Data[2] = data_element.Data[1]
                data_element.Data[1] = temp
                data_element.Data[0] = 0x00

            uvalue2 = valueofbit(data_element)
            uvalue = uvalue1 | uvalue2

        library.write_log(lib_constants.LOG_INFO, "INFO: MMIO call data." +
                          "0x" + hex(uvalue)[2:].strip('L'), test_case_id,
                          script_id, "None", "None", log_level, tbd)

        if bitvalid:
            if startbit == endbit:                                            # If startbit is same as endbit
                mask = (1 << int(startbit))
                finalresult = (int(uvalue) & mask) >> int(startbit)
            else:
                mask = (1 << (int(endbit) - int(startbit) + 1)) - 1
                finalresult = (int(uvalue) >> int(startbit)) & mask

            library.write_log(lib_constants.LOG_INFO, "INFO: MMIO final data "
                              "with start and endbit." +
                              hex(finalresult).strip('L'), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            result = hex(finalresult)[2:].strip('L') + "'h"
        else:
            result = hex(uvalue)[2:].strip('L') + "'h"

        if data_value != "None":
            if data_value == finalresult:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: MMIO final data %s is equals to "
                                  "given data %s." % (finalresult, data_value),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                hw.HWAPITerminate()
                return result
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: MMIO final data %s"
                                  "with start and endbit is not matching with "
                                  "the given data %s"
                                  % (hex(finalresult).strip('L'), data_value),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                hw.HWAPITerminate()
                return False
        else:
            hw.HWAPITerminate()
            return result
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        hw.HWAPITerminate()
        return False
