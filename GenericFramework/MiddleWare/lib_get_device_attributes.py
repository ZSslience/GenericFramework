__author__ = "jkmody"

##########################General Python Imports ###############################
import os
import subprocess
import wmi
import codecs
############################ Local Imports #####################################
import lib_constants
import library
import utils
################################################################################
# Function Name : get_device_name
# Parameters    : token, loglevel, tbd
# Return Value  : returns the device name
# Purpose       : Extract device name from token
################################################################################


def get_device_name(token, loglevel="ALL", tbd="None"):

    token_list = token.split(" ")                                               #Converting to list to perform extraction operation
    dev_name, end_pos = library.\
        extract_parameter_from_token(token_list, "OF", "FROM", loglevel, tbd)   #Gets the device name from the original token on stripping the mandatory token
    return dev_name                                                             #Returns the token with only device name

################################################################################
# Function Name  : get_property_name
# Parameters     : token, loglevel, tbd
# Return Value   : returns the device property name
# Purpose        : Extract property name from token
################################################################################


def get_property_name(token, loglevel="ALL", tbd="None"):

    token_list = token.split(" ")                                               #Converting to list to perform extraction operation
    dev_property, end_pos = library.\
        extract_parameter_from_token(token_list, "GET", "OF")                   #Gets the device property name from the original token on stripping the mandatory token
    token = dev_property                                                        #Assigning the property name to the token
    return token                                                                #Returns the token with device property name

################################################################################
# Function Name : get_device_attribute
# Parameters    : test_case_id, script_id, token, loglevel, tbd
# Return Value  : returns the device attribute name
# Purpose       : Get device attribute
################################################################################


