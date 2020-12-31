__author__ = 'singhd1x'

############################General Python Imports##############################
import wmi
import glob
import re
import subprocess
import os
import time
import codecs

############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_check_brightness_of_display_device
import lib_plug_unplug
################################################################################
# Function Name     : change_brightness
# Parameters        : tc_id, script_id, device, loglevel, tbd
# Functionality     : function to get change Brightness level
# Return Value      : Brightness level(if pass), False(if fail)
################################################################################
def change_brightness(inc_dec,display,brightness_per,script_id,tc_id,
                      log_level = "ALL",tbd = None):
    try:
        present_brightness1 = lib_check_brightness_of_display_device.\
            display_brightness(display, tc_id, script_id, log_level, tbd="None")#Calling display brightness library to check for current brightness of display

        if (int(brightness_per)> lib_constants.BRIGHTNESS_NEG_CHECK and \
                    int(brightness_per) <= lib_constants.BRIGHTNESS_MAX_VALUE): #Checking for the brightness percentage max value
            if int(brightness_per)== int(present_brightness1):                  #Checking if input is matching with present brightness of display
                library.write_log(lib_constants.LOG_INFO,"INFO: Verified the "
                    "current brightness is same as input %s hence exiting as "
                    "success"%(brightness_per),script_id,tc_id, "None","None",
                                  log_level, tbd)
                return True
            else:
                c = wmi.WMI(namespace='wmi')                                    #Creating wmi object
                methods = c.WmiMonitorBrightnessMethods()[0]                    #Calling "WmiMonitorBrightnessMethods" method
                methods.WmiSetBrightness(brightness_per, 0)                     #Calling "WmiSetBrightness" method and passing the percentage value

                library.write_log(lib_constants.LOG_INFO,"INFO: Brightness "
                "of device %s, %s by %s "%(display,inc_dec,brightness_per),
                                script_id,tc_id, "None","None",log_level, tbd)
            present_brightness2 = lib_check_brightness_of_display_device. \
                display_brightness(tc_id, script_id, log_level,
                                   tbd)                                         #Calling display brightness library to check for current brightness of display
            if "INCREASE" == inc_dec.upper():
                if int(present_brightness2) >= int(present_brightness1):
                    library.write_log(lib_constants.LOG_INFO,"INFO: Verified the "
                        "current brightness. It has been modified to %s"%
                        (brightness_per),script_id,tc_id, "None","None",
                                      log_level, tbd)
                    return True                                                 #If change return true
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Verified the "
                        "actual brightness. It does not match with the modified %s"
                        " percentage"%(brightness_per),script_id,tc_id, "None",
                                      "None",log_level, tbd)
                    return False
            else:
                if int(present_brightness2) <= int(present_brightness1):
                    library.write_log(lib_constants.LOG_INFO,"INFO: Verified the "
                        "current brightness. It has been modified to %s"%
                        (brightness_per),script_id,tc_id, "None","None",
                                      log_level, tbd)
                    return True                                                 #If change return true
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Verified the "
                        "actual brightness. It does not match with the modified %s"
                        " percentage"%(brightness_per),script_id,tc_id, "None",
                                      "None",log_level, tbd)
                    return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Failed to %s  "
                "the brightness of display %s "%(inc_dec,display),tc_id,
                              script_id, "None","None",log_level, tbd)
            return False                                                        #else return false

    except Exception as e:                                                      #error thrown from here
         library.write_log(lib_constants.LOG_DEBUG,"DEBUG: " +str(e),
                          script_id,tc_id,log_level,tbd)
################################################################################
# Function Name     : connected_display
# Parameters        : device, tc_id, script_id, loglevel, tbd
# Functionality     : function to return  connected display
# Return Value      : Display name
################################################################################
def connected_display(device,script_id,tc_id,log_level = "ALL",tbd = None):

    try:
        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")
        cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")                         #Read the tools directory path from the config and store in tool_dir
        for data in [tool_dir,cmd_to_run]:
            if "FAIL:" in data:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config value is"
                " missing in display section", script_id,tc_id, "None",
                                  "None",log_level, tbd)
                return False
        else:
            pass
        library.write_log(lib_constants.LOG_INFO, "INFO: Checking for Connected"
                          " display device", script_id,tc_id, "None",
                          "None", log_level, tbd)
        utils.filechangedir(tool_dir)                                           #set controller to tools directory
        process = subprocess.Popen(cmd_to_run,shell=True,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()                                                          #Executing the command to get the connected display device
        process_output = process.communicate()
        if process_output == 0:                                                 #if command is unsuccessfully
            library.write_log(lib_constants.LOG_INFO, "INFO: Empty file created"
                        " fail to write the display information" , script_id,
                              tc_id, "None", "None",log_level, tbd)
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
                        pass                                                    #do nothing
                    break                                                       #break the loop
                return name                                                     #name parameter
    except Exception as e:                                                      #error thrown from here
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
                    script_id,tc_id, "None", "None", log_level, tbd)
        return False

