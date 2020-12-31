__author__ = r"dal/tnaidux/kashokax/sushil/surabh1x"

# General Python Imports
import codecs
import csv
import logging
import os
import re
import serial
import subprocess
import sys
import time
import datetime
import win32com
import wmi
import win32com.client

# Local Python Imports
import lib_constants
import lib_run_command
import lib_set_bios
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations
import utils
sys.path.append(lib_constants.XMLCLI_TOOLPATH)
import pysvtools.xmlcli.XmlCli as cli
import KBM_Emulation as kbm

################################################################################
# Function Name : RebootTheSystem
# Parameters    : none
# Functionality : Performs G3 followed by power button press
# Return Value  : True/False
################################################################################


def g3_reboot_system(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        dc_signal_port = utils.ReadConfig("TTK", "dc_signal_port")
        dc_power_port = utils.ReadConfig("TTK", "dc_power_port")
        typec_port = utils.ReadConfig("TTK", "typec_power_port")

        if "FAIL:" in [dc_signal_port, dc_power_port, typec_port]:
            write_log(lib_constants.LOG_WARNING, "WARNING: failed to get "
                      "config entry for dc_signal_port, dc_power_port, "
                      "typec_port", test_case_id, script_id, "None", "None",
                      log_level, tbd)
            return False

        # lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)
        ttk_device = lib_ttk2_operations.gpio_initialize(test_case_id, script_id, log_level, tbd)
        result = lib_ttk2_operations.\
            perform_g3_reboot(dc_signal_port, dc_power_port, typec_port,
                              test_case_id, script_id, log_level, tbd)

        if result:
            return True
        else:
            return False
    except Exception as e:
        return False

################################################################################
# Function Name : sendKeys
# Parameters    : key to be pressed
# Return Value  : True/False
# Functionality : sending key strokes required to the SUT
################################################################################


def sendkeys(key, test_case_id, script_id, loglevel="ALL", tbd = None):

    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini
        if "FAIL:" in port or "FAIL:" in input_device_name:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                                                 "com port details or "
                                                 "input device name from "
                                                 "Config.ini ", "None", "None",
                      "None", "None", loglevel, tbd)                            # Failed to get info from config file
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: COM Port and input "
                                              "device name is identified as "
                                              "is identified as %s and %s from "
                                              "config.ini"
                      % (port, input_device_name), "None", "None", "None",
                      "None", loglevel, tbd)
        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        for num in range(1, 140):                                               # it sends the 'F2'keys in the range(1,80) times
            k1.key_press(key)                                                   # Sending F2 keys to go to Bios page
            time.sleep(0.2)                                                     # Sending key strokes to load Bios
        time.sleep(5)
        if "F2" == key or "f2" == key:
            k1.key_type("Y")                                                    #Sending Y key to bios page
        else:
            pass
        return True
    except Exception as e:
        return False

################################################################################
# Function Name : sendKeys_times
# Parameters    : key to be pressed n times
# Return Value  : True/False
# Functionality : sending key strokes required to the SUT
################################################################################


def sendkeys_times(key, times, loglevel="ALL", tbd = None):

    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini
        if "FAIL:" in port or "FAIL:" in input_device_name:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                                                 "com port details or "
                                                 "input device name from "
                                                 "Config.ini ", "None", "None",
                      "None", "None", loglevel, tbd)                            # Failed to get info from config file
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: COM Port and input "
                                              "device name is identified as "
                                              "is identified as %s %s from "
                                              "config.ini"
                      % (port, input_device_name), "None", "None", "None",
                      "None", loglevel, tbd)
        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        for num in range(1,times):                                              # it sends the 'F2'keys in the range(1,80) times
            k1.key_press(key)                                                   # Sending F2 keys to go to Bios page
            time.sleep(0.2)                                                     # Sending key strokes to load Bios
        time.sleep(5)
        if "F2" == key or "f2" == key:
            k1.key_type("Y")
        else:
            pass
        return True
    except Exception as e:
        return False

################################################################################
# Function name : set_multiple_bootorder()
# Parameters    : test_case_id, script_id, log_level and tbd
# Return Value  : True on successful action, False otherwise
# Functionality : Setting bootorder in bios for 1 or multiple bootable options
################################################################################


def set_multiple_bootorder(test_case_id, script_id, log_level="ALL", tbd=None):         # Function to set the boot order for 1 or n devices in order

    xml_cli_log_mesg = lib_constants.XML_CLI_LOG_MESG

    try:
        bootorder = ''
        bootorder1 = ''
        edk_number = ''
        xml_cli_log_path = lib_constants.XML_CLI_LOG_PATH

        if os.path.exists(xml_cli_log_path):
            os.remove(xml_cli_log_path)

        cli.clb._setCliAccess("winhwa")

        try:
            cli.GetBootOrder()
        except:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                      "current boot order", test_case_id, script_id, "None", "None",
                      log_level, tbd)
            return False

        with open(xml_cli_log_path, "r") as bootlog:
            for line in bootlog:
                if "The Current Boot Order" in line:
                    bootorder = line.split(":")[1].strip()
                elif "internal edk shell" in line.lower() or \
                     "internal efi shell" in line.lower() or \
                     "efi internal shell" in line.lower() or \
                     "internal uefi shell" in line.lower():
                    edk_number = line.split()[0].strip()
                    break

        if bootorder.startswith(edk_number + "-"):
            write_log(lib_constants.LOG_INFO, "INFO: Bootorder already set to "
                      "EDK Shell", test_case_id, script_id, "None", "None", log_level,
                      tbd)
            return True
        else:
            bootorder = bootorder.replace("-" + edk_number, "")
            bootorder = edk_number + "-" + bootorder

        try:
            cli.SetBootOrder(bootorder)
            with open(xml_cli_log_path, 'r') as file_des:
                for line in file_des:
                    if xml_cli_log_mesg == line.strip():
                        flag_xml_cli_mesg = True
                        break

            if flag_xml_cli_mesg is True:
                write_log(lib_constants.LOG_INFO, "INFO: Boot order "
                          "successfully set to %s" % bootorder1, test_case_id,
                          script_id, "None", "None", log_level, tbd)
                return True
            else:
                return False
        except:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set Boot "
                      "Order", test_case_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s " % e, test_case_id,
                  script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : extract_parameter_from_token
# Parameters    : token[entire grammar token list],start_token,end_token
# Return Value  : returns the parameter as single variable
# Purpose       : to get the parameter from the grammar
################################################################################


def extract_parameter_from_token(token, start_token, end_token, loglevel="ALL",
                                 tbd = None):

    str = ""
    start_pos = 0                                                               # Declaring empty string
    end_pos = 0

    for i in range(len(token)):                                                 # looping to identify within the length of token
        if token[i] == start_token:                                             # assigning start token to one value
            start_pos = i+1                                                     # incrementing the token
        else:
            pass
        if end_token != "":                                                     # checking if the end token is not empty
            if token[i] == end_token:                                           # checking the value of token assigned is equal as end token
                end_pos = i
        else:
            end_pos = len(token)
    for val in range(start_pos, end_pos):                                       # checking for range of start and end value
        str = str + " " + token[val]                                            # appending the string
    return str.strip(' '), end_pos                                              # returns the value


def setup_logger(test_case_id):
    cwd = lib_constants.SCRIPTDIR
    log_dir = cwd + "\log"

    if not (os.path.exists(log_dir)):
        os.mkdir(log_dir)

    log_file_name = test_case_id + ".log"
    file_handle = log_dir + "\\" + log_file_name
    logging.basicConfig(level=logging.DEBUG,
                        filename=file_handle,
                        format='%(lineno)d  %(module)s %(asctime)s %(name)-6s \
                        %(levelname)-6s %(message)-s ',
                        datefmt='%y-%m-%d %H:%M:%S',
                        )

################################################################################
# Function Name : write_log
# Parameters    : level, msg, test_case_id, script_id, toolname, info_fetched
#                 loglevel, tdb2
# Functionality : writes output messages to log file and console based on input
# Return Value  : None
################################################################################


def write_log(level, msg, test_case_id="None", script_id="None",
              toolname="None", info_fetched="None", loglevel="ALL",
              tbd="None"):

    loglevel = str(loglevel)
    tbd = str(tbd)                                                              # If any object is passed as tool name, etc, it may result in exception. to avoid it

    if loglevel == "ALL":
        loglevel = "012345"

    if "None" != test_case_id and "None" != script_id:
        logstring = "TC_ID:" + test_case_id + " SCRIPT_NAME: " + \
            script_id + " " + msg
    else:
        logstring = msg

    time_format = "%Y-%m-%d %H:%M:%S"
    time_now = datetime.datetime.now().strftime(time_format)
    logstring = time_now + " " + logstring

    if 1 == level and "1" in loglevel:                                          # If-else to check log level is x and is enabled
        print("INFO: " + logstring)
        logging.info(logstring)
    elif 0 == level and "0" in loglevel:
        logstring = logstring + " TOOL_USED: " + toolname + " TOOL_LOG:" + \
            str(info_fetched)
        print("DEBUG: " + logstring)
        logging.debug(logstring)
    elif 2 == level and "2" in loglevel:
        logstring = logstring + " TOOL_USED: " + toolname + " TOOL_LOG:" + \
            str(info_fetched)
        print("WARNING: " + logstring)
        logging.warning(logstring)
    elif 3 == level and "3" in loglevel:
        logstring = logstring + " TOOL_USED: " + toolname + " TOOL_LOG:" + \
            str(info_fetched)
        print("ERROR: " + logstring)
        logging.error(logstring)
    elif 4 == level and "4" in loglevel:
        logstring = logstring + " TOOL_USED: " + toolname + " TOOL_LOG:" + \
            str(info_fetched)
        print("PASS: " + logstring)
        logging.info(logstring)
    elif 5 == level and "5" in loglevel:
        logstring = logstring + " TOOL_USED: " + toolname + " TOOL_LOG:" + \
            str(info_fetched)
        print("FAIL: " + logstring)
        logging.error(logstring)


class KBClass():
                                                                                #KBClass will automatically open a serial communication on the port number of brainbox passed as an argument
    keySet = {                                                                  # These are the list of keys which can be sent through serial communication
    'Backspace': r'\x08',
    'Tab': r'\x09',
    'Enter': r'\x0D',
    'Esc': r'\x1B',
    'Space': r'\x20',
    '!': r'\x21',
    '"': r'\x22',
    '#': r'\x23',
    '$': r'\x24',
    '%': r'\x25',
    '&': r'\x26',
    '(': r'\x28',
    ')': r'\x29',
    '*': r'\x2A',
    '+': r'\x2B',
    ',': r'\x2C',
    '-': r'\x2D',
    '.': r'\x2E',
    '/': r'\x2F',
    '0': r'\x30',
    '1': r'\x31',
    '2': r'\x32',
    '3': r'\x33',
    '4': r'\x34',
    '5': r'\x35',
    '6': r'\x36',
    '7': r'\x37',
    '8': r'\x38',
    '9': r'\x39',
    ':': r'\x3A',
    ';': r'\x3B',
    '<': r'\x3C',
    '=': r'\x3D',
    '>': r'\x3E',
    '?': r'\x3F',
    '@': r'\x40',
    'A': r'\x41',
    'B': r'\x42',
    'C': r'\x43',
    'D': r'\x44',
    'E': r'\x45',
    'F': r'\x46',
    'G': r'\x47',
    'H': r'\x48',
    'I': r'\x49',
    'J': r'\x4A',
    'K': r'\x4B',
    'L': r'\x4C',
    'M': r'\x4D',
    'N': r'\x4E',
    'O': r'\x4F',
    'P': r'\x50',
    'Q': r'\x51',
    'R': r'\x52',
    'S': r'\x53',
    'T': r'\x54',
    'U': r'\x55',
    'V': r'\x56',
    'W': r'\x57',
    'X': r'\x58',
    'Y': r'\x59',
    'Z': r'\x5A',
    '[': r'\x5B',
    ']': r'\x5D',
    '^': r'\x5E',
    '_': r'\x5F',
    "'": r'\x60',
    'a': r'\x61',
    'b': r'\x62',
    'c': r'\x63',
    'd': r'\x64',
    'e': r'\x65',
    'f': r'\x66',
    'g': r'\x67',
    'h': r'\x68',
    'i': r'\x69',
    'j': r'\x6A',
    'k': r'\x6B',
    'l': r'\x6C',
    'm': r'\x6D',
    'n': r'\x6E',
    'o': r'\x6F',
    'p': r'\x70',
    'q': r'\x71',
    'r': r'\x72',
    's': r'\x73',
    't': r'\x74',
    'u': r'\x75',
    'v': r'\x76',
    'w': r'\x77',
    'x': r'\x78',
    'y': r'\x79',
    'z': r'\x7A',
    '{': r'\x7B',
    '|': r'\x7C',
    '}': r'\x7D',
    '~': r'\x7E',
    'F1': r'\xA0',
    'F2': r'\xA1',
    'F3': r'\xA2',
    'F4': r'\xA3',
    'F5': r'\xA4',
    'F6': r'\xA5',
    'F7': r'\xA6',
    'F8': r'\xA7',
    'F9': r'\xA8',
    'F10': r'\xA9',
    'F11': r'\xAA',
    'F12': r'\xAB',
    'Num_lock': r'\xB0',
    'Caps_lock': r'\xB1',
    'Scroll_lock': r'\xB2',
    'num_enter': r'\xC0',
    'num_/': r'\xC1',
    'num_*': r'\xC2',
    'num_9': r'\xC3',
    'num_8': r'\xC4',
    'num_7': r'\xC5',
    'num_6': r'\xC6',
    'num_5': r'\xC7',
    'num_4': r'\xC8',
    'num_3': r'\xC9',
    'num_2': r'\xCA',
    'num_1': r'\xCB',
    'num_0': r'\xCC',
    'num_-': r'\xCD',
    'num_+': r'\xCE',
    'num_.': r'\xCF',
    'Insert': r'\xD0',
    'Home': r'\xD1',
    'End': r'\xD2',
    'Page_down': r'\xD4',
    'Up_arrow': r'\xD5',
    'Down_arrow': r'\xD6',
    'Left_arrow': r'\xD7',
    'Right_arrow': r'\xD8',
    'Print_screen': r'\xD9',
    'Pause_break': r'\xDA',
    'Del': r'\xDB',
    '`': r'\x27',
    r"\'": r'\x5C'}

    makeKeysList = {
    'Win': r'\x88',
    'Ctrl': r'\x81',
    'Alt': r'\x83',
    'Shift': r'\x82'
    }

    breakKeysList = {
    'Win': r'\x98',
    'Ctrl': r'\x91',
    'Alt': r'\x93',
    'Shift': r'\x92'
    }

