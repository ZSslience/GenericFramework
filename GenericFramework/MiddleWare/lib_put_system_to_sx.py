__author__ = "tnaidux/mmakhmox"

# Global Python Imports
import os
import time
from threading import Thread

# Local Python Imports
import library
import lib_constants
import lib_press_button_on_board
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


def put_system_to_sx(test_case_id, script_id, sx_state, source_button,
                     log_level="ALL", tbd=None):

    try:
        lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)
        ttk_device = lib_ttk2_operations.\
            gpio_initialize(test_case_id, script_id, log_level, tbd)

        thread1 = ThreadWithReturnValue(target=code_post_code,
                                        args=(test_case_id, script_id,
                                              sx_state, log_level, tbd))
        thread2 = ThreadWithReturnValue(target=code_button_press,
                                        args=(test_case_id, script_id,
                                              source_button, log_level, tbd))

        thread1.start()
        thread2.start()

        if thread1.join() and thread2.join():
            library.write_log(lib_constants.LOG_INFO, "INFO: %s pressed "
                              "successfully. SUT is in %s state"
                              % (source_button, sx_state), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "press %s or SUT is not in %s state"
                              % (source_button, sx_state), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def code_post_code(test_case_id, script_id, sx_state, log_level="ALL",
                   tbd=None):

    try:
        if "S3" == sx_state.upper():
            post_code = str(lib_constants.S3_POSTCODE)                          # S3 post code fetched from lib_constant
        elif "DEEPS3" == sx_state.upper():
            post_code = str(lib_constants.S3_POSTCODE)                          # S3 post code fetched from lib_constant
            led_code = str(lib_constants.DEEPS3_LED)                            # S3 led code fetched from lib_constant
        elif "S4" == sx_state.upper():
            post_code = str(lib_constants.S4_POSTCODE)                          # S4 post code fetched from lib_constant
        elif "DEEPS4" == sx_state.upper():
            post_code = str(lib_constants.S4_POSTCODE)                          # S4 post code fetched from lib_constant
            led_code = str(lib_constants.DEEPS4_LED)                            # S4 led code fetched from lib_constant
        elif "S5" == sx_state.upper():
            post_code = str(lib_constants.S5_POSTCODE)                          # S5 post code fetched from lib_constant
        elif "DEEPS5" == sx_state.upper():
            post_code = str(lib_constants.S5_POSTCODE)                          # S5 post code fetched from lib_constant
            led_code = str(lib_constants.DEEPS5_LED)                            # S5 led code fetched from lib_constant
        elif "CS" == sx_state.upper() or \
                "CONNECTED-MOS" == sx_state.upper() or \
                "CMOS" == sx_state.upper() or \
                "DISCONNECTED-MOS" == sx_state.upper() or \
                "DMOS" == sx_state.upper() or "CMS" == sx_state.upper():
            post_code = str(lib_constants.CS_POSTCODE)                          # CMOS/DMOS/CS post code fetched from lib_constant
        else:
            post_code = None

        library.write_log(lib_constants.LOG_INFO, "INFO: start to reading post code",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)

        if library.\
            check_for_post_code(post_code, lib_constants.DEBUG_COUNTER,
                                test_case_id, script_id, log_level, tbd):       # If post code found, pass
            if sx_state in lib_constants.DEEPSX:                                # If sx state id deeps3/deeps4/deeps5
                if lib_read_the_status_of_led.\
                    read_sx_led_status_using_lsd_device(sx_state, "ON",
                                                        test_case_id,
                                                        script_id, log_level,
                                                        tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: SUT is "
                                      "in %s state" % sx_state, test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return True
                else:                                                           # If failed to get the led status
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to put sut to %s state"
                                      % sx_state, test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: SUT is in %s "
                                  "state" % sx_state, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "put sut to %s state" % sx_state, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def code_button_press(test_case_id, script_id, source_button, log_level="ALL",
                      tbd=None):

    try:
        time.sleep(10)
        result = lib_press_button_on_board.\
            press_button(1, source_button, lib_constants.ON, test_case_id,
                         script_id, log_level, tbd)                             # Press required button

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s button has "
                              "been pressed successfully" % source_button,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "press %s button" % source_button, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
