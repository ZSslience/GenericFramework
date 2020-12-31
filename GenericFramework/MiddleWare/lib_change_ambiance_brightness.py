__author__ = 'jiten/patnaikx\sushil3x'
############################General Python Imports##############################
import os
import subprocess
import time
import shutil
import csv
#########################Local Imports #########################################
import utils
import library
import lib_constants
import lib_sensorviewer
################################################################################
# Function Name     : change_ambiance_brightness
# Parameters        : test_case_id, script_id, device, loglevel, tbd
# Functionality     : function to get current Brightness level
# Return Value      : Brightness level(if pass), False(if fail)
################################################################################

def change_ambiance_brightness(sensor_name, tc_id, script_id, log_level='All',
                               tbd='None'):
    try:
        tool = "SENSORVIEWER"
        val = lib_sensorviewer.get_sensor_val(sensor_name, tc_id, script_id,
                                              tool, log_level, tbd)
        if val is False:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: ALS sensor level[lux] value not"
                              "captured with USB light OFF %s " % val, tc_id,
                              script_id, tool, "None", log_level, tbd)          #ALS sensor level[lux] value captured with USB light OFF

            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: ALS sensor level[lux] value  "
                              "captured with USB light OFF %s " % val, tc_id,
                              script_id, tool, "None", log_level, tbd)

        log = lib_constants.SCRIPTDIR +"\\" + sensor_name + ".txt"
        with open(log, "w") as _f:
            _f.writelines(sensor_name + " = " + val)
            _f.close()
        return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due to:"
                          " %s " % e, tc_id, script_id, "None", log_level, tbd)
        return False


################################################################################
# Function Name : handle_relay_ambiance
# Parameters    : On board button name,action,test case id,script id
# Functionality : Read the relay number from config file based on the input
#                 button name, if button name not there in config or it has a
#                 entry as 'NC',the script will exit as fail
# Return Value :  True/False
################################################################################

def handle_relay_ambiance(button,action, test_case_id, script_id,
                 log_level="ALL", tbd="None"):
    try:
        relay = utils.ReadConfig("TTK",button)                                  #Read Relay details for the button name
        if "FAIL:" in relay:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
                              " missing for relay", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        elif "NC" != relay:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s button rework"
                              " is connected to Relay number %s in TTK"
                              % (button,relay), test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #if config entry has 'NC' as the entry means the particular
        else:                                                                   #rework is not connected,script will exit here
            library.write_log(lib_constants.LOG_WARNING, "WARNING : %s button "
                              "rework not connected to TTK relay" % button,
                              test_case_id, script_id, "None", "None", 
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "ERROR: Config entry not found for %s"%button,
                          test_case_id,script_id, "Config.ini", str(e),
                          log_level, tbd)                                       #If config entry is not present, exception will be handled here
        return False

    try:
        if "ON" == action :
            ret = library.ttk_set_relay(action,int(relay), test_case_id,
                                        script_id, log_level, tbd)

        elif "OFF" == action :
            ret = library.ttk_set_relay(action,int(relay), test_case_id,
                                        script_id, log_level, tbd)
        else:
            ret = 1

        if 1 == ret :
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Relay Handle Failure",
                              test_case_id,script_id,"None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Relay Handle Success",
                              test_case_id,script_id,"None",
                              "None",log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "ERROR: Config entry not found for %s "% button,
                          test_case_id, script_id, "Config.ini", str(e),
                          log_level, tbd)                                       #If config entry is not present, exception will be handled here
        return False

################################################################################
# Function Name     : compare_ambiance
# Parameters        : logfile1, logfile2, status, test_case_id, script_id,
#                       log_level, tbd
# Functionality     : function to compare ambiance
# Return Value      : True(if pass), False(if fail)
################################################################################
def compare_ambiance(sensor_name,tc_id,script_id, log_level='All',tbd='None'):
    try:
        tool = "SENSORVIEWER"
        val2 = lib_sensorviewer.get_sensor_val(sensor_name, tc_id, script_id,
                                               tool, log_level, tbd)
        if val2 is False:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: ALS sensor "
                              "level[lux] value not captured with USB light ON"
                              " %s " % val2, tc_id, script_id, tool, "None",
                              log_level, tbd)                                   #ALS sensor level[lux] value captured with USB light OFF

            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: ALS sensor "
                              "level[lux] value captured with USB light ON %s "
                              % val2, tc_id, script_id, tool, "None", log_level,
                              tbd)

        log = lib_constants.SCRIPTDIR + "\\" + sensor_name + ".txt"

        with open(log, "r") as _f:
            lines = _f.readlines()
            for line in lines:
                if sensor_name in line:
                    val1 = line.split("=")[1].strip()


            if float(val1) < float(val2):
                library.write_log(lib_constants.LOG_INFO, "INFO: ALS sensor "
                                  "level[lux] is increase with USB light ON",
                                  tc_id, script_id, tool, "None",log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: ALS "
                                  "sensor level[lux] is Decrease with USB light "
                                  "ON", tc_id, script_id, tool, "None",
                                  log_level, tbd)
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Config entry not "
                          "found for %s", tc_id, script_id, "Config.ini", str(e),
                          log_level, tbd)                                        #If config entry is not present, exception will be handled here
        return False
################################################################################