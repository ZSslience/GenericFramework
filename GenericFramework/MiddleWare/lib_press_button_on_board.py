__author__ = 'bisweswx'

# General Python Imports
import time
from subprocess import Popen, PIPE

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : press_button
# Parameters    : On board button name, duration to press, test case id,
#                 script id
# Functionality : Read the relay number from config file based on the input
#                 button name, if button name not there in config or it has a
#                 entry as 'NC',the script will exit as fail
# Return Value  : True/False
################################################################################


def press_button(times, button, duration, test_case_id, script_id,
                 loglevel="ALL", tbd="None"):

    try:
        relay = utils.ReadConfig("TTK", button)                                 # Read Relay details for the button name

        if "FAIL:" in relay:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry missing for relay", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return False
        elif "NC" != relay:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s button rework "
                              "is connected to Relay number %s in TTK"
                              % (button, relay), test_case_id, script_id,
                              "None", "None", loglevel, tbd)                    # if config entry has 'NC' as the entry means the particular
        else:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: %s button "
                              "rework not connected to TTK relay" % button,
                              test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Config entry not "
                          "found for %s" % button, test_case_id, script_id,
                          "Config.ini", str(e), loglevel, tbd)                  # If config entry is not present, exception will be handled here
        return False

    try:
        import lib_ttk2_operations
        press_delay = 30
        result = lib_ttk2_operations.\
            press_release_button(int(duration), int(times), int(relay),
                                 int(press_delay), test_case_id, script_id,
                                 loglevel, tbd)
        if result is True:
            return result
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                          "performing TTK action", test_case_id, script_id,
                          "TTK", str(e), loglevel, tbd)                         # Any ttk exception is handled here
        return False


def press_power_button_presi(test_case_id, script_id, loglevel="ALL",
                             tbd="None"):

    try:
        cmd = lib_constants.TOOLPATH + "\\simicscmd.exe power-button-press"
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Pressing "
                              "power button fails using simics", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return False
        else:
            time.sleep(lib_constants.TWO)
            library.write_log(lib_constants.LOG_INFO, "INFO: Pressed power "
                              "button using simics cmd", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False
