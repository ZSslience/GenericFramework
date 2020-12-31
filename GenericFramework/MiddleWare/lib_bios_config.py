"""
File Name   : lib_bios_config.py
Description : The BIOS config library provides methods, to navigate BIOS menu
              and set all config options
Author      : Michael/Jinliang
Created On  : 13 Dec 2019
Modified On : 23 Dec 2019
"""
import os
import re

from HardwareAbstractionLayer.hal_serial_opt import SerialComm
from SoftwareAbstractionLayer import lib_constants
from SoftwareAbstractionLayer.library import write_log
from SoftwareAbstractionLayer.vt100_screen_parser import ScreenParser
from SoftwareAbstractionLayer.vt100_screen_parser import EntryType
from SoftwareAbstractionLayer.vt100_screen_parser import parse_edk_shell
from SoftwareAbstractionLayer.lib_parse_config import ParseConfig


class BiosConfigError(Exception):
    # Did not get any information from existing BIOS page
    BIOS_INITIALIZE_FAIL = "Did not get any information from BIOS page, " \
                           "please confirm whether entered in BIOS"

    # Failed to do some BIOS config operation
    BIOS_OPERATE_FAIL = "Operating BIOS configuration failed"

    # Not found the given menu path in BIOS page
    MENU_PATH_NOT_FOUND = "Menu path not be found in BIOS page"

    # The type of item does not match user wanted
    ITEM_TYPE_MISMATCH = "The type of item does not match"

    # Press key, but not get correctly responded
    KEY_EVENT_FAILURE = "The key event is failure, not responded correctly"

    # Invalid input parameter
    INVALID_INPUT = "Input parameter is invalid"

    # Empty input parameter
    EMPTY_INPUT = "Input parameter is empty"

    # Invalid section or key settings in config file
    INVALID_SETTINGS = "Invalid section or key settings in config file"

    # Failed to move cursor
    FAILED_MOVE_CURSOR = "Failed to move cursor to specific menu"

    def __init__(self, error_msg, specific_msg=None):
        """Initialize BiosConfigError class
        :param error_msg: this object's generic error message
        :param specific_msg: specific message to be append after generic
                             message
        """
        Exception.__init__(self)
        self._error_msg = error_msg
        self._specific_msg = specific_msg

    def get_generic_error_message(self):
        """Return generic error message
        :return: generic error message
        :rtype: str
        """
        return self._error_msg

    def get_error_message(self):
        """Splice generic error message with specific message (if existing)
        and return
        :return: finial error message
        :rtype: str
        """
        final_message = "Unknown exception"

        if self._error_msg:
            final_message = "%s: " % self.__class__.__name__
            final_message += self._error_msg
            if self._specific_msg:
                final_message += ": %s" % self._specific_msg

        return final_message

    def __str__(self):
        """Return error message if object is created as string
        """
        return self.get_error_message()


