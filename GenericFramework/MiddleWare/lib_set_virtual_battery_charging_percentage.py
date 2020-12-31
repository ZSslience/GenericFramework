__author__ = 'kapilshx'
###########################General Imports######################################
import time
import os
import string
import wmi
############################Local imports#######################################
import library
import lib_constants
import utils
################################################################################
# Function Name : set_virtual_battery_mode_charging_percentage
# Parameters    : test case id,script id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : Set the virtual battery charging_percentage to 50%
################################################################################
def set_virtual_battery_charging_percentage(test_case_id,
                                        script_id,loglevel="ALL",tbd=None):
    try:
        port = utils.ReadConfig("BRAINBOX", "PORT")                             #Read brainbox port from config
        if "FAIL" in port:
            library.write_log(lib_constants.LOG_FAIL, "FAIL: Config entry is"
                " missing for tag variable port",test_case_id,script_id,
                              "None", "None", loglevel, tbd)                    # write error msg to log
            return False
        else:
            pass
        kb = library.KBClass(port)                                              #instantiate Brainbox class from the library
        send_key = lib_constants.SEND_KEY_SET_BATTERY
        kb.combiKeys(send_key)                                                  #send combikeys through Brainbox to sut
        time.sleep(lib_constants.DEFAULT_RELAY_PRESS_DURATION)                  #sleep for two seconds
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "set_virtual_battery_charging_percentage library function due to "
            "%s."%e,test_case_id, script_id,"None", "None", loglevel, tbd)      # write error msg to log
        return False
################################################################################
# Function Name : get_virtual_battery_charge_specific
# Parameters    : test case id,script id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : to check  and verify current virtual battery charge of SUT
################################################################################
def get_virtual_battery_charge_specific(virtual_token,test_case_id,script_id,
                                        loglevel="ALL",tbd=None):
    try:
        virtual_token = virtual_token.split(" ")
        virtual_token = virtual_token[-2]+"0"
        charge_remaining = ""
        c=wmi.WMI()
        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            charge_remaining = battery.EstimatedChargeRemaining
        if virtual_token == str(charge_remaining):                              #check if charge_remaining is equals to int(50) percentage
            library.write_log(lib_constants.LOG_INFO, "INFO :Verified "
                "successfully that current"
                " virtual battery charge is %s percent "%charge_remaining,
                test_case_id, script_id, "None", "None", loglevel, tbd)         # write info msg to log
            return True
        else:
            library.write_log(lib_constants.LOG_FAIL, "FAIL :Failed to verify "
                "Current virtual battery charge is %s percent"%(virtual_token),
                test_case_id, script_id, "None", "None", loglevel, tbd)         # write info msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "get_virtual_battery_charge_specific library function due to %s."%e,
            test_case_id, script_id,"None", "None", loglevel, tbd)              # write error msg to log
        return False
################################################################################