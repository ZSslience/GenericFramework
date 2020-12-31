__author__ = 'kashokax/mmakhmox'

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
import lib_constants
import utils
import lib_plug_unplug
import lib_press_button_on_board
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
        try:
            ostr_display = ostr.split(" ")[2]
        except:
            ostr_display = False

        try:
            for filename in os.listdir("."):
                if filename.endswith("json"):                                   # Searching for Json file
                    with open(filename, "r") as _f:
                        data = json.load(_f)                                    # Reading which display have to verify from json file
                        display_type = data["Display"]
                        display_type = display_type.split("-")[0]
                else:
                    display_type = False
        except:
            display_type = False

        if "CAPTURE SCREEN" in ostr.upper() and ostr_display:
            display_type = ostr.split(" ")[-1]
            display_type = display_type + "_CAMERA"
            usb_camera = utils.ReadConfig("DISPLAY", display_type)              # get the information of usb camera from config entry
            port = utils.ReadConfig("TTK", display_type)
            if 0 == library.ttk_set_relay("ON", [int(port)]):  # relay action ON
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: TTK action performed successfully",
                                  test_case_id, script_id, "TTK", "None",
                                  log_level, tbd)

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                                  "perform TTK action",
                                  test_case_id, script_id,
                                  "TTK", "None", log_level, tbd)
                return False, "FAIL"

        elif "VERIFY" in ostr.upper() and display_type:
            if display_type:
                display_type = display_type + "_CAMERA"
                usb_camera = utils.ReadConfig("DISPLAY", display_type)          # get the information of usb camera from config entry
                port = utils.ReadConfig("TTK", display_type)
                if 0 == library.ttk_set_relay("ON", [int(port)]):               # relay action ON
                    library.write_log(lib_constants.LOG_INFO,
                            "INFO: TTK action performed successfully",
                                      test_case_id, script_id, "TTK", "None",
                                      log_level, tbd)

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                            "perform TTK action", test_case_id, script_id,
                            "TTK", "None", log_level, tbd)
                    return False, "FAIL"
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Unable to find the camera from Json"
                                  " file which cold plugged.",
                                  test_case_id, script_id, "None",
                                  "None", log_level,tbd)                        # write warning message to log file if camera not found from json
                return False, "FAIL"


        else:
            usb_camera = utils.ReadConfig("DISPLAY", "USB_CAMERA")              #get the information of usb camera from config entry
            port = utils.ReadConfig("TTK", "USB_CAMERA")
            if 0 == library.ttk_set_relay("ON", [int(port)]):  # relay action ON
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: TTK action performed successfully",
                                  test_case_id, script_id, "TTK", "None",
                                  log_level, tbd)

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                                                          "perform TTK action",
                                  test_case_id, script_id,
                                  "TTK", "None", log_level, tbd)
                return False, "FAIL"

        if "FAIL:" in usb_camera:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
            " is not provided for usb camera", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #write warning message to log file if config entry is missing
            if 0 == library.ttk_set_relay("OFF", [int(port)]):                  # relay action OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                    "performed successfully", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
            return False, "FAIL"

        time.sleep(3)
        if "Connected" != lib_plug_unplug.check_device("camera", test_case_id,
            script_id, usb_camera, log_level, tbd):                             #function call to verify whether usb camera is connected to host system
            library.write_log(lib_constants.LOG_WARNING, "WARNING: USB Camera "
            "is not connected to host system", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #write warning message to log file if usb camera is not connected to host system

            if 0 == library.ttk_set_relay("OFF", [int(port)]):                  # relay action OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                    "performed successfully", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
            return False, "FAIL"
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: USB Camera is "
            "detected in host system", test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #write message to log file if usb camera is connected to host system

        image_path = lib_constants.SCRIPTDIR + "\\" +\
                     script_id.split(".")[0] + ".jpg"

        if os.path.exists(image_path):
            os.remove(image_path)                                                   #if the image already exists remove the image
        camera_port = 0
        ramp_frames = 30                                                        #Number of frames to throw away while the camera adjusts to light levels
        camera = cv2.VideoCapture(camera_port)                                  #initialize the camera capture object with the cv2.VideoCapture class.
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        for i in range(ramp_frames):                                           #Ramp the camera - these frames will be discarded and are only used to allow v4l2
            temp = get_image()

        camera_capture = get_image()                                            #capture image after discarding unwanted frames
        cv2.imwrite(image_path, camera_capture)                                     #save the image in script directory
        time.sleep(lib_constants.FIVE_SECONDS)
        del(camera)                                                             #release the camera after capture
        if os.path.exists(image_path):            #verify whether the image is captured
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT-Display  "
            " captured successfully from host system", test_case_id, script_id,
                             log_level, tbd)                                    #write message to log file

            if 0 == library.ttk_set_relay("OFF", [int(port)]):                  # relay action OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                    "performed successfully", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)

            return True, image_path

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "capture sut display from host system", test_case_id, script_id,
                              log_level, tbd)                                   #write warning message to log file

            if 0 == library.ttk_set_relay("OFF", [int(port)]):                  # relay action OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                    "performed successfully", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
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
        time.sleep(lib_constants.TEN_SECONDS)                                   #delay of five seconds

        if "UEFI" in device.upper() or "EDK SHELL" in device.upper():                                            #if uefi is the display to be verified
            flag = False
            with codecs.open(lib_constants.SCRIPTDIR + "\\" +
                                     script_id.split(".")[0] + ".txt", "r",
                encoding='utf8') as file:                                       #open the log file to read the content of UEFI from log file
                for line in file:                                               #reading log file
                    for word in lib_constants.UEFI_DISPLAY:                     #taking all the possible UEFI contents stored in lib constants
                        if word in line:                                        #taking each  UEFI contents stored in lib constants and comparing it with log file
                            flag = True                                         #if match is found assign flag to True
                            break

        elif "BIOS SETUP" in device.upper():                                    #if uefi is the display to be verified
            flag = False
            with codecs.open(lib_constants.SCRIPTDIR + "\\" +
                                     script_id.split(".")[0] + ".txt", "r",
                             encoding='utf8') as file:                          #open the log file to read the content of BIOS setup page from log file
                for line in file:                                               #reading log file
                    for word in lib_constants.BIOS_SETUP:                       #taking all the possible BIOS contents stored in lib constants
                        if word in line:                                        #taking each BIOS contents stored in lib constants and comparing it with log file
                            flag = True
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
            print(pixels)
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

        if normal_display == 3 or win_display == 3:                            # If all are satisfied then it is verifying that SUT is in OS
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


