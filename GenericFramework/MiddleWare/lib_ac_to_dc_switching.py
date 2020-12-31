__author__ = "UST Automation Team"

# Global Python Imports
import time

# Local Python Imports
import lib_constants
import library
import lib_connect_disconnect_power_source

################################################################################
# Function Name : ac_to_dc_switch()
# Parameters    : test_case_id, script_id, log_level, tbd
# Functionality : This will switch from ac to dc mode
# Return Value  : True on successful action, False otherwise
################################################################################


def ac_to_dc_switch(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        if lib_connect_disconnect_power_source.\
                power_source_actions("TTK", "DC", "CONNECT", test_case_id,
                                     script_id, log_level, tbd):
            library.write_log(lib_constants.LOG_INFO, "INFO: DC Power turned "
                              "ON to SUT", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            time.sleep(30)
            if lib_connect_disconnect_power_source.\
                    power_source_actions("TTK", "AC", "DISCONNECT",
                                         test_case_id, script_id, log_level,
                                         tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: AC Power "
                                  "turned OFF to SUT", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                library.write_log(lib_constants.LOG_INFO, "INFO: Switching "
                                  "from AC to DC is successful", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to turn OFF AC using TTK", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "turn ON DC using TTK", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : dc_to_ac_switch()
# Parameters    : test_case_id, script_id, log_level, tbd
# Functionality : This will switch from dc to ac mode
# Return Value  : True on successful action, False otherwise
################################################################################


def dc_to_ac_switch(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        if lib_connect_disconnect_power_source.\
                power_source_actions("TTK", "AC", "CONNECT", test_case_id,
                                     script_id, log_level, tbd):
            library.write_log(lib_constants.LOG_INFO, "INFO: AC Power turned "
                              "ON to SUT", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            time.sleep(60)
            if lib_connect_disconnect_power_source.\
                    power_source_actions("TTK", "DC", "DISCONNECT",
                                         test_case_id, script_id, log_level,
                                         tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: DC Power "
                                  "turned OFF to SUT", test_case_id, script_id,
                                  "None", "None", log_level, tbd)

                library.write_log(lib_constants.LOG_INFO, "INFO: Switching "
                                  "from DC to AC is successful", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to turn OFF DC using TTK", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "turn ON AC using TTK", test_case_id, script_id,
                              "TTK", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : ac_to_dc_switch_presi()
# Parameters    : log_level
# Functionality : This will switch from dc to ac mode
# Return Value  : True/False
################################################################################

def ac_to_dc_switch_presi(test_case_id, script_id,log_level= "ALL",tbd=None):
    try:
        cmd = lib_constants.TOOLPATH + "\\simicscmd.exe detach-ac"
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_INFO, "INFO: Disconnect AC"
              "power source fails using simics cmd",test_case_id,script_id, "None",
                              "None",log_level, tbd)
            return False
        else:
            time.sleep(lib_constants.SHORT_TIME)
            library.write_log(lib_constants.LOG_INFO,"INFO: Disconnected AC power"
            " source using simics cmd",test_case_id,script_id,log_level,tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_INFO,"INFO: Exception in "
            "in disconnectig AC using simics cmd",test_case_id,
                          script_id,log_level,tbd)
        return False