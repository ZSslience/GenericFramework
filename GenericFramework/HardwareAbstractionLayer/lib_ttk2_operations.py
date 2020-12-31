"""
Script Name : lib_ttk2_operations.py
Version     : 0.1
Description : This library contain the operations performed using TTK2.0
Compatible  : Python2.7x
Created On  : 04 APR 2018
Modified On : 29 MAR 2019
"""

__author__ = 'mmahad3X/nnagachX/sedavlx/yusufmox/ashafeex/sushil3x/tnaidux/mmakhmox'

# Global python imports
import os
import re
import sys
import threading
import time
import mmap

# Local python imports
import library
import lib_constants
import lib_xmlcli
import utils
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    sys.path.append(lib_constants.TTK2_INSTALL_FOLDER)
    sys.path.append(lib_constants.TTK2_PYTHON_FILES_PATH)
    from TTK2_GpioPort import *
    from TTK2_PowerControl import *
    from TTK2_ConfigManager import *
    from TTK2_Port_80 import *
    from TTK2_I2C import *
    from TTK2_BiosProgrammer import *
    from TTK2_PlatformControl import *

# Global Variables
TTK2_APP_LIST = ["TTK2_Server.exe", "TTK2Client.exe"]
PVALUE_FLASH_IMAGE_BIOS = "BIOS"


class TtkReadThread(object):

    """
    Class Name   : TtkReadThread
    Parameters   : object
    Return Value : Class object
    Purpose      : To create a background thread for reading ttk post code
                   until stop() method of same class is called.
    """

    def __init__(self, ttk_device=None):

        """
        Function Name       : __init__(Constructor)
        Parameters          : ttk_device
        Functionality       : This is used to initialize class variables to
                              defaults
        Function Invoked    : None
        Return Value        : None
        """

        self.ttk_device = ttk_device
        self.stopped = False
        self.postcode = self.ttk_device.Read()
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                                                    # Daemonize thread
        thread.start()                                                          # Start the execution

    def run(self):

        """
        Function Name       : run()
        Parameters          : None
        Functionality       : This is used to read ttk device post code
                              until stopped variable is True
        Function Invoked    : ttk_device.Read()
        Return Value        : None
        """

        while True:
            if self.stopped:
                break
            self.postcode = self.ttk_device.Read()

    def read(self):

        """
        Function Name       : read()
        Parameters          : None
        Functionality       : This is used to return the postcode most recently
                              read
        Function Invoked    : None
        Return Value        : None
        """

        return self.postcode

    def stop(self):

        """
        Function Name       : stop()
        Parameters          : None
        Functionality       : This is used to stop the thread execution
        Function Invoked    : None
        Return Value        : None
        """

        self.stopped = True


def callback(name, *args):

    """
    Function Name     : callback
    Parameters        : name, *args
    Functionality     : It's a recursive function, which will log all the
                        events happening(Detecting chip, Chip select,
                        Detected Chip..)in TTk2 during flash_ifwi() into console
    Function Invoked  : None
    Return Value      : None
    """
    print(name)
    print(args[0])


def power_control_initialize(tc_id, script_id, log_level, tbd):

    """
    Function Name     : power_control_initialize
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : Initializes and returns power control object required
                        to perform ttk power related operations
    Function Invoked  : library.write_log(), power_interface.OpenPowerControl()
    Return Value      : Returns power control object on successful action
                        and False otherwise
    """

    ret_status = False
    try:
        power_interface = Power_Control()                                       # Initalizes an PowerControl object
        power_interface.OpenPowerControl()
        ret_status = power_interface
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From power_"
                          "control_initialize(), error raised due to %s"
                          % e_obj, tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)

    return ret_status


def gpio_initialize(tc_id, script_id, log_level, tbd):

    """
    Function Name     : gpio_initialize
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : Initializes and returns gpio object required
                        to perform ttk relay related operations
    Function Invoked  : library.write_log(), cfg.LoadXml(),
                        gpio_port_interface.OpenThumbking()
    Return Value      : Returns gpio object on successful action
                        and False otherwise
    """

    ret_status = False
    try:
        cfg = ConfigManager()
        plt_obj = cfg.LoadXml(lib_constants.GPIO_XML)
        port_num = lib_constants.TWO
        gpio_port_interface = GPIOPort()
        gpio_port_interface.OpenThumbking(plt_obj.GpioPorts[port_num])
        ret_status = gpio_port_interface
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From gpio_"
                          "initialize(), error raised due to %s" % e_obj,
                          tc_id, script_id, "TTK2", "None", log_level, tbd)
    return ret_status


