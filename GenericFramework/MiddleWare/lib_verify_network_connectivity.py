__author__ = "bchowdhx\Sushil3x"

##############################General Library import############################
import os
import wmi
import time
import re
import subprocess
##############################Local libary import###############################
import library
import lib_constants
import utils
import lib_verify_device_enumeration
import lib_plug_unplug
import lib_boot_to_environment
################################################################################

################################################################################
# Function Name : verify_network_connectivity
# Parameters    : test_case_id is test case number, script_id is script_number,
#                  dev_name is device name, dev_prop is device property
# Functionality : verify network connectivity for lan/wi-fi
# Return Value  : 'True' on successful action and 'False' on failure
# UDL Parameter : LAN, WIFI
################################################################################

def verify_network_connectivity(token, test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        token = token.split(" ")
        con_type, pos1 = utils.\
            extract_parameter_from_token(token, "VERIFY", "CONNECTIVITY")

        if "LAN" in con_type.upper():
            device = 'onboard'
            status, result = lib_plug_unplug.read_devcon_ip_address\
                (device, test_case_id, script_id, log_level, tbd)

            if status == True:                                                  #checking status pass or fail , whether wifi is connected to SUT or not
                library.write_log(lib_constants.LOG_INFO,"INFO: LAN "
                "is Connected to IP %s"%result, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #return True if available
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: LAN "
                "is not connected", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # else return false
                return False

            hostip = utils.ReadConfig("WIFI","host_ip")                         # host ip is extracted from config.ini
            if "FAIL:" in hostip:
                library.write_log(lib_constants.LOG_INFO, "INFO: Host IP  "
                                                          "not found in config.ini",
                                  test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            lan_ping = library.check_connectivity \
                (hostip, test_case_id, script_id, log_level="ALL",
                 tbd=None)                                                          # function calling for check connectivity

            if lan_ping == True:                                                   # checking status pass or fail , whether wifi is ping to Server or not
                library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                                          "Connectivity is verified" % con_type,
                                  test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                                                          "verify %s connectivity" % con_type,
                                  test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        elif "WIFI" in con_type.upper():

            status, result = lib_plug_unplug.read_devcon_ip_address\
                (con_type, test_case_id, script_id, log_level, tbd)             #Function to check the wifi connectivity

            if status == True:                                                  #checking status pass or fail , whether wifi is connected to SUT or not
                library.write_log(lib_constants.LOG_INFO,"INFO: WIFI "
                "is Connected", test_case_id, script_id,
                "None", "None", log_level, tbd)
                                                                                #return True if available
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: WIFI "
                "is not connected", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # else return false
                return False

        library.write_log(lib_constants.LOG_INFO, "INFO: 1.Connected to WiFI"
                "2.LAN is Disable 3.WiFi Connectivity is going to checked",
                test_case_id, script_id,"None", "None", log_level, tbd)

        os.system('netsh interface show interface > lan_wifi.txt')
        with open('lan_wifi.txt','r') as f:
            stdout = f.read()
            list = re.findall('.*(ETHERNET(.\d)?).*',stdout,re.I)
            list = [x[0] for x in list]

            for item in range(len(list)):
                item = '\"' + list[item] + '\"'
                cmd = lib_constants.ETHDIS_PARAM1 + ' ' +  item  + ' ' + lib_constants.ETHDIS_PARAM2
                os.system(cmd)
                time.sleep(lib_constants.SHORT_TIME)

        os.system(lib_constants.WIFI_ENABLE)
        time.sleep(lib_constants.SHORT_TIME)

        serverip = utils.ReadConfig("WIFI","server_ip")                         # server ip is extracted from config.ini
        if "FAIL:" in serverip:
            library.write_log(lib_constants.LOG_INFO,"INFO: Server IP  "
            "not found in config.ini", test_case_id, script_id,
            "None", "None", log_level, tbd)
            return False

        wifi_ping = library.check_connectivity\
            (serverip, test_case_id, script_id, log_level="ALL", tbd=None)      # function calling for check connectivity

        if wifi_ping == True:                                                   #checking status pass or fail , whether wifi is ping to Server or not
            library.write_log(lib_constants.LOG_INFO,"INFO: %s "
            "Connectivity is verified"%con_type, test_case_id, script_id,
            "None", "None", log_level, tbd)
            os.system(lib_constants.WIFI_DISABLE)
            time.sleep(lib_constants.SHORT_TIME)

            os.system('netsh interface show interface > lan_wifi.txt')
            with open('lan_wifi.txt', 'r') as f:
                stdout = f.read()
                list = re.findall('.*(ETHERNET(.\d)?).*', stdout, re.I)
                list = [x[0] for x in list]

                for item in range(len(list)):
                    item = '\"' + list[item] + '\"'
                    cmd = lib_constants.ETHEN_PARAM1 + ' ' + item + ' ' + lib_constants.ETHEN_PARAM2
                    os.system(cmd)
                    time.sleep(lib_constants.SHORT_TIME)

            os.system(lib_constants.WIFI_ENABLE)
            time.sleep(lib_constants.SHORT_TIME)

            library.write_log(lib_constants.LOG_INFO, "INFO: 1.1.Dis-connected "
                    "to WiFI 2.LAN is Enable",
                    test_case_id, script_id, "None", "None",log_level, tbd)

            return True
                                                                                 #return True if successful else return false
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "verify %s connectivity" % con_type,test_case_id, script_id,
            "None", "None", log_level, tbd)
            return False



    except Exception as e:                                                      # exception handled
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception is  %s"%e,
        test_case_id, script_id)
        return False




################################################################################