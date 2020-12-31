__author__ = r'bisweswx\tnaidux'

# Global Python Imports
import time
import os

# Local Python Imports
import library
import utils
import lib_constants
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations

################################################################################
# Function Name : perform_g3
# Parameters    : test_case_id, script_id, log_level and tbd
# Functionality : This code will disconnect DC and then AC connected to the
#                 system using TTK
# Return Value :  True on successful action, False otherwise
################################################################################


def perform_g3(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        time.sleep(10)
        dc_signal_port = utils.ReadConfig("TTK", "dc_signal_port")
        dc_power_port = utils.ReadConfig("TTK", "dc_power_port")
        typec_power_port = utils.ReadConfig("TTK", "typec_power_port")

        if "FAIL:" in dc_signal_port or\
                "FAIL:" in  dc_power_port or\
                "FAIL:" in typec_power_port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entries for dc_signal_port or "
                              "dc_power_port or typec_power_port under [TTK] "
                              "from config file", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        result = lib_ttk2_operations.\
            perform_g3(dc_signal_port, dc_power_port, typec_power_port,
                       test_case_id, script_id, log_level, tbd)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: G3 performed "
                              "successfully", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "perform G3", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