def platform_control_initialize(tc_id, script_id, log_level, tbd):

    """
    Function Name     : platform_control_initialize
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : Initializes and returns platform control object required
                        to perform ttk related operations
    Function Invoked  : library.write_log(), cfg.LoadXml(),
                        plt_interface.OpenThumbking()
    Return Value      : Returns platform control object on successful action
                        and False otherwise
    """

    ret_status = False
    try:
        cfg = ConfigManager()
        plt_obj = cfg.LoadXml(lib_constants.PLATFORM_XML)
        plt_interface = Platform_Control()
        plt_interface.OpenThumbking(plt_obj)
        ret_status = plt_interface
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From platform_"
                          "control_initialize(), error raised due to %s"
                          % e_obj, tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def post_code_initialize(tc_id, script_id, log_level, tbd):

    """
    Function Name     : post_code_initialize
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : Initializes and returns post code object required
                        to read post code data
    Function Invoked  : library.write_log(), cfg.LoadXml(),
                        i2c.OpenThumbking(), p80_interface.OpenI2C()
    Return Value      : Returns I2C object on successful action
                        and False otherwise
    """

    ret_status = False
    try:
        cfg = ConfigManager()
        plt_obj = cfg.LoadXml(lib_constants.POSTCODE_XML)
        i2c = I2C()
        i2c_interface = i2c.OpenThumbking()
        p80_interface = Port_80()
        p80_interface.OpenPort80Interface()
        ret_status = p80_interface
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From post_code_"
                          "initialize(), error raised due to %s" % e_obj,
                          tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def perform_g3(dc_signal_port, dc_power_port, typec_port, tc_id, script_id,
               log_level, tbd):

    """
    Function Name     : perform_g3
    Parameters        : dc_signal_port, dc_power_port, typec_port, tc_id,
                        script_id, log_level, tbd
    Functionality     : Function will call the function which will Performs G3.
    Function Invoked  : library.write_log(), ac_on_off(), dc_typec_power_off()
    Return Value      : Returns True on successful action and False otherwise
    """

    try:
        if ac_on_off("OFF", lib_constants.TTK2_SWITCH_NO_AC, tc_id, script_id,
                     log_level, tbd):                                           # Function calling which will Power on/off AC power
            library.write_log(lib_constants.LOG_INFO, "INFO: AC Powered off "
                              "successfully", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)

            typec_dc_power_status = \
                dc_typec_power_off(dc_signal_port, dc_power_port, typec_port,
                                   tc_id, script_id, log_level, tbd)            # Function calling which will Power off DC and TypeC power
            if typec_dc_power_status:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                                  "performed TTK operation on DC and TypeC "
                                  "power source", tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_ERROR, "Failed to perform "
                                  "TTK operation on DC, TypeC power source",
                                  tc_id,  script_id, lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_ERROR, "Failed to perform AC "
                              "Power off action", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e_obj:                                                  # Exception in raised, if unable to perform G3
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In perform_g3()"
                          ", due to %s" % e_obj, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)
        return False


def perform_g3_reboot(dc_signal_port, dc_power_port, typec_port, tc_id,
                      script_id, log_level, tbd):

    """
    Function Name     : perform_g3_reboot
    Parameters        : dc_signal_port, dc_power_port, typec_port,
                        tc_id, script_id, log_level, tbd
    Functionality     : Function will call the function which will Performs G3
                        and power on AC to reboot the system
    Function Invoked  : library.write_log(), ac_on_off(),
                        dc_typec_power_off()
    Return Value      : Returns True on successful action and False otherwise
    """

    try:
        if ac_on_off("OFF", lib_constants.TTK2_SWITCH_NO_AC,
                     tc_id, script_id, log_level, tbd):                         # Calling function which will Power on/off AC power
            library.write_log(lib_constants.LOG_INFO, "INFO: AC Powered off "
                              "successfully", tc_id, script_id, "TTK2",
                              "None", log_level, tbd)

            typec_dc_power_status = \
                dc_typec_power_off(dc_signal_port, dc_power_port, typec_port,
                                   tc_id, script_id, log_level, tbd)            # Calling function which will Power off DC and TypeC power
            if typec_dc_power_status:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                                  "performed TTK operation on DC and TypeC "
                                  "power source", tc_id, script_id, "TTK2",
                                  "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to perform TTK operation on DC, TypeC power "
                                  "source", tc_id, script_id, "TTK2", "None",
                                  log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "perform AC Power off action", tc_id, script_id,
                              "TTK2", "None", log_level, tbd)
            return False

        time.sleep(lib_constants.SHORT_TIME)                                    #waiting for some time before powering on
        if ac_on_off("ON", lib_constants.TTK2_SWITCH_NO_AC,
                     tc_id, script_id, log_level, tbd):                         # Calling function which will Power on/off AC power
            library.write_log(lib_constants.LOG_INFO, "INFO: AC Powered ON "
                              "successfully after G3", tc_id, script_id,
                              "TTK2", "None", log_level, tbd)

            power = utils.ReadConfig("TTK", "POWER")
            if "FAIL:" in power:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get config entry for Power button from "
                                  "Config.ini", tc_id, script_id, "TTK2",
                                  "NONE", log_level, tbd)
                return False
            power_button_press = press_release_button(int(1), int(1), power,
                                                      int(30), tc_id,
                                                      script_id, log_level, tbd)
            if power_button_press:
                library.write_log(lib_constants.LOG_INFO, "INFO: Power button "
                                  "pressed successfully after AC Power ON",
                                  tc_id, script_id, "TTK2", "None", log_level,
                                  tbd)
                return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "Failed to perform AC "
                              "Power ON action after performing G3", tc_id,
                              script_id, "TTK2", "None", log_level, tbd)
            return False
    except Exception as e_obj:                                                  # Exception in raised, if unable to perform G3
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From perform_"
                          "g3(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def dc_typec_power_off(dc_signal_port, dc_power_port, typec_port, tc_id,
                       script_id, log_level, tbd):

    """
    Function Name     : dc_typec_power_off
    Parameters        : dc_signal_port, dc_power_port, typec_port, tc_id,
                        script_id, log_level, tbd
    Functionality     : Function will call  the Function which will Perform
                        turn off dc/typec power source
    Function Invoked  : library.write_log(), ttk_set_relay_dc()
                        ttk_set_relay_type_c
    Return Value      : Returns True on successful action and False otherwise
    """

    ret_status = False
    try:
        if "NC" == str(dc_signal_port).upper() or \
           "NC" == str(dc_power_port).upper():
            library.write_log(lib_constants.LOG_INFO, "INFO: DC Battery not "
                              "connected to SUT", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)                                   # Verifying whether DC port value is not applicable or not
            ret_status = True
        else:
            status = ttk_set_relay_dc("OFF", dc_signal_port,
                                      dc_power_port, tc_id, script_id,
                                      log_level, tbd)                           # Powering off DC power

            if not status:
                library.write_log(lib_constants.LOG_ERROR, "Failed to power "
                                  "off %s and %s relay ports for DC"
                                  % (dc_power_port, dc_signal_port), tc_id,
                                  script_id, lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "%s and %s relay "
                                  "ports for DC, powered off successfully"
                                  % (dc_power_port, dc_signal_port), tc_id,
                                  script_id, lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)

                if str(typec_port).upper() == "NC":                             # Verifying whether TypeC port value is not applicable or not
                    library.write_log(lib_constants.LOG_INFO, "TypeC device "
                                      "not connected to SUT", tc_id, script_id,
                                      lib_constants.TOOL_TTK2,
                                      lib_constants.STR_NONE, log_level, tbd)
                    ret_status = True
                else:
                    if ttk_set_relay_type_c("OFF", typec_port,
                                            tc_id, script_id, log_level, tbd):  # Calling function which will turn off TypeC power
                        library.write_log(lib_constants.LOG_INFO, "relay port "
                                          "%s for TypeC turned off "
                                          "successfully" % typec_port, tc_id,
                                          script_id, lib_constants.TOOL_TTK2,
                                          lib_constants.STR_NONE, log_level,
                                          tbd)
                        ret_status = True
                    else:
                        library.write_log(lib_constants.LOG_ERROR, "Failed to "
                                          "turn off relay port %s of TypeC "
                                          "power source" % typec_port, tc_id,
                                          script_id, lib_constants.TOOL_TTK2,
                                          lib_constants.STR_NONE, log_level,
                                          tbd)
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In dc_typec_"
                          "power_off(),due to: %s" % e_obj, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)
    return ret_status