################################################################################
# Function Name : __init__
# Parameters    : port [Port number of the Brainbox used]
# Return Value  : None
# Purpose       : function is automatically called when object is created.
#                 opens serial communication channel on the given port
################################################################################


def __init__(self, port, baudrate=9600, timeout=1, loglevel="ALL", tbd=None):

    try:
        comPort = self.comPortNum(port)                                         # declaring the com port of brainbox
        self.port = serial.Serial(comPort, baudrate=baudrate, timeout=timeout)  # declaring the speed of characters to be sent
        time.sleep(2)
        self.port._isOpen = True                                                # checking for any open port
        self.port.flushInput()                                                  # assignes the input to the port
        self.port.flushOutput()                                                 # assigns output to the port
    except Exception as msg:
        raise serial.SerialException("could not open port %s: %s" % (port,
                                                                     msg))      # exception on error

################################################################################
# Function Name : close
# Parameters    : None
# Return Value  : None
# Purpose       : closes serial communication channel on the opened port
################################################################################


def close(self, loglevel="ALL", tbd=None):

    try:
        self.port.close()                                                       # closing the port which is opened for serial communicatiom
    except serial.SerialException as msg:                                       # sends exception on error in closing the port
        pass

    self.port._isOpen = False

################################################################################
# Function Name : comPortNum
# Parameters    : portNum [port number used on Brainbox device]
# Return Value  : returns the mapped COM port
# Purpose       : gets the COM port mapped to the given port number of the
#                 BrainBox
################################################################################


def comPortNum(self, portNum, loglevel="ALL", tbd=None):

    i = 0
    comPort = 0                                                                 # assigning value to comport
    comList = []                                                                # declaring empty list
    query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE \
        '%Brainboxes%' AND Name LIKE '%COM%)'"                                  # Wni query to fetch the com and port of the brain box connected
    coms = wmi.WMI().query(query)                                               # calling wmi query
    for com in coms:
        comBrac = com.name
        comPort = comBrac[comBrac.index("(") + 1:comBrac.rindex(")")]           # getting the comport index
        comPort = int(comPort.lstrip('COM'))                                    # stripping the com from the value returned
        comList.append(comPort)                                                 # appending the com port to the empty list declared
    comList.sort()                                                              # sorting the list
    portNum = int(portNum) - 1                                                  # Fetching the number
    return comList[portNum] - 1

################################################################################
# Function Name : longString
# Parameters    : stringArg [string for sending over Serial COM port]
# Return Value  : None
# Purpose       : sends the text send as an argument over serial com without
#                 processing for special keys
################################################################################


def longString(self, stringArg,loglevel="ALL", tbd=None):

    for char in stringArg:
        self.port.flushInput()                                                  # converts the characters to long string
        self.port.write(char)
        time.sleep(0.1)

################################################################################
# Function Name : whiteKeys
# Parameters    : stringArg [Takes single key which doesn't print any
#                 character ex F1 to F12, Esc, Home, Arrows, Enter.
#                 Anything that is processed as Special charactors etc.]
# Return Value  : None
# Purpose       : sends single key whitekey
################################################################################


def whiteKeys(self, stringArg, loglevel="ALL", tbd=None):
    char = self.keySet[stringArg]                                               # writes only the spl keys
    self.writeX(char)
    time.sleep(0.1)

################################################################################
# Function Name : sendWithEnter
# Parameters    : stringArg [Takes single key which doesn't print any character
#                 ex F1 to F12, Esc, Home, Arrows, Enter.
#                 Anything that is processed as Special characters etc.]
# Return Value  : None
# Purpose       : send given text and simulate enter after the text
################################################################################


def sendWithEnter(self, stringArg, loglevel="ALL", tbd=None):
    self.longString(stringArg)                                                  # Taking the long string of the SPl keys which is single key
    time.sleep(0.3)
    self.whiteKeys("Enter")                                                     # Sends the key follwed with enter key

################################################################################
# Function Name : writeX
# Parameters    : str [Takes single key to be send to the keyboard \
#                 controller over serial cable]
# Return Value  : None
# Purpose       : Takes single key to be send to the keyboard controller
#                 over serial cable.
################################################################################


def writeX(self, str, loglevel="ALL", tbd=None):
    self.port.flushInput()                                                      # from the port connected to brainbox it will sends the keys pressed
    char = str.decode("string-escape")                                          # Decodes the string
    self.port.write(char)                                                       # writes the string
    time.sleep(0.5)

################################################################################
# Function Name : makeKeys()
# Parameters    : str [Takes single key to be send to the keyboard controller
#                 over serial cable]
# Return Value  : None
# Purpose       : press the key sent
################################################################################


def makeKeys(self, str, loglevel="ALL", tbd=None):
    char = self.makeKeysList[str]                                               # It will press the key
    self.writeX(char)
    time.sleep(1)

################################################################################
# Function Name : breakKeys
# Parameters    : str [Takes single key to be send to the keyboard controller \
#                 over serial cable]
# Return Value  : None
# Purpose       : reveals the key pressed.
################################################################################


def breakKeys(self, str, loglevel="ALL", tbd=None):
    char = self.breakKeysList[str]                                              # releaves the key pressed
    self.writeX(char)
    time.sleep(0.2)

################################################################################
# Function Name : combiKeys
# Parameters    : str [Takes combination of keys like Win+R, SHIFT+F10 or\
#                 CTRL+ALT+DEL in the string format]
# Return Value  : None
# Purpose       : send key combinations in order and uses other \
#                 functions like write, whiteKeys
################################################################################


def combiKeys(self, str, loglevel="ALL", tbd=None):
    listK = str.split('+')                                                      # it will split the keys with "+" when combination of 2 or more keys are given
    breakList = []                                                              # creating a empty list for appending the keys
    if listK:
        for spe in listK:                                                       # For loop for checking the special keys
            if spe in self.makeKeysList:
                self.makeKeys(spe)
                breakList.append(spe)                                           # Appending the keys into empty list assigned if the keys exist
            else:
                self.whiteKeys(spe)                                             # Calling for white keys
        for bspe in breakList:
            self.breakKeys(bspe)

################################################################################
# Function Name : verify_yellow_bangs
# Parameters    : tc_id, script_id, tbd1, tbd
# Return Value  : returns True if any devices with yellow bang is found
#                 and False otherwise
# Purpose       : to check for devices with yellow bangs in device manager
################################################################################


def verify_yellow_bangs(tc_id, script_id, log_level="ALL", tbd=None):

    c = wmi.WMI()
    count = 0

    for device in c.Win32_PnPEntity():                                          # for all device manager entries, loop and do following

        if 0 != device.ConfigManagerErrorCode:                                  #device manager error code for all working devices will be zero
            count = count + 1

            if device.Name != None:                                             #if device name is known, log that to file, or unknown
                write_log(lib_constants.LOG_WARNING, "WARNING: Device manager "
                          "shows yellow bang for '%s'. Error code: %s"
                          % (device.Name, device.ConfigManagerErrorCode),
                          tc_id, script_id, "None", "None", log_level, tbd)
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Device manager "
                          "shows yellow bang for 'Unknown Device'. Error "
                          "code:%s" % device.ConfigManagerErrorCode, tc_id,
                          script_id, "None", "None", log_level, tbd)
        else:
            pass

    if count > 0:
        return True
    else:
        return False

################################################################################
# Function Name : getTTKdeviceId()
# Parameters    : aServer
# Return Value  : device index
# Purpose       : When multiple TTK devices connected to host, this function
#                 will check the device ID based on the TTK id from the config
################################################################################


def getTTKdeviceId(aServer):
    DeviceID = utils.ReadConfig("TTK", "DeviceId")
    if "FAIL: " in DeviceID or "NA" in DeviceID:
        x = 0
    else:
        for x in range(len(aServer.getDevices())):
            DeviceConnectedToTTKServer = aServer.getDevices()[x].deviceName
            if DeviceConnectedToTTKServer.lower() == DeviceID.lower():
                break
    return x

################################################################################
# Function Name : initialize_ttk()
# Parameters    : loglevel, tbd
# Return Value  : aDevice handle to the current device
# Purpose       : Initialize TTK device connected to SUT
################################################################################


def initialize_ttk(loglevel="ALL", tbd = None):
    import pyttk                                                                #importing default ttk library
    try:
        aServer = pyttk.Server('localhost')                                     #Invoking ttk server
        x = getTTKdeviceId(aServer)
        aDevice = aServer.getDevices()[x]                                       #Invoking ttk server using index values
        return aDevice

    except Exception as e:
        if "list index out of range" in e.lower():                              #Checking for exception
            os.system("sc stop TTKserver")                                      #stopping the TTK server service
            os.system("sc start TTKserver")                                     #Starting the ttk server service
            time.sleep(lib_constants.FIVE_SECONDS)
            aServer = pyttk.Server('localhost')                                 #Invoking ttk server
            x = getTTKdeviceId()
            aDevice = aServer.getDevices()[x]                                   #Invoking ttk server using index values
            return aDevice
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Exception in "
                      "initializing TTK due to %s" % e, loglevel, tbd)

################################################################################
# Function Name : ttk_set_relay()
# Parameters    : action = ON/OFF relay =relay number for the connected device
# Return Value  : 0 for Pass,1 for Fail
# Purpose       : setGPIO() library in pyttk module used to turn on/off devices
################################################################################


def ttk_set_relay(action, relay, tc_id, script_id, loglevel="ALL", tbd = None):

    try:
        import lib_ttk2_operations
        result = lib_ttk2_operations.ttk2_set_relay(action, relay, tc_id,
                                                    script_id, loglevel, tbd)

        if result:
            ttk2_pin_status = 0
            return ttk2_pin_status
        else:
            ttk2_pin_status = 1
            return ttk2_pin_status

    except Exception as e:
        write_log(lib_constants.LOG_WARNING, "WARNING: Exception due to: %s" % e,
                  tc_id, script_id, "TTK2", loglevel, tbd)
        return False


################################################################################
# Function Name : ac_power()
# Parameters    : action = ON/OFF
# Return Value  : True for successful ac power action else False
# Purpose       : acon() or acoff() commands invoked to switch AC sources
################################################################################


def ac_power(action, tc_id, script_id, loglevel="ALL", tbd=None):
    try:
        import lib_ttk2_operations
        lib_ttk2_operations.kill_ttk2(tc_id, script_id, loglevel, tbd)
        time.sleep(10)
        result = lib_ttk2_operations.ac_on_off(action,
                                               lib_constants.TTK2_SWITCH_NO_AC,
                                               tc_id, script_id, loglevel, tbd)
        if result is not None:
            return result
        else:
            return False
    except Exception as e:
        write_log(lib_constants.LOG_WARNING, "WARNING: Exception due to: %s" %e,
                  tc_id, script_id, "TTK2", loglevel, tbd)
        return False


################################################################################
# Function Name : change_power_settings
# Parameters    : command, tc_id, script_id, tbd1, tbd
# Return Value  : returns True on successfully changing power option and False
#                 otherwise
# Purpose       : to change power options
###############################################################################


