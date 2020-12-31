__author__ = 'kvex/sushil3x/tnaidux/mmakhmox'

# Global Python Imports
import os
import subprocess
import time
from threading import Thread

# Local Python Imports
import library
import lib_constants
import lib_press_button_on_board
import utils
import lib_read_the_status_of_led
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={},
                 Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def wake_system_from_sx(test_case_id, script_id, sx_state, wake_source,
                        log_level="ALL", tbd=None):

    try:
        lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)
        ttk_device = lib_ttk2_operations.\
            gpio_initialize(test_case_id, script_id, log_level, tbd)

        thread1 = ThreadWithReturnValue(target=read_post_code,
                                        args=(test_case_id, script_id,
                                              sx_state, log_level, tbd))

        thread2 = ThreadWithReturnValue(target=wake_sut_from_sx,
                                        args=(test_case_id, script_id,
                                              wake_source, log_level, tbd))

        thread1.start()
        thread2.start()

        if thread1.join() and thread2.join():
            library.write_log(lib_constants.LOG_INFO, "INFO: %s pressed "
                              "successfully. SUT wake from %s state"
                              % (wake_source, sx_state), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "press %s or SUT is not in %s state"
                              % (wake_source, sx_state), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name     : read_post_code
# Parameters        : test_case_id, script_id, sx_state, log_level, tbd
# Functionality     : will wake the sut from sx state using required source
#                     and check the post code
# Return Value      : returns True on successful action and False otherwise
################################################################################


def read_post_code(test_case_id, script_id, sx_state, log_level="ALL",
                   tbd=None):

    try:
        if "S3" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S3_WAKE_POSTCODE]     # S3 post code fetched from lib constants
        elif "S4" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S4_WAKE_POSTCODE]     # S4 post code fetched from lib constants
        elif "S5" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S5_WAKE_POSTCODE]     # S5 post code fetched from lib constants
        elif "DEEPS3" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S3_WAKE_POSTCODE]     # S3 post code fetched from lib constants
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # S3 led code fetched from lib constants
        elif "DEEPS4" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S4_WAKE_POSTCODE]     # S4 post code fetched from lib constants
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # S4 led code fetched from lib constants
        elif "DEEPS5" == sx_state.upper():
            post_code = [x.lower() for x in lib_constants.S5_WAKE_POSTCODE]     # S5 post code fetched from lib constants
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # S5 led code fetched from lib constants
        elif "CS" == sx_state.upper() or "CMOS" == sx_state.upper() or \
                "DMOS" == sx_state.upper() or "CMS" == sx_state.upper():        # CS/CMOS/DMOS post code fetched from lib constants
            post_code = [x.lower() for x in lib_constants.CS_WAKE_POSTCODE]
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid SX "
                              "State", test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        if library.check_for_post_code(post_code, lib_constants.DEBUG_COUNTER,
                                       test_case_id, script_id, log_level,
                                       tbd):
            if sx_state in lib_constants.DEEPSX:
                if lib_read_the_status_of_led. \
                        read_sx_led_status_using_lsd_device(sx_state, "OFF",
                                                            test_case_id,
                                                            script_id,
                                                            log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: SUT wake "
                                      "from %s state" % sx_state, test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    time.sleep(60)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to wake sut from %s state"
                                      % sx_state, test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: SUT wake "
                                  "from %s state" % sx_state, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "wake SUT from %s state" % sx_state,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name     : wake_sut_from_sx
# Parameters        : test_case_id, script_id, sx_state, wake_source,
#                     log_level, tbd
# Functionality     : will wake the sut from sx state using required source
# Return Value      : returns True on successful action and False otherwise
################################################################################


def wake_sut_from_sx(test_case_id, script_id, wake_source, log_level="ALL",
                     tbd=None):

    try:
        if "PWR_BTN" == wake_source:
            result = lib_press_button_on_board.\
                press_button(1, "POWER", lib_constants.ON, test_case_id,
                             script_id, log_level, tbd)                         # Press power button

            time.sleep(30)                                                      # Delay to boot to OS
            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Power button "
                                  "has been pressed successfully",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to press power button", test_case_id,
                                  script_id, "TTK", "None", log_level, tbd)
                return False
        elif "LID_ACTION" == wake_source:
            result = lib_press_button_on_board.\
                press_button(1, "LID", lib_constants.ON, test_case_id,
                             script_id, log_level, tbd)                         # Press lid switch

            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Lid switch "
                                  "has been pressed successfully",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to press lid switch", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "MOUSE" == wake_source or "USB-MOUSE" == wake_source or \
             "PS2-MOUSE" == wake_source:                                        # If wake source is mouse/usb-mouse/ps/2mouse
            mouse_click = utils.ReadConfig("TTK", "MOUSE")                      # Left-click btn port fetched from config entry
            if "FAIL" in mouse_click:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: config "
                                  "entry is missing for tag MOUSE under section"
                                  " TTK", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            for i in range(lib_constants.THREE):
                press = library.ttk_set_relay("ON", int(mouse_click),
                                              test_case_id, script_id)
                time.sleep(lib_constants.DEFAULT_RELAY_PRESS_DURATION)
                release = library.ttk_set_relay("OFF", int(mouse_click),
                                                test_case_id, script_id)
                if 0 == press and 0 == release:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Mouse "
                                      "click pressed and released successfully"
                                      " for %d times" % (i+1), test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Mouse click press and release got "
                                      "failed", test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
        elif "LAN" == wake_source or "USB-LAN" == wake_source or \
                "WLAN" == wake_source or "WOL" == wake_source:                  # LAN, USB-LAN, WLAN as a wake source
            wol_path = utils.ReadConfig("WIFI", "wol_path")

            if "LAN" == wake_source or "WOL" == wake_source:
                wol_mac = utils.ReadConfig("WIFI", "wol_lan")                   # Reading from config file's
            elif "USB-LAN" == wake_source:
                wol_mac = utils.ReadConfig("WIFI", "wol_usblan")                # Reading from config file's
            elif "WLAN" == wake_source:
                wol_mac = utils.ReadConfig("WIFI", "wol_wlan")                  # Reading from config file's
            else:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Parameter "
                                  "not implemented", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            for item in [wol_path, wol_mac]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Config not present under [WIFI]",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False

            if os.path.exists(wol_path):
                library.write_log(lib_constants.LOG_INFO, "INFO: WOL path "
                                  "verified & config present under tag",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)                               # Continue execution,if wol path & config verified
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: WOL "
                                  "path is not verified", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            os.chdir(wol_path)
            time.sleep(lib_constants.FIVE_SECONDS)
            wol_command = lib_constants.WOL_COMMAND_WAKEUP + " " + wol_mac      # Getting command from lib constant

            result = os.system(wol_command)                                     # Running command

            if 0 == result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command for "
                                  "wake on %s is successfully executed"
                                  % wake_source, test_case_id, script_id,
                                  "None", "None", log_level, tbd)               # Continue execution if command is successful
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Command"
                                  " execution for wake on %s is un-successful"
                                  % wake_source, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        elif "KEYBOARD" == wake_source or "USB-KEYBOARD" == wake_source or \
             "PS2-KEYBOARD" == wake_source:
            keyboard_click = utils.ReadConfig("TTK", "KEYBOARD")

            if "FAIL" in keyboard_click:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: config "
                                  "entry is missing for tag KEYBOARD under "
                                  "section TTK", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            for i in range(lib_constants.THREE):
                press = library.ttk_set_relay("ON", int(keyboard_click),
                                              test_case_id, script_id)
                time.sleep(lib_constants.DEFAULT_RELAY_PRESS_DURATION)
                release = library.ttk_set_relay("OFF", int(keyboard_click),
                                                test_case_id, script_id)

                if 0 == press and 0 == release:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Keyboard "
                                      "key pressed and released successfully "
                                      "for %d times" % (i+1), test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Keyboard key press and release got "
                                      "failed", test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
