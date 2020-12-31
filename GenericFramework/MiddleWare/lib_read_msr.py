__author__ = r'bisweswx\tnaidux\mmakhmox'

# Global python Imports
import time

# Local Python Imports
import library
import lib_constants
from ssa import hwapi
from ssa import BasicStructs

################################################################################
# Function Name : read_msr
# Parameters    : core, address, start bit, end bit, test_case_id,script_id
# Functionality : Return the binary value for the bit/bit ranges using HWAPI()
#                 for the input offset and bit positions
# Return Value  : Binary bits
################################################################################


def read_msr(core, address, start_bit, end_bit, test_case_id, script_id,
             log_level="ALL", tbd=None):

    if core == "None":
        Core = int(lib_constants.ZERO)                                          # Default value for core is 0
    else:
        Core = int(core)

    if 'H' in address:
        address = address.strip('H')                                            # Strip the 'H' from the input Hex address
    elif '0X' in address:
        address = address.split('0X')[1]                                        # Strip t#he '0X' from the input Hex address
    else:
        pass

    dec_val = int(address, 16)                                                  # Hex value is converted to decimal to be passed to HWAPI()
    time.sleep(lib_constants.TEN_SECONDS)
    hw = hwapi.HWAPI()                                                          # Initialization of HWAPI()
    hw.HWAPIInitialize()
    msrInfo = BasicStructs.MSRInfoBlock()                                       # Invoking MSR Read
    msrInfo.msr = dec_val                                                       # Input of MSR address in decimal and number of cores default to 0

    if Core == 0:
        msrInfo.cpu = 0                                                         # CPU number is 0 by default
    else:
        msrInfo.cpu = Core

    result = hw.ReadMSR(msrInfo)                                                # Reading MSR

    if result != BasicStructs.eUserErrorCode["eNoError"]:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: PCIRead "
                          "returned error code", test_case_id, script_id,
                          "HWAPI", "None", log_level, tbd)
        hw.HWAPITerminate()
        return False
    else:
        hi_bin = "{:032b}".format(msrInfo.hiContent)[::-1]                      # Converting higher/lower order bits to 32 bit format and
        lo_bin = "{:032b}".format(msrInfo.loContent)[::-1]                      # Reversing the bit order to extract bits

        if 63 == int(start_bit) and 0 == int(end_bit):                          # Read all bits if no bits/bitrange selected
            str = hi_bin[::-1] + lo_bin[::-1]                                   # Return all 64bits in binary
            hw.HWAPITerminate()
            return str

        elif start_bit == end_bit:                                              # When only single bit to be read
            bit = int(start_bit)
            if (bit >= 0) and (bit <= 31):
                hw.HWAPITerminate()
                return lo_bin[bit]                                              # Returning lower bit if bit is <31
            elif (bit >= 32) and (bit <= 63):
                bit = (bit-32)                                                  # Reading the bits from higher order byte
                hw.HWAPITerminate()
                return hi_bin[bit]                                              # Returning higher bit if bit position is >31 and <63
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid"
                                  " bit positions, Please enter values in "
                                  "range[63:0]", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                hw.HWAPITerminate()
                return False
        else:
            if int(start_bit) >= 32 and int(end_bit) >= 32:
                temp_end_bit = end_bit
                end_bit = int(start_bit)                                        # Since the byte order is already reversed
                start_bit = int(temp_end_bit)
                start_bit = (start_bit - 32)
                end_bit = (end_bit - 32)
                hw.HWAPITerminate()
                return hi_bin[start_bit:end_bit + 1][::-1]                      # Return binary bits for higher order bytes by reversing the order
            elif int(start_bit) > 31 or int(end_bit) > 31:
                str = hi_bin[::-1] + lo_bin[::-1]                               # Return all 64bits in binary
                hw.HWAPITerminate()
                return str
            else:
                if int(start_bit) > int(end_bit):
                    temp = start_bit
                    start_bit = end_bit
                    end_bit = temp
                    start_bit = int(start_bit)
                    end_bit = int(end_bit) + 1
                    hw.HWAPITerminate()
                    return lo_bin[start_bit:end_bit][::-1]
                else:
                    start_bit = int(start_bit)
                    end_bit = int(end_bit) + 1
                    hw.HWAPITerminate()
                    return lo_bin[start_bit:end_bit][::-1]                      # Return binary bits for lower order bytes by reversing the order
