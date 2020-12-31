__author__ = r"asharanx\tnaidux"

# Global Python Imports
import platform

# Local Python Imports
import lib_constants
import library

################################################################################
# Function Name : read_registry
# Parameters    : tc_id, script_id, reg_path, reg_val_name, log_level, tbd
# Functionality : Reads the registry value of the path given
# Return Value  : Returns registry key value if condition is True, 
#                 False otherwise
################################################################################


def read_registry(tc_id, script_id, reg_path, reg_val_name, log_level="ALL", 
                  tbd=None):

    try:
        reg_path = reg_path.replace("/", "\\")
        if not reg_path:
            return None                                                         # Returns None if reg_path is not found
        reg_val = regkey_value(r"" + reg_path, reg_val_name)  # Calls the function to get the registry key value
        return reg_val
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


def regkey_value(path, name="", start_key=None, log_level="ALL", tbd=None):     # Function for reading the registry

    try:
        if "3" == platform.python_version()[0]:
            import winreg as wreg                                               # Imports based on the platform python version
        elif "2" == platform.python_version()[0]:
            import winreg as wreg
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "import the windows registry", "None", "None",
                              "None", "None", log_level, tbd)

        if isinstance(path, str):                                               # Checks for the registry path
            path = path.split("\\")                                             # Splits the registry path based on the slash"\\"

        if start_key is None:                                                   # Checks if the start key is none
            start_key = getattr(wreg, path[0])                                  # Gets the starting sting of the registry path
            return regkey_value(path[1:], name, start_key)
        else:
            subkey = path.pop(0)

        with wreg.OpenKey(start_key, subkey) as handle:                         # Checks for the registry key if present in that path
            assert handle
            if path:
                library.write_log(lib_constants.LOG_INFO, "INFO: registry "
                                  "path is %s" % path, "None", "None",
                                  "None", "None", log_level, tbd)
                return regkey_value(path, name, handle)                         # Returns the path and name of the registry if it is present
            else:
                desc, i = None, 0
                try:
                    while not desc or desc[0] != name:
                        desc = wreg.EnumValue(handle, i)
                        i += 1
                    return desc[1]                                              # iteraIes to find the registry key name as mentioned in the test step and returns the same
                except Exception as e:
                    if "WARNING" in e:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "Registry path and value not found",
                                          "None", "None", "None", "None",
                                          log_level, tbd)
                        return False
                    else:
                        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION:"
                                          " Unable To Find The Registry Value",
                                          "None", "None", "None", "None",
                                          log_level, tbd)
                        return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          "None", "None", "None", "None", log_level, tbd)
        return False
