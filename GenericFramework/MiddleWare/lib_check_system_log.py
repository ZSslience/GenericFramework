__author__ = r"patnaikx\tnaidux"

# General Python Imports
import os
import time
import re

# Local Python Imports
import lib_constants
import library
import utils

################################################################################
# Function Name : check_system_log
# Parameters    : event, test_case_id, script_id, log_level, tbd
# Functionality : check system log for bug check/events.
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def check_system_log(event, test_case_id, script_id, log_level="ALL",
                     tbd="None"):

    try:
        if "SHUTDOWN" in event or "RESTART" in event:
            cmd_to_run = lib_constants.RESTART_SHELL_COMMAND                    # Power shell command for shutdown check in system log
        elif "S3" in event or "S4" in event:
            cmd_to_run = lib_constants.C3_SHELL_COMMAND                         # Power shell command for sleep or hibernation check in system log
        elif "CS" in event:
            cmd_to_run = lib_constants.CS_SHELL_COMMAND                         # Power shell command for connected standby check in system log
        elif "BSOD" in event:
            cmd_to_run = lib_constants.BSOD_SHELL_COMMAND                       # Power shell command for BSODcheck in system log
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is not "
                              "implemented" % event, test_case_id, script_id,
                              "None", "None", log_level, tbd)

        for filename in os.listdir("."):                                        # Check for filename in directory for nsh
            if filename.endswith("ps1"):                                        # If any nsh file is there unlink the file
                os.unlink(filename)

        myFile = open(lib_constants.SCRIPTDIR + "\\psquery.ps1", "w")
        myFile.write(cmd_to_run)
        myFile.close()

        time.sleep(lib_constants.FIVE_SECONDS)                                  # Sleep for 5 seconds

        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        script_dir = lib_constants.SCRIPTDIR
        log_path = script_dir + "\\" + log_file

        powershell_path = utils.ReadConfig("WIN_POWERSHELL", "PATH")            # Read from powershell the value of powershell path
        if "FAIL" in powershell_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry of powershell path",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        shell_script = 'psquery.ps1'                                            # Shell script should be placed in script directory
        exe_path = os.path.join(lib_constants.SCRIPTDIR, shell_script)

        final_command = 'powershell.exe '+ exe_path + ' > ' + log_path          # Concat the commands along with the log path

        try:
            os.chdir(powershell_path)
            os.system(final_command)
        except Exception as e:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s"
                              % e, test_case_id, script_id, "None", "None",
                              log_level, tbd)

        os.chdir(lib_constants.SCRIPTDIR)

        if os.path.exists(log_path):
            file_size = os.path.getsize(log_file)                               # Get the size of the log file
            found = False

            if "SHUTDOWN" == event:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)power off(.*)", line) or \
                           re.match("(.*)shutdown(.*)", line):
                            found = True
                            break                                               # Return TRUE value if log generated and SHUTDOWN found
                        else:
                            continue
            elif "RESTART" == event:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)restart(.*)", line):
                            found = True
                            break                                               # Return True value if log generated and RESTART found
                        else:
                            continue
            else:
                if file_size != 0:
                    found = True                                                # Return TRUE if bugcheck found in log
                else:
                    found = False

            if found:
                library.write_log(lib_constants.LOG_INFO, "INFO: System log "
                                  "verified for %s" % event, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "content was not found in system log"
                                  % event, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