def flash_ifwi(flash_image, flash_image_add, image_type_path, mac_id, tc_id,
               script_id, log_level="ALL", tbd=None):

    """
    Function Name     : flash_ifwi()
    Parameters        : flash_image, flash_image_add, image_type_path,
                        script_id, log_level, tbd
    Functionality     : TO flash the given image type on the SUT
    Return Value      : True on successful action, False otherwise
    """

    try:
        dc_signal_port = utils.ReadConfig("TTK", "dc_signal_port")
        dc_power_port = utils.ReadConfig("TTK", "dc_power_port")
        typec_power_port = utils.ReadConfig("TTK", "typec_power_port")
        port = "0"

        if "FAIL:" in [dc_signal_port, dc_power_port, typec_power_port]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get required config entries", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if perform_g3(dc_signal_port, dc_power_port, typec_power_port, tc_id,
                      script_id, log_level, tbd):                               # Performing G3 operation on SUT
            library.write_log(lib_constants.LOG_INFO, "INFO: Performed G3 "
                              "successfully", tc_id, script_id, "None", "None",
                              log_level, tbd)
        else:                                                                   # Failed to perform G3 operation on SUT
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "perform G3", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        result = flash_ifwi_core(flash_image, flash_image_add, image_type_path,
                                 mac_id, tc_id, script_id, log_level, tbd)      # Function call for to perform TTK operations on flashing

        if result:
            verify_image_version = lib_xmlcli.\
                read_image_version(image_type_path, result[1], tc_id, script_id,
                                   log_level, tbd)

            if verify_image_version:
                library.write_log(lib_constants.LOG_INFO, "INFO: Flash %s "
                                  "performed successfully on SUT and Offline "
                                  "image version is matching with %s"
                                  % (flash_image, result[1]), tc_id, script_id,
                                  "None", "None", log_level, tbd)

                time.sleep(lib_constants.SLEEP_TIME)
                ac_on_status = ac_on_off("ON", lib_constants.TTK2_SWITCH_NO_AC,
                                         tc_id, script_id, log_level, tbd)

                if ac_on_status:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Powered "
                                      "on AC performed successfully", tc_id,
                                      script_id, "None", "None", log_level, tbd)

                    time.sleep(lib_constants.SHORT_TIME)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to perform Power on AC", tc_id,
                                      script_id, "None", "None", log_level, tbd)
                    return False

                current_postcode = \
                    check_for_post_code(lib_constants.
                                        POSTCODE_OS_BOOT_SEQUENCE_LIST,
                                        lib_constants.WAIT_TIME, tc_id,
                                        script_id, log_level, tbd)              # Reading and verifying post code on SUT
                if current_postcode:
                    library.write_log(lib_constants.LOG_INFO, "POST code "
                                      "found with OS boot sequence", tc_id,
                                      script_id, lib_constants.TOOL_TTK2,
                                      lib_constants.STR_NONE, log_level, tbd)
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, "POST code not "
                                      "found with OS boot sequence", tc_id,
                                      script_id, lib_constants.TOOL_TTK2,
                                      lib_constants.STR_NONE, log_level, tbd)

                    power = utils.ReadConfig("TTK", "POWER")
                    if "FAIL:" in power:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "Failed to get config entry for Power"
                                          " button from Config.ini", tc_id,
                                          script_id, "TTK2", "NONE", log_level,
                                          tbd)

                    power_button_press = press_release_button(int(1), int(1),
                                                              power, int(30),
                                                              tc_id, script_id,
                                                              log_level, tbd)
                    if power_button_press:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Power "
                                          "button pressed successfully after "
                                          "AC Power ON", tc_id, script_id,
                                          "TTK2", "None", log_level, tbd)
                        return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Flash "
                                  "%s performed successfully on SUT. Offline "
                                  "image version is not matching with %s"
                                  % (flash_image, result[1]), tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "perform flash %s" % flash_image, tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


