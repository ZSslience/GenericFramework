__author__ = 'kvex'

############################General Python Imports##############################
import random
############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_calculate_number

################################################################################
# Function Name : generate_random_number
# Parameters    : tc_id;script_id;range_start;range_end;log_level;tbd
# Functionality : generates a random number in the given range
# Return Value  : returns the random value [INCLUDING ZERO] or False
################################################################################

                                                                                #this function returns 'false' on failure as 0 is a valid return and it may create conflict
def generate_random_number(tc_id, script_id, range_start, range_end,
                           log_level="ALL", tbd=None):
    try:
        start_range = utils.parse_variable(range_start, tc_id, script_id)
        end_range = utils.parse_variable(range_end, tc_id, script_id)
        if not start_range or not end_range:
            return False                                                        # invalid input value
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Generating random "
                              "number between " + start_range + " and " +
                              end_range, tc_id, script_id, "None", "None",
                              log_level, tbd)                                   #valid inputs, so continue
        start_range = \
            lib_calculate_number.number_conversion(start_range.upper())
        end_range = \
            lib_calculate_number.number_conversion(end_range.upper())
        if int(end_range) > int(start_range):                                   #range can be in the reverse order also (first number is greater)
            random_number = random.randint(int(start_range), int(end_range))
            return random_number
        else:
            random_number = random.randint(int(end_range), int(start_range))
            return random_number

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)     # Any exception in ttk operation are handled here and logged
        return False

