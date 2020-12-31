__author__ = 'kapilshx'
###########################General Imports######################################
import time
import os
import string
############################Local imports#######################################
import library
import lib_constants
import utils
import lib_connect_disconnect_power_source
################################################################################
# Function Name : set_virtual_battery_mode
# Parameters    : virtual_token,test case id,script id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : to set the virtual battery mode
#################################################################################
def set_virtual_battery_mode(virtual_token,test_case_id,script_id,
                                                    loglevel="ALL",tbd=None):
    try:
        if lib_connect_disconnect_power_source.\
            connect_disconnect_power_ttk("DC","DISCONNECT",test_case_id, script_id,
                             loglevel,tbd):                                     #library calls to disconnect the DC power supply & DC signal
            time.sleep(lib_constants.SHORT_TIME)
            library.write_log(lib_constants.LOG_INFO,"INFO: Real battery"
                " disconnected successfully from SUT",test_case_id,
                script_id,"TTK","setGPIO()",loglevel,tbd)                       #write pass msg to log
            pass
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL:Failed to "
                "disconnect real battery from SUT",test_case_id,
                        script_id,"TTK","setGPIO()",loglevel,tbd)               #write fail msg to log
            return False
        button = "VIRTUAL BATTERY"
        try:
            relay = utils.ReadConfig("TTK",button)                              # Read Relay details for the button name
            if "FAIL:" in relay:
                library.write_log(lib_constants.LOG_WARNING,"WARNING : Config"
                    " entry missing for relay", test_case_id, script_id,
                                  "None", "None", loglevel, tbd)                # write info msg to log
                return False
            elif relay != "NC":
                library.write_log(lib_constants.LOG_INFO,"INFO: %s button "
                    "rework is connected to Relay number %s in "
                    "TTK"%(button,relay), test_case_id,
                                  script_id, "None", "None", loglevel, tbd)     #if config entry has 'NC' as the entry means the particular
            else:                                                               #rework is not connected,script will exit here
                library.write_log(lib_constants.LOG_ERROR,"ERROR : %s button "
                    "rework not connected to TTK relay"%(button),
            test_case_id, script_id,"None", "None", loglevel, tbd)              # write error msg to log
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR :Config entry not "
            "found for %s"%(button), test_case_id, script_id, "Config.ini",str(e),
                              loglevel, tbd)                                    #If config entry is not present, exception will be handled here
            return False
        try:
            if "DC" in  virtual_token:
                press = library.ttk_set_relay('ON',int(relay), test_case_id, script_id)                #Pressing the button using ttk
            elif "AC" in virtual_token:
                press = library.ttk_set_relay('OFF',int(relay), test_case_id, script_id)               #Pressing the button using ttk
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Input Syntax"
                    " is incorrect",test_case_id, script_id,"None", "None",
                                  loglevel, tbd)                                # write error msg to log
                return False
            if 0 == press:                                                      #If any return value of Press 1 ,then press action is Fail
                library.write_log(lib_constants.LOG_INFO,"INFO: Pressing %s "
                    "button is successful"%(button), test_case_id, script_id,
                                  "None", "None", loglevel,tbd)                 #Return value of aDevice.setGPIO() is 0 means success
                return True
            else:
                library.write_log(lib_constants.LOG_ERROR,"ERROR: TTK Press "
                    "button action failed",test_case_id,script_id,"TTK",
                                  "setGPIO()",loglevel,tbd)                     # write error msg to log
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
                              "performing TTK action",test_case_id, script_id,
                              "TTK",str(e),loglevel,tbd)                        #Any ttk exception is handled here
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "get_virtual_battery_charge library function due to %s."%e,
            test_case_id, script_id,"None", "None", loglevel, tbd)              # write error msg to log
        return False
################################################################################
