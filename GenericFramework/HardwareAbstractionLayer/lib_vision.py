"""
########################################################################################################################
# GHERKIN PRIMITIVE ACTION DESCRIPTION                                                                                 #
#                                                                                                                      #
# Title: Vision.py                                                                                                     #
# Author: Luongt														                                               #
# Date Created: <10/01/2017>	    						  			                                               #
#                                                                                                                      #
# Description: Can read screen text and determine what state sut is in.                                                #
#                                                                		                                               #
# Prerequisites:															                                           #
#  - state: OBS open and can monitor the SUT                                                                           #
#  - files: Capture2Text exists somewhere on executor                                                                  #
#                                                                                                                      #
# Modification History:                                                                                                #
# Name       Date                  Reason			                                                                   #
#                                                                                                                      #
# Thomas     10/01/17    Functions to capture SUT screen text and verify which state the SUT is in                     #
# Thomas     11/09/17    Add additional step to verify removed screen shot does not exist after deletion               #
# Brett      11/27/17    Add ability to check if on securtity (ctrl + alt + del) screen                                #
# Renjith    02/16/18    Code refactoring to PEP8 standards. Phase #4                                                  #
# Thomas     02/21/18    Add ability to change Vision's window title that it looks for to read screenText              #
#                           (useful to enable screen reading from Raritan)                                             #
# Thomas     02/26/18    Add step to check if screen has any of the known phrases from any of the dictionaries         #
# Thomas     04/04/18    Stability increase for Internal EDK Shell screen by adding phrase "UEFI"                      #
# Renjith    04/11/18    Enhancement to avoid the vision window size dependency and border shades                      #
# Thomas     04/17/18    Remove extra entries from raritan Toolbar when using Raritan Vision                           #
# Michael    05/09/18    Added multithreading methods look_to_see_if_in_state and look_to_see_if_in_state_async;       #
#                            Added __take_screenshot to use new __get_adjusted_rect function                           #
# Renjith    19/24/19    Added functionality to search for a text in the the screen                                    #
# Renjith    11/13/19    Refactor and custom screen text capture functionality                                         #
########################################################################################################################
"""

########################################################################################################################
# PYTHON IMPORTS                                                                                                       #
########################################################################################################################
import os
import subprocess
import time
from datetime import timedelta, datetime
from ctypes import windll
import threading
import codecs


# 01/23/20202 - to avoid the multiple dependency with other gherkin libraries, Commenting the below imports
# and adding a workaround - START

# from lib_gherkin import gk_Log, Success, Failure, CAPTURE2TEXT_PATH
# from Common import SYNCEVENT, GKTimer

TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Results
Success = True
Failure = False
class GKLog(object):
    def info(self, message):
        print(message)
    def error(self, message):
        print(message)

gk_Log = GKLog()

SYNCEVENT = threading.Event()


class GKTimer(object):
    """
        This is a timer class. Usage is as follows.
        timer = GKTimer()
        while timer.timeup(duration):
            do your task
    """
    def __init__(self):
        self.__start_time = time.time()
        self.__end_time = None

    def __set_end_time(self, duration):
        """
        __set_end_time(): Set the end time
        :param duration: Timeout duration in seconds
        :return: n/a
        """
        self.__end_time = self.__start_time + int(duration)

    def __get_end_time(self):
        """
        __get_end_time()
        :return: timer end time from the start time.
        """
        if self.__end_time:
            return self.__end_time
        else:
            str_error = u"Timer's end_time was not initialized"
            # gk_Log.exception(str_error)
            raise ValueError(str_error)

    def timeup(self, duration):
        """
        timeup(): Checks whether the timeout is reached or not. (Loop has to be implemented by the caller)
        :param duration: Duration in seconds
        :return: True if the time is elapsed else False.
        """

        if not self.__end_time:  # Set the timer duration.
            self.__set_end_time(duration)

        is_time_not_over = time.time() < self.__get_end_time()

        if not is_time_not_over:  # Time over
            self.__end_time = None

        return is_time_not_over

# 01/23/20202 - to avoid the multiple dependency with other gherkin libraries - END

# Screenshot libraries
import win32con
import win32gui
import win32ui

from PIL import Image

from win32api import GetSystemMetrics


