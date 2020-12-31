__author__ = r'singhd1x\tnaidux'

# General Python Imports
import re
from ssa import hwapi
from ssa import BasicStructs

# Local Python Imports
import lib_constants
import library
import utils

# Global Variables
global msr_step_value

################################################################################
# Function Name     : write_msr
# Parameters        : original_string, test_case_id, script_id, log_level, tbd
# Functionality     : write to msr
# Return Value      : returns True on successful action and False otherwise
################################################################################


def write_msr(original_string, test_case_id, script_id, log_level="All",
              tbd=None):

    try:
        token = original_string.split(" ")

        if "core" in original_string.lower():
            core_num = original_string.lower().split('core')[1].strip().\
                split(' ')[0].strip()
        else:
            core_num = "0"

        if "address" in original_string.lower():
            address = original_string.lower().split('address')[1].strip().\
                split(' ')[0].strip()

        if "bit" in original_string.lower():
            bit_range = original_string.lower().split('bit')[1].strip().\
                split(' ')[0].strip()
        elif "bits" in original_string.lower():
            bit_positions = original_string.lower().split('bits')[1].strip().\
                split(' ')[0].strip()
        elif "range" in original_string.lower():
            bit_range = original_string.lower().split('range')[1].strip().\
                split(' ')[0].strip()

        else:
            bit_range = "0:63"

        bit_value = str(original_string.split("=")[1]).strip()

        if any(re.findall(r'h|H', address, re.IGNORECASE)):                     # Strip the 'H' or 'h' from the input Hex address
            address = address.strip('h')
            address = address.strip('H')
        elif any(re.findall(r'0x|0X', address, re.IGNORECASE)):                 # Strip the '0X' or '0x' from the input Hex address
            address = address.strip('0x')
            address = address.strip('0X')
        else:
            pass

        dec_val = int(address, 16)                                              # Hex value is converted to decimal to be passed to HWAPI()
        hw = hwapi.HWAPI()                                                      # Initialization of HWAPI()
        hw.HWAPIInitialize()
        msrInfo = BasicStructs.MSRInfoBlock()                                   # Invoking MSR Read
        msrInfo.msr = dec_val                                                   # Input of MSR address in decimal and number of cores default to 0
        msrInfo.cpu = int(str(core_num))                                        # CPU number is core_no by default
        result = hw.ReadMSR(msrInfo)                                            # Reading MSR

        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "read MSR returned error code %d" % result,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            readmsrhi = "{:032b}".format(msrInfo.hiContent)[::-1]               # Converting higher/lower order bits to 32 bit format and
            readmsrlo = "{:032b}".format(msrInfo.loContent)[::-1]               # Reversing the bit order to extract bits

            library.write_log(lib_constants.LOG_INFO, "INFO: High bit and "
                              "low bit values read successfully", test_case_id,
                              script_id, "None", "None", log_level,tbd)

        range_of_bit = extractbitvalue(bit_range, test_case_id, script_id,
                                      log_level, tbd)
        library.write_log(lib_constants.LOG_INFO, "INFO: Extracted bit range "
                          "successfully", test_case_id, script_id, "None",
                          "None", log_level, tbd)

        writelo, writehi = writeindex(readmsrlo, readmsrhi, range_of_bit,
                                      bit_value, test_case_id, script_id,
                                      log_level, tbd)                           # Function calling Valuetobewrite to convert values to be write

        library.write_log(lib_constants.LOG_INFO, "INFO: Modified high bit "
                          "and low bit values successfully", test_case_id,
                          script_id, "None", "None", log_level, tbd)

        address = dec_val
        highcontent = writehi
        lowcontent = writelo
        msrInfo.msr = address                                                   # Setting the msr value
        msrInfo.cpu = int(core_num)                                             # Setting the cpu value
        msrInfo.hiContent = highcontent                                         # Setting the high value
        msrInfo.loContent = lowcontent                                          # Setting the low value
        result = hw.WriteMSR(msrInfo)

        if result != BasicStructs.eUserErrorCode["eNoError"]:
            library.write_log(lib_constants.LOG_INFO, "INFO: Write MSR "
                              "call returned error " + str(result),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Writing to MSR "
                              "is successful", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name     : extractbitvalue
# Parameters        : test_case_id, script_id, bit_range, loglevel, tbd
# Functionality     : Function will extract the bit value based on the input
# Return Value      : returns exception if fail
################################################################################


def extractbitvalue(bit_range, test_case_id, script_id, log_level="ALL",
                    tbd=None):

    try:
        emptylist = []                                                          # Defining empty list
        index = []                                                              # Defining empty list

        for bit in bit_range:                                                   # Extract Bit to get range
            emptylist.append(bit)

        if len(bit_range) <= 4:                                                 # Checking for bit range
            bit_range = bit_range
            if bit_range.isdigit():
                index.append(int(bit_range))
        else:
            bit_range = bit_range                                       # Checking entire range and separate comma and colon

            rangedump = bit_range.split(",")
            checkforcolon = ":"

            for value in rangedump:
                if checkforcolon in value:                                      # Check if the value contain clone
                    rangebit = value.split(":")
                    firstelement = int(rangebit[0])
                    endelement = int(rangebit[1])
                    loptemp = firstelement
                    for bitinterval in range(endelement, firstelement + 1):     # If colon then create index range
                        index.append(loptemp)
                        endelement += 1
                        loptemp -= 1
                else:
                    index.append(int(value))
        return index
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name  : writeindex
# Parameters     : readmsrlo, readmsrhi, index, bit_value, test_case_id,
#                  script_id, log_level, tbd
# Functionality  : Function to write the index to MSRLow and MSRHigh bit
#                  position
# Return Value   : returns exception if fail
################################################################################


def writeindex(readmsrlo, readmsrhi, index, bit_value, step_number,
               test_case_id, script_id, log_level="ALL", tbd=None):             # Function to write index value to the bit range

    try:
        if "," in bit_value:
            orignalbit = bit_value.split(",")                                   # Check for coma and then split
        else:
            orignalbit = bit_value

        if len(index) == len(orignalbit):                                       # Check for the range of original bit and index
            low = readmsrlo                                                     # Define low bit range and high bit range
            high = readmsrhi

            lowrange = library.stringtoindex(low, test_case_id, script_id,
                                             log_level, tbd)                    # Convert the bit range into index parameter

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "changed the lower range bit values to index "
                              "format", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            highrange = library.stringtoindex(high, test_case_id, script_id,
                                              log_level, tbd)                   # Convert the bit range into higher range parameter

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "changed the higher range bit values to index "
                              "format", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            lower_range_values = lib_constants.LOWER_RANGE.split(",")           # Getting lower range value from lib constant
            lower_range_low_value = int(lower_range_values[0])                  # Converting lower range bit into integer
            lower_range_high_value = int(lower_range_values[1])
            list_number_low = (list(range(lower_range_low_value,
                                     lower_range_high_value)))                   # Creating range list
            high_range_values = lib_constants.HIGH_RANGE.split(",")             # Getting high range value from lib constant
            higher_range_low_value = int(high_range_values[0])                  # Converting higher range bit into integer
            higher_range_high_value = int(high_range_values[1])
            list_number_hi = (list(range(higher_range_low_value,
                                    higher_range_high_value)))                   # Creating range list
            lower_bits = dict(list(zip(list_number_low,lowrange)))
            higher_bit = dict(list(zip(list_number_hi,highrange)))
            postion = 0

            for check in index:                                                 # Check for the index in bit range and change the value
                if check <= lib_constants.MSR_LOWBIT:                           # If it is less then "31" then it is lower range
                    lower_bits[check] = str(orignalbit[postion])
                    lowrange = list(lower_bits.values())
                else:
                    higher_bit[check] = str(orignalbit[postion])                # If it is more then "31" then it is consider as high range
                    highrange = list(higher_bit.values())
                postion += 1

            writetolow = library.Indextostring(reversed(lowrange),
                                               test_case_id, script_id,
                                               log_level, tbd)

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "changed the lower range index values to string "
                              "format", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            writetohigh = library.Indextostring(reversed(highrange),
                                                test_case_id, script_id,
                                                log_level, tbd)

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "changed the higher range index values to string "
                              "format", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            if "'b" in writetohigh:
                writetohigh = writetohigh.strip("'b")
            elif "'b" in writetolow:
                writetolow = writetolow.strip("'b")

            writetolow = int(writetolow, base=2)                                # Get the value of lower bit after changing the index value
            writetohigh = int(writetohigh, base=2)                              # Get the value of higher bit after changing the index value
            return writetolow, writetohigh
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, log_level, tbd)
        return False
