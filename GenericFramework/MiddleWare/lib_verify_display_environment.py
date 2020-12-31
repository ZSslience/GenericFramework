__author__ = 'AsharanX/kashokax/mmakhmox'

############################General Python Imports##############################
import cv2
import numpy as np
import subprocess
import os
import time
import codecs
import json
from PIL import ImageGrab, Image
############################Local Python Imports################################
import library
import lib_boot_to_environment
import lib_constants
import utils
import lib_plug_unplug
import lib_press_button_on_board

################################################################################
# Function Name         : verify_display_environment
# Parameters            : token, tc_id, script_id
# Target                : host
# Syntax                : Verify <Display Page> display
# Implemented Parameters: BIOS, OS, UEFI SHELL
################################################################################
def verify_display_environment(input, tc_id, script_id, log_level = "ALL",
                               tbd = None):                                     # function to verify the display environment
    try:
        kvm_name = utils.ReadConfig("kvm_name","name")                          # KVM is read from the config file
        sikuli_path = utils.ReadConfig("sikuli","sikuli_path")                  # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli","sikuli_exe")                    # Sikuli exe name fetched from config file
        for item in  [kvm_name, sikuli_path, sikuli_exe]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO :config entry is"
                " missing for tag name :kvm_name or sikuli_path or sikuli_exe",
                tc_id,script_id,"None","None",log_level,tbd)
                return False                                                    # if the readconfig function returnd fail it means no config entry is given
            else:
                pass
        sikuli_cmd_for_os = " OS_display.skl"                                   # Sikuli file for verifying OS Page
        sikuli_cmd_for_BIOS = " Bios_display.skl"                               # Sikuli file for verifying BIOS Page
        sikuli_cmd_for_EDK = " EFI_display.skl"                                 # Sikuli file for verifying EFI Page
        os.chdir(os.getcwd())
        time.sleep(lib_constants.SIKULI_EXECUTION_TIME)
        kvm_title = utils.ReadConfig("kvm_name","kvm_title")
        title = kvm_name + " - "+ kvm_title                                     # KVM command for activating the kvm window
        activate_path = utils.ReadConfig("sikuli","Activexe")
        window_path = activate_path + " " + title
        if "OS" == input.upper():                                               # checking if the input param is OS
            cur_state = lib_boot_to_environment.checkcuros(log_level,tbd)                # checking current state of the system by ping
            if "OS" == cur_state:                                               # if the current state is OS
                kvm_activate = subprocess.Popen(window_path,
                                                stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE)      # KVM window is activated from the host
                os.chdir(sikuli_path)
                cmd_for_os = sikuli_exe + sikuli_cmd_for_os                     # sikuli command to verify the Display
                Sikuli_execution = subprocess.Popen(cmd_for_os, shell=False,
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE)                    # Executes the Sikuli file for verifying the display environment
                output = Sikuli_execution.stdout.read()
                if "PASS" in output:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "is in OS",tc_id,script_id,"None","None",log_level,tbd)
                    return True                                                 # returns True if the display is 'OS'
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "Environment is not OS",tc_id,script_id,"None","None",
                                      log_level,tbd)
                    return False                                                # returns False if failed to verify display
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : System Current"
                " state is not OS",tc_id,script_id,"None","None",log_level,tbd)
                return False
        elif "BIOS SETUP" == input.upper():                                     # checking if the input param is BIOS
            cur_state = lib_boot_to_environment.checkcuros(log_level,tbd)
            if "EDK SHELL" == cur_state :                                       # checking current state of the system by ping
                kvm_activate = subprocess.Popen(window_path ,
                                                stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE)         # returns EDK Shell as current state if ping fails
                os.chdir(sikuli_path)
                cmd_for_BIOS = sikuli_exe + sikuli_cmd_for_BIOS                 # Executes the Sikuli file for verifying the display en
                Sikuli_execution = subprocess.Popen(cmd_for_BIOS ,shell = False,
                                     stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE)
                output = Sikuli_execution.stdout.read()
                if "PASS" in output:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "is in BIOS",tc_id,script_id,"None","None",log_level,tbd)
                    return True                                                 # returns True if the display is 'BIOS'
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "Environment is not BIOS",tc_id,script_id,"None","None",
                                      log_level,tbd)
                    return False                                                # returns False if failed to verify display
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : System Current"
                " state is not BIOS",tc_id,script_id,"None","None",log_level,tbd)
                return False
        elif "UEFI" == input.upper():                                           # checking if the input param is UEFI
            cur_state = lib_boot_to_environment.checkcuros(log_level,tbd)                # checking current state of the system by ping
            if "EDK SHELL" == cur_state :
                kvm_activate = subprocess.Popen(window_path ,
                                                stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE)         # returns EDK Shell as current state if ping fails
                os.chdir(sikuli_path)
                cmd_for_EDK = sikuli_exe + sikuli_cmd_for_EDK
                Sikuli_execution = subprocess.Popen(cmd_for_EDK ,shell = False,
                                     stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE)                    # Executes the Sikuli file for verifying the disp
                output = Sikuli_execution.stdout.read()
                if "PASS" in output:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "is in EFI",tc_id,script_id,"None","None",log_level,tbd)
                    return True                                                 # returns True if the display is 'EFI Shell'
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Display "
                    "Environment is not EDK SHELL",tc_id,script_id,"None","None",
                                      log_level,tbd)
                    return False                                                # returns False if failed to verify display
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : System Current"
                " state is not EDK SHELL",tc_id,script_id,"None","None",
                                  log_level,tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e ,
        tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # Returns Error if Exception occurred
