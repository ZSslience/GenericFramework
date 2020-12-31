__author__ = r"kapilsh/Sushil3x/tnaidux"

# General Python Imports
import csv
import os
import platform
import shutil
import subprocess
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_read_sensor_status

################################################################################
# Function Name : extract device information
# Parameters    : test_case_id, script_id, original_token, log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : to extract device information from token
################################################################################


def extract_device_information(ori_token, test_case_id, script_id,
                               log_level="ALL", tbd="None"):

    try:
        device_token = ori_token.upper()

        if "HIDDEN" in device_token:                                            # If 'hidden' is present in the token
            result = device_name_hidden(device_token, test_case_id, script_id,
                                        log_level, tbd)
        elif "UNDER" in device_token:                                           # If 'UNDER' is present in the token
            token_org = device_token.split(' ')
            parent_device_from_tc, end_pos = \
                utils.extract_parameter_from_token(token_org, "UNDER", "IN")    # Extract parameter between 'UNDER' and 'IN' in token
            child_device_from_tc, end_pos = \
                utils.extract_parameter_from_token(token_org, "VERIFY",
                                                   "UNDER")                     # Extract parameter between 'VERIFY and ''UNDER' in token

            if "CONFIG-" in parent_device_from_tc:
                parent_device_from_tc = \
                    utils.configtagvariable(parent_device_from_tc)

            if "CONFIG-" in child_device_from_tc:
                child_device_from_tc = \
                    utils.configtagvariable(child_device_from_tc)

            if parent_device_from_tc is False or child_device_from_tc is False:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: config "
                                  "does not have parent_device name",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            result = check_child_enumeration_under_parent\
                (parent_device_from_tc, child_device_from_tc, test_case_id,
                 script_id, log_level, tbd)                                     # If child device is enumerated under parent device in device manager
        elif "UNDER" not in device_token and "HIDDEN" not in device_token:      # If 'UNDER' is not present in the token
            token_org = device_token.split(' ')
            child_device_from_tc, end_pos = \
                utils.extract_parameter_from_token(token_org, "VERIFY", "IN")   # Extract parameter between 'VERIFY and 'IN' in token

            if "CONFIG-" in child_device_from_tc:                               # If 'CONFIG-' is present child device name in token
                child_device_from_tc = \
                    utils.configtagvariable(child_device_from_tc)
                if child_device_from_tc is False:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "config entry is missing for child "
                                      "device name or sensor", test_case_id,
                                      script_id, "None","None",log_level, tbd)
                    return False

            if "SENSOR" in device_token:
                device_token = ori_token.upper().split("VERIFY")[1].\
                split("IN")[0].strip()
                result = \
                    lib_read_sensor_status.read_status_from_sensor_tool\
                        (device_token,"Ready", test_case_id,script_id,
                         log_level="ALL", tbd=None)                            # Sensor Viewer Lib is called to check the sensor is listed or not
            else:
                result = library.\
                    check_child_device_enumeration(child_device_from_tc,
                                                   test_case_id, script_id,
                                                   log_level, tbd)              # If child device is enumerated in device manager
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Input token"
                              "is incorrect", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        if result:
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : device_name_hidden()
# Parameters    : original_string, test_case_id, script_id, log_level and tbd
# Return Value  : True on success, False on failure
# Functionality : Checks if device is hidden in device manager
################################################################################


