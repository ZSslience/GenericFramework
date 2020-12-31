author = "AsharanX"
################################################################################
#    Function name : update_registry
#    description   : Updates the registry with the given registry patch
#    parameters    : test_case_id: testcase_id;script_id: Script id
#    Returns       : 'True' on successful action and 'False' on failure
############################ Global Imports ####################################
import os
########################### Local Imports ######################################
import utils
import library
import lib_constants
################################################################################
def update_registry(test_case_id,script_id,reg_tag,
                    log_level="ALL",tbd=None):
    try:                                                                        # value name of the registry
        registry_path = reg_tag                                                 # gets the registry path and value where the key has to be added
        if False == registry_path:
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Config entry "
            "for registry is missing", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry file"
            " found for registry update %s"%registry_path, test_case_id,
            script_id, "None", "None", log_level, tbd)
        os.chdir(lib_constants.TOOLPATH)
        if os.path.exists("reg.reg"):
            pass
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: File not found in"
            " 'c:\automation\tools'",test_case_id,script_id, "None", "None",
            log_level, tbd)
            return False
        command = lib_constants.REGISTRY_UPDATE_CMD + " %s"%registry_path       # cmd for update registry is " regedit /s "
                                                                                # command to execute the reg patch file
        if 0 == os.system(command) :                                            # returns True if registry update is success
            library.write_log(lib_constants.LOG_INFO, "INFO: Registry path %s, "
            "updated successfully"%registry_path, test_case_id, script_id,
            "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Registry path %s, "
            "failed to update "%registry_path, test_case_id, script_id, "None",
                              "None", log_level, tbd)                           # returns False on failed to update
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Error in updating "
        "the registry values: %s"%e, test_case_id, script_id, "None", "None",
        log_level, tbd)
        return False
