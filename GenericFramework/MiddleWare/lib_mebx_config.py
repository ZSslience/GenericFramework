"""
File Name   : lib_mebx_config.py
Description : The MEBx config library provides methods, to navigate MEBx menu
              and set all config options
Author      : Jinliang
Created On  : 15 Jan 2020
Modified On : 19 Jan 2020
"""
import os

from HardwareAbstractionLayer.hal_serial_opt import SerialComm
from SoftwareAbstractionLayer import lib_constants
from SoftwareAbstractionLayer.vt100_screen_parser import ScreenParserMEBx
from SoftwareAbstractionLayer.vt100_screen_parser import parse_edk_shell
from SoftwareAbstractionLayer.lib_parse_config import ParseConfig
from MiddleWare.lib_bios_config import BiosConfigError
from MiddleWare.lib_bios_config import BiosMenuConfig


class MebxConfig(BiosMenuConfig):

    INITIAL_PASSWORD = "admin"

    def __init__(self, tc_id=None, script_id=None, loglevel="ALL", data=None):
        """Initialize BiosMenuConfig class.
        :param tc_id: test case id
        :param script_id: script id
        :param loglevel: log levels that allowed to be output
        :param data: data of MEBx interface captured from serial port when
                     entering MEBx. it's optional parameter, if no available
                     data, do not pass this parameter. and at the time to do
                     MEBx configuration, call mebx_initialize() to initialize
                     MEBx data
        """
        self.sc = SerialComm()
        self.sp = ScreenParserMEBx(tc_id, script_id)
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

    def mebx_initialize(self):
        """Initialize the MEBx home page and login, be called every time when
        enter into MEBx
        :return: None
        :raise: BiosConfigError
        """
        # press "Ctrl+Alt+Delete" to reboot system, next to press "CTRL+P" once
        # and wait for MEBx, then obtain the data of the bios home page
        self.sc.serial_io_hii_enum(1, "CTRL_ALT_DELETE",
                                   key_step=1,
                                   time_out=2,
                                   leave_closed=False)
        self.enter_mebx()

    def ctrl_p_press(self, times=1, time_out=1):
        """Press ctrl+p
        :param times: number of times the function key be pressed
        :type times: int
        :param time_out: operation time out to get data after press key
        :type time_out: int
        :return: None
        """
        data = self.sc.serial_io_hii_enum(4, "DLE", key_step=times,
                                          time_out=time_out)
        self.sp.feed(data)
        self._bios_items = self.sp.get_selectable_page()

    def enter_mebx(self):
        """Press key to enter MEBx
        :return: True while enter MEBx
        :raise: BiosConfigError
        """
        # define the key words to be pressed to enter to MEBx
        key_words = ["[CTRL+P]", "[CTRL-P]"]

        def find_keyword_in_buffer(words, buffer):
            for key_word in words:
                if key_word in buffer.upper():
                    return True
            else:
                return False

        # set 600 seconds time out to wait for "Press [CTRL+P]" option appear
        # in the serial output
        wait_boot_timeout = 600
        # send any key event to open serial port, and keep opening
        self.sc.serial_io_hii_enum(1, "ESC", leave_closed=False)
        while wait_boot_timeout:
            # get data from serial port
            data = self.sc.serial_io_get_buffer(time_out=2)
            # parse data
            output = parse_edk_shell(data)
            if find_keyword_in_buffer(key_words, output):
                break
            wait_boot_timeout -= 2
        else:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: not found entry to go to MEBx")
            raise BiosConfigError(BiosConfigError.BIOS_INITIALIZE_FAIL)

        # press ctrl+p with 5 times to ensure enter into the MEBx
        self.ctrl_p_press(times=5)
        # check whether has got MEBx page information
        self._check_bios_items()
        return True

    def mebx_login(self, password):
        """login MEBx with password
        :param password: password to MEBx login
        :return: None
        :raise: BiosConfigError
        """
        if not password:
            self._log_write(lib_constants.LOG_WARNING,
                            "WARNING: Parameter 'password' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        # select MEBx Login menu and press Enter
        if not self.select_menu_option("MEBx Login"):
            return False
        self.bios_control_key_press("ENTER", time_out=2)

        # login with password, if fail, then means first time login,
        # should enter initial password, and then set new password
        if self.search_item_in_dialog_box("ME Password", False):
            self.bios_string_input(password)
            self.bios_control_key_press("ENTER", time_out=2)
            if not self._bios_items['is_dialog_box']:
                self._log_write(lib_constants.LOG_INFO,
                                "INFO: No dialog box popup, login succeed")
                return True

            # cancel dialog box with login error, login with initial password
            self.bios_control_key_press("ESC")
            self.select_menu_option("MEBx Login")
            self.bios_control_key_press("ENTER", time_out=2)
            self.bios_string_input(self.INITIAL_PASSWORD)
            self.bios_control_key_press("ENTER", time_out=2)
            # login error with initial password
            if self.search_item_in_dialog_box("MEBx Login Error"):
                self._log_write(lib_constants.LOG_DEBUG,
                                "DEBUG: Invalid Initial Password")
                self.bios_control_key_press("ESC")
                return False
            # set new password
            if self.search_item_in_dialog_box("ME New Password", False):
                self.bios_string_input(password)
                self.bios_control_key_press("ENTER", time_out=2)
                # verify new password
                self.bios_string_input(password)
                self.bios_control_key_press("ENTER", time_out=2)
                if self._bios_items['is_dialog_box'] and \
                        self.search_item_in_dialog_box("MEBx Login Error"):
                    self._log_write(lib_constants.LOG_DEBUG,
                                    "DEBUG: Error applying new password")
                    self.bios_control_key_press("ESC")
                    return False
                self._log_write(lib_constants.LOG_INFO, "INFO: Login succeed")
                return True
            else:
                pass

    def search_item_in_dialog_box(self, item_name, complete_matching=True):
        """In a dialog box, search the item by provided item_name
        :param item_name: item name to be searched in dialog box
        :param complete_matching: True to complete matching item
                                  False to inclusion matching item
        :return: True if searched, otherwise False
        :raise: BiosConfigError
        """
        if not item_name:
            self._log_write(lib_constants.LOG_WARNING,
                            "Parameter 'item_name' cannot be empty")
            raise BiosConfigError(BiosConfigError.EMPTY_INPUT)

        if not self._bios_items['is_dialog_box']:
            self._log_write(lib_constants.LOG_ERROR,
                            "ERROR: The top screen is not a dialog box")
            raise BiosConfigError(BiosConfigError.ITEM_TYPE_MISMATCH,
                                  "dialog box")

        for item in self._bios_items["entries"]:
            if complete_matching and item_name == item[0].strip():
                return True
            elif not complete_matching and item_name in item[0]:
                return True
        else:
            return False

    def bios_back_home(self):
        """Back to MEBx main menu page.
        :return: None
        """
        max_times_to_press_esc = 10
        for _ in range(max_times_to_press_esc):
            # verify bios page information, to determine whether back at home
            # page: home page has no page title, but has other bios information
            bios_page_info = self._get_bios_page_info()
            if len(bios_page_info) > 0 and self._bios_items["title"] == "MAIN MENU":
                self._log_write(lib_constants.LOG_INFO,
                                "INFO: Back at BIOS home page now")
                return
            self.bios_control_key_press("ESC")

        self._log_write(lib_constants.LOG_ERROR,
                        "ERROR: Cannot back to BIOS home page after %d "
                        "times to press 'Esc'" % max_times_to_press_esc)
        raise BiosConfigError(BiosConfigError.KEY_EVENT_FAILURE, "ESC key")

    def mebx_exit(self):
        """Pree MEBx Exit to exit
        :return: True if exit succeed, otherwise False
        :raise: BiosConfigError
        """
        if not self.select_menu_option("MEBx Exit"):
            return False

        # press 'Enter' to popup dialog box, and send 'Y' to confirm
        self.bios_control_key_press("ENTER")
        if self._bios_items["is_dialog_box"]:
            self.bios_string_input("Y")

        self._log_write(lib_constants.LOG_INFO, "INFO: Exit successfully")
        return True
