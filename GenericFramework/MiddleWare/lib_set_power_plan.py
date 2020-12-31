__author__ = r"asharanx/tnaidux"

# General Python Imports
import os
import subprocess
import time

# Local Python Imports
import lib_constants
import library

################################################################################
# Function Name : update_power_option_all
# Parameters    : test_case_id, script_id, pwrsettingname, mysetting,
#                 powersource, log_level, tbd
# Functionality : Updates the power option settings in both AC and DC Source
# Return Value  : True on successful action, False otherwise
################################################################################


def update_power_option_all(test_case_id, script_id, pwrsettingname, mysetting,
                            powersource, log_level="ALL", tbd=None):

    try:
        if "SLEEP AFTER" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.POWER_SETTING_CONSTANT_MAX):   # These are the settings for all the power options available along with the source
            guid, subuid, pwr_setting = get_guid("Sleep", "Sleep after")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):   # This will apply the settings in the power option
                return True
            else:
                return False

        elif "HIBERNATE AFTER" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.POWER_SETTING_CONSTANT_MAX):   # Same is repeated through out with ilif conditions for all the possible entries
            guid, subuid, pwr_setting = get_guid("Sleep", "Hibernate after")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "DIM DISPLAY AFTER" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.POWER_SETTING_CONSTANT_MAX):
            guid, subuid, pwr_setting = get_guid("Display",
                                                 "Dim display after")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "TURN OFF THE DISPLAY" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.POWER_SETTING_CONSTANT_MAX):
            guid, subuid, pwr_setting = get_guid("Display",
                                                 "Turn off display after")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "DISPLAY BRIGHTNESS" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Display",
                                                 "Display brightness")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "DIMMED DISPLAY BRIGHTNESS" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Display",
                                                 "Dimmed display brightness")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "LOW BATTERY LEVEL" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting)<= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Low battery level")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "CRITICAL BATTERY LEVEL" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting)<=lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Critical battery level")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "RESERVE BATTERY LEVEL" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Reserve battery level")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "MINIMUM PROCESSOR STATE" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Processor power management",
                                                 "Minimum processor state")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "MAXIMUM PROCESSOR STATE" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_MAX):
            guid, subuid, pwr_setting = get_guid("Processor power management",
                                                 "Maximum processor state")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "CRITICAL BATTERY ACTION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_THIRD_LEVEL):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Critical battery action")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "LOW BATTERY NOTIFICATION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_FIRST_LEVEL):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Low battery notification")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "LOW BATTERY ACTION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_THIRD_LEVEL):
            guid, subuid, pwr_setting = get_guid("Battery",
                                                 "Low battery action")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "LID CLOSE ACTION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_THIRD_LEVEL):
            guid, subuid, pwr_setting = get_guid("Power buttons and lid",
                                                 "Lid close action")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "POWER BUTTON ACTION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_THIRD_LEVEL):
            guid, subuid, pwr_setting = get_guid("Power buttons and lid",
                                                 "Power button action")

            if apply_with_settings(test_case_id, script_id, guid, subuid,
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False

        elif "SLEEP BUTTON ACTION" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_THIRD_LEVEL):
            guid, subuid, pwr_setting = get_guid("Power buttons and lid",
                                                 "Sleep button action")
            
            if apply_with_settings(test_case_id, script_id, guid, subuid, 
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False
        
        elif "START MENU POWER BUTTON" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_SECOND_LEVEL):
            guid, subuid, pwr_setting = get_guid("Power buttons and lid", 
                                                 "Start menu power button")
            
            if apply_with_settings(test_case_id, script_id, guid, subuid, 
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False
        
        elif "ALLOW HYBRID SLEEP" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_FIRST_LEVEL):
            guid, subuid, pwr_setting = get_guid("Sleep", "Allow hybrid sleep")
            
            if apply_with_settings(test_case_id, script_id, guid, subuid, 
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False
        
        elif "ALLOW WAKE TIMERS" == pwrsettingname and \
                (int(mysetting) >= lib_constants.PWR_SET_MIN) and \
                (int(mysetting) <= lib_constants.PWR_SET_FIRST_LEVEL):
            guid, subuid, pwr_setting = get_guid("Sleep", "Allow wake timers")
            
            if apply_with_settings(test_case_id, script_id, guid, subuid, 
                                   pwr_setting, int(mysetting), powersource):
                return True
            else:
                return False
        
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Due to "
                              "option is not available in the list of "
                              "powersettings or power setting option is not "
                              "handled", test_case_id, script_id, "None", 
                              "None", log_level,tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, 
                          test_case_id, script_id, "None", "None", log_level, 
                          tbd)
        return False

