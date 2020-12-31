
__author__ = 'asharanx/jkmody'

############################General Python Imports #############################
import re
import os
import winreg as winreg
import wmi
import time
from subprocess import Popen, PIPE
#########################Local Python imports###################################
import utils
import library
import lib_constants

################################################################################
# Function name   : check_Bluetooth_enumerate
# Functionality   : function to check enumerations of bluetooth and WiFi
# Parameters      : module, tc_id,script_id, log_level = "ALL", tbd = None
# Returns         : False, True
################################################################################


def check_bluetooth_enumerate(module, tc_id, script_id, log_level = "ALL",
                              tbd = None):
    try:
        device_list = wmi.WMI()                                                 # retrieving device list on the SUT
        bt_device_name=utils.ReadConfig("BLUETOOTH", "device_name")             # read config file for BT details.
        bt_dev_enum1=utils.ReadConfig("BLUETOOTH","dev_enum1")
        bt_dev_enum2=utils.ReadConfig("BLUETOOTH","dev_enum2")

        for item in [bt_device_name, bt_dev_enum1,
            bt_dev_enum2]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO:Config Tag,"
                "Variable Or Value is incorrect or missing for %s,"
                " %s, %s"%(bt_device_name, bt_dev_enum1,bt_dev_enum2),
                tc_id,script_id,"None", "None",log_level, tbd)
                return False
            else:
                pass
        bt_status_check1 = False                                                # Assigning bluetooth status to false
        bt_status_check2 = False
        wmi_output = device_list.Win32_PnPEntity()                              # wmi query to get the device list from device manager
        if 'BLUETOOTH' == module or "BT" == module:                             # checks for the string "bluetooth" is a input from test step
            bluetooth_device_present = False                                    # assigning bluetooth present status to false
            for device in wmi_output:
                if device.name== bt_device_name:                                # comparing the devices in devicemanager and the user input
                    bluetooth_device_present = True                             # assigning True to bluetooth device present if the above comparision is success
                    break
                else:
                    pass
            if bluetooth_device_present :                                       # if the blutooth device is present the checks for the bluetooth enumeration devices
                for device in wmi_output:
                    if device.name == bt_dev_enum1:                             # comparing the Bt devices from device manager
                         bt_status_check1 = True                                # assigning True if present
                    elif device.name == bt_dev_enum2:
                         bt_status_check2 = True
                    else:
                        pass
            else:
                return False                                                    # returns False if Bluetooth device is not found in the device manager
            if(True == bt_status_check1) and (True == bt_status_check2):
                return "BT_ON"                                                  # BT enumerations detected in device manager. So BT is already enabled
            else:
                return "BT_OFF"                                                 # No BT enumerations. That means BT is Disabled
        else:                                                                   # if input module name is ivalid or not supported, return false
            library.write_log(lib_constants.LOG_INFO,"INFO: BT Module not "
            "supported",tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False

################################################################################
# Function name   : check_gnss_enumerate
# Functionality   : function to check enumerations of bluetooth and WiFi
# Parameters      : module, tc_id,script_id, log_level, tbd
# Returns         : False, True
################################################################################


def check_gnss_enumerate(module, tc_id, script_id, log_level="ALL",tbd=None):
    try:
        gnss_dev_enum = utils.ReadConfig("GNSS", "device_enum")
        devcon_path = utils.ReadConfig("Update_Drivers", "devcon_path")

        for item in [gnss_dev_enum,devcon_path]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config Tag,"
                "Variable Or Value is incorrect or missing for "
                "%s,%s"%(gnss_dev_enum,devcon_path), tc_id,script_id, "None", "None", log_level, tbd)
                return False
            else:
                pass                                                            # No gnss enumerations. That means gnss is Disabled
        if 'GNSS' == module:                                                    # while using the variable wifi_device_name and wifi_dev_enum
            os.chdir(devcon_path)
            cmd = "devcon hwids =Sensor > hwids.txt"
            os.system(cmd)
            gnss_log_file_name = os.path.join(devcon_path, 'hwids.txt')
            with open(gnss_log_file_name,'r') as fread:
                read_data = fread.read()
                for line in read_data:
                    if gnss_dev_enum == line:
                        library.write_log(lib_constants.LOG_INFO, "INFO: GNSS "
                        "module detected in device manager", tc_id,script_id,
                        "None","None", log_level, tbd)
                    return True
                else:
                    pass
        else:                                                                   # if input module name is ivalid or not supported,  return false
            library.write_log(lib_constants.LOG_INFO, "INFO: GNSS Module not "
            "supported", tc_id,script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " % str(e),
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


################################################################################
# Function name   : check_wifi_enumerate
# Functionality   : function to check enumerations of bluetooth and WiFi
# Parameters      : module, tc_id,script_id, log_level, tbd
# Returns         : False, True
################################################################################


def check_wifi_enumerate(module, tc_id, script_id, log_level = "ALL",
                         tbd = None):
    try:
        device_list = wmi.WMI()                                                 # retrieving device list on the SUT  and read confif file for WiFi details. Any error while reading is checked
        wifi_dev_enum=utils.ReadConfig("WIFI","dev_enum")

        for item in [wifi_dev_enum]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO:Config Tag,"
                "Variable Or Value is incorrect or missing for "
                "Wifi",tc_id,script_id,"None", "None",log_level, tbd)
                return False
            else:
                pass                                                            # No BT enumerations. That means BT is Disabled
        if 'WIFI' == module :                                                   # while using the variable wifi_device_name and wifi_dev_enum
            for device in device_list.Win32_NetworkAdapter():                   #  wmi query to get network devices list from device manager
                if device.description == wifi_dev_enum:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Wifi module"
                " detected in device manager", tc_id,script_id,"None",
                                      "None",log_level, tbd)
                    return True
                else:
                    pass
        else:                                                                   # if input module name is ivalid or not supported,  return false
            library.write_log(lib_constants.LOG_INFO,"INFO: WIFI Module not "
            "supported",tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False


################################################################################
# Function name   : check_enumerate
# Functionality   : function to check enumerations of bluetooth and WiFi
# Parameters      : module, tc_id,script_id, log_level, tbd
# Returns         : False, True
################################################################################


def check_enumerate(module, tc_id, script_id, log_level = "ALL", tbd = None):
    try:
        if 'BLUETOOTH' == module or "BT" == module:                             # checks for the string "bluetooth" is a input from test step
            output = check_bluetooth_enumerate(module,tc_id,script_id,log_level,tbd)
            if "BT_ON" == output:
                library.write_log(lib_constants.LOG_INFO,"INFO: Bluetooth "
                "module detected in device manager", tc_id,script_id,"None",
                                  "None",log_level, tbd)
                return "BT_ON"
            elif "BT_OFF" == output:
                return "BT_OFF"                                                 # returns False if Bluetooth device is not found in the device manager
            else:
                return False

        elif 'WIFI' == module :                                                 # while using the variable wifi_device_name and wifi_dev_enum
            if check_wifi_enumerate(module, tc_id, script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,"INFO: Wifi module"
                " detected in device manager", tc_id,script_id,"None",
                                  "None",log_level, tbd)
                return True
            else:
                return  False
        elif 'GNSS' == module :
            if check_gnss_enumerate(module, tc_id, script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: GNSS module"
                " detected in device manager",tc_id, script_id, "None",
                "None", log_level, tbd)
                return True
            else:
                return  False
        else:                                                                   # if input module name is ivalid or not supported,  return false
            library.write_log(lib_constants.LOG_INFO,"INFO:Module not supported",
                 tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False

###############################################################################
# Function name   : bluetooth_toggle
# Functionality   : function to handle enable/disable of wireless modules
# Parameters      : action(enable/disable), module, tc_id,script_id,
#                  log_level, tbd
# Returns         : True/False (Boolean)
################################################################################


def bluetooth_toggle(action, module, tc_id, script_id, log_level = "ALL",
                     tbd = None):
    try:
        module_check = check_enumerate(module, tc_id, script_id,
                                                log_level, tbd)                 #Check enumeration of bluetooth module
        if (False == module_check or None == module_check):                     # Exit if BT module is not enumerated/not connected
            library.write_log(lib_constants.LOG_INFO,"INFO:No %s "
             "device on this system Or wrong config values for %s "
             "variables"%(module,module),tc_id, script_id, "None","None",
             log_level, tbd)
            return False
        else:
            pass
        if "ENABLE" == action and "BLUETOOTH" == module and \
                        "BT_ON" == module_check:                                # if the input from text file is 'Enable Bluetooth' and if module is 'ON' returns True
            return True
        elif "ENABLE" == action and "BLUETOOTH" == module and \
                        "BT_OFF" == module_check:                               # if the input is 'Enable Bluetooth' and if module is 'OFF' it calls enable_disable_toggle function
            if enable_disable_bluetooth(tc_id,script_id, log_level, tbd):
                return True                                                     # this function call will enable the BT module
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed "
                 " to enable bluetooth ",tc_id, script_id,"None",
                 "None", log_level, tbd)
                return False

        elif "DISABLE" == action and "BLUETOOTH" == module and \
                        "BT_ON" == module_check :                               # Disable BT if it's current status is enabled
            if enable_disable_bluetooth(tc_id,script_id, log_level,
                                        tbd):                                   # this function will disable the bluetooth
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed "
                 " to Disable Bluetooth",tc_id, script_id,"None",
                 "None", log_level, tbd)
                return False
        elif "DISABLE" == action and "BLUETOOTH" == module and \
                        "BT_OFF" == module_check:                               # Do nothing if BT is already disabled
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO:Module not supported",
                 tc_id, script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False

