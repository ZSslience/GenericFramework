__author__ = r"patnaikx\hvinayx\sivakisx\tnaidux\parunacx"

# Global Python Imports
import codecs
import io
import os
import platform
import subprocess
import time
#########################Local library import###################################
import utils
import library
import lib_constants
################################################################################


################################################################################
# Function Name : verify_usb_modes
# Parameters    : token, test_case_id, script_id, log_level and tbd
# Functionality : to verify different usb data transfer modes
# Return Value  : True on successful action, False otherwise
################################################################################


def verify_usb_modes(token, test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        token_list = token.split(' ')                                           #Splitting token based on space and appending to token_list
        usb_type, pos = \
            utils.extract_parameter_from_token(token_list, "CHECK", "AS",
                                               log_level, tbd)                  #Extracting the usb type from the token

        if "IN" in token_list:
            speed, pos_speed = \
                utils.extract_parameter_from_token(token_list, "AS", "IN",
                                                   log_level, tbd)              #Extracting the speed from the token if system is specified
        else:
            speed, pos_speed = \
                utils.extract_parameter_from_token(token_list, "AS", "",
                                                   log_level, tbd)              #Extracting the speed from the token if system is not specified

        usb20_flag, usb30_flag, usb31_flag, usb_version =\
            verify_usb_tree_view_log(usb_type, speed, test_case_id, script_id,
                                     log_level, tbd)                            # Function to check the operating speed and bcdusb version

        if usb20_flag != 0 and speed == "HIGHSPEED" and \
                (usb_version == "0x200" or usb_version == "0x210"):
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        elif usb30_flag != 0 and speed == "SUPERSPEED" and\
                usb_version == "0x300":
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        elif usb30_flag != 0 and speed == "HIGHSPEED" and\
                (usb_version == "0x200" or usb_version == "0x210"):
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        elif usb31_flag != 0 and speed == "SUPERSPEEDPLUS" and\
                usb_version == "0x310":
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        elif usb31_flag != 0 and speed == "SUPERSPEED" and\
                usb_version == "0x300":
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        elif usb31_flag != 0 and speed == "HIGHSPEED" and\
                (usb_version == "0x200" or usb_version == "0x210"):
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s detected as %s in the system"
                              % (usb_type, speed), test_case_id,
                              script_id, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: No USB device detected in system",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Writing log warning message to the log file
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #Writing exception message to the log file
        return False

################################################################################
# Function Name : verify_usb_log
# Parameters    : test_case_id, script_id, log_level and tbd
# Functionality : verify usb type variable
# Return Value  : returns counter values for different modes of usb
################################################################################


def verify_usb_log(device_name, test_case_id, script_id, log_level="ALL",
                   tbd=None):

    try:
        log_file = script_id.replace(".py", ".txt")                             # Replacing the script id with ".txt" extension
        log_path = lib_constants.SCRIPTDIR + "\\" + log_file                    # Appending log file to the script directory

        if os.path.exists(log_path):
            os.remove(log_path)                                                 # Removing the log file form defined path

        if "64" in platform.uname()[4]:                                         # if Platform is 64 bit
            command = lib_constants.USBVIEW_PATH + "\\" + "x64" + "\\" + \
                      lib_constants.USBVIEW_SETUP + \
                      " /f /q /saveall:" + log_path                             # Appending the command
        else:
            command = lib_constants.USBVIEW_PATH + "\\" + "x86" + "\\" + \
                      lib_constants.USBVIEW_SETUP + \
                      "/f /q /saveall:" + log_path                              # Appending the command

        if get_usb_view_log(lib_constants.USBVIEW_PATH, command, test_case_id,
                            script_id, log_level="ALL", tbd=None):              #Function call for to generate log
            pass
        else:
            return False

        os.chdir(lib_constants.SCRIPTDIR)
        usb2flag, usb3_highflag, usb3_superflag, = 0, 0, 0

        with codecs.open(os.path.join(log_path), "r") as \
                file:                                                           #File operation
            for line in file:                                                   #Iterate through file
                if "USB Mass Storage Device" in line or \
                   "WINUSB" in line.upper():                                    #Search for USB  mass storage device
                    for i in range(lib_constants.ITERATE1):                     #Iterate for next 20 lines rather than full file
                        line = next(file)                                       #Got to next line
                        if "===>Device Descriptor<===" in line:
                            for i in range(lib_constants.ITERATE2):             #Iterate for next 10 lines instead of complete file
                                line = next(file)
                                if "0x0210" in line:                            #Check for 0x0210 (usb3)
                                    for i in range(8):
                                        line = next(file)
                                        if "Manufacturer" in line:
                                            for i in range(1):
                                                line = next(file)
                                                if device_name.upper() in \
                                                        line.upper():
                                                    usb2flag += 1
                                                    usb3_highflag += 1          #If found high flag is 1
                                elif "0x0300" in line:                          #Check for 0x300  (usb3)
                                    for i in range(8):
                                        line = next(file)
                                        if "Manufacturer" in line:
                                            for i in range(1):
                                                line = next(file)
                                                if device_name.upper() in \
                                                        line.upper():
                                                    usb3_superflag += 1         #If found super flag is 1
                                elif "0x0200" in line:                          #Check for 0x0200 (usb2)
                                    for i in range(8):
                                        line = next(file)
                                        if "Manufacturer" in line:
                                            for i in range(1):
                                                line = next(file)
                                                if device_name.upper() in \
                                                        line.upper():
                                                    usb2flag += 1               #If found high flag is 1
                                else:
                                    pass
                        else:
                            pass
                else:
                    pass
        return usb2flag, usb3_highflag, usb3_superflag
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #Writing exception message to the log file

################################################################################
# Function Name : verify_usb_tree_view_log
# Parameters    : usb_type, test_case_id, script_id, log_level and tbd
# Functionality : to verify usb type data transfer mode
# Return Value  : returns counter values for different modes of usb type
################################################################################


def verify_usb_tree_view_log(usb_type, speed, test_case_id, script_id,
                             log_level="ALL", tbd=None):

    try:
        device_mount_point = "None"
        device_name = "None"
        usb20_flag, usb30_flag, usb31_flag, usb_version = 0, 0, 0, 0
        if "PENDRIVE" in usb_type.upper() or "HDD" in usb_type.upper():
            device_mount_point = utils.ReadConfig("PLUG_UNPLUG",
                                                  "%s_MOUNT_POINT" % usb_type)

            if "FAIL:" in device_mount_point or device_mount_point is None:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to get the config entry for"
                                  " %s_MOUNT_POINT under [PLUG_UNPLUG]"
                                  % usb_type, test_case_id, script_id,
                                  "None", "None", log_level, tbd)               # Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Config entry found for "
                                  "%s_MOUNT_POINT under [PLUG_UNPLUG]"
                                  % usb_type, test_case_id, script_id, "None",
                                  "None", log_level, tbd)                       # Writing log info message to the log file
        else:
            device_name = utils.ReadConfig("PLUG_UNPLUG",
                                           "%s_DEVICE_NAME" % usb_type)
            if "FAIL:" in device_name or device_name is None:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to get the config entry for"
                                  " %s_MOUNT_POINT under [PLUG_UNPLUG]"
                                  % usb_type, test_case_id, script_id,
                                  "None", "None", log_level, tbd)               # Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Config entry found for "
                                  "%s_MOUNT_POINT under [PLUG_UNPLUG]" % usb_type,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

        result, log_path = get_usb_tree_view_log(lib_constants.USBTREEVIEW_PATH,
                                                 lib_constants.USBTREEVIEW_EXE,
                                                 test_case_id, script_id,
                                                 log_level, tbd)

        if os.path.exists(log_path):
            with codecs.open(log_path, 'r', 'utf-16') as file:
                for line in file:
                    if "Device Description" in line and\
                            "Mass Storage Device" in line:
                        for temp in range(100):
                            try:
                                line = next(file)
                            except:
                                pass
                            if "Mountpoint" in line and device_mount_point in line:
                                for temp in range(100):
                                    line = next(file)
                                    if "DevIsOpAtSsOrHigher" in line and\
                                            "0" in line and "HIGHSPEED" == speed:
                                        usb20_flag = +1
                                    elif "DevIsOpAtSsOrHigher" in line and\
                                            "1" in line and "SUPERSPEED" == speed:
                                        usb30_flag = +1
                                    elif "DevIsSsCapOrHigher" in line and\
                                            "1" in line and "HIGHSPEED" == speed:
                                        usb20_flag = +1
                                    elif "DevIsOpAtSsPlusOrHigher" in line and\
                                            "1" in line and "SUPERSPEEDPLUS" == speed:
                                        usb31_flag = +1
                                    elif "DevIsSsPlusCapOrHigher" in line and\
                                            "1" in line and "SUPERSPEED" == speed:
                                        usb30_flag = +1
                                    elif "DevIsSsPlusCapOrHigher" in line and \
                                            "1" in line and "HIGHSPEED" == speed:
                                        usb20_flag = +1
                                    else:
                                        pass
                                    if "bcdUSB" in line:
                                        usb_version = \
                                            line.split(":")[1].split(" ")[1]
                        else:
                            pass
                    elif "Device Description" in line and device_name in line:
                        for temp in range(100):
                            line = next(file)
                            if "DevIsOpAtSsOrHigher" in line and\
                                    "0" in line and "HIGHSPEED" == speed:
                                usb20_flag = +1
                            elif "DevIsOpAtSsOrHigher" in line and\
                                    "1" in line and "SUPERSPEED" == speed:
                                usb30_flag = +1
                            elif "DevIsSsCapOrHigher" in line and\
                                    "1" in line and "HIGHSPEED" == speed:
                                usb20_flag = +1
                            elif "DevIsOpAtSsPlusOrHigher" in line and \
                                    "1" in line and "SUPERSPEEDPLUS" == speed:
                                usb31_flag = +1
                            elif "DevIsSsPlusCapOrHigher" in line and \
                                    "1" in line and "SUPERSPEED" == speed:
                                usb30_flag = +1
                            elif "DevIsSsPlusCapOrHigher" in line and \
                                    "1" in line and "HIGHSPEED" == speed:
                                usb20_flag = +1
                            else:
                                pass
                            if "bcdUSB" in line:
                                usb_version = line.split(":")[1].split(" ")[1]

            return usb20_flag, usb30_flag, usb31_flag, usb_version

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #Writing exception message to the log file
        return False

