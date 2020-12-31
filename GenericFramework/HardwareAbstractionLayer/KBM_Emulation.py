__author__ = 'jkmody'

"""
########################################################################################################################
# INTEL CONFIDENTIAL                                                                                                   #
# Copyright 2017 Intel Corporation All Rights Reserved.                                                                #
#                                                                                                                      #
# The source code contained or described herein and all documents related to the source code ("Material") are owned by #
# Intel Corporation or its suppliers or licensor's. Title to the Material remains with Intel Corporation or its        #
# suppliers and licensor's. The Material contains trade secrets and proprietary and confidential information of Intel  #
# or its suppliers and licensor's. The Material is protected by worldwide copyright and trade secret laws and treaty   #
# provisions. No part of the material may be used, copied, reproduced, modified, published, uploaded, posted,          #
# transmitted, distributed, or disclosed in any way without Intel's prior express written permission. No license under #
# any patent, copyright, trade secret or other intellectual property right is granted to or conferred upon you by      #
# disclosure or delivery of the Materials, either expressly, by implication, inducement, estoppal or otherwise. Any    #
# license under such intellectual property rights must be express and approved by Intel in writing.                    #
########################################################################################################################

########################################################################################################################
# PRIMITIVE ACTION DESCRIPTION                                                                                         #
#                                                                                                                      #
# Title: Keyboard.py                                                                                                   #
# Author: Renjith                                                                                                      #
# Date Created: 09/29/2016                                                                                             #
#                                                                                                                      #
# Prerequisites:                                                                                                       #
#  - state: OS/BIOS/EDK                                                                                                #
#  - For keyboard emulation two teensy LC/ teensy 3.2 is used. One will act as a master and other as a slave.          #
#  - The master is loaded with a FIRMATA protocol library, pass the keyboard signals to slave using i2c protocol       #
#  - All data is send as 2BYTES.                                                                                       #
#                                                                                                                      #
# Modification History:                                                                                                #
# Date        Modified                     Reason                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#  11/16/17   Renjith     Inherited functionality from existing Gherkin vetra core, Added Teensys KB and mouse-        #
#                         functionality.                                                                               #
#  11/30/17   Renjith     Added new mouse functionality - Move, MoveTo, Scroll, screenSize                             #
#  12/19/17   Thomas      Add backsupport for Vetra key commands (enter, up, down, left, right, esc)                   #
#  01/02/18   Renjith     Fix for KBM sleep wake-up and fix crash issue during get screen-resolution in non-os mode.   #
#  01/02/18   Thomas      Add flexibility to add multiple spaces between key commands                                  #
#  01/10/18   Bhargavi    Enhanced the KBM init method to enable mouse coordinates when SUT is in OS                   #
#  02/07/18   Renjith     Code refactoring to PEP8 standards. Phase #3                                                 #
#  04/04/18   Renjith     Bugfix - Fixing exception when we access the KBM in non OS                                   #
#  04/10/18   Thomas      Adding delay in move_to step, to separate moving and verifying mouse movement                #
#  04/25/18   Renjith     Added proper clean-up to release the acquired ports during exception                         #
#  05/09/18   Michael     Added key_spam_async method allows key spamming to exit early when common SYNCEVENT is set   #
########################################################################################################################
"""

########################################################################################################################
# PYTHON IMPORTS                                                                                                       #
########################################################################################################################
import time
from re import split

########################################################################################################################
# LOCAL LIBRARY IMPORTS                                                                                                #
########################################################################################################################
# from lib_gherkin import gk_ConfigInstance, gk_Log, Success, Failure, COM_PORT, BAUDRATE, KEYBOARD_MOUSE
# from Common import DebugLogger, GKTimer, Common, SYNCEVENT
from SerialCore import SerialDevicesCore
from Protocol import FirmataProtocol
# from System import SystemCore


# TODO Renjith - Below are the minimal changes to use the file.
import random

# Results
Success = True
Failure = False

