__author__ = 'singhd1x/kapilshx'

# Global Python Imports
import os
import subprocess
import time

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : launch_application()
# Description   : launch any application or game
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successful launch of app and 'false'
#                   on failure
# Purpose       : launch application or game
################################################################################


def launch_application(application, test_case_id, script_id, log_level="ALL",
                       tbd=None):

    try:
        if "config-" in application.lower():                                    # If 'config-' is present in token
            app_ind = application.split('-')
            app_location = utils.ReadConfig(app_ind[1], app_ind[2])
            if "FAIL:" == str(app_location):
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is incorrect for app_location",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
        else:                                                                   # If 'config-' is not present in token
            application = ((application.lower()).replace(" ","_")).strip(" ")
            application_name = application + "_path"
            app_location = utils.ReadConfig("APP",application_name)             # To get the app_location with the help of config file
            if "FAIL:" == str(app_location):
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is incorrect for app_location",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

        if not os.path.exists(app_location):
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s file is "
                              "present in the system" % app_location,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s file is present"
                              " in the system" % app_location, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            pass

        app_name = (app_location.rsplit("\\", 1)[1]).strip(" ")
        active_application = library.\
            check_running_application(app_name, test_case_id, script_id,
                                      log_level, tbd)                           # Function to check whether application is already running

        if active_application:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is running in "
                              "system" % app_name, test_case_id, script_id,
                              "None", "None", log_level, tbd)

            library.write_log(lib_constants.LOG_INFO, "INFO: %s is about to "
                              "close" % app_name, test_case_id, script_id,
                              "None", "None", log_level, tbd)

            close_app = library.\
                kill_running_application(app_name, test_case_id, script_id,
                                         log_level, tbd)                        # Function to close the running application

            if close_app:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s closed "
                                  "successfully trying to launch application"
                                  % app_name, test_case_id, script_id, "None",
                                  "None", log_level, tbd)

                path, exe_file = os.path.split(app_location)
                os.chdir(path)
                launch_app = \
                    launch_application_sys_specific(exe_file, app_location,
                                                    test_case_id, script_id,
                                                    log_level,  tbd)            # Function to launch the given application

                if launch_app:
                   return True
                else:
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to close %s" % app_name, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            try:
                library.write_log(lib_constants.LOG_INFO, "INFO: Trying to "
                                  "launch %s" % app_name, test_case_id,
                                  script_id, "None", "None", log_level, tbd)

                path, exe_file = os.path.split(app_location)
                os.chdir(path)
                launch_app = \
                    launch_application_sys_specific(exe_file, app_location,
                                                    test_case_id, script_id,
                                                    log_level, tbd)             # Function to launch the given application
                os.chdir(lib_constants.SCRIPTDIR)

                if launch_app:
                    return True
                else:
                    return False
            except Exception as e:                                              #error if failed to run the command
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e,test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : launch_application_sys_specific()
# Description   : launch application in system
# Parameters    : app_name, app_file_path, test_case_id, script_id
# Returns       : 'true' on successfully launch of app in system and 'false'
#                 on failure
# Purpose       : launch the application task
################################################################################


def launch_application_sys_specific(app_name, app_file_path, test_case_id,
                                    script_id, log_level="ALL", tbd=None):

    if "PECI" in app_name.upper():
        if os.path.exists(lib_constants.PECI_INSTALLED_PATH):
            library.write_log(lib_constants.LOG_INFO, "INFO: PECI Tool is "
                              "already Installed", test_case_id, script_id,
                              "PECI", "None", log_level, tbd)
            return True

        os.chdir(app_file_path)
        cmd_to_run_run_app = '"' + app_name + ".exe" + '"' + " -s"
    else:
        cmd_to_run_run_app = ['START', '%s' % app_file_path]                    # Command to launch an application

    try:
        try:
            prog = subprocess.Popen(cmd_to_run_run_app, shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)                     # To open the given application file using subprocess

            if prog is []:
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Please wait "
                                  "for 10 sec to launch %s" % app_name,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                time.sleep(10)
                return True
        except OSError as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s"
                              % e, test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
