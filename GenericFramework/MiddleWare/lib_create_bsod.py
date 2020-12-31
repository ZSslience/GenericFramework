__author__ = "jkmody"

###########################General Imports######################################
import os
import time
import platform
from subprocess import Popen, PIPE
################################################################################

############################Local imports#######################################
import lib_constants
import library
import utils
################################################################################

################################################################################
# Function Name : create_bsod
# Parameters    : test_case_id, script_id, ostr,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To create BSOD manually
################################################################################

def create_bsod(test_case_id,script_id,ostr,log_level,tbd):
    try:
        token=utils.ProcessLine(ostr)
        if "USING" in token and "REGEDIT" not in token:
            library.write_log(lib_constants.LOG_WARNING, "WARNING : %s is not "
             "implemented yet"%token[4],test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:

            if "64" in platform.uname()[4]:
                tool_path = utils.ReadConfig("BSOD", "toolpath_64")             #use 64 bit exe if platform name has 64 in it
            else:
                tool_path = utils.ReadConfig("BSOD", "toolpath_32")             #use 32 bit exe if platform name has 32 in it
            if "FAIL:" in tool_path:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config value "
                "under BSOD context is missing", test_case_id, script_id,
                "DISPLAY", "None",log_level, tbd)                               #if failed to get the BSOD tool path information from config file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config value under "
                "BSOD context is found", test_case_id, script_id, "DISPLAY",
                "None",log_level, tbd)
            library.write_log(lib_constants.LOG_INFO, "INFO: Creating The BSOD."
                " Next Toolcase will verify whether BSOD created successfully "
                "or not.",test_case_id,script_id, "NotMyfault", "None",
                              log_level, tbd)                                   #Write the Info to the log
            os.chdir(tool_path)
            command = lib_constants.BSOD_COMMAND                                #command for creating the BSOD
            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            os.chdir(lib_constants.SCRIPTDIR)
            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to "
                    " create the BSOD due to %s "%str(stderr),test_case_id,
                              script_id, "NotMyfault", "None",log_level, tbd)   #Write the error to the log
                return False
            else:
                return True                                                     #returning True on Success

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
        test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : ensure_crash
# Parameters    : test_case_id, script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To Verify whether BSOD created or not
################################################################################

def ensure_crash(test_case_id,script_id,log_level,tbd):
    try:
        filename = os.path.expandvars(r'%systemroot%\memory.dmp')
        if os.path.isfile(filename):
            statbuf = os.stat(filename)
            if ((time.time() - statbuf.st_mtime)/lib_constants.SHORT_TIME) < \
                    lib_constants.FIVE_MIN :
                library.write_log(lib_constants.LOG_INFO, "INFO: BSOD created"
                    "  successfully",test_case_id,script_id, "NotMyfault",
                                   "None",log_level, tbd)                       #Write the Info to the log
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to"
                    " create BSOD manually",test_case_id,script_id, "NotMyfault",
                                  "None",log_level, tbd)                        #Write the WARNING to the log
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to"
                    " create BSOD manually",test_case_id,script_id, "NotMyfault",
                                  "None",log_level, tbd)                        #Write the WARNING to the log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
            test_case_id, script_id, "None", "None", log_level, tbd)            #Write the Exception to the log

        return False