def change_power_settings(command, tc_id, script_id, loglevel="ALL", tbd=None):
                                                                                #Execute any powercfg commands#command(list): command except powercfg
    command.insert(0, "powercfg")
    pwr = subprocess.Popen(command, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    my_cmd = "".join(command)
    if pwr.returncode:                                                          #based in the powercfg command return value, return True/False
        return False
    else:
        return True

###############################################################################
# Function Name : set_button_action
# Parameters    : tc_id, script_id, sx_state, source, tbd1, tbd
# Return Value  : returns True on successfully changing power option and False
#                 otherwise
# Purpose       : to change power options
###############################################################################


def set_button_action(tc_id, script_id, sx_state, source, log_level="ALL",
                      tbd=None):

    if "PWR_BTN" == source:                                                     #change power button actio as follows

        if "S3" == sx_state or "DEEPS3" == sx_state or "CS" == sx_state or \
           "CONNECTED-MOS" == sx_state or "DISCONNECTED-MOS" == sx_state or \
           "CMOS" == sx_state or "DMOS" == sx_state or "S0I3" == sx_state or "CMS" == sx_state:      #change action to sleep for sx state= s3/cs/DeepS3

            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "1"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "1"]                                         #change power options for both ac and dc

            if "KBL" == tbd.upper() or "KBLR" == tbd.upper():
                powershell_path = utils.ReadConfig("WIN_POWERSHELL","Path")     # reading config entry
                new_script_id = script_id.strip(".py")
                log_file = new_script_id + '.txt'
                script_dir = lib_constants.SCRIPTDIR
                log_path = script_dir + "\\" + log_file

                write_log(lib_constants.LOG_INFO, "INFO: Running power shell "
                          "file to allow magic packets", tc_id, script_id,
                          "None", "None", log_level, tbd)

                cmd = lib_constants.WOL_SETTING_CMD                             # power shell query file content
                os.chdir(powershell_path)                                       # Changing directory to power shell
                result_ps = lib_run_command.\
                    powershell_script(cmd, tc_id, script_id, loglevel="ALL",
                                      tbd=None)                                 # function to create power shell query file

                if True == result_ps:
                    write_log(lib_constants.LOG_INFO, "INFO: Power shell file "
                              "created", tc_id, script_id, "None", "None",
                              log_level, tbd)

                    shell_script = 'psquery.ps1'                                # shell script should be placed in script directory
                    exe_path = os.path.join(lib_constants.SCRIPTDIR,
                                            shell_script)
                    final_command = 'powershell.exe ' + exe_path + ' > ' + \
                                    log_path                                    # concat the commands along with the log path
                    os.chdir(powershell_path)
                    os.system(final_command)                                    # run power shell file present in script folder
                    command = lib_constants.WOL_SETTING_S3_S4                   # get command from lib_constant file
                    os.system(command)                                          # run this command to enable hibernate mode
                    os.chdir(script_dir)
                    count = 0

                    if os.path.exists(log_path):                                # checking log file path
                        write_log(lib_constants.LOG_INFO, "INFO: log path is "
                                  "verified", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                        with open(log_path, 'r') as fp:                         # reading log file content
                            read_data = fp.readlines()
                            for line in read_data:
                                if "Enable" in line:
                                    count += 1
                            if count == 3:
                                write_log(lib_constants.LOG_INFO, "INFO: "
                                          "Mandatory Setting is completed for "
                                          "WOL S3 & log is verified", tc_id,
                                          script_id, "None", "None", log_level,
                                          tbd)                                  # checking log file if all the options are enabled
                            else:
                                write_log(lib_constants.LOG_WARNING,
                                          "WARNING: Mandatory Setting is not "
                                          "completed for WOL S3 & log is not "
                                          "verified", tc_id, script_id, "None",
                                          "None", log_level, tbd)
                                return False                                    # Return False if log is not verified and setting is not set
                else:
                    write_log(lib_constants.LOG_WARNING, "WARNING: Power shell"
                              " file not created for WOL S3 & Log file is not"
                              " created", tc_id, script_id, "None", "None",
                              log_level, tbd)
                    return False
            else:
                pass

            if change_power_settings(ac, tc_id, script_id, log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change power options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Power button action "
                          "has been set to S3", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "power button action to S3", tc_id, script_id,
                          "None", "None", log_level, tbd)
                return False

        elif "S4" == sx_state or "DEEPS4" == sx_state:                          #change action to hibernate
            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "2"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "2"]

            if "KBL" == tbd.upper() or "KBLR" == tbd.upper():
                powershell_path = utils.ReadConfig("WIN_POWERSHELL", "Path")    # reading config entry
                new_script_id = script_id.strip(".py")
                log_file = new_script_id + '.txt'
                script_dir = lib_constants.SCRIPTDIR
                log_path = script_dir + "\\" + log_file

                write_log(lib_constants.LOG_INFO, "INFO: Running power shell "
                          "file to allow magic packets", tc_id, script_id,
                          "None", "None", log_level, tbd)

                cmd = lib_constants.WOL_SETTING_CMD                             # power shell query file content
                os.chdir(powershell_path)                                       # Changing directory to power shell
                result_ps = lib_run_command.\
                    powershell_script(cmd, tc_id, script_id, loglevel="ALL",
                                      tbd=None)                                 # function to create power shell query file

                if True == result_ps:
                    write_log(lib_constants.LOG_INFO, "INFO: Power shell file "
                              "created", tc_id, script_id, "None", "None",
                              log_level, tbd)
                    shell_script = 'psquery.ps1'                                # shell script should be placed in script directory
                    exe_path = os.path.join(lib_constants.SCRIPTDIR,
                                            shell_script)
                    final_command = 'powershell.exe ' + exe_path + ' > ' + \
                                    log_path                                    # concat the commands along with the log path
                    os.chdir(powershell_path)
                    os.system(final_command)                                    # run power shell file present in script folder
                    command = lib_constants.WOL_SETTING_S3_S4                   # get command from lib_constant file
                    os.system(command)                                          # run this command to enable hibernate mode
                    os.chdir(script_dir)
                    count = 0

                    if os.path.exists(log_path):                                # checking log file path
                        write_log(lib_constants.LOG_INFO, "INFO: log path is "
                                  "verified", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                        with open(log_path, 'r') as fp:                         # reading log file content
                            read_data = fp.readlines()
                            for line in read_data:
                                if "Enable" in line:
                                    count += 1
                            if count == 3:
                                write_log(lib_constants.LOG_INFO, "INFO: " 
                                          "Mandatory Setting is completed for"
                                          " WOL S4 & log is verified", tc_id,
                                          script_id, "None", "None", log_level,
                                          tbd)                                  # checking log file if all the options are enabled
                            else:
                                write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Mandatory Setting is not completed"
                                          " for WOL S4 & log is not verified",
                                          tc_id, script_id, "None", "None",
                                          log_level, tbd)
                                return False                                    # Return False if log is not verified and setting is not set
                else:
                    write_log(lib_constants.LOG_WARNING, "WARNING: Power shell"
                              " file not created for WOL S4 & Log file is not "
                              "created", tc_id, script_id, "None", "None",
                              log_level, tbd)
                    return False
            else:
                pass

            if change_power_settings(ac, tc_id, script_id, log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change power options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Power button action "
                          "has been set to S4", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "power button action to S4", tc_id, script_id,
                          "None", "None", log_level, tbd)
                return False

        elif "S5" == sx_state or "DEEPS5" == sx_state:                          #change action to shutdown
            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "3"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "PBUTTONACTION", "3"]

            if "KBL" == tbd.upper() or "KBLR" == tbd.upper():
                powershell_path = utils.ReadConfig("WIN_POWERSHELL", "Path")    # reading config entry
                new_script_id = script_id.strip(".py")
                log_file = new_script_id + '.txt'
                script_dir = lib_constants.SCRIPTDIR
                log_path = script_dir + "\\" + log_file

                write_log(lib_constants.LOG_INFO, "INFO: Running power shell "
                          "file to allow magic packets", tc_id, script_id,
                          "None", "None", log_level, tbd)

                cmd = lib_constants.WOL_SETTING_CMD                             # power shell query file content
                os.chdir(powershell_path)                                       # Changing directory to power shell
                result_ps = lib_run_command.\
                    powershell_script(cmd, tc_id, script_id, loglevel="ALL",
                                      tbd=None)                                 # function to create power shell query file

                if True == result_ps:
                    write_log(lib_constants.LOG_INFO, "INFO: Power shell file "
                              "created", tc_id, script_id, "None", "None",
                              log_level, tbd)
                    shell_script = 'psquery.ps1'                                # shell script should be placed in script directory
                    exe_path = os.path.join(lib_constants.SCRIPTDIR,
                                            shell_script)
                    final_command = 'powershell.exe ' + exe_path + ' > ' + \
                                    log_path                                    # concat the commands along with the log path
                    os.chdir(powershell_path)
                    os.system(final_command)                                    # run power shell file present in script folder
                    command = lib_constants.WOL_SETTING_S3_S4                   # get command from lib_constant file
                    os.system(command)                                          # run this command to enable hibernate mode
                    os.chdir(script_dir)
                    count = 0
                    if os.path.exists(log_path):                                # checking log file path
                        write_log(lib_constants.LOG_INFO, "INFO: log path is "
                                  "verified", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                        with open(log_path, 'r') as fp:                         # reading log file content
                            read_data = fp.readlines()
                            for line in read_data:
                                if "Enable" in line:
                                    count += 1
                            if count == 3:
                                write_log(lib_constants.LOG_INFO, "INFO: "
                                          "Mandatory Setting is completed for"
                                          " WOL S5 & log is verified", tc_id,
                                          script_id, "None", "None", log_level,
                                          tbd)                                  # checking log file if all the options are enabled
                            else:
                                write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Mandatory Setting is not completed"
                                          " for WOL S5 & log is not verified",
                                          tc_id, script_id, "None", "None",
                                          log_level, tbd)
                                return False                                    # Return False if log is not verified and setting is not set
                else:
                    write_log(lib_constants.LOG_WARNING, "WARNING: Power shell"
                              " file not created for WOL S5 & Log file is not"
                              " created", tc_id, script_id, "None", "None",
                              log_level, tbd)
                    return False
            else:
                pass

            if change_power_settings(ac, tc_id, script_id, log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change power options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Power button action "
                          "has been set to S5", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "power button action to S5", tc_id, script_id,
                          "None", "None", log_level, tbd)
                return False
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Invalid parameter "
                      "for sx state", tc_id, script_id, "None", "None",
                      log_level, tbd)
            return False

    elif "LID_ACTION" == source:
        if "S3" == sx_state or "CS" == sx_state or "CONNECTED-MOS" == sx_state \
           or "DISCONNECTED-MOS" == sx_state or "CMOS" == sx_state or \
           "DMOS" == sx_state:                                                  #change action to sleep
            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "1"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "1"]

            if change_power_settings(ac, tc_id, script_id,log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change lid options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Lid switch action set"
                          " to S3", tc_id, script_id, "None", "None",
                          log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "lid action to S3 state", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return False
        elif "S4" == sx_state:                                                  #change action to hibernate
            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "2"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "2"]

            if change_power_settings(ac, tc_id, script_id, log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change power options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Lid switch action set"
                          " to S4 state", tc_id, script_id, "None", "None",
                          log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "lid action to S4 state", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return False
        elif "S5" == sx_state:                                                  #change action to shutdown
            ac = ["/SETACVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "3"]
            dc = ["/SETDCVALUEINDEX", "SCHEME_BALANCED", "SUB_BUTTONS",
                  "LIDACTION", "3"]

            if change_power_settings(ac, tc_id, script_id, log_level, tbd) and \
               change_power_settings(dc, tc_id, script_id, log_level, tbd):     #change power options for both ac and dc
                write_log(lib_constants.LOG_INFO, "INFO: Lid switch action set"
                          " to S5 state", tc_id, script_id, "None", "None",
                          log_level, tbd)
                return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set "
                          "lid action to S5 state", tc_id, script_id, "None",
                          "None", log_level, tbd)
                return False
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Invalid parameter "
                      "for sx state", tc_id, script_id, "None", "None",
                      log_level, tbd)
            return False
    else:
        write_log(lib_constants.LOG_WARNING, "WARNING: Invalid parameter for "
                  "sx source", tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : parse_variable
# Parameters    : token, test_case_id, script_id
# Functionality : This function takes token as input to be parsed, identifies
#                 if the token starts with Config or Step
# Return Value  : it retrieves the mapped values from Config.ini or
#                 Result.ini. Else, send backs the token as it is
################################################################################


def parse_variable(token, test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        if re.search("Config*", token, re.IGNORECASE):                          # Gets the config tag from the original token
            configvalue = utils.configtagvariable(token)                        # Gets the section and tag value from the config using this config tag function

            if configvalue:
                return configvalue
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Unable to read "
                          "value from Config.ini", test_case_id, script_id,
                          "None", "None", loglevel, tbd)                        # Writes the error output to the log when unable to read the config value
                return False
        elif re.search("Step+", token, re.IGNORECASE):                          # Checks for the tag step in the original step
            stepnum = None

            try:
                stepnum = token.split()[1]                                      # Splits the step in the original step
            except:
                write_log(lib_constants.LOG_WARNING, "WARNING: Step number "
                          "token is not proper", test_case_id, script_id,
                          "None", "None", loglevel, tbd)                        # Writes the error log to the file if the step number is not properly given
                return False

            stepvalue = utils.read_from_Resultfile(stepnum)

            if stepvalue:
                return stepvalue
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Unable to read "
                          "value from Results.ini", test_case_id, script_id,
                          "None", "None", loglevel, tbd)
                return False                                                    # Returns false if unable to read the value from the result
        else:
            return token                                                        # Returns the token if step and the number is found proper
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : get_property_value()
# Parameters    : object,property_name,test_case_id,Script_id
# Functionality : this function returns the device property value from \
#                 the device manager which are applicable and available
# Return Value  : returns the device property value
################################################################################


