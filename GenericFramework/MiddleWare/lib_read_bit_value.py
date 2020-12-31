__author__ = 'kvex'

# Local Python Imports
import lib_constants
import library
import utils

################################################################################
# Function Name : read_bit_value
# Parameters    : test_case_id, script_id,
#                 token[can be any hexa value or step n], bit, log_level, tbd
# Functionality : checks n th bit of hexa value given as input
# Return Value  : returns the nth value on reading from input or 'false'
################################################################################


def read_bit_value(test_case_id, script_id, token, bit, log_level="ALL",
                   tbd=None):

    try:
        if "STEP" in token.upper():                                             # Input param is step. read from step result
            before_keyword, keyword, step = token.partition("STEP ")            # Get the step number
            hexa_value = utils.read_from_Resultfile(step)                       # Get the value from result file
        else:
            hexa_value = token
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In getting "
                          "hexa value from result file provided as: %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

    try:                                                                        # Convert hexa to binary
        if "'h" in  hexa_value.lower():
            hexa_value = hexa_value.split("'")[0]
        elif "H" == hexa_value[-1] or "h" == hexa_value[-1]:                    # If h in value, remove it
            hexa_value = hexa_value[0:-1]
        elif "x" in hexa_value[1] or "X" in hexa_value[1]:
            pass
        elif 'h' or 'd' or 'x' not in hexa_value.lower():
            hexa_value = hexa_value
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: The given hexa "
                              "value %s is not valid" % hexa_value,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        if hexa_value.endswith("b"):
            masked_binary = hexa_value.split("'")[0]
        else:
            binary_string = bin(int(hexa_value, 16))
            masked_binary = binary_string[2:].zfill(64)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: The given hexa "
                          "value %s is not valid" % hexa_value, test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return False

    try:                                                                        # Fetch the nth bit and return
        message = "INFO: Binary equivalent of given hexa input " + \
                str(hexa_value) + " is " + str(masked_binary)

        library.write_log(lib_constants.LOG_INFO, message, test_case_id,
                          script_id, "None", "None", log_level, tbd)
        if ":" in bit:
            start_bit = bit.split(":")[0]
            end_bit = bit.split(":")[1]
            masked_binary = masked_binary[::-1]
            return masked_binary[int(end_bit): (int(start_bit)+1)]
        else:
            return masked_binary[-(int(bit)+1)]
    except:
        if "index out of range" in str(e):
            library.write_log(lib_constants.LOG_WARNING, "WARNINGO: The given "
                              "hexa value doesn't have bit %s" % bit,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Warning in"
                              " validating hexa value input", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
