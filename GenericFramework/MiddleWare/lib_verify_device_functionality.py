__author__ = r'patnaikx/nareshgx/hvinayx/sushil3x/kashokax/surabh1x/tnaidux'

# General Python Imports
import codecs
import cv2
import io
import msvcrt
import os
import pyautogui
import serial
import shutil
import subprocess
import time
import wmi
import win32api
import win32con
import win32gui
import numpy as np
from subprocess import PIPE
from win32api import GetSystemMetrics

# Local Python Imports
import lib_constants
import library
import utils
import lib_boot_to_environment
import lib_set_bios
import lib_read_bios
import lib_perform_g3
import lib_connect_disconnect_power_source
import lib_press_button_on_board
import lib_plug_unplug
import lib_sensorviewer
import KBM_Emulation as kbm
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations
# Global Variables
flag = ""

################################################################################
# Function Name : press_keys
# Parameters    : input_device, env, tc_id, script_id, log_level, tbd
# Functionality : checks keyboard press functionality in OS, BIOS and EFI
# Return Value  : returns True on success and Fail otherwise
################################################################################


def press_keys(input_device, env, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if input_device.upper()== "PS2-KEYBOARD":
            port = utils.ReadConfig("BRAINBOX", "PORT")
            if "FAIL:" in port:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get "
                                  "brain box port details from Config.ini under"
                                  " tag [BRAINBOX] and variable PORT", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Port for brain"
                                  " box is identified as %s from config.ini"
                                  % port, tc_id, script_id, "None", "None",
                                  log_level, tbd)

            if "OS" == env:
                kb_obj = library.KBClass(port)                                  # kb_obj object of KBClass
                kb_obj.combiKeys("Win+r")                                       # Send combination keys of (Windows+r)
                kb_obj.sendWithEnter("notepad")                                 # Type notepad and press enter

                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter"
                                  " key press is triggered so as to open "
                                  "notepad in the SUT", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            elif "BIOS" == env:
                kb_obj = library.KBClass(port)                                  # kb_obj object of KBClass
                kb_obj.whiteKeys("N")                                           # Press key N for the pop-up in the first bios page
                kb_obj.whiteKeys("Up_arrow")                                    # Press up arrow to move selection to reset and press enter
                kb_obj.whiteKeys("Enter")

                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter"
                                  " key press is triggered so as to boot SUT "
                                  "back to OS", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            elif "EFI" == env:
                kb_obj = library.KBClass(port)                                  # kb_obj object of KBClass
                kb_obj.sendWithEnter("bcfg boot mv 1 0")                        # Press key N for the pop-pu in the first bios page
                kb_obj.sendWithEnter("reset")                                   # Press up arrow to move selection to reset and press enter

                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter"
                                  " key press is triggered so as to return SUT "
                                  "to OS from EFI", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: The parameter "
                                  "%s is not valid" % env, tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        else:
            input_device_name = utils.ReadConfig("KBD_MOUSE",
                                                 "KEYBOARD_MOUSE_DEVICE_NAME")  # Extract input device name from config.ini
            port = utils.ReadConfig("KBD_MOUSE", "PORT")                        # Extract com port details from config.ini

            if "FAIL:" in port or "FAIL:" in input_device_name:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get com port details or input device "
                                  "name from Config.ini", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                                  "input device name is identified as is "
                                  "identified as %s %s from config.ini"
                                  % (port, input_device_name), tc_id,
                                  script_id, "None", "None", log_level, tbd)

            if "OS" == env:
                kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)       # kb_obj object of USBKbMouseEmulation class
                kb_obj.key_press("KEY_GUI")                                     # Press windows button
                kb_obj.key_press("KEY_ENTER")                                   # Press enter
                kb_obj.key_type("run")                                          # Send run command
                kb_obj.key_press("KEY_ENTER")                                   # Press enter
                kb_obj.key_press("KEY_BACKSPACE")                               # Press backspace
                kb_obj.key_type("notepad")                                      # Send notepad
                kb_obj.key_press("KEY_ENTER")                                   # Press enter

                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter"
                                  " key press is triggered so as to open "
                                  "notepad in the SUT", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            elif "BIOS" == env:
                kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)       # kb_obj object of USBKbMouseEmulation class
                for _ in range(lib_constants.TEN):
                    kb_obj.key_press("KEY_ESC")                                 # Press key ESC more times for back to the bios home page
                    time.sleep(lib_constants.SEND_KEY_TIME)
                kb_obj.key_press("KEY_UP")                                      # Press up arrow to move selection to reset and press enter
                kb_obj.key_press("KEY_ENTER")
                kb_obj.key_type("N")                                            # Enter 'N' to discard changes if pop-up a dialog
                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                  "enter key press is triggered so as to boot "
                                  "SUT back to OS", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            elif "EFI" == env:
                kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)       # kb_obj object of USBKbMouseEmulation
                kb_obj.key_type(lib_constants.SET_BOOT_ORDER_CMD)               # Send set boot order bcfg boot mv 1 0
                kb_obj.key_press("KEY_ENTER")                                   # Press enter
                kb_obj.key_type("reset")                                        # Send reset
                kb_obj.key_press("KEY_ENTER")                                   # Press enter

                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter"
                                  " key press is triggered so as to return SUT "
                                  "to OS from EFI", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: The parameter "
                                  "%s is not valid" % env, tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : file_transfer
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : checks whether file transfer is possible with given device
# Return Value  : returns True on success and False otherwise
################################################################################

def file_transfer(device, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if "NVME-SSD" in device.upper():                                        #if device is NVME_SSD
            nvme_device_name = utils.ReadConfig("DEVICE_FN","nvme_ssd_name")    #read the device name from config file
            device_name = utils.ReadConfig("DEVICE_FN","USB-DEVICE")            #read the target device from config file
            if "FAIL:" in [nvme_device_name ,device_name ]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to read the config entry from config file ", tc_id, script_id,
                                  "None", "None", log_level, tbd)               #write fail message to log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "read successfully from config file ", tc_id, script_id, "None",
                                  "None", log_level, tbd)                       #write pass message to log file

            os.chdir(lib_constants.DEVCON_PATH)                                 #change current working directory to devcon tool path
            cmd = lib_constants.FIND_ALL_DEVICE_LIST_CMD                        #read the command to get the device info from device manager
            cmd_to_run = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE, shell=True)

            if "" != cmd_to_run.communicate()[0]:                               #executes command to generate log and verifies whether the command is executed successfully
                library.write_log(lib_constants.LOG_WARNING,"WARNING: Failed to"
                " execute command to generate log using devcon tool", tc_id,
                                  script_id, "None", "None", log_level, tbd)    #write fail message to log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Command "
                "executed successfully to generate log using devcon tool", tc_id
                                  , script_id, "None", "None", log_level, tbd)  #write pass message to log file


            flag_device = False

            if os.path.exists('devices.txt'):                                   #check if the log exist after executing command
                with open("devices.txt","r") as file:                           #read the contents of log file
                    for line in file:
                        if nvme_device_name in line.upper():                    #confirm if the bootable device used is nvme-ssd
                            line = line.split(":")[-1].strip()
                            if line == nvme_device_name:
                                flag_device = True                              #write true value to flag_device and break from the loop if nvme-ssd config entry is found in the line
                                os.chdir(lib_constants.SCRIPTDIR)               #change current working directory to script directory
                                break
                            else:
                                flag_device = False

            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to generate the device list log file", tc_id, script_id,
                                  "None", "None", log_level, tbd)               #write fail message to log file
                return False

            if True == flag_device:                                             #confirms nvme-ssd is the booting device
                library.write_log(lib_constants.LOG_INFO,"INFO: NVME-SSD is "
                "found as bootable device", tc_id, script_id, "None", "None",
                                  log_level, tbd)                               #write message to log file if nvme-ssd is found as bootable device
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry is found incorrect or nvme-ssd is not plugged in", tc_id,
                                  script_id, "None", "None", log_level, tbd)    #write fail message to log file
                return False

        else:
           device_name = utils.ReadConfig("DEVICE_FN", device)

           if "FAIL" in device_name:
               library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to"
               " get drive name from Config.ini under tag [DEVICE_FN] and "
               "variable %s" %device, tc_id, script_id, "None", "None",
                                 log_level, tbd)                                #Failed to get info from config file
               return False

           else:
               library.write_log(lib_constants.LOG_INFO, "INFO: Drive name is "
                "fetched as %s from config.ini" % device_name, tc_id, script_id,
                                  "None", "None",log_level, tbd)

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e, tc_id,
        script_id, "None", "None", log_level, tbd)                              #Failed to get info from config file
        return False

    try:
        command = lib_constants.LOGICAL_DISK_CMD
        data = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdin=subprocess.PIPE)  # Get the drive details with wmic query
        device_list = data.communicate()[0]
        devices = str(device_list).split("\\r\\r\\n")                                   # Remove tabs and new lines

        flag = False
        drive_letter = None
        for item in devices:                                                    # Check for the drive name in the wmic output
            if device_name.lower() in item.lower():
                flag = True
                drive_letter, key, after_key = item.partition(":")              # Get the drive letter from the line
                break
            else:
                pass

        if flag:                                                                # Pass
            library.write_log(lib_constants.LOG_INFO, "INFO: Device enumerated "
                                                      "as drive %s:"
                              % drive_letter, tc_id, script_id, "None", "None",
                              log_level, tbd)

        else:                                                                   # Device not found as storage space
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Device is "
            "not available as storage (logical drive)", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e, tc_id,
        script_id, "None", "None", log_level, tbd)                              #Failed to get info from config file
        return False

    try:
        new_file = open("Test.txt", "w")
        new_file.write("Test file with test line")
        new_file.close()                                                        # Create a sample file
        command_src_dst = lib_constants.COPY_CMD + str(os.path.join(os.getcwd(),
            "Test.txt")) + " " + str(drive_letter) + ":\\"
        subprocess.Popen(command_src_dst, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)         #Get the drive details with wmic query
        time.sleep(lib_constants.THREE)

        os.remove(str(os.path.join(os.getcwd(), "Test.txt")))                   #Remove sample file from source

        command_dst_src = lib_constants.COPY_CMD + str(drive_letter) + \
                          ":\\Test.txt "+ os.getcwd()
        subprocess.Popen(command_dst_src, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)         #Get the drive details with wmic query
        time.sleep(lib_constants.THREE)

        if os.path.exists(os.path.join(os.getcwd(), "Test.txt")) and \
           os.path.exists(str(drive_letter) + ":\\Test.txt"):
            library.write_log(lib_constants.LOG_INFO, "INFO: File operation is "
            "successful across the device", tc_id, script_id, "None", "None",
                              log_level, tbd)                                   # File operation in successful, if its available in both source and destinatoin
            return True

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: File "
            "operation failed across the device", tc_id, script_id, "None",
                              "None", log_level, tbd)                           # Failed to transfer file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        tc_id, script_id, "None", "None", log_level, tbd)                       #Exception
        return False