def device_name_hidden(ostr, test_case_id, script_id, log_level="ALL",
                       tbd="None"):

    try:
        ostr = ostr.upper().split()                                             # Convert to list
        device,pos = utils.extract_parameter_from_token(ostr, "VERIFY", "IS")   # Extract the device name from the list
        devcon_path = utils.ReadConfig("Install_drivers", "devcon_path")        # Read devcon path from

        if "FAIL" in devcon_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for Devcon path is missing from config "
                              "file", test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        flag_device = 0
        flag_device_hidden = 0
        os.chdir(devcon_path)                                                   # Change to devcon path
        os.system(lib_constants.FIND_ALL_DEVICE_LIST_CMD)                       # Rrun on command prompt
        time.sleep(lib_constants.THREE)                                         # Wait for 3 seconds
        os.system(lib_constants.FIND_HIDDEN_DEVICE_LIST_CMD)                    # Run the second command on command prompt
        os.chdir(devcon_path)                                                   # Change to devcon path

        if os.path.exists('devices.txt') and \
           os.path.exists('devices_hidden.txt'):
            pass
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate the device list log file",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        with open("devices.txt", "r") as file:                                  # Read the first file
            for line in file:                                                   # Iterate through the lines
                if device.upper() in line.upper():                              # Check for device in each line
                    flag_device = 1                                             # Put flag to 1 and break from the loop
                    break
                else:
                    flag_device = 0

        with open("devices_hidden.txt", "r") as file:                           # Read the second file
            for line in file:                                                   # Iterate through the lines
                if device.upper() in line.upper():                              # Check for device in each line
                    flag_device_hidden = 1                                      # Put flag to 1 and break from the loop
                    break
                else:
                    flag_device_hidden = 0

        os.chdir(devcon_path)
        shutil.copy("devices.txt", lib_constants.SCRIPTDIR)
        shutil.copy("devices_hidden.txt", lib_constants.SCRIPTDIR)
        os.chdir(lib_constants.SCRIPTDIR)

        if 1 == flag_device_hidden and 0 == flag_device:                        # If not present in normal list and present in hidden list then only condition passes
            library.write_log(lib_constants.LOG_INFO, "INFO: It is verified "
                              "that %s is hidden in device manager" % device,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is not "
                              "present in the hidden device list in device "
                              "manager" % device, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : check_child_enumeration_under_parent
# Parameters    : parent_device_from_tc, child_device_from_tc, test_case_id,
#                 script_id, log_level and tbd
# Return Value  : True on success, False on failure
# Functionality : to check child is enumerated under parent in device manager
################################################################################


def check_child_enumeration_under_parent(parent_device_from_tc,
                                         child_device_from_tc, test_case_id,
                                         script_id, log_level="ALL",
                                         tbd="None"):

    try:
        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path, 'devcon')
        result_path = os.getcwd()

        if library.device_list_under_class_devmgmt("classes", log_level, tbd):  # TO get device manager Parent device list and save it in text file
            library.file_text_to_upper(devcon_path, "device_list.txt",
                                       log_level, tbd)

            devcon_file_path_upper = os.path.join(devcon_path,
                                                  'device_list_upper.txt')

            return_line_parent = \
                library.return_line_from_log(devcon_file_path_upper,
                                             parent_device_from_tc, log_level,
                                             tbd)

            if False != return_line_parent and 2 != return_line_parent:
                if parent_device_from_tc.upper() in return_line_parent:
                    req_string = \
                        return_line_parent.split(parent_device_from_tc.upper())
                    req_string = req_string[0].replace(":", "").strip()
                    if req_string == "":
                        req_string = return_line_parent.split(":")[0].strip()
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Parent Device: %s Not found in Device "
                                      "manager" % parent_device_from_tc,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                return False
        else:
            return False

        child_dev_list = \
            get_child_devices_under_parent(test_case_id, script_id, req_string,
                                           log_level, tbd)                      # TO get device manager child device list and save it in text file
        os.chdir(result_path)

        if child_dev_list:                                                      # If return value from get_child_devices_under_parent() is true
            library.file_text_to_upper(devcon_path, "child_device_list.txt",
                                       log_level, tbd)

            devcon_file_path_upper_child = \
                os.path.join(path, 'devcon\child_device_list_upper.txt')
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Child "
                              "device list command not executed ",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        os.chdir(result_path)
        return_line_child = library.\
            return_line_from_log(devcon_file_path_upper_child,
                                 child_device_from_tc, log_level, tbd)          # TO compare device manager child device list with child_device_from_tc
        os.chdir(result_path)

        if False != return_line_child and 2 != return_line_child:

            if child_device_from_tc.upper() in return_line_child:               # Check if child_device  is present in return_line1
                library.write_log(lib_constants.LOG_INFO, "INFO: Child Device:"
                                  " %s is enumerated under %s in device "
                                  "manage " % (child_device_from_tc,
                                               parent_device_from_tc),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Child "
                                  "Device: %s not found under %s in device "
                                  "manager" % (child_device_from_tc,
                                               parent_device_from_tc),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : get_child_devices_under_parent
# Parameters    : test_case_id, script_id, child_device_name, log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : generating parent list through devcon
################################################################################


def get_child_devices_under_parent(test_case_id, script_id, child_device_name,
                                   log_level="ALL", tbd="None"):

    try:
        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path, 'devcon')                              # Tool path to devcon tool
        dev_listfile = os.path.join(devcon_path, 'child_device_list.txt')       # Txt file joining with path
        os.chdir(devcon_path)

        if dev_listfile in path:                                                # Check for list file in path
            os.remove(dev_listfile)                                             # Remove the file if it exists

        if "64" in platform.uname()[4]:                                         # If platform is 64 bit
            devcon = 'devcon_x64.exe'                                           # Use devcon 64 bit exe
            devcon_cmd = os.path.join(devcon_path, devcon)                      # Join path with exe
            cmd = devcon_cmd + " find " + "=" + child_device_name + \
                " > child_device_list.txt"                                      # Run the command
        else:
            devcon = 'devcon.exe'                                               # For other platform use devcon exe
            devcon_cmd = os.path.join(devcon_path, devcon)                      # Join path and exe
            cmd = devcon_cmd + " find " + "=" + child_device_name + \
                " > child_device_list.txt"

        temp = os.system(cmd)                                                   # Run command using os.system

        if 0 == temp:
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : actionmanager_enumeration
# Parameters    : token, test_case_id, script_id, log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : To check sensors gets enumerated in Sensor Viewer
################################################################################