ALPHA_NUMERIC_SYMBOLS = \
    {
        # Alphabets
        u"A": 65, u"a": 97, u"B": 66, u"b": 98, u"C": 67, u"c": 99, u"D": 68, u"d": 100, u"E": 69, u"e": 101,
        u"F": 70, u"f": 102, u"G": 71, u"g": 103, u"H": 72, u"h": 104, u"I": 73, u"i": 105, u"J": 74, u"j": 106,
        u"K": 75, u"k": 107, u"L": 76, u"l": 108, u"M": 77, u"m": 109, u"N": 78, u"n": 110, u"O": 79, u"o": 111,
        u"P": 80, u"p": 112, u"Q": 81, u"q": 113, u"R": 82, u"r": 114, u"S": 83, u"s": 115, u"T": 84, u"t": 116,
        u"U": 85, u"u": 117, u"V": 86, u"v": 118, u"W": 87, u"w": 119, u"X": 88, u"x": 120, u"Y": 89, u"y": 121,
        u"Z": 90, u"z": 122,
        # Numbers
        u"0": 48, u"1": 49, u"2": 50, u"3": 51, u"4": 52, u"5": 53, u"6": 54, u"7": 55, u"8": 56, u"9": 57,
        # Symbols
        u" ": 32, u"!": 33, u'"': 34, u"#": 35, u"$": 36, u"%": 37, u"&": 38, u"'": 39, u"(": 40, u")": 41, u"*": 42,
        u"+": 43, u",": 44, u"-": 45, u".": 46, u"/": 47, u":": 58, u";": 59, u"<": 60, u"=": 61, u">": 62, u"?": 63,
        u"@": 64, u"[": 91, u"\\": 92, u"]": 93, u"^": 94, u"_": 95, u"`": 96, u"{": 123, u"|": 124, u"}": 125,
        u"~": 126, u"DEL": 127
    }

MODIFIER_KEYS =\
    {
        # Modifier keys
        u"KEY_CTRL":        (0x01 | 0xE000), u"KEY_SHIFT":      (0x02 | 0xE000),
        u"KEY_ALT":         (0x04 | 0xE000), u"KEY_GUI":        (0x08 | 0xE000),
        u"KEY_LEFT_CTRL":   (0x01 | 0xE000), u"KEY_LEFT_SHIFT": (0x02 | 0xE000),
        u"KEY_LEFT_ALT":    (0x04 | 0xE000), u"KEY_LEFT_GUI":   (0x08 | 0xE000),
        u"KEY_RIGHT_CTRL":  (0x10 | 0xE000), u"KEY_RIGHT_SHIFT": (0x20 | 0xE000),
        u"KEY_RIGHT_ALT":   (0x40 | 0xE000), u"KEY_RIGHT_GUI":  (0x80 | 0xE000),
    }

COMMAND_KEYS = \
    {
        u"F1":  (58 | 0xF000), u"F2":  (59 | 0xF000), u"F3": (60 | 0xF000), u"F4": (61 | 0xF000), u"F5":  (62 | 0xF000),
        u"F6":  (63 | 0xF000), u"F7":  (64 | 0xF000), u"F8": (65 | 0xF000), u"F9": (66 | 0xF000), u"F10": (67 | 0xF000),
        u"F11": (68 | 0xF000), u"F12": (69 | 0xF000),

        u"KEY_ENTER":   (40 | 0xF000), u"KEY_ESC":     (41 | 0xF000), u"KEY_BACKSPACE":    (42 | 0xF000),
        u"KEY_TAB":     (43 | 0xF000), u"KEY_SPACE":   (44 | 0xF000), u"KEY_MINUS":        (45 | 0xF000),
        u"KEY_EQUAL":   (46 | 0xF000), u"KEY_LEFT_BRACE": (47 | 0xF000), u"KEY_RIGHT_BRACE": (48 | 0xF000),
        u"KEY_BACKSLASH": (49 | 0xF000), u"KEY_NON_US_NUM": (50 | 0xF000), u"KEY_SEMICOLON": (51 | 0xF000),
        u"KEY_QUOTE":   (52 | 0xF000), u"KEY_TILDE":    (53 | 0xF000), u"KEY_COMMA":        (54 | 0xF000),
        u"KEY_PERIOD":  (55 | 0xF000), u"KEY_SLASH":    (56 | 0xF000), u"KEY_CAPS_LOCK":    (57 | 0xF000),
        u"KEY_PRINTSCREEN": (70 | 0xF000), u"KEY_SCROLL_LOCK": (71 | 0xF000), u"KEY_PAUSE": (72 | 0xF000),
        u"KEY_INSERT":  (73 | 0xF000), u"KEY_HOME":     (74 | 0xF000), u"KEY_PAGE_UP":      (75 | 0xF000),
        u"KEY_DELETE":  (76 | 0xF000), u"KEY_END":      (77 | 0xF000), u"KEY_PAGE_DOWN":    (78 | 0xF000),
        u"KEY_RIGHT":   (79 | 0xF000), u"KEY_LEFT":     (80 | 0xF000), u"KEY_DOWN":         (81 | 0xF000),
        u"KEY_UP":      (82 | 0xF000), u"KEY_NUM_LOCK": (83 | 0xF000), u"KEYPAD_SLASH":     (84 | 0xF000),
        u"KEYPAD_ASTERIX": (85 | 0xF000), u"KEYPAD_MINUS": (86 | 0xF000), u"KEYPAD_PLUS":   (87 | 0xF000),
        u"KEYPAD_ENTER": (88 | 0xF000), u"KEYPAD_1":    (89 | 0xF000), u"KEYPAD_2":         (90 | 0xF000),
        u"KEYPAD_3":    (91 | 0xF000), u"KEYPAD_4":     (92 | 0xF000), u"KEYPAD_5":         (93 | 0xF000),
        u"KEYPAD_6":    (94 | 0xF000), u"KEYPAD_7":     (95 | 0xF000), u"KEYPAD_8":         (96 | 0xF000),
        u"KEYPAD_9":    (97 | 0xF000), u"KEYPAD_0":     (98 | 0xF000), u"KEYPAD_PERIOD":    (99 | 0xF000),
        u"KEY_NON_US_BS": (100 | 0xF000), u"KEY_MENU":  (101 | 0xF000),

        # Back support for VETRA
        u"ENTER":   (40 | 0xF000),
        u"UP":      (82 | 0xF000),
        u"RIGHT":   (79 | 0xF000),
        u"LEFT":    (80 | 0xF000),
        u"DOWN":    (81 | 0xF000),
        u"ESC":     (41 | 0xF000),
    }