class Vision(object):
    """
        Vision class Implementation
    """
    def __init__(self, screenshot_path, log_name):
        self.screenshot_path = screenshot_path
        self.txt_file_name = log_name
        self.target_window_title = u'Windowed Projector (Source) - Video Capture Device'

        self.bios_phrases = [u"Intel Advanced Menu",
                             u"Boot Manager Menu",
                             u"Select Language",
                             u"Platform Information",
                             u"Boot Configuration Menu",
                             u"Continue",
                             u"Reset",
                             u"F2=Discard Changes",
                             u"F3=Load Defaults"]

        self.os_phrases = [u"VISION",
                           u"vision",
                           u"WINDOWS",
                           u"Recycle"]

        self.efishell_phrases = [u"Press ESC",
                                 u"PciRoot(0x0)",
                                 u"startup.nsh",
                                 u"other key to continue",
                                 u"Mapping table",
                                 u"UEFI Interactive Shell",
                                 u"Shell",
                                 u"Alias(s)"]

        self.blueboot_device_menu_phrases = [u"Boot Manager",
                                             u"ESC to exit",
                                             u"Enter to select boot device",
                                             u"to move selection",
                                             u"Enter Setup",
                                             u"Internal EDK Shell",
                                             u"UEFI Internal Shell"]

        self.boot_mgr_menu_phrases = [u"Device Path",
                                      u"Discard Changes",
                                      u"keys to choose a boot option",
                                      u"key to exit the Boot"]

        # These are the phrases for Win 10. It may different for other versions
        self.security_screen_phrases = [u"Lock",
                                        u"Switch user"
                                        u"Sign out",
                                        u"Change a password",
                                        u"Task Manager",
                                        u"Cancel"]
    @classmethod
    def _capture_text_from_image(self, image_file, txt_file_name, verbose=False):
        """
        Core method the capture the text from the specified image
        :param image_file: image file
        :param white_list: text characters to be considered for extraction
        :param black_list: text characters to be ignored
        :param verbose:
        :return:
        """
        start_time = datetime.now()

        capture_to_txt_arguments = TESSERACT_PATH + " " + image_file + " " +\
                                   txt_file_name

        proc = subprocess.Popen(capture_to_txt_arguments, stdout=subprocess.PIPE)
        proc.communicate()

        log_file = txt_file_name + ".txt"
        if os.path.exists(log_file):
            f = open(log_file, encoding='utf-8')
            screen_text = f.read()
            f.close()
        else:
            screen_text = None

        if verbose:
            gk_Log.info(screen_text)
        endtime = datetime.now() - start_time
        gk_Log.info(u"Time to do OCR on image is: " + str(endtime))

        return screen_text


    def custom_capture_screen_text(self, white_list, black_list, verbose=False):
        """
        Take screenshot and extract text based on specified whitelist and blacklist
        :param white_list:
        :param black_list:
        :param verbose:
        :return:
        """
        self._take_screenshot()
        screen_text = self._capture_text_from_image(self.screenshot_path,
                                                    self.txt_file_name,
                                                    verbose=verbose)
        return screen_text

    def capture_screen_text(self, verbose=False):
        """
        Takes screenshot of OBS window, then passes image file to Capture2Text to get text from image
        :param verbose: Boolean for if debug statements to be printed out (time it takes to do OCR)
        :return: screen_text string of the captured text from OBS screenshot
        """

        self._take_screenshot()
        white_list_chars = u'"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\\/:!@#$%^&*()_+-=<>?,' \
                           u'./[]{}"'
        screen_text = self._capture_text_from_image(self.screenshot_path,
                                                    self.txt_file_name,
                                                    verbose=verbose)
        return screen_text

    def _remove_screenshot(self):
        """
        Removes the old screenshot file
        :return: None
        """
        try:
            if os.path.isfile(self.screenshot_path):
                os.remove(self.screenshot_path)

            if os.path.isfile(self.screenshot_path):
                raise Exception(u" File is not removed")
        except Exception as ex:
            str_error = u'Image file still exists even after attempting to remove: ' \
                        u'{0}, {1}'.format(self.screenshot_path, ex)
            gk_Log.error(str_error)
            raise Exception(str_error)

    def _verify_screenshot(self):
        """
        Ensures screenshot is available to be parsed
        :return: Boolean - True if screenshot is available
        """
        try:
            if os.path.isfile(self.screenshot_path):
                return True
            return False

        except Exception as ex:
            str_error = u'Image file is not in expected path: {0}, {1}'.format(self.screenshot_path, ex)
            gk_Log.error(str_error)
            raise Exception(str_error)

    def set_target_window_title(self, target_window_title):
        """
        Change the title of the window that Vision will read the screen text from
        :param target_window_title: window handle name to read text from
        :return:
        """
        self.target_window_title = target_window_title

    @staticmethod
    def __get_adjusted_rect(client_left, client_top, client_right, client_bottom, window_handle):
        """
        Takes the boounds of the client area of a window and returns the total size of the window
        :param client_left:   left coordinate
        :param client_right:  right coordinate
        :param client_top:    top coordinate
        :param client_bottom: bottom coordinate
        :param window_handle: handle of window to adjust
        :return: new window rect coordinates
        """
        width = client_right - client_left
        height = client_bottom - client_top

        win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(window_handle)
        win_width = win_right - win_left
        win_height = win_bottom - win_top

        adj_right = win_right - width + win_width
        adj_bottom = win_bottom - height + win_height

        return win_left, win_top, adj_right, adj_bottom

    def _take_screenshot(self):
        """
        Take a screenshot of a desired non-minimized window.
        :return: None, saves screenshot file to temp file
        """

        # Gets the current resolution of the executor
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)

        hwnd = win32gui.FindWindow(None, self.target_window_title)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, width, height, win32con.SWP_SHOWWINDOW)
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        ad_left, ad_top, ad_right, ad_bottom = self.__get_adjusted_rect(left, top, right, bottom, hwnd)

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, ad_left, ad_top, ad_right, ad_bottom, win32con.SWP_SHOWWINDOW)
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bot - top

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)

        save_dc.SelectObject(save_bitmap)

        # Change the line below depending on whether you want the whole window or just the client area.
        capture_whole_window = 1  # or 0
        windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), capture_whole_window)

        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)

        image = Image.frombuffer(u'RGB', (bmpinfo[u'bmWidth'], bmpinfo[u'bmHeight']), bmpstr, u'raw', u'BGRX', 0, 1)

        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        self._remove_screenshot()

        verify_count = 0

        while not self._verify_screenshot() and verify_count < 5:
            verify_count += 1
            image.save(self.screenshot_path, u"png", optimize=True, quality=100)
            time.sleep(2.0)

    def verify_os_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in os_phrases dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.os_phrases:
            if phrase in screen_text:
                log_msg = u"\n We're in Operating System, line found: " + phrase + u'\n'
                gk_Log.info(log_msg)
                return True
        return False

    def verify_bios_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in bios_phrases dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.bios_phrases:
            if phrase in screen_text:
                log_msg = u"\n We're in BIOS menu, line found: " + phrase + u'\n'
                gk_Log.info(log_msg)
                return True
        return False

    def verify_blueboot_device_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in blueBootDeviceMenu dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.blueboot_device_menu_phrases:
            if phrase in screen_text:
                log_msg = u"\n We're in blue boot device menu, line found: " + phrase + u'\n'
                gk_Log.info(log_msg)
                return True
        return False

    def verify_efi_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in efishell_phrases dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.efishell_phrases:
            if phrase in screen_text:
                log_msg = u"\n We're in EFI Shell, line found: " + phrase + u'\n'
                gk_Log.info(log_msg)
                return True
        return False

    def verify_bootmanager_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in boot_mgr_menu_phrases dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.boot_mgr_menu_phrases:
            if phrase in screen_text:
                log_msg = u"\n We're in the Boot Manager Menu, line found: " + phrase + u'\n'
                gk_Log.info(log_msg)
                return True
        return False

    def verify_windows_security_screen(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in security_screen_phrases dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        for phrase in self.security_screen_phrases:
            if phrase in screen_text:
                log_msg = (
                    u"\n We're in the Windows Security (ctrl alt del) screen "
                    u"line found: " + phrase + u"\n"
                )
                gk_Log.info(log_msg)
                return True
        return False

    def verify_screen_by_type(self, screen_type, max_duration):
        """
        verify the screen with a known template.
        :param screen_type: the template type (Its a function pointer)
        :param max_duration: the duration to wait.
        :return: Success when the screen type is seen within the specified time. Else will return failure
        """
        seconds_between_each_attempt = 1
        timer = GKTimer()
        start_time = datetime.now()
        while timer.timeup(max_duration):
            screen_text = self.capture_screen_text(True)
            if screen_type(screen_text):
                time_passed = start_time + timedelta(seconds=int(max_duration)) - datetime.now()
                time_passed = str(int(max_duration) - time_passed.total_seconds())
                time_passed_msg = u'SUT verified via Vision to be in {0} in {1} seconds.'.format(screen_type.__name__,
                                                                                                 time_passed)
                gk_Log.info(time_passed_msg)
                return Success
            time.sleep(seconds_between_each_attempt)
        return Failure

    def verify_screen_by_text(self, text, max_duration):
        """
        verify the screen has the specified test.
        :param text: the text to be searched in screen
        :param max_duration: the duration to wait.
        :return: Success when the screen has the specified text within the specified time. Else will return failure
        """
        seconds_between_each_attempt = 1
        timer = GKTimer()
        start_time = datetime.now()
        while timer.timeup(max_duration):
            screen_text = self.capture_screen_text(True)
            if text in screen_text:
                time_passed = start_time + timedelta(seconds=int(max_duration)) - datetime.now()
                time_passed = str(int(max_duration) - time_passed.total_seconds())
                time_passed_msg = u'SUT verified via Vision to have text {0} in {1} seconds.'.format(text, time_passed)
                gk_Log.info(time_passed_msg)
                return Success
            time.sleep(seconds_between_each_attempt)
        return Failure

    def check_screen_text_for_known_phrases(self, screen_text):
        """
        Check if the screen_text has any substring that is defined in any dictionary
        :param screen_text: text returned from Capture2Text
        :return: Boolean of whether a substring is found in screen_text
        """
        dictionaries = [self.security_screen_phrases,
                        self.bios_phrases,
                        self.blueboot_device_menu_phrases,
                        self.boot_mgr_menu_phrases,
                        self.efishell_phrases,
                        self.os_phrases]

        for phrase_dict in dictionaries:
            for phrase in phrase_dict:
                if phrase in screen_text:
                    log_message = u"Screen text has the known phrase of: " + phrase
                    gk_Log.info(log_message)
                    return True
        return False

    def get_device_index_in_bootdevice(self, target_device, screen_text):
        """
        Primarily for Blue Boot Device Menu, we determine what index a device is in, given the screen_text
        :param target_device: The name of the device as shown in the Blue Boot Device Menu
                This is best to do a unique substring of the expected device listing, since OCR may not capture
                the entire device listing name correctly

        :param screen_text: The captured text from Blue Boot Device Menu
        :return: Int of a zero-based index value of where device was found in the string of devices
                if not found, will return -1
        """
        try:
            boot_devices = screen_text.split('\n')
            if u'active kvm client' in self.target_window_title.lower():
                # Raritan is used, toolbar text should be removed, aka any text prior to 'please'
                list_start_index = [i for i, s in enumerate(boot_devices) if 'please' in s.lower()][0]
                boot_devices = boot_devices[list_start_index:]

            # Filter out all strings with no value
            # remove entry of "Please select boot device" and lines that are empty
            filtered_boot_devices = [s for s in boot_devices if len(s) > 2 and not s.lower().startswith("please")]
            device_index = -1
            for i, boot_entry in enumerate(filtered_boot_devices):
                if target_device in boot_entry:
                    device_index = i
                    info_log = u'Blue Boot Device Menu Device ' + target_device + u' found in index: ' + \
                               str(device_index)
                    gk_Log.info(info_log)
                    break
            return device_index
        except Exception as ex:
            str_error = u'Unable to determine device index from blue boot device menu screen text : ' + str(ex)
            gk_Log.error(str_error)
            raise Exception(str_error)

    @classmethod
    def __filter_boot_devices(cls, boot_device):
        """
        Helper to filter out entries that are not valid boot devices.
        :param boot_device: Boot device entry to filter against
        :return: Returns True if device appears to be valid, False otherwise
        """
        non_boot_devices = [u"device", u"boot"]
        if len(boot_device) < 2:
            return False
        if boot_device[0].isdigit():
            return False
        for non_device in non_boot_devices:
            if boot_device.lower().startswith(non_device):
                return False
        return True

    def get_device_index_in_bootmanager(self, target_device, screen_text):
        """
        Primarily for Boot Manager Menu, we determine the index of a device in the list
        :param target_device: The name of the device as shown in the Boot Manager Menu
                This is best to do a unique substring of the expected device listing, since OCR may not capture
                the entire device listing name correctly
        :param screen_text: The captured text from Boot Manager Menu
        :return: Int of a zero-based index value of where device was found in the string of devices
                if not found, will return -1
        """
        try:
            boot_devices = screen_text.split('\r\n')
            filtered_boot_devices = filter(self.__filter_boot_devices, boot_devices)

            if u'active kvm client' in self.target_window_title.lower():
                # Raritan is used, toolbar text should be removed, aka any text prior to 'boot manager'
                try:
                    list_start_index = [i for i, s in enumerate(boot_devices) if u'boot manager' in s.lower()][0]
                    filtered_boot_devices = boot_devices[list_start_index:]
                except Exception as ex:
                    str_error = u"The phrase 'boot manager' was not found in the screen text, " + str(ex)
                    gk_Log.info(str_error)
                    raise Exception(str_error)

            device_index = -1
            for i, boot_entry in enumerate(filtered_boot_devices):
                if target_device.lower() in boot_entry.lower():
                    device_index = i
                    info_log = u'Boot Manager Menu Device {0} found at index: {1}'.format(target_device, device_index)
                    gk_Log.info(info_log)
                    break
            return device_index
        except Exception as ex:
            str_error = u'Unable to determine device index from Boot Manager Menu screen text :' + str(ex)
            gk_Log.error(str_error)
            raise Exception(str_error)

    def look_to_see_if_in_state(self, sut_state, time_total):
        """
        Thread function to check if SUT is in state
        :param sut_state: OS/EFI/BIOS/Bootmenu/Security menu, etc
        :param time_total: Time limit for confirming sut_state
        :return:
        """
        if sut_state.lower() in [u'blue boot device menu']:
            verify_correct_sut_state = self.verify_blueboot_device_screen
        elif sut_state.lower() in [u'bios menu', u'bios']:
            verify_correct_sut_state = self.verify_bios_screen
        else:
            raise Exception(u'Incorrect sut state option, try blue boot device menu or BIOS menu')

        start_time = datetime.now()
        timed_out = False

        while not SYNCEVENT.isSet() and not timed_out:
            timed_out = datetime.now() > (start_time + timedelta(seconds=int(time_total)))
            screen_text = self.capture_screen_text(True)
            if verify_correct_sut_state(screen_text):
                SYNCEVENT.set()
            else:
                time.sleep(0.5)

        elapsed_time = str(datetime.now() - start_time)

        if SYNCEVENT.isSet():
            gk_Log.info(u'Time to verify ' + sut_state + u': ' + elapsed_time)
        else:
            gk_Log.error(u'Verification of ' + sut_state + u'abandoned after ' + elapsed_time)

    def look_to_see_if_in_state_async(self, time_total, sut_state):
        """
        Use asynchronous threading to put SUT into state
        :param time_total: Total time to verify before timing out
        :param sut_state: OS/EFI/BIOS/Bootmenu/Security menu, etc
        :return Success if thread started:
        """
        try:
            SYNCEVENT.clear()

            v_thread = threading.Thread(name='vision_thread', target=self.look_to_see_if_in_state,
                                        args=(sut_state, time_total))
            v_thread.start()
            return Success
        except RuntimeError as ex:
            str_error = u'Error creating vision_thread: ' + str(ex)
            gk_Log.error(str_error)
            return Failure
# try:
#     a=Vision("abc.png", "log")
#     text = a.capture_screen_text()
#     print(a.verify_bios_screen(text))
#     # print(a.verify_efi_screen(text))
#     # print(a.verify_os_screen(text))
#
# except Exception as e:
#     print(e)
