__author__ = 'kvex'

############################General Python Imports##############################
import os
import wmi
import string
import subprocess
############################Local Python Imports################################
import library
import lib_constants

################################################################################
# Function Name : get_power_mode
# Parameters    : tc_id;script_id;loglevel,tbd
# Functionality : checks system power mode and returns
# Return Value  : returns the power mode as AC, DC or AC+DC
################################################################################

def get_power_mode(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        Proc = subprocess.Popen("wmic path win32_Battery get BatteryStatus "
                "/Format:List", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE) #using subprocess and wmic query to get the power mode
        power_mode = Proc.communicate()[0]                                      #assings the raw data output of the wmic command

                                                                                #based on the return value, decide power mode
        if "" in power_mode and not "BatteryStatus" in power_mode:              #BatteryStatus=Value has defined values as per wmic
            mode = "AC"                                                         #based on those values decide the power mode
            library.write_log(lib_constants.LOG_INFO, "INFO: Power mode "
            "has been identified as %s"%mode, tc_id, script_id, "None", "None",
            log_level, tbd)

        elif "BatteryStatus=1" in power_mode or "BatteryStatus=4" in \
            power_mode or "BatteryStatus=5" in power_mode:
            mode = "DC"
            library.write_log(lib_constants.LOG_INFO, "INFO: Power mode "
            "has been identified as %s"%mode, tc_id, script_id, "None", "None",
            log_level, tbd)

        elif "BatteryStatus=2" in power_mode or "BatteryStatus=6" in \
            power_mode or "BatteryStatus=7" in power_mode or \
            "BatteryStatus=8" in power_mode or "BatteryStatus=9" in \
            power_mode:
            proc = subprocess.Popen("wmic path win32_Battery",
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE)#using subprocess and wmic query to get the battery charge
            charge = proc.communicate()[0]                                      #assings the raw data output of the wmic command
            if "Battery 0" in charge:                                           #if this string is present, no battery is connected
                mode = "AC"
            else:
                mode = "AC+DC"
            library.write_log(lib_constants.LOG_INFO, "INFO: Power mode "
            "has been identified as %s"%mode, tc_id, script_id, "None", "None",
            log_level, tbd)

        else:
            mode = False
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
            " power mode information using WMIC query", tc_id, script_id,
            "None", "None", log_level, tbd)

        return mode

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in getting"
        " power mode information from OS", tc_id, script_id, "None", "None",
                          log_level, tbd)
        return False