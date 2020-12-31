__author__ = "jkmody/sushil3x"

###########################General Imports######################################
import os
import platform
import wmi
import subprocess
import glob
import time
import dircache
import shutil
import codecs
############################Local imports#######################################
import lib_constants
import library
import utils
################################################################################
# Function Name : verify_device_attributes
# Parameters    : test_case_id, script_id, token, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to verify device attributes
################################################################################


def verify_device_attributes(token, test_case_id, script_id, loglevel="ALL",
                             tbd=None):

    try:
        token = utils.ProcessLine(token)
        property_name, index = utils.extract_parameter_from_token(token, "IF",
                                                                  "OF")         #Extracting Property name
        device_name, index = utils.extract_parameter_from_token(token, "OF",
                                                                "IS")           #Extracting Device name
        expected_value, index = utils.extract_parameter_from_token(token, "IS",
                                                                   "IN")        #Extracting Expected value

        property_name = utils.config_check(property_name, test_case_id,
                                           script_id, loglevel, tbd)            #Checking if Property name is given in config
        device_name = utils.config_check(device_name, test_case_id, script_id,
                                         loglevel, tbd)                         #Checking if Device name is given in config
        expected_value = utils.config_check(expected_value, test_case_id,
                                            script_id, loglevel, tbd)           #Checking if Expected value is given in config

        library.write_log(lib_constants.LOG_INFO, "INFO: Device Name is: %s"
        %str(device_name), test_case_id, script_id, "None", "None", loglevel,
        tbd)

        library.write_log(lib_constants.LOG_INFO, "INFO: Property Name is: %s"
        %str(property_name), test_case_id, script_id, "None", "None", loglevel,
        tbd)

        library.write_log(lib_constants.LOG_INFO, "INFO: Expected Value is: %s"
        %str(expected_value), test_case_id, script_id, "None", "None", loglevel,
        tbd)

        if False == property_name or False == device_name or \
           False == expected_value:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Provided "
            "input is not correct", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False

        if "SENSOR" in device_name.upper():                                     # Sensor is param
            devcon_path = utils.ReadConfig("Install_drivers","devcon_path")     #read devcon path from

            if "FAIL:" in devcon_path:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Devcon "
                " path entry is missing from config", test_case_id, script_id,
                "None", "None",loglevel, tbd)
                return False                                                    #Failed to get config entries returen true
            else:
                for dirname in os.listdir(devcon_path):
                    if dirname.startswith('du'):
                        os.chdir(devcon_path)
                        os.remove(dirname)                                      #Removing old dump files

                os.chdir(devcon_path)                                           #Changing the path to devecon folder
                command = lib_constants.FIND_ALL_HWIDS                          #Command to run & get HWIDS
                process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           shell=True, stdin=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                out = process.communicate()[0]
                time.sleep(lib_constants.SX_TIME)

                expected_value = expected_value.split(' ')[0].strip(' ')
                time.sleep(lib_constants.TEN_SECONDS)

                dirlist = dircache.listdir(devcon_path)                         #To get all the files in deveon path
                for file in dirlist:
                    if "dump.txt" in file.strip():                              #Below code check for Sensor viewer tag & hwids
                        with open("dump.txt", "r") as file_pointer:
                            for line in file_pointer:
                                if device_name.upper() in line.upper():
                                    for x in range(5):
                                        fp = next(file_pointer)
                                        if expected_value in fp:
                                            library.write_log\
                                            (lib_constants.LOG_INFO, "INFO: "
                                            "Driver found %s with value %s"
                                            %(device_name, expected_value),
                                            test_case_id, script_id, "None",
                                            "None", loglevel, tbd)
                                            return True

                            library.write_log(lib_constants.LOG_WARNING,
                            "WARNING: Driver not found %s with value %s"
                            %(device_name, expected_value), test_case_id,
                            script_id, "None", "None", loglevel, tbd)
                            return False

                library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable "
                "to get log files ", test_case_id, script_id, "None", "None",
                loglevel, tbd)
                return False                                                    #Unable to get the log files

        global temp_var, found
        c = wmi.WMI()                                                           #Assigning the wmi import to the variable
        query = ""                                                              #Assigning empty string to the variable
        property_value = ""

        if "PROCESSOR" == device_name:                                          #Checking if device name is processor
            query = "Select * from Win32_Processor"                             #Getting the wmi query specific to the  processor
            result = c.query(query)                                             #Wmi query output is assigned to the result
            for temp_var in result:
                property_value = library.\
                    get_property_value(temp_var, property_name, test_case_id,
                                       script_id)                               #Getting the property value

        elif "MEMORY" == device_name:                                           #Checks if the device name is 'Memory'
            query = "Select * from Win32_PhysicalMemory"                        #Wmi query specific to the memory device
            result = c.query(query)                                             #Wmi query output is assigned to the result
            if "MEMORYSIZE" == property_name or "CAPACITY" == property_name:
                property_name = "CAPACITY"
            if 1 == len(result):
                for temp_var in result:                                         #Checking for the result
                    property_value = library.\
                        get_property_value(temp_var, property_name,
                                           test_case_id, script_id)

                    if "MEMORYSIZE" == property_name or \
                       "CAPACITY" == property_name:
                        property_value = str(int(property_value)/1048576) + "mb"
            else:
                if "MEMORYSIZE" == property_name or "CAPACITY" == property_name:#Checking if the device name is 'Memory' or 'Capacity'
                    property_value = False
                    memory_read = False

                    for temp_var in result:
                        if temp_var.Description is None:                        #Checking if the value is present in the device description list
                            continue
                        property_value += int(temp_var.Capacity)
                        memory_read = True

                    if memory_read:
                        pass
                    else:
                        property_name = ""
                else:
                    for temp_var in result:
                        if temp_var.Description is None:                        #Checking if the property value is present in the device description value
                            continue
                        property_value = library.\
                            get_property_value(temp_var, property_name,
                                               test_case_id, script_id)

        elif property_name == "DRIVER VERSION":
            p = subprocess.Popen(lib_constants.DRIVER_VERSION_COMMAND,
                                 shell=False, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)           #Executing command to get the driver version
            output = p.stdout.read()
            log_file = script_id.replace(".py",".log")

            with open(log_file, "w") as f_:
                f_.write(output)                                                #Writing the driver versions in file
            f_.close()

            with open(log_file, 'r') as f1_:
                data = f1_.readlines()
            flag = False
            for i in range(len(data)):
                if device_name in data[i].upper():
                    data[i] = data[i].upper()
                    driver_ver = data[i].split(device_name)[1].strip()
                    flag = True
                    property_value = str(driver_ver)

            if flag == False:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable "
                "to get the driver version for %s"%str(device_name),
                test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
            else:
                pass

        elif "INTEL(R) SMART SOUND TECHNOLOGY (INTEL(R) SST)" == \
             device_name.upper():
            devcon_path = utils.ReadConfig("Install_drivers", "devcon_path")
            if "FAIL:" in devcon_path:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry is missing for devcon_path under Install_drivers tag",
                test_case_id, script_id, "None", "None", loglevel, tbd)

            utils.filechangedir(devcon_path)                                    #Change to devcon path

            command = lib_constants.FIND_ALL_DEVICE_LIST_CMD                    #'devcon.exe Find * > devices.txt', finds all the displayed and existing device in device manager
            cmd_exe = subprocess.Popen(command, shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE)
            time.sleep(lib_constants.FIVE_SECONDS)                              #Execute bat file in subprocess wait for 5 seconds

            if os.path.exists("devices.txt"):
                library.write_log(lib_constants.LOG_INFO, "INFO: Devcon log "
                "file found %s"%(os.path.abspath("device.txt")), test_case_id,
                script_id, "None", "None", loglevel, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Devcon "
                "log file not found", test_case_id, script_id, "None", "None",
                loglevel, tbd)
                return False

            with open("devices.txt", "r") as file_out:
                for line in file_out:
                    if expected_value in line and "OED" not in line and \
                       "AUDIO CONTROLLER" not in line and \
                       "MICROPHONE ARRAY" not in line and \
                       property_name in lib_constants.HWID_PROPERTY_NAME:
                        property_value = line.split(":")

        else:
            query = "Select * from Win32_PnPEntity"                             #Wmi query for fetching the device list
            result = c.query(query)
            device_name_split = device_name.split()

            for temp_var in result:
                if temp_var.Description is None:                                #Check for the device name
                    continue
                found = False

                for name in device_name_split:
                    if device_name.upper().strip() == \
                       temp_var.Description.upper().strip():
                        found = True                                            #Returns found = 1 if the device name is available
                    else:
                        found = False                                           #Returns found = 0 if the device name is not available
                        break
                if found:
                    break

            if found:
                if temp_var.Description is not None:
                    property_value = library.\
                        get_property_value(temp_var, property_name,
                                           test_case_id, script_id)             #Checking for the device property value is available or not

        if type(property_value) == tuple:
            property_value = property_value[0]
        elif type(property_value) == list:
            if "\\\\" in property_value:
                property_value = property_value[0].replace("\\\\", "\\")
            else:
                property_value = property_value[0]
        else:
            pass

        library.write_log(lib_constants.LOG_INFO, "INFO: Property Value is: %s"
        %str(property_value), test_case_id, script_id, "None", "None",
        loglevel, tbd)

        if "" == property_value or property_value is None:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
            "get the Property Value", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False                                                        #Returning False if unable to get property_value
        else:
            if expected_value.lower() in property_value.lower():                #Checking whether the property value is equal to expected value
                library.write_log(lib_constants.LOG_INFO, "INFO: Property Value"
                "is equal to Expected Value", test_case_id, script_id, "None",
                "None", loglevel, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Property"
                " Value is not equal to Expected Value", test_case_id,
                script_id, "None", "None", loglevel, tbd)
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", loglevel, tbd)
        return False                                                            #Returning False if some exception