def reverify_post_code(dc_signal_port, dc_power_port, typec_port,
                       reverify_post_code_list, port, tc_id, script_id,
                       log_level, tbd):

    """
    Function Name     : reverify_post_code
    Parameters        : dc_signal_port, dc_power_port, typec_port,
                        reverify_post_code_list, port, tc_id, script_id,
                        log_level, tbd
    Functionality     : Verifies the post code after performing G3,
                        press, release power button
    Functions Invoked : perform_g3(), ac_on_off(), ttk2_set_relay(),
                        check_for_post_code(), library.write_log()
    Return Value      : True on success or False on failure
    """

    try:
        if perform_g3(dc_signal_port, dc_power_port, typec_port, tc_id,
                      script_id, log_level, tbd):                               # Performing G3 operation
            library.write_log(lib_constants.LOG_INFO, "Performing G3 was "
                              "Successful", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_ERROR, "Failed to perform g3",
                              tc_id, script_id, lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
            return False                                                        # Returns False if G3 operation is failed

        ac_on_status = ac_on_off(lib_constants.STR_ON,
                                 lib_constants.TTK2_SWITCH_NO_AC,
                                 tc_id, script_id, log_level, tbd)              # Turning on the ac power
        if ac_on_status:                                                        # Verifying ac power status
            press_release_power = \
                press_release_button(lib_constants.ONE, lib_constants.ONE,
                                     int(port), lib_constants.THIRTY_SECOND,
                                     tc_id, script_id, log_level, tbd)          # press and releasing the power button using ttk

            if press_release_power:
                library.write_log(lib_constants.LOG_INFO, "On and off of "
                                  "relay port %s for power button was "
                                  "successful" % port, tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_ERROR, "Failed do on and "
                                  "off of relay port %s for power button"
                                  % port, tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False

            current_postcode = \
                check_for_post_code(reverify_post_code_list,
                                    lib_constants.DEBUG_COUNTER, tc_id,
                                    script_id, log_level, tbd)                  # Reading and verifying post code on SUT
            if not current_postcode:
                library.write_log(lib_constants.LOG_ERROR, "POST code not "
                                  "found with OS boot sequence", tc_id,
                                  script_id, lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False                                                    # Returns False if post code does not match on SUT
            else:
                library.write_log(lib_constants.LOG_INFO, "POST code found "
                                  "with OS boot sequence", tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                return lib_constants.STR_PASS                                   # Returns PASS if post code matches
    except Exception as e_obj:                                                  # Raises an exception, if unable to reverify post code
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In reverify_"
                          "post_code(),due to: %s" % e_obj, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)
        return lib_constants.STR_FAIL


def ttk_set_relay_dc(action, dc_signal_port, dc_power_port, tc_id, script_id,
                     log_level, tbd):

    """
    Function Name    : ttk_set_relay_dc()
    Parameters       : action, dc_signal_port, dc_power_port, tc_id,
                       script_id, log_level, tbd
    Functionality    : This is used to turn on/off DC/TypeC devices
    Function Invoked : ttk2_set_relay(), turn_on_off_dc(), library.write_log()
    Return Value     : Returns True on Success or False on failure
    """

    try:
        dc_power_status = turn_on_off_dc(action, int(dc_signal_port),
                                         int(dc_power_port), tc_id, script_id,
                                         log_level, tbd)                        # Turn on the DC signal, power port

        if dc_power_status:
            library.write_log(lib_constants.LOG_INFO, "DC power source %s is "
                              "successful on relay ports %s and %s"
                              % (action, dc_signal_port, dc_power_port), tc_id,
                              script_id, lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "Failed to perform DC "
                              "power source operation %s on relay ports %s and "
                              "%s" % (action, dc_signal_port, dc_power_port),
                              tc_id, script_id, lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In ttk_set_"
                          "relay_dc(), due to %s" % e_obj, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)
        return False


def ttk_set_relay_type_c(action, type_c_signal_port, tc_id, script_id,
                         log_level, tbd):

    """
    Function Name   : ttk_set_relay_type_c()
    Parameters      : action, type_c_signal_port, tc_id, script_id,
                      log_level, tbd
    Functionality   : This is used to turn on/off DC/TypeC devices
    Function Invoked: ttk2_set_relay(), turn_on_off_dc(), library.write_log()
    Return Value    : Returns True on Success or False on failure
    """

    try:
        signal_port_type_c_high_status = \
            ttk2_set_relay(action, int(type_c_signal_port), tc_id, script_id,
                           log_level, tbd)                                      # Turning on the Typec port

        if signal_port_type_c_high_status:
            library.write_log(lib_constants.LOG_INFO, "Successfully performed"
                              " Type_C %s operation on relay port %s"
                              % (action, type_c_signal_port), tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "Unable to perform Type"
                              "_C power operation %s on relay port %s"
                              % (action, type_c_signal_port), tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In ttk_set_"
                          "relay_type_c(),due to %s" % e_obj, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)


def ttk_set_relay_virtual_battery(action, virtual_battery_signal_port, tc_id,
                                  script_id, log_level, tbd):

    """
    Function Name   : ttk_set_relay_virtual_battery()
    Parameters      : action, virtual_battery_signal_port, tc_id, script_id,
                      log_level, tbd
    Function Invoked: ttk2_set_relay(), library.write_log()
    Functionality   : This is used to turn on/off virtual battery
    Return Value    : Returns True on Success or False on failure
    """

    try:
        signal_port_virtual_battery_high_status = \
            ttk2_set_relay(action, int(virtual_battery_signal_port), tc_id,
                           script_id, log_level, tbd)                           # Turning on the virtual battery

        if signal_port_virtual_battery_high_status:
            library.write_log(lib_constants.LOG_INFO, "Successfully performed "
                              "virtual battery %s operation on relay port %s"
                              % (action, virtual_battery_signal_port), tc_id,
                              script_id, lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "Unable to perform "
                              "virtual battery power operation %son relay "
                              "port %s"
                              % (action, virtual_battery_signal_port), tc_id,
                              script_id, lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In ttk_set_"
                          "relay_virtual_battery(), due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)


def ac_on_off(action, switch_number, tc_id, script_id, log_level, tbd):

    """
    Function Name         : ac_on_off
    Parameters            : action, switch_number, tc_id,
                            script_id, log_level, tbd
    Functionality         : Function to switch on/off AC using TTK functions
    Function Invoked      : utils.write_to_log(),
                            power_control_initialize(), ttk_device.PortOn(),
                            ttk_device.GetPortState(), ttk_device.PortOff(),
                            ttk_device.Close()
    Return Value          : Returns True successful action
                            and False otherwise
    """

    ret_status = False
    try:
        switch_number = int(switch_number)                                      # Converting switch number to integer
        ttk_device = power_control_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is False:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK2 "
                              "failed", tc_id, script_id, "TTK2", "None",
                              log_level, tbd)
        else:
            if lib_constants.TTK_ACTION_ON == action:
                ttk_device.PortOn(switch_number)                                # Turns on AC port
                ret_status = ttk_device.GetPortState(switch_number)             # Fetches AC port status as a boolean value
                if ret_status is False:                                         # Returns False on turning on AC power
                    ret_status = True
                ttk_device.Close()
            elif lib_constants.TTK_ACTION_OFF == action:
                ttk_device.PortOff(switch_number)                               # Turns off AC port
                ret_status = ttk_device.GetPortState(switch_number)             # Fetches AC port status as a boolean value
                ttk_device.Close()
            else:
                library.write_log(lib_constants.LOG_INFO, "Invalid action, "
                                  "action should be either ON/OFF given %s"
                                  % action, tc_id, script_id, "TTK2",
                                  "None", log_level, tbd)
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In ac_on_off(), "
                          "error raised due to %s" % e_obj, tc_id, script_id,
                          "TTK2", "None", log_level, tbd)
    return ret_status

################################################################################
# Function Name : kill_ttk2
# Parameters    : None
# Return Value  : None
# Purpose       : Kill TTK2 service if running
################################################################################


def kill_ttk2(tc_id, script_id, log_level, tbd):
    try:
        task_list_text_file_path = r"C:\Testing\task_list.txt"
        if os.path.exists(task_list_text_file_path):
            os.remove(task_list_text_file_path)

        os.system('tasklist /FI "IMAGENAME eq TTK2_Server.exe" > %s'
                  % task_list_text_file_path)
        f = open(task_list_text_file_path)
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        if s.find(b'TTK2_Server.exe') != -1:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: TTK2_Server service is running, killing"
                              " now", tc_id, script_id, lib_constants.TOOL_TTK2,
                              "None", log_level, tbd)
            result = os.system("taskkill /F /IM TTK2_Server.exe")
            if 0 == result:
                time.sleep(1)
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: TTK2_Server.exe service killed "
                                  "successfully", tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to kill TTK2_Server.exe "
                                  "service", tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  "None", log_level, tbd)
                return False
    except Exception as err:
        print(("EXCEPTION: due to %s" % err))
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % err,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False

