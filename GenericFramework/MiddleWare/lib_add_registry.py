__author__ = r'patnaikx\tnaidux'

# General Python Imports
import winreg as winreg
from winreg import *

# Local Python Imports
import library
import lib_constants

################################################################################
# Function Name : add_registry
# Parameters    : reg_name, reg_path, reg_type, reg_value, test_case_id,
#                 script_id, log_level, tbd
# Return Value  : True if registry added, False otherwise
# Purpose       : Adding registry key and value
# Target        : SUT
################################################################################


def add_registry(reg_name, reg_path, reg_type, reg_value, test_case_id,
                 script_id, log_level="ALL", tbd=None):

    try:
        reg_type = library.return_type(reg_type)

        if "/" in reg_path:                                                     # If forward slashes are present in the registry path
            reg_path = reg_path.replace("/", "\\")                              # Replace with backward slashes to give input to read resitry function
        elif "->" in reg_path:                                                  # If arrows(->) are present in the registry path
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Input "
                              "syntax is incorrect for set registry path",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        hkeypath = reg_path.split("\\")[0]                                      # Split registry path and take the HKEY PATH
        hkeypath = library.return_reg(hkeypath)                                 # Take the HKEY value from library
        reg_path = reg_path.split("\\", 1)[1]

        if "0x" in reg_value or "0X" in reg_value:                              # If reg_value is equal to hex data
            reg_value = int(reg_value, 16)
        else:
            reg_value = hex(int(reg_value, 16))                                 # Converting it to hexadecimal
            reg_value = int(reg_value, 16)

        library.write_log(lib_constants.LOG_INFO, "INFO: Registry add for %s "
                          "in %s path with %s value and %s type"
                          % (reg_name, reg_path, reg_value, reg_type),
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)

        try:
            reg_key = winreg.OpenKeyEx(hkeypath, reg_path, 0,
                                       winreg.KEY_ALL_ACCESS)                   # Store registry key value

            winreg.SetValueEx(reg_key, reg_name, 0, reg_type, reg_value)        # Add registry key and value

            CloseKey(reg_key)                                                   # Close the registry key and value

            library.write_log(lib_constants.LOG_INFO, "INFO: Registry for %s "
                              "added in %s path" % (reg_name, reg_path),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        except WindowsError as e:
            try:
                reg_key = winreg.OpenKeyEx(hkeypath, reg_path, 0,
                                           winreg.KEY_ALL_ACCESS)               # Store registry key value

                winreg.SetValueEx(reg_key, reg_name, 0, reg_type, reg_value)    # Add registry key and value

                CloseKey(reg_key)                                               # Close the registry key and value

                library.write_log(lib_constants.LOG_INFO, "INFO: Registry for "
                                  "%s added in %s path" % (reg_name, reg_path),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            except WindowsError as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Failed "
                                  "to add the registry due to %s " % e,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
    except WindowsError as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
