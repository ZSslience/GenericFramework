__author__ = r"tnaidux\surabh1x"

# General Python Imports
import os
import time
from threading import Thread

# Local Python Imports
import lib_constants
import library
import utils
import KBM_Emulation as kbm
import lib_ttk2_operations

postcode_lst = list()
result = False

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


def navigation_in_bios(original_string, environment, test_case_id, script_id,
                       log_level="ALL", tbd=None):

    try:
        current_post_code = library.\
            check_for_post_code(lib_constants.BIOS_PAGE_POSTCODE, 60,
                                test_case_id, script_id, log_level, tbd)

        if current_post_code[1] in lib_constants.BIOS_PAGE_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT is in %s "
                              "Setup" % environment, test_case_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: SUT is not "
                              "in %s Setup" % environment, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in [input_device_name, port]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get required config entries from Config.ini",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name identified as %s and %s from "
                              "Config.ini" % (port, input_device_name),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        time.sleep(lib_constants.SEND_KEY_TIME)                                 # Sleep for 0.5 seconds

        if "reset" in original_string.lower() and \
           "enter" in original_string.lower():
            time.sleep(lib_constants.SEND_KEY_TIME)                             # Sleep for 0.5 seconds
            k1.key_press("KEY_ESC")                                             # Pressing Esc Key
            time.sleep(lib_constants.SEND_KEY_TIME)                             # Sleep for 0.5 seconds
            k1.key_press("KEY_UP")                                              # Pressing UP Arrow
            time.sleep(lib_constants.SEND_KEY_TIME)                             # Sleep for 0.5 seconds
            k1.key_press("KEY_ENTER")                                           # Pressing Enter key
            time.sleep(lib_constants.FIVE_SECONDS)
            library.write_log(lib_constants.LOG_INFO, "INFO: Reset and Enter "
                              "key press performed successfully in BIOS Setup "
                              "using Keyboard-Mouse Simulator", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is not "
                              "handled" % original_string, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def navigation_in_os(original_string, test_case_id, script_id,
                     log_level="ALL", tbd=None):

    try:
        import lib_ttk2_operations
        lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)  #Kill old TTK2 services
        ttk_device = lib_ttk2_operations.gpio_initialize(test_case_id,
                                                    script_id, log_level, tbd)  #Initialize TTk2

        thread1 = ThreadWithReturnValue(target=verify_navigation,
                                        args=(original_string, test_case_id,
                                              script_id, log_level, tbd))       #Thread for verifying navigation
        thread2 = ThreadWithReturnValue(target=navigate_to_path,
                                        args=(original_string, test_case_id,
                                              script_id, log_level, tbd))       #Thread for navigating the path in OS

        thread1.start()
        thread2.start()

        if thread1.join() and thread2.join():
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "navigated to the path %s and verified it"
                              % (original_string),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "navigated to the path %s and verified it"
                              % (original_string),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def navigate_to_path(original_string, test_case_id, script_id,
                     log_level="ALL", tbd=None):                                #Navigate the path in OS
    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in [input_device_name, port]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get required config entries from Config.ini",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name identified as %s and %s from "
                              "Config.ini" % (port, input_device_name),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        if "-->" in original_string or "->" in original_string:
            navigate_path = original_string.split(":")[1]
            navigate_path = navigate_path.split()                               #Extracting the path to traverse in OS from token
            control_name = navigate_path[-1].strip()                            #Extract the control name

            if "start" in navigate_path[0].lower() and \
                            "power" in navigate_path[0].lower():

                k1 = kbm.USBKbMouseEmulation(input_device_name, port)
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_GUI d")                                       #Press key to select windows option
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_GUI x")                                       #Press key to select windows option
                time.sleep(lib_constants.SEND_KEY_TIME)
                k1.key_press("KEY_MENU u")                                      #Press key to select power options menu
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds

                if control_name.lower() == "restart":
                    time.sleep(lib_constants.SEND_KEY_TIME)                     # Sleep for 0.5 seconds
                    k1.key_type("r")                                            #select restart from power options menu
                elif control_name.lower() == "shutdown":
                    time.sleep(lib_constants.SEND_KEY_TIME)                     # Sleep for 0.5 seconds
                    k1.key_type("u")                                            #select shutdown from power options menu
                elif control_name.lower() == "sleep":
                    time.sleep(lib_constants.SEND_KEY_TIME)                     # Sleep for 0.5 seconds
                    k1.key_type("s")                                            #select sleep from power options menu
                elif control_name.lower() == "hibernate":
                    time.sleep(lib_constants.SEND_KEY_TIME)                     # Sleep for 0.5 seconds
                    k1.key_type("h")                                            #select hibernate from power options menu
                else:
                    pass
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: %s is successful" % original_string,
                                  test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
        elif "SHUTDOWNWINDOWS" in original_string.upper().replace(" ",""):
            control_name = original_string.split()[-1]
            k1 = kbm.USBKbMouseEmulation(input_device_name, port)

            if control_name.lower() == "restart":
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_type("r")                                                # select restart from power options menu
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_ENTER")
            elif control_name.lower() == "hibernate":
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_type("h")                                                # select hibernate from power options menu
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_ENTER")
            elif control_name.lower() == "shutdown" or \
                            control_name.lower() == "sleep":
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_GUI d")                                       #press key for desktop
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_ALT f4")                                      #press alt+f4 for shut down windows
                time.sleep(lib_constants.SEND_KEY_TIME)                         # Sleep for 0.5 seconds
                k1.key_press("KEY_ENTER")                                       #Press enter
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Implemenation"
                                  " is not done for %s" %control_name,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: %s is successful" % original_string,
                              test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Implemenation"
                              " is not done for %s" % original_string,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: Due to %s" %e_obj, test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return False


def verify_navigation(original_string, test_case_id, script_id,
                    log_level="ALL", tbd=None):                                 #Check the post code according to sx state
    try:
        if "POWER" in original_string.upper() or \
                "SHUTDOWNWINDOWS" in original_string.upper().replace(" ",""):
            if "HIBERNATE" in original_string.upper():
                post_code = lib_constants.S4_POSTCODE
            elif "SLEEP" in original_string.upper():
                post_code = lib_constants.S3_POSTCODE
            elif "SHUTDOWN" in original_string.upper():
                post_code = lib_constants.S5_POSTCODE
            else:
                post_code = None

            library.write_log(lib_constants.LOG_INFO, "INFO: Checking for"
                              " postcode %s" %post_code, test_case_id,
                              script_id, "None", "None", log_level, tbd)

            if "RESTART" in original_string.upper():
                for i in range(20):
                    time.sleep(.5)
                    curr_postcode = \
                        lib_ttk2_operations.read_post_code(test_case_id,
                                    script_id, log_level="ALL", tbd=None)
                    postcode_lst.append(curr_postcode)                          #Monitoring postcode while restarting the system
                postcode_set = set(postcode_lst)

                if (len(postcode_set) >= 3) and \
                        (postcode_lst[-1] in lib_constants.OS_POSTCODE):
                    result = postcode_set
                    library.write_log(lib_constants.LOG_INFO, "INFO: Result "
                                      "for setting the control is %s" % result,
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                else:
                    result = False
            else:
                result = lib_ttk2_operations.check_for_post_code(post_code,
                                      300, test_case_id, script_id,
                                      log_level="ALL", tbd=None)                #Checking for the required post code

            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully"
                                  " set the control option in OS", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable "
                                  "to set the control option in OS", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Implemenation"
                              " is not done for %s" % original_string,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return False
