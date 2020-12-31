__author__ = "Sushil3x"

###########################General Imports######################################
import os
import time
import string
import subprocess
import shutil
import csv
import dircache
############################Local imports#######################################
import utils
import library
import lib_constants
import lib_apply_workload
import lib_read_temperature
import lib_tool_installation
from lib_constants import *
from winreg import *
from collections import Counter
################################################################################
# Function Name : increasing CPU temperature
# Parameters    : testcaseid, scriptid, original token, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to increasing the CPU temperature
################################################################################

def increasing_cpu_temperature(ori_token,test_case_id,script_id,
                               log_level="ALL",tbd="NONE"):                     # Funtion to increase the CPU temperature

    try:

        ori_token = ori_token.upper()
        ori_token = ori_token.split(' ')

        param1, pos1 = utils.extract_parameter_from_token(ori_token, "OF", "TO")#parm1 extracted from token i.e. CPU
        param2, pos2 = utils.extract_parameter_from_token(ori_token, "TO", "")  #parm2 extracted from token i.e. temperature range 40,50,60

        param2=int(param2)

        if 40 <= param2 < 50:                                                   #If teperature need to be increased in the range of 40 to 50
            ostr= lib_constants.LOAD_40

        elif 50 <= param2 < 60:                                                 #If teperature need to be increased in the range of 50 to 60
            ostr= lib_constants.LOAD_50

        elif 60 <= param2 < 70:                                                 #If teperature need to be increased in the range of 60 to 70
            ostr= lib_constants.LOAD_60

        elif 70 <= param2 < 80:                                                 #If teperature need to be increased in the range of 70 to 80
            ostr= lib_constants.LOAD_70

        elif 80 <= param2 < 90:                                                 #If teperature need to be increased in the range of 80 to 90
            ostr= lib_constants.LOAD_80

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: "                  #If temperature need to be increased to above 90 then its a invalid input
            "Invalid Input Temperature",test_case_id,script_id,"None",
                              "None", log_level, tbd)
            return False

        load_apply = lib_apply_workload.apply_workload(ostr, test_case_id,
                            script_id, loglevel="ALL", tbd=None)                #Apply load to CPU to increase the temperature

        cpu_param1 = lib_constants.CPU_TEMP_PARAM1
        cpu_param2 = lib_constants.CPU_TEMP_PARAM2
        cpu_param3 = lib_constants.CPU_TEMP

        load_temp = get_speed_temp(test_case_id, script_id,
                    param1, cpu_param1, cpu_param2, cpu_param3, log_level, tbd) #to get the CPU temperature

        fan_param1 = lib_constants.FAN_SPEED_PARAM1
        fan_param2 = lib_constants.FAN_SPEED_PARAM2
        fan_param3 = lib_constants.CPU_SPEED

        load_speed = get_speed_temp(test_case_id, script_id,
                    param1, fan_param1, fan_param2, fan_param3, log_level, tbd)

        if 40 <= load_temp < 50:                                                #To check after load temperature is falling under this range or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Temperature is in the Range of 40 to 50 Degree",
            test_case_id, script_id, "None", "None", log_level, tbd)            #print the temperature range message
            return True, load_speed
        elif 50 <= load_temp < 60:                                              #To check after load temperature is falling under this range or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Temperature is in the Range of 50 to 60 Degree",
            test_case_id, script_id, "None", "None", log_level, tbd)            #print the temperature range message
            return True, load_speed
        elif 60 <= load_temp < 70:                                              #To check after load temperature is falling under this range or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Temperature is in the Range of 60 to 70 Degree",
            test_case_id, script_id, "None", "None", log_level, tbd)            #print the temperature range message
            return True, load_speed
        elif 70 <= load_temp < 80:                                              #To check after load temperature is falling under this range or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Temperature is in the Range of 70 to 80 Degree",
            test_case_id, script_id, "None", "None", log_level, tbd)            #print the temperature range message
            return True, load_speed
        elif 80 <= load_temp < 90:                                              #To check after load temperature is falling under this range or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Temperature is in the Range of 80 to 90 Degree",
                              test_case_id,script_id,"None",
                              "None", log_level, tbd)                           #print the temperature range message
            return True, load_speed
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Failed to increase the temperature",
            test_case_id, script_id, "None", "None", log_level, tbd)            #print the message if temperature is not set
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception due to : %s " %e,
                    test_case_id, script_id, "None", "None", log_level, tbd)
        return False                                                            #Exception Message