# Key Types
ALPHANUMERIC = u'AlphaNumeric'
MODIFIERKEYS = u'ModifierKeys'
COMMANDKEYS = u'CommandKeys'

KEYBOARD_CMD = \
    {
        u'Press':       80,
        u'Release':     82,
        u'Write':       87,
        u'ReleaseAll':  65,
        u'Wakeup':       83
    }

MOUSE_CMD = \
    {
        u'Click':     99,
        u'Move':      109,
        u'MoveTo':    116,
        u'Press':     112,
        u'Release':   114,
        u'IsPressed': 105,
        u'ScreenSize': 122,
        u'Scroll':    115
    }

MOUSE_BTN_NAMES = (u'Left', u'Middle', u'Right')

MOUSE_BTN = \
    {
        u'Left':    1,
        u'Middle':  4,
        u'Right':   2
    }


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


class USBKbMouseEmulation(SerialDevicesCore):
    """
        Class for USB mouse and keyboard emulation
    """
    def __init__(self, mouse_support, port):
        """
        __init__() : Constructor method for USB KBM Emulation
        :param mouse_support: Flag to enable mouse support
        """
        self.debug_enabled = False  # Flag to Enable/Disable debugging.
        self.seconds_between_press = 0.08
        self.port = port

        # TODO Renjith - Changes to set the serial port setting
        # THis is COM ID of teensy.
        #port = "COM29"   # gk_ConfigInstance.get(COM_PORT, KEYBOARD_MOUSE)
        baudrate = 9600  # gk_ConfigInstance.get(BAUDRATE, KEYBOARD_MOUSE)

        if port is None or baudrate is None:
            str_error = u"Either COM port or Baud rate not set for Keyboard_Mouse in gherkin.ini"
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        SerialDevicesCore.__init__(self, port, baudrate)
        if mouse_support:
            # self.sys_obj = SystemCore()
            # if self.sys_obj.is_sut_alive(1):  # Mouse screen coordinates to be enabled when SUT is in OS
                # Define the screen resolution size for mouse cursor movement.
                # gk_Log.info(u'Enabling mouse screen coordinates')
                # TODO Renjith -  Get the SUT screen coordinates of SUT. Use your framework logic to talk to SUT and
                #  get the screen resolution
                # screen_width, screen_height = self.sys_obj.get_screen_resolution()
                screen_width = 1920
                screen_height = 1080

                if screen_width is None or screen_height is None:
                    str_error = u"SUT screen resolution is not set for mouse emulation. \
                                Mouse cursor positioning will not be accurate"
                    # gk_Log.warning(str_error)  # Warning is sufficient as it is not breaking mouse move functionality
                else:
                    self.mouse_screensize(screen_width, screen_height)

    @classmethod
    def __string_to_array(cls, string):
        array = split(r'(\s+)', string)
        return array

    @classmethod
    def __get_key_info(cls, key):
        """
        __get_key_info(): get the information about a key
        :param key: key name
        :return: a tuple data of (key_type, key_value) if the key is found. otherwise (None, None)
        """
        key_value = None
        try:
            key_value = ALPHA_NUMERIC_SYMBOLS[key]
        except KeyError:
            pass

        if key_value:  # Found an Alpha Numeric/ Symbol key
            return ALPHANUMERIC, key_value

        try:
            key_value = MODIFIER_KEYS[key]
        except KeyError:
            pass

        if key_value:  # Found a Modifier key
            return MODIFIERKEYS, key_value

        try:
            key_value = COMMAND_KEYS[key]
        except KeyError:
            pass

        if key_value:  # Found a command key
            return COMMANDKEYS, key_value

        return None, None

    def __get_button_info(self, mouse_btn):
        """
        __get_button_info(): Get the mouse button info
        :param mouse_btn: button name
        :return: return a valid button name.
        """
        try:
            return MOUSE_BTN_NAMES[[item.lower() for item in MOUSE_BTN_NAMES].index(mouse_btn.lower())]
        except:
            self.cleanup()
            str_error = u'Unknown Button : ' + str(mouse_btn)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

    def __create_keys_hid_report(self, keys, report_type):
        """
        __create_keys_hid_report() : Create the HID report protocol for the keys
        :param keys: keys to be pressed
        :param report_type: Type of key
        :return: hid report
        """

        hid_report = []

        if report_type == ALPHANUMERIC:  # Alpha Numeric Symbol
            for key in keys:
                # DebugLogger.print_log(self, AlphaNumericKey=key)
                for character in key:
                    ch_type, ch_value = self.__get_key_info(character)
                    # DebugLogger.print_log(self, CharacterType=ch_type, CharacterValue=ch_value)
                    assert ch_value is not None
                    hid_report.append(FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Write'], ch_value))
            return hid_report
        elif report_type == MODIFIERKEYS:  # Modifier
            for key in keys:
                # DebugLogger.print_log(self, ModifierKey=key)
                key_upper = key.upper()
                key_type, key_value = self.__get_key_info(key_upper)
                if key_type == ALPHANUMERIC:    # We don't need to take a forced upper case when alphanumeric key is \
                                                #  passed along with a modifier key.
                    key_type, key_value = self.__get_key_info(key)
                assert key_value is not None
                hid_report.append(FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Press'], key_value))
            # Release key only at the end of the KB msg
            hid_report.append(FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'ReleaseAll']))

            return hid_report

        elif report_type == COMMANDKEYS:  # Command keys
            for key in keys:
                # DebugLogger.print_log(self, CommandKey=key)
                if key.isspace():
                    continue
                key_type, key_value = self.__get_key_info(key.upper())
                assert key_value is not None
                hid_report.append(FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Press'], key_value))
                # Release key immediately
                hid_report.append(FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Release'], key_value))
            return hid_report
        else:
            self.cleanup()
            str_error = u"Unknown report type"
            # gk_Log.exception(str_error)
            raise Exception(str_error)

    def set_time_between_keypress(self, seconds_between_press):
        """
        set_time_between_keypress(): Set the time between each key press. Default is 0.08
        :param seconds_between_press: seconds
        :return: Success / Exception
        """
        self.seconds_between_press = float(seconds_between_press)
        return Success

    def key_spam_async(self, key, duration):
        """
        key_spam(): Spam a key for the specified duration
        :param key: Key to be spammed
        :param duration: Spamming duration
        :return: Success if event set within specified duration
        """
        key_type, key_value = self.__get_key_info(str(key).upper())

        if key_type == ALPHANUMERIC:  # Alpha numeric key
            self.cleanup()
            str_error = u"Not a valid key to be spammed:" + str(key)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        if not key_value:
            self.cleanup()
            str_error = u"Key not defined:" + str(key)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        hid_report = [FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Press'], key_value),
                      FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'ReleaseAll'])]

        timer = GKTimer()
        while timer.timeup(duration):   # and not SYNCEVENT.isSet():
            FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)
            time.sleep(self.seconds_between_press)

        # TODO Renjith - To use the teensy functionality you dont need any EVENTS logic. The Event logic is for
        #  our Framework
        # if SYNCEVENT.isSet():
        #     return Success
        # return Failure

        return Success

    def key_spam(self, key, duration):
        """
        key_spam(): Spam a key for the specified duration
        :param key: Key to be spammed
        :param duration: Spamming duration
        :return: Success / Exception
        """
        key_type, key_value = self.__get_key_info(str(key).upper())

        if key_type == ALPHANUMERIC:  # Alpha numeric key
            self.cleanup()
            str_error = u"Not a valid key to be spammed:" + str(key)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        if not key_value:
            self.cleanup()
            str_error = u"Key not defined:" + str(key)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        hid_report = [FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Press'], key_value),
                      FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'ReleaseAll'])]

        timer = GKTimer()
        while timer.timeup(duration):
            FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)
            time.sleep(self.seconds_between_press)

        return Success

    def key_type(self, keys):
        """
        key_type(): type only alphanumeric/symbol keys
        :param keys: alpha/numeric/symbol keys
        :return: Success / Exception
        """
        keys = self.__string_to_array(keys)
        hid_report = self.__create_keys_hid_report(keys, ALPHANUMERIC)
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)

    def key_press(self, keys):
        """
        key_press(): Press key are used for modifier keys and command keys
        :param keys: Key to be pressed
        :return: Success / Exception
        """
        keys = self.__string_to_array(keys)
        key_array = [x for x in keys if x != u' ']  # Array without space

        if self.__get_key_info(key_array[0].upper())[0] == MODIFIERKEYS:  # Check the first key is a modifier key
            hid_report = self.__create_keys_hid_report(key_array, MODIFIERKEYS)
            return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)
        elif self.__get_key_info(key_array[0].upper())[0] == COMMANDKEYS:  # if the first key is a Command
            hid_report = self.__create_keys_hid_report(key_array, COMMANDKEYS)
            return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)
        else:  # Write keys are not allowed here
            self.cleanup()
            str_error = u"Key not found:" + str(key_array[0])
            # gk_Log.exception(str_error)
            raise Exception(str_error)

    def mouse_click(self, mouse_btn):
        """
        mouse_click() - Emulate mouse button click
        :param mouse_btn: Button name - Left/Right/Middle
        :return: Success / Exception
        """
        btn_name = self.__get_button_info(mouse_btn)
        hid_report = FirmataProtocol().create_hid_report(MOUSE_CMD[u'Click'], MOUSE_BTN[btn_name])
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, hid_report)

    def mouse_doubleclick(self, mouse_btn):
        """
        mouse_doubleclick(): Emulate mouse button double-click
        :param mouse_btn: Button name - Left/Right/Middle
        :return: Success / Exception
        """
        btn_name = self.__get_button_info(mouse_btn)
        hid_report = [FirmataProtocol().create_hid_report(MOUSE_CMD[u'Click'], MOUSE_BTN[btn_name])]
        hid_report += [FirmataProtocol().create_hid_report(MOUSE_CMD[u'Click'], MOUSE_BTN[btn_name])]
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, *hid_report)

    def mouse_move(self, ptx, pty):
        """
        mouse_move(): Move the mouse pointer to a new position from the current position.
        :param ptx: points to move in X direction
        :param pty: points to move in y direction
        :return: Success / Exception
        """
        curr_x, curr_y = self.mouse_get_position()
        new_x, new_y = curr_x + int(ptx), curr_y + int(pty)
        if new_x < 0:
            new_x = 0
        if new_y < 0:
            new_y = 0

        # DebugLogger.print_log(self, curr_x=curr_x, curr_y=curr_y, new_x=new_x, new_y=new_y)
        return self.mouse_moveto(new_x, new_y)

    def mouse_moveto(self, ptx, pty):
        """
        mouse_moveto(): Move to X,Y with respect to screen
        :param ptx: X position in screen
        :param pty: Y position in screen
        :return: Success / Exception
        """
        exec_status = None
        pt_cur_x, pt_cur_y = self.mouse_get_position()  # Present position

        hid_report = FirmataProtocol().create_hid_report(MOUSE_CMD[u'MoveTo'], int(ptx), int(pty))

        # A single mouse move message is not getting registered on OS. So sending the message multiple (3) times
        for _ in range(0, 3):
            exec_status = FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, hid_report)

        time.sleep(2)  # Give sufficient time for the mouse cursor to relocate to new position.
        pos_x, pos_y = self.mouse_get_position()

        if int(pos_x) == int(pt_cur_x) and int(pos_y) == int(pt_cur_y):
            self.cleanup()
            str_error = u"The mouse cursor is not moved. Try with a different position X,Y"
            # gk_Log.exception(str_error)
            raise Exception(str_error)
        return exec_status

    @classmethod
    def generate_random(cls, randint1, randint2):
        """
        generate_random(): Generate a random number between randint1 and randint2
        :param randint1:  An integer number for the lower/higher boundary
        :param randint2:  An integer number for the higher/lower boundary
        :return: random number
        """
        if not isinstance(randint1, int) or \
                not isinstance(randint2, int):
            str_error = u'Not able to generate random number - Unidentified numbers passed: ' + str(randint1) + \
                                u' and ' + str(randint2)
            # gk_Log.exception(str_error)
            raise Exception(str_error)

        if randint1 <= randint2:
            return random.randint(randint1 + 1, randint2 - 1)
        return random.randint(randint2 + 1, randint1 - 1)

    def mouse_moverandom(self):
        """
        mouse_moverandom(): Random move from the x pos and y pos.
        :return: Success / failure.
        """
        pt_cur_x, pt_cur_y = self.mouse_get_position()  # Present position
        # TODO Renjith - Get the present screen resolution. Use your framework logic to talk to SUT and get the
        #  present resolution
        # common = Common()
        # screen_width, screen_height = self.sys_obj.get_screen_resolution()
        screen_width = 1920
        screen_height = 1080

        # DebugLogger.print_log(self, pt_cur_x=pt_cur_x, pt_cur_y=pt_cur_y)
        # DebugLogger.print_log(self, screen_width=screen_width, screen_height=screen_height)

        randwidth = max([0, int(screen_width)], key=lambda x: abs(x - pt_cur_x))
        randheight = max([0, int(screen_height)], key=lambda x: abs(x - pt_cur_y))

        # DebugLogger.print_log(self, randwidth=randwidth, randheight=randheight)

        rand_x = self.generate_random(int(pt_cur_x), randwidth)
        rand_y = self.generate_random(int(pt_cur_y), randheight)

        # DebugLogger.print_log(self, rand_x=rand_x, rand_y=rand_y)

        return self.mouse_moveto(rand_x, rand_y)

    def mouse_screensize(self, width, height):
        """
        mouse_screensize(): Declare the current screen resolution to the mouse emulator.
        This will make the mouse cursor movement accurate with respect to screen co-ordinate system
        :param width: Screen resolution width
        :param height: Screen resolution height
        :return: Success / Exception
        """
        hid_report = FirmataProtocol().create_hid_report(MOUSE_CMD[u'ScreenSize'], int(width), int(height))
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, hid_report)

    def mouse_scroll(self, wheel):
        """
        mouse_scroll(): scroll the mouse
        :param wheel: number of times the mouse wheel to be scrolled
        :return: Success / Exception
        """
        scroll_up = False
        if int(wheel) < 0:
            scroll_up = True

        wheel = abs(int(wheel))

        hid_report = FirmataProtocol().create_hid_report(MOUSE_CMD[u'Scroll'], wheel, scroll_up)
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, hid_report)

    def mouse_get_position(self):
        """
        mouse_get_position(): Get the current mouse cursor position
        :return: X,Y position of cursor in screen-coordinates.
        """
        # return self.sys_obj.get_mouse_position()

        # TODO  - Renjith - Get the mouse present X,Y coordinates. Use your framework logic to talk to SUT and get the
        #  coordinates. If this fails, some mouse movement methods validation check may fails.

        x = 100
        y = 200
        return x, y

    def kbm_wakeup(self):
        """
        kbm_wakeup(): Wake-up the system using the KBM emulator
        :return: Success / Exception
        """
        hid_report = FirmataProtocol().create_hid_report(KEYBOARD_CMD[u'Wakeup'])
        return FirmataProtocol().send_hid_report(self.write, self.seconds_between_press, hid_report)