###############################################################################
# Function name   : gnss_toggle
# Functionality   : function to handle enable/disable of gnss modules
# Parameters      : action(enable/disable), module, tc_id,script_id,
#                  log_level, tbd
# Returns         : True/False (Boolean)
################################################################################


def gnss_toggle(action, module, tc_id, script_id, log_level="ALL",tbd=None):
    try:

        gnss_dev_enum = utils.ReadConfig("GNSS","device_enum")
        devcon_path = utils.ReadConfig("Update_Drivers", "devcon_path")
        for item in [gnss_dev_enum,devcon_path]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO,"INFO:Config Tag,"
                "Variable Or Value is incorrect or missing for %s,"
                " %s"%(gnss_dev_enum, devcon_path),
                tc_id,script_id,"None", "None",log_level, tbd)
                return False
            else:
                pass

        module_check = check_enumerate(module, tc_id, script_id,log_level,tbd)  # Check enumeration of bluetooth module

        if (False == module_check or None == module_check):                     # Exit if GNSS module is not enumerated/not connected
            library.write_log(lib_constants.LOG_INFO, "INFO:No %s "
            "device on this system Or wrong config values for %s "
            "variables" % (module, module), tc_id, script_id, "None", "None",
            log_level, tbd)
            return False
        else:
            pass

        if "ENABLE" == action and "GNSS" == module:
            os.chdir(devcon_path)
            cmd = lib_constants.GNSS_ENABLE
            os.system(cmd)
        elif "DISABLE" == action and "GNSS" == module:
            os.chdir(devcon_path)
            cmd = lib_constants.GNSS_DISABLE
            os.system(cmd)
        else:
            pass

        module_check = check_enumerate(module, tc_id, script_id, log_level,tbd) # Check enumeration of bluetooth module

        if module_check == True:
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "GNSS is enable", tc_id,script_id, "None", "None",log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to"
            "GNSS is not enabled", tc_id,script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s " % str(e),
        tc_id, script_id, "None", "None", log_level, tbd)
    return False