def press_release_button(duration, no_of_times, relay, press_delay, tc_id,
                         script_id, log_level, tbd):

    """
    Function Name     : press_release_button
    Parameters        : duration, no_of_times, relay, press_delay,
                        tc_id, script_id, log_level, tbd
    Functionality     : Function which will press and release the power/reset
                        button using ttk
    Function Invoked  : library.write_log(),
                        gpio_initialize(), ttk_device.GPIOSetMode(),
                        ttk_device.GPIOClearPins(), ttk_device.GPIOSetPins(),
                        ttk_device.Close()
    Return Value      : Returns True on successful action and False otherwise
    """

    ret_status = False
    try:
        ttk_device = gpio_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is None:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
        else:
            relay = int(relay)
            for count in range(0, no_of_times):
                ttk_device.GPIOSetMode(0x1 << relay, 0x1 << relay)
                ttk_device.GPIOClearPins(0x1 << relay)                          # Presses GPIO pin
                time.sleep(duration)
                ttk_device.GPIOSetMode(0x1 << relay, 0x1 << relay)
                ttk_device.GPIOSetPins(0x1 << relay)                            # Releases GPIO pin
                if no_of_times != 1:
                    time.sleep(press_delay)

            ttk_device.Close()
            ret_status = True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From press_"
                          "release_button(), error raised due to %s" % e_obj,
                          tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def clear_cmos(tc_id, script_id, log_level="ALL", tbd=None):

    """
    Function Name       : clear_cmos
    Parameters          : tc_id, script_id, log_level, tbd
    Purpose             : to clear rtc state using TTK
    Function Invoked    : utils.write_to_log(), get_ttk_device()
                          ClearCMOS()
    Return Value        : returns True if the given post code is seen within
                          the time limit and False otherwise
    """

    try:
        ttk_device = BiosProgrammer()
        if ttk_device is False:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, "None", log_level, tbd)
            return False
        else:
            ttk_device.ClearCMOS()                                              # Clearing CMOS
            ttk_device.Close()
            library.write_log(lib_constants.LOG_INFO, "Clearing CMOS "
                              "sucessfull", tc_id, script_id,
                              lib_constants.TOOL_TTK2, "None", log_level, tbd)
            return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From clear_"
                          "cmos(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def read_post_code(tc_id, script_id, log_level="ALL", tbd=None):

    """
    Function Name       : read_post_code
    Parameters          : tc_id, script_id, log_level, tbd
    Functionality       : This is used to read the current postcode
    Function Invoked    : utils.write_to_log(), ttk_device.Close()
                          post_code_initialize(), ttk_device.Read()
    Return Value        : returns True if post code is read sucessfully
                           and False otherwise
    """

    try:
        ttk_device = post_code_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is False:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, log_level, tbd)
            return False
        else:
            post_code_obj = ttk_device.Read()                                   # For reading current post code
            ttk_device.Close()
            return "%02x%02x" % (post_code_obj[0].Result[1],
                                 post_code_obj[0].Result[0])                    # Converting to hexadecimal format
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From read_post_"
                          "code(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def check_for_post_code(post_code, wait_time, tc_id, script_id, log_level,
                        tbd):

    """
    Function Name       : check_for_post_code
    Parameters          : post_code, wait_time, tc_id,
                          script_id, log_level, tbd
    Functionality       : This is used to verify whether fetched post code
                          matched with post code list or not
    Function Invoked    : utils.write_to_log(), ttk_device.Close()
                          post_code_initialize(), ttk_device.Read()
    Return Value        : returns True if the given post code is verified within
                          the time limit and False otherwise
    """

    return_status = False
    ttk_device = False
    current_post_code_set = set()
    try:
        ttk_device = post_code_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is False:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2,
                              lib_constants.STR_NONE, log_level, tbd)
        else:
            start_time = time.time()
            post_code_obj = TtkReadThread(ttk_device)
            while True:
                current_post_code = post_code_obj.read()                        # For reading current post code
                current_post_code = "%02x%02x" % \
                                    (current_post_code[0].Result[1],
                                     current_post_code[0].Result[0])            # Converting to hexadecimal format
                time_stamp = time.time() - start_time
                current_post_code_set.add(current_post_code)
                if current_post_code.lower() in post_code:                              # The expected post code is found
                    library.write_log(lib_constants.LOG_INFO, "INFO: SUT shows "
                                      "post code %s" % current_post_code, tc_id,
                                      script_id, lib_constants.TOOL_TTK2,
                                      lib_constants.STR_NONE, log_level, tbd)
                    post_code_obj.stop()
                    return True, current_post_code
                    break
                elif time_stamp >= wait_time:                                   # Post code not found even after wait time
                    library.write_log(lib_constants.LOG_INFO, "SUT doesn't "
                                      "show correct post code %s" % post_code,
                                      tc_id, script_id,
                                      lib_constants.TOOL_TTK2,
                                      lib_constants.STR_NONE, log_level, tbd)
                    post_code_obj.stop()
                    break
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From check_for_"
                          "post_code(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    finally:
        library.write_log(lib_constants.LOG_INFO, "INFO: Retrieved Post codes "
                          "list: %s" % current_post_code_set, tc_id, script_id,
                          lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                          log_level, tbd)
        if ttk_device:
            ttk_device.Close()
    return return_status