################################################################################
# Function Name : press_key_host
# Parameters    : input_device, env, tc_id, script_id, log_level and tbd
# Functionality : checks keyboard triggering through Host
# Return Value  : returns True on success and Fail otherwise
################################################################################


def press_key_host(input_device, env, tc_id, script_id, log_level="ALL",
                   tbd=None):

    try:
        time.sleep(lib_constants.KEYPRESS_WAIT_HOST)

        if input_device == "PS2-KEYBOARD":
            kb_enter = utils.ReadConfig("TTK", "KB_ENTER_PS2")                  # Fetching ps2 keyboard enter key port number from TTK
        else:
            kb_enter = utils.ReadConfig("TTK", "KB_ENTER")                      # Fetching keyboard enter key port number from TTK

        if "FAIL:" in kb_enter:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry for KB_ENTER from config.ini",
                              tc_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard enter "
                              "key is connected to relay : %s" % kb_enter,
                              tc_id, script_id, "None", "None", log_level, tbd)

            for i in range(lib_constants.THREE):                                # Iterating ttk on/off loop for 5 times
                press = library.ttk_set_relay("ON", int(kb_enter), tc_id,
                                              script_id, log_level, tbd)        # Return pass/fail for TTK "ON"
                release = library.ttk_set_relay("OFF", int(kb_enter), tc_id,
                                                script_id, log_level, tbd)      # Return pass/fail for TTK "OFF"

                if 0 == press and 0 == release:                                 # If both TTK press/release successfully done
                    library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                      "enter key pressed and released for %d "
                                      "times successfully in %s" % (i+1, env),
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to press & release Keyboard "
                                      "enter key", tc_id, script_id, "None",
                                      "None", log_level, tbd)
                    return False
                time.sleep(lib_constants.TWO)
            return True
    except Exception as e:                                                      # Exception handling for TTK operation
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : press_key_host_presi
# Parameters    : env, tc_id, script_id, loglevel, tbd
# Functionality : checks keyboard triggering through Host
# Return Value  : returns True on success and Fail otherwise
################################################################################

def press_key_host_presi(env, test_case_id, script_id, log_level="ALL",
                         tbd=None):
    try:
        time.sleep(lib_constants.THREE)                                         # Sleep time for 3 seconds to make sure command prompt window is opened in sut
        process = subprocess.Popen(lib_constants.ACTIVATE_SIMICS_WINDOW,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)                       # Executing app_activation_has utility
        stdout, stderr = process.communicate()                                  # Getting command output and error information
        if len(stderr) > 0:                                                     # If any error found in executing exe
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "activate simics console window", test_case_id, script_id,
                log_level, tbd)
                return False                                                    # Function exists by Returning False if error occurs in activating simics console
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "activated simics console window", test_case_id, script_id,
                log_level, tbd)
            time.sleep(lib_constants.THREE)                                     # Wait for 3 seconds before the simics console is activated
            process = subprocess.Popen(lib_constants.MOUSE_DOUBLE_CLICK,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)                   # Executing double_click_mouse utility
            stdout, stderr = process.communicate()                              # Getting command output and error information
            if len(stderr) > 0:                                                 # If any error found in sending mouse double click
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "send double click to simics console window", test_case_id,
                    script_id, log_level, tbd)
                    return False                                                # Function exists by Returning False if error occurs in sending mouse_click signals
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "sent double click to simics console window", test_case_id,
                script_id, log_level, tbd)
                time.sleep(lib_constants.THREE)                                 # Wait for 3 seconds  before the commands are in sut command prompt
                pyautogui.press('enter')                                        # Send enter to simics console
                return True                                                     # Returns true if Keypress is sent

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "sending key signal to simics setup:%s"%e, test_case_id, script_id,
        "None", "None", log_level, tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : trigger_mouse_host_presi
# Parameters    : env, test_case_id, script_id, loglevel, tbd
# Functionality : checks keyboard press functionality in OS, BIOS and EFI
# Return Value  : returns True on success and Fail otherwise
################################################################################


def trigger_mouse_host_presi(env, test_case_id, script_id, log_level="ALL",
                             tbd=None):
    try:
        if lib_boot_to_environment.simics_sendkeys((lib_constants.ACTIVATE_SIMICS_WINDOW)
                                            , ""):                              # Calling send keys function to send {ENTER} key
            time.sleep(lib_constants.TEN)
            width = int(GetSystemMetrics(0))/2                                  # Get center point of the total screen width
            height = int(GetSystemMetrics(0))/2                                 # Get center point of the total screen height
            library.write_log(lib_constants.LOG_INFO, "INFO: Activating Simics "
            "sut screen", test_case_id, script_id,log_level, tbd)
            pyautogui.click(width, height, button = 'left')                     # Mouse left button click at the center of the screen
            process = subprocess.Popen(lib_constants.MOUSE_DOUBLE_CLICK,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)                   # Executing double_click_mouse utility to grab the simics screen
            stdout, stderr = process.communicate()                              # Getting command output and error information
            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to send"
                "mouse click to simics setup", test_case_id, script_id,
                log_level, tbd)
                return False                                                    # Function exists by Returning False if error occurs in sending mouse_click signals
            else:
                for i in range(3):
                    pyautogui.click()                                           # Send mouse click for 3 times
                    time.sleep(lib_constants.TWO)                               # Sleep for 2 seconds
                library.write_log(lib_constants.LOG_INFO, "INFO: Mouse click "
                " sent to simics setup successfully",test_case_id, script_id,
                log_level, tbd)
                return True                                                     # Function exists by Returning True if mouse_click signal sent successfully

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "triggering mouse click:%s"%e, test_case_id, script_id, "NONE",
        "MOUSE_CLICK", log_level, tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : keypress_receiver
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : receive keyboard key press signal
# Return Value  : returns True on success and Fail otherwise
################################################################################


def keypress_receiver(tc_id, script_id, log_level="All", tbd=None):             # Code for  receiving key pressing signal
    finishat = time.time() + lib_constants.SIXTY_ONE
    result = []
    value = False
    while True:
        if msvcrt.kbhit():                                                      # If any key from keyboard pressed
            result.append(ord(msvcrt.getche()))
            if lib_constants.ENTER_ASCII == result[-1]:                         # Check for pressed key is "ENTER" or not
                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                                          "ENTER key pressed "
                                                          "successfully", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            time.sleep(lib_constants.POINT_ONE_SECONDS)
        else:
            if time.time() > finishat:                                          # Return false if time-out
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                                                          "press ENTER key "
                                                          "from keyboard",
                                  tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return value
################################################################################
# Function Name : enumhandler_maximize
# Parameters    : HWND, lparam
# Functionality : maximize the screen
################################################################################


def enumhandler_maximize(HWND, lparam):                                         # Code for maximizing a window
    if win32gui.IsWindowVisible(HWND):
        if lparam in win32gui.GetWindowText(HWND):
            win32gui.ShowWindow(HWND, win32con.SW_MAXIMIZE)

################################################################################
# Function Name : enumnandler_minimize
# Parameters    : HWND, lparam
# Functionality : minimize the screen
################################################################################


def enumhandler_minimize(HWND, lparam):                                         # Code for minimizing a window
    if win32gui.IsWindowVisible(HWND):
        if lparam in win32gui.GetWindowText(HWND):
            win32gui.ShowWindow(HWND, win32con.SW_MINIMIZE)


