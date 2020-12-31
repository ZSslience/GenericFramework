__author__ = "jkmody"

# General Python Imports
import os
import platform
import time
import wmi

# Local Python Imports
import lib_constants
import library
import utils

################################################################################
# Function Name : device_state_verification
# Parameters    : device_name,test_case_id, script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To Check whether a device is enable or disable in
#                   device manager
################################################################################


def device_state_verification(device_name, action, device_ID, test_case_id,
                              script_id, log_level="ALL", tbd=None):

    try:
        WMI_info = wmi.WMI()
        dev_status_flag = WMI_info.query("SELECT * from Win32_PnPEntity where "
                                         "Name = "+ '"' + device_name + '"' +
                                         " AND Status = 'OK'")                  # Getting the device status(Enable/Disable) from Device manager

        if len(dev_status_flag) > 0 and action == "ENABLE":
            dev_status_flag = True                                              #Device is in Enable state
        elif len(dev_status_flag) == 0 and action == "DISABLE":
            dev_status_flag = True                                              #Device is in Disable state
        else:
            dev_status_flag = False                                             #Device is in Disable state
        return dev_status_flag
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : enable_disable_devices
# Parameters    : original_string, test_case_id, script_id, log_level, tbd
# Return Value  : action,Device name and (True on success, False on failure)
# Functionality : To Enable/Disable a device  in device manager
################################################################################


def enable_disable_devices(original_string, test_case_id, script_id, 
                           log_level="ALL", tbd=None):

    token = utils.ProcessLine(original_string)
    action = str(token[1])                                                      # Extracting the action(Enable/disable) to perform
    device_name, index = utils.extract_parameter_from_token(token, action,
                                                            "IN")               # Extracting the device name

    if "CONFIG" in device_name:                                                 # Check if token[1] is a config var and retrieve its value from config.ini
        (config, section, key) = device_name.split("-")
        device_name = utils.ReadConfig(section, key)

        if "FAIL" in device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

    device_name = str(device_name)

    try:
        if "64" in platform.uname()[4]:
            devcon = 'devcon_x64.exe'
        else:
            devcon = 'devcon.exe'

        os.chdir(lib_constants.TOOLPATH + "\\devcon")
        cmd_to_run = devcon + " findAll * > device_list.log"
        os.system(cmd_to_run)                                                   # Command to get the list of the devices available in device manager

        with open("device_list.log", "r") as f_:
            data = f_.read()
            count = data.count(device_name)

        with open("device_list.log", "r") as f__:
            data = f__.readlines()

        os.chdir(lib_constants.SCRIPTDIR)
        flag_check = False

        for device in data:                                                     # Checking whether the device to enable/disable is available in device manager or not
            if device_name.upper() in device.upper():
                device_id = '"' + device.split(":")[0].strip() + '"'
                device_idx = device_id.encode('string-escape').split("\\")		# Splitting the (\x)
                device_id = device_idx[0] + "\\" + device_idx[2] + '"'
                flag_check = True

                if flag_check is True:
                    library.write_log(lib_constants.LOG_INFO, "INFO: The %s "
                                      "is available in Device Manager"
                                      % device_name, test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: The"
                                      " %s Device is not available in Device "
                                      "Manager" % device_name, test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return False, action, device_name

                library.write_log(lib_constants.LOG_INFO, "INFO: %sing the "
                                  "%s Device" % (str(action),
                                                 str(device_name)),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                if count > 1 or device_name.upper() == \
                        "INTEL(R) MANAGEMENT ENGINE INTERFACE":
                    cmd_to_run = lib_constants.TOOLPATH + \
                        "\\devcon\\devcon_x64.exe " + action + " " + \
                        device_id + " >log1.txt"
                    os.system(cmd_to_run)                                       # Executing the command to enable/disable the given device
                    time.sleep(lib_constants.FIVE_SECONDS)
                else:
                    dev_status_flag = \
                        device_state_verification(device_name, action,
                                                  device_id, test_case_id,
                                                  script_id, log_level, tbd)    # Function call to get the Status(Enable/Disable) of a device in device manager

                    if dev_status_flag is True and action == "ENABLE":          # Checking if device is already enabled in device manager when action is Enable
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s"
                                          "Device is already Enabled"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return True, action, device_name
                    elif dev_status_flag is True and action == "DISABLE":       # Checking if device is already disabled in device manager when action is Disable
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s"
                                          "Device is already Disabled"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return True, action, device_name
                    else:
                        cmd_to_run = lib_constants.TOOLPATH + \
                            "\\devcon\\devcon_x64.exe "+ action + " " + \
                            device_id
                        os.system(cmd_to_run)                                   # Executing the command to enable/disable the given device
                        time.sleep(lib_constants.FIVE_SECONDS)

                        if "GFX" in device_name.upper() or \
                           "GRAPHIC" in device_name.upper():
                            for device in data:                                 # Checking whether the device to enable/disable is available in device manager or not
                                if "pcie".upper() in device.upper():
                                    device_id = device.split(":")[0].strip()
                                else:
                                    pass

                            os.system('netsh interface set interface '
                                      '"Ethernet 2" admin=Enable')
                            os.system('netsh interface set interface '
                                      '"Ethernet" admin=Enable')
                            time.sleep(lib_constants.TEN)

        if "INTEL(R) MANAGEMENT ENGINE INTERFACE" == device_name.upper() or \
           "USB INPUT DEVICE" == device_name.upper():
            with open("log1.txt","r") as line:
                log_line = line.readline()
                if action.upper() == "ENABLE":
                    if "Enabled" in log_line:
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s"
                                          "Device is Enabled Successfully"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return True, action, device_name
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " %s Device is not Enabled "
                                          "Successfully" % device_name,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False, action, device_name
                else:
                    if "Disabled" in log_line:
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                          "Device is Disabled Successfully"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return True, action, device_name
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          "%s Device is not Disabled "
                                          "Successfully" % device_name,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False, action, device_name
        else:
            dev_status_flag = \
                device_state_verification(device_name, action, device_id,
                                          test_case_id, script_id, log_level,
                                          tbd)                                  # Function call to get the Status(Enable/Disable) of a device in device manager
            return dev_status_flag, action, device_name
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False, action, device_name