def ttk2_set_relay(action, relay, tc_id, script_id, log_level, tbd):

    """
    Function Name    : ttk2_set_relay
    Parameters       : action, relay, tc_id, script_id, log_level, tbd
    Functionality    : This will turn on/off GPIO pins
    Function Invoked : gpio_initialize(), ttk_device.GPIOSetMode(),
                       library.write_log(), ttk_device.GPIOClearPins(),
                       ttk_device.GPIOSetPins(), ttk_device.Close()
    Return Value     : Returns True on successful action and False otherwise
    """

    ret_status = False
    ttk_name = "TTK2_Server.exe"
    result = utils.execute_with_command("tasklist", tc_id, script_id,
                                        lib_constants.STR_NONE,
                                        log_level="ALL", tbd="None")
    if result.return_code == 0:
        for app in result.stdout.split(','):
            if ttk_name == app:
                task_kil_command = "taskkill /f /im TTK2_Server.exe"
                os.system(task_kil_command)
    try:
        ttk_device = gpio_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is None:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed ", tc_id, script_id, "TTK2", "None",
                              log_level, tbd)
        else:
            if lib_constants.TTK_ACTION_ON == action:
                ttk_device.GPIOSetMode(0x1 << relay, 0x1 << relay)
                ttk_device.GPIOClearPins(0x1 << relay)                          # Turns on GPIO pin
                time.sleep(1)
                ttk_device.Close()
                ret_status = True
            else:
                ttk_device.GPIOSetMode(0x1 << relay, 0x1 << relay)
                ttk_device.GPIOSetPins(0x1 << relay)                            # Turns off GPIO pin
                time.sleep(1)
                ttk_device.Close()
                ret_status = True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From ttk2_set_"
                          "relay(), error raised due to %s" % e_obj, tc_id,
                          script_id, "TTK2", "None", log_level, tbd)
    return ret_status