def verify_display_using_mirabox(environment, test_case_id, script_id,
                                 log_level="ALL", tbd="None"):
    try:
        from lib_vision import Vision
        screenshot_name = script_id.replace('.py', '.png')
        log_name = script_id.replace('.py', '')
        screenshot_path = lib_constants.SCRIPTDIR + os.sep + screenshot_name
        image_to_txt_file_name = lib_constants.SCRIPTDIR + os.sep + log_name
        vision_obj = Vision(screenshot_path, image_to_txt_file_name)
        try:
            screen_text = vision_obj.capture_screen_text()

            environment_page_dict = {
                "UEFI": "vision_obj.verify_efi_screen(screen_text)",
                "BIOS SETUP": "vision_obj.verify_bios_screen(screen_text)",
                "OS": "vision_obj.verify_os_screen(screen_text)"
            }
            return_value = eval(environment_page_dict.get(environment.upper()))

            if return_value is True:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Successfully verified %s display"
                                  % environment, test_case_id,
                                  script_id, "None",
                                  "None", log_level,
                                  tbd)                                          # Write pass message to log file
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to verify %s display"
                                  % environment, test_case_id,
                                  script_id, "None",
                                  "None", log_level,
                                  tbd)                                          # Write warning message to log file
                return False
        except Exception as e_obj:
            if str(e_obj) == "not enough image data":
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Video Capture device window is not"
                                  " active", test_case_id, script_id, "None",
                                  "None", log_level, tbd)                       # Write exception message to log file
            else:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Due to %s " % e_obj,
                                  test_case_id, script_id, "None", "None",
                                  log_level,
                                  tbd)                                          # Write exception message to log file
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " % e_obj,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  # Write exception message to log file
        return False


def close_vision_test_app_in_sut(test_case_id, script_id, log_level="ALL",
                                 tbd="None"):
    try:
        cmd = 'taskkill /f /im VisionTestApp.exe'
        result = utils.execute_with_command(cmd, test_case_id, script_id,
                                            log_level, tbd)
        if result.return_code == lib_constants.RETURN_SUCCESS:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "closed the VisionTestApp.exe application",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        elif r'"VisionTestApp.exe" not found' in result.stderr:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: VisionTestApp.exe "
                              "process is currently not running",
                              test_case_id, script_id, "None",
                              "None", log_level, tbd)                           # Write warning message to log file
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " % e_obj,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  # Write exception message to log file
        return False


def launch_vision_test_app(test_case_id, script_id, log_level="ALL",
                           tbd=None):                                           # Boot order change in EDK shell
    try:
        from KBM_Emulation import USBKbMouseEmulation
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get com port details or input device name from "
                              "Config.ini ", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           # Failed to get info from config file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name is identified as %s %s from "
                              "config.ini" % (port, input_device_name),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        keyboard_obj = USBKbMouseEmulation(input_device_name, port)
        time.sleep(lib_constants.FIVE_SECONDS)
        keyboard_obj.key_press("KEY_GUI r")                                     #pressing enter key
        time.sleep(lib_constants.FIVE_SECONDS)
        keyboard_obj.key_type("cmd")                                            #sending cmd text to launch cmd prompt
        time.sleep(lib_constants.TWO_SECONDS)
        keyboard_obj.key_press("KEY_ENTER")                                     #pressing enter key
        time.sleep(lib_constants.FIVE_SECONDS)
        keyboard_obj.key_type(r"cd C:\Testing\GenericFramework\Tools\Vision"
                              r"\VisionTest")
        keyboard_obj.key_press("KEY_ENTER")                                     #pressing enter key
        time.sleep(lib_constants.THREE)
        keyboard_obj.key_type(r"VisionTestApp.exe VisionTestOSTemplate.png 120")
        keyboard_obj.key_press("KEY_ENTER")
        time.sleep(lib_constants.FIVE_SECONDS)
        library.write_log(lib_constants.LOG_INFO, "INFO: Keys sent from "
                          "keyboard-mouse simulator to launch VisionTestApp.exe"
                          " application", test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