def get_property_value(object, property_name, test_case_id, Script_id):
    try:
        if property_name == "AVAILABILITY":                                     # checks if device manager property name is '"AVAILABILITY"'
            return object.Availability                                          # returns the object
        elif property_name == "CPUNAME":
            return object.Name
        elif property_name == "CAPTION":
            return object.Caption
        elif property_name == "CLASSGUID":
            return object.ClassGuid
        elif property_name == "COMPATIBLEID" or \
                property_name == "COMPATIBLE ID" or \
                property_name == "COMPATIBLE IDS":
            return object.CompatibleID[0]
        elif property_name == "CONFIGMANAGERERRORCODE":
            return object.ConfigManagerErrorCode
        elif property_name == "CONFIGMANAGERUSERCONFIG":
            return object.ConfigManagerUserConfig
        elif property_name == "CREATIONCLASSNAME":
            return object.CreationClassName
        elif property_name == "DESCRIPTION" or \
                property_name == "DEVICE DESCRIPTION":
            return object.Description
        elif property_name == "DEVICEID":
            return object.DeviceID
        elif property_name == "ERRORCLEARED":
            return object.ErrorCleared
        elif property_name == "ERRORDESCRIPTION":
            return object.ErrorDescription
        elif property_name == "HARDWAREID" or \
                property_name == "HARDWARE ID" or \
                "HARDWARE IDS" == property_name.strip():
            return object.HardwareID
        elif property_name == "INSTALLDATE":
            return object.InstallDate
        elif property_name == "LASTERRORCODE":
            return object.LastErrorCode
        elif property_name == "MANUFACTURER":
            return object.Manufacturer
        elif property_name == "NAME":
            return object.Name
        elif property_name == "PNPCLASS":
            return object.PNPClass
        elif property_name == "PNPDEVICEID":
            return object.PNPDeviceID
        elif property_name == "POWERMANAGEMENTCAPABILITIES":
            return object.PowerManagementCapabilities[0]
        elif property_name == "POWERMANAGEMENTSUPPORTED":
            return object.PowerManagementSupported
        elif property_name == "PRESENT":
            return object.Present
        elif property_name == "SERVICE":
            return object.Service
        elif property_name == "STATUS":
            return object.Status
        elif property_name == "STATUSINFO":
            return object.StatusInfo
        elif property_name == "SYSTEMCREATIONCLASSNAME":
            return object.SystemCreationClassName
        elif property_name == "SYSTEMNAME":
            return object.SystemName
        elif property_name == "ADDRESSWIDTH":
            return object.AddressWidth
        elif property_name == "ARCHITECTURE":
            return object.Architecture
        elif property_name == "ASSETTAG":
            return object.AssetTag
        elif property_name == "AVAILABILITY":
            return object.Availability
        elif property_name == "CHARACTERISTICS":
            return object.Characteristics
        elif property_name == "CPUSTATUS":
            return object.CpuStatus
        elif property_name == "CURRENTCLOCKSPEED":
            return object.CurrentClockSpeed
        elif property_name == "CURRENTVOLTAGE":
            return object.CurrentVoltage
        elif property_name == "DATAWIDTH":
            return object.DataWidth
        elif property_name == "EXTCLOCK":
            return object.ExtClock
        elif property_name == "FAMILY":
            return object.Family
        elif property_name == "L2CACHESIZE":
            return object.L2CacheSize
        elif property_name == "L2CACHESPEED":
            return object.L2CacheSpeed
        elif property_name == "L3CACHESIZE":
            return object.L3CacheSize
        elif property_name == "L3CACHESPEED":
            return object.L3CacheSpeed
        elif property_name == "LEVEL":
            return object.Level
        elif property_name == "LOADPERCENTAGE":
            return object.LoadPercentage
        elif property_name == "MAXCLOCKSPEED":
            return str(object.MaxClockSpeed) + " MHz"
        elif property_name == "NUMBEROFCORES":
            return object.NumberOfCores
        elif property_name == "NUMBEROFENABLEDCORE":
            return object.NumberOfEnabledCore
        elif property_name == "NUMBEROFLOGICALPROCESSORS":
            return object.NumberOfLogicalProcessors
        elif property_name == "OTHERFAMILYDESCRIPTION":
            return object.OtherFamilyDescription
        elif property_name == "PARTNUMBER":
            return object.PartNumber
        elif property_name == "PROCESSORID":
            return object.ProcessorId
        elif property_name == "PROCESSORTYPE":
            return object.ProcessorType
        elif property_name == "REVISION":
            return object.Revision
        elif property_name == "ROLE":
            return object.Role
        elif property_name == "SECONDLEVELADDRESSTRANSLATIONEXTENSIONS":
            return object.SecondLevelAddressTranslationExtensions
        elif property_name == "SERIALNUMBER":
            return object.SerialNumber
        elif property_name == "SOCKETDESIGNATION":
            return object.SocketDesignation
        elif property_name == "STEPPING":
            return object.Stepping
        elif property_name == "THREADCOUNT":
            return object.ThreadCount
        elif property_name == "UNIQUEID":
            return object.UniqueId
        elif property_name == "UPGRADEMETHOD":
            return object.UpgradeMethod
        elif property_name == "VERSION":
            return object.Version
        elif property_name == "VIRTUALIZATIONFIRMWAREENABLED":
            return object.VirtualizationFirmwareEnabled
        elif property_name == "VMMONITORMODEEXTENSIONS":
            return object.VMMonitorModeExtensions
        elif property_name == "VOLTAGECAPS":
            return object.VoltageCaps
        elif property_name == "ATTRIBUTES":
            return object.Attributes
        elif property_name == "BANKLABEL":
            return object.BankLabel
        elif property_name == "CAPACITY":
            return object.Capacity
        elif property_name == "CONFIGUREDCLOCKSPEED":
            return object.ConfiguredClockSpeed
        elif property_name == "CONFIGUREDVOLTAGE":
            return object.ConfiguredVoltage
        elif property_name == "DEVICELOCATOR":
            return object.DeviceLocator
        elif property_name == "FORMFACTOR":
            return object.FormFactor
        elif property_name == "HOTSWAPPABLE":
            return object.HotSwappable
        elif property_name == "INTERLEAVEDATADEPTH":
            return object.InterleaveDataDepth
        elif property_name == "INTERLEAVEPOSITION":
            return object.InterleavePosition
        elif property_name == "MAXVOLTAGE":
            return object.MaxVoltage
        elif property_name == "MEMORYTYPE":
            return object.MemoryType
        elif property_name == "MINVOLTAGE":
            return object.MinVoltage
        elif property_name == "MODEL":
            return object.Model
        elif property_name == "OTHERIDENTIFYINGINFO":
            return object.OtherIdentifyingInfo
        elif property_name == "POSITIONINROW":
            return object.PositionInRow
        elif property_name == "POWEREDON":
            return object.PoweredOn
        elif property_name == "REMOVABLE":
            return object.Removable
        elif property_name == "REPLACEABLE":
            return object.Replaceable
        elif property_name == "SKU":
            return object.SKU
        elif property_name == "SMBIOSMEMORYTYPE":
            return object.SMBIOSMemoryType
        elif property_name == "SPEED":
            return object.Speed
        elif property_name == "TAG":
            return object.Tag
        elif property_name == "TOTALWIDTH":
            return object.TotalWidth
        elif property_name == "TYPEDETAIL":
            return object.TypeDetail
        else:
            return None                                                         # returns None if not device found
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, Script_id)
        return None

################################################################################


def Syscope_Specifications(TC_id, script_id):

    """
    function name   : Syscope_Specifications.
    Description     : Returns True if Syscope installed Successful,
                      Returns False if not.
    Parameters      : TC_id:test_case_id; script_id:script_id.
    returns         : True/False.
    """

    import lib_constants
    from lib_toolInstallation import SystemScope

    obj = SystemScope()
    path1 = utils.ReadConfig("Systemscope", "Tooldir")
    Exe_name = utils.ReadConfig("Systemscope", "Exe_name ")
    path = path1 + "\\" + Exe_name

    if os.path.exists(path):
        return True
    else:
        if obj.install_Syscope():
            write_log(lib_constants.LOG_INFO, "INFO: Systemscope Tool "
                      "Installed Successfully", TC_id, script_id)
            return True
        else:
            write_log(lib_constants.LOG_ERROR, "ERROR: Fail to Install "
                      "Systemscope Tool", TC_id, script_id)
            return False

################################################################################


def Syscope_Log(TC_id, script_id):

    """
    function name   : Syscope_Log.
    Description     : To generate the syscope log file
    Parameters      : TC_id:test_case_id; script_id:script_id.
    returns         : True/False.
    """

    import lib_constants

    if Syscope_Specifications(TC_id, script_id):
        write_log(lib_constants.LOG_INFO, "INFO: SystemScope is Installed.",
                  TC_id, script_id)
    else:
        write_log(lib_constants.LOG_ERROR, "FAIL: SystemScope is NOT "
                  "installed,please install the Tool.", TC_id, script_id)
        return False

    path1 = utils.ReadConfig("Systemscope", "Tooldir")
    path = path1
    exe = utils.ReadConfig("Systemscope", "Exe_name")
    os.chdir(path)
    command = path + "\\" + exe + " -log Syscope.csv"
    subprocess.check_output(command)
    time.sleep(15)

    if os.path.exists(path + "\\" + "Syscope.csv"):
        write_log(lib_constants.LOG_INFO, "INFO: SystemScope Log generated "
                  "Successfully.", TC_id, script_id)
        return True
    else:
        write_log(lib_constants.LOG_ERROR, "FAIL: SystemScope Log not "
                  "generated.", TC_id, script_id)
        return False

################################################################################
# Function name      : lib_step_read_bios
# Description        : Read Step no. result value
# Parameters         : string_inbios
# Returns            : return step_inbios,step_value,Flag
# Dependent Function : lib_read_bios(string_inbios, TC_id, Script_id, ost,
#                                    cur_dir, Flag)
################################################################################


def lib_step_read_bios(string_inbios, log_level, tbd=None):

    if "step " in string_inbios.lower():
        string_inbios = string_inbios.lower()
        step_inbios = string_inbios.split("=")[1].strip()
        step_no = step_inbios.split("step")[1].strip()
        step_value = utils.read_from_Resultfile(step_no)
        type_val = type(step_value)

        try:
            if "'d" in step_value.lower():
                step_value = step_value.replace("'d", "")
                step_value = str(int(float(step_value)))
            elif "'h" in step_value.lower():
                step_value = step_value.replace("'h", "")
                step_value = str(int(step_value, 16))
            elif "'b" in step_value.lower():
                step_value = step_value.replace("'b", "")
                step_value = str(int(step_value, 2))
            else:
                try:
                    step_value = str(int(float(step_value)))
                except:
                    pass
            Flag = "True"
        except ValueError:
            pass
            Flag = "False"
        return step_inbios,step_value,Flag
    else:
        step_inbios = ''
        step_value = ''
        Flag = False
        return step_inbios, step_value, Flag

################################################################################
# Function    : get_bootorder()
# Parameter   : test_case_id, script_id, loglevel and tbd
# Description :	This function gives boot.txt / XmlCli.log in which booting
#               devices list is available
# Return      :	Returns log file if Successful, False otherwise
################################################################################