def turn_on_off_dc(action, signal_port, power_port, tc_id, script_id,
                   log_level, tbd):

    """
    Function Name    : turn_on_off_dc
    Parameters       : action, signal_port, power_port, tc_id,
                       script_id, log_level, tbd
    Functionality    : This will turn on/off DC device
    Function Invoked : gpio_initialize(),ttk_device.GPIOSetMode(),
                       library.write_log(), ttk_device.GPIOClearPins(),
                       ttk_device.GPIOSetPins(), ttk_device.Close()
    Return Value     : Returns True on successful action and False otherwise
    """

    ret_status = False
    try:
        ttk_device = gpio_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is None:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
        else:
            if lib_constants.TTK_ACTION_ON == action:
                ttk_device.GPIOSetMode(0x1 << signal_port, 0x1 << signal_port)
                ttk_device.GPIOClearPins(0x1 << signal_port)                    # Turns on DC signal GPIO pin
                time.sleep(lib_constants.ONE)
                ttk_device.GPIOSetMode(0x1 << power_port, 0x1 << power_port)
                ttk_device.GPIOClearPins(0x1 << power_port)                     # Turns on DC power GPIO pin
                ttk_device.Close()
                ret_status = True
            else:
                ttk_device.GPIOSetMode(0x1 << power_port, 0x1 << power_port)    # Turns off DC power GPIO pin
                ttk_device.GPIOSetPins(0x1 << power_port)
                time.sleep(lib_constants.ONE)
                ttk_device.GPIOSetMode(0x1 << signal_port, 0x1 << signal_port)
                ttk_device.GPIOSetPins(0x1 << signal_port)                      # Turns off DC signal GPIO pin
                ttk_device.Close()
                ret_status = True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: From turn_on_"
                          "off_dc(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def flash_ifwi_core(flash_image, flash_image_add, image_path, mac_id, tc_id,
                    script_id, log_level="ALL", tbd=None):

    """
    Function Name     : flash_ifwi_core()
    Parameters        : flash_image, flash_image_add, image_path, mac_id,
                        tc_id, script_id, log_level, tbd
    Functionality     : Detects, erases chip, Loads the BIN file content and
                        write into SPI device, Sets the MAC and clears CMOS
    Functions Invoked : library.write_log(), ttk_device.OpenThumbking(),
                        ttk_device.SubscribeEvent(),
                        ttk_device.SetChipSelect(),
                        ttk_device.SetCheckPowerIsOn(),
                        ttk_device.DetectChip(), ttk_device.Program(),
                        ttk_device.Erase(), ttk_device.LoadImage(),
                        ttk_device.BlankCheck(), ttk_device.Verify(),
                        ttk_device.ClearCMOS(), ttk_device.ReadBiosVersion(),
                        ttk_device.Close(), ttk_device.SetCustomMacAddress(),
                        ttk_device.ReadMacAddressFromChip(),
                        ttk_device.OverrideMacAddress()
    Return Value      : Returns True on success or False on Failure
    """

    try:
        ttk_device = BiosProgrammer()
        ttk_device.OpenThumbking()
        ttk_device.SubscribeEvent("MsgEventHandler", callback)
        ttk_device.SetCheckPowerIsOn(False)
        ttk_device.SetChipSelect(0)

        if PVALUE_FLASH_IMAGE_BIOS == flash_image.upper():
            flash_image_add = int(flash_image_add, 16)
            ttk_device.DetectChip()
            ttk_device.SetStartAddress(flash_image_add)
            ttk_device.Erase()
            ttk_device.BlankCheck()
            ttk_device.LoadImage(image_path)
            ttk_device.Program()
            ttk_device.Verify()
            ttk_device.ClearCMOS()
            bios_version_obj = ttk_device.ReadBiosVersion()
        elif mac_id == "NA":
            mac_id = ttk_device.ReadMacAddressFromChip()
            ttk_device.DetectChip()
            ttk_device.Erase()
            ttk_device.BlankCheck()
            ttk_device.LoadImage(image_path)
            ttk_device.Program()
            ttk_device.Verify()
            ttk_device.SetCustomMacAddress(mac_id)
            ttk_device.ClearCMOS()
            bios_version_obj = ttk_device.ReadBiosVersion()
        else:
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",
                        mac_id.lower()):                                        # Validating the MAC Address format
                new_mac_id = [int(x.encode("ASCII"), 16) for x in
                              mac_id.split(":")]                                # Getting the Byte array of decimal numbers from the input MAC ID

                ttk_device.DetectChip()
                ttk_device.Erase()
                ttk_device.BlankCheck()
                ttk_device.LoadImage(image_path)
                ttk_device.Program()
                ttk_device.Verify()
                ttk_device.OverrideMacAddress(0x1000, 4 * 1024, new_mac_id)
                ttk_device.ClearCMOS()
                bios_version_obj = ttk_device.ReadBiosVersion()
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Please "
                                  "provide valid MAC ID through config", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

        if bios_version_obj is not None:
            library.write_log(lib_constants.LOG_INFO, "INFO: BIOS Version "
                              "after %s Flash is %s"
                              % (flash_image, bios_version_obj.MajorVersion),
                              tc_id, script_id, "None", "None", log_level, tbd)
            ttk_device.Close()
            return True, bios_version_obj.MajorVersion
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "read BIOS version", tc_id, script_id, "None",
                              "None", log_level, tbd)
            ttk_device.Close()
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        ttk_device.Close()
        return False


def read_led_status_ttk2(led_code, wait_time, s3_port, s4_port, s5_port,
                         sus_port, test_case_id, script_id, tool, target_os,
                         log_level, tbd):

    """
    Function Name : read_led_status_ttk2
    Parameters    : led_code,wait_time, s3_port, s4_port, s5_port, sus_port,
                    test_case_id, script_id, tools, target_os, log_level, tbd
    Functionality : Function to get verify LED status for all SX state
    Return Value  : (Bool)'True' on successful action and 'False' on failure
    """

    if (s3_port is False) or (s4_port is False) or (s5_port is False) or \
       (sus_port is False):
        library.write_log(lib_constants.LOG_ERROR, "Config entry is not "
                          "updated, Update config for s3_led, s4_led, s5_led "
                          "and sus_led", test_case_id, script_id, tool,
                          lib_constants.STR_NONE, log_level, tbd)
    else:
        counter = lib_constants.ZERO
        while counter < wait_time:
            value = get_gpio_pin(test_case_id, script_id, log_level, tbd)
            if value is not None:
                led_stat = [int(value[int(s3_port)]), int(value[int(s4_port)]),
                            int(value[int(s5_port)]), int(value[int(sus_port)])]

            convert_first_to_string = (str(w) for w in led_stat)
            final_val = ''.join(convert_first_to_string)
            if led_code == final_val:                                           # if current led status and pre-defined led status matches
                library.write_log(lib_constants.LOG_INFO, "INFO: LED status "
                                  "for sx state is verified successfully",
                                  test_case_id, script_id, tool,
                                  lib_constants.STR_NONE, log_level, tbd)
                return True
        counter = counter + 1                                                   # wait till debug-counter time for led check
    library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed to verify LED "
                      "status for sx state", test_case_id, script_id, tool,
                      lib_constants.STR_NONE, log_level, tbd)
    return False