###############################################################################
# Function name   : wifi_toggle
# Functionality   : function to handle enable/disable of wireless modules
# Parameters      : action(enable/disable), module, tc_id,script_id,
#                  log_level, tbd
# Returns         : True/False (Boolean)
################################################################################


def wifi_toggle(action, module, tc_id, script_id, log_level = "ALL",tbd = None):
    try:
        if "ENABLE" == action and "WIFI" == module:                             # retrieving device list on the SUT
            os.system('netsh interface show interface > wifi_check.txt')
            with open("wifi_check.txt", "r") as f_:
                output = f_.readlines()
                flag = False
                for line in output:
                    if "Wi-Fi" in line:
                        wifi_name = re.search("Wi-Fi\s*[A-Za-z0-9]*", line)
                        wifi_name_enum = (str(wifi_name.group(0))).strip()

            command = "netsh interface set interface " + '"' + wifi_name_enum \
                      + '"' + " admin=enable"
            ret_status = utils.execute_with_command(command, tc_id, script_id,
                                                    "None", log_level, tbd)
            if ret_status.return_code != 0 and  \
                    'This network connection does not exist' in \
                    ret_status.stdout or ret_status.return_code == 0:
                os.system('netsh interface show interface > wifi_check_name.txt')
                with open("wifi_check_name.txt", "r") as f_:
                    output = f_.readlines()
                    flag = False
                    for line in output:
                        if "Wi-Fi" in line:
                            if "enabled" in line.lower():                       #checking if WI-FI is enabled or not
                                return True
                            else:
                                pass
                if False == flag:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Failed to"
                            " enable  WiFi", tc_id, script_id, "None","None",
                            log_level, tbd)
                    return False
                else:
                    pass

        elif "DISABLE" == action and "WIFI" == module:                          # Disable Wifi if it's current status is enable
            os.system('netsh interface show interface > wifi_check.txt')
            with open("wifi_check.txt","r") as f_:
                output = f_.readlines()
                flag = False
                for line in output:
                    if "Wi-Fi" in line:
                        wifi_name = re.search("Wi-Fi\s*[A-Za-z0-9]*", line)
                        wifi_name_enum = str(wifi_name.group(0))
                command = "netsh interface set interface " + '"' + \
                          wifi_name_enum + '"' + " admin=disable"
            ret_status = utils.execute_with_command(command, tc_id,
                                                    script_id, "None", log_level,
                                                    tbd)
            print(ret_status)
            if ret_status.return_code == 0:
                os.system('netsh interface show interface > wifi_check_name.txt')
                with open("wifi_check_name.txt", "r") as f_:
                    output = f_.readlines()
                    flag = False
                    for line in output:
                        if "Wi-Fi" in line:
                            if "disabled" in line.lower():                      # checking if WI-FI is disabled or not
                                return True
                            else:
                                pass
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Module "
            "not supported",tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False