################################################################################
# Function Name : press_keyboard
# Parameters    : env, tc_id, script_id, log_level, tbd
# Functionality : checks keyboard press functionality in OS, BIOS and EFI
# Return Value  : returns True on success and Fail otherwise
################################################################################
def press_keyboard(env, tc_id, script_id, log_level="ALL", tbd=None):           # Code for keyboard press
    try:
        os.chdir(lib_constants.SCRIPTDIR)
        if os.path.exists("a.txt"):
            os.remove("a.txt")
        else:
            pass
        cmd = "start cmd"
        process = subprocess.Popen(cmd,shell=True, stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        time.sleep(lib_constants.ONE)                                           # Wait for one second
        win32gui.EnumWindows(enumhandler_maximize,"Administrator:")
        time.sleep(lib_constants.ONE)
        status = SendKeys("dir{SPACE}>{SPACE}a.txt{ENTER}")
        time.sleep(lib_constants.KEYPRESS_WAIT_SUT)
        status = SendKeys("exit")
        time.sleep(lib_constants.KEYPRESS_WAIT_SUT)
        if os.path.exists("a.txt"):
            return True
        else:
            return False


    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                                                   "pressing key from "
                                                   "keyboard", tc_id, script_id,
                          "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : draw_circle
# Parameters    : event, x, y co-ordinate, flags, param
# Functionality : receive mouse click
# Return Value  : returns True on success and False otherwise
################################################################################


def draw_circle(event, x, y, flags, param):                                     # Receive mouse click in a image window
    global flag
    if event == cv2.EVENT_LBUTTONDOWN:                                          # If left_click pressed
        flag = True
    elif event == cv2.EVENT_RBUTTONDOWN:                                        # If right click pressed
        flag = True
    elif event == cv2.EVENT_MOUSEWHEEL:                                         # If scroll pressed
        flag = True
    else:                                                                       # If no action
        flag = False

################################################################################
# Function Name : mouse_press
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : receive mouse click
# Return Value  : returns True on success and False otherwise
################################################################################


def mouse_press(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        img = np.zeros((GetSystemMetrics(1), GetSystemMetrics(0), 1),
                       np.uint8)                                                # Create a black image, a window and bind the function to window
        cv2.namedWindow('mouse receiver')
        timeout = time.time() + lib_constants.SIXTY_ONE
        win32api.SetCursorPos((lib_constants.CURSOR_POS_DEFAULT,
                               lib_constants.CURSOR_POS_DEFAULT))

        while(1):
            cv2.imshow('mouse receiver', img)                                   # Creating a mouse receiver windows
            win32gui.EnumWindows(enumhandler_maximize, "mouse receiver")        # Maximizing the mouse receiver windows
            cv2.setMouseCallback('mouse receiver', draw_circle)                 # Calling draw_circle for receiving mouse click

            if cv2.waitKey(20) & 0xFF == 27 or time.time() > timeout:           # If any left click received in time
                if flag is True:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Button "
                                      "clicked successfully from mouse",
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    cv2.destroyAllWindows()
                    win32api.SetCursorPos((lib_constants.CURSOR_POS,
                                           lib_constants.CURSOR_POS))
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to get click from mouse", tc_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    cv2.destroyAllWindows()
                    win32api.SetCursorPos((lib_constants.CURSOR_POS,
                                           lib_constants.CURSOR_POS))
                    return False
            elif flag is True:                                                  # If any mouse key clicked
                library.write_log(lib_constants.LOG_INFO, "INFO: Button "
                                  "clicked successfully from mouse", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                cv2.destroyAllWindows()
                win32api.SetCursorPos((lib_constants.CURSOR_POS,
                                       lib_constants.CURSOR_POS))
                return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : click_mouse
# Parameters    : env, tc_id, script_id, log_level, tbd
# Functionality : mouse functionality check
# Return Value  : returns True on success and False otherwise
################################################################################


def click_mouse(env, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        global flag                                                             # Set a global variable flag

        if mouse_press(tc_id, script_id, log_level, tbd):                       # If left-click received from mouse
            library.write_log(lib_constants.LOG_INFO, "INFO: Mouse click "
                              "validated successfully", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        else:                                                                   # If fail to receive left-click from mouse
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "validate mouse click", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : lib_verify_key_press_bios
# Parameters    : input_device, env, tc_id, script_id, log_level and tbd
# Functionality : keyboard functionality check
# Return Value  : returns True on success and False otherwise
################################################################################


def lib_verify_key_press_bios(input_device, env, tc_id, script_id,
                              log_level="ALL", tbd=None):

    if input_device.upper() == "PS2-KEYBOARD":
        port = utils.ReadConfig("BRAINBOX", "PORT")
        if "FAIL:" in port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get brain box port details from Config.ini "
                              "under tag [BRAINBOX] and variable PORT", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Port for brain "
                              "box is identified as %s from config.ini" % port,
                              tc_id, script_id, "None", "None", log_level, tbd)

        kb_obj = library.KBClass(port)                                          # kb_obj object of KBClass
        kb_obj.whiteKeys("Up_arrow")                                            # Press up arrow to move selection to reset and press enter
    else:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get com port details or input device name from "
                              "Config.ini ", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name is identified as %s and %s "
                              "from config.ini" % (port, input_device_name),
                              tc_id, script_id, "None", "None", log_level, tbd)
        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("KEY_ESC")                                             # Pressing Esc Key
        time.sleep(lib_constants.SEND_KEY_TIME)                                 # Sleep for 0.5 seconds
        kb_obj.key_press("KEY_UP")

    status = press_key_host(input_device, env, tc_id, script_id, log_level, tbd)
    if status:                                                                  #Press enter using TTK connected relay
        library.write_log(lib_constants.LOG_INFO, "INFO: %s Enter key pressed "
                          "in %s for to boot SUT to OS" % (input_device, env),
                          tc_id, script_id, "None", "None", log_level, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to press "
                          "%s Enter Key in %s" % (input_device, env), tc_id,
                          script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : lib_verify_key_press_efi
# Parameters    : input_device, env, tc_id, script_id, log_level and tbd
# Functionality : keyboard functionality check in EFI
# Return Value  : returns True on success and False otherwise
################################################################################


def lib_verify_key_press_efi(input_device, env, tc_id, script_id,
                             log_level="ALL", tbd=None):

    cur_os = lib_boot_to_environment.checkcuros(tc_id, script_id, log_level, tbd)        # Check whether system is in OS or EFI

    if "EDK SHELL" == cur_os:
        library.write_log(lib_constants.LOG_INFO, "INFO: System is in EDK "
                          "Shell", tc_id, script_id, "None", "None", log_level,
                          tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: System is not "
                          "in EDK Shell", tc_id, script_id, "None", "None",
                          log_level, tbd)
        return False

    if input_device.upper() == "PS2-KEYBOARD":
        port = utils.ReadConfig("BRAINBOX", "PORT")
        if "FAIL:" in port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get brain box port details from Config.ini "
                              "under tag [BRAINBOX] and variable PORT", tc_id,
                              script_id, "None", "None", log_level, tbd)        # Failed to get info from config file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Port for brain "
                              "box is identified as %s from config.ini" % port,
                              tc_id, script_id, "None", "None", log_level, tbd)
            kb_obj = library.KBClass(port)                                      # kb_obj object of KBClass
            kb_obj.sendWithEnter(lib_constants.SET_BOOT_ORDER_CMD)              # Send to set boot order bcfg boot mv 1 0
            kb_obj.longString("reset")                                          # Send reset
    else:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get com port details or input device name from "
                              "Config.ini", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name is identified as %s and %s "
                              "from config.ini" % (port, input_device_name),
                              tc_id, script_id, "None", "None", log_level, tbd)

            kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)
            kb_obj.key_type(lib_constants.SET_BOOT_ORDER_CMD)                   # Send set boot order bcfg boot mv 1 0
            kb_obj.key_press("KEY_ENTER")                                       # Send Enter key
            kb_obj.key_type("reset")                                            # Send Reset cmd

            library.write_log(lib_constants.LOG_INFO, "INFO: Change Boot order "
                              "command and reset send successfully through "
                              "Keyboard-Simulator", tc_id, script_id, "None",
                              "None", log_level, tbd)

    status = press_key_host(input_device, env, tc_id, script_id, log_level,
                            tbd)                                                # Function call for to press enter using TTK connected relay

    if status:
        library.write_log(lib_constants.LOG_INFO, "INFO: %s Enter key pressed "
                          "in %s for SUT to boot to OS" % (input_device, env),
                          tc_id, script_id, "None", "None", log_level, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to press "
                          "%s Enter Key in %s" % (input_device, env), tc_id,
                          script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : sendkeys_in_bios_presi
# Parameters    : test_case_id,script_id,log_level,tbd
# Functionality : keyboard functionality check in BIOS setup
# Return Value  : returns True on success and False otherwise
################################################################################

def sendkeys_in_bios_presi(test_case_id,script_id,log_level,tbd):
    try:
        tool = lib_constants.TOOLPATH+"\\simicssut.exe"                         # Getting tool path simics sendkeys utility
        time.sleep(lib_constants.THREE)
        if lib_boot_to_environment.simics_sendkeys(tool,"{UP}"):                         # Calling send keys function to send {UP} key
            time.sleep(lib_constants.TWO)
            if lib_boot_to_environment.simics_sendkeys(tool,"{UP}"):                     # Calling send keys function to send {UP} key
                time.sleep(lib_constants.TWO)
                if lib_boot_to_environment.simics_sendkeys(tool,"{ENTER}"):              # Calling send keys function to send {ENTER} key
                    library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                    "keys sent to simics setup successfully"
                    ,test_case_id, script_id, log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "send keyboard keys to simics setup", test_case_id,
                    script_id, log_level, tbd)
                    return False                                                # Function exists by Returning False if send keys are unsuccessful
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to send"
                    " keyboard keys to simics setup"
                    ,test_case_id, script_id, log_level, tbd)
                return False                                                    # Function exists by Returning False if send keys are unsuccessful
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to send"
                    " keyboard keys to simics setup"
                    ,test_case_id, script_id, log_level, tbd)
            return False                                                        # Function exists by Returning False if send keys are unsuccessful
        if lib_boot_to_environment.system_in_os(lib_constants.HUNDRED):
            library.write_log(lib_constants.LOG_INFO, "INFO: Simics "
                "setup booted to OS successfully from BIOS after Keyboard keypre"
                "ss" ,test_case_id, script_id, log_level, tbd)
            time.sleep(lib_constants.SIXTY_ONE)
            return True                                                         # Function exists by Returning True if setup is in OS
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: System boot to OS"
            "after keyboard keypress failed", test_case_id, script_id, log_level,
            tbd)
            return False                                                        # Function exists by Returning False if setup is not in OS

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "sending key signal to simics setup", test_case_id, script_id,
        "None", "None", log_level, tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : restart_from_state_presi
# Parameters    : env, test_case_id, script_id, loglevel, tbd
# Functionality : keyboard functionality check
# Return Value  : returns True on success and False otherwise
################################################################################


