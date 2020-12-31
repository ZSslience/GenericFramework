__author__ = 'sharadth\yusufmox'

######################### Global Library import ################################
import subprocess
import time
import os
import fnmatch
########################## Local Library import ################################
import utils
import library
import lib_constants
################################################################################


################################################################################
# Function Name : pavp_heavy
# Parameters    : pavp_tool_path, test_case_id,script_id,log_level,tbd
# Return Value  : Returns true if run bat file successful else fail
# Description   : checks if bat file creation is successful and runs the bat
#                 file
################################################################################
def pavp_mode_run(pavp_tool_path, pavp_bat, test_case_id, script_id, log_level,
                  tbd):

    os.chdir(pavp_tool_path)                                                    # Change os path to Bat file
    file_flag = False
    for root, dirs, files in os.walk(pavp_tool_path):                           # Check if pavp bat file is created or not
        for file in files:
            if file.endswith(pavp_bat):
                file_flag = True
                break
            else:
                file_flag = False

        if file_flag:
            break

    if file_flag:
        library.write_log(lib_constants.LOG_INFO,"INFO : Pavp bat File"         # File successfully created
                         " found", test_case_id, script_id, "None", "None",
                          log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO : unable to find Pavp "
                          "bat File", test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return False

    os.chdir(pavp_tool_path)                                                    # RUN THE BAT FILE
    for dirname in os.listdir(pavp_tool_path):
        if dirname == "PavpLog_Case1.txt":
            os.remove('PavpLog_Case1.txt')                                      # Removing old log files
    try:
        if subprocess.Popen(pavp_tool_path + '\\' + pavp_bat,
                            stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE):                  # Start the subprocess of powershell
                                                                                # Delay time to run Pavp test
            library.write_log(lib_constants.LOG_INFO,"INFO : Pavp cmdline "
                              "triggered. Waiting 10sec for log file",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            time.sleep(lib_constants.SX_TIME)
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to run bat"
                          "bat file due to %s." % e, test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name : read_log_file
# Parameters    : pavp_mode,test_case_id,script_id,log_level,tbd
# Return Value  : Returns true if run is successful else fail
# Description   : Reads for specific tags in logfile on successfully performing
#                 the task
################################################################################
def read_log_file(pavp_mode, pavp_tool_path, test_case_id, script_id, log_level,
                                                                        tbd):
    try:
        file_list = fnmatch.filter(os.listdir(pavp_tool_path),
                                   'PavpLog_Case1.txt')                         # Search for generated log
        file_name = file_list[0]

        if "PavpLog_Case1.txt" == file_name:
            library.write_log(lib_constants.LOG_INFO,"INFO : Log file %s found"
                              % file_name, test_case_id, script_id, "None",
                              "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : Log file %s not "
                              "found" % file_name, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        file = open(file_name, "r")                                             # Open file to read
        log_data = file.readlines()
        file.close()
        session_created, all_frame_verfied, session_destroyed = False, False,\
                                                                False
        for line in log_data:                                                   # Check for success tags
            if -1 != line.find("DX 'CreatePavp' succeeded."):                   # Check for createPAVP success
                library.write_log(lib_constants.LOG_INFO,"INFO : Pavp session "
                                 "created",test_case_id,script_id, "None",
                                 "None", log_level, tbd)
                session_created = True

            elif -1 != line.find("Reached EOF for input stream"):               # Check EOF stream
                library.write_log(lib_constants.LOG_INFO,"INFO: Video frames "
                                  "run successfully", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                all_frame_verfied = True

            elif -1 != line.find("Destroy PAVP session"):                       # Check For PAVP destroyed session
                library.write_log(lib_constants.LOG_INFO, "INFO : session "
                                  "destroyed successfully", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                session_destroyed = True

            else:
                pass

        if session_created is True and all_frame_verfied is True\
                and session_destroyed is True:                                  # Successfully checked for PAVP mode

            library.write_log(lib_constants.LOG_INFO, "INFO : Successfully "
                              "checked PAVP in %s mode "%pavp_mode,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Failed to run"
                               " PAVP in %s mode " % pavp_mode, test_case_id,
                               script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to run pavp "
                          "test mode due to %s." % e, test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name : pavp_test_modes
# Parameters    : token, tc_id, script_id, log-level, tbd
# Return Value  : Returns True if Pavp mode test is successful else False
# Description   : Checks for lite and heavy pavp mode run
################################################################################
def pavp_test_modes(token, test_case_id, script_id, log_level, tbd):

    try:
        token = token.upper()                                                   # Convert token into upper
        token = token.split(" ")                                                # Convert token into list
        pavp_tool_path = lib_constants.PAVP_PATH

        pavp_mode = utils.extract_parameter_from_token(token, "IN", "MODE")[0]  # Extract PAVP test mode

        library.write_log(lib_constants.LOG_INFO, "INFO : Mode of test is %s"
                          % pavp_mode, test_case_id, script_id, "None", "None",
                          log_level, tbd)

        pavp_heavy_bat = lib_constants.PAVP_HEAVY_BAT
        pavp_lite_bat = lib_constants.PAVP_LITE_BAT

        if "HEAVY" == pavp_mode:
            bat_flag = pavp_mode_run(pavp_tool_path, pavp_heavy_bat,
                                     test_case_id, script_id, log_level, tbd)   # Calling function for heavy mode

        elif "LITE" == pavp_mode:
            bat_flag = pavp_mode_run(pavp_tool_path, pavp_lite_bat,
                                     test_case_id, script_id, log_level, tbd)   # Calling function for lite mode

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Unknown mode %s,"
                              " not implemented" % pavp_mode, test_case_id,
                              script_id, "None", "None", log_level, tbd)        # Pavp mode unknown
            return False

        if bat_flag:
            if read_log_file(pavp_mode, pavp_tool_path, test_case_id,
                                       script_id, log_level, tbd):              # Read the log file generated
                return True
            else:
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Failed to run bat"
                              " file", test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Pavp mode unknown

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to run pavp "
                          "test mode due to %s." % e, test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False
################################################################################
