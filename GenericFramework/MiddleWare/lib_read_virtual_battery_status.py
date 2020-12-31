__author__ = 'kapilshx'
###########################General Imports######################################
import time
import os
import wmi
############################Local imports#######################################
import library
import lib_constants
import utils
################################################################################
# Function Name : get_virtual_battery_charge
# Parameters    : test case id,script id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : to check current battery charge of SUT
#################################################################################
def get_virtual_battery_charge(test_case_id,script_id, loglevel="ALL",tbd=None):
    try:
        charge_remaining = ""
        c=wmi.WMI()
        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            charge_remaining = battery.EstimatedChargeRemaining
        if (charge_remaining >= 0 and charge_remaining <= 100):                 #if charge_remaining value is occurs in the range from 0 to 100 percent
            library.write_log(lib_constants.LOG_INFO, "INFO :The Current"
                " battery charge is: %s percent" %charge_remaining,
                test_case_id, script_id, "None", "None", loglevel, tbd)         # write info msg to log
            return charge_remaining
        else:                                                                   #if charge_remaining value is exceeding the range from 0 to 100 percent
            library.write_log(lib_constants.LOG_FAIL, "FAIL : Battery"
            " charge_remaining value is exceeding from range 0 to 100 percent",
                test_case_id, script_id, "None", "None", loglevel, tbd)         # write info msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "get_virtual_battery_charge library function due to %s."%e,
            test_case_id, script_id,"None", "None", loglevel, tbd)              # write error msg to log
        return False
################################################################################