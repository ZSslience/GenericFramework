__author__ = "kapilshx"

###########################General Imports######################################
import os
import subprocess
import time
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_run_command
################################################################################
# Function Name : enable_ucsi
# Parameters    : typec_token, system_info, test_case_id, script_id, log_level
#                 and tbd
# Return Value  : returns log_file on successful action, False otherwise
# Functionality : to run the UCSI reg file in sut & host, to enable ucsi
################################################################################


def enable_ucsi(typec_token, system_info, test_case_id, script_id,
                log_level="ALL", tbd="None"):

    try:
        reg_file_name = utils.ReadConfig("TYPEC_COMMAND_FILE", "reg_file")      #Extracting registry file for ucsi enabling
        if "FAIL:" in reg_file_name:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get "
            "config entry for reg_file under [TYPEC_COMMAND_FILE] tag",
            test_case_id, script_id, "None", "None", log_level, tbd)            #Writing log_info message to the log file
            return False

        cmd_ucsi_enable = "regedit.exe /s " + reg_file_name                     #Command to run enable ucsi
        cmd_output = subprocess.Popen(cmd_ucsi_enable, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)                   #Running command using subprocess

        out, error = cmd_output.communicate()
        if 0 == len(error):                                                     #If no error in running the command for enabling ucsi
            library.write_log(lib_constants.LOG_INFO, "INFO: Command ran "
            " succesfully for to enable UCSI", test_case_id, script_id,
            "UCSI_tool", "None", log_level, tbd)                                #Writing log_info message to the log file
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to execute"
            "UCSI command", test_case_id, script_id, "UCSI_tool", "None",
            log_level, tbd)                                                     #Writing log_info message to the log file
            return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "UCSI_tool", "None", log_level, tbd)           #Writing exception message to the log file
        return False

################################################################################
# Function Name : running_typec_command
# Parameters    : typec_token, system_info, test_case_id, script_id,
#                 loglevel and tbd
# Return Value  : returns log_file on successful action, False otherwise
# Functionality : to run the typec command using ucsi tool in sut & host and
#                 returns the log_path
################################################################################


def running_typec_command(typec_token, system_info, test_case_id, script_id,
                          log_level="ALL", tbd="None"):

    try:
        ucsi_control_exe_path_name = utils.ReadConfig("TYPEC_COMMAND_FILE",
                                                      "ucsi_control")           #Extracting ucsi_control from config file
        if "FAIL:" in ucsi_control_exe_path_name:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get "
            "config entry for ucsi_control under [TYPEC_COMMAND_FILE] tag",
            test_case_id, script_id, "None", "None", log_level, tbd)
            return False

        typec_token_list = typec_token.strip().upper().split(" ")               #Splitting and removing spaces from token and appending to token list

        if "IN" in typec_token.strip().upper():
            cmd_info, pos = library.\
                            extract_parameter_from_token(typec_token_list,
                                            "COMMAND", "IN", log_level, tbd)    #Extractring cmd_info
            cmd_info = cmd_info.strip(" ")
        else:
            cmd_info = (typec_token_list[-2:])
            cmd_info = (" ".join(cmd_info)).strip(" ")

        ucsi_control_exe_path_final = ucsi_control_exe_path_name + " " + \
                                      "send"+ " " + cmd_info                    #Appending ucsi_control_exe_path_name and cmd_info
        ucsi_log_path = lib_run_command.run_command(ucsi_control_exe_path_final,
                            test_case_id, script_id, log_level, tbd)            #Running the command using ucsicontrol.exe file

        if False != ucsi_log_path:                                              # if no log for the ucsi control run command
            library.write_log(lib_constants.LOG_INFO, "INFO: Typec command %s "
            "is executed in the %s system successfully"%(cmd_info, system_info),
            test_case_id, script_id, "UCSI_tool", "None", log_level, tbd)       #Writing log_info message to the log file
            return ucsi_log_path
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to execute"
            "Typec command %s in the %s system"%(cmd_info, system_info),
            test_case_id, script_id, "UCSI_tool", "None", log_level, tbd)       #Writing log_info message to the log file
            return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "UCSI_tool", "None", log_level, tbd)           #Writing exception message to the log file
        return False