def get_bootorder(test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        tool_path = utils.ReadConfig("XML_CLI", "TOOL_PATH")                    #Extracting tool_path from the config file
        if "FAIL:" in tool_path:
            write_log(lib_constants.LOG_WARNING, "WARNING: Config entry"
                      " for tool_path is missing under [xml_cli] tag",
                      test_case_id, script_id, "None", "None", loglevel, tbd)   #Writing the warning message to the log file
            return False

        xml_cli_log_path = lib_constants.XML_CLI_LOG_PATH
        if os.path.exists(xml_cli_log_path):
            os.remove(xml_cli_log_path)                                         #Removing the log file if it exists in the path

        cli.clb._setCliAccess("winhwa")
        
        try:
            cli.GetBootOrder()                                                  #Getting the boot order list using the xmlcli tool
            return xml_cli_log_path                                             #Returns Log file
        except Exception as e:
            write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                      test_case_id, script_id, "None", "None", loglevel, tbd)   #Writing exception message to the lo file
            return False
        
    except Exception as e:
        write_log(lib_constants.LOG_WARNING, "WARNING: Exception due to: %s" % e,
                  test_case_id, script_id, "TTK2", loglevel, tbd)
        return False

################################################################################
# Function    : clear_cmos_function
# Parameter   : log_level,tbd
# Description :	This function will clear CMOS
# Return      :	returns 1 if it clears CMOS  or returns 0
##########################General python Imports################################


def clear_cmos_function(log_level="ALL", tbd=None):
    import time

    aDevice = initialize_ttk(log_level, tbd)                                    #initializing the TTK
    time.sleep(lib_constants.SLEEP_TIME)

    res = aDevice.clearCMOS(5)                                                  #Clearing CMOS Using TTK

    time.sleep(lib_constants.SHORT_TIME)

    if res == [0]:
        status = 1
    else:
        status = 0

    return status

###############################################################################
# Function name   : device_list_in_devie manager
# description     : lists all devices available in device manager based on the
#                   parameter passed to the function.
# parameters      : dev_class_name - is calss name of device comes under in
#                   device manager
# Returns         : True on success, False on Failure
###############################################################################


def device_list_under_class_devmgmt(dev_class_name, loglevel="ALL", tbd=None):

    import lib_constants
    import platform

    path = lib_constants.TOOLPATH
    devcon_path = os.path.join(path, 'devcon')
    dev_listfile = os.path.join(devcon_path, 'device_list.txt')                 #join with device list along with the devcon path
    os.chdir(devcon_path)

    if dev_listfile in path:                                                    # check for dev_listfile in path
        os.remove(dev_listfile)                                                 # remove the file if existing
    else:
        pass

    if "64" in platform.uname()[4]:
        devcon = 'devcon_x64.exe'                                               #use 64 bit exe if platform name has 64 in it
        devcon_cmd = os.path.join(devcon_path, devcon)                          #join the path with exe and store in a variable
        cmd = devcon_cmd + " classes" + " > device_list.txt"                    #concat the stored variable with classes and filename to output the results to

    else:
        devcon = 'devcon.exe'
        devcon_cmd = os.path.join(devcon_path, devcon)                          #join the path with exe and store in a variable
        cmd = devcon_cmd + " classes " + "> device_list.txt"                    #concat the stored variable with classes and filename to output the results to

    temp = os.system(cmd)                                                       #run the command in os.system

    if 0 == temp:                                                               #if temp is 0
        return True                                                             #return True
    else:
        write_log(lib_constants.LOG_WARNING, "WARNING: Get Device list "
                  "command is not executed successfully", "None", "None",
                  loglevel, tbd)
        return False                                                            #return False

################################################################################
# Function name : convert file text into upper
# Description   : To convert file text into the upper case
# Parameters    : file_path - which containing file path and textfile_name-
#                 contain the file name
# Return        : returning file text with upper case
################################################################################


def file_text_to_upper(path, textfile_name, loglevel = "ALL", tbd = None):

    new_file = textfile_name.split('.')[0] + "_upper" + ".txt"                  #store the file name
    os.chdir(path)

    if os.path.exists(new_file):                                                #if path exists
        os.remove(new_file)                                                     #remove the file
        foutput = open(new_file, 'w')                                           #open new file
    else:
        foutput = open(new_file, 'w')                                           #open new file

    os.chdir(path)
    for line in open(textfile_name):                                            #iterate through line
        line = line.upper()                                                     #convert lines to upper
        foutput.write(line)                                                     #write line
    foutput.close()                                                             #close the file

################################################################################
# Function name : return_line_from_log()
# Description   : To search perticular string in log file
# Parameters    : file_name - file name including whole path, req_pattern -
#                 string/pattern/word to find in log file should be case
#                 sensitive
# Return        : On success first occurrence of whole line, 0 on fail to find
#                 the string, 2 on file not existed
################################################################################


def return_line_from_log(file_name, req_pattern, loglevel="ALL", tbd=None):

    global temp_line
    find_flag = False

    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as file_handler:                          # Open file
                for line in file_handler:                                       # Iterate through each line
                    if req_pattern.upper() in line:                             # If req pattern in line
                        temp_line = line                                        # Store line in temp_line
                        find_flag = True                                        # Find_flag set to true
                        break
        except:
            with codecs.open(file_name, "r", encoding="utf-8",
                             errors="ignore") as file_handler:                  # Open file
                for line in file_handler:                                       # Iterate through each line
                    if req_pattern.upper() in line:                             # If req pattern in line
                        temp_line = line                                        # Store line in temp_line
                        find_flag = True                                        # Find_flag set to true
                        break

        if find_flag:
            return temp_line                                                    # If true return temp_line
        else:
            write_log(lib_constants.LOG_INFO, "INFO: Given '%s' string "
                      "is not found in this file %s" % (req_pattern, file_name),
                      "None", "None", loglevel, tbd)
            return False
    else:
        write_log(lib_constants.LOG_WARNING, "WARNING: Given file %s does not "
                  "exist" % file_name, "None", "None", loglevel, tbd)
        return 2

################################################################################
# Function name : get_device_list()
# Description   : To get device list
# Parameters    : file_name - file name including whole path, req_pattern -
#                 string/pattern/word to find in log file should be case
#                 sensitive
# Return        : returns string or False
################################################################################


def get_device_list(log_file, script_id, test_case_id, loglevel="ALL",
                    tbd=None):

    try:
        import codecs
        import wmi

        c = wmi.WMI()
        query = "Select * from Win32_PnPEntity"
        result = c.query(query)                                                 #store query in result
        s = ''                                                                  #s = empty string
        count = 0

        for x in result:                                                        #iterate through result
            if x.caption is None:                                               # if x.caption is None
                continue                                                        #continue
            else:
                s = s + x.caption
                s += '\n'                                                       #add s to x.caption
                count += 1                                                      #add count with 1

        if count > 0:
            f = codecs.open(log_file, 'w', "utf-8")                             # open txt file as codecs handle
            f.write(s)                                                          # write s to file
            f.close()                                                           # close file
            return True                                                         # return the txt
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Device list "
                      "command is not executed", test_case_id, script_id,
                      "None", "None", loglevel, tbd)
            return False                                                        # else return false
    except Exception as e:
        return False

################################################################################
# Function Name : check_device_status
# Parameters    : device_name, tc_id, script_id, log_level, tbd
# Return Value  : returns True if required device with no yellow bang is found
#                 and False otherwise
# Purpose       : to check required device is found in device manager
################################################################################


def check_device_status(device_name, tc_id, script_id, log_level="ALL",
                        tbd="None"):

    import lib_constants
    c = wmi.WMI()

    for device in c.Win32_PnPEntity():
        try:
            if device.Name.upper().strip() == device_name.upper().strip():      #check if device name present in device manager
                if 0 != device.ConfigManagerErrorCode:                          #check if yellow bang is present for device_name
                    write_log(lib_constants.LOG_INFO, "INFO: There is yellow "
                              "bang observed for child '%s' in Device Manager"
                              % device.Name, tc_id, script_id,"None", "None",
                              log_level, tbd)                                   #write the info msg to log if devie has yellow bang in dev.manager
                    return False
                else:
                    write_log(lib_constants.LOG_INFO, "INFO: There is no "
                              "yellow bang observed for child '%s' in Device "
                              "Manager" % device.Name,tc_id, script_id, "None",
                              "None", log_level, tbd)                           #write the info msg to log if device has no yellow bang in dev. manager
                    return True
            else:
                pass
        except Exception as e:
            pass
    write_log(lib_constants.LOG_WARNING, "WARNING: required device: %s is "
              "not found in the device manager" % device_name, tc_id,
              script_id, "None", "None", log_level, tbd)                        # write error msg to log if device not found in dev. manger
    return None

################################################################################
# Function Name    : move_char_index
# Functionality    : it will swap the boot order based on the priority
# input parameter  : chars,char,new_index,log_level = "012345",tbd=None
# return           : it will return the bootorder index to be set
################################################################################


def move_char_index(chars, char, new_index, log_level="012345", tbd=None):

    char_list = chars.split("-")
    old_index = char_list.index(char)
    char = char_list.pop(old_index)
    char_list.insert(new_index, char)
    return '-'.join(char_list)

################################################################################
# Function Name : update_mac
# Parameters    : tc_id, script_id, log_level, tbd
# Return Value  : returns True if mac address update is successful and False
#                 otherwise
# Purpose       : to update mac address on the SUT
################################################################################


def update_mac(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        mac_address = utils.ReadConfig("BIOS_FLASHING", "MAC_ADDRESS")          #get mac address from config file

        if "FAIL" in mac_address:                                               #failed to get value form config
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get mac "
                      "address from config.ini unber tag BIOS_FLASHING & "
                      "variable MAC_ADDRESS", tc_id, script_id, "None", "None",
                      log_level, tbd)
            return False

        fft_path = utils.ReadConfig("BIOS_FLASHING", "FFT_INSTALLED_PATH")      #get fft path dfrom config file

        if "FAIL" in fft_path:                                                  #failed to get value form config
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get mac "
                      "FFT tools installed path from config.ini unber tag BIOS"
                      "_FLASHING & variable FFT_INSTALLED_PATH", tc_id,
                      script_id, "None", "None", log_level, tbd)
            return False

        fft_file = os.path.join(fft_path, "FFT.exe")

        if os.path.isfile(fft_file):                                            #check if fft.exe is available in the installed path
            write_log(lib_constants.LOG_INFO, "INFO: FFT tool is identified "
                      "at %s" % fft_file, tc_id, script_id, "FFT", "None",
                      log_level, tbd)
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to locate "
                      "FFT tool in the installed path %s" % fft_file, tc_id,
                      script_id, "FFT", "None", log_level, tbd)
            return False

        command = fft_file + " -l flashmac:" + mac_address                      #command for flashing mac address
        result = subprocess.Popen(command, stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE).communicate()[0]      #result will have the output from the tool

        if "Success: MAC address is flashed" in result:                         #if success msg in the result, pass
            write_log(lib_constants.LOG_INFO, "INFO: MAC address is flashed "
                      "successfully", tc_id, script_id, "FFT", "None",
                      log_level, tbd)
            return True
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to flash "
                      "MAC address in the SUT", tc_id, script_id, "FFT",
                      "None", log_level, tbd)
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name  : column_number
# Description    : parses the log file and returns the column number
#                  of string passed to the function
# Parameters     : file_name = .csv file name to be parsed,
#                  column_name = column name to be parsed
#                  tc_id,script_id,log_level
# Returns        : column number of the string column_name
###############################################################################


def find_column_number(file_name, column_name, tc_id, script_id,
                       log_level="ALL", tbd="None"):

    try:
        col_num = 0                                                             #value zero initilise for column  number
        tat_path_folder = os.path.join(lib_constants.SCRIPTDIR)                 #getting the tat file location
        os.chdir(tat_path_folder)                                               #setting child directory
        new_tat_file = open(file_name, "rb")                                    #opening the found log file
        reader = csv.reader(new_tat_file)                                       #reading the tat log file
        row_num = 0                                                             #value zero initilised to row number
        cnt = 0                                                                 #value zero initilised to count(use to get the count of column)

        for row in reader:                                                      #loop through the row
            if 0 == row_num:
                header = row
                for indexelement in header:                                     #loop through header of the log file
                    if column_name.lower() in indexelement.lower():             #checking if the column name present if not increse the count and go to next coloumn
                        col_num = cnt
                        break
                    cnt += 1
            break
        new_tat_file.close()
        return col_num
    except Exception as e:                                                      #return execption if any error occour while reading or finding the matching value
     write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
               script_id, "None", "None", log_level, tbd)
     return False

################################################################################
# Function name   : get_avg_system_value
# Parameters      : file_name = .csv file name to be parsed,
#                   column_number = column number to be parsed
# Returns         : average value .
################################################################################


