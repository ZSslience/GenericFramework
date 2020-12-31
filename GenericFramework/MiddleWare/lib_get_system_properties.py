__author__ = 'jkmody'
########################## General Imports #####################################
import os
from subprocess import Popen, PIPE
from win32api import GetSystemMetrics
import codecs
import datetime
import wmi
########################## Local Imports #######################################
import lib_constants
import utils
import library
################################################################################
#   Function name   : get_screen_brightness()
#   description     : Code to get current Brightness level
#   parameters      : 'tc_id' is test case id
#                     'script_id' is script id
#   Returns         : Brightness level(if pass), False(if fail)
######################### Main script ##########################################

def get_screen_brightness(test_case_id, script_id,log_level,tbd):
    try:
        cmd= 'powercfg -query > powercfg_log.txt'
        os.system(cmd)
        with open("powercfg_log.txt",'r') as log:
            data=log.readlines()
        os.remove("powercfg_log.txt")
        for i in range(len(data)):
            if "(Display brightness)" in data[i]:
                brightness_ac=data[i+5][-3:].strip()
                brightness_dc=data[i+6][-3:].strip()
        WMIobj = wmi.WMI()
        battery = WMIobj.query("SELECT Availability FROM Win32_Battery")
        if battery:
            for values in battery:
                power_mode= values.Availability
        if lib_constants.AC_MODE == power_mode:                                 #Checking if SUT is in AC mode
            library.write_log(lib_constants.LOG_INFO, "INFO : System is in AC "
                              "power mode",test_case_id,script_id, "None",
                              "None", log_level, tbd)                           #Write the information to the log
            return str(int(brightness_ac,16))
        elif lib_constants.DC_MODE == power_mode:                               #Checking if SUT is in DC mode
            library.write_log(lib_constants.LOG_INFO, "INFO : System is in DC "
                              "power mode",test_case_id,script_id, "None",
                              "None", log_level, tbd)                           #Write the information to the log
            return str(int(brightness_dc,16))
        else:
            return "False"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception : %s " %e,
            test_case_id,script_id, "None", "None", log_level, tbd)             #Write the execption error to the log
        return "False"


################################################################################
#   Function name   : get_screen_resolution()
#   description     : Code to get current Resolution level
#   parameters      : 'tc_id' is test case id
#                     'script_id' is script id
#   Returns         : Screen Resolution(if pass), False(if fail)
######################### Main script ##########################################

def get_screen_resolution(test_case_id, script_id,log_level,tbd):
    try:
        if GetSystemMetrics(0) != None and GetSystemMetrics(1) != None:
            screen_width = GetSystemMetrics(0)                                  #getting the screen width
            screen_height = GetSystemMetrics(1)                                 #getting the screen height
            return str(screen_width) + " X " + str(screen_height)               #returning screen resolution
        else:
            return "False"

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception : %s " %e,
            test_case_id,script_id, "None", "None", log_level, tbd)             #Write the execption error to the log
        return "False"


################################################################################
#   Function name   : get_audio_level()
#   description     : Code to get current Audio level
#   parameters      : 'tc_id' is test case id
#                     'script_id' is script id
#   Returns         : Audio level(if pass), False(if fail)
######################### Main script ##########################################

def get_audio_level(test_case_id, script_id,log_level,tbd):
    try:
        tool_path = lib_constants.TOOLPATH + "\\soundvolumeview-x64"
        os.chdir(tool_path)
        device_name = utils.ReadConfig("AUDIO","Device")
        command = "SoundVolumeView.exe /stext log.txt"                          #command for generating the log for SoundVolumeView.exe
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if len(stderr) > 0:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to get the"
              " Current Audio Level ",test_case_id,script_id, "None", "None",
                              log_level, tbd)                                   #Write the error to the log
            return "False"
        else:
            os.chdir(tool_path)
            with codecs.open("log.txt", "r", "UTF-16") as file:                 #Parsing the log file generated through SoundVolumeView.exe
                data=file.readlines()
            for line in range(len(data)):
                if (device_name.lower() in data[line].lower()):
                    if "Device" in data[line+1]:
                        return str(data[line+6].split(":")[1].strip().replace("%",""))          #returning system volume
                    else:
                        pass
                else:
                    pass
            library.write_log(lib_constants.LOG_INFO, "INFO: "
                              "No Audio Device is Installed",test_case_id,
                                    script_id,"None", "None",log_level, tbd)
            return "False"

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception : %s " %e,
            test_case_id,script_id, "None", "None", log_level, tbd)             #Write the execption error to the log
        return "False"

################################################################################
#   Function name   : get_system_time()
#   description     : Code to get current Audio level
#   parameters      : 'tc_id' is test case id
#                     'script_id' is script id
#   Returns         : system time(if pass), False(if fail)
######################### Main script ##########################################

def get_system_time(test_case_id,script_id,log_level,tbd):
    try:
        system_time=str(datetime.datetime.now())                                #Getting the current time
        system_time=system_time.split(" ")

        if int(system_time[1].split(".")[0].split(":")[0])<24:
            system_time=system_time[1].split(".")[0]
            return system_time
        else:
            return "False"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception : %s " %e,
            test_case_id,script_id, "None", "None", log_level, tbd)             #Write the execption error to the log
        return "False"

################################################################################
#   Function name   : get_system_properties()
#   description     : Code to get the system properties
#   parameters      : 'tc_id' is test case id,'script_id' is script id,
#                     'ostr' is step,'log_level' is log level to print
#   Returns         : property name,property value(if Pass),False(if Fail)
######################### Main script ##########################################

def get_system_properties(test_case_id,script_id ,ostr , log_level ,tbd):
    token=utils.ProcessLine(ostr)
    property_name=' '.join(token[2:])
    if ("audio level" in property_name.lower()) or ("volume" in
                                                        property_name.lower()):
        result=get_audio_level(test_case_id,script_id,log_level,tbd)            #calling the function for getting system volume
        return result,property_name

    elif ("brightness" in property_name.lower()):
        result=get_screen_brightness(test_case_id,script_id,log_level,tbd)      #calling the function for getting screen brightness
        return result,property_name

    elif ("resolution" in property_name.lower()):
        result=get_screen_resolution(test_case_id,script_id,log_level,tbd)      #calling the function for getting screen resolution
        return result,property_name

    elif ("time" in property_name.lower()):
        result=get_system_time(test_case_id,script_id,log_level,tbd)            #calling the function for getting system time
        return result,property_name
    else:
        return "False",property_name