def restart_from_state_presi(env, test_case_id, script_id, loglevel, tbd):      # Function to restart the Simics Setup from BIOS/EFI states
    try:
        if "OS" == env:                                                         # Function to verify whether the Simics setup is in OS
            if lib_boot_to_environment.system_in_os(lib_constants.CURSOR_POS):           # Calling "lib_boot_to_environment.system_in_os"  to get the Simics Setup status
                library.write_log(lib_constants.LOG_INFO,"INFO: System booted "
                    "to OS successfully after restart ", test_case_id,
                     script_id, loglevel, tbd)
                return True                                                     # Function exists by returning True if Simics setup is in OS
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to boot "
                    "the system to OS after restart ", test_case_id,
                     script_id, loglevel, tbd)
                return False                                                    # Function exists by returning False if Simics setup is not in OS
        elif "BIOS" == env:                                                     # Function to restart the Simics setup from BIOS Setup
            if lib_boot_to_environment.boot_from_bios(test_case_id, script_id,
                                            loglevel, tbd):                     # Calling "lib_boot_to_environment.boot_from_bios"  to boot the Simics Setup from BIOS
                library.write_log(lib_constants.LOG_INFO,"INFO: System booted "
                    "to OS successfully from BIOS ", test_case_id,
                     script_id, loglevel, tbd)
                return True                                                     # Function exists by returning True if Simics setup is in OS after rebooting from BIOS Setup
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to boot "
                    "the system to OS from BIOS ", test_case_id,
                     script_id, loglevel, tbd)
                return False                                                    # Function exists by returning False if Simics setup is not in OS after rebooting from BIOS Setup
        elif "EFI" == env:                                                      # Function to restart the Simics setup from EFI SHELL
            if lib_boot_to_environment.boot_from_efi(test_case_id, script_id,
                                            loglevel, tbd):                     # Calling "lib_boot_to_environment.boot_from_efi"  to boot the Simics Setup from EFi SHELL
                library.write_log(lib_constants.LOG_INFO,"INFO: System booted "
                    "to OS successfully from EFI Shell ", test_case_id,
                     script_id, loglevel, tbd)
                return True                                                     # Function exists by returning True if Simics setup is in OS after rebooting from EFI SHELL
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to boot "
                    "the system to OS from EFI Shell ", test_case_id,
                     script_id, loglevel, tbd)
                return False                                                    # Function exists by returning FALSE if Simics setup is not in OS after rebooting from EFI SHELL
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Unable to find"
                    "the system state", test_case_id, script_id, loglevel, tbd)
            return False                                                        # Function exists by returning False if input state is other than OS/BIOS/EFI
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Booting to OS from"
                    " %s failed"%env, test_case_id, script_id, "None", "None",
                     loglevel, tbd)
        return False                                                            # Function exists by returning False when exception arises out

################################################################################
# Function Name : file_transfer_presi
# Parameters    : device, tc_id, script_id, log_level, tbd
# Functionality : checks whether file transfer is possible with given device
# Return Value  : returns True on success and False otherwise
################################################################################

def file_transfer_presi(device, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        flag = False
        config_entry = device + "_DEVICE-NAME"
        device_name1 = utils.ReadConfig("PLUG_UNPLUG", config_entry)
        cmd = lib_constants.DRIVE_NAME                                          # Command to get the list of drive names
        subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)                                        # Run wmic command
        time.sleep(lib_constants.TEN_SECONDS)
        with codecs.open("drive.txt",'r',"utf-16") as f:                        # Open drive.txt from sript directory
            for line in f:
                if "E:" in line:                                                # Verify if Drive E is available in the drive.txt
                    library.write_log(lib_constants.LOG_INFO, "INFO:Logical disk"
                    " detected succesfully", tc_id, script_id, "None","None",
                    log_level,tbd)
                    flag = True                                                 # Assign flag as true
                    break

        if False == flag and  ("USB3.0-PENDRIVE" or "USB2.0-PENDRIVE" in \
                lib_constants.WMI_CHECK_PRESI):                                 # Check for device if it is  listed as device manager enumerated
            c = wmi.WMI()
            for devices in c.Win32_PnPEntity():
                if devices.Name is not None:                                    # Get list of device names from device manager
                    if device_name1.upper() == devices.Name.upper():            # If device found in device manager list
                        command = lib_constants.CREATE_DISK_PRESI               # Command to create new logical drive
                        create_disk = subprocess.Popen(command,stdout=PIPE,     # Run create disk command
                                                       stderr=PIPE)
                        stdout, stderr = create_disk.communicate()              # Get error message if found any while running the command
                        if "No usable free extent could be found" in stdout:    # If the given sentence is found in stdout assign drive letter
                            command = lib_constants.ASSIGN_DRIVE_PRESI
                            assign_disk = subprocess.Popen(command,stdout=PIPE, # Run assign letter command if already Disk is present to assign letter to drive.
                                                           stderr=PIPE)
                        else:
                            library.write_log(lib_constants.LOG_INFO, "INFO:Logi"
                            "cal disk created succesfully", tc_id, script_id,
                            "None", "None", log_level,tbd)                      # Write to log file
                        time.sleep(lib_constants.SLEEP_TIME)                    # Calling create_disk command to create logical drive
                    else:
                        pass

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:Logical "
            "disk already created succesfully ", tc_id, script_id, "None", "None",
                                log_level, tbd)                                 # If already logical disk is found

        time.sleep(lib_constants.TEN_SECONDS)
        device_name = utils.ReadConfig("DEVICE_FN", device)
        if "FAIL" in device_name:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get "
                                                      "drive name from "
                                                      "Config.ini under tag "
                                                      "[DEVICE_FN] and "
                                                      "variable %s" % device,
                              tc_id, script_id, "None", "None", log_level, tbd) # Failed to get info from config file
            return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Drive name is "
                                                      "fetched as %s from "
                                                      "config.ini"
                              % device_name, tc_id, script_id, "None", "None",
                              log_level, tbd)

    except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                                                       "getting config entry:"%e,
                              tc_id, script_id, "None", "None", log_level, tbd) # Failed to get info from config file
            return False

    try:
        command = lib_constants.LOGICAL_DISK_CMD
        data = subprocess.Popen(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)                         # Get the drive details with wmic query
        device_list = data.communicate()[0]
        devices = device_list.split("\r\r\n")                                   # Remove tabs and new lines

        flag = False
        drive_letter = None
        for item in devices:                                                    # Check for the drive name in the wmic output
            if " " + device_name.lower() + " " in item.lower():
                flag = True
                drive_letter, key, after_key = item.partition(":")              # Get the drive letter from the line
                break
            else:
                pass

        if flag:                                                                # Pass
            library.write_log(lib_constants.LOG_INFO, "INFO: Device enumerated "
                                                      "as drive %s:"
                              % drive_letter, tc_id, script_id, "None", "None",
                              log_level, tbd)

        else:                                                                   # Device not found as storage space
            library.write_log(lib_constants.LOG_INFO, "INFO: Device is not "
                                                      "available as storage "
                                                      "(logical drive)", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                                                   "checking drive list "
                                                   "entries", tc_id, script_id,
                          "None", "None", log_level, tbd)                       #failed to get info from config file
        return False

    try:
        new_file = open("Test.txt", "w")
        new_file.write("Test file with test line")
        new_file.close()                                                        #create a sample file
        command_src_dst = "xcopy /i /y " + str(os.path.join(os.getcwd(),
            "Test.txt")) + " " + str(drive_letter) + ":\\"
        data = subprocess.Popen(command_src_dst, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)                         # Get the drive details with wmic query
        stdout, stderr = data.communicate()                                     # Getting command output and error information
        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to run the "
            "xcopy command for source to destination", tc_id, script_id,
            log_level, tbd)
            return False                                                        # Function exists by Returning False if error occurs in executing xcopy command
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Xcopy command execu"
            "ted successfully", tc_id, script_id, log_level, tbd)
        os.remove(str(os.path.join(os.getcwd(), "Test.txt")))                   # Remove sample file from source
        command_dst_src = "xcopy /i /y " + str(drive_letter) + ":\\Test.txt " \
                          + os.getcwd()
        data = subprocess.Popen(command_dst_src, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)                         # Get the drive details with wmic query
        stdout, stderr = data.communicate()                                     # Getting command output and error information
        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to run the "
            "xcopy command for destination to source", tc_id, script_id,
            log_level, tbd)
            return False                                                        # Function exists by Returning False if error occurs in sending mouse_click signals
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Xcopy command execu"
            "ted successfully", tc_id, script_id, log_level, tbd)
        if os.path.exists(os.path.join(os.getcwd(), "Test.txt")) and \
           os.path.exists(str(drive_letter) + ":\\Test.txt"):
            library.write_log(lib_constants.LOG_INFO, "INFO: File transfer is "
                                                      "successful across the "
                                                      "device", tc_id,
                              script_id, "None", "None", log_level, tbd)        # File operation in successful, if its available in both source and destination
            return True

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: File operation "
                                                      "failed across the "
                                                      "device", tc_id,
                              script_id, "None", "None", log_level, tbd)        # Failed to transfer file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in file "
                                                   "transfer and checking "
                                                   "device functionality",
                          tc_id, script_id, "None", "None", log_level, tbd)     # Exception
        return False



