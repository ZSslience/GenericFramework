__author__ = "patnaikx"

##############################General Library import############################
import os
import utils
import time
import sys
import winreg as winreg
#########################Local library import###################################
import lib_constants
import lib_run_command
import library

################################################################################
# Function Name : enable_kernel_dump_mode
# Parameters    : test_case_id is test case number, script_id is script_number
# Functionality : enable kernel dump mode
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################
def enable_kernel_dump_mode(token, test_case_id, script_id, log_level="ALL",
                     tbd="None"):

    try:
        kernel_dump_reg_path = lib_constants.KERNEL_DUMP_PATH                   # registry path for kernel dump mode
        reg_value = lib_constants.KERNEL_DUMP_MODE                              # registry value for kernel dump mode enable i.e. 2
        if set_registry_value('CrashDumpEnabled',kernel_dump_reg_path, reg_value,
                              test_case_id, script_id, log_level, tbd):         # registry set function calling to set crash kerneldump to 2
            library.write_log(lib_constants.LOG_INFO,"INFO: Registry value for "
            "crashdumpenabled set to kernel dump mode", test_case_id,
            script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Failed to set "
            "Registry value for crashdumpenabled to kernel dump mode",
            test_case_id, script_id, "None", "None", log_level, tbd)
            return False
        return_value = get_registry_value('CrashDumpEnabled',kernel_dump_reg_path,
                              test_case_id, script_id, log_level, tbd)          # getting the crash kernel dump registry value after setting
        if reg_value == return_value:
            library.write_log(lib_constants.LOG_INFO,"INFO: Registry value for "
            "crashdumpenabled set to kernel dump mode enable successfully",
            test_case_id, script_id, "None", "None", log_level, tbd)            # if successfully registry update done
            library.write_log(lib_constants.LOG_INFO,"INFO: Sut is going for"
            "reboot to reflect the registry setting for kernel dump mode enable",
            test_case_id, script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: unable to set the"
            "registry value for crashdumpenabled to kernel dump mode enable ",
            test_case_id, script_id, "None", "None", log_level, tbd)            # if failed to set the registry update for kernel dump mode
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
        test_case_id, script_id, "None", "None", log_level, tbd)                #exception error catch if failed
        return False
################################################################################
# Function Name : set_registry_value
# Parameters    : name:- registry name, value:- registry value
# Functionality : set registry value of enable kernel dump
# Return Value  : 'True' on successful action and 'False' on failure
#################################################################################function for set registry value for kernel dump mode
def set_registry_value(name, reg_path, value, test_case_id, script_id,
                       log_level="ALL", tbd="None"):
    try:
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                       winreg.KEY_WRITE)                        # creating variable for crash kernel dump
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_DWORD, value)       # setting value to crash kernel dump
        winreg.CloseKey(registry_key)
        library.write_log(lib_constants.LOG_INFO,"INFO: Registry value for "
        "kernel dump mode set to %s"%value, test_case_id,script_id, "None",
        "None", log_level, tbd)
        return True
    except WindowsError:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed to set the "
        "registry value for kernel dump mode", test_case_id,script_id, "None",
        "None", log_level, tbd)
        return False
################################################################################
# Function Name : get_registry_value
# Parameters    : name:- registry name
# Functionality : get registry value of enable kernel dump
# Return Value  : registry value on successful action and None on failure
################################################################################Function for getting crashkernel dump variable registry value

def get_registry_value(name,reg_path,test_case_id, script_id, log_level="ALL",
                     tbd="None"):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)                # value to be fetched for kernel dump mode
        winreg.CloseKey(registry_key)
        library.write_log(lib_constants.LOG_INFO,"INFO: Registry value for "
        "kernel dump mode is %s"%value, test_case_id,script_id, "None",
        "None", log_level, tbd)
        return value
    except WindowsError:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed to get the "
        "registry value for kernel dump mode", test_case_id,script_id, "None",
        "None", log_level, tbd)
        return None