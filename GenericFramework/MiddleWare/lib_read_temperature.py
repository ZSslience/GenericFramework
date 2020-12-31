__author__ = 'anilxpatnaik\kashokax\yusufmox'

############################General Python Imports##############################
import os
import glob
import time
import shutil
import subprocess
import csv
from winreg import *
############################Local Python Imports################################
import utils
import library
import lib_constants
import lib_tool_installation
################################################################################
# Function Name : lib_read_temperature
# Parameters    : test_case_id-test case ID, script_id  - script ID,
#                 comp-component name e.g. CPU/PCH , PECI , token
# Purpose       : return temperature value of CPU/PCH or cpu package temperature
# Return Value  : returns temperature value of CPU or cpu package temperature on
#                 successful action or 'False' on failure
# Syntax        : read the temperature of <component>
#               : Get CPU package temperature using <interface> ex peci
################################################################################


def read_temperature(component, token, test_case_id, script_id, log_level="None"
                     , tbd=None):

    try:
        if "CPU" == component:
            path = utils.ReadConfig("PECI_TOOL", "InstalledPath")               #read the installed path for PECI tool from config file
            registry_path = utils.ReadConfig('PECI_TOOL','reg_path')            #read the registry path for PECI tool from config file
            exe = utils.ReadConfig("PECI_TOOL", "Run_Cmd")                      #read exe name for PECI tool from config file
            cmd_for_log = lib_constants.GET_CPU_TEMPERATURE

            if "PECI" in token:
                cmd_for_log = lib_constants.GET_CPU_PKG_TEMPERATURE             #read the command to get the cpu package temperature using peci tool

            data = ""
            if "FAIL:" in [path, registry_path, exe, cmd_for_log]:
                library.write_log(lib_constants.LOG_WARNING,
                "WARNING: Config entry for tool is missing", test_case_id,
                                  script_id, "None", "None",log_level, tbd)     #fail if config entry is missing
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "for tool is found", test_case_id, script_id, "PECI", "None",
                                  log_level, tbd)                               #if config entry is proper
            if lib_tool_installation.peci_install_check(test_case_id,
                            script_id,log_level,tbd):                           #check if PECI tool already installed or not
                pass

            else:
               library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to"
                "install PECI Tool", test_case_id, script_id, "PECI", "None",
                                 log_level, tbd)                                #write fail message to log file if fail in peci tool installation
               return False
            utils.filechangedir(path)
            command = exe + " " + cmd_for_log                                   #command for getting temperature in csv file

            try:
                temp = []                                                       #create a empty list for temperature
                if utils.check_file(path + "\\" + "peci_gettemp.csv"):
                    try:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Deleting older/existing temperature log file ",
                        test_case_id, script_id, "PECI", "None",log_level, tbd)
                        os.remove(path + "\\" + "peci_gettemp.csv")             #deleting older log
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR:"
                        " Exception in deleting old log due to %s."%e,
                        test_case_id,script_id, "PECI",  "None", log_level, tbd)
                        return False
                subprocess.Popen(command, shell=True,stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE)                           #run the command to get temperature using PECI tool
                time.sleep(lib_constants.TEN_SECONDS)
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " running the tool due to %s"%e,test_case_id, script_id,
                "PECI",  "None", log_level, tbd)
                return False

            time.sleep(lib_constants.DELAY)                                     #wait till the log is generated

            if utils.check_file(path + "\\" + "peci_gettemp.csv"):              #checking path for the log file generated using tool
                try:
                    shutil.copy(path + "\\" + "peci_gettemp.csv",
                        lib_constants.SCRIPTDIR)                                #copy the temperature log to script directory
                except Exception as e:
                    library.write_log(lib_constants.LOG_ERROR, "ERROR: "
                    "Exception in copying the log file to script directory due"
                    " to %s "%e, test_case_id,script_id, "PECI",  "None",
                    log_level, tbd)
                with open(path + "\\" + "peci_gettemp.csv") as f:
                    data = f.readlines()
                    for line in data:
                        if 'Temperature' in line:                               #check for content "TEMPERATURE"
                            temp = line.split(",")[lib_constants.GET_TEMP_VALUE]
                        else:
                            pass
                f.close()
                return temp                                                     #return the temperature value

            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to generate  the log file using PECI tool", test_case_id,
                script_id, "PECI",  "None", log_level, tbd)                     #write fail message to log file if log is not generated
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Wrong"
            " input given for reading value",test_case_id,
            script_id, "None",  "None", log_level, tbd)
            return False

    except Exception as e:                                                      #exception for error
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "running the tool due to %s"%e,test_case_id, script_id,
        "PECI",  "None", log_level, tbd)
        return False