def actionmanager_enumeration(ori_token, test_case_id, script_id,
                              log_level="ALL", tbd=None):                       # Definition of Sensor Viewer Enumeration

    try:
        library.write_log(lib_constants.LOG_INFO, "INFO: Sensor Viewer Tool "
                          "is used instead of Action Manager", test_case_id,
                          script_id, "None", "None", log_level, tbd)

        if "SENSOR" in ori_token.upper():
            sensor_token = ori_token.split("-")[0].strip()                      # Sensor is removed from token
        else:
            sensor_token = ori_token

        flag = False
        flag_config = False

        path = utils.ReadConfig("SensorViewer", "path")                         # Path of Sensor Viewer taken from config
        configpath = utils.ReadConfig("SensorViewer", "sensor_config")

        if "FAIL" in path and "FAIL" in configpath:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Sensor"
                              "viewer tool path or xml file is missing",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        if os.path.exists(path) and os.path.exists(configpath):                 # To check the path of Sensor Viewer
            library.write_log(lib_constants.LOG_INFO, "INFO: Sensor Viewer "
                              "Path is Verified\nSensor Viewer XML File "
                              "Exists\nSensor Viewer Path: %s" % path,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Verified the  path of Sensor Viewer & continue the execution

            os.chdir(path)
            for dirname in os.listdir(path):
                if dirname.startswith("log_"):
                    shutil.rmtree(dirname)                                      # Remove old log_0 or any log_x

            time.sleep(lib_constants.TWENTY)
            command = lib_constants.ISH_COMMAND_SENSOR_VIEWER                   # Sensor Viewer Command to generate the log for sensor's
            process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       shell=True, stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out = process.communicate()[0]
            time.sleep(lib_constants.TEN_SECONDS)

            if "GLK" == tbd.upper():
                if sensor_token.upper() == "COMPASS":
                    library.write_log(lib_constants.LOG_INFO, "INFO: COMPASS "
                                      "files is with the name MAGNOMETER - "
                                      "COMPASS sensor enumeration",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    sensor_token = "MAGNOMETER"
            elif "CNL" == tbd.upper():
                if sensor_token.upper() == "COMPASS":
                    library.write_log(lib_constants.LOG_INFO, "INFO: COMPASS "
                                      "files is with the name MAGNOMETER - "
                                      "COMPASS sensor enumeration",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    sensor_token = "MAGNOMETER"
                elif sensor_token.upper() == "PROXIMITY":
                    library.write_log(lib_constants.LOG_INFO, "INFO: PROXIMITY"
                                      " files is with the name SAR - PROXIMITY"
                                      " sensor enumeration", test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    sensor_token = "SAR"
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Sensor "
                              "Viewer Path is In-correct\nSensor Viewer XML "
                              "File Doesn't Exists", test_case_id, script_id,
                              "None", "None", log_level, tbd)                   # Path of Sensor Viewer Verification failed & retun false
            return False

        for dirname in os.listdir(path):
            if dirname.startswith("log_"):
                logpath = os.path.join(path, dirname)

        if os.path.exists(logpath):                                             # To check the path of Sensor Viewer
            library.write_log(lib_constants.LOG_INFO, "INFO: Sensor Viewer "
                              "Log Path is Verified\nSensor Viewer Log Path: %s"
                              % logpath, test_case_id, script_id, "None",
                              "None", log_level, tbd)                           # Verified the  log path of Sensor Viewer & continue the execution
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Sensor "
                              "Viewer Log Path is In-correct", test_case_id,
                              script_id, "None", "None", log_level, tbd)        # Verification of log path failed
            return False

        os.chdir(logpath)
        dirlist = dircache.listdir(logpath)                                     # To get the list of file
        time.sleep(lib_constants.TWENTY)

        for i in dirlist:
            if sensor_token.upper() in i.upper():
                with open(i, 'r') as fp:
                    reader = csv.reader(fp)
                    for row in reader:
                        if row[1] != 0 and row[1] != None:
                            flag = True
                        else:
                            flag = False

        if True == flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is Listed in "
                              "Sensor Viewer" % sensor_token.upper(),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True                                                         # If sensors contains the data in log file, then verified
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is Not "
                              "Listed in Sensor Viewer" % sensor_token.upper(),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False                                                        # If sensors doesn't contains the data in log file, then not verified
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