################################################################################
# Function Name         : verify_home_button
# Parameters            : token, tc_id, script_id
# Target                : host
# Syntax                : Verify home-button functionality
# Implemented Parameters: home-button
################################################################################
def verify_home_button(tc_id, script_id, log_level = "ALL",
                               tbd = None):                                     # Function to verify the home button
    try:
        time.sleep(lib_constants.KEYPRESS_WAIT_HOST)
        home_button = utils.ReadConfig("TTK", "HOME")                           # Fetching Home button port number from TTK
        if "FAIL:" in home_button:
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Config "
                "entry for home_button is not found", tc_id,
                          script_id, "TTK", "Home_button", log_level, tbd)      # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Home button "
                    "is connected to relay : %s " % (home_button), tc_id,
                    script_id, "TTK","Home_Button_port: %s" % home_button,
                              log_level, tbd)
        press = library.ttk_set_relay("ON", [int(home_button)])                 # Return pass/fail for TTK "ON"
        time.sleep(1)
        release = library.ttk_set_relay("OFF", [int(home_button)])              # Return pass/fail for TTK "OFF"
        if 0 == press and 0 == release:                                         # If both TTK press/release successfully done
            library.write_log(lib_constants.LOG_INFO, "INFO: Home Button "
                    "pressed and released successfully ",tc_id,script_id, "TTK",
                    "Home_button_port: %s" %home_button,log_level,tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING,"WARNING: Home "
                    "button press and release got failed", tc_id,
                    script_id, "TTK", "Home_Button_port: %s"% home_button,
                    log_level, tbd)

            return False

        kvm_name = utils.ReadConfig("kvm_name","name")                          # KVM is read from the config file
        sikuli_path = utils.ReadConfig("sikuli","sikuli_path")                  # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli","sikuli_exe")                    # Sikuli exe name fetched from config file
        for item in  [kvm_name, sikuli_path, sikuli_exe]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO :config entry is"
                " missing for tag name :kvm_name or sikuli_path or sikuli_exe",
                tc_id,script_id,"None","None",log_level,tbd)
                return False                                                    # If the readconfig function returned fail it means no config entry is given
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Config entry is"
                " missing for tag name :kvm_name or sikuli_path or sikuli_exe",
                tc_id,script_id,"None","None",log_level,tbd)
                pass

        sikuli_cmd_for_windows_button = " Windows_functionality.skl"
        os.chdir(os.getcwd())
        time.sleep(lib_constants.SIKULI_EXECUTION_TIME)
        kvm_title = utils.ReadConfig("kvm_name","kvm_title")
        title = kvm_name + " - "+ kvm_title                                     # KVM command for activating the kvm window
        activate_path = utils.ReadConfig("sikuli","Activexe")
        window_path = activate_path + " " + title


        cur_state = lib_boot_to_environment.checkcuros(log_level,tbd)                    # Checking current state of the system by ping
        if "OS" == cur_state:                                                   # If the current state is OS
            library.write_log(lib_constants.LOG_INFO, "INFO: Activating KVM "
            "Window", tc_id, script_id,log_level, tbd)
            kvm_activate = subprocess.Popen(window_path , stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)                             # KVM window is activated from the host
                                                                                # Executing double_click_mouse utility to grab the simics screen
            stdout, stderr = kvm_activate.communicate()                         # Getting command output and error information
            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to activ"
                "ate KVM window", tc_id, script_id, log_level, tbd)
                return False                                                    # Function exists by Returning False if error occurs in activating simics window
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: KVM window "
                "activated successfully", tc_id, script_id,
                log_level, tbd)
            os.chdir(sikuli_path)
            cmd_for_win_button = sikuli_exe + sikuli_cmd_for_windows_button     # Sikuli command to verify the home button
            Sikuli_execution = subprocess.Popen(cmd_for_win_button ,
                                shell = False,stdout=subprocess.PIPE)           # Executes the Sikuli file for verifying the home button
            output = Sikuli_execution.stdout.read()
            flag1 = True
            flag2 = True
            if "found windows button" in output:
                library.write_log(lib_constants.LOG_INFO,"INFO : Verified "
                "home-button functionality",tc_id,script_id,"None","None"
                ,log_level,tbd)
                flag1 = True                                                      # Returns True if the home button functionality is verified succesfully
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Verifying home-"
                "button Functionality failed",tc_id,script_id,"None","None",
                log_level,tbd)
                flag1 = False                                                   # Returns False if failed to verify home button functionality

            time.sleep(lib_constants.KEYPRESS_WAIT_HOST)
            home_button = utils.ReadConfig("TTK", "HOME")                       # Fetching Home button port number from TTK
            if "FAIL:" in home_button:
                library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Config "
                    "entry for home_button is not found", tc_id,
                              script_id, "TTK", "Home_button", log_level, tbd)  # If failed to get config info, exit
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Home button "
                        "is connected to relay : %s " % (home_button), tc_id,
                        script_id, "TTK","Home_Button_port: %s" % home_button,
                                  log_level, tbd)
            press = library.ttk_set_relay("ON", [int(home_button)])             # Return pass/fail for TTK "ON"
            time.sleep(1)
            release = library.ttk_set_relay("OFF", [int(home_button)])          # Return pass/fail for TTK "OFF"
            if 0 == press and 0 == release:                                     # If both TTK press/release successfully done
                library.write_log(lib_constants.LOG_INFO, "INFO: Home Button "
                    "pressed and released successfully ",tc_id,script_id, "TTK",
                    "Home_button_port: %s" %home_button,log_level,tbd)
                flag2 = True
            else:
                library.write_log(lib_constants.LOG_WARNING,"WARNING: Home "
                    "button press and release got failed", tc_id,
                    script_id, "TTK", "Home_Button_port: %s"% home_button,
                    log_level, tbd)

                flag2 = False
            if flag1 == True and flag2 == True:
                return True
            else:
                return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : Parameter not"
            " handled",tc_id,script_id,"None","None",log_level,tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e ,
        tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # Returns Error if Exception occurred
################################################################################
################################################################################
# Function Name : uart_functionality
# Parameters    : device_name, tc_id, script_id, log_level, tbd
# Functionality : verify uart functionality by transfer - receive data from
#                 host using UART(serial cable)
# Return Value  : returns True on success and Fail otherwise
################################################################################
def uart_functionality(device, tc_id, script_id,
                       log_level="ALL", tbd=None):

    c = wmi.WMI()
    flag = False
    com_port = ""
    wql = lib_constants.UART_USB_QUERY
    for item in c.query(wql):
        if "USB-to-Serial" in item.Dependent.Caption:
            com_port = item.Dependent.Caption.split(" ")[-1].strip("(")\
                .strip(")")                                                     #checking for com_port where seriable connected
            library.write_log(lib_constants.LOG_INFO,"INFO: USB to serial "
                "cable is connected on the system", tc_id, script_id, "None",
                "None", log_level, tbd)
            flag = True                                                         #if com_port founded write pass log
        else:
            pass
    if flag:
        pass
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: USB to serial "
             "cable is not connected on the system", tc_id, script_id, "None",
                "None", log_level, tbd)
        return False                                                            #return false if com_port isn't verified

    ser = serial.Serial()
    ser.port = com_port
    ser.baudrate = lib_constants.BAUDRATE

    try:
        ser.open()
        library.write_log(lib_constants.LOG_INFO, "INFO: %s connection "
        "established successfully"%device,tc_id,script_id, log_level,tbd)
    except Exception as e:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to  "
            "establish the %s connection"%device,tc_id,script_id,log_level,
            tbd)
            return False

    if ser.isOpen():
        library.write_log(lib_constants.LOG_INFO, "INFO: Sending data"
        " and getting back using uart or serial cable connection from host"
        ,tc_id,script_id, log_level,tbd)

        try:
            ser = serial.serial_for_url('loop://', timeout=lib_constants.ONE)
            sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

            snd_word = lib_constants.UART_MESSAGE                               #message to be transferred for uart functionality check
            sio.write(str(snd_word))
            sio.flush()                                                         # it is buffering. required to get the data out *now*
            time.sleep(lib_constants.FIVE)
            response = ser.readline()
            if response == snd_word:
                library.write_log(lib_constants.LOG_INFO, "INFO: Data "
                "transmitted and received successfully from host using %s"
                %device,tc_id, script_id,"None", "None",log_level, tbd)         #getting the response from host or another device
                library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                "functionality verified successfully"%device,tc_id,
                script_id,"None", "None",log_level, tbd)                        #return true if functionality is verified

                return True
            ser.close()                                                         #closing the serial connection
        except Exception as e:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to verify "
            "%s functionality"%e,tc_id, script_id,log_level, tbd)               #return false if functionality is verified
            return False                                                        #exception occur when communicating

    else:                                                                       #unable to open serial port
        library.write_log(lib_constants.LOG_INFO , "INFO : Failed to open "
        "serial port connection ",tc_id,script_id,log_level,tbd)
        return False
################################################################################
# Function Name : Lan_functionality
# Parameters    : device_name, tc_id, script_id, log_level, tbd
# Functionality : checks ping status tohost machine
# Return Value  : returns True on success and Fail otherwise
################################################################################
def lan_functionality(device, tc_id, script_id,
                      log_level="ALL", tbd=None):

    host_ip = utils.ReadConfig("DEVICE_FN","HOST_IP")
    if "FAIL:" in host_ip:
        library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Config "
            "entry for host_ip is not found", tc_id,script_id, log_level, tbd)  # If failed to get config info, exit
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Host_ip "
            "is successfully founded in config entry ", tc_id,script_id,
            log_level, tbd)
    try:
        if device.upper() == "USBLAN":
            usb_lan_ip = utils.ReadConfig("DEVICE_FN","USBLAN_IP")
            if "FAIL:" in usb_lan_ip:
                library.write_log(lib_constants.LOG_DEBUG,
                                  "DEBUG: Config entry for USBLAN_IP is not "
                                  "found under DEVICE_FN",
                                  tc_id, script_id, log_level,
                                  tbd)                                          # If failed to get config info, exit
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: USBLAN_IP-%s is successfully founded "
                                  "in config entry under tag DEVICE_FN"
                                  % usb_lan_ip,
                                  tc_id, script_id,
                                  log_level, tbd)
            lan_ping_status = check_ping_internet(usb_lan_ip,
                                                  host_ip,
                                                  tc_id,
                                                  script_id,
                                                  log_level,
                                                  tbd)                          # Function calling to check ping connectivity
            if lan_ping_status is True:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Connectivity successful from SUT ip %s"
                                  " to destination %s" % (usb_lan_ip,host_ip),
                                  tc_id,
                                  script_id,
                                  "None",
                                  "None",
                                  log_level,
                                  tbd)
                return True                                                     # Writing log info message to the log file
            else:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Connectivity failed from SUT ip %s to"
                                  " destination %s" % (usb_lan_ip, host_ip),
                                  tc_id,
                                  script_id,
                                  "None",
                                  "None",
                                  log_level,
                                  tbd)
                return False                                                    # Writing log error message to the log file

        else:
            if library.check_connectivity(host_ip, tc_id, script_id,
                                          log_level="ALL", tbd=None):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: %s functionality verified by pinging"
                                  " to %s"%(device,host_ip), tc_id,
                                  script_id,"None", "None",log_level, tbd)
                                                                                #return True if functionality is verified
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: %s functionality failed to verified "
                                  "by  pinging to %s"%(device,host_ip), tc_id,
                                  script_id, "None","None", log_level, tbd)     #return false if functionality is  not verified
                return False

    except Exception as e:                                                      #RETURN FALSE WHEN EXCEPTION OCCUR
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e ,
               tc_id, script_id, "None", "None", log_level, tbd)
        return False