def get_system_value(file_name, column_name, tc_id, script_id, log_level="ALL",
                     tbd="None"):

    try:
        Required_List = []                                                      #Emptly list define with name Required_List
        Total_Sum = 0.0                                                         #value zero initilise for total sum
        rownum = 0                                                              #value zero initilise for row number

        with open(file_name, "rb") as tfile:                                    #opening the tat log file
            reader = csv.reader(tfile)                                          #reading .csv file
            for row in reader:                                                  #Looping through the header row of .csv file
                if 0 == rownum:
                    header = row
                else:
                    colnum =0
                    for col in row:                                             #loop through the column to find the matching coloumn
                        if colnum == column_name:
                            if col:
                                col = col.replace('"', "")
                                if 'Invalid' == col:
                                    col = 0
                            Required_List.append(col)                           #creating list of the found values in matching coloumn
                        colnum = colnum + 1
                rownum += 1
        validate_list = [item.isdigit()for item in Required_List]               #Validate if required col is integer
        if False in validate_list:
            return Required_List[-1]
        else:
            if Required_List[-1] == '0':
                return str(Required_List[-1])
            else:
                return float(Required_List[-1])
    except Exception as e:                                                      #Exeption throw if fail to get avrage value
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
                  script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : logical_processors
# Parameters      : n/a
# Functionality   : get logical processor
# Return Value    :'Returns the number of logical processor
################################################################################


def logical_processors():

    c = wmi.WMI()                                                               #create wmi instance
    result = c.query("SELECT NumberOfLogicalProcessors FROM Win32_Processor")
    if result:
        for x in result:
            return str(x.NumberOfLogicalProcessors)                             #return the number of logical processor of the sut

################################################################################
# Function Name : check_for_post_code
# Parameters    : post_code, wait_time, tc_id, script_id, log_level, tbd
# Return Value  : returns True if the given post code is seen within the time
#                 limit and False otherwise
# Purpose       : to check whether a specific post code is seen or not
################################################################################


def check_for_post_code(post_code, wait_time, tc_id, script_id,
                        log_level="ALL", tbd=None):

    try:
        import lib_ttk2_operations
        result = lib_ttk2_operations.\
            check_for_post_code(post_code, wait_time, tc_id, script_id,
                                log_level, tbd)
        if result is not None:
            return result
        else:
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
                  script_id, "TTK", "None", log_level, tbd)
        return False

################################################################################
# Function Name : find_file
# Parameters    : file_name, root_folder, tc_id, script_id, log_level, tbd
# Return Value  : returns full file path if the given file is found and False
#                 otherwise
# Purpose       : to find a particular file under a particular root folder
################################################################################


def find_file(file_name, root_folder, tc_id, script_id, log_level="ALL",
              tbd=None):

    try:
        for root, dirs, files in os.walk(root_folder):                          #this will give a tuple of root dirctory, directories and files
            for item in files:
                if file_name.lower() == item.lower():                           #if file is available in files, return it and break
                    write_log(lib_constants.LOG_INFO, "INFO: File is found "
                              "in the system at %s" % os.path.join(root, item),
                              tc_id, script_id, "None", "None", log_level, tbd)
                    return root

        write_log(lib_constants.LOG_WARNING, "WARNING: File %s is not found "
                  "in the system" % file_name, tc_id, script_id, "None",
                  "None", log_level, tbd)                                       #if the file is not found anywhere, only then control comes here and thus failure
        return False

    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : nsh_file_logical_drive_creation
# Parameters    : cmd_to_run, test_case_id,script_id,log_level, tbd
# Return Value  : returns true on success and False
#                 otherwise
# Purpose       : To create the .nsh file & create the logical drive
#                 and set first boot order to edk shell
################################################################################


def nsh_file_logical_drive_creation(cmd_to_run, test_case_id, script_id,
                                    loglevel="ALL", tbd=None):

    try:
        ####################General python import #############################
        import glob
        import shutil
        import os
        ####################local python import ###############################
        import lib_run_command
        import lib_constants

        data_ret = lib_run_command.nsh_file_gen(cmd_to_run, test_case_id,
                                                script_id, loglevel, tbd)       #calling library function to generate nsh file
        if False == data_ret:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to generate "
                      "required .nsh files", test_case_id, script_id, "None",
                      "None", loglevel, tbd)
            return False

        if lib_run_command.create_logical_drive('S', test_case_id, script_id,
                                                loglevel, tbd):                 #library call to create logical drive
            tool_name=cmd_to_run.split(".EFI")                                  #save the toolname by splitting with .EFI
            tool_path = lib_constants.TOOLPATH

            if len(tool_name[0]) != 0:                                          #search for efi file in tools directory
                files = glob.glob(tool_path + "\\\\*")
                for f in files:
                    if tool_name[0].lower() in f.lower():
                        if os.path.isdir(f):
                            files1 = glob.glob(f + "\\\\*.efi")
                            for g in files1:
                                if tool_name[0].lower() in g.lower():
                                    shutil.copy(g, "S:\\\\")                    #copy to Shared drive from tools directory
                                    break
                        else:
                            shutil.copy(f, "S:\\\\")                             #copy to shared drive in the other condition
                            write_log(lib_constants.LOG_INFO,"INFO: Tool "
                                      "copied", test_case_id, script_id,
                                      "None", "None", loglevel, tbd)

            if os.path.exists('S:\\\\') :                                       #check for new logical drive
                time.sleep(lib_constants.FIVE_SECONDS)                          #sleep for 5 seconds
                shutil.copy("startup.nsh","S:\\\\")                             #copy startup nsh to current working directory
                write_log(lib_constants.LOG_INFO, "INFO:The Logical Drive "
                          "created", test_case_id, script_id, "None", "None",
                          loglevel, tbd)
            else:
                os.chdir(lib_constants.SCRIPTDIR)
                write_log(lib_constants.LOG_FAIL, "FAIL: Failed to create "
                          "logical drive", test_case_id, script_id, "None",
                          "None", loglevel, tbd)                                #write fail msg to log
                return False

            if set_multiple_bootorder(test_case_id, script_id, loglevel, tbd):
                write_log(lib_constants.LOG_INFO, "INFO: Internal EDK Shell "
                          "is set as the first boot device", test_case_id,
                          script_id, "None", "None", loglevel, tbd)             #write pass msg to log
                return True
            else:
                write_log(lib_constants.LOG_FAIL, "FAIL: Failed to set "
                          "Internal EDK Shell as the first boot deivice",
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)                                                  #write fail msg to log
                return False
        else:
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id,"None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : logical_drive_mapping
# Parameters    : gen_log,test_case_id,script_id,log_level, tbd
# Return Value  : returns true on success and False
#                 otherwise
# Purpose       : To map the logical drive and copy the log from logical drive
################################################################################


def logical_drive_mapping(gen_log, test_case_id, script_id, loglevel="ALL",
                          tbd=None):

    try:
        ####################General python import ##############################
        import shutil
        import os
        import time
        import codecs
        ####################local python import ################################
        import lib_run_command
        import lib_constants

        if lib_run_command.create_logical_drive('S', test_case_id, script_id,
                                                loglevel, tbd):                 #Call library function to create logical drive S
            if os.path.exists(gen_log) :
                shutil.copy(gen_log, lib_constants.SCRIPTDIR)                   #copy log to Script directory
                os.chdir(lib_constants.SCRIPTDIR)
                write_log(lib_constants.LOG_INFO, "INFO: The log is generated "
                          "in EFI shell", test_case_id, script_id, "None",
                          "None", loglevel, tbd)                                #write info msg to log

                final_result = lib_run_command.\
                    drive_cleanup(test_case_id, script_id, loglevel, tbd)       #call library to cleanup shared drive
                if final_result:
                    write_log(lib_constants.LOG_INFO, "INFO: .nsh files "
                              "removed successfully", test_case_id, script_id,
                              "None", "None", loglevel, tbd)                                              #write pass msg to log
                    time.sleep(lib_constants.POWER_TEST_MIN_TIME)
                    return True
                else:
                    write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "remove .nsh files", test_case_id, script_id,
                              "None", "None", loglevel, tbd)                    #write fail msg to log
                    time.sleep(lib_constants.POWER_TEST_MIN_TIME)
                    return False
            else:
                os.chdir(lib_constants.SCRIPTDIR)
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                          "verify the log in the logical drive", test_case_id,
                          script_id, "None", "None", loglevel, tbd)                                          #write fail msg to log
                time.sleep(lib_constants.POWER_TEST_MIN_TIME)
                return False
        else :
            write_log(lib_constants.LOG_WARNING, "WARNING: Fail to create "
                      "logical drive", test_case_id, script_id, "None", "None",
                      loglevel, tbd)                                            #write fail msg to log
            time.sleep(lib_constants.POWER_TEST_MIN_TIME)
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : map_drive_read_secure_boot
# Parameters    : test_case_id,script_id,log_level, tbd
# Return Value  : returns true on success and False otherwise
# Purpose       : To map the logical drive & delete the .nsh files and read
#                 security option from powershell
################################################################################


def map_drive_read_secure_boot(test_case_id, script_id, loglevel="ALL",
                               tbd=None):

    try:
        ####################local python import ################################
        import lib_run_command
        import lib_constants
        import lib_set_bios

        if lib_run_command.create_logical_drive('S', test_case_id, script_id,
                                                loglevel, tbd):                 #Call library function to create logical drive S
            final_result = lib_run_command.\
                drive_cleanup(test_case_id, script_id, loglevel, tbd)           #call library to cleanup shared drive

            if final_result:
                if lib_set_bios.read_secure_boot(test_case_id, script_id,
                                                 loglevel, tbd):
                    write_log(lib_constants.LOG_INFO, "INFO: Secure Boot "
                              "Option set successfully in BIOS", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
                    return True
                else:
                    write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "set Secure boot option to Enable in BIOS",
                              test_case_id, script_id, "None","None", loglevel,
                              tbd)
                    return False
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                          "remove .nsh files and also to set the bios option",
                          test_case_id, script_id, "None","None", loglevel, tbd)
                return False
        else :
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to create "
                      "logical drive", test_case_id, script_id, "None", "None",
                      loglevel, tbd)
            time.sleep(lib_constants.POWER_TEST_MIN_TIME)
            return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", loglevel, tbd)
        time.sleep(lib_constants.POWER_TEST_MIN_TIME)
        return False

################################################################################
# Function Name : check_ac_dc_connection()
# Parameters    : testcase id, script id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to verify if DC is connected to SUT or not
################################################################################


def check_ac_dc_connection(test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        battery_name = ""
        batteryinfo_str = \
            str(batteryinfo(test_case_id, script_id, loglevel,tbd))             # library call to batteryinfo() function

        if batteryinfo_str:
            pass
        else:
            return False

        time.sleep(lib_constants.FIVE_SECONDS)
        c = wmi.WMI()

        for n in c.Win32_Battery():                                             #WMI query to get the battery information and its status
            battery_name = n.Name

        if 'Battery 0' not in battery_name:                                     #Checking if DC battery is connected to SUT(only DC)
            write_log(lib_constants.LOG_INFO, "INFO: DC Battery is Connected",
                      test_case_id, script_id, "None", "None", loglevel, tbd)   # write info msg to log
            if str(lib_constants.TWO) == batteryinfo_str:                       #Checking if SUT is in AC+DC mode
                write_log(lib_constants.LOG_INFO, "INFO: It is verified that, "
                          "SUT is in AC + DC  mode", test_case_id, script_id,
                          "None", "None", loglevel, tbd)                        # write info msg to log
                return "AC + DC"
            else:
                write_log(lib_constants.LOG_INFO, "INFO: SUT is in DC mode "
                          "but AC is not connected ", test_case_id,
                          script_id, "None", "None", loglevel, tbd)             # write info msg to log
                return "DC"
        else:
            if str(lib_constants.TWO) == batteryinfo_str:                       #Checking if SUT is in AC mode
                write_log(lib_constants.LOG_INFO, "INFO: It is verified that, "
                          "SUT is in AC mode & Virtual Battery relay is set "
                          "to OFF  but DC battery is not connected",
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)                                                  # write info msg to log
                return "AC"
            elif str(lib_constants.THREE) == batteryinfo_str:                   #Checking if SUT is in AC mode
                write_log(lib_constants.LOG_INFO, "INFO: It is verified that, "
                          "SUT is in AC mode & Virtual Battery relay is set "
                          "to ON but DC battery is not connected ",
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)                                                  # write info msg to log
                return "virtual_battery_mode"
            else:                                                               #Checking if SUT is not in AC mode and not in DC mode
                write_log(lib_constants.LOG_WARNING, "WARNING: Not able to "
                          "verify power mode of SUT system", test_case_id,
                          script_id, "None", "None", loglevel, tbd)             # write info msg to log
                return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id,"None", "None", loglevel, tbd)        # write error msg to log
        return False

################################################################################
# Function Name : batteryinfo
# Parameters    : test case id,script id, loglevel, tbd
# Functionality : This checks the status of the battery
# Return Value :  result value/false
################################################################################


def batteryinfo(test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        WMIobj = wmi.WMI()
        battery = WMIobj.query("SELECT Availability FROM Win32_Battery")        #WMI query to get the battery information and its status

        if battery:
            for values in battery:
                return values.Availability                                      # Charging Battery Grammar section end
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: No value found in "
                      "the wmi query of Win32_Battery", test_case_id,
                      script_id, "None", "None",loglevel, tbd)                  # write info msg to log
            return False
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id,"None", "None", loglevel, tbd)        # write error msg to log
        return False

