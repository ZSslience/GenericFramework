__author__ = 'jkmody'

# General Python Imports
import csv
import glob
import os
import shutil
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_tat_tool_installation

################################################################################
# Function Name : read_package_power
# Parameters    : log_file - TAT Log File Name
# Functionality : reading package power from TAT log
# Return Value  : Value of package power
################################################################################


def read_package_power(log_file):

    str_package_power = "Power-Package Power(Watts)"
    data = []
    column_package_power = []

    with open(log_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            data.append(row)

    for j in range(len(data[0])):
        if str_package_power == data[0][j]:
            column_package_power.append(j)
            break

    data = []

    with open(log_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            content = list(row[k] for k in column_package_power)
            data.append(content)

    package_power = str(float(data[2][0]))
    return package_power

################################################################################
# Function Name : get_package_power
# Parameters    : token, tc_id, script_id, log_level, tbd
# Functionality : getting package power
# Return Value  : Value on successful action and 'False' on failure
# Syntax        : Get package power {from Step <n> log}
################################################################################


def get_package_power(token, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        token = utils.ProcessLine(token)

        if len(token) > lib_constants.TOKEN_LENGTH:
            step_no = token[5]
            step_value = utils.read_from_Resultfile((int(step_no)))             # token[5] is the step number. Retrieve the step # value from result.ini

            if "not present in result.ini" in step_value.lower():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: " +
                                  str(step_value) + " Hence Comparision failed",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return False
            else:
                package_power = read_package_power(step_value)
                return package_power
        else:
            tat_install_status = lib_tat_tool_installation.\
                tat_tool_installation(tc_id, script_id, log_level, tbd)         # TAT tool installation check

            if False == tat_install_status:                                     # Checking for TAT Installation
                library.write_log(lib_constants.LOG_WARNING, "WARNING: TAT "
                                  "tool installation Fail", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
            else:
                tat_tooldir = utils.ReadConfig("TAT_TOOL", "installedpath")     # Get tool directory of TAT tool from config file
                cmdexe = utils.ReadConfig("TAT_TOOL","Run_Cmd")                 # Get command for executing from config file

                for item in [tat_tooldir, cmdexe]:
                    if "FAIL:" in item:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Config entry for ToolDir or cmdexe"
                                          " is missing", tc_id, script_id,
                                          "None", "None", log_level, tbd)
                        return False

                os.chdir(tat_tooldir)
                files = glob.glob('TATMonitor_*.csv')
                for file in files:
                    os.remove(file)

                cmd = cmdexe + " -AL" + " -t=" + str(lib_constants.TAT_EXE) + \
                    " -p=" + str(lib_constants.TAT_POL)                         # Store the command to run in a variable which will run the tat tool

                value = os.system(cmd)                                          #Run the system command to generate log file for TAT
                os.chdir(lib_constants.SCRIPTDIR)
                time.sleep(lib_constants.TWENTY)

                if 0 == value or 1 == value:                                    #Checking the condition for command execution to generate log file
                    library.write_log(lib_constants.LOG_INFO, "INFO: TAT "
                                      "command execution successful", tc_id,
                                      script_id, "None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: TAT"
                                      " command execution not successful",
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False

                files = glob.glob(tat_tooldir + '\\TATMonitor_*.csv')
                tat_log = script_id.replace(".py", ".csv")

                shutil.move(files[0], tat_log)                                  # Moving log file to script directory
                package_power = read_package_power(tat_log)
                return package_power
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