################################################################################


################################################################################
# Function Name         : verify_display_state_presi
# Parameters            : token, tc_id, script_id
# Target                : host
# Syntax                : Verify <Display Page> display
# Implemented Parameters: BIOS, OS, UEFI SHELL
################################################################################
def verify_display_state_presi(input, tc_id, script_id, log_level = "ALL",
                               tbd = None):
    try:
        sikuli_path = utils.ReadConfig("sikuli","sikuli_path")                  # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli","sikuli_exe")                    # Sikuli exe name fetched from config file
        activate_path = utils.ReadConfig("sikuli","Activexe")                   # Activate_exe name fetched from config file
        for item in  [sikuli_path, sikuli_exe, activate_path]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO :config entry is"
                " missing for tag name :sikuli_path/sikuli_exe/Activate.exe",
                tc_id,script_id,"None","None",log_level,tbd)
                return False                                                    # Function exists by Returning False if config entry is missing
            else:
                pass
        sikuli_cmd_for_os = sikuli_path+"\Simics_OS_Display.skl"                # Sikuli executable file path for OS fetched from the config file
        sikuli_cmd_for_bios = sikuli_path+"\Simics_BIOS_Display.skl"            # Sikuli executable file path for BIOS fetched from the config file
        sikuli_cmd_for_edk = sikuli_path+"\Simics_EFI_Display.skl"              # Sikuli executable file path for EFI_SHELL fetched from the config file
        cmd = activate_path + " " + "GenXFSim PID:"
        activate_simics = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           stdin=subprocess.PIPE)              # Activating Simics Setup
        stdout, stderr = activate_simics.communicate()                          # Getting command output and error information
        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_INFO,"INFO :Error is activating"
                " Simics setup",tc_id,script_id,"None","None",log_level,tbd)
            return False                                                        # Function exists by returning False if Simics setup activation is failed

        if "OS" == input.upper():                                               # This block will run if Simics setup display needs to be verified in OS
            cmd_for_os = sikuli_exe + " " + sikuli_cmd_for_os                   # sikuli command to verify the Display in OS
            for count in range(5):                                              # Verifing display for 5 iterations
                Sikuli_execution = subprocess.Popen(cmd_for_os, shell = False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE) # Executes the Sikuli file for verifying the display environment
                stdout, stderr = Sikuli_execution.communicate()
                if "PASS" in stdout:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Simics "
                      "setup is in OS", tc_id, script_id, "None",
                      "None", log_level, tbd)
                    return True                                                 # Function exists by returning True if Simics Setup Display is successfully verified in OS
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Simics setup "
                "is not in OS",tc_id,script_id,"None","None",
                                  log_level,tbd)
                return False                                                    # Function exists by returning False if Display verification failed in OS
        elif "BIOS SETUP" == input.upper():                                     # This block will run if Simics setup display needs to be verified in BIOS SETUP
            cmd_for_bios = sikuli_exe + " " + sikuli_cmd_for_bios               # sikuli command to verify the Display in BIOS SETUP
            for count in range(5):                                              # Verifing display for 5 iterations
                Sikuli_execution = subprocess.Popen(cmd_for_bios, shell = False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE) # Executes the Sikuli file for verifying the display environment
                stdout, stderr = Sikuli_execution.communicate()
                if "PASS" in stdout:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Simics "
                      "setup is in BIOS Setup", tc_id, script_id, "None",
                      "None", log_level, tbd)
                    return True                                                 # Function exists by returning True if Simics Setup Display is successfully verified in BIOS SETUP
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Simics setup "
                "is not in BIOS Setup",tc_id,script_id,"None","None",
                                  log_level,tbd)
                return False                                                    # Function exists by returning False if Display verification failed in BIOS SETUP
        elif "UEFI" == input.upper():                                           # This block will run if Simics setup display needs to be verified in EFI SHELL
            cmd_for_edk = sikuli_exe + " " + sikuli_cmd_for_edk                 # sikuli command to verify the Display in EFI SHELL
            for count in range(5):                                              # Verifing display for 5 iterations
                Sikuli_execution = subprocess.Popen(cmd_for_edk, shell = False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                    stdin=subprocess.PIPE) # Executes the Sikuli file for verifying the display environment
                stdout, stderr = Sikuli_execution.communicate()
                if "PASS" in stdout:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Simics "
                      "setup is in EFI Shell", tc_id, script_id, "None",
                      "None", log_level, tbd)
                    return True                                                 # Function exists by returning True if Simics Setup Display is successfully verified in EFI SHELL
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Simics setup "
                "is not in EFI Shell",tc_id,script_id,"None","None",
                                  log_level,tbd)
                return False                                                    # Function exists by returning False if Display verification failed in EFI SHELL
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : Mentioned state is"
                " not handled",tc_id,script_id,"None","None",log_level,tbd)
            return False                                                        # Function exists by returning False if input other than OS/BIOS/EFI
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e ,
        tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # Function exists by returning False when Exception aries