###############################################################################
#Function name   : hibernate_read_registery
#Functionality   : function to read the registery value for hibernate state
#Parameters      : action(enable/disable)
#Returns         : False/Registery Value
################################################################################

def hibernate_regkey_value(registery_path, registery_name="", start_key = None):
    if isinstance(registery_path, str):
        registery_path = registery_path.split("\\")                             #Splitting the registery path
    if start_key is None:
        start_key = getattr(winreg, registery_path[0])                          #Get a named attribute from an object
        return hibernate_regkey_value(registery_path[1:],
                                      registery_name, start_key)
    else:
        subkey = registery_path.pop(0)
    with winreg.OpenKey(start_key, subkey) as handle:                           #Opening the specified key
        if registery_path:
            return hibernate_regkey_value(registery_path, registery_name, handle)
        else:
            desc, i = None, 0
            while not desc or desc[0] != registery_name:
                desc = winreg.EnumValue(handle, i)                              #Enumerating values of an open registry key
                i += 1
            return desc[1]

################################################################################
# Function name   : hibernate_toggle
# Functionality   : function to handle enable/disable of hibernate module
# Parameters      : action(enable/disable), module, tc_id, script_id,
#                   log_level, tbd
# Returns         : True/False (Boolean)
################################################################################


def hibernate_toggle(action, module, tc_id, script_id, log_level="ALL",
                     tbd=None):

    try:
        if "ENABLE" == action.upper():                                          # Enable Hibernate
            hibernate_status = get_hibernate_status(tc_id, script_id,
                                                    log_level, tbd)

            if 1 == hibernate_status:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s is %sd"
                                  % (module, action), tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Currently %s "
                                  "is not %sd, Executing command for to %s %s"
                                  "hibernate" % (module, action, action,
                                                 module), tc_id, script_id,
                                  "None", "None", log_level, tbd)

                process = Popen("powercfg.exe /Hibernate on", stdout=PIPE,
                                stderr=PIPE, shell=True)
                output = process.communicate()[0]
                returncode = int(process.returncode)

                if 0 == int(returncode):
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s %s "
                                      "command executed properly" % (action, module),
                                      tc_id, script_id, "None",
                                      "None", log_level, tbd)
                    hibernate_status = get_hibernate_status(tc_id, script_id,
                                                            log_level, tbd)
                    if 1 == hibernate_status:
                        library.write_log(lib_constants.LOG_INFO,
                                          "INFO: Hibernate is "
                                          "%sd" % action, tc_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "Failed to %s %s" % (action, module),
                                          tc_id, script_id, "None", "None",
                                          log_level, tbd)
                        return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                                      "execute command for to %s %s" % (action, module),
                                      tc_id, script_id, "None",
                                      "None", log_level, tbd)
                    return False
        elif "DISABLE" == action and "HIBERNATE" == module:                     # Disable Hibernate if it's current status is enable
            process = Popen("powercfg -h off", stdout=PIPE, stderr=PIPE,
                            stdin=PIPE)
            stdout, stderr = process.communicate()
            if len(stderr) > lib_constants.SUBPROCESS_SUCESS_VALUE:
                if lib_constants.HIBERNATE_FAILURE_CODE in stderr:
                    library.write_log(lib_constants.LOG_ERROR,"ERROR:The system "
                        "could not create the hibernation file. The specific"
                        " error code is %s"%str(lib_constants.HIBERNATE_FAILURE_CODE),
                                  tc_id,script_id, "None","None",log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Failed to"
                      " Disable Hibernate State", tc_id, script_id, "None","None",
                                  log_level, tbd)
                return False
            else:
                pass
            registry_value=hibernate_regkey_value(lib_constants.
                HIBERNATE_REGISTRY_PATH,lib_constants.HIBERNATE_REGISTRY_KEY)   #Reading the Registery value of Key HibernateEnabled
            if lib_constants.HIBERNATE_DISABLE_REGISTRY_VALUE == registry_value: # hibernate_regkey_value() function returns 0 if Hibernate is disabled
                library.write_log(lib_constants.LOG_INFO,"INFO: Registry Value "
                 "of Key HibernateEnabled is %s"%str(registry_value), tc_id,
                                  script_id, "None","None",log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to"
                 " Disable Hibernate State", tc_id, script_id, "None","None",
                                  log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Module "
            "not supported",tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False


###############################################################################
#Function name   : hyperv_toggle
#Functionality   : function to handle enable/disable of hyper-v hypervisor
#Parameters      : action(enable/disable), module, tc_id,script_id,
#                  log_level, tbd
#Returns         : True/False (Boolean)
################################################################################
def hyperv_toggle(action, module, test_case_id, script_id, log_level, tbd):
    try:
        hyper_v_cmd = ""
        if "ENABLE" == action and "HYPER-V HYPERVISOR" == module:                     # Enable Hype-V module if it's current status is disable
            hyper_v_cmd = lib_constants.HYPER_V_ENABLE_CMD
        elif "DISABLE" == action and "HYPER-V HYPERVISOR" == module:
            hyper_v_cmd = lib_constants.HYPER_V_DISABLE_CMD
        os.chdir(lib_constants.SYSTEM_PATH)                                     # change directory to windows/system32 path
        process = Popen(hyper_v_cmd, stdout=PIPE, stderr=PIPE)                  # running hyper v command in subprocess and getting output
        stdout, stderr = process.communicate()
        if len(stderr) > 0:                                                     # if any error occurs in command run for hyper-v enable or disable
            library.write_log(lib_constants.LOG_INFO, "INFO: Unable to "
            "run the hyper-v command",test_case_id,script_id, "None", "None",
                              log_level, tbd)                                   #Write the error to the log
            return False
        else:
            if lib_constants.HYPER_V_OUTPUT_STATUS \
                in stdout and lib_constants.HYPER_V_OUTPUT in stdout:           # if command for Hyper-v enable or disable successfully ran
                library.write_log(lib_constants.LOG_INFO,"INFO: %s module"
                "got %s successfully "%(module,action), test_case_id, script_id,
                "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to"
                " %s the %s module"%(action,module), test_case_id, script_id, "None","None",
                log_level, tbd)
                return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occurred "
        "due to %s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
        return False

###############################################################################
#Function name   : module_toggle
#Functionality   : function to handle enable/disable of wireless modules
#Parameters      : action(enable/disable), module, tc_id,script_id,
#                  log_level, tbd
#Returns         : True/False (Boolean)
################################################################################

def module_toggle(action, module, tc_id, script_id, log_level = "ALL",
                  tbd = None):
    try:
        if "BLUETOOTH" == module:                                               # if module connected is Bluetooth
            if bluetooth_toggle(action,module,tc_id,script_id,log_level,tbd):   # calls the function Bluetooth_toggle to enable/disable the module based on the test input
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed "
                 " to toggle bluetooth module",tc_id, script_id,"None",
                 "None", log_level, tbd)
                return False                                                    # fails if unsucess to toggle the bluetooth module
        elif "WIFI" == module:                                                  # if module connected is wifi
            if wifi_toggle(action, module, tc_id, script_id, log_level, tbd):   # calls the function wifi_toggle to enable/disable the module based on the test input
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed "
                 " to toggle wifi module",tc_id, script_id,"None",
                 "None", log_level, tbd)
                return False                                                    # fails if unsucess to toggle the wifi module
        elif "GNSS" == module:
            if gnss_toggle(action, module, tc_id, script_id, log_level,
                           tbd):                                                # calls the function wifi_toggle to enable/disable the module based on the test input
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed "
                " to toggle gnss module",tc_id, script_id, "None",
                "None", log_level, tbd)
                return False
        elif "HYPER-V HYPERVISOR" == module:                                             # if module to be toggled is hibernate
            if hyperv_toggle(action, module, tc_id, script_id, log_level, tbd): # calls the function hyperv_toggle to enable/disable the hype-v module based on the test input
                library.write_log(lib_constants.LOG_INFO, "INFO: Hyper-v"
                " hypervisor module toggled successfully",tc_id, script_id,
                 "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed "
                 " to toggle hyper-v hypervisor module",tc_id, script_id,
                 "None", "None", log_level, tbd)
                return False
        elif "HIBERNATE" == module:                                             # if module to be toggled is hibernate
            if hibernate_toggle(action, module, tc_id, script_id, log_level, tbd): # calls the function hibernate_toggle to enable/disable the module based on the test input
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed "
                 " to toggle Hibernate State",tc_id, script_id,"None",
                 "None", log_level, tbd)
                return False                                                    # fails if unsucess to toggle the wifi module
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO:Module not supported",
                 tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False