def set_speed_step(TC_id, script_id, loglevel ="ALL", tbd = None):
    try:
        if "GLK" == tbd:
            string_inbios_set = lib_constants.SET_INTEL_SPEED_STEP_DISABLE_SMALL
        else:
            string_inbios_set = lib_constants.SET_INTEL_SPEED_STEP_DISABLED_BIG
        ret=lib_set_bios.lib_write_bios(string_inbios_set, TC_id, script_id,
            loglevel, tbd)
        if 3 == ret:                                                            # If function call returns 3 then update is successful
            library.write_log(lib_constants.LOG_INFO,
            'INFO:BIOS Update Successfull for option %s'%string_inbios_set,
            TC_id,script_id,'BIOS-conf',"none",loglevel,str(tbd))
            process = subprocess.Popen(lib_constants.SHUTDOWN_CMD,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)                     # Executing shutdown command with delay of 10 seconds
            stdout, stderr = process.communicate()                              # Getting command output and error information
            if len(stderr) > 0:                                                 # If any error found in executing shutdown command
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                " execute shutdown command to perform G3 and perform clear "
                "cmos", TC_id, script_id, loglevel, tbd)
                return False                                                    # Function exists by Returning False if error occurs in executing shutdown command
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Shutdown comma"
                "nd is successful to perform G3 and perform clear cmos", TC_id,
                script_id, 'None', "None", loglevel, str(tbd))
                return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: BIOS Update failed"
            " for option Speed Shift", TC_id, script_id, 'BIOS-conf', "none",
            loglevel, str(tbd))
            return False                                                        # If function call returns 4 then bios failed to update
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
        TC_id,script_id,"biosconf","None",loglevel,tbd)
def read_speed_step(TC_id, script_id, loglevel ="ALL", tbd = None):
    try:
        if "GLK" == tbd:
            string_inbios_read = lib_constants.\
                READ_INTEL_SPEED_STEP_ENABLE_SMALL
        else:
            string_inbios_read = lib_constants.READ_INTEL_SPEED_STEP_ENABLED_BIG
        cur_dir = lib_constants.SCRIPTDIR
        ret,value = lib_read_bios.read_bios(string_inbios_read, TC_id, script_id
                    ,cur_dir, loglevel, tbd)                                    # Function to read bios value for SpeedStep
        if 3 == ret or 5 == ret:                                                # If function call returns 3 or 5, then update is success
            library.write_log(lib_constants.LOG_INFO,
            "INFO: BIOS read successful in verifying default value for option,"
            " Intel Speed Step = Disabled", TC_id, script_id, 'BIOS-conf',
            "none", loglevel, str(tbd))
            return True
        else:                                                                   # If function call returns 4 then, bios failed to update
            library.write_log(lib_constants.LOG_INFO,
            "INFO:BIOS read unsuccessful in verifying default value for option"
            ", Intel Speed Step = Disabled", TC_id, script_id, 'BIOS-conf',
            "none", loglevel, str(tbd))
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
        TC_id, script_id, 'BIOS-conf', "None", loglevel, tbd)
def perform_clearcmos(test_case_id, script_id, log_level ="ALL", tbd = None):
    try:
        result = lib_perform_g3.perform_g3(test_case_id, script_id, log_level,
                                           tbd)                                 # Calling perform_g3 function
        if result:
            library.write_log(lib_constants.LOG_INFO,"INFO: Perform G3 "
            "successful", test_case_id,script_id,"None","None",log_level,tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Perform G3 failed",
            test_case_id,script_id,"None","None",log_level,tbd)
            return False
        time.sleep(lib_constants.FIVE_SECONDS)
        if library.clear_cmos_function(log_level, tbd):                         # Calling clear_cmos_function to clear the cmos
            library.write_log(lib_constants.LOG_INFO, "INFO: Clear CMOS done "
            "successfully", test_case_id, script_id, "TTK", "None", log_level,
            tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to clear "
            "CMOS state", test_case_id, script_id, "TTK", "None", log_level,
            tbd)                                                                # Write the fail msg to log
            return False
        time.sleep(lib_constants.FIVE)
        if lib_connect_disconnect_power_source.connect_disconnect_power("CONNE"
           "CT","AC",test_case_id, script_id, log_level, tbd):                  # Library calls to connect the AC power supply & DC signal
            library.write_log(lib_constants.LOG_INFO, "INFO: Connect power "
            "source successful", test_case_id, script_id, "None", "None",
            log_level)
            result = lib_press_button_on_board.press_button(lib_constants.ONE,
                     "POWER", lib_constants.ONE, test_case_id, script_id,
                     log_level, tbd="None")                                     # Library calls to press power button
            if result:
                library.write_log(lib_constants.LOG_INFO,"INFO: Pres"
                "sing power button is successful ",test_case_id,
                script_id,"TTK","setGPIO()",log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Pressing power "
                "button failed ", test_case_id, script_id, "TTK",
                "setGPIO()", log_level, tbd)
                time.sleep(lib_constants.SHORT_TIME)
                return False                                                    # Returns false if fail to press power button
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:Connect"
            "ion of power source failed", test_case_id, script_id,
            "None","None",log_level)
            return False
        return True                                                             # Returns True if G3,clear cmos and connect power source is done successfully
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
        test_case_id, script_id, 'BIOS-conf', "None", log_level, tbd)
        return False

################################################################################
# Function Name : create_file
# Parameters    : drive,tc_id, script_id, log_level, tbd
# Functionality : creates a file in USB device
# Return Value  : returns drive_letter on success and False otherwise
################################################################################
def create_file(drive, test_case_id, script_id, log_level="ALL", tbd="None"):
    try:
        log_file = drive +  ".txt"                                              #create log file ine name of the type of usb device connected
        drive_name = utils.ReadConfig("USB_EFI",drive)                          #read  config entry for usb device
        if "FAIL:" in [drive_name]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
            " of usb device is incorrect", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Write fail message to log file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO:Config entry found"  
            "  correct", test_case_id, script_id, "None", "None", log_level,tbd) #write pass message to log file
        log = script_id.replace(".py" , "-1.txt")                               #create a log_file with script_id
        os.chdir(lib_constants.SCRIPTDIR)
        cmd  = lib_constants.GET_INFO + log                                     #get the drive information in os and save it in log
        flag_device = False
        os.system(cmd)
        with io.open(log ,"r",encoding='utf-16-le') as f:                       #read the log file
            for lines in f:
                if drive_name in lines:                                         #if usb device name is present in the log
                    text = lines.split(drive_name)                              #gets the drive letter of usb device connected
                    tval = text[0].strip()                                      #gets the drive letter of usb device connected
                    drive_drivename = tval[-2] + ":"                            #gets the drive letter of usb device connected
                    flag_device = True
                    break
                else:
                    flag_device = False
        if flag_device:                                                         #if drive exists
            f = open(drive_drivename + "\\" +  log_file , "w")                  #create a .txt file in the name of the type of usb device connected
            return drive_drivename                                              #returns drive letter
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING:USB device "
            "doesnot exists", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #Write info to log file as usb device is not connected
            return False                                                        #Return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Write exception message to log file
        return False
################################################################################
# Function Name : nsh_file_gen_to_get_dir
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : gets the contents of usb device
# Return Value  : returns True on success and False otherwise
################################################################################
def nsh_file_gen_to_get_dir(test_case_id, script_id, log_level="ALL",
                       tbd="None"):
    try:
        log = script_id.split(".")[0].split('-')
        log[-1] = "1.txt"
        log_file = "-".join(log)
        log_path = os.path.join(lib_constants.SCRIPTDIR, log_file)
        f = codecs.open(log_path,"r", "utf-16")                                 #read the log file
        L=[]                                                                    #create empty list
        for line in f:                                                          #read each line in file
            if "FS" in line:                                                    #reads each fs information in efi shell
                line = line.split("FS")                                         #reads each fs information in efi shell
                line = line[1][0]                                               #reads each fs information in efi shell
                L.append("fs"+line+":")                                         #reads each fs information in efi shell and store it in list
                L = sorted(L)                                                   #sort the list
        M = L.pop()                                                             #gets fs information of s: drive from efi shell
        f = open("startup.nsh",'w')                                             #create .nsh file
        f.write("bcfg boot mv 01 00" + '\n' )                                   #write to nsh file
        n = 0
        for i in L :                                                            #for each fs in list
            n = n+1
            gen_cmd = "%s"%i + '\n' + "dir >a" + " " + str(M)+"\\" + \
            script_id.split(".")[0]  + "-" + str(n) + ".txt" "\n"               #write to .nsh file to get the contents of usb device
            f.write(gen_cmd)
        f.write("reset")                                                        #write to nsh file
        f.close()                                                               #close file
        return True

    except Exception as e:                                                      #Exception
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)
        return False
################################################################################
# Function Name : search_log_file
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : search the log file in os and copy it  to script_dir
# Return Value  : returns True on success and False otherwise
################################################################################
def search_log_file(test_case_id, script_id, log_level="ALL",
                       tbd="None"):
    try:
        log = script_id.split("-")
        log.pop()
        log_file = "-".join(log)+"-1.txt"                                  		#file to be searched
        drives = win32api.GetLogicalDriveStrings()                              #gets the drive information
        drives = drives.split("\000")[:-1]                                      #gets the drive information ond stores it in list
        for i in drives:
            if i == "O:\\" or i== "C:\\":                                       #if c: and network drive in list
                drives.remove(i)                                                #remove c: and network drive from list
        for j in drives:                                                        #for each drive in the list
            gen_log = os.path.join(j, log_file)                                 #search the log_file in each drive
            if os.path.exists(gen_log):                                         #search the log_file in each drive
                shutil.copy(gen_log, lib_constants.SCRIPTDIR)                    #if log_file is found copy log_file to script directory
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO,"INFO : The log is"    #write pass message to log if file is found
                " generated in efi shell ", test_case_id, script_id,"None",
                                  "None", log_level, tbd)
                return True
            else:
                pass
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Log file is not"
        " generated after executing command in efi shell", test_case_id,
        script_id, "None", "None", log_level, tbd)                              #Write info to log if file not found
        return False

    except Exception as e:                                                      #Exception
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)
        return False