class BiosMenuConfig:

    def __init__(self, tc_id=None, script_id=None, loglevel="ALL", data=None):
        """Initialize BiosMenuConfig class.
        :param tc_id: test case id
        :param script_id: script id
        :param loglevel: log levels that allowed to be output
        :param data: data of BIOS interface captured from serial port when
                     entering BIOS. it's optional parameter, if no available
                     data, do not pass this parameter. and at the time to do
                     BIOS configuration, call bios_initialize() to initialize
                     BIOS data
        """
        self.sc = SerialComm()
        self.sp = ScreenParser(tc_id, script_id)
        self._tc_id = tc_id
        self._script_id = script_id
        self._log_level = loglevel
        self._bios_items = None
        if data:
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()

        self._sut_config_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                os.path.pardir,
                r"SoftwareAbstractionLayer\system_configuration.ini")
        self._config = ParseConfig()

    def bios_initialize(self, wait_timeout=600, f2_press_wait=0, admin_pwd=""):
        """Initialize the BIOS home page, be called every time when into BIOS
        :param wait_timeout: wait time to catch 'Press F2' string from serial
        :param f2_press_wait: wait time between press F2 and goes into BIOS
        :param admin_pwd: Admin password to login BIOS setup
        :return: None
        :raise: BiosConfigError
        """
        # press "Ctrl+Alt+Delete" to reboot system, next to press "F2" and wait
        # a few times to go to BIOS, then obtain the data of the BIOS home page
        self.sc.serial_io_hii_enum(1, "CTRL_ALT_DELETE")
        return self.enter_bios(wait_timeout=wait_timeout,
                               f2_timeout=f2_press_wait,
                               admin_pwd=admin_pwd)

    def select_menu_option(self, menu, complete_matching=True, index=1):
        """Highlight/select menu option in BIOS by its name
        :param menu: valid menu option, represents only that can be selected or highlighted
        :param complete_matching: True to complete matching menu
                                  False to inclusion matching menu
        :param index: index of items which contain duplicate menu name, default as and starts at 1
                      if want to assign a index > 1, should back to the beginning of this BIOS menu,
                      and figured out the index value from top to bottom
        :return: True if menu selected success, otherwise False
        :raise: BiosConfigError
        """
        if not menu:
            self._log_write(lib_constants.LOG_WARNING, "No menu option given")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if int(index) < 1:
            self._log_write(lib_constants.LOG_WARNING,
                            "Menu index is %d, it's less than 1" % int(index))
            raise BiosConfigError(BiosConfigError.INVALID_INPUT)

        try:
            # find path between menu and current highlighted item
            steps = self._path_finder(menu, complete_matching, int(index))
            # move cursor to given menu
            self._gui_vert_move_cursor(menu, steps)
            return True
        except BiosConfigError as e:
            self._log_write(lib_constants.LOG_ERROR, "ERROR: %s" % e)
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Failed to select menu option '%s'"
                            % menu)
            return False

    def press_menu(self, menu, complete_matching=True, index=1):
        """Press menu option in BIOS by its name
        :param menu: valid menu option, represents only that can be selected or highlighted
        :param complete_matching: True to complete matching menu
                                  False to inclusion matching menu
        :param index: index of items which have/contain duplicate menu name
        :return: True if menu pressed success, otherwise False
        """
        if not self.select_menu_option(menu, complete_matching, index):
            return False

        # press 'Enter' key
        self.bios_control_key_press("ENTER")
        return True

    def bios_menu_navi(self, menu_path=[], wait_time=10, complete_matching=True):
        """SUT BIOS navigation based on menu path given.
        :param menu_path: menu path list in BIOS config
                          e.g. ["Intel Advanced Menu", "ACPI Settings"]
        :type menu_path: list
        :param wait_time: wait time to enter a new menu
        :type wait_time: int
        :param complete_matching: complete match menu, or partial match menu
        :type complete_matching: bool
        :return: True if navigate success, otherwise False
        :raise: BiosConfigError
        """
        if not menu_path:
            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Empty menu path, no navigation required")
            return True

        if type(menu_path) != list:
            self._log_write(lib_constants.LOG_WARNING,
                            "Input menu path should be string list")
            raise BiosConfigError(BiosConfigError.INVALID_INPUT)

        for menu in menu_path:
            if not self.select_menu_option(menu, complete_matching=complete_matching):
                return False

            item_type = self._get_highlight_item_type()
            if item_type == EntryType.MENU \
                    or item_type == EntryType.SELECTABLE_TXT:
                # press 'Enter' to goes into menu
                self.bios_control_key_press("ENTER", time_out=wait_time)
            else:
                self._log_write(lib_constants.LOG_WARNING,
                                "WARNING: Item '%s' not accessible" % menu)
                return False

        self._log_write(lib_constants.LOG_INFO,
                        "INFO: Success to navigate into menu: %s" % menu_path)
        return True

    def bios_opt_drop_down_menu_select(self, menu, value, menu_index=1, complete_matching=True):
        """Click given menu from current BIOS menu, then from the popup
        drop down menu, find and select given value
        :param menu: BIOS menu to be popup sub menu, represents only that can
                     be selected or highlighted
        :type menu: str
        :param value: the value set for the menu
        :type value: str
        :param menu_index: index of items which have/contain duplicate menu name
        :type menu_index: int
        :param complete_matching: complete match menu, or partial match menu
        :type complete_matching: bool
        :return: True if select item in drop down menu success, otherwise False
        :raise: BiosConfigError, CursorMovementError
        """
        if not value:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'value' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if not self.select_menu_option(menu, complete_matching=complete_matching, index=menu_index):
            return False

        # get type of highlight item, and check if it has drop down menu
        item_type = self._get_highlight_item_type()
        if item_type != EntryType.DROP_DOWN:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Menu '%s' has no drop down menu" % menu)
            return False

        # press 'Enter' key to popup drop down menu
        self.bios_control_key_press("ENTER")

        if not self.select_menu_option(value):
            # press 'Esc' key to cancel drop down menu select
            self.bios_control_key_press("ESC")
            return False

        # press 'Enter' key to confirm selection and close drop down menu
        self.bios_control_key_press("ENTER")
        if self._bios_items['is_dialog_box']:
            for content in self._bios_items['entries']:
                # if selection 'Y/N' in dialog box, set 'Y' to confirm
                if "Y/N" in content[0]:
                    self.bios_string_input('Y')
                    break
            else:
                # otherwise press Esc to cancel dialog box
                self.bios_control_key_press("ESC")

        self._log_write(lib_constants.LOG_INFO,
                        "INFO: Success to set value %s to menu %s"
                        % (value, menu))
        return True

    def bios_opt_get_drop_down_values(self, menu, menu_index=1, complete_matching=True):
        """Click given menu from current BIOS page, then from the popup
        drop down dialog, fetch all the values and return
        :param menu: BIOS menu to be popup sub menu, represents only that can
                     be selected or highlighted
        :type menu: str
        :param menu_index: index of items which have/contain duplicate menu name
        :type menu_index: int
        :param complete_matching: complete match menu, or partial match menu
        :type complete_matching: bool
        :return: values list in drop down dialog, otherwise []
        """
        if not self.select_menu_option(menu, complete_matching=complete_matching, index=menu_index):
            return []

        # get type of highlight item, and check if it has drop down menu
        item_type = self._get_highlight_item_type()
        if item_type != EntryType.DROP_DOWN:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Menu '%s' has no drop down dialog" % menu)
            return []

        # press 'Enter' key to popup drop down dialog
        self.bios_control_key_press("ENTER")
        # get all current showed values
        values = [item[0].strip() for item in self._bios_items["entries"]]
        # if drop down dialog could be scroll down, then scroll down to get more values
        while self._bios_items["is_scrollable_down"]:
            self.bios_navigation_key_press("DOWN")
            highlight_value = self._get_highlight_item_content().strip()
            if highlight_value not in values:
                values.append(highlight_value)

        # press 'Esc' key to close drop down dialog
        self.bios_control_key_press("ESC")
        self._log_write(lib_constants.LOG_INFO, "INFO: success to get values")
        return values

    def bios_opt_checkbox_check(self, menu, to_be_check=True, menu_index=1, complete_matching=True):
        """Check or uncheck the checkbox with given BIOS menu.
        :param menu: BIOS menu has checkbox to be check, represents only that
                     can be selected or highlighted
        :type menu: str
        :param to_be_check: True to check as [x]; False to uncheck as [ ]
        :type to_be_check: bool
        :param menu_index: index of items which have/contain duplicate menu name
        :type menu_index: int
        :param complete_matching: complete match menu, or partial match menu
        :type complete_matching: bool
        :return: True if change checkbox status success, otherwise False
        :raise: BiosConfigError
        """
        if not self.select_menu_option(menu, complete_matching=complete_matching, index=menu_index):
            return False

        def is_checkbox_at_correct_state(checked, to_check):
            """get highlighted checkbox state, determine whether it is
            consistent with the state to be check
            """
            if to_check and checked:
                return True
            if not to_check and not checked:
                return True
            return False

        # verify checkbox state
        is_checked = self.is_checkbox_checked()
        if is_checkbox_at_correct_state(is_checked, to_be_check):
            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Checkbox state already be correct")
            return True

        # press 'Enter' key to change checkbox state
        self.bios_control_key_press("ENTER")
        # if there is a dialog box popup, press Esc to close it
        if self._bios_items['is_dialog_box']:
            for content in self._bios_items['entries']:
                # if selection 'Y/N' in dialog box, set 'Y' to confirm
                if "Y/N" in content[0]:
                    self.bios_string_input('Y')
                    break
            else:
                # otherwise press Esc to cancel dialog box
                self.bios_control_key_press("ESC")

        # verify checkbox state again
        is_checked = self.is_checkbox_checked()
        if is_checkbox_at_correct_state(is_checked, to_be_check):
            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Success to change checkbox state")
            return True
        else:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Failed to change checkbox state")
            return False

    def bios_opt_textbox_input(self, menu, content, menu_index=1, complete_matching=True):
        """To the given BIOS menu, input text content as its value.
        :param menu: BIOS menu has a textbox, represents only that can be selected or highlighted
        :type menu: str
        :param content: text content to be input
        :type content: str
        :param menu_index: index of items which have/contain duplicate menu name
        :type menu_index: int
        :param complete_matching: complete match menu, or partial match menu
        :type complete_matching: bool
        :return: True if input text success, otherwise False
        :raise: BiosConfigError
        """
        if not content:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'content' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if not self.select_menu_option(menu, complete_matching=complete_matching, index=menu_index):
            return False

        # get type of highlight item, and check if it is input box
        item_type = self._get_highlight_item_type()
        if item_type != EntryType.INPUT_BOX:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Menu '%s' has no input box" % menu)
            return False

        # press 'Enter' key to select input box
        self.bios_control_key_press("ENTER")
        # input content
        self.bios_string_input(content)

        # get the entered value from input box [ ]
        item_value = self._get_highlight_item_value()
        item_input = item_value.split('[')[1]
        item_input = item_input.split(']')[0]
        item_input = item_input.strip()
        # verify content be input success or fail
        if content == item_input:
            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Success to input content '%s' to menu: %s"
                            % (content, menu))
            # press 'Enter' to confirm input
            self.bios_control_key_press("ENTER")
            return True
        else:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Failed to input content '%s', illegal "
                            "character or length out of range" % content)
            # press 'Esc' to cancel input
            self.bios_control_key_press("ESC")
            return False

    def get_input_box_content(self):
        for item in self._bios_items["entries"]:
            if item[2] == EntryType.INPUT_BOX:
                return item[0]

    def dialog_box_interaction(self, content):
        """Input content to dialog box
        :param content: text content to be input
        :return: None
        :raise: BiosConfigError
        """
        if not content:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'content' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if not self._bios_items['is_dialog_box']:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: The top screen is not a dialog box")
            return False

        # remove origin content, then input news
        origin_content = self.get_input_box_content()
        length = len(origin_content.rstrip())
        if length > 0:
            self.bios_control_key_press("BACKSPACE", times=length, time_out=1)
        self.bios_string_input(str(content))

        input_content = self.get_input_box_content()
        self._log_write(lib_constants.LOG_DEBUG,
                        "Input content is: %s" % input_content)
        return True

    def search_item_in_dialog_box(self, item_name, complete_matching=True):
        """In a dialog box, search the item by provided item_name
        :param item_name: item name to be searched in dialog box
        :param complete_matching: True to complete matching item
                                  False to inclusion matching item
        :return: True if searched, otherwise False
        """
        if not item_name:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'item_name' cannot be empty")
            return False

        if not self._bios_items['is_dialog_box']:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: The top screen is not a dialog box")
            return False

        for item in self._bios_items["entries"]:
            if complete_matching and item_name == item[0].strip():
                return True
            elif not complete_matching and item_name in item[0]:
                return True
        else:
            return False

    def bios_opt_dialog_box_input(self, menu, content, menu_index=1):
        """Click the given BIOS menu, and input text into the popup dialog box
        :param menu: BIOS menu to be clicked, represents only that can be selected or highlighted
        :type menu: str
        :param content: text content to be input
        :type content: str
        :param menu_index: index of items which have/contain duplicate menu name
        :type menu_index: int
        :return: None
        :raise: BiosConfigError
        """
        if not content:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'content' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if not self.select_menu_option(menu, complete_matching=False, index=menu_index):
            return False

        # get type of highlight item, and check if it is input box
        item_type = self._get_highlight_item_type()
        if item_type != EntryType.SELECTABLE_TXT:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Menu '%s' could not be clicked to popup"
                            "a dialog box" % menu)
            return False

        # press "Enter" to click the menu and popup dialog box
        self.bios_control_key_press("ENTER")
        # verify if there's dialog box popup on current page
        if not self._bios_items['is_dialog_box']:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Dialog box failed to popup")
            return False

        # remove origin content, then input news
        origin_content = self.get_input_box_content()
        length = len(origin_content.rstrip())
        if length > 0:
            self.bios_control_key_press("BACKSPACE", times=length, time_out=1)
        # input content to BIOS screen
        self.bios_string_input(str(content))

        # get what has been input on the screen and compare it with the
        # parameter content
        item_content = self.get_input_box_content()
        if item_content:
            item_content = item_content.rstrip()
            if str(content) == item_content:
                self._log_write(lib_constants.LOG_INFO,
                                "INFO: Success to input content in dialog box "
                                "of menu '%s'" % menu)
                # press 'Enter' to confirm input
                self.bios_control_key_press("ENTER")
                return True
            else:
                self._log_write(lib_constants.LOG_WARNING,
                                "WARNING: Failed to input content in dialog "
                                "box of menu '%s'" % menu)
                # press 'Esc' to cancel input
                self.bios_control_key_press("ESC")
                return False
        else:
            pass

    def bios_file_explorer(self, volume, file_path="", wait_time=10, complete_matching=True):
        """SUT BIOS navigation based on menu path given.
        :param volume: volume label in BIOS File Explorer to be selected
        :type volume: str
        :param file_path: file path in volume, connect by slash e.g. "Tools/a.efi"
        :type file_path: str
        :param wait_time: wait time to enter a directory
        :type wait_time: int
        :param complete_matching: complete match file path, or partial match file path
        :type complete_matching: bool
        :return: True if succeed to select file in File Explorer, otherwise False
        :raise: BiosConfigError
        """
        if not volume or not file_path:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'value' cannot be empty")
            return False

        if not self._select_device_volume(volume):
            return False

        # split file_path as path & file
        if '/' in file_path:
            full_path = file_path.split('/')
        elif '\\' in file_path:
            full_path = file_path.split('\\')
        else:
            full_path = [file_path]
        file = full_path[-1]
        if len(full_path) > 1:
            path = full_path[:-1]
        else:
            path = []
        # in File Explorer, path will be showed as "<path>",
        # so for complete matching of path, needs to assemble it with above specific format
        if complete_matching:
            new_path = []
            for folder in path:
                folder = '<' + folder + '>'
                new_path.append(folder)
        else:
            new_path = path

        for menu in new_path:
            # insert one blank line in bios entries for File Explorer page
            self._bios_items["entries"].insert(2, ['', '', ''])
            if not self.bios_menu_navi(menu_path=[menu], wait_time=wait_time,
                                       complete_matching=complete_matching):
                return False

        # insert one blank line in bios entries for File Explorer page
        self._bios_items["entries"].insert(2, ['', '', ''])
        return self.press_menu(file, complete_matching=complete_matching)

    def bios_back_home(self, wait_time=5):
        """Back to BIOS home page.
        :param wait_time: wait time to return back to previous menu
        :type wait_time: int
        :return: None
        """
        max_times_to_press_esc = 10
        for _ in range(max_times_to_press_esc):
            # verify BIOS page information, to determine whether back at home
            # page: home page has no page title, but has other BIOS information
            bios_page_info = self._get_bios_page_info()
            if len(bios_page_info) > 0 and self._bios_items["title"] is None:
                self._log_write(lib_constants.LOG_INFO,
                                "Back at BIOS home page now")
                return True
            self.bios_control_key_press("ESC", time_out=wait_time)

        self._log_write(lib_constants.LOG_ERROR,
                        "ERROR: Cannot back to BIOS home page after %d "
                        "times to press 'Esc'" % max_times_to_press_esc)
        return False

    def bios_save_changes(self, by_hot_key=True):
        """Save the configured BIOS changes, if not use hot key, this operation
        requires user to firstly navigate to BIOS page contains Save Changes
        menu
        :param by_hot_key: whether use hot key to implement save changes
        :return: True if save changes success, otherwise False
        :raise: BiosConfigError
        """
        if by_hot_key:
            key = self._config.get_value(self._sut_config_file,
                                         "function_keys",
                                         "save_changes",
                                         abort_on_failure=False)
            if key:
                self.bios_function_key_press(key)
                if self._bios_items["is_dialog_box"]:
                    # send 'Y' to confirm
                    self.bios_string_input("Y")
                else:
                    pass

                self._log_write(lib_constants.LOG_INFO,
                                "INFO: Save changes successfully")
                return True
            else:
                self._log_write(lib_constants.LOG_ERROR,
                                "ERROR: Not get the function key to save "
                                "changes in configuration")
                raise BiosConfigError(BiosConfigError.INVALID_SETTINGS)
        else:
            if not self.select_menu_option("Save Changes"):
                return False

            # press "Enter"
            self.bios_control_key_press("ENTER")
            if self._bios_items["is_dialog_box"]:
                # send 'Y' to confirm
                self.bios_string_input("Y")
            else:
                pass

            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Save changes successfully")
            return True

    def commit_changes_and_exit_menu(self):
        """Commit the boot management changes, then exit boot menu, this
        operation requires user to firstly navigate to BIOS page contains
        Commit Changes and Exit menu
        :return: True if commit changes and exit success, otherwise False
        """
        return self.press_menu("Commit Changes and Exit")

    def bios_discard_changes(self, by_hot_key=True):
        """Discard the configured BIOS changes, if not use hot key, this
        operation requires user to firstly navigate to BIOS page contains
        Discard Changes menu
        :param by_hot_key: whether use hot key to implement discard changes
        :return: True if discard changes success, otherwise False
        :raise: BiosConfigError
        """
        if by_hot_key:
            key = self._config.get_value(self._sut_config_file,
                                         "function_keys",
                                         "discard_changes",
                                         abort_on_failure=False)
            if key:
                self.bios_function_key_press(key)
                if self._bios_items["is_dialog_box"]:
                    # send 'Y' to confirm
                    self.bios_string_input("Y")
                else:
                    pass

                self._log_write(lib_constants.LOG_INFO,
                                "INFO: Discard changes successfully")
                return True
            else:
                self._log_write(lib_constants.LOG_ERROR,
                                "ERROR: Not get the function key to "
                                "discard changes in configuration")
                raise BiosConfigError(BiosConfigError.INVALID_SETTINGS)
        else:
            if not self.select_menu_option("Discard Changes"):
                return False

            # press "Enter"
            self.bios_control_key_press("ENTER")
            if self._bios_items["is_dialog_box"]:
                # send 'Y' to confirm
                self.bios_string_input("Y")
            else:
                pass

            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Discard changes successfully")
            return True

    def discard_changes_and_exit_menu(self):
        """Discard the boot management changes, then exit boot menu, this
        operation requires user to firstly navigate to BIOS page contains
        Discard Changes and Exit menu
        :return: True if discard changes and exit success, otherwise False
        """
        return self.press_menu("Discard Changes and Exit")

    def bios_get_boot_order(self):
        """In change boot order menu, enter boot menu and get its order,
        this operation requires user to firstly navigate to BIOS page contains
        change boot order menu
        :return: list of boot order item once item exists, otherwise False
        :raise: BiosConfigError
        """
        if not self.select_menu_option("Change the order", complete_matching=False):
            return False
        # press 'Enter' popup boot order submenu
        self.bios_control_key_press("ENTER")
        boot_order_item = [item[0] for item in self._bios_items["entries"]]
        # press 'Esc' to cancel change
        self.bios_control_key_press("ESC")
        return boot_order_item

    def bios_set_boot_order(self, boot_option, order=1, boot_option_index=1):
        """In change boot order menu, select boot option and change its order,
        this operation requires user to firstly navigate to BIOS page contains
        change the order option
        :param boot_option: boot option to be select
        :type boot_option: str
        :param order: order to be changed to, starts from 1
        :type order: int
        :param boot_option_index: index of items which have/contain duplicate boot option
        :type boot_option_index: int
        :return: True if boot order selection success, otherwise False
        :raise: BiosConfigError
        """
        if type(order) != int or order <= 0:
            self._log_write(lib_constants.LOG_WARNING,
                            "Input order is invalid value or type")
            raise BiosConfigError(BiosConfigError.INVALID_INPUT)

        if not self.select_menu_option("Change the order", complete_matching=False):
            return False

        # press 'Enter' popup boot order submenu
        self.bios_control_key_press("ENTER")
        # find boot option in boot order submenu
        if not self.select_menu_option(boot_option,
                                       complete_matching=False,
                                       index=boot_option_index):
            return False

        number_of_oder = len(self._bios_items["entries"])
        if order > number_of_oder:
            # press 'Esc' to cancel change
            self.bios_control_key_press("ESC")
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: The number of boot orders is %d, the "
                            "order %d to be set is out of range"
                            % (number_of_oder, order))
            return False

        # get the boot option order, due to the index of list
        # self._bios_item["entries"] starts from 0, so needs + 1 to calculate
        # the correct order
        boot_option_order = self._bios_items["highlight_idx"] + 1
        if boot_option_order > order:
            # move boot option up
            steps = boot_option_order - order
            self.bios_control_key_press("PLUS", times=steps)
        elif boot_option_order < order:
            # move boot option down
            steps = order - boot_option_order
            self.bios_control_key_press("MINUS", times=steps)

        # get the boot option order again
        boot_option_order = self._bios_items["highlight_idx"] + 1
        if boot_option_order == order:
            # press 'Enter' to confirm change
            self.bios_control_key_press("ENTER")
            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Success to change boot order")
            return True
        else:
            # press 'Esc' to cancel change
            self.bios_control_key_press("ESC")
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Failed to change boot order")
            return False

    def bios_exit(self, to_save=False):
        """Exit BIOS with configuration save or un-save, this operation
        requires user to firstly navigate to BIOS page contains Exit menu
        :param to_save: True to save, False to discard
        :type to_save: bool
        :return: True if exit success, otherwise False
        """
        if to_save:
            if not self.select_menu_option("Save Changes and Exit"):
                return False
        else:
            if not self.select_menu_option("Discard Changes and Exit"):
                return False

        # press 'Enter' to popup dialog box
        self.bios_control_key_press("ENTER")
        if self._bios_items["is_dialog_box"]:
            # send 'Y' to confirm
            self.bios_string_input("Y")

        self._log_write(lib_constants.LOG_INFO, "INFO: Exit successfully")
        return True

    def bios_load_default(self, by_hot_key=True):
        """Loads defaults config to BIOS, if not use hot key, this operation
        requires user to firstly navigate to BIOS page contains Load Default
        menu
        :param by_hot_key: True to load default by hot key;
                           False to load default by press BIOS menu
        :return: True if load default success, otherwise False
        :raise: BiosConfigError
        """
        if by_hot_key:
            key = self._config.get_value(self._sut_config_file,
                                         "function_keys",
                                         "load_defaults",
                                         abort_on_failure=False)
            if key:
                self.bios_function_key_press(key)
                if self._bios_items["is_dialog_box"]:
                    # send 'Y' to confirm
                    self.bios_string_input("Y")
                else:
                    pass

                self._log_write(lib_constants.LOG_INFO,
                                "INFO: Load Defaults successfully")
                return True
            else:
                self._log_write(lib_constants.LOG_ERROR,
                                "ERROR: Not get the function key to load "
                                "defaults in configuration")
                raise BiosConfigError(BiosConfigError.INVALID_SETTINGS)
        else:
            if not self.select_menu_option("Load Defaults", complete_matching=False):
                return False

            # press 'Enter'
            self.bios_control_key_press("ENTER")
            if self._bios_items["is_dialog_box"]:
                # send 'Y' to confirm
                self.bios_string_input("Y")
            else:
                pass

            self._log_write(lib_constants.LOG_INFO,
                            "INFO: Load Defaults successfully")
            return True

    def continue_system(self, to_save=True):
        """Continue system, this operation requires user to firstly navigate to
        BIOS page contains Continue menu
        :param to_save: True to save, False to discard
        :return: True if continue success, otherwise False
        """
        if not self.press_menu("Continue", False):
            return False

        if self._bios_items["is_dialog_box"]:
            if to_save:
                # send 'Y' to save changes
                self.bios_string_input("Y")
                if self._bios_items['is_dialog_box']:
                    # press ENTER to confirm reset
                    self.bios_control_key_press("ENTER")
            else:
                # send 'N' to discard changes
                self.bios_string_input("N")

        self._log_write(lib_constants.LOG_INFO,
                        "INFO: Continue system successfully")
        return True

    def reset_system(self, to_save=True):
        """Reset system, this operation requires user to firstly navigate to
        BIOS page contains Reset menu
        :param to_save: True to save changes, False to discard changes
        :return: True if reset success, otherwise False
        """
        if not self.press_menu("Reset", False):
            return False

        # check is there dialog box popup to confirm save changes or not
        if self._bios_items["is_dialog_box"]:
            if to_save:
                # enter 'Y' to save changes
                self.bios_string_input("Y")
            else:
                # enter 'N' to discard changes
                self.bios_string_input("N")

        self._log_write(lib_constants.LOG_INFO,
                        "INFO: Reset system successfully")
        return True

    def enter_bios(self, wait_timeout=600, f2_timeout=1, admin_pwd=""):
        """Press key to enter BIOS
        :param wait_timeout: wait time to catch 'Press [F2]' string from serial
        :param f2_timeout: time out between press F2 and goes into BIOS,
                           mainly for debug IFWI
        :param admin_pwd: Admin password to login BIOS setup
        :return: True while enter BIOS
        :raise: BiosConfigError
        """
        # clean existing data
        self._bios_items = None
        self.sp.clean_screen_data()

        # get function key to enter BIOS setup page
        key = self._config.get_value(self._sut_config_file,
                                     "function_keys",
                                     "enter_bios_setup_page",
                                     abort_on_failure=False)
        if not key:
            key = "F2"
        key_word = "[%s]" % key

        # set 600 seconds time out to wait for "Press [Fx]" option in
        # serial output
        wait_boot_timeout = wait_timeout
        # send any key event to open serial port, and keep opening
        self.sc.serial_io_hii_enum(1, "ESC", leave_closed=False)
        while wait_boot_timeout:
            # get data from serial port
            data = self.sc.serial_io_get_buffer(time_out=1)
            # parse data
            output = parse_edk_shell(data)
            # search key word in serial data
            if key_word in output:
                break
            wait_boot_timeout -= 1
        else:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: not found entry to go to BIOS")
            raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)

        # press function key for 50 times to ensure the key be actually triggered
        data = self.sc.serial_io_hii_enum(2, key, key_step=5, time_out=1, leave_closed=False)
        try:
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()
            # check whether has got BIOS page information
            self._check_bios_items()
        except BiosConfigError:
            data = self.sc.serial_io_get_buffer(f2_timeout)
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()
            self._check_bios_items()

        if self._bios_items['is_dialog_box']:
            # there might be request to enter password
            if self.search_item_in_dialog_box("Enter Password",
                                              complete_matching=False):
                self.bios_string_input(admin_pwd)
                self.bios_control_key_press("ENTER", time_out=3)
                if self._bios_items['is_dialog_box'] \
                        and self.search_item_in_dialog_box("Invalid Password",
                                                           complete_matching=False):
                    self._log_write(lib_constants.LOG_ERROR,
                                    "ERROR: Invalid Password to enter BIOS")
                    raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)
            # there might be dialog box popup via press "F2" for multiple times,
            # then should press "Esc" to close dialog box
            elif self.search_item_in_dialog_box("Discard configuration",
                                                complete_matching=False):
                self.bios_control_key_press("ESC")
            else:
                # there might be dialog box to let user to select option, then select
                # "Enter Setup" to enter BIOS
                self._select_option_in_dialog("Enter Setup")

        return True

    def reset_to_bios(self, to_save=True, wait_timeout=600, f2_press_wait=1, admin_pwd=""):
        """Click Reset menu in BIOS to reset system, wait for Press [F2] menu
        appear in serial port, then press it to enter BIOS
        :param to_save: True to save changes, False to discard changes
        :param wait_timeout: wait time to catch 'Press [F2]' string from serial
        :param f2_press_wait: wait time between press F2 and goes into BIOS,
                              mainly for debug IFWI
        :param admin_pwd: Admin password to login BIOS setup
        :return: True if reset and enter BIOS success, otherwise False
        :raise: BiosConfigError
        """
        self.reset_system(to_save)
        return self.enter_bios(wait_timeout=wait_timeout,
                               f2_timeout=f2_press_wait,
                               admin_pwd=admin_pwd)

    def select_boot_device(self, wait_timeout=600, f7_timeout=1, device_name=None):
        """Press key to enter BIOS
        :param wait_timeout: wait time to catch 'Press [F7]' string from serial
        :param f7_timeout: time out between press F7 and show dialog of select boot device,
                           mainly for debug IFWI
        :param device_name: boot device name, None is default to select first boot device
        :return: True while select boot device and press enter to boot
        :raise: BiosConfigError
        """
        # clean existing data
        self._bios_items = None
        self.sp.clean_screen_data()

        # get function key to enter BIOS setup page
        key = self._config.get_value(self._sut_config_file,
                                     "function_keys",
                                     "show_boot_menu_options",
                                     abort_on_failure=False)
        if not key:
            key = "F7"
        key_word = "[%s]" % key

        # set wait time out to wait for "Press [Fx]" option in
        # serial output
        wait_boot_timeout = wait_timeout
        # send any key event to open serial port, and keep opening
        self.sc.serial_io_hii_enum(1, "ESC", leave_closed=False)
        while wait_boot_timeout:
            # get data from serial port
            data = self.sc.serial_io_get_buffer(time_out=1)
            # parse data
            output = parse_edk_shell(data)
            # search key word in serial data
            if key_word in output:
                break
            wait_boot_timeout -= 1
        else:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: not found entry to select boot device")
            raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)

        # press function key for 15 times to ensure popup dialog of select boot device
        data = self.sc.serial_io_hii_enum(2, key, key_step=15, time_out=1, leave_closed=False)
        try:
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()
            # check whether has got BIOS page information
            self._check_bios_items()
        except BiosConfigError:
            data = self.sc.serial_io_get_buffer(f7_timeout)
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()
            # check whether has got BIOS page information
            self._check_bios_items()

        if device_name is not None:
            return self._select_option_in_dialog(device_name)
        else:
            self.bios_control_key_press("ENTER")
            return True

    def enter_efi_shell(self, volume_alias='', time_out=10, bios_navi_time=3):
        """Enter into EFI Shell from BIOS Boot Manager Menu, return mapping table
        :param volume_alias: volume alias name, such as: HD0n0b
        :param time_out: time out between select efi shell in BIOS Boot Manager Menu
                         and get 'Shell>' prompt in console
        :param bios_navi_time: time out of BIOS menu navigation
        :return: if provide volume_alias, and be searched in Mapping table, return mapped volume label;
                 if not provide volume_alias, or not be searched in Mapping table, return str list from console
                 otherwise return False
        """
        try:
            # navigate into Boot Manager Menu
            ret = self.bios_menu_navi(["Boot Manager Menu"], wait_time=bios_navi_time)
            if ret is False:
                self._log_write(lib_constants.LOG_WARNING,
                                "Failed to navigate to Boot Manager Menu")
                return False

            # to confirm there are boot options in boot device list
            self._check_bios_items()

            efi_shell_entries = ["UEFI Internal Shell", "EDK Shell", "EDK SHELL", "EFI Shell",
                                 "EFI SHELL", "Internal Shell", "Internal SHELL"]
            first_boot_device = None
            last_boot_device = None
            while True:
                # get current highlighted item
                boot_device = self._get_highlight_item_content()
                if boot_device == first_boot_device or boot_device == last_boot_device:
                    break

                for entry in efi_shell_entries:
                    if entry in boot_device:
                        # press Enter to goes into EFI Shell
                        data = self.sc.serial_io_hii_enum(1, "ENTER", key_step=1, time_out=time_out)
                        # get output data of mapping table and 'Shell>' prompt
                        ret_val = parse_edk_shell(data)

                        if "Shell>" not in ret_val:
                            self._log_write(lib_constants.LOG_WARNING,
                                            "Not caught 'Shell>' prompt, might be not enter in "
                                            "efi shell, or not give enough time out")
                            ret_val = False
                        elif volume_alias:
                            ret_val = ret_val.split('\r\n')
                            search_string = r'      (.*)\: Alias\(s\)\:' + str(volume_alias) + r'.*'
                            volume_label = list(filter(lambda x: re.match(search_string, x) is not None, ret_val))
                            if len(volume_label) > 0:
                                ret_val = volume_label[0].strip().split()[0]
                        return ret_val

                if first_boot_device is None:
                    first_boot_device = boot_device
                last_boot_device = boot_device
                self.bios_navigation_key_press("DOWN", time_out=bios_navi_time)

            self._log_write(lib_constants.LOG_WARNING,
                            "Not found EFI Shell entry in Boot Manager Menu")
            return False
        except BiosConfigError as e:
            self._log_write(lib_constants.LOG_ERROR, e)
            return False

    def efi_shell_cmd(self, command, time_out=3):
        """Run command in EFI shell.
        :param command: command to be ran
        :param time_out: operation time out to get output
        :return: output of command execution
        :rtype: string
        """
        data = self.sc.serial_plain_cmd(command, time_out)
        ret_val = parse_edk_shell(data)
        return ret_val

    def exit_efi_shell_to_bios(self, time_out=3):
        """Run exit command in EFI shell, back to BIOS page
        :param time_out: operation time out to back BIOS
        :return: success to return True, otherwise return False
        """
        try:
            command = "exit"
            data = self.sc.serial_plain_cmd(command, time_out)
            self.sp.feed(data)
            self._bios_items = self.sp.get_selectable_page()
            self._check_bios_items()
            return True
        except BiosConfigError:
            return False

    def find_file_in_fs(self, file_path):
        r"""In EFI shell, search file path in each file system, and return
        the full path
        :param file_path: file path, e.g. xxx.efi; xxx\xxx\xxx.exe
        :return: full path, if not found return None
        :rtype: string
        """
        for num in range(10):
            full_path = r"fs%d:\%s" % (num, file_path)
            # command to list files in file system fsX:
            command = "dir %s" % full_path
            ret = self.efi_shell_cmd(command)
            if "Directory of:" in ret:
                return full_path
        else:
            return None

    def bios_navigation_key_press(self, navi_key, times=1, time_out=2):
        """Quick implementation navigation function under the BIOS
        with the navigation key provided
        :param navi_key: navigation key in uppercase, key list as:
                         ['UP', 'DOWN', 'RIGHT', 'LEFT']
        :type navi_key: str
        :param times: number of times the navigation key be pressed
        type times: int
        :param time_out: operation time out to get data after press key
        type time_out: int
        :return: None
        """
        data = self.sc.serial_io_hii_enum(0, navi_key, key_step=times,
                                          time_out=time_out)
        self.sp.feed(data)
        self._bios_items = self.sp.get_selectable_page()

    def bios_function_key_press(self, func_key, times=1, time_out=2):
        """Quick implementation full function under the BIOS
        with the function key provided.
        :param func_key: function key in uppercase, key list as:
                         ['F1', 'F2', 'F3', 'F4', 'F5', 'F6',
                         'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        :type func_key: str
        :param times: number of times the function key be pressed
        type times: int
        :param time_out: operation time out to get data after press key
        type time_out: int
        :return: None
        """
        data = self.sc.serial_io_hii_enum(2, func_key, key_step=times,
                                          time_out=time_out)
        self.sp.feed(data)
        self._bios_items = self.sp.get_selectable_page()

    def bios_control_key_press(self, ctrl_key, times=1, time_out=3):
        """Quick implementation full control function under the BIOS
        with the control key provided
        :param ctrl_key: control key in uppercase, key list as:
                         ['ENTER', 'ESC', 'HOME', 'END', 'INSERT', 'SPACE',
                          'PLUS', 'MINUS', 'BACKSPACE', 'CTRL_ALT_DELETE']
        :type ctrl_key: str
        :param times: number of times the control key be pressed
        type times: int
        :param time_out: operation time out to get data after press key
        type time_out: int
        :return: None
        """
        data = self.sc.serial_io_hii_enum(1, ctrl_key, key_step=times,
                                          time_out=time_out)
        self.sp.feed(data)
        self._bios_items = self.sp.get_selectable_page()

    def bios_string_input(self, content, times=1, time_out=3):
        """Input string to BIOS through serial port
        :param content: string content to be input
        :type content: str
        :param times: number of times to input string
        type times: int
        :param time_out: operation time out to get data after input
        type time_out: int
        :return: None
        """
        data = self.sc.serial_io_hii_enum(3, content, key_step=times,
                                          time_out=time_out)
        self.sp.feed(data)
        self._bios_items = self.sp.get_selectable_page()

    def get_system_information(self, menu, index_to_query=1):
        """Traverse all submenus in current BIOS menu page with page up/down,
        to get the system information response to provided submenu name
        :param menu: BIOS submenu need to query its value
        :param index_to_query: if there are multiple submenus with same name as
                               provided submenu, need to give the index which
                               one to be query, the index starts from 1
        :return: value response to provided system submenu, or ""
        """
        if not menu:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: No menu option given")
            return ""

        value = ""
        values = []

        # page up to back to beginning of current BIOS menu
        while self._is_bios_page_scroll_up():
            self.bios_control_key_press("PAGE_UP")

        while True:
            values.extend(self.sp.get_value_by_key(menu))
            # return value directly if be queried
            if index_to_query <= len(values):
                value = values[index_to_query - 1]
                return value
            if self._is_bios_page_scroll_down():
                # page down to traverse all submenus
                self.bios_control_key_press("PAGE_DOWN")
            else:
                break

        if len(values) == 0:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Not found '%s' in the BIOS menu page"
                            % menu)
        else:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Index to query is out of range")

        return value

    def get_tc_id(self):
        """Return value of self._tc_id
        :return: self._tc_id
        """
        return self._tc_id

    def get_script_id(self):
        """Return value of self._script_id
        :return: self._script_id
        """
        return self._script_id

    def set_tc_id(self, tc_id):
        """Set new value to self._tc_id
        :param tc_id: tc_id new value
        :return: None
        """
        self._tc_id = tc_id

    def set_script_id(self, script_id):
        """Set new value to self._script_id
        :param script_id: script_id new value
        :return: None
        """
        self._script_id = script_id

    def is_checkbox_checked(self, menu=None):
        """If menu given, determine its checkbox is checked; if menu not
        given, determine the highlighted menu's checkbox is checked; if given
        menu is not found or not checkbox type, raise exception
        :param menu: BIOS menu to be determine
        :return: True while checkbox is checked;
                 False while checkbox is unchecked
        :rtype: bool
        :raise: BiosConfigError
        """
        checkbox_state = EntryType.UNKNOWN

        if menu:
            # traverse BIOS entries to find menu and its type
            for entry in self._bios_items["entries"]:
                if menu in entry[0]:
                    checkbox_state = entry[2]
                    break
        else:
            checkbox_state = self._get_highlight_item_type()

        if checkbox_state == EntryType.CHECKBOX_CHECKED:
            self._log_write(lib_constants.LOG_INFO, "Checkbox is checked")
            return True
        elif checkbox_state == EntryType.CHECKBOX_UNCHECKED:
            self._log_write(lib_constants.LOG_INFO, "Checkbox is unchecked")
            return False
        else:
            # type mismatching, the menu has no checkbox
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: Menu not be found, or the menu "
                            "has no checkbox")
            raise BiosConfigError(BiosConfigError.ITEM_TYPE_MISMATCH,
                                  "checkbox")

    def _select_option_in_dialog(self, option):
        """find the option in dialog box, and press ENTER to select it
        :param option: option to be select
        :return: True if option be selected, otherwise False
        """
        recorded_item = None
        # get length of bios entries
        entry_length = len(self._bios_items["entries"])
        while entry_length:
            entry_length -= 1
            for item in self._bios_items["entries"]:
                # find the selected item (be highlighted) in dialog
                if item[2] == EntryType.INPUT_BOX:
                    selected_item = item[0]
                    if str(option).lower() in selected_item.lower():
                        # matches with selected item and required option, then press ENTER
                        self.bios_control_key_press("ENTER")
                        self._log_write(lib_constants.LOG_INFO,
                                        "Selected the required option in boot device dialog")
                        return True

                    # on most server platform, if selected time equal to recorded item, means cannot
                    # move down cursor again, also means no new items in boot device list and not
                    # found the required one
                    if selected_item == recorded_item:
                        self._log_write(lib_constants.LOG_WARNING,
                                        "Not found required option '%s' in boot device dialog" % option)
                        return False
                    else:
                        # not matches the required option, record the item
                        recorded_item = selected_item
                        break

            if not recorded_item:
                self._log_write(lib_constants.LOG_WARNING,
                                "No highlighted option could be selected in boot device dialog")
                return False

            # move down cursor to new selection item
            self.bios_navigation_key_press("DOWN")

        # on some client platform, the cursor could be moved cyclically, so take the entries length as
        # the total cycles number of while loop. out of loop means has retrieved all the boot devices,
        # and not found the required one
        else:
            self._log_write(lib_constants.LOG_WARNING,
                            "Not found required option '%s' in boot device dialog" % option)
            return False

    def _select_device_volume(self, volume):
        """find the device volume in File Explorer, and press ENTER to select it
        :param volume: volume to be select
        :return: True if volume be selected, otherwise False
        """
        recorded_item = None
        # get length of bios entries
        entry_length = len(self._bios_items["entries"])
        while entry_length:
            entry_length -= 1
            if self._bios_items['highlight_idx'] is None:
                continue

            # find the highlighted item
            if self._get_highlight_item_type() == EntryType.MENU:
                selected_item = self._get_highlight_item_content()
                if str(volume).lower() in selected_item.lower():
                    # matches with selected item and required volume, then press ENTER
                    self.bios_control_key_press("ENTER")
                    self._log_write(lib_constants.LOG_INFO,
                                    "Selected the required volume: %s" % volume)
                    return True

                # on most server platform, if selected time equal to recorded item, means cannot
                # move down cursor again, also means no new items in file explorer list and not
                # found the required one
                if selected_item == recorded_item:
                    self._log_write(lib_constants.LOG_WARNING, "Not found required volume")
                    return False

                if recorded_item is None:
                    # not matches the required volume, record the item
                    recorded_item = selected_item

            # move down cursor to new selection item
            self.bios_navigation_key_press("DOWN")

        # on some client platform, the cursor could be moved cyclically, so take the entries length as
        # the total cycles number of while loop. out of loop means has retrieved all the HD volume,
        # and not found the required one
        else:
            self._log_write(lib_constants.LOG_WARNING, "Not found required volume")
            return False

    def _get_bios_page_info(self):
        """Get BIOS information list form current page.
        :return: all information on current BIOS page
        :rtype: list
        """
        return self.sp.get_whole_page()

    def _is_bios_page_scroll_up(self):
        """Check if the BIOS page could scroll up
        :return: True if could scroll up, otherwise False
        :rtype: bool
        """
        return self._bios_items["is_scrollable_up"]

    def _is_bios_page_scroll_down(self):
        """Check if the BIOS page could scroll down
        :return: True if could scroll down, otherwise False
        :rtype: bool
        """
        return self._bios_items["is_scrollable_down"]

    def _get_highlight_item_content(self):
        """Return the content of highlighted item.
        :return: item content
        :rtype: string
        """
        entry = self._bios_items["entries"]
        index = self._bios_items["highlight_idx"]
        item_content = entry[index][0]
        return item_content

    def _get_highlight_item_value(self):
        """Return the value of highlighted item.
        :return: item value
        :rtype: string
        """
        entry = self._bios_items["entries"]
        index = self._bios_items["highlight_idx"]
        item_value = entry[index][1]
        return item_value

    def _get_highlight_item_type(self):
        """Return the entry type of highlighted item.
        :return: item type, e.g. EntryType.MENU
        :rtype: int
        """
        entry = self._bios_items["entries"]
        index = self._bios_items["highlight_idx"]
        item_type = entry[index][2]
        return item_type

    def _check_bios_items(self):
        """Check the attribute _bios_items and its keys exist, will
        raise exception if one of them missing
        :return: None
        :raise: BiosConfigError
        """
        bios_page_info = self._get_bios_page_info()
        for info in bios_page_info:
            if info.strip():
                break
        else:
            raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)

        if not self._bios_items or \
                (not self._bios_items["title"] and
                 len(self._bios_items["entries"]) == 0):
            raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)

    def _path_finder_in_current_screen(self, menu, complete_matching=True):
        """From current screen with all selectable BIOS items, find and return
        the number of moving steps between given menu and highlight menu.
        :param menu: menu which should click to enter
        :type menu: str
        :param complete_matching: True to complete matching menu
                                  False to inclusion matching menu
        :type complete_matching: bool
        :return: find count and a list contains moving steps
        :rtype: int, list
        """
        path_index = 0
        find_count = 0
        moving_steps = []
        # traverse all entries in current BIOS screen
        for entry in self._bios_items["entries"]:
            entry_name = entry[0].strip()
            if complete_matching:
                # if entry has ' > ' at the beginning, split it
                if entry_name.startswith('>'):
                    entry_name = entry_name.split('>', maxsplit=1)[1]
                if menu == entry_name.strip():
                    find_count += 1
                    moving_steps.append(path_index - self._bios_items["highlight_idx"])
            else:
                if menu in entry_name:
                    find_count += 1
                    moving_steps.append(path_index - self._bios_items["highlight_idx"])
            path_index += 1

        return find_count, moving_steps

    def _path_finder(self, menu, complete_matching=True, index=1):
        """Page up/down with scrollable BIOS page, to find and return the
        number of moving steps between given menu and highlight menu.
        :param menu: menu to be searched
        :type menu: str
        :param complete_matching: True to complete matching menu
                                  False to inclusion matching menu
        :type complete_matching: bool
        :param index: index of items which have/contain duplicate menu name
        :type index: int
        :return: steps while path found
        :rtype: int
        :raise: BiosConfigError
        """
        if not menu:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'menu' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        # check if BIOS items have be initialized
        self._check_bios_items()

        while self._is_bios_page_scroll_up():
            # page up to find more menus
            self.bios_control_key_press("PAGE_UP")
            if self._bios_items["highlight_idx"] is None \
                    and len(self._bios_items["entries"]) > 0:
                self.bios_navigation_key_press("UP")

        index = index
        # while self._is_bios_page_scroll_down():
        while True:
            find_count, steps = self._path_finder_in_current_screen(menu, complete_matching)
            if find_count >= index:
                return steps[index-1]
            else:
                index -= find_count
            # page down to find more menus
            if self._is_bios_page_scroll_down():
                self.bios_control_key_press("PAGE_DOWN")
                if self._bios_items["highlight_idx"] is None \
                        and len(self._bios_items["entries"]) > 0:
                    self.bios_navigation_key_press("DOWN")
            else:
                break

        self._log_write(lib_constants.LOG_ERROR,
                        "Error: Menu '%s' not be found" % menu)
        raise BiosConfigError(BiosConfigError.MENU_PATH_NOT_FOUND, menu)

    def _gui_vert_move_cursor(self, query_item=None, steps=0):
        """From BIOS gui, vertically move cursor with steps, then query
        current highlighted item.
        :param query_item: item to be queried
        :type query_item: str
        :param steps: steps to be moved down/up
        :type steps: int
        :return: None
        :raise: CursorMovementError
        """
        if int(steps) == 0:
            self._log_write(lib_constants.LOG_INFO,
                            "input step is 0, no movement required")
            return True

        if int(steps) > 0:
            action = "DOWN"
        else:
            action = "UP"

        try:
            # move up/down and get BIOS page raw data through serial
            self.bios_navigation_key_press(action, times=abs(steps), time_out=1)
        except Exception as e:
            self._log_write(lib_constants.LOG_ERROR, "ERROR: %s" % e)
            raise BiosConfigError(BiosConfigError.FAILED_MOVE_CURSOR)

        # query item is highlighted item
        item_content = self._get_highlight_item_content()
        if query_item and query_item not in item_content:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: Menu '%s' not be highlighted" % query_item)
            raise BiosConfigError(
                BiosConfigError.FAILED_MOVE_CURSOR,
                query_item)

    def _log_write(self, level, log_msg):
        """Call write_log() or print() to write log to local file or console
        :param level: log levels defined in lib_constants.py
                      e.g. lib_constants.LOG_ERROR
        :param log_msg: log message
        :return: None
        """
        write_log(level, log_msg, self._tc_id, self._script_id,
                  loglevel=self._log_level)