################################################################################
# Function Name : apply_with_settings()
# Parameters    : test_case_id, script_id, guid, subgrp_UID, pwr_setting, 
#                 mysetting, powersource, log_level, tbd
# Functionality : Updates the power option settings in both AC and DC Source
# Return Value  : True/False
################################################################################


def apply_with_settings(test_case_id, script_id, guid, subgrp_UID, pwr_setting, 
                        mysetting, powersource, log_level="ALL", tbd=None):

    apply_data_inhex = hex(mysetting)

    cmd_setacvalue = "powercfg.exe /SETACVALUEINDEX " + guid + " " + \
        subgrp_UID + " " + pwr_setting + " " + str(mysetting)

    cmd_setdcvalue = "powercfg.exe /SETDCVALUEINDEX " + guid + " " + \
        subgrp_UID + " " + pwr_setting + " " + str(mysetting)

    ac_dc_output = 1
    powersource = powersource.upper()

    try:
        os.chdir(lib_constants.SYSTEM_PATH)
        if 'AC' == powersource.upper():
            ac_dc_output = subprocess.Popen(cmd_setacvalue, shell=False,
                                            stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdout=subprocess.PIPE)
            ac_dc_output.communicate()

            if not ac_dc_output.returncode:
                time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
                return True
            else:
                return False
        elif 'DC' == powersource.upper():
            ac_dc_output = subprocess.Popen(cmd_setdcvalue, shell=False,
                                            stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdout=subprocess.PIPE)
            ac_dc_output.communicate()
            if not ac_dc_output.returncode:
                time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
                return True
            else:
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Power "
                              "source AC or DC is not specified in the syntax "
                              "Provide proper input", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : get_guid()
# Parameters    : subgrp, pwr_setting, tc_id, script_id, log_level, tbd
# Functionality : gets the GUID of the power options to be set in AC and DC
# Return Value  : True/False
################################################################################


def get_guid(subgrp, pwr_setting, tc_id=None, script_id=None, log_level="ALL",
             tbd=None):

    try:
        os.chdir(lib_constants.SYSTEM_PATH)
        cmd = "powercfg.exe q > powercfg_log.txt"                               # Command to execute powercfg to read and save the power option entries

        Proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True,
                                stdin=subprocess.PIPE)
        Proc.communicate()
        output = Proc.returncode

        with open("powercfg_log.txt", 'r') as log:                              # Opens the file and searches if the "power scheme" string is available and fetches the option question id of it
            for lines in log:
                line = lines
                if "Power Scheme GUID:" in lines:
                    guid = lines.split('Power Scheme GUID' ':')[1].\
                        strip().split()[0]
                    break
            log.close()

        with open("powercfg_log.txt", 'r') as log:                              # Opens the file and searches if the "subgroup guid:" string is available and fetches the option question id of it
            for lines in log:
                if 'Subgroup GUID:' in lines:
                    if subgrp in lines:
                        subgrp_UID = lines.split('Subgroup GUID:')[1].strip()
            log.close()

        with open("powercfg_log.txt", 'r') as log:                              # Opens the file and searches if the "power setting" string is available and fetches the option question id of it
            for lines in log:
                if pwr_setting in lines:
                    pwr_setting_UID = lines.split('Power Setting GUID:')[1].\
                        strip().split()[0]
                    break

            return guid, subgrp_UID.split()[0], pwr_setting_UID
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