################################################################################
#  Function name   : run_socwatch
#  description     : To start/stop socwatch tool
#  parameters      : 'status' is start/stop
#  Returns         : True on sucess, False on Failure to perform status
################################################################################


def run_socwatch(status, state, test_case_id, script_id, log_level ="ALL",
                 tbd= "None"):

    try:
        soc_path = utils.ReadConfig('capture_socwatch','path')                  # reads the socwatch tool path from config file
        soc_exe = utils.ReadConfig('capture_socwatch','installed_exe')          # reads the socwatch application name from config file
        if os.path.exists(soc_path) :                                           # checks if the tool is present in the given path

            for filename in os.listdir(soc_path):
                if ((filename.startswith('SOCWatchOutput') and
                     filename.endswith('.csv')) or
                     (filename.endswith('_SOC_LOG.csv'))):                      #Checks if the soc log file already existing
                    filename = os.path.join(soc_path, filename)
                    os.remove(filename)                                         #Removes the old\existing socwatch log
                else:
                    pass
            if status == "START" :                                              # checks for state if already present
                if state == "C-state" or state == "C-STATE":
                    state = 'cpu-cstate'                                        # returns the state which have to be captured from soc watch
                elif state == "P-state" or state == "P-STATE" :
                    state = 'cpu-pstate'
                elif state == "T-state" or state == "T-STATE":
                    state = 'cpu-tstate'
                elif state == "S-state" or state == "S-STATE" :
                    state = 'sstate'
                elif state == "D-state" or state == "D-STATE" or \
                     state == "rtd3" or state == "RTD3":
                    state = 'acpi-dstate'
                elif state == 'slp-s0' or state == 'SLP-S0':
                    state = 'pch-slps0'
                elif state == 'GT-state' or state == 'GT-STATE':
                    state = 'gfx-pstate'
                elif state == 'cm-states' or state == 'CM-STATES':
                    state = 'cs -f sstate'
                else:
                    pass

                soc_path_exe = os.path.join(soc_path, soc_exe)                  # combines the tool path along with the socwatch application name
                cmd_PROCESS = soc_path_exe + " -f " + state                     # cmd to execute the socwatch tool to capture the states
                os.chdir(lib_constants.SCRIPTDIR)
                log_file_name = os.path.join(lib_constants.SCRIPTDIR,
                                                 "SOCWatchOutput.csv")
                ret = os.system("START CMD /C " + cmd_PROCESS)                  # executes the Soc watch application to start the state capture

                if ret == 0:
                    return log_file_name 
                else:
                    return False
            else:
                tasklist = subprocess.check_output("TASKLIST")                  # checks the list in task manager
                time.sleep(lib_constants.TWO)
                if "socwatch.exe" in tasklist :                                 # checks if socwatch.exe application is running in taskmanager
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shell.AppActivate("cmd.exe")                                # activates the SOC watch application window
                    time.sleep(lib_constants.TWO)
                    shell.SendKeys(""""^{c}""")                                 # sends key (Ctrl+c) to terminated the socwatch application

                    time.sleep(lib_constants.TEN_SECONDS)
                    log_file_name = os.path.join(lib_constants.SCRIPTDIR,
                                                 "SOCWatchOutput.csv")          #Joins the logfile with the logpath

                    if os.path.exists(log_file_name):
                        os.chdir(soc_path)
                        write_log(lib_constants.LOG_INFO, "INFO: Socwatch log "
                                  "file found", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                        return log_file_name                                            #Returns the log file name as a string
                    else:
                        write_log(lib_constants.LOG_WARNING, "WARNING: "
                                  "Socwatch log file not found", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                        return False
                else:
                    return False
        else:
            return 2
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)      #Write error msg to log
        return False

################################################################################
# Function Name : press_keys_dictionary
# Parameters    : press_key_token,test case id,script id, loglevel, tbd
# Functionality : Mapping of press_key to KBC class dictionary
# Return Value :  Return press key mapping value on success & false on failure
################################################################################


def press_keys_dictionary(press_key_token, test_case_id, script_id,
                          loglevel="ALL", tbd=None):

    try:
        final_list = []                                                         #list initialize
        final_press_key_string = ""

        if "+" in press_key_token:                                              #if '+' is present in press_key_token
            press_key_token_list = press_key_token.split("+")
            for item in press_key_token_list:                                   #loop to iterate for capitalize the every element of press_key_token_list
                if item.isdigit():                                              #if element of list is digit(0-9)
                    final_list.append(item)
                elif (1 == len(item)) and (item > 'a' and item <'z'):           #if element of list is in b/w single lower case letter(a-z)
                    final_list.append(item)
                else:
                    item_press  = item.capitalize()
                    final_list.append(item_press)
            final_press_key_string = '+'.join(str(e) for e in final_list)
        elif (1 == len(press_key_token)) and \
                (press_key_token > 'a' and press_key_token <'z'):               #if element of list is in b/w single lower case letter(a-z) and '+' is not present in token
            final_press_key_string = press_key_token
        elif " "in press_key_token:                                             #if element of list is containing single space(" ")
            press_key_token =  press_key_token.replace(" ", "_")
            final_press_key_string = press_key_token.capitalize()
        else:
            final_press_key_string = press_key_token.capitalize()
        return final_press_key_string
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", loglevel, tbd)       # write error msg to log
        return False

################################################################################
# Function Name : activate_kvm
# Functionality : to activate the KVM for to use sikuli
# Parameters    : tc_id, script_id, log_level and tbd
# Return Value  : True on successful action, False otherwise
################################################################################


def activate_kvm(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        kvm_name = utils.ReadConfig("kvm_name", "name")
        kvm_title = utils.ReadConfig("kvm_name", "kvm_title")
        activate_path = utils.ReadConfig("sikuli", "Activexe")

        title = kvm_name + " - " + kvm_title                                    #Command for activating the kvm window

        if "FAIL:" in [kvm_name, kvm_title, activate_path]:
            write_log(lib_constants.LOG_WARNING, "WARNING: config entry is "
                      "missing for tag name :kvm_name or sikuli_path or "
                      "sikuli_exe", tc_id, script_id, "None", "None",
                      log_level, tbd)
            return False                                                        #If the readconfig function returnd fail it means no config entry is given

        window_path = activate_path + " " + title
        kvm_activate = subprocess.Popen(window_path, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        return True
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
                  script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name : get_entire_device_list()
# Description   : To get entire device list from device manager
# Parameters    : file_name - file name including whole path,
# Return        : returns log file path or False
################################################################################


def get_entire_device_list(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        import platform
        from subprocess import Popen, PIPE

        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path, 'devcon')
        file_name = test_case_id.replace(".py", ".txt")
        dev_listfile = os.path.join(lib_constants.SCRIPTDIR, file_name)         #join with device list along with the devcon path
        os.chdir(devcon_path)

        if dev_listfile in path:                                                # check for dev_listfile in path
            os.remove(dev_listfile)                                             # remove the file if existing
        else:
            pass

        if "64" in platform.uname()[4]:
            devcon_exe = 'devcon_x64.exe'                                       #use 64 bit exe if platform name has 64 in it
        else:
            devcon_exe = 'devcon.exe'                                           #use 32 bit exe if platform name has 64 in it

        command = devcon_exe + " findAll * "                                    #Command to generate the device list
        time.sleep(lib_constants.FIVE_SECONDS)
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        os.chdir(lib_constants.SCRIPTDIR)

        if len(stderr) > 0:
            write_log(lib_constants.LOG_WARNING, "WARNING: Unable to get the "
                      "device list due to %s " % str(stderr),test_case_id,
                      script_id, "None", "None",log_level, tbd)                 #Write the error to the log
            return False
        else:
            with open(dev_listfile, "w") as f_:
                f_.write(str(stdout))
            return dev_listfile                                                 #returning True on Success

    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)      #Write the execption error to the log
        return False

################################################################################
# Function Name     : Indextostring
# Parameters        : tc_id, script_id, Index, bit_value,tbd
# Functionality     : convert index parameter to string
# Return Value      : returns exception if fail
################################################################################


def Indextostring(Index, tc_id, script_id, log_level="All", tbd = None):        #function  to change index to string

    try:
        orignalstr = ""
        orignalstr = ''.join(Index)
        return orignalstr
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name     : stringtoindex
# Parameters        : tc_id, script_id, orignalstr, bit_value,tbd
# Functionality     : convert string input to index
# Return Value      : returns exception if fail
################################################################################


def stringtoindex(orignalstr, tc_id, script_id, log_level="All", tbd=None):     #function to change string to index

    try:
        bitlist=[]
        for bitpos in orignalstr:
            bitlist.append(bitpos)
        return bitlist
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
                  script_id, "None", "None", log_level, tbd)                    #throw error if any exception
        return False

################################################################################
# Function Name : return_reg
# Parameters    : reg
# Functionality : Returns Registry required
# Return Value  : Returns Registry required
################################################################################


def return_reg(reg=None):

    import winreg as winreg
    _reg = ""

    if reg == 'HKEY_CLASSES_ROOT':
        _reg = winreg.HKEY_CLASSES_ROOT
    if reg == 'HKEY_CURRENT_USER':
        _reg = winreg.HKEY_CURRENT_USER
    if reg == 'HKEY_LOCAL_MACHINE' or reg == 'HKLM':
        _reg = winreg.HKEY_LOCAL_MACHINE
    if reg == 'HKEY_USERS':
        _reg = winreg.HKEY_USERS
    if reg == 'HKEY_PERFORMANCE_DATA':
        _reg = winreg.HKEY_PERFORMANCE_DATA
    if reg == 'HKEY_CURRENT_CONFIG':
        _reg = winreg.HKEY_CURRENT_CONFIG
    if reg == 'HKEY_DYN_DATA':
        _reg = winreg.HKEY_DYN_DATA

    return _reg

################################################################################
# Function Name : return_type
# Parameters    : regtype
# Functionality : Returns Registry type
# Return Value  : Returns Registry type
################################################################################


def return_type(regtype=None):

    import winreg as winreg
    _type = ""

    if regtype == 'DWORD' or regtype == 'REG_DWORD':
        _type = winreg.REG_DWORD
    if regtype == 'REG_DWORD_LITTLE_ENDIAN' or regtype == 'DWORD_LITTLE_ENDIAN':
        _type = winreg.REG_DWORD_LITTLE_ENDIAN
    if regtype == 'REG_DWORD_BIG_ENDIAN' or regtype == 'DWORD_BIG_ENDIAN':
        _type = winreg.REG_DWORD_BIG_ENDIAN
    if regtype == 'REG_EXPAND_SZ' or regtype == 'EXPAND_SZ':
        _type = winreg.REG_EXPAND_SZ
    if regtype == 'REG_LINK' or regtype == regtype == 'LINK':
        _type = winreg.REG_LINK
    if regtype == 'REG_MULTI_SZ' or regtype == 'MULTI_SZ':
        _type = winreg.REG_MULTI_SZ
    if regtype == 'REG_NONE' or regtype == 'NONE':
        _type = winreg.REG_NONE
    if regtype == 'REG_RESOURCE_LIST' or regtype == 'RESOURCE_LIST':
        _type = winreg.REG_RESOURCE_LIST
    if regtype == 'REG_FULL_RESOURCE_DESCRIPTOR' or \
            regtype == 'FULL_RESOURCE_DESCRIPTOR':
        _type = winreg.REG_FULL_RESOURCE_DESCRIPTOR
    if regtype == 'REG_RESOURCE_REQUIREMENTS_LIST' or \
            regtype == 'RESOURCE_REQUIREMENTS_LIST':
        _type = winreg.REG_RESOURCE_REQUIREMENTS_LIST
    if regtype == 'REG_SZ' or regtype == 'SZ':
        _type = winreg.REG_SZ

    return _type

################################################################################
# Function Name : check_child_device_enumeration
# Parameters    : child_device_from_tc,testcase id, script id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : To check child device name  is enumerated in device manager
################################################################################


def check_child_device_enumeration(child_device_from_tc, test_case_id,
                                   script_id, loglevel="ALL", tbd="None"):

    try:
        path=os.getcwd()
        log_file = os.path.join(path, 'devicemanager_list.txt')

        if get_device_list(log_file, script_id, test_case_id, loglevel, tbd):   # TO get device List from the device manager
            file_text_to_upper(path, 'devicemanager_list.txt', loglevel , tbd)  #to convert file text to upper case
            devic_list_path = os.path.join(path, 'devicemanager_list_upper.txt')
            return_line_child = \
                return_line_from_log(devic_list_path, child_device_from_tc,
                                     loglevel, tbd)

            if False !=  return_line_child and 2 != return_line_child:
                if child_device_from_tc.upper() in return_line_child:
                    write_log(lib_constants.LOG_INFO, "INFO: Child device:%s "
                              "found in Device manager" % child_device_from_tc,
                              test_case_id, script_id, "None","None", loglevel,
                              tbd)
                    return True
                else:                                                           #if child device is not found in return line
                    write_log(lib_constants.LOG_WARNING, "WARNING: Child "
                              "Device:%s Not found in device manager"
                              % child_device_from_tc, test_case_id, script_id,
                              "None", "None", loglevel, tbd)
                    return False
            else:
                return False
    except Exception as e:                                                      #write error msg to log
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : bios_update_for_audio_video
# Parameters    : child_device_from_tc,testcase id, script id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : To update bios option and shut down
################################################################################


def bios_update_for_audio_video(test_case_id, script_id, log_level="ALL",
                                tbd="None"):

    try:
        result = lib_set_bios.\
                 xml_cli_set_bios(lib_constants.KBL_STATE_AFTER_G3,
                                  test_case_id, script_id, log_level, tbd)  #If tbd is KBL, the Bios path for State After G3 is set to S5

        if lib_constants.THREE == result:
            write_log(lib_constants.LOG_INFO, "INFO: BIOS updated successful "
                      "for state after G3", test_case_id, script_id, "None",
                      "None", log_level, tbd)                                   #Writing log info message to the log file
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to set state"
                      " after G3 bios option, system will boot to S0 after G3",
                      test_case_id, script_id, "None", "None", log_level, tbd)  #Writing warning message to the log file
            return False

        shutdown_cmd = 'shutdown /s /f /t ' + str(lib_constants.FIVE_SECONDS)
        os.system(shutdown_cmd)                                                 #Running the shutdown command

        write_log(lib_constants.LOG_INFO, "INFO: SUT is now put to shutdown to"
                  " perform G3", test_case_id, script_id, "None", "None",
                  log_level, tbd)                                               #Writing log info message to the log file
        return True
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)      #Writing exception message to the log file
        return False

