__author__ = 'patnaikx'

############################General Python Imports##############################
import os
############################Local Python Imports################################
import library
import lib_constants
import utils
################################################################################
# Function Name : verify_right_click_option_in_desktop_context
# Parameters    : ostr - token, test_case_id-test case ID, script_id - script ID
# Functionality : verify right click options in desktop context
# Return Value  : 'True' if found, else 'False'
# Syntax        : verify if <option> present on desktop context menu
################################################################################


def verify_right_click_option_on_desktop(ostr, test_case_id, script_id,
                                         log_level="ALL",tbd=None):
    try:
        token = ostr.upper().split(" ")
        right_click_opt, pos = utils.extract_parameter_from_token(token,
                                            "IF", "PRESENT")                    # right click option extracted from input token
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Option to be verify "
        "for right click menu is %s"%right_click_opt,test_case_id,
        script_id, "None", "None", log_level, tbd)
        if "INTEL(R) GRAPHICS SETTINGS" in right_click_opt:                     #if option is intel graphics settings
            reg_path = lib_constants.GRAPHICS_REG_PATH                          #registry path for intel graphics setting
            reg_value = lib_constants.GRAPHICS_REG_VALUE                        #registry value for intel graphics setting
            new_script_id = script_id.strip(".py")
            log_file = new_script_id + '.txt'
            log_path = lib_constants.SCRIPTDIR + "\\" + log_file
            reg_query_cmd = lib_constants.REG_QUERY_COMMAND                     # reg query command fetch from lib_constants
            cmd = reg_query_cmd + reg_path + " /s > " + log_path                # command to get all sub registry folder and their coresponding value
            os.system(cmd)
            if os.path.exists(log_path):                                        #check for registry output log path and log file size
                file_size = os.path.getsize(log_path)                           #get the size of the log file
                if 0 != file_size:
                    with open(log_path, "r") as f:
                        for line in f:
                            if reg_value.upper() in line.upper():               #print pass log, if registry value for intel graphics setting found
                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Registry value for Intel(r) Graphics "
                                "Setting is found in log and matched",
                                test_case_id, script_id, "None", "None",
                                log_level, tbd)

                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Intel(r) graphics setting is present "
                                "in desktop right click option list",
                                test_case_id, script_id,"None", "None",
                                log_level, tbd)
                                return True
                        else:
                            pass
                    library.write_log(lib_constants.LOG_INFO, "INFO:"
                    " Intel(r) graphics setting is not present in desktop "
                    "right click option list", test_case_id, script_id, "None",
                    "None", log_level, tbd)
                    return False                                                # print Fail log if registry value and path not found in log i.e. option is not present in registry log
        else:                                                                   # print Fail log if right click option is not handled to check
            library.write_log(lib_constants.LOG_INFO,"INFO: Verification of %s "
            "option in right menu is not handled"%right_click_opt,test_case_id,
            script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:                                                      # exception handled
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable To verify The"
        " right click option due to %s"%e, test_case_id, script_id,
        "None", "None", log_level, tbd)
        return False