################################################################################
# Function Name : nsh_file_gen_to_perform_copy
# Parameters    :drive, tc_id, script_id, log_level, tbd
# Functionality : create nsh file in the virtual drive to perform copy operation
# Return Value  : returns True on success and False otherwise
################################################################################
def nsh_file_gen_to_perform_copy(drive,test_case_id, script_id, log_level="ALL",
                       tbd="None"):
    try:
        os.chdir(lib_constants.SCRIPTDIR)
        log = script_id.split("-")
        log.pop()
        log_file = "-".join(log)+"-3-1.txt"
        fname = open(log_file,"r")                                              #read the log file that was generated after executing dir cmd in EFI shell
        dir_var = ""
        for line in fname.readlines():                                          #read each line of log file
            if "Directory" in line:
                dir_var = line.split(":")[1].strip()                            #gets the fs information  of usb device from the log
            if drive + ".txt" in line:                                          #searches each line in the file for .txt file
                library.write_log(lib_constants.LOG_INFO, "INFO: USB-device is" #gives the fs information of usb device connected in efi shell
                  " enumerated as " + dir_var +" in efi shell",test_case_id,
                                  script_id,"None", "None", log_level, tbd)
                break
        log = log_file.replace("-3-1.txt","-1.txt")                             #read the log file that was generated after executing map -r in efi shell
        file_to_copy = log_file                                                 #file to be copied to usb device from s: drive
        f = codecs.open(log,"r", "utf-16")                                                       #read the log file
        L=[]                                                                    #create empty list
        for line in f:                                                          #read each line in file
            if "FS" in line:                                                    #reads each fs information in efi shell
                line = line.split("FS")                                         #reads each fs information in efi shell
                line = line[1][0]                                               #reads each fs information in efi shell
                L.append("fs"+line+":")                                         #reads each fs information in efi shell and store it in list
        L = sorted(L)                                                           #sort the list
        M = L.pop()                                                             #gets fs information of s: drive from efi shell
        if os.path.exists("startup.nsh"):                                       #check for startup.nsh file, if exist remove
            os.remove("startup.nsh")
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Startup.nsh"
            " doesnot exist", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #Write message to log if .nsh file does not exist

        gen_cmd_f = "stall 1000000"+"\n"                                        #Delay
        gen_cmd_f = gen_cmd_f + "rm "+ dir_var.lower() + ":\\" + file_to_copy \
            + " \n"                                                             #Remove file if the file to be copied exists in usb device
        gen_cmd_f = gen_cmd_f + "cp -r " + M.lower() + "\\"+ file_to_copy + \
            " " + dir_var.lower() + ":" + "\n"                                  #Copy file from s drive to usb device

        f = open("startup.nsh", 'w')                                            #Create .nsh file
        f.write("bcfg boot mv 01 00" + "\n")                                    #Write  gen_cmd_f to .nsh file
        f.write(gen_cmd_f)                                                      #Write  gen_cmd_f to .nsh file
        f.write("reset")                                                        #Write to .nsh file
        f.close()                                                               #Close file
        return True                                                             #Return true

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Exception
        return False

################################################################################
# Function Name         : plug_usb_hub_usb_drive
# Parameters            : tc_id, script_id
# Target                : host
# Implemented Parameters: usb-hub
################################################################################
def plug_usb_hub_usb_drive(tc_id, script_id, log_level = "ALL",
                               tbd = None):                                     # Function to verify the usb-hub
    try:
        if lib_plug_unplug.plug_unplug(tc_id, script_id, "HOT-PLUG",
                    "usb-hub_usb-drive","USB-HUB", log_level="ALL", tbd=None):  # function calling for hot-plug usb drive to usb-hub
            library.write_log(lib_constants.LOG_INFO, "INFO: Usb pendrive "
            "plugged to usb-hub successfully", tc_id, script_id, "TTK", "None",
            log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to plug"
            "usb pendrive to usb-hub", tc_id, script_id, "TTK", "None",
            log_level, tbd)
            return False
    except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due "
            "to %s"% e, tc_id, script_id, "TTK", "None", log_level, tbd)
            return False
################################################################################
# Function Name         : verify usb hub
# Parameters            : token, tc_id, script_id
# Target                : sut
# Implemented Parameters: usb-Hub
################################################################################
def verify_usb_hub(tc_id, script_id, log_level = "ALL",
                               tbd = None):                                     # Function to verify the usb-hub
    try:
        device_name = utils.ReadConfig("PLUG_UNPLUG",
                                  "USB-HUB_USB-DRIVE_DEVICE-NAME")

        if "FAIL" in device_name or 'NC' in device_name.upper() or\
                        'NA' in device_name.upper():

            library.write_log(lib_constants.LOG_DEBUG, "DEBUG: Config entry "
            "for USB-HUB_USB-DRIVE_DEVICE-NAME is not proper",
            tc_id, script_id, "None", "None", log_level, tbd)                   #if failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for "
            "USB-HUB_USB-DRIVE_DEVICE-NAME is %s in config.ini"
            % device_name, tc_id, script_id, "None", "None", log_level, tbd)    #continie to remaining steps as config entry is fetched

        if lib_plug_unplug.check_device("USB-HUB_USB-DRIVE", tc_id, script_id,
                device_name, log_level="ALL", tbd=None):                        # function calling for checking usb drive enumeration to usb-hub
            library.write_log(lib_constants.LOG_INFO, "INFO: Usb pendrive "
            "plugged to usb-hub successfully", tc_id, script_id, "None",
            "None", log_level, tbd)
            if file_transfer("USB-HUB_USB-DRIVE", tc_id, script_id,
                             log_level="ALL", tbd=None):                        # function calling for usb pendrive functionality through usb-hub
                library.write_log(lib_constants.LOG_INFO, "INFO: Usb-hub "
                "functionality verified successfully", tc_id, script_id, "None",
                "None", log_level,tbd)
                return True
            else :
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "verify  usb-hub functionality ", tc_id, script_id, "None",
                "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to plug"
            "usb pendrive to usb-hub", tc_id, script_id, "None", "None",
            log_level, tbd)
            return False
    except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due "
            "to %s"% e, tc_id, script_id, "None", "None", log_level, tbd)
            return False

################################################################################
# Function Name         : plug_usb_drive
# Parameters            : tc_id, script_id
# Target                : host
# Implemented Parameters: usb devices
################################################################################
def plug_usb_drive(tc_id, script_id, log_level = "ALL", tbd = None):            #function to verify usb-device is plugged in or not
    try:
        if lib_plug_unplug.plug_unplug(tc_id, script_id, "HOT-PLUG",
                                       "USB-DEVICE", "USB", log_level="ALL",
                                       tbd=None):                               #function call to hot-plug usb drive
            library.write_log(lib_constants.LOG_INFO, "INFO: USB pendrive "
            "plugged in  successfully", tc_id, script_id, "TTK", "None",
                              log_level, tbd)                                   #write pass message to log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "plug in usb device ", tc_id, script_id, "TTK", "None", log_level,
                              tbd)                                              #write fail message to log file
            return False
    except Exception as e:                                                      #exception
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due "
            "to %s"% e, tc_id, script_id, "TTK", "None", log_level, tbd)        #write exception message to log file
            return False

################################################################################
# Function Name         : unplug_usb_drive
# Parameters            : tc_id, script_id
# Target                : host
# Implemented Parameters: usb devices
################################################################################
def unplug_usb_drive(tc_id, script_id, log_level = "ALL", tbd = None):          #function to unplug usb-device
    try:
        if lib_plug_unplug.plug_unplug(tc_id, script_id, "HOT-UNPLUG",
                                       "USB-DEVICE", "USB", log_level="ALL",
                                       tbd=None):                               #function call to hot-unplug usb drive
            library.write_log(lib_constants.LOG_INFO, "INFO: USB device "
            "unplugged successfully", tc_id, script_id, "TTK", "None",
                              log_level, tbd)                                   #write pass message to log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "unplug usb device ", tc_id, script_id, "TTK", "None", log_level,
                              tbd)                                              #write fail message to log file
            return False
    except Exception as e:                                                      #exception
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception due "
            "to %s"% e, tc_id, script_id, "TTK", "None", log_level, tbd)        #write exception message to log file
            return False

################################################################################
# Function Name         : check_ping_internet
# Parameters            : tc_id, script_id
# Target                : host
# Implemented Parameters: usb devices
#Functionality          : to verify the access network pings provided ip
################################################################################
def check_ping_internet(ip_address, network_device_id, tc_id, script_id,
                        log_level, tbd):

    library.write_log(lib_constants.LOG_INFO,
                      "INFO: Function to ping the provided IP",
                      tc_id,
                      script_id,
                      "None",
                      "None",
                      log_level,
                      tbd)
    try:
        str_destination = " Destination net unreachable."
        str_packets = "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)"
        ping_cmd = "ping " + network_device_id + " -S " + \
                   ip_address
        ping_res = utils.execute_with_command(ping_cmd,
                                              tc_id, script_id, "None",
                                              log_level, tbd)
        if ping_res.returncode != lib_constants.ZERO:
            library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Exception while running Command %s "
                              % ping_cmd,
                              tc_id,
                              script_id,
                              "None",
                              "None",
                              log_level,
                              tbd)
            return False                                                        # Writing log error message to the log file
        elif ping_res.stdout != '':
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Command %s is successful" % ping_cmd,
                              tc_id,
                              script_id,
                              "None",
                              "None",
                              log_level,
                              tbd)                                              # Writing log info message to the log file
            if str_packets in ping_res.stdout and str_destination in \
                    ping_res.stdout:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Ping from SUT to destination %s is "
                                  "not successful. No Internet"
                                  % network_device_id,
                                  tc_id,
                                  script_id,
                                  "None",
                                  "None",
                                  log_level,
                                  tbd)
                return False                                                    # Writing log error message to the log file
            elif str_packets in ping_res.stdout:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Ping from SUT to destination %s is "
                                  "successful" % network_device_id,
                                  tc_id,
                                  script_id,
                                  "None",
                                  "None",
                                  log_level,
                                  tbd)
                return True                                                     # Writing log info message to the log file
            else:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Ping from SUT to destination %s is "
                                  "not successful"
                                  % network_device_id,
                                  tc_id,
                                  script_id,
                                  "None",
                                  "None",
                                  log_level,
                                  tbd)
                return False                                                    # Writing log error message to the log file
        else:
            library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Failed to execute the command %s"
                              % ping_cmd,
                              tc_id,
                              script_id,
                              "None",
                              "None",
                              log_level,
                              tbd)                                              # Writing log error message to the log file
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: Exception in check_ping_internet "
                          "function due to %s" % e_obj,
                          tc_id,
                          script_id,
                          "None",
                          "None",
                          log_level,
                          tbd)                                                  # Writing exception message to log file
        return False

