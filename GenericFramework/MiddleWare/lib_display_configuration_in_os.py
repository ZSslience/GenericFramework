__author__ = "patnaikx"

##############################General Library import############################
import os
import glob
import codecs
import subprocess
import time
#########################Local library import###################################
import lib_constants
import library
import utils
import KBM_Emulation as kbm
################################################################################
# Function Name : lib_display_configuration_in_os
# Parameters    : test_case_id is test case number, script_id is script_number,
#                  token is token
# Functionality : configure different modes of display in OS.
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def display_configuration_in_os(token, test_case_id, script_id,
                                        log_level="ALL", tbd="None"):

    try:
        token = token.upper().split(" ")
        display_mode = utils.extract_parameter_from_token(token,
                                                        "SETUP","DISPLAY")[0]   # display mode extracted from input token
        display_device = utils.extract_parameter_from_token(token,
                                                                 "USING", "")[0]#display device extracted from input token
        display1, display2, display3 = "", "", ""
        display = []                                                            #creating a list of display devices

        if "SINGLE" == display_mode:
            display_type = " "                                                  #set mode type to null; if display is in single mode
            display1 = display_device.split('-')[0]
        else:
            display_type,end_pos = utils.extract_parameter_from_token(token,
                                                    "IN", "MODE")               #display configuration extracted from input token
            display_device = display_device.split('+')
            display1 = display_device[0].split('-')[0]
            display2 = display_device[1].split('-')[0]
            if "TRI" == display_mode:
                display3 = display_device[2].split('-')[0]
        display.extend((display1, display2, display3))                          # appending all display device names to display list

        if "SINGLE" == display_mode:
            if "EDP" == display1 or "DP" == display1:
                cmd = "%windir%\System32\DisplaySwitch.exe /internal"           # command for switching eDP/DP display
            elif "HDMI" == display1:
                cmd = "%windir%\System32\DisplaySwitch.exe /external"           # command for switching HDMI display
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Wrong "
                "input given for display configuration",test_case_id, script_id,
                "DISPLAY", "None", log_level,tbd)
                return False
            try:
                cmd_exe = subprocess.Popen(cmd, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           stdin=subprocess.PIPE)               #Execute the command to get the display property
                if "" != cmd_exe.communicate()[0]:                              #Failed to execute the command
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed in"
                                      " running the command for switching display",
                                      test_case_id, script_id, "DISPLAY", "None",
                                      log_level,tbd)
                    return False
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " running the command for switching display as: %s"%e,
                test_case_id, script_id, "DISPLAY", "None", log_level,tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command for "
                " switching display ran successfully.",test_case_id, script_id,
                "DISPLAY", "None", log_level,tbd)


        elif "DUAL" == display_mode or "TRI" == display_mode:
            if "CLONE" == display_type or "TRICLONE" == display_type:
                cmd_switch = "%windir%\System32\DisplaySwitch.exe /clone"       #command for switching display in clone mode
            elif "EXTENDED" == display_type or "TRIEXTENDED" == display_type:
                cmd_switch = " %windir%\System32\DisplaySwitch.exe /extend"     #command for switching display in extended mode
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Wrong "
                                  "input for display mode",test_case_id, script_id,
                                  "DISPLAY",  "None", log_level,tbd)
                return False
            try:
                cmd_exe = subprocess.Popen(cmd_switch, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           stdin=subprocess.PIPE)               #Execute the command to get the display property
                if "" != cmd_exe.communicate()[0]:                              #Failed to execute the command for switching
                    library.write_log(lib_constants.LOG_INFO, "INFO:"
                " Command for getting display information log failed to run",
                                test_case_id,script_id, "DISPLAY", "None",
                        log_level,tbd)
                    return False
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " running the command for switching display as: %s"%e,
                test_case_id, script_id, "DISPLAY", "None", log_level,tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command for "
                " configure display ran successfully",test_case_id, script_id,
                "DISPLAY", "None", log_level,tbd)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : %s " %e,
        test_case_id, script_id, "DISPLAY", "None", log_level, tbd)
        return False


def setup_display_config(token, display_device, tc_id, script_id, log_level,tbd):
    try:
        import time
        display_type = utils.extract_parameter_from_token(token.upper().split(" "),
                                                          "SETUP", "DISPLAY")[0]
        input_device_name = utils.ReadConfig("KBD_MOUSE",
                                             "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:                     # "FAIL:" in config details
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: Failed to get com port details and"
                              " input device name under KBD_MOUSE from "
                              "Config.ini", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        token = token.upper()
        token = token.split(" ")
        display_mode = utils.extract_parameter_from_token(token, "IN", "MODE")[0]  # display mode extracted from input token

        display1, display2, display3 = "", "", ""
        display = []                                                            # creating a list of display devices

        if "SINGLE" == display_mode:
            display_type = " "                                                  # set mode type to null; if display is in single mode
            display1 = display_device.split('-')[0]
        else:
            display_device = display_device.split('+')
            display1 = display_device[0].split('-')[0]
            display2 = display_device[1].split('-')[0]
            if "TRI" == display_mode:
                display3 = display_device[2].split('-')[0]
        display.extend((display1, display2, display3))                          # appending all display device names to display list

        if "SINGLE" == display_type:
            if "EDP" == display1 or "DP" == display1:
                cmd_cmd = "%windir%\System32\DisplaySwitch.exe /internal"       # command for switching eDP/DP display
            elif "HDMI" == display1:
                cmd_cmd = "%windir%\System32\DisplaySwitch.exe /external"       # command for switching HDMI display
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Wrong input given for display configuration",
                                  tc_id, script_id,
                                  "DISPLAY", "None", log_level, tbd)
                return False

        elif "DUAL" == display_type or "TRI" == display_type:
            if "CLONE" == display_mode or "TRICLONE" == display_mode:
                cmd_cmd = "%windir%\System32\DisplaySwitch.exe /clone"          # command for switching display in clone mode
            elif "EXTENDED" == display_mode or "TRIEXTENDED" == display_mode:
                cmd_cmd = " %windir%\System32\DisplaySwitch.exe /extend"        # command for switching display in extended mode
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Wrong input for display mode", tc_id,
                                  script_id, "DISPLAY", "None", log_level, tbd)
                return False

        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("KEY_GUI")                                             # Press Windows button
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("cmd")                                                  # Send cmd command
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type(cmd_cmd)
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.ONE)
        kb_obj.key_press("KEY_ENTER")

        library.write_log(lib_constants.LOG_INFO, "INFO: Set successfully",
                          tc_id, script_id, "None", "None", log_level, tbd)
        return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception : %s " % e,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False