def get_gpio_pin(tc_id, script_id, log_level, tbd):

    """
    Function Name    : get_gpio_pin
    Parameters       : test_case_id, script_id, log_level, tbd
    Function Invoked : gpio_initialize(), library.write_log(),
                       ttk_int.GPIOGetPins()
    Functionality    : Function to get GPIO pin value
    Return Value     : binary value on successful else False
    """

    try:
        ttk_int = gpio_initialize(tc_id, script_id, log_level, tbd)
        if not ttk_int:
            library.write_log(lib_constants.LOG_ERROR, "Failed initialise TTK "
                              "object", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return False

        value = ttk_int.GPIOGetPins()                                           # get the GPIO pin status using TTK2
        value = bin(value)[2:]
        value=value.zfill(8)
        value = value[::-1]                                                     # Convert the value to binary value
        return value
    except Exception as e_obj:                                                  # Raises an exception, if unable to read bin file or updating SPI chip
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In get_gpio_"
                          "pin(), error raised due to : %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def get_ttk2_gpio_status(port_no, tc_id, script_id, log_level, tbd):

    """
    Function Name     : get_ttk2_port_status
    Parameters        : port_no, tc_id, script_id, log_level, tbd
    Functionality     : reads the status of ttk2 gpio ports
    Function Invoked  : library.write_log(), gpio_initialize()
    Return Value      : True if the port is high
                        False if port is low
    """

    ret_status = False
    try:
        gpio_interface = gpio_initialize(tc_id, script_id, log_level, tbd)
        pin_states = gpio_interface.GPIOGetPins()

        if pin_states:
            if int(pin_states) & (1 << int(port_no)) == 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: Port %s in "
                                  "ON state" % port_no, tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                ret_status = True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Port %s in "
                                  "OFF state" % port_no, tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                ret_status = False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNINING: Unable "
                              "to get ttk2 gpio status", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            ret_status = False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In get_ttk2_"
                          "gpio_status(), error raised due to %s" % e_obj,
                          tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def get_ttk2_ac_switch_status(switch_number, tc_id, script_id, log_level, tbd):

    """
    Function Name     : get_ttk2_ac_switch_status
    Parameters        : switch_number, tc_id, script_id, log_level, tbd
    Functionality     : reads the status of ttk2 gpio ports
    Function Invoked  : library.write_log(), gpio_initialize(),
                        ttk_device.GetPortState()
    Return Value      : True if the switch is high
                        False if switch is low
    """

    ret_status = False
    try:
        ttk_device = power_control_initialize(tc_id, script_id, log_level, tbd)
        if ttk_device is False:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
        else:
            status = ttk_device.GetPortState(int(switch_number))                # Fetches AC port status as a boolean value
            ttk_device.Close()
            if not status:                                                      # Returns False on turning on AC power
                ret_status = True
            else:
                library.write_log(lib_constants.LOG_INFO, "Detected AC switch "
                                  "is in OFF state", tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In get_ttk2_ac_"
                          "switch_status(), error raised due to %s" % e_obj,
                          tc_id, script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return ret_status


def config_jumper_ttk2(gpio_pin, connection_status, tc_id, script_id, tool,
                       log_level, tbd):

    """
    Function Name     : config_jumper_ttk2
    Parameters        : gpio_pin(int, eg: 2), connection_status_list(string,
                        eg: ON/OFF), tc_id, script_id, tool, log_level, tbd
    Functionality     : Turn on or off the given relay  for configuring
                        jumper pins
    Return Value      : Returns True on successful action and False otherwise
    """

    try:
        if not ttk2_set_relay(connection_status, gpio_pin, tc_id, script_id,
                              log_level, tbd):
            library.write_log(lib_constants.LOG_ERROR, "Failed to set gpio "
                              "state", tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "Successfully set gpio "
                              "pin state", tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return True

    except Exception as ex:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception while "
                          "setting gpio pins using ttk2 tool: %s" % ex, tc_id,
                          script_id, tool, lib_constants.STR_NONE, log_level,
                          tbd)
        return False


def ttk2_reset_relay(action, tc_id, script_id, log_level, tbd):

    """
    Function Name    : ttk2_reset_relay
    Parameters       : action, relay, tc_id, script_id, log_level, tbd
    Functionality    : This will turn on/off all relay ports
    Function Invoked : gpio_initialize(), library.write_log()
    Return Value     : Returns True on successful action and False otherwise
    """

    library.write_log(lib_constants.LOG_INFO, "Function to turn ON/OFF relay "
                      "device based on action", tc_id, script_id,
                      lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                      log_level, tbd)
    try:
        ttk_device = gpio_initialize(tc_id, script_id, log_level, tbd)          # Initialising TTK2
        if ttk_device is None:
            library.write_log(lib_constants.LOG_ERROR, "Initializing TTK "
                              "failed", tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return False

        if "off" == str(action).lower():                                        # If off is he action then turning OFF all the relay ports
            for pin_number in range(8):
                library.write_log(lib_constants.LOG_INFO, "Turning OFF GPIO "
                                  "pin %s" % pin_number, tc_id, script_id,
                                  lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                #time.sleep(lib_constants.TWO)
                #ttk_device.GPIOSetMode(0x1 << pin_number, 0x1 << pin_number)
                ttk_device.GPIOSetPins(0x1 << pin_number)
            return True

        elif "on" == str(action).lower():                                       # If on is he action then turning ON all the relay ports
            for pin_number in range(8):
                library.write_log(lib_constants.LOG_INFO, "Turning ON GPIO "
                                  "pin %s" % str(pin_number), tc_id,
                                  script_id, lib_constants.TOOL_TTK2,
                                  lib_constants.STR_NONE, log_level, tbd)
                #time.sleep(2)
                #ttk_device.GPIOSetMode(0x1 << pin_number, 0x1 << pin_number)
                ttk_device.GPIOClearPins(0x1 << pin_number)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "invalid action %s"
                              % str(action), tc_id, script_id,
                              lib_constants.TOOL_TTK2, lib_constants.STR_NONE,
                              log_level, tbd)
            return False

    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: In ttk2_reset_"
                          "relay(), error raised due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_TTK2,
                          lib_constants.STR_NONE, log_level, tbd)
    return False