def get_device_attribute(test_case_id, script_id, token, loglevel="ALL",
                         tbd=None):

    try:
        global x, found
        c = wmi.WMI()                                                           #Assigning the wmi import to the variable
        property_name = get_property_name(token)                                #Assigning the property name to the variable
        property_name = library.parse_variable(property_name, test_case_id,
                                               script_id)                       #Gets the property name from the variable list
        device_name = get_device_name(token)                                    #Assigning the device name to the variable
        if "CONFIG-ME-DRIVER" == device_name:                                   #Assigning the device name to the variable
            device_name = "CONFIG-ME-DRIVER"
        else:
            device_name = library.parse_variable(device_name, test_case_id,
                                                 script_id)                     #Gets the device name from the variable list

        query = ""                                                              #Assigning empty string to the variable
        property_value = ""

        if "PROCESSOR" in device_name:                                          #Checks if device name is processor
            query = "Select * from Win32_Processor"                             #Gets the wmi query specific to the  processor
            result = c.query(query)                                             #Wmi query output is assigned to the result
            for x in result:
                property_value = library.\
                    get_property_value(x, property_name, test_case_id,
                                       script_id)                               #Gets the property value

        elif "MEMORY" == device_name or "PHYSICALMEMORY" == device_name:        #Checks if the device name is 'Memory'
            query = "Select * from Win32_PhysicalMemory"                        #Wmi query specific to the memory device
            result = c.query(query)                                             #Wmi query output is assigned to the result
            if "CAPACITY" == property_name or "MEMORYSIZE" == property_name:
                property_name = "CAPACITY"
            elif "SPEED" == property_name or "MEMORYFREQUENCY" == property_name:
                property_name = "SPEED"
            else:
                pass

            if 1 == len(result):
                for x in result:                                                #Checks for the result
                    property_value = library.\
                        get_property_value(x, property_name, test_case_id,
                                           script_id)
                    if "CAPACITY" == property_name:
                        property_value = str(int(property_value)/1048576) + \
                                         " MB"
                    if "SPEED" == property_name:
                        property_value = str(property_value) + " MHz"
                    else:
                        pass
                    return True, property_value                                 #Returns the property value

            else:
                if "MEMORYSIZE" == property_name or "CAPACITY" == property_name:#Checks if the device name is 'Memory' or 'Capacity'
                    property_value = False
                    memory_read = False
                    for x in result:
                        if x.Description is None:                               #Checks if the value is present in the device description list
                            continue
                        property_value += int(x.Capacity)
                        memory_read = True
                    if memory_read:
                        pass
                    else:
                        property_name = ""
                else:
                    for x in result:
                        if x.Description is None:                               #Checks if the propert value is present in the device description value
                            continue
                        property_value = library.\
                            get_property_value(x, property_name, test_case_id,
                                               script_id)

        elif property_name == "DRIVER VERSION":
            if "CONFIG-ME-DRIVER" == device_name:
                logfile = script_id.split(".")[0] + "_driver_details.txt"       #Assigning a name for the log
                me_hwid = utils.ReadConfig("Install_Drivers", "me_hwid")        #Get hwid from config file
                devcon_path = utils.ReadConfig("Install_Drivers",
                                               "devcon_path")                   #Read devcon path from config file
                if "FAIL:" in [devcon_path, me_hwid]:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                    "Failed to the config entry for devcon_path & me_hwid",
                    test_case_id, script_id, "None", "None", loglevel, tbd)     #Write log message if config entry is missing
                    return False

                os.chdir(devcon_path)
                driver_output = os.system("devcon_x64.exe drivernodes" + " " +
                                          '"' + me_hwid + '"' + ' > ' + logfile)#Executes the command to get the driver details and stores in log file in toolpath
                flag = False
                with open(logfile, "r") as f:
                    driver_ver = ""                                             #Opens the log from toolpath and reads
                    for line in f:
                        if "Driver version" in line:
                            driver_ver = line.split()[-1]                       #Get the driver version from log file
                            flag = True
                        else:
                            pass
                if flag:
                    return True, driver_ver
                else:
                    return False, 0

            else:
                cmd = '''powershell.exe Get-WmiObject Win32_PnPSignedDriver| \
                select devicename, driverversion'''
                p = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)                    #Executing Command to clear the event viwer logs
                output = p.stdout.read()
                log_file = script_id.replace(".py", ".log")
                with open(log_file, "w") as f_:
                    f_.write(output)                                            #Writing the events which are cleared from event viewer logs
                f_.close()
                with open(log_file, 'r') as f1_:
                    data = f1_.readlines()
                flag = False
                for i in range(len(data)):
                    if device_name in data[i]:
                        driver_ver = data[i].split(device_name)[1].strip()
                        flag = True
                        return True, str(driver_ver)
                if flag == False:
                    return False, 0
                else:
                    pass

        elif 'SERIAL IO I2C HOST CONTROLLER' in device_name.upper() or\
                'SERIAL IO SPI HOST CONTROLLER' in device_name.upper():
            if 'SERIAL IO I2C HOST CONTROLLER' in device_name.upper()\
                    or 'SERIAL IO SPI HOST CONTROLLER' in\
                    device_name.upper() and 'HARDWAREIDS' in property_name:
                logfile = script_id.replace(".py", ".log")
                logpath = lib_constants.SCRIPTDIR + os.sep + logfile
                cmd = "devcon.exe findall * > " + logpath
                os.chdir(lib_constants.DEVCON_PATH)
                device_list = utils.execute_with_command(cmd, test_case_id,
                                                         script_id, "None",
                                                         loglevel, tbd,
                                                         shell_status=True)
                if device_list.return_code == 0:
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: Log generated for getting the"
                                      " Hardware ID's for the devices in"
                                      " device manager", test_case_id,
                                      script_id, "None", "None", loglevel, tbd)
                    logpath = logpath.decode('iso-8859-1')
                    with codecs.open(logpath, 'r') as file:
                        for line in file :
                            if device_name in line:
                                hardware_id = line.split(':')[0].split('\\')
                                hardware_id = os.path.join(hardware_id[0],
                                                           hardware_id[1])
                                return True, str(hardware_id.lower())

            else:
                driver_hid = ''
                cmd = 'powershell.exe Get-WmiObject Win32_PnPSignedDriver|' \
                      'select devicename, driverversion'
                p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, stdin=subprocess.PIPE)        # Executing Command to get Driver info
                output = p.stdout.read()
                log_file=script_id.replace(".py", ".log")
                with open(log_file, "w") as f_:
                    f_.write(output)                                            #Writing the Driver info in log
                f_.close()
                with open(log_file, 'r') as f1_:
                    data = f1_.readlines()
                flag = False
                for i in range(len(data)):
                    if "SERIAL IO I2C HOST".lower() in data[i].strip().lower():
                        driver_hid = data[i].split()[-2]
                        flag = True
                        return True, str(driver_hid)
                if flag == False:
                    return False, 0
                else:
                    pass

        else:
            query = "Select * from Win32_PnPEntity"                             #Wmi query for fetching the device list
            result = c.query(query)
            device_name_split = device_name.split()

            for x in result:
                if x.Description is None:                                       #Checks for the device name in
                    continue
                found = False
                for name in device_name_split:
                    if device_name.upper().strip() in \
                            x.Description.upper().strip():
                        found = True                                            #Returns found = 1 if the device name is available
                    else:
                        found = False                                           #Returns found = 0 if the device name is not available
                        break
                if found:
                    break

            if found:
                if x.Description is not None:
                    property_value = library.\
                        get_property_value(x, property_name, test_case_id,
                                           script_id)                           #Checks for the device property value is available in the

        if property_name == "HARDWAREID" or property_name == "HARDWARE ID" and \
           type(property_value) == tuple:                                       #Capture all the hardware ids in the tuple
            hid = ''
            for item in property_value:
                hid = hid + ' ' + str(item)
            property_value = hid
        elif type(property_value) == tuple:
            property_value = property_value[0]
        if "" == property_value or property_value is None:
            return False, 0                                                     #Return False and 0 as value
        else:
            if "MEMORYSIZE" == property_name or "CAPACITY" == property_name:
                property_value = int(property_value/1048576)
                property_value = repr(property_value) + " MB"
            elif "SPEED" == property_name:
                property_value = property_value + " MHz"
            elif "NUMBEROFENABLEDCORE" == property_name:
                property_value = str(property_value) + "Core(s)"                #Appending Core(s) with property value
            elif "NUMBEROFLOGICALPROCESSORS" == property_name:
                property_value = str(property_value) + "Thread(s)"              #Appending Thread(s) with property value
            else:
                pass
            return True, property_value                                         #Return True and the new found value

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Issue observed due "
        "to %s"%e, test_case_id, script_id)
        return False, 0
