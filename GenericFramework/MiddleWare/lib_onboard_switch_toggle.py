__author__ = 'NARESHGX'
############################General Python Imports##############################
import os
############################Local Python Imports################################
import library
import utils
import lib_constants
import os.path
import subprocess
import re
import glob
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations

################################################################################
# Function Name : lib_wifi_device
# Parameters    : token, TC_id is test case id,
#                   script_id is script number
# Return Value  : device id, enable and disable
# Purpose       : To read WI-FI status
# Target        : SUT
################################################################################


def lib_wifi_device_id(token, tc_id, script_id, log_level="All", tbd=None):     # get hw_id function
    try:
        device_id = utils.ReadConfig("wifi","hw_id")                            #print device.name
        if "DEV_" in device_id:                                                 # validate config.ini for hw_id
            device_id = device_id
            r = re.findall('.*?DEV_(\w+)&.*?',device_id)[0]                     #get exact hw_id
            device_id = r.strip()
            if len(device_id) != lib_constants.EIGHT:                           # check if fetched hw_id is proper
                library.write_log(lib_constants.LOG_INFO,"INFO "
                            "Please update config.ini with valid hw_id",tc_id,
                                                      script_id,log_level,tbd)
                return None                                                     # if not found return None
            return "DEV_"+str(device_id)                                        # return hw_id
        else:
            library.write_log(lib_constants.LOG_ERROR,"ERROR "
            "please update config.ini with hw_id",tc_id,script_id,log_level,tbd)
            return None                                                         # if not found return None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"Error: Unable to Execute"    # if result.ini doesn't contain the valid file then exception
            "'%s'"%e,tc_id,script_id,"None","None",
                              log_level, tbd)
        return None                                                             #return None if exception found


################################################################################
# Function Name : lib_wifi_toggle_status
# Parameters    : device_id, tc_id, script_id, log_level="All",tbd=None
# Return Value  : device id, enable and disable
# Purpose       : To check switch toggle status
# Target        : SUT
################################################################################


def lib_wifi_toggle_status(device_id, tc_id, script_id, log_level="All",
                                                              tbd=None):        # get current wifi status
    try:
        log_path = script_id.replace(".py", "_status.log")                      # status log path set
        log_path = os.path.join(lib_constants.SCRIPTDIR,log_path)
        devcon_path = utils.ReadConfig("Install_drivers","devcon_path")         # get devcon path from config.ini
        devcon_exe = devcon_path+"\\"+"*dev*64*"
        devcon_exe = glob.glob(devcon_exe)[0]
        command = str(devcon_exe)+" status "+"*"+str(device_id)+"* > "+log_path # create a command for execution
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        exec_out = p.communicate()[0]
        fopen = open(log_path,'r')                                              # read log file for status
        for i in fopen:
            if "Driver is running" in i:                                        # status for enable
                return "Enable"
            elif "Device is disabled" in i:                                     # staua for disable
                return "Disable"
            else:
                pass
        library.write_log(lib_constants.LOG_ERROR,"ERROR no status log"
                                  ,tc_id,script_id,log_level,tbd)
        return None

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"Error: Unable to Execute"    # if result.ini doesn't contain the valid file then exception
            "'%s'"%e,tc_id,script_id,"None","None",
                              log_level, tbd)
        return None                                                             #return None if exception found


################################################################################
# Function Name : lib_wifi_toggle_change
# Parameters    : device_id, tc_id, script_id, log_level="All",tbd=None
# Return Value  : device id, enable and disable
# Purpose       : To toggle switch
# Target        : SUT
################################################################################


def lib_wifi_toggle_change(device_id,current_status, tc_id, script_id,          # function for toggle
                           log_level="All", tbd=None):
    try:
        log_path = script_id.replace(".py", "_toggle.log")                      # log file path for toggle
        log_path = os.path.join(lib_constants.SCRIPTDIR,log_path)
        devcon_path = utils.ReadConfig("Install_drivers","devcon_path")         # get devcon path
        devcon_exe = devcon_path+"\\"+"*dev*64*"
        devcon_exe = glob.glob(devcon_exe)[0]
        if "Enable" == current_status :
            command = str(devcon_exe)+" disable "+"*"+str(device_id)+"* > "+\
                      log_path                                                  # execution command set for disable
        else:
            command = str(devcon_exe)+" enable "+"*"+str(device_id) +"* > "+\
                      log_path                                                  # execution command set for enable
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE)   # run command in subprocess
        exec_out = p.communicate()[0]
        fopen = open(log_path,'r')
        for i in fopen:                                                         # check log file
            if "device(s) disabled" in i :                                      # check log for disable
                return "Disabled"
            elif "device(s) enabled" in i:                                      # check log for enable
                return "Enable"
            else:
                pass
        library.write_log(lib_constants.LOG_ERROR,"ERROR no status log"
                                  ,tc_id,script_id,log_level,tbd)
        return None

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"Error: Unable to Execute"    # if result.ini doesn't contain the valid file then exception
            "'%s'"%e,tc_id,script_id,"None","None",
                              log_level, tbd)
        return None                                                             #return None if exception found

################################################################################
# Function Name : lib_onboard_switch_toggle
# Parameters    : switch type, token, test case id,
#                   script_id is script number
# Return Value  : True or False
# Purpose       : To read Switch status and toggle
# Target        : HOST
################################################################################


def lib_onboard_switch_toggle(switch_type, test_case_id, script_id, log_level,
                              tbd):

    gpiopin_value = False
    relay_status = False
    try:
        port_no = utils.ReadConfig("TTK", switch_type)
        if lib_constants.STR_FAIL in switch_type:
            library.write_log(lib_constants.LOG_WARNING,
                              "Failed to parse relay details from config file",
                              test_case_id, script_id, log_level, tbd)
            return False
        gpiopin_value = lib_ttk2_operations.get_ttk2_gpio_status(port_no,
                                                                 test_case_id,
                                                                 script_id,
                                                                 log_level, tbd)
        if not gpiopin_value:
            relay_status_on = lib_ttk2_operations.ttk2_set_relay("ON", int(port_no),
                                                                  test_case_id,
                                                              script_id, log_level,
                                                              tbd)
            relay_status_off = lib_ttk2_operations.ttk2_set_relay("OFF", int(port_no),
                                                              test_case_id,
                                                              script_id, log_level,
                                                              tbd)
            if relay_status_off is True and relay_status_on is True:
                library.write_log(lib_constants.LOG_INFO,
                                  "Toggling of %s through ttk port num %s is "
                                  "successful " % (switch_type, port_no),
                                  test_case_id, script_id, log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_FAIL,
                                  "Toggling of %s through ttk port num %s is "
                                  "unsuccessful " % (switch_type, port_no),
                                  test_case_id, script_id, log_level, tbd)
                return False

        elif not gpiopin_value:
            relay_status = lib_ttk2_operations.ttk2_set_relay("ON", int(port_no),
                                                              test_case_id,
                                                              script_id, log_level,
                                                              tbd)
            if relay_status:
                library.write_log(lib_constants.LOG_INFO,
                                  "Toggling of %s through ttk port num %s is "
                                  "successful " % (switch_type, port_no),
                                  test_case_id, script_id, log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_FAIL,
                                  "Toggling of %s through ttk port num %s is "
                                  "unsuccessful " % (switch_type, port_no),
                                  test_case_id, script_id, log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "Failed to get the relay port no: %s" % port_no,
                              test_case_id, script_id, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "Error: Unable to perform toggle action '%s'" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