################################################################################
# Function Name : get_usb_view_log
# Parameters    : usbview_path, usbview_log, usbview_exe, usbview_cli,
#                 test_case_id, script_id, log_level and tbd
# Functionality : to generate the usb view log
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def get_usb_view_log(usbview_path, command, test_case_id, script_id,
                     log_level="ALL", tbd=None):

    try:
        os.chdir(usbview_path)
        subprocess.Popen(command,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        time.sleep(lib_constants.FIVE_SECONDS)                                  #Sleep for the tool to complete run if it takes time
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #Writing exception message to the log file

################################################################################
# Function Name : get_usb_tree_view_log
# Parameters    : usb_tree_view, test_case_id, script_id, log_level and tbd
# Functionality : to generate the usbtree view log
# Return Value  : True on successful action, False otherwise
################################################################################


def get_usb_tree_view_log(tooldir, usb_tree_view, test_case_id, script_id,
                          log_level, tbd):

    try:
        script_log_path = lib_constants.SCRIPTDIR + '\\' + \
                          script_id.replace(".py", ".txt")                      #Appending Script directory and log file
        if os.path.exists(script_log_path):
            os.remove(script_log_path)

        os.chdir(tooldir)
        command = usb_tree_view + " /R:" + os.path.join(script_log_path)
        cmd_exe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE)                    #Executing command to get the usbtree_view log file

        time.sleep(lib_constants.FIVE_SECONDS)                                  #Delay for five seconds

        if "" != cmd_exe.communicate()[0]:                                      #Failed to execute the command
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "run the command for to get the UsbTreeView "
                              "log", test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #Writing log warning message to the log file
            return False, ""
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Command for to "
                              "get the UsbTreeView log ran successfully",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #Writing log_info message to the log file
            return True, script_log_path
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #Writing exception message to the log file
        return False

