__author__ = r'kapilshx\tnaidux'

# Local Python Imports
import lib_constants
import library
import lib_reading_the_registry
import lib_add_registry
################################################################################
# Function Name : edit_registry
# Parameters    : reg_token, test_case_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : Editing registry key and value
################################################################################


def edit_registry(reg_token, test_case_id, script_id, log_level="ALL",
                  tbd=None):

    try:
        if "->" in reg_token:                                                   # If backslashes are not present in the registry path
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Input "
                              "syntax is incorrect for set registry path",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        elif "\\" in reg_token:                                                 # If backslashes are present in the registry path
            reg_token = reg_token.replace("\\", "/")                            # Replace with forward slashes to give input to read registry function

        reg_token_list = reg_token.split("/")                                   # Convert string to list

        for temp in reg_token_list:
            if "DWORD" in temp:
                reg_type_input = "DWORD"
        registry_value = str(reg_token_list[-1])
        if "=" in registry_value:
            registry_value = registry_value.split(" ")
            reg_value = str(registry_value[-1]).strip()
            reg_name = str(registry_value[0]).strip()

        reg_token_list = reg_token_list[:-1]
        reg_path = "/".join(reg_token_list)

        if "set registry dword in" in reg_path.lower():
            if "Set " in reg_path:
                reg_path = str(reg_path).replace("Set registry DWORD in ", "")
            else:
                reg_path = str(reg_path).replace("set registry DWORD in ", "")

        try:
            data = lib_reading_the_registry.\
                read_registry(test_case_id, script_id, reg_path, reg_name)      # Call this read_registry() function to read current value of registry

            if type(data) is not bool and data is not None:                     # If data is some integer or hex value in the registry path
                library.write_log(lib_constants.LOG_INFO, "INFO: The Registry "
                                  "is read successfully and the value is %s "
                                  % str(data), test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to read the registry", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Failed to "
                              "read the registry() function due to %s" % e,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        reg_path = reg_path.replace("/", "\\")                                  # Replacing forward slashes by backward slashes

        try:
            result = lib_add_registry.add_registry(reg_name, reg_path,
                                                   reg_type_input, reg_value,
                                                   test_case_id, script_id,
                                                   log_level, tbd)

            if result is True:
                library.write_log(lib_constants.LOG_INFO, "INFO: Set %s value "
                                  "to %s for registry %s %s path"
                                  % (reg_type_input, reg_value, reg_path,
                                     reg_name), test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to set %s value to %s for registry %s %s "
                                  "path" % (reg_type_input, reg_value,
                                            reg_path, reg_name), test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                              "add_registry() function due to %s" % e,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "edit_registry() function due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