################################################################################
# Function Name : capture_image
# Parameters    : test_case_id, script_id, log_level, tbd
# Functionality : captures display of SUT from host system
# Return Value  : returns True on success and False otherwise
################################################################################

def capture_image(ostr, test_case_id, script_id,
                  log_level = "ALL", tbd="None"):
    global camera
    try:
        usb_camera = utils.ReadConfig("DISPLAY", "USB_CAMERA")                  #get the information of usb camera from config entry
        port = utils.ReadConfig("TTK", "USB_CAMERA")                            #get the relay number from config file
        if "FAIL:" in [usb_camera , port]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
            " is not provided for usb camera", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #write warning message to log file if config entry is found missing
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry read"
            " successfully from config file" , test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #if config entry is found write successful message to log file

        if 0 == library.ttk_set_relay("ON", [int(port)]):                       # connect USB-Camera to host system
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: TTK action performed successfully",
                              test_case_id, script_id, "TTK", "None",
                              log_level, tbd)                                   #write pass message if ttk action is performed successfully

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                                                      "perform TTK action",
                              test_case_id, script_id,
                              "TTK", "None", log_level, tbd)                    #write warning message to log file if TTK action is not performed successfully
            return False, "FAIL"


        time.sleep(lib_constants.THREE)
        if "Connected" != lib_plug_unplug.check_device("camera", test_case_id,
            script_id, usb_camera, log_level, tbd):                             #function call to verify whether usb camera is connected to host system
            library.write_log(lib_constants.LOG_WARNING, "WARNING: USB Camera "
            "is not connected to host system", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #write warning message to log file if usb camera is not connected to host system

            return False, "FAIL"
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: USB Camera is "
            "detected in host system", test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #write message to log file if usb camera is connected to host system

        image_path = lib_constants.SCRIPTDIR + "\\" +\
                     script_id.split(".")[0] + ".jpg"                           #image path location

        if os.path.exists(image_path):
            os.remove(image_path)                                               #if the image already exists remove the image
        camera_port = 0
        ramp_frames = 30                                                        #Number of frames to throw away while the camera adjusts to light levels
        camera = cv2.VideoCapture(camera_port)                                  #initialize the camera capture object with the cv2.VideoCapture class.
        time.sleep(lib_constants.THREE)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)                              #enhance the captured image
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)                              #enhance the captured image
        time.sleep(lib_constants.THREE)

        for i in xrange(ramp_frames):                                           #Ramp the camera - these frames will be discarded and are only used to allow v4l2
            temp = get_image()

        camera_capture = get_image()                                            #capture image after discarding unwanted frames
        cv2.imwrite(image_path, camera_capture)                                 #save the image in script directory
        time.sleep(lib_constants.FIVE_SECONDS)
        del(camera)                                                             #release the camera after capture
        if os.path.exists(image_path) and (0 != os.path.getsize(image_path)):   #verify whether the image is captured
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT-Display  "
            " captured successfully from host system", test_case_id, script_id,
                             log_level, tbd)                                    #write message to log file

            if 0 == library.ttk_set_relay("OFF", [int(port)]):                  #relay action OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                    "performed successfully", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to disconnect USB camere from host system ", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)     #warning message to log file if failed to disconnect camera


            return True, image_path

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "capture sut display from host system", test_case_id, script_id,
                              log_level, tbd)                                   #write warning message to log file
            return False, "FAIL"

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " %e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #write exception message to log file
        return False