################################################################################
# Function Name : keyboard_functionality_in_os
# Parameters    : input_device, env, tc_id, script_id, log_level and tbd
# Functionality : To verify Keyboard functionality in OS
# Return Value  : Returns True on success and Fail otherwise
################################################################################


def keyboard_functionality_in_os(input_device, env, tc_id, script_id,
                                 log_level="ALL", tbd=None):

    try:
        time.sleep(lib_constants.KEYPRESS_WAIT_HOST)

        if "PS2-KEYBOARD" == input_device.upper():
            kb_enter = utils.ReadConfig("TTK", "KB_ENTER_PS2")                  # Fetching ps2 keyboard enter key port number from TTK
        else:
            kb_enter = utils.ReadConfig("TTK", "KB_ENTER")                      # Fetching keyboard enter key port number from TTK
            input_device_name = utils.ReadConfig("KBD_MOUSE",
                                                 "KEYBOARD_MOUSE_DEVICE_NAME")  # Extract input device name from config.ini
            port = utils.ReadConfig("KBD_MOUSE", "PORT")                        # Extract com port details from config.ini

            if "FAIL:" in port or "FAIL:" in input_device_name or \
                    "FAIL:" in kb_enter:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get com port details and input device "
                                  "name under KBD_MOUSE or KB_ENTER under TTK "
                                  "from Config.ini", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            if os.path.exists(r"Z:\GenericFramework\keyboard_"
                              r"functionality.txt"):
                os.remove("Z:\GenericFramework\keyboard_functionality.txt")
                library.write_log(lib_constants.LOG_INFO, "INFO: keyboard_"
                                                          "functionality.txt file deleted"
                                                          , tc_id, script_id,"None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: keyboard_"
                                                          "functionality.txt file doesnot exist"
                                  , tc_id, script_id, "None", "None", log_level, tbd)

            kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)           # kb_obj object of USBKbMouseEmulation class
            kb_obj.key_press("KEY_GUI")                                         # Press Windows button
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            kb_obj.key_type("cmd")                                              # Send cmd command
            kb_obj.key_press("KEY_ENTER")
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("python")                                           # Send python
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("import os, subprocess, lib_constants")             # Send python modules
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("os.chdir(r'C:\\Testing\\GenericFramework')")       # Send cmd for to change directory
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("subprocess.Popen('start cmd', shell=True, "
                            "stdout=subprocess.PIPE, stdin=subprocess.PIPE, "
                            "stderr=subprocess.PIPE)")                          # Send cmd for to open command prompt
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("python")                                           # Send python
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("import os")                                        # Send os module
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.THREE)
            kb_obj.key_type("os.system('dir > keyboard_functionality.txt')")    # Send cmd for to create keyboard_functionality text file
            time.sleep(lib_constants.THREE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key

            duration = lib_constants.ONE
            times = lib_constants.THREE
            press_delay = lib_constants.TWO

            result = lib_ttk2_operations.\
                press_release_button(int(duration), int(times), int(kb_enter),
                                     int(press_delay), tc_id, script_id,
                                     log_level, tbd)

            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                  "Enter key pressed and released for %d "
                                  "times successfully in %s" % (times, env),
                                  tc_id, script_id, "None", "None",
                                  log_level, tbd)
                time.sleep(lib_constants.ONE)
                kb_obj.key_type("exit()")                                       # Send exit
                time.sleep(lib_constants.ONE)
                kb_obj.key_press("KEY_ENTER")                                   # Press Enter key
                time.sleep(lib_constants.ONE)
                kb_obj.key_type("exit()")                                       # Send exit
                time.sleep(lib_constants.ONE)
                kb_obj.key_press("KEY_ENTER")                                   # Press Enter key
                time.sleep(lib_constants.ONE)
                kb_obj.key_type("exit()")                                       # Send exit
                time.sleep(lib_constants.ONE)
                kb_obj.key_press("KEY_ENTER")                                   # Press Enter key
                time.sleep(lib_constants.ONE)
                kb_obj.key_type("exit()")                                       # Send exit
                time.sleep(lib_constants.ONE)
                kb_obj.key_press("KEY_ENTER")                                   # Press Enter key

                if os.path.exists(r"Z:\GenericFramework\keyboard_"
                                  r"functionality.txt"):
                    library.write_log(lib_constants.LOG_INFO, "INFO: keyboard_"
                                      "functionality.txt file created "
                                      "successfully and exists in SUT Generic"
                                      "Framework folder", tc_id, script_id,
                                      "None", "None", log_level, tbd)

                    library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                      "functionality verified successfully in "
                                      "%s" % env, tc_id, script_id, "None",
                                      "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "keyboard_functionality.txt file does "
                                      "not exists in GenericFramework folder",
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed"
                                  " to press & release Keyboard Enter key in "
                                  "%s" % env, tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
    except Exception as e:                                                      # Exception handling for TTK operation
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : trigger_mouse_host
# Parameters    : env, tc_id, script_id, log_level, tbd
# Functionality : To verify Mouse functionality in OS
# Return Value  : Returns True on success and Fail otherwise
################################################################################


def trigger_mouse_host(env, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        mouse_click = utils.ReadConfig("TTK", "MOUSE_CLICK")

        if "FAIL:" in mouse_click:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for mouse_click is not found", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        duration = lib_constants.ONE
        times = lib_constants.THREE
        press_delay = lib_constants.TWO

        result = lib_ttk2_operations. \
            press_release_button(int(duration), int(times), int(mouse_click),
                                 int(press_delay), tc_id, script_id,
                                 log_level, tbd)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Mouse click "
                              "pressed and released successfully for %d "
                              "times in  %s " % (times, env), tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "press and release Mouse click", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : mouse_functionality_in_os
# Parameters    : env, input_device, tc_id, script_id, log_level, tbd
# Functionality : To verify Mouse functionality in OS
# Return Value  : Returns True on success and Fail otherwise
################################################################################


def mouse_functionality_in_os(env, input_device, tc_id, script_id,
                              log_level="ALL", tbd=None):

    try:
        time.sleep(lib_constants.FIVE_SECONDS)

        input_device_name = utils.ReadConfig("KBD_MOUSE",
                                             "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini
        mouse_click = utils.ReadConfig("TTK", "MOUSE_CLICK")

        if "FAIL:" in port or "FAIL:" in input_device_name or \
                "FAIL:" in mouse_click:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                              "to get com port details and input device "
                              "name under KBD_MOUSE or mouse_click under TTK "
                              "from Config.ini", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("KEY_GUI")                                             # Press Windows button
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("cmd")
        time.sleep(lib_constants.THREE)                                         # Send cmd command
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("python")                                               # Send python
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("import os, subprocess, lib_constants")                 # Send python modules
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("os.chdir(r'C:\Testing\GenericFramework\Middleware')")  # Send cmd for to change directory
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("subprocess.Popen('start cmd', shell=True, "
                        "stdout=subprocess.PIPE, stdin=subprocess.PIPE, "
                        "stderr=subprocess.PIPE)")                              # Send cmd for to open command prompt
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("python")                                               # Send python
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("import os, subprocess, lib_constants, "
                        "lib_verify_device_functionality")                      # Send python modules
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.THREE)
        kb_obj.key_type("cmd = lib_verify_device_functionality.click_mouse"
                        "('None', 'None', 'None', 'None', 'None')")             # Send command for to execute click_mouse() function
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("subprocess.Popen('cmd', shell=True, "
                        "stdout=subprocess.PIPE, stdin=subprocess.PIPE, "
                        "stderr=subprocess.PIPE)")                              # Send cmd for to execute the given command
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key

        library.write_log(lib_constants.LOG_INFO, "INFO: Successfully created "
                          "Mouse Receiver Window", tc_id, script_id,
                          "None", "None", log_level, tbd)

        duration = lib_constants.ONE
        times = lib_constants.THREE
        press_delay = lib_constants.TWO

        result = lib_ttk2_operations. \
            press_release_button(int(duration), int(times), int(mouse_click),
                                 int(press_delay), tc_id, script_id,
                                 log_level, tbd)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Mouse click "
                              "pressed and released successfully for %d "
                              "times in  %s " % (times, env), tc_id, script_id,
                              "None", "None", log_level, tbd)

            time.sleep(lib_constants.ONE)
            kb_obj.key_type("exit()")                                           # Send exit
            time.sleep(lib_constants.ONE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.ONE)
            kb_obj.key_type("exit()")                                           # Send exit
            time.sleep(lib_constants.ONE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.ONE)
            kb_obj.key_type("exit()")                                           # Send exit
            time.sleep(lib_constants.ONE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            time.sleep(lib_constants.ONE)
            kb_obj.key_type("exit()")                                           # Send exit
            time.sleep(lib_constants.ONE)
            kb_obj.key_press("KEY_ENTER")                                       # Press Enter key
            library.write_log(lib_constants.LOG_INFO, "INFO: Verified %s "
                              "functionality in %s" % (input_device, env),
                              tc_id, script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "press and release Mouse click", tc_id,
                              script_id, "None", "None", log_level, tbd)

            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


def sensor_functionality_in_os(sensor_name, tc_id, script_id, log_level, tbd):

    try:
        if "-" in sensor_name:
            sensor_name = sensor_name.replace("-", " ")
        sensor_status = lib_sensorviewer.\
            get_sensor_status(sensor_name, tc_id, script_id, "SensorViewer")

        if sensor_status.upper() == "READY":
            library.write_log(lib_constants.LOG_INFO, "INFO: current status "
                              "of %s is %s" % (sensor_name, sensor_status),
                              tc_id, script_id, "SensorViewer", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Status of "
                              "%s is %s" %(sensor_name, sensor_status), tc_id,
                              script_id, "SensorViewer", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s " % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
