__author__ = r'kvex\tnaidux'

# General Python Imports
import time

# Local Python Imports
import lib_constants
import library
import utils

################################################################################
# Function Name     : pause_execution
# Parameters        : token, test_case_id, script_id, log_level, tbd
# Functionality     : will pause the execution as per the input time
# Return Value      : returns True on successful pause and False otherwise
################################################################################


def pause_execution(token, test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        if "STEP " in token:                                                    # Extract step number from grammar
            before_keyword1, keyword1, after_keyword1 = \
                token.partition("STEP ")
            before_keyword2, keyword2, after_keyword2 = \
                after_keyword1.partition(" SECONDS")
            wait_timex = utils.read_from_Resultfile(before_keyword2)

            try:
                wait_time = int(wait_timex)                                     # If exception occurs on converting given time to int, its not valid
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        elif "CONFIG-" in token:                                                # If time need to be taken from token, read time from time config
            before_keyword1, keyword1, after_keyword1 = \
                token.partition("CONFIG-")
            before_keyword2, keyword2, after_keyword2 = \
                after_keyword1.partition(" SECONDS")
            tag, key, variable = before_keyword2.partition("-")
            wait_timex = utils.ReadConfig(tag, variable)

            try:
                wait_time = int(wait_timex)                                     # If exception occurs on converting given time to int, its not valid
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        else:
            before_keyword1, keyword1, after_keyword1 = \
                token.partition(" SECONDS")
            before_keyword2, keyword2, after_keyword2 = \
                before_keyword1.partition("FOR ")

            try:                                                                # Token is time to pause and it should be integer
                wait_time = int(after_keyword2)
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

        library.write_log(lib_constants.LOG_INFO, "INFO: Execution will be "
                          "paused for %s seconds" % wait_time, test_case_id,
                          script_id, "None", "None", log_level, tbd)
        time.sleep(wait_time)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False