################################################################################
# Function Name : calculate mode
# Parameters    : numbers
# Return Value  : column number
# Functionality : to get the column number from xl file
################################################################################
def calculate_mode(numbers):                                                    #Function to get the most common number from the list
    c = Counter(numbers)
    mode = c.most_common(1)
    return mode[0][0]


################################################################################
# Function Name : get_row_numb
# Parameters    : testcaseid, scriptid
# Return Value  : row number
# Functionality : to get the row number from xl log
################################################################################
def get_row_numb(test_case_id, script_id, param1, param2, param3, param4,
                 log_level, tbd):                                               #Funtion to get the row number for CPU FAN

    script_id = script_id.strip('.py')
    file_name = script_id + ".csv"                                              #Getting the file Name to be parsed
    os.chdir(lib_constants.SCRIPTDIR)
    dirlist = dircache.listdir(lib_constants.SCRIPTDIR)                         #Getting the list of file in the curent directory

    for i in dirlist:                                                           #Checking the CPU FAN parameter in log file
        if i.upper() == file_name.upper():
            with open (i,'rb') as fp:
                reader = csv.reader(fp)
                index = 0
                for row in reader:
                    for item in row:
                        if param2.upper() in item.upper() and\
                                        param3.upper() in item.upper():         #to check whether FAN Speed Parameter is present in the log or not
                            return index
                        else:
                            index +=1
                fp.close()                                                      #Return the row number

################################################################################
# Function Name : get_fan_speed
# Parameters    : testcaseid, scriptid
# Return Value  : retun FAN speed
# Functionality : to get the cpu fan speed from xl log
################################################################################
def get_speed_temp(test_case_id, script_id, param1, param2, param3, param4,
                   log_level, tbd):                                             #Funtion to get the Speed of CPU FAN

    try:
        row_num = get_row_numb(test_case_id, script_id, param1, param2, param3,
                               param4, log_level, tbd)                          #Get the row number

        if None == row_num:                                                     #to check the row is present or not
            library.write_log(lib_constants.LOG_INFO, "INFO: "
            "Tool log File Doesn't contain the data for %s"%param4,
                              test_case_id, script_id,"None",
                              "None", log_level, tbd)
            return False
        else:
            pass

        script_id = script_id.strip('.py')
        file_name = script_id + ".csv"
        os.chdir(lib_constants.SCRIPTDIR)
        dirlist = dircache.listdir(lib_constants.SCRIPTDIR)                     #Getting the list of file in the curent directory

        speed_temp = []

        for i in dirlist:                                                       #Checking the CPU FAN parameter in log file
            if i.upper() == file_name.upper():
                with open (i,'rb') as fp:
                    reader = csv.reader(fp)
                    for col in reader:
                        if (col[row_num] != None):
                            speed_temp.append(col[row_num])
                    fp.close()

        del speed_temp[0]

        actual = calculate_mode(speed_temp)
        cur_speed_temp = format(actual)
        cur_speed_temp = int(cur_speed_temp)                                    #convert string type to int type
        library.write_log(lib_constants.LOG_INFO, "INFO: "
        "CPU %s is %s"%(param4,cur_speed_temp),test_case_id, script_id, "None",
                              "None", log_level, tbd)
        return cur_speed_temp                                                   #Return the Fan Speed to calling function

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Exception: Due to %s " %e,
                    test_case_id, script_id)
        return False