################################################################################
#Function name   : enable_disable_bluetooth
#Functionality   : function to handle enable/disable bluetooth
#Parameters      : tc_id,script_id, log_level, tbd
#Returns         : True/False (Boolean)
################################################################################
def enable_disable_bluetooth(tc_id, script_id, log_level = "ALL", tbd = None):
    try:
        bt_cmd_path = utils.ReadConfig('ENABLEDISABLE','BLUETOOTH')             #Read the path of bluetooth app from config file
        if "FAIL:" in bt_cmd_path:
            library.write_log(lib_constants.LOG_INFO,"INFO:Config Tag,"
        "Variable Or Value is incorrect or missing for Bluetooth.exe file",
        tc_id,script_id,"None", "None",log_level, tbd)
            return False
        else:
            pass
        if  "Bluetooth.exe" in bt_cmd_path:                                     #If exe path not updated in config file, return False
            cmd_status = os.system(bt_cmd_path)
            if False == cmd_status:                                             #Returns 0 if command is executed successfully
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Bluetooth "     #Return False if Bluetooth tool missing or fails to run
                "tool may not be present or incorrect config name for BLUETOOTH",
                tc_id, script_id,"None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING,"WARNING: Config Tag,"
             " Variable Or Value for BLUETOOTH is incorrect or missing",
             tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s "%str(e),
         tc_id,script_id,"None","None",log_level,tbd)
        return False


def get_hibernate_status(tc_id, script_id, log_level="ALL", tbd=None):

    """
    Function Name     : get_hibernate_status
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : Reads the Hibernated Enabled variable from windows
                        registry path
    Return Value      : 0/1 on successful performing action, False on failure
    """

    try:
        hibernate_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                       lib_constants.HIBERNATE_REGISTRY_PATH)   # Open corresponding windows registry path with local machine key
        status = winreg.QueryValueEx(hibernate_key,
                                     lib_constants.HIBERNATE_REGISTRY_KEY)      # Checking the status of 'HibernateEnabled' status in Path

        library.write_log(lib_constants.LOG_INFO, "INFO: Querying windows "
                          "registry for Hibernate status", tc_id, script_id,
                          "None", "None", log_level, tbd)

        if status:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s status is "
                              "obtained from query"
                              % lib_constants.HIBERNATE_REGISTRY_KEY, tc_id,
                              script_id, "None", "None", log_level, tbd)
            return status[0]
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Windows "
                              "registry hibernate query failed", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