################################################################################
# Function Name : check_running_application()
# Description   : check for running application in system
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successful running of app in system and 'false'
#                   on failure
# Purpose       : check for running application
################################################################################

def check_running_application(app, test_case_id, script_id, log_level="ALL",
                              tbd=None):

    os.chdir(lib_constants.SCRIPTDIR)
    app_name = app
    new_script_id = script_id.strip(".py")
    log_file = new_script_id + '.txt'
    log_path = lib_constants.SCRIPTDIR + "\\" + log_file
    cmd_to_check_app_run = 'tasklist > %s' % (log_path)                         # command to check if that application started or not

    try:
        found = False
        os.system(cmd_to_check_app_run)                                         # run the command cmd_to_check_app_run: Checking if application is
        datafile = file(log_path, 'r+')
        for line in datafile:
            line = line.lower()
            if app_name.lower() in line:
                found = True
                break
        return found

    except Exception as e:                                                      # error if failed to run the command
        os.chdir(lib_constants.SCRIPTDIR)
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : kill_running_application()
# Description   : killing running application in system
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successfully close of app in system and 'false'
#                   on failure
# Purpose       : kill the application task
################################################################################


def kill_running_application(app, test_case_id, script_id, log_level="ALL",
                             tbd=None):

    app_name = app
    cmd_to_kill_run_app = ['taskkill', '/f', '/im','%s' % (app_name)]           # command to kill an application

    try:
        process = subprocess.Popen(cmd_to_kill_run_app, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        output = process.communicate()

        if output:
            return True
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Please check the "
                      "application %s input according to task manager"
                      % app_name, test_case_id, script_id, "None", "None",
                      log_level, tbd)
            return False
    except Exception as e:                                                      # error if failed to run the command
        os.chdir(lib_constants.SCRIPTDIR)
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : launch_application_sys()
# Description   : launch application in system
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successfully launch of app in system and 'false'
#                   on failure
# Purpose       : launch the application task
################################################################################


def launch_application_sys(app, test_case_id, script_id, log_level="ALL",
                           tbd=None):

    app_name = app
    cmd_to_run_run_app = ['START', '%s' %(app_name)]                            # command to launch an application

    try:
        try:
            prog = subprocess.Popen(cmd_to_run_run_app, shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            if prog == []:
                return False
            else :
                write_log(lib_constants.LOG_INFO, "INFO: Please wait for  "
                          "10 sec to launch %s " % app_name, test_case_id,
                          script_id, "None", "None", log_level, tbd)
                time.sleep(10)
                return True
        except OSError as e:
            write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                      test_case_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:                                                      # error if failed to run the command
        os.chdir(lib_constants.SCRIPTDIR)
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : check_connectivity()
# Description   : check LAN or wifi connectivity
# Parameters    : ip,test_case_id is test case number, script_id is script
#                 number
# Returns       : 'true' on successfully launch of app in system and 'false'
#                   on failure
# Purpose       : to check lan or wifi connectivity
################################################################################


def check_connectivity(ip, test_case_id, script_id, log_level="ALL", tbd=None):

    ping_cmd = "ping "+str(ip).strip()
    p = subprocess.Popen(ping_cmd,stdout=subprocess.PIPE,shell=True,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out = p.communicate()[0]

    try:
        if "Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)" in out:
            write_log(lib_constants.LOG_INFO, "INFO: Ping from source to "
                      "destination is Verified ", test_case_id, script_id,
                      "None", "None", log_level, tbd)                           # return true if pass
            return True
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to verify "
                      "ping from source to destination", test_case_id,
                      script_id, "None", "None", log_level,tbd)                 # return false if fail
            return False
    except Exception as e:                                                      # error if failed to run the command
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : check_for_post_code_pre_silicon
# Parameters    : post_code, wait_time, tc_id, script_id, log_level, tbd
# Return Value  : returns True if the given post code is seen within the time
#                 limit and False otherwise
# Purpose       : to check whether a specific post code is seen or not
################################################################################


def check_for_post_code_presi(post_code, wait_time, tc_id, script_id,
                              log_level="ALL", tbd=None):

    try:
        counter = 0

        def read_simicslog(simics_log):                                         # Generator function to read the file from last line
            simics_log.seek(0, 2)                                               # Read simics log file from last line
            while True:
                line = simics_log.readline()                                    # Read line in simics log
                if not line:
                    time.sleep(lib_constants.POINT_ONE_SECONDS)                 # Sleep for 0.1 seconds
                    continue
                yield line                                                      # yields each line

        simics_log = open(lib_constants.SIMICS_LOG_PATH, 'r')                   # open simics log file
        loglines = read_simicslog(simics_log)

        for line in loglines:
            if post_code in line:                                               # Expected tranisition state info from Ex.S0->S5 is found
                write_log(lib_constants.LOG_INFO, "INFO: SUT shows %s"
                          % post_code, tc_id, script_id, "None", "None",
                          log_level, tbd)
                return True
            elif counter > wait_time:                                           # Expected tranisition info from ex.S0->S5 is not found even after wait time
                write_log(lib_constants.LOG_WARNING, "WARNING: SUT does not "
                          "show: %s" % post_code, tc_id, script_id, "None",
                          "None", log_level, tbd)
                return False
            else:                                                               # ignore and continue
                counter += 1

    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, tc_id,
                  script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : launch_application_sys()
# Description   : launch application in system
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successfully launch of app in system and 'false'
#                   on failure
# Purpose       : launch the application task
################################################################################


def run_powershell_cmd(cmd_to_run, test_case_id,script_id, loglevel="ALL",
                       tbd=None):

    try:
        import lib_run_command
        data_ret = lib_run_command.powershell_script(cmd_to_run, test_case_id,
                                                    script_id, loglevel, tbd)   #library call to generate the powershell script

        if False == data_ret:
            write_log(lib_constants.LOG_WARNING, "WARNING: The powershell "
                      "script failed to get generated", test_case_id,
                      script_id, "None", "None", loglevel, tbd)
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: The powershell script "
                      "got successfully generated", test_case_id, script_id,
                      "None", "None", loglevel, tbd)
            pass

        time.sleep(lib_constants.FIVE_SECONDS)                                  #sleep for 5 seconds

        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        script_dir = lib_constants.SCRIPTDIR
        log_path = script_dir + "\\" + log_file

        powershell_path = utils.ReadConfig("WIN_POWERSHELL", "PATH")            #Read from powershell the vaue of powershell path
        if "FAIL" in powershell_path:
            write_log(lib_constants.LOG_WARNING, "WARNING: config entry of "
                      "powershell_path is missing from the config file",
                      test_case_id, script_id, "None", "None", loglevel, tbd)
            return False

        shell_script = 'psquery.ps1'                                            #shell script should be placed in script directory
        exe_path = os.path.join(lib_constants.SCRIPTDIR, shell_script)

        final_command = 'powershell.exe '+ exe_path + ' > ' + log_path          #concat the commands along with the log path

        try:
            os.chdir(powershell_path)
            flag = os.system(final_command)                                     #run the command in command prompt using os.system
        except Exception as e:
            os.chdir(lib_constants.SCRIPTDIR)
            write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                      test_case_id, script_id, "None", "None", loglevel, tbd)
            return False

        os.chdir(lib_constants.SCRIPTDIR)
        if 0 == flag:
            if os.path.exists(log_file):
                file_size = os.path.getsize(log_file)                           #get the size of the log file
                if  "0" == file_size :
                    write_log(lib_constants.LOG_WARNING, "WARNING: failed to "
                              "generate log for command: %s" % cmd_to_run,
                              test_case_id, script_id, "None", "None",
                              loglevel, tbd)
                    return False
                else:
                    write_log(lib_constants.LOG_INFO, "INFO: The log is "
                              "generated successfully for the command: %s "
                              % cmd_to_run, test_case_id, script_id, "None",
                              "None", loglevel, tbd)
                    return True
            else:
                write_log(lib_constants.LOG_WARNING, "WARNING: log failed to "
                          "get generate for command: %s" % cmd_to_run,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
                return False
        else:
            write_log(lib_constants.LOG_WARNING, "WARNING: The execution of "
                      "the command/tool in powershell was unsuccessful & log "
                      "failed to get generated", test_case_id, script_id,
                      "None", "None", loglevel, tbd)
            return  False
    except Exception as e:                                                      #write error msg to log
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %S" % e,
                  test_case_id, script_id, "None", "None",loglevel, tbd)
        return False

################################################################################


def get_led_status(led_code, wait_time, test_case_id, script_id,
                   log_level="ALL", tbd=None):                                  #function to get verify LED status for all SX state

    try:
        aDevice = initialize_ttk()
        counter = lib_constants.ZERO
        s3_port = utils.ReadConfig("ttk", 's3_led')                             # s3_led port fetched from config.ini
        s4_port = utils.ReadConfig("ttk", 's4_led')                             # s4_led port fetched from config.ini
        s5_port = utils.ReadConfig("ttk", 's5_led')                             # s5_led port fetched from config.ini
        sus_port = utils.ReadConfig("ttk", 'sus_led')                           # sus_led port fetched from config.ini

        for sx_port in [s3_port, s4_port, s5_port, sus_port]:                   # if failed to fetch the s3/s4/s5/sus port details from config
            if "FAIL" in sx_port or 'NC' in sx_port.upper() or 'NA' in sx_port:
                write_log(lib_constants.LOG_WARNING, "WARNING: config entry "
                          "for sx port is not proper", test_case_id, script_id,
                          "TTK", "None", log_level, tbd)                        #if failed to get config info, exit
                return False
            else:
                write_log(lib_constants.LOG_INFO, "INFO: config entry for sx "
                          "port %s in config.ini" % sx_port, test_case_id,
                          script_id, "TTK", "None", log_level, tbd)

        while True:
            direc, value = aDevice.getGPIO(0)                                   # current led status fetched from getGPIO() function

            if None != value:
                led_stat = []                                                   # empty list to collect all individual led status
                led_stat.append(int(value[int(s3_port)]))
                led_stat.append(int(value[int(s4_port)]))
                led_stat.append(int(value[int(s5_port)]))
                led_stat.append(int(value[int(sus_port)]))
                convert_first_to_string = (str(w) for w in led_stat)
                final_val = ''.join(convert_first_to_string)

                if led_code == final_val:                                       # if current led status and pre-defined led status matches
                    write_log(lib_constants.LOG_INFO, "INFO: LED status for "
                              "sx state is verified successfully",
                              test_case_id, script_id, "TTK", "None",
                              log_level, tbd)
                    return True
                else:
                    pass
            elif counter > wait_time:                                           # wait till debug-counter time for led check
                write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                          "verify led status for sx state", test_case_id,
                          script_id, "TTK", "None", log_level, tbd)
                return False
            else:
                counter = counter + 1
    except Exception as e:
        write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                  test_case_id, script_id, "TTK", "None", log_level, tbd)
        return False
