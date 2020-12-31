__author__ = 'tnaidux'

##############################General Library import############################
import os
import glob
import subprocess
import shutil
#########################Local library import###################################
import lib_constants
import library
import utils
################################################################################
# Function Name : lib_get_display_configuration
# Parameters    : test_case_id is test case number, script_id is script number
# Functionality : to configure display
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################

def get_display_configuration(token, test_case_id, script_id, log_level="ALL",
                                  tbd="None"):

    try:
        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")                       #display tool directory path extracted from config
        display_cmd = utils.ReadConfig("DISPLAY", "cmd")                        #display command extracted from config
        file_path = lib_constants.DISPLAY_FILE_PATH                             #displayinfo file path extracted from lib_constants
        if "FAIL:" in [tool_dir, display_cmd]:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get "
            "config value under DISPLAY context", test_case_id, script_id,
            "DISPLAY", "None", log_level, tbd)                                  #if failed to get display tool information from config file, code exits
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Found config "
            "value under DISPLAY context successfully", test_case_id,
            script_id, "DISPLAY", "None", log_level, tbd)                       #if information extracted from config file under DISPLAY context, continue
        utils.filechangedir(tool_dir)                                           #change dir to display tool directory path
        if os.path.exists(file_path):
            os.remove(file_path)                                                #remove file_path if it exists
        cmd_exe = subprocess.Popen(display_cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE)       #execute the command to get the display property
        if "" != cmd_exe.communicate()[0]:                                      #failed to execute the command
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to run "
            "the command for display property", test_case_id, script_id,
            "DISPLAY", "None", log_level,tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Command for "
            "display property ran successfully", test_case_id, script_id,
            "DISPLAY", "None", log_level, tbd)

        file = glob.glob("DisplayInfo.txt")                                     #check for displayinfo file in the display tool directory
        if [] == file:                                                          #if file is empty
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "        #write fail msg to the log
            "get the display info log", test_case_id, script_id, "DISPLAY",
            "None", log_level, tbd)
            return False
        else:
            os.rename(tool_dir + "\\DisplayInfo.txt", tool_dir + "\\" +
                      script_id.split(".")[0] + ".txt")                         #rename displayinfo file
            if os.path.exists(script_id.split(".")[0] + ".txt"):
                shutil.copy(script_id.split(".")[0] + ".txt",
                            lib_constants.SCRIPTDIR)
            utils.filechangedir(lib_constants.SCRIPTDIR)                        #change dir to script directory path
            with open(script_id.split(".")[0] + ".txt", "r") as handle:         #file operation, open file in read mode and save the text in handle
                handle = handle.readlines()
                for line in handle:                                             #iterate through the lines
                    if "Current System Configuration" in line:                  #verifying display token in line
                        temp = line.split("::")[1]
                        if "HDMI" in temp:
                            display_device = "HDMI"
                        elif "DP" in temp:
                            display_device = "DP"
                        else:
                            display_device = "EDP"
            if display_device:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s Display "   #write pass msg to the log
                "got configured successfully"%display_device, test_case_id,
                script_id, "DISPLAY", "None", log_level, tbd)
                return display_device
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "    #write fail msg to the log
                "configure display", test_case_id, script_id, "DISPLAY",
                "None", log_level, tbd)
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : %s "     #write fail exception error to log
        %e, test_case_id, script_id, "DISPLAY", "None", log_level, tbd)
        return False