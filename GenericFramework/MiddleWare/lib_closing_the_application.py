__author__ = 'patnaikx'


###########################Global library imports###############################
import os
import shutil
import time
import sys
################################################################################

############################Local library imports###############################
import library
import lib_constants
import utils
################################################################################


################################################################################
# Function Name : close_application()
# Description   : closing any application or game
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successful closing of app and 'false'
#                   on failure
# Purpose       : closing application or game
################################################################################

def close_application(application, test_case_id, script_id, log_level="ALL",
                                                                    tbd=None):
    new_script_id = script_id.strip(".py")
    log_file = new_script_id + '.txt'
    log_path = lib_constants.SCRIPTDIR + "\\" + log_file

    if "config" in application:
        app_ind = application.split('-')
        app_name = utils.ReadConfig(app_ind[1], app_ind[2])
        if "FAIL:" in app_name:
            library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Config entry for file_name is incorrect",
                test_case_id, script_id, "None", "None", log_level, tbd=None)   #fail if config entry is missing
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                        "INFO: Config entry for file_name is %s"%app_name,
                test_case_id, script_id, "None", "None", log_level, tbd=None)   #pass if config entry is correct
        app = app_name
    else:
        app_loc = utils.ReadConfig(application, "Tooldir")                      #read from config the file location to copy
        if "FAIL:" in app_loc:
                library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Config entry for app_loc is incorrect",
                    test_case_id, script_id, "None", "None",log_level, tbd=None)#fail if config entry is missing
                return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                        "INFO: Config entry for app_loc is %s"%app_loc,
                test_case_id, script_id, "None", "None", log_level, tbd=None)   #pass if config entry is correct
        app_name = utils.ReadConfig(application, "setup")                       #read from config the file name in host
        if "FAIL:" in app_name:                                                 #fail if config entry is missing
            library.write_log(lib_constants.LOG_ERROR,
                "ERROR: Config entry for app_name is not proper",test_case_id,
                          script_id, "None", "None", log_level, tbd=None)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                        "INFO: Config entry for app_name is %s"%app_name,
                test_case_id, script_id, "None", "None", log_level, tbd=None)   #pass if config entry is correct
    cmd_to_run_1 = 'tasklist | find "%s" > %s' % (app_name,log_path)            #command to check for a application exist or not

    cmd_to_run_2 = 'taskkill /f /im %s > %s' %(app_name, log_path)              #command to kill a application

    try:
        os.system(cmd_to_run_1)                                                 #run the command to check if application is
                                                                                # opened or not
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occurred "
            "due to %s"%e, test_case_id, script_id, "None", "None", log_level,
            tbd)
        sys.exit(lib_constants.EXIT_FAILURE)
    if os.path.exists(log_file):                                                #check for logfile generated
        file_size = os.path.getsize(log_file)                                   #check for size of the file
        if 0 == file_size:                                                      #return True as no application is running
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_INFO, "INFO: The log data "
                "resulting from the command execution confirms that "
                "There is No Application is running to Kill ", test_case_id,
                 script_id, "None", "None", log_level, tbd)
            return True
        else:                                                                   #check if that application is still running
            try:
                os.system(cmd_to_run_2)                                         #command to kill that application
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR,
                    "ERROR: Exception occurred " "due to %s"%e, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
    else:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to generate "
            "log file by executing %s command "%cmd_to_run_2,
                          test_case_id,script_id,"None", "None", log_level, tbd)
        return False
    time.sleep(10)
    try:
        os.system(cmd_to_run_1)                                                 #run the command 1:application exist or not
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occurred "
            "due to %s"%e, test_case_id, script_id, "None",
                          "None", log_level,tbd)
        return False
    if os.path.exists(log_file):                                                #check for logfile generated
        file_size = os.path.getsize(log_file)                                   #check for size of the file
        if 0 == file_size:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_INFO, "INFO: The log data "
                     "resulting from the command execution confirms that "
                    "Application has closed Successfully ", test_case_id,
                              script_id,"None", "None", log_level, tbd)
            return True
        else:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_ERROR, "ERROR: The log data "
                "resulting from the command execution confirms that "
                    "Application is not closed ", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    else:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to generate "
            "log file by executing %s command "%cmd_to_run_2,
                          test_case_id,script_id,"None", "None", log_level, tbd)
        return False