################################################################################
# Function Name : convert_image_to_text
# Parameters    : test_case_id, script_id, log_level, tbd
# Functionality : converts image to text and parses text file to verify input
#                 display
# Return Value  : returns drive_letter on success and False otherwise
################################################################################
def convert_image_to_text(device, test_case_id, script_id, log_level = "ALL",
                          tbd = "None"):
    try:
        tesseract_tool_path = utils.ReadConfig("DISPLAY", "TESSERACT_TOOL_PATH")#read the tesseract tool path from config file
        if "FAIL:" in tesseract_tool_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
            " is not provided for tesseract tool", test_case_id, script_id,
                              log_level, tbd)                                   #write warning message to log file if config entry is not provided
            return False
        os.chdir(tesseract_tool_path)                                           #change directory to tesseract tool path
        cmd = "tesseract "+ lib_constants.SCRIPTDIR +"\\" + \
              script_id.split(".")[0] +".jpg" + " "+\
              lib_constants.SCRIPTDIR + "\\"+ script_id .split(".")[0]          #command to convert image to text
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=False,
                                  stdin=subprocess.PIPE)               #execute command through sub process

        if ""!= output.communicate()[0]:                                        #if the command is not executed successfully
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
            "convert captured image to text file", test_case_id, script_id,
                             log_level, tbd)                                    #write warning message to log file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Captured image is "
            "successfully converted to text file", test_case_id, script_id,
                             log_level, tbd)                                    #write pass message to log file
        time.sleep(lib_constants.FIVE_SECONDS)                                  #delay of five seconds

        if device.upper() in lib_constants.SUT_DISPLAY:                         #if uefi is the display to be verified
            flag = False
            with codecs.open(lib_constants.SCRIPTDIR + "\\" +
                                     script_id.split(".")[0] + ".txt", "r",
                encoding='utf8') as file:                                       #open the log file to read the content of device(UEFI/BIOS/EDK)
                for line in file:                                               #reading log file
                    for word in lib_constants.device.upper()+"_DISPLAY":         #taking all the possible UEFI/EDK/BIOS contents stored in lib constants
                        if word in line:                                        #taking each  UEFI?EDK?BIOS contents stored in lib constants and comparing it with log file
                            flag = True                                         #if match is found assign flag to True
                            break
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Parameter "
            "not handled", test_case_id, script_id, log_level, tbd)             #write warning message to log file if parameter is not handled
            return False


        if flag:                                                                #if input display is verified
            library.write_log(lib_constants.LOG_INFO, "INFO: Image processing "
            "is completed successfully",test_case_id, script_id, log_level, tbd)#write pass message to log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "process the captured image", test_case_id, script_id, log_level,
                             tbd)                                               #write warning message to log file
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " %e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #write exception message to log file
        return False


