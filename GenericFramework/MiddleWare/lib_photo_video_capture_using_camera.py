__author__ = r'nareshgx\tnaidux'

# General Python Imports
import codecs
import cv2
import numpy
import os
import pyautogui
import _thread
import wmi
import time
from win32api import GetSystemMetrics
from datetime import datetime

# Local Python Imports
import lib_constants
import library
import utils

# Global constants
file_path = []

################################################################################
# Function Name : lib_photo_video_capture
# Parameters    : original_string, test_case_id, script_id, log_level, tbd
# Return Value  : True and filepath on sceessful action, False otherwise
# Purpose       : To capture photo and video using camera
# Target        : SUT
################################################################################


def lib_photo_video_capture(original_string, test_case_id, script_id,
                            log_level="ALL", tbd=None):

    try:
        if "photo" in original_string.lower():
            capture_type = "photo"
        else:
            capture_type = "video"
        
        if "uf" in original_string.lower():
            camera_type = "UF"
            camera_index = 0
        elif "USB" in original_string.lower() or \
                        "USB2.0" in original_string.lower() or \
                        "USB3.0" in original_string.lower():
            camera_type = "USB_Camera"
            camera_index = 0
        elif "wf" in original_string.lower():
            camera_type = "WF"
            camera_index = 1
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Camera type"
                              " is not supported", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False, "FAIL"

        if "normal" in original_string.lower():
            mode = "Normal"
        elif "burst" in original_string.lower():
            mode = "Photo_burst"
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: mode is "
                              " not implemented", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False, "FAIL"

        if ("minutes" in original_string.lower() or
            "minute" in original_string.lower()) and \
                "video" in original_string.lower():
            try:
                minutes = original_string.lower().split("minute")[0]
                duration = str(minutes).split(" ")[1]
            except:
                minutes = original_string.lower().split("minutes")[0]
                duration = minutes.split(" ")[11]
            duration = int(duration) * 60
        elif "seconds" in original_string.lower() and "video" in \
                original_string.lower():
            minutes = original_string.split(" ")
            duration = utils.extract_parameter_from_token(minutes, "CAPTURE",
                                                          "VIDEO")
            duration = int(duration)
        else:
            duration = 1
        if "photo" == capture_type.lower():                                     # If capture type is photo call photo capture function
            status, file_path = photo_capture(camera_index, duration, mode,
                                              test_case_id, script_id,
                                              log_level, tbd)
        elif "video" == capture_type.lower():                                   # If capture type is video call video capture function
            status, file_path = video_capture(camera_index, duration, mode,
                                              test_case_id, script_id,
                                              log_level, tbd)

        if status:
            return True, file_path                                              # return True and file path of captured image or video
        else:
            return False, 'FAIL'
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False, "FAIL"

################################################################################
# Function Name : photo_capture
# Parameters    : camera_index, time, mode, test_case_id, script_id, log_level,
#                 tbd
# Return Value  : returns true and file path
# Purpose       : to capture image and return true and file path
# Target        : SUT
################################################################################


def photo_capture(camera_index, duration, mode, test_case_id, script_id,
                  log_level="ALL", tbd=None):                                   # Photo capture function

    try:
        if duration == "None":
            duration = lib_constants.ONE
        else:
            duration = int(duration)

        for seq in range(duration):
            global file_path
            camera = cv2.VideoCapture(camera_index)
            width = GetSystemMetrics(0)
            height = GetSystemMetrics(1)
            camera.set(3, width)
            camera.set(4, height)
            reval, img = camera.read()
            file = script_id.replace(".py", "") + "-" + str(seq) + ".png"

            if "grayscale" == mode:                                             # Set grayscale properties to camera frame
                mode_col = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif "negative" == mode:                                            # Set negative properties to camera frame
                mode_col = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
            elif "sepia" == mode:                                               # Set sepia properties to camera frame
                m_sepia = numpy.asarray([[0.393, 0.769, 0.189],
                                         [0.349, 0.686, 0.168],
                                         [0.272, 0.534, 0.131]])
                mode_col = cv2.transform(img, m_sepia)
            else:                                                               # Set normal properties to camera frame
                mode_col = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

            cv2.imwrite(file, mode_col)
            file_path.append(os.path.abspath(file))
            camera.release()
            cv2.destroyAllWindows()

            if not os.path.exists(os.path.abspath(file)):                       # If captured file found pass else fail
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to capture image with %s mode" % mode,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False, 'FAIL'
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Captured "
                                  "image with %s mode successfully" % mode,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True, os.path.abspath(file)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False, "FAIL"

################################################################################
# Function Name : video_capture
# Parameters    : camera_index, duration, mode, test_case_id, script_id,
#                 log_level, tbd
# Return Value  : returns true and file path
# Purpose       : to capture video and return true and file path
# Target        : SUT
################################################################################


def video_capture(camera_index, duration, mode, test_case_id, script_id,
                  log_level="ALL", tbd=None):                                   # Video capture function

    try:
        video_file = script_id + ".mp4"                                      # Set video file name
        fps = 30.0
        if os.path.exists(os.path.abspath(video_file)):
            os.remove(os.path.abspath(video_file))

        cap = cv2.VideoCapture(camera_index)
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)
        cap.set(3, width)
        cap.set(4, height)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')                                # To specify the video codec
        out = cv2.VideoWriter(video_file, fourcc, fps, (int(cap.get(3)),
                                                        int(cap.get(4))))       # Desired FPS of the output video file
        thread.start_new_thread(run_cam, (cap, out, mode))
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            out.write(frame)
            final_time = time.time()
            elapsed = final_time - start_time
            if elapsed > duration:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        if not os.path.exists(os.path.abspath(video_file)):                     # Check file exists or not if doesn't return False with fail comment
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "capture video with %s mode" % mode,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False, 'FAIL'
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Captured video "
                              "with %s mode successfully" % mode, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            captured_video = os.path.abspath(video_file)
            return True, captured_video

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False, "FAIL"

################################################################################
# Function Name : run_cam
# Parameters    : cap, out, mode
# Return Value  : None
# Purpose       : thread call to keep open camera
# Target        : SUT
################################################################################


def run_cam(cap, out, mode):                                                    # Camera launch and file save function

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if ret is True:
                if "grayscale" == mode:                                         # Grayscale mode settings
                    mode_col = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                elif "negative" == mode:                                        # Negative  mode settings
                    mode_col = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
                elif "sepia" == mode:                                           # Sepia mode settings
                    m_sepia = numpy.asarray([[0.393, 0.769, 0.189],
                                             [0.349, 0.686, 0.168],
                                             [0.272, 0.534, 0.131]])
                    mode_col = cv2.transform(frame, m_sepia)
                else:
                    mode_col = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)          # Else normal mode

                cv2.imshow('frame', mode_col)
                out.write(mode_col)                                             # Write the frame

                if cv2.waitKey(1) & 0xFF == ord('q'):                           # Close window if esc or q is sent from keyboard
                    break
            else:
                break
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          "None", "None", "None", "None", "None", "None")
        return False, "FAIL"
