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
# Function Name : check_for_battery
# Parameters    : tc_id;script_id;loglevel,tbd
# Functionality : checks whether battery is connected or not
# Return Value  : returns True is battery is connected and False otherwise
################################################################################

def check_for_battery(tc_id, script_id, log_level="ALL", tbd=None):
    try:
        ProcC = subprocess.Popen("wmic path win32_Battery",
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)                         #using subprocess and wmic query to get the battery charge
        charge = ProcC.communicate()[0]                                         #assings the raw data output of the wmic command
        if "Battery 0" in str(charge):                                               #if this string is present, no battery is connected
            library.write_log(lib_constants.LOG_INFO, "INFO: Battery is not "
            "connected to the SUT", tc_id, script_id, "None", "None", log_level,
                              tbd)
            return False
        else:
            return True                                                         #battery is connected. level1 check. so not printing msg

    except Exception as e:
        library.write_log(lib_constants.LOG_INFO, "INFO: Exception in getting"
        " battery information", tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False


################################################################################
# Function Name : get_battery_charge
# Parameters    : tc_id, script_id = script id; tdb1= None, tdb2= None
# Functionality : gets the battery charge from the sut
# Return Value  : returns battery charge on successfully getting the information
#                 via wmic query and returns False otherwise
################################################################################
def get_battery_charge(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if check_for_battery(tc_id, script_id, log_level, tbd):
            ProcC = subprocess.Popen("wmic path win32_Battery Get "
                                     "EstimatedChargeRemaining",
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE)#using subprocess and wmic query to get the battery charge
            battery_info = ProcC.communicate()[0]                               #assings the raw data output of the wmic command
            battery_charge = str(battery_info).split()[1].strip("\\r\\r\\n")                            #returns the current charge
            library.write_log(lib_constants.LOG_INFO, "INFO: Battery "
            "information has been successfully fetched from OS", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return battery_charge                                               #returns battery charge on getting the info successfully

        else:
            return False

    except Exception as e:
        if "list index" in str(e):
            library.write_log(lib_constants.LOG_INFO, "INFO: Battery is not "
            "connected to the SUT",tc_id, script_id, "None", "None",
                              log_level, tbd)                                  #returns exception on errors
            return False
        else:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "getting battery info as %s"%e,tc_id, script_id, "None", "None",
                              log_level, tbd)                                  #returns exception on errors
            return False
