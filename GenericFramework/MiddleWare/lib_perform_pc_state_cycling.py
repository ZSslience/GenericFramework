__author__ = r'bchowdhx\apilshx\tnaidux'

# General Python Imports
import glob
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
from subprocess import Popen,PIPE

# Local Python Imports
import lib_constants
import library
import utils
import lib_tat_tool_installation

################################################################################
# Function Name : px_cycling
# Parameters    : original string, test_case_id, script_id, log_level, tbd
# Functionality : This code perform p-state cycling
# Return Value :  True/False
################################################################################


def px_cycling(ostr, test_case_id, script_id, log_level="ALL", tbd="None"):

    try:
        change_delay = 0
        ostr = ostr.upper()
        token = ostr.split()                                                    # Convert to list
        time_to_run = int(token[4])                                             # Extract the time to run from token
        perc = (token[7])                                                       # Extract load percentage from token
        perc = perc[:-1]                                                        # Remove the % sign from percentage
        perc = int(perc)                                                        # Convert to integer

        if percentage_calibration(perc, test_case_id, script_id, log_level,
                                  tbd):                                         # Library call to check the percentage
            pass
        else:
            return False

        os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)
        cmd1 = lib_constants.DELETE_CSV_FILE
        os.system(cmd1)
        os.chdir(lib_constants.SCRIPTDIR)

        if os.path.exists(lib_constants.TAT_TOOL_PATH):
            library.write_log(lib_constants.LOG_INFO, "INFO: TAT Tool is "
                              "already installed", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            try:
                host_service_start_cmd = "net start Intel(R)TATHostService"
                target_service_start_cmd = "net start Intel(R)TATTargetService"
                os.chdir(lib_constants.TAT_TOOL_PATH)
                host_op = os.system(host_service_start_cmd)
                os.chdir(lib_constants.INSTALLEDPATH_TARGET)
                target_op = os.system(target_service_start_cmd)

                library.write_log(lib_constants.LOG_INFO, "INFO: TAT Target "
                                  "service & Host service has started "
                                  "successfully", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                pass
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        else:
            install = lib_tat_tool_installation.\
                tat_tool_installation(test_case_id, script_id, log_level,tbd)

            if install:
                pass
            else:
                return False

        tree = ET.parse(lib_constants.PSTATE_CYCLING_SCRIPT)                    # Parse the cycling script
        pstate_script = lib_constants.SCRIPTDIR + \
            "\\pstate_cycling_updated.xml"                                      # Store the name of the new script to run with edited settings

        root = tree.getroot()                                                   # Get the root of the xml structure
        for i in range(1,10):                                                   # Iterate through the root for 10 times
            if root[i][1].text == "StartWorkLoad":
                root[i][5].text = str(perc)                                     # Append the required percentage to the file
            if root[i][4].text == "Time to run":
                root[i][5].text = \
                    str(time_to_run/lib_constants.SHORT_TIME) + " Min"          # Append the required time to run to the file
                change_delay = 1
            if root[i][1].text == "Delay" and change_delay == 1:
                root[i][4].text = str(((int(time_to_run) *
                                        lib_constants.THOUSAND)) +
                                      (5*lib_constants.THOUSAND))               # Put delay and append to file
                change_delay = 0

        tree.write(pstate_script)                                               # Write the updated script to the new script
        tool_exe = lib_constants.TAT_TOOL_PATH + "\ThermalAnalysisToolCmd.exe"  # Store the toolexe location in a variable

        cmd = tool_exe + " -AL -w=" + lib_constants.PSTATE_WORKSPACE + \
            " -s=" + pstate_script + " -t=" + str(time_to_run)                  # Store the command to run in a variable which will run the tat tool

        os.chdir(lib_constants.TAT_TOOL_PATH)                                   # Change to tat installed directory
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = process.communicate()

        time.sleep(time_to_run)                                                 # Wait for the given time
        time.sleep(lib_constants.FIVE_SECONDS)                                  # Store the name of the tat file in a variable file as glob returns list
        tat_kill_cmd = r"TASKKILL /F /IM ThermalAnalysisToolCmd.exe /T"
        os.system(tat_kill_cmd)
        file_name_script = script_id.replace(".py", ".csv")
        time.sleep(5)

        try:
            os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)

            for file in os.listdir(lib_constants.TAT_TOOL_RESULT_PATH):
                file_name, file_ext = os.path.splitext(file)
                os.rename(lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                          file_name + ".csv",
                          lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                          file_name_script)
                time.sleep(5)

            shutil.copy(lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                        file_name_script, lib_constants.SCRIPTDIR)              # Change to scriptdir
            os.chdir(lib_constants.SCRIPTDIR)
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s"
                              % e, test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        os.chdir(lib_constants.SCRIPTDIR)                                       # Change to scriptdir
        utils.write_to_Resultfile(lib_constants.SCRIPTDIR + "\\" +
                                  file_name_script, script_id)                  # Write to result file the location of the file

        library.write_log(lib_constants.LOG_INFO, "INFO: %s percentage "
                          "Workload for %s seconds duration is completed"
                          % (str(perc), str(time_to_run)), test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : applying_workload
# Parameters    : ostr, test_case_id, script id, log_level, tbd
# Functionality : This code will apply workload on the CPU
# Return Value  : True/False
################################################################################


def applying_workload(ostr, test_case_id, script_id, log_level="ALL",
                      tbd=None):

    token = ostr.split()                                                        # Convert to list from string
    duration = str(int(token[4]))                                               # Extract duration from the syntax
    perc = (token[7])                                                           # Extract the percentage of workload to apply from the syntax

    perc = perc[:-1]                                                            # Remove the percentage symbol
    perc = int(perc)                                                            # Convert to integer

    if percentage_calibration(perc, test_case_id, script_id, log_level, tbd):   # Library call to check the percentage
        pass
    else:
        return False

    if 0 == perc:
        result = cstate_monitor(duration, perc, test_case_id, script_id,
                                log_level, tbd)
        if result:
            return True
        else:
            return False
    else:
        pass
    try:
        if os.path.exists(lib_constants.TAT_TOOL_PATH):
            library.write_log(lib_constants.LOG_INFO, "INFO: TAT Tool is "
                              "already installed", test_case_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            install = lib_tat_tool_installation.\
                tat_tool_installation(test_case_id, script_id, log_level,tbd)

            if install:
                pass
            else:
                return False

        tat = r'<?xml version="1.0"?>' + "\n"                                   # Create the workload xml with input percentage and time
        tat_script = tat + r"<TatScript><Version>1.0</Version><CMD>" \
                           r"<ComponentName/><Command>StartLog</Command>" \
                           r"<NodeCount>0</NodeCount><CommandName/>" \
                           r"<Value>0</Value></CMD><CMD><ComponentName>" \
                           r"CPU Component</ComponentName><Command>" \
                           r"StartWorkLoad</Command><NodeCount>1" \
                           r"</NodeCount><NodeArg>CPU Power</NodeArg>" \
                           r"<CommandName>CPU-All</CommandName><Value>%s" \
                           r"</Value></CMD><CMD><ComponentName/><Command>" \
                           r"Delay</Command><NodeCount>0</NodeCount>" \
                           r"<CommandName/><Value>%s</Value></CMD><CMD>" \
                           r"<ComponentName>CPU Component" \
                           r"</ComponentName><Command>StopWorkLoad" \
                           r"</Command><NodeCount>1</NodeCount><NodeArg>" \
                           r"CPU Power</NodeArg><CommandName>CPU-All" \
                           r"</CommandName></CMD><CMD><ComponentName/>" \
                           r"<Command>StopLog</Command><NodeCount>0" \
                           r"</NodeCount><CommandName/><Value>0</Value>" \
                           r"</CMD></TatScript>" %(perc, duration)
        
        os.chdir(lib_constants.TAT_TOOL_PATH)

        with open("TatScript.xml", "w") as handle:                              # Write the appended script as Tatscript.xml in Tat installed directory
            handle.write(tat_script)

        tool_exe = lib_constants.TAT_TOOL_PATH + "\ThermalAnalysisToolCmd.exe"  # Store the name of the Tool in toolexe variable

        os.chdir(lib_constants.TAT_TOOL_PATH)

        tat_cmd = tool_exe + " -AL" + " -s=TatScript.xml" + \
            " -t=%s" % duration + " -w=" + lib_constants.PSTATE_WORKSPACE       # Store the command to run in a variable

        subprocess.Popen(tat_cmd, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)        # Run the command

        if cstate_monitor(duration, perc, test_case_id, script_id, log_level, 
                          tbd):                                                 # Library call to monitor cstate while workload is applied
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e, 
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


################################################################################
# Function Name : cstate_monitor
# Parameters    : time, percentage, test_case_id, script id , log_level, tbd
# Functionality : Generate log from socwatch
# Return Value :  True/False
################################################################################


def cstate_monitor(time_to, perc, test_case_id, script_id, log_level="ALL",
                   tbd="None"):

    try:
        script_dir = lib_constants.SCRIPTDIR
        soc_watch_tool_dir = utils.ReadConfig("SOC_WATCH", "tooldir")

        if "FAIL:" in soc_watch_tool_dir:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry for soc watch tool dir",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Ccheck if config entry for socwatch is given
            return False

        os.chdir(soc_watch_tool_dir)
        file = glob.glob("SOCWatchOutput*.csv")                                 # Search for the out put log file

        if file == []:
            pass
        else:
            file_name = file[0]
            if os.path.exists(soc_watch_tool_dir + "\\"+file_name):
                os.remove(file_name)

        time_to_run = int(time_to)                                              # Convert  time_to_run to integer
        cmd_to_run = "socwatch.exe -f cpu-cstate -t " + str(time_to_run)        # Run the command for socwatch after appending with new time

        for file in glob.glob("monitor*.csv"):                                  # Search for monitor file
            os.remove(file)                                                     # If exist remove

        output, err = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE).communicate()     # start the process

        file = glob.glob("SOCWatchOutput*.csv")                                 # Search for the out put log file
        if file == []:
            return False
        else:
            file_name = file[0]

        os.chdir(script_dir)                                                    # Change to scriptdir
        file_name_script = script_id.replace(".py", "")

        for var_name in glob.glob(file_name_script + "_SOC_LOG.csv"):           # Check for existing soc_loc.csv file in scriptdir
            os.remove(var_name)                                                 # Remove if found

        if file == []:                                                          # If the log file is empty
            pass
        else:
            shutil.copy(dir + "\\" + file_name, script_dir)                     # Copy the file from tat dir to scriptdir

            os.rename(lib_constants.SCRIPTDIR + "\\" + file_name,
                      file_name_script + "_SOC_LOG.csv")                        # Rename the file to standard name

            utils.write_to_Resultfile(lib_constants.SCRIPTDIR + "\\" +
                                      file_name_script + "_SOC_LOG.csv",
                                      script_id)                                # Write to result file the location of the log path

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "generated log file from socwatch tool",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : percentage_calibration
# Parameters    : percentage, test_case id, script id, log_level, tbd
# Functionality : This code will check the percentage of load
# Return Value  : True/False
################################################################################


def percentage_calibration(perc, test_case_id, script_id, log_level="ALL",
                           tbd="None"):

    counter = False

    for item in lib_constants.C_STATE_PERC:
        if item == perc:
            counter = True
            break
        else:
            counter = False

    if counter:
        library.write_log(lib_constants.LOG_INFO, "INFO: Current percentage "
                          "to be applied is %s percentage" % str(perc),
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Load percentage"
                          " should be either 0, 50, 60, 70, 80, 90 or 100 "
                          "percent", test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return False