################################################################################
# Function Name : verify_usb_modes_presi
# Parameters    : token, test_case_id, script_id, log_level and tbd
# Functionality : Verify usb type variable
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def verify_usb_modes_presi(token, test_case_id, script_id, log_level="ALL",
                           tbd=None):

    try:
        token_list = token.split(' ')
        usb_type, pos = \
            utils.extract_parameter_from_token(token_list, "CHECK", "AS",
                                               log_level, tbd)                  #Extract the usb type from the token
        if "IN" in token_list:
            speed, pos_speed = \
                utils.extract_parameter_from_token(token_list, "AS", "IN",
                                                   log_level, tbd)              #Extract the speed from the token if system is specified
        else:
            speed, pos_speed = \
                utils.extract_parameter_from_token(token_list, "AS", "",
                                                   log_level, tbd)              #Extract the speed from the token if system is not specified

        usb2_flag, usb3_highflag, usb3_superflag = \
            verify_usb_log_presi(test_case_id, script_id, log_level, tbd)       #Library call to get the type of usb connected and their respective speeds

        if "USB2.0" in usb_type and usb2_flag != 0:                             #If USB2.0 in token and usb2 is connected to system
            library.write_log(lib_constants.LOG_INFO, "INFO: %s detected as %s"
                              % (usb_type, speed), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        elif "USB3.0" in usb_type and speed == "HIGHSPEED" and \
             usb3_highflag != 0:                                                #If usb3.0 in token and the pendrive connected to the system is highspeed
            library.write_log(lib_constants.LOG_INFO, "INFO: %s detected as %s"
                              % (usb_type, speed), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        elif "USB3.0" in usb_type and speed == "SUPERSPEED" and\
             usb3_superflag != 0:                                               #If usb3.0 in token and the pendrive connected to the system is superspeed
            library.write_log(lib_constants.LOG_INFO, "INFO: %s detected as %s"
                              % (usb_type, speed), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        elif "WINUSB" == usb_type:
            if "HIGHSPEED" == speed and (usb3_highflag != 0 or usb2_flag != 0):
                library.write_log(lib_constants.LOG_INFO, "INFO: %s is detected"
                                  " as %s" % (usb_type, speed), test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            elif "SUPERSPEED" == speed and usb3_superflag != 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s is detected"
                                  " as %s" % (usb_type, speed), test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is "
                                  "not detected as %s" % (usb_type, speed),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
        else:                                                                   #else no usb pendrive detected in system
            library.write_log(lib_constants.LOG_WARNING, "WARNING: No USB "
                              "pendrive detected in system", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : verify_usb_log_presi
# Parameters    : test_case_id, script_id, log_level and tbd
# Functionality : Verify usb type variable
# Return Value  : returns counter values for different modes of usb
################################################################################


def verify_usb_log_presi(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        log_file = script_id.replace(".py",
                                     ".txt")                                    # Replacing the script id with ".txt" extension
        log_path = lib_constants.SCRIPTDIR + "\\" + log_file                    # Appending log file to the script directory

        if os.path.exists(log_path):
            os.remove(log_path)                                                 # Removing the log file form defined path

        if "64" in platform.uname()[4]:                                         # if Platform is 64 bit
            command = lib_constants.USBVIEW_PATH + "\\" + "x64" + "\\" +\
                      lib_constants.USBVIEW_SETUP + \
                      " /f /q /saveall:" + log_path                             # Appending the command
        else:
            command = lib_constants.USBVIEW_PATH + "\\" + "x86" + "\\"\
                      + lib_constants.USBVIEW_SETUP + \
                      "/f /q /saveall:" + log_path                              # Appending the command

        if get_usb_view_log(lib_constants.USBVIEW_PATH, command, test_case_id,
                            script_id, log_level="ALL",
                            tbd=None):                                          # Function call for to generate log
            pass
        else:
            return False

        os.chdir(lib_constants.SCRIPTDIR)
        usb2flag, usb3_highflag, usb3_superflag, usb3_superplus = 0, 0, 0, 0

        with codecs.open(os.path.join(usbview_path, usbview_log), "r") as \
                file:                                                           #File operation
            for line in file:
                if "High-Speed mass storage 2.0" in line or \
                   "USB 3.0 Disk" in line:                                      #Search for USB  mass storage device
                    for i in range(lib_constants.ITERATE1):                     #Iterate in range of lines
                        line = next(file)
                        if "Vtech Turbo_Disk(tm) USB Device" in line:
                            for temp in range(lib_constants.ITERATE3):          #Iterate in the range of lines
                                line = next(file)
                                if "USB Version       : 3.00" in line:          #Check for "USB Version       : 3.00" (usb3)
                                    usb3_highflag += 1                          #If found high flag is 1
                                    break
                                elif "USB Version       : 2.00" in line:        #Check for "USB Version       : 2.00" (usb2)
                                    usb2flag += 1                               #If found high flag is 1
                                    break
                                else:
                                    pass
                        else:
                            if usb2flag or usb3_highflag:
                                break
                            else:
                                pass
                else:
                    pass
        return usb2flag, usb3_highflag, usb3_superflag                          #Returns count of usb2, usb3 with highspeed and usb3 with superspeed flags
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