###############################################################################
# Function Name : get_image
# Parameters    : none
# Functionality : To discard unwanted frames
# Return Value  : returns the actual image in matrix form
##############################################################################
def get_image():                                                                #Ramp the camera - these frames will be discarded and are only used to allow v4l2
    retval, im = camera.read()
    return im


################################################################################
# Function Name : verify_os_display
# Parameters    : device, test_case_id, script_id, log_level, tbd
# Functionality : Take screenshot of sut and verify whether it is in os or not
#                 based on pixel values.
# Return Value  : returns True on success and False otherwise
################################################################################


def verify_os_display(test_case_id, script_id, log_level="ALL", tbd="None"):

    try:
        image_path = lib_constants.SCRIPTDIR + "\\" + \
                     script_id.split(".")[0] + ".jpg"
        time.sleep(lib_constants.THREE)
        ImageGrab.grab().save(image_path, "JPEG")

        image = Image.open(image_path)

        colour_tuple = [None, None, None]
        for channel in range(3):
            pixels = image.getdata(band=channel)                                # Get data for one channel at a time
            values = []
            for pixel in pixels:
                values.append(pixel)

            colour_tuple[channel] = sum(values) / len(values)                   # Calculating average value for RGB

        rgb_pixel =  tuple(colour_tuple)                                        # typecasting to tuple

        r_clr_flag = False                                                      # Initializing rgb flags to False
        g_clr_flag = False
        b_clr_flag = False
        win_display = 0
        normal_display = 0
        if rgb_pixel[0] >= 0 and rgb_pixel[0] <= 30:                            # Here checking the range of window light emitting OS display pixel values:(10, 75, 130)
            r_clr_flag = True                                                   # Checking red color pixels values there within range or not
            win_display += 1
        if rgb_pixel[1] >= 60 and rgb_pixel[1] <= 90:                           # Checking for Green color range
            g_clr_flag = True
            win_display += 1
        if rgb_pixel[2] >= 115 and rgb_pixel[2] <= 145:                         # Checking for Blue color range
            b_clr_flag = True
            win_display += 1

        if rgb_pixel[0] >= 0 and rgb_pixel[0] <= 30:                            #Here checking the range of dark blue OS screen pixel values:(18, 19, 75)
            r_clr_flag = True                                                   # Checking red color pixels values there within range or not
            normal_display += 1
        if rgb_pixel[1] >= 0 and rgb_pixel[1] <= 30:                            # Checking for Green color range
            g_clr_flag = True
            normal_display += 1
        if rgb_pixel[2] >= 60 and rgb_pixel[2] <= 90:                           # Checking for Blue color range
            b_clr_flag = True
            normal_display += 1

        if normal_display == 3 or win_display == 3:                             #If all are satisfied then it is verifying that SUT is in OS
            library.write_log(lib_constants.LOG_INFO, "INFO: Image processing "
            "is completed successfully", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Write pass message to log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "process the captured image", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Write warning message to log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " % e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Write exception message to log file
        return False