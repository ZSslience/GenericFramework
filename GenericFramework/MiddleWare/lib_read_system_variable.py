__author__ = 'Deepak\kapilshx'
###########################Local library imports################################
import lib_tat_tool_installation
import lib_constants
import library
import lib_constants
import utils
################################################################################
###########################General library imports##############################
import os
import sys
import time
import csv
import configparser
import shutil
################################################################################

################################################################################
# Function Name : read_system_variable
# Parameters    : token- variable_name
#                 tc_id-test case ID, script_id,
# Functionality : Pull all the latest TAT values and verify the mentioned system
#                 variable
# Return Value  : 'value on successful \
#                  and 'False' on failure
################################################################################

def read_system_variable(variable_name,step_number,tc_id,script_id,
                         log_level="ALL", tbd="None"):
    try:
        if "CPU-FREQUENCY(MHZ)" in variable_name.upper():
            variable_name = "cpu0-frequency(mhz)"
        else:
            pass
        if "None" == step_number:
            Install_Status=lib_tat_tool_installation.tat_tool_installation\
                (tc_id,script_id,log_level,tbd)                                 # TAT tool installation check
            if Install_Status :                                                 #if installation success print info to log file else return false
                library.write_log(lib_constants.LOG_INFO,"INFO :"
                                  "TAT tool installation sucessfull",
                                tc_id,script_id,"None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING,"WARNING :"
                                  "TAT tool installation Fail",
                                tc_id,script_id, "None", "None", log_level, tbd)
                return False
            ToolDir = utils.ReadConfig("TAT_TOOL","installedpath")              #Get tool directory of TAT tool from config file
            cmdexe = utils.ReadConfig("TAT_TOOL","Run_Cmd")                     #Get command for executing from config file
            for item in [ToolDir,cmdexe]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_INFO, "INFO : "
                        "Config entry for ToolDir or cmdexe is missing",
                        tc_id,script_id, "None", "None", log_level, tbd)
                    return False                                                #If any of the config entry is missing return false
                else:
                    pass

            os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)                        #change directory to tat tool path
            os.system(lib_constants.DELETE_CSV_FILE)                            #deleteting existing log
            time.sleep(lib_constants.FIVE_SECONDS)
            os.chdir(ToolDir)                                                   #change directory to tat tool directory
            filelist = [csvfile for csvfile in os.listdir('.')
                        if csvfile.endswith(".csv")                             #Find all the existing TATMonitor csv file
                        and csvfile.startswith("TATMonitor")]
            for csvfile in filelist:
                os.remove(csvfile)                                              #Remove all the existing TATMonitor csv file
            cmd = cmdexe+" -AL"+" -t="+str(lib_constants.TAT_EXE)\
                  +" -p="+str(lib_constants.TAT_POL)                            #Store the command to run in a variable which will run the tat tool
            value=os.system(cmd)                                                #Run the system command to generate log file for TAT
            time.sleep(lib_constants.TWENTY)
            time.sleep(lib_constants.TEN)
            if(0==value) or (1==value):
                library.write_log(lib_constants.LOG_INFO,"INFO :"               #Check the condition for executed command to generate log file
                        "TAT command execution successful",
                           tc_id,script_id, "None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO :"
                        " TAT command execution not successful",
                            tc_id,script_id,"None", "None",log_level, tbd)
                return False

            latesttatfile = script_id.replace(".py","_log.csv")                 #log file
            try:
                os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)                    #change directory to tat tool result path
                for file in os.listdir(lib_constants.TAT_TOOL_RESULT_PATH):
                    file_name,file_ext = os.path.splitext(file)
                    os.rename(lib_constants.TAT_TOOL_RESULT_PATH+"\\"+file_name
                              + ".csv",lib_constants.TAT_TOOL_RESULT_PATH+"\\"+
                              latesttatfile)                                    #rename log with script_id
                shutil.copy(lib_constants.TAT_TOOL_RESULT_PATH+"\\"+"\\"+
                            latesttatfile,lib_constants.SCRIPTDIR )             #copy log file to script directory
            except Exception as e:
                library.write_log(lib_constants.LOG_INFO, "INFO: Unable to "
                "Apply Workload due to %s."%e, tc_id, script_id, "None",
                          "None", log_level,tbd)                                #exception
                return False

        else:
            step_gen_log = utils.read_from_Resultfile(step_number)
            latesttatfile = str(step_gen_log.split("\\")[-1])

        column_number = library.find_column_number(latesttatfile,variable_name,
                                tc_id,script_id,log_level, tbd)                 #Calling library function to find the column number of matching grammar
        if column_number :                                                      #if condition satisfied return true or return false
            library.write_log(lib_constants.LOG_INFO,"INFO :"
                    "Found matching system variable in TATMonitor file",
                              tc_id,script_id,"None","None",log_level,tbd)

        else:
            library.write_log(lib_constants.LOG_INFO,"INFO :"
                "Can not able to find TATMonitor log file or matching system "
                "variable in TATMonitor log file",tc_id,script_id,"None","None",
                              log_level,tbd)

            return False
        if "CPU0-FREQUENCY(MHZ)" in variable_name.upper():
            gen_system_value = get_system_value_cpu_frequency(latesttatfile,
                        column_number,tc_id,script_id,log_level, tbd)               #Calling library function for find the system variable
        else:
            gen_system_value = library.get_system_value(latesttatfile,
                        column_number,tc_id,script_id,log_level, tbd)               #Calling library function for find the system variable

        if gen_system_value :                                                   #if condition satisfied return true or return false
            library.write_log(lib_constants.LOG_INFO,"INFO :"
                "Pass value of system variable from TATMonitor file present in "
                "result file",tc_id,script_id,"None","None",log_level,tbd)
            return str(gen_system_value) + "'d"
        else:

            library.write_log(lib_constants.LOG_INFO,"INFO :"
                "Fail to get the system variable from TATMonitor log file"
                              ,tc_id,script_id,"None","None",log_level,tbd)
            return False
    except Exception as e:                                                      #throw exception if all above condition fail
        library.write_log(lib_constants.LOG_ERROR, "Exception : %s " %e,
                    tc_id,script_id, "None", "None", log_level, tbd)
#######################################################################
# Function name   : get_system_value_cpu_frequency
# Parameters      : file_name = .csv file name to be parsed,
#                   column_number = column number to be parsed
# Returns         : average value .
# Dependent Functions: os, sys, csv, utils imports included.
#######################################################################

def get_system_value_cpu_frequency(file_name, column_name,tc_id,script_id,
                                log_level="ALL", tbd="None"):
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
                                if 'Invalid' == col :
                                    col = 0
                            Required_List.append(col)                           #creating list of the found values in matching coloumn
                        colnum = colnum + 1
                rownum+=1
        validate_list = [item.isdigit()for item in Required_List]               #Validate if required col is integer
        if False in validate_list:
            return max(Required_List)
        else:
            if (max(Required_List)== '0'):
                 return str(max(Required_List))
            else:
                Required_List = list(map(int, Required_List))                         # Convert values in Required_List to int
                return float(max(Required_List))
    except Exception as e:                                                      #Exeption throw if fail to get avrage value
     library.write_log(lib_constants.LOG_ERROR,"ERROR : Exception occurs"
" in get_system_value_cpu_frequency() function Due to %s "%e,tc_id,script_id,
            "None","None",log_level, tbd)
     return False
#######################################################################