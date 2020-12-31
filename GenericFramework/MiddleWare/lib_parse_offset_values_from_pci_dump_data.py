############################General library imports#############################
import os
import codecs
############################Local library imports###############################
import lib_constants
import library
import utils
################################################################################
# Function Name     : parse_offset_values_from_pci_dump_data
# Parameters        : token, test_case_id, script_id, log_level, tbd
# Functionality     : to read the offsey value from PCI dump data
# Return Value      : returns True, offset value on successful action and
#                     False otherwise
################################################################################

# Local variables
DEVICE = "Device"
INVALID = "Invalid"
READ_MODE = 'r'
h = 'h'
H = "'h"
OX = '0x'
ASTERISK = "*"
HYPHEN = "-"
S_COLON = ":"


def parse_offset_values_from_pci_dump_data(token, test_case_id, script_id,
                                           log_level, tbd):                     # Function to read offset value from PCI dump data

    global extracted_step
    token = token.upper()                                                       # convert to upper case
    source = token.split("FROM")                                                # split string token with "FROM"
    extracted_operation = source[0].strip()
    extracted_source = source[1].strip()                                        # store the 2nd element in source which is the source
    offset_value = extracted_source.split(" ")[-1]

    if "CONFIG-" in extracted_source:                                           # to bypass operation on config related syntax
        pass
    else:
        extracted_source_nospace = extracted_source.split(" ")
        extracted_step = extracted_source_nospace[1]                            # extract step number from extracted source

    if "CONFIG-" in source[1]:
        pcidump_path = utils.configtagvariable(extracted_source)                # extract file_path from config file
    else:
        pcidump_path = utils.read_from_Resultfile(extracted_step)               # extract file path from config file

    if "FAIL" == pcidump_path.upper():                                          # if previous step is failing then this code will return False and exit
        library.write_log(lib_constants.LOG_ERROR,
                          "Unable to get PCI dump path from %s"
                          % pcidump_path, test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False
    else:
        library.write_log(lib_constants.LOG_INFO,
                          "PCI Dump path is  : %s " % pcidump_path,
                          test_case_id, script_id, "None", "None",
                          log_level,  tbd)

        if OX in offset_value:
            offset_value = offset_value.strip(OX)
        elif "H" in offset_value:
            offset_value = offset_value.strip("H")
        else:
            offset_value = offset_value

        library.write_log(lib_constants.LOG_INFO,
                          "Getting the %s offset from PCI dump at %s"
                          % (pcidump_path, offset_value),
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)

        offset_list = []
        if os.path.isfile(pcidump_path) and os.path.getsize(
                pcidump_path) > lib_constants.ZERO:
            with codecs.open(pcidump_path, READ_MODE, encoding='utf16')\
                    as reader:                                                  # get read handler using utf-8 encoding
                for line in reader:
                    if "" != line and S_COLON in line and DEVICE not in \
                            line and INVALID not in line:
                        line = line.split(S_COLON)[1].split(ASTERISK)[0].strip()# strip all the unwanted strings and symbols
                        offset_val_first_8_bit, offset_val_second_8_bit = \
                            line.strip().split(HYPHEN)
                        offset_list.extend(offset_val_first_8_bit.split(" "))   # add each line 1st 8-bit to list
                        offset_list.extend(offset_val_second_8_bit.split(" "))  # add each line 2nd 8-bit to list
            library.write_log(lib_constants.LOG_INFO,
                              "The PCI dump is processed successfully",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_ERROR,
                              "PCI dump path from result file either don't "
                              "exist or has no data",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # if result.ini file doesn't contain valid file then else block will be executed
            return False

        try:
            offset_val = offset_list[int(offset_value, 16)]                     # read required offset value
            library.write_log(lib_constants.LOG_INFO, "PCI read value for "
                              "offset '%s' is '%s'" % (offset_value,
                                                       offset_val),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True, str(offset_val) + "'h"                                 # return offset value
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,
                              "Unable to get offset value due to %s" % str(e),  # if offset id is more than 255 then exception will be thrown
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False                                                        # return False if exception found
