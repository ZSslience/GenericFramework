__author__ = 'singhd1x'

############################General Python Imports##############################
import glob
import re
import subprocess
from win32com.client import GetObject
############################Local Python Imports################################
import library
import lib_constants
import utils
################################################################################
# Function Name     : display_brightness
# Parameters        : tc_id, script_id, device, loglevel, tbd
# Functionality     : function to get current Brightness level
# Return Value      : Brightness level(if pass), False(if fail)
################################################################################
def display_brightness(device, tc_id, script_id, log_level = "ALL", tbd = None):
    try:
        objWMI = GetObject('winmgmts:\\\\.\\root\\WMI').\
            InstancesOf('WmiMonitorBrightness')                                 #defining object file of WMI
        for obj in objWMI:                                                      #checking for current brightness in WMI object
            if obj.CurrentBrightness != None:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Successfully got the current brightness of %s as %s"
                                  % (device, str(obj.CurrentBrightness)), tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return str(obj.CurrentBrightness)                               #Return the present value of current brightness
            else:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: Failed to get the current brightness of %s"
                                  % device,
                                  tc_id, script_id, "None", "None", log_level, tbd)
            return False                                                        #else return false

    except Exception as e:                                                      #error thrown from here
         library.write_log(lib_constants.LOG_ERROR,"ERROR: " +str(e),
                          tc_id,script_id,log_level,tbd)
################################################################################
# Function Name     : connected_display
# Parameters        : tc_id, script_id, loglevel, tbd
# Functionality     : function to return  connected display
# Return Value      : Display name
################################################################################
def connected_display(device,tc_id,script_id,log_level = "ALL",tbd = None):

    try:
        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")
        cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")                         #Read the tools directory path from the config and store in tool_dir
        for data in [tool_dir,cmd_to_run]:
            if "FAIL:" in data:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config value is"
                " missing in 'DISPLAY' section", tc_id,
                              script_id, "None", "None",log_level, tbd)
                return False
        else:
            pass
        library.write_log(lib_constants.LOG_INFO, "INFO: Checking for Connected"
                          " display device", tc_id, script_id, "None",
                          "None", log_level, tbd)
        utils.filechangedir(tool_dir)                                           #set controller to tools directory
        process = subprocess.Popen(cmd_to_run, shell=True,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()                                                          #Executing the command to get the connected display device
        process_output = process.communicate()
        if  0 == process_output :                                               #if command is unsuccessfully
            library.write_log(lib_constants.LOG_INFO, "INFO: Empty file created"
                        " fail to write the display information" , tc_id,
                         script_id, "None", "None",log_level, tbd)
            return False                                                        #return "False"
        else:
            file = glob.glob("DisplayInfo.txt")                                 #check for displayinfo.txt in the directory
            if [] == file:                                                      #if file is empty
                return False                                                    #return "false"
            else:
                utils.filechangedir(tool_dir)                                   #change to tools directory where tool is kept
                with open("DisplayInfo.txt","r") as displayfile:                #file operation open file in utf-8 mode and save the texts in handle
                    filetext = displayfile.read()
                    displayfile.close()
                display_matches = re.findall("HDMI|EDP|DP|MIPI", filetext)      #regular expression for checking different display type
                found_display_list = set(display_matches)                       #creating set of found different display type
                name = " "                                                      #checking for empty string.
                for name in found_display_list:                                 #looping through the list for find matching name
                    if name.upper() == device.strip().upper():                  #If match
                        pass                                                    # do noting
                    break                                                       #break the loop
                return name                                                     #name parameter
    except Exception as e:                                                      #error thrown from here
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
                    tc_id, script_id, "None", "None", log_level, tbd)
        return False

