__author__ = 'kapilshx'
###########################General Imports######################################
import time
import os
import subprocess
import sys
import codecs
import re
############################Local imports#######################################
import library
import lib_constants
import utils
import lib_clear_event_viewer_logs
################################################################################
# Function Name : enable_hyper_v_using_powershell
# Parameters    : vsm_token,test case id,script id,loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : function to enable hyper-v option using_powershell
################################################################################
def enable_hyper_v_using_powershell(vsm_token,test_case_id,script_id,
                                    loglevel="ALL", tbd=None):                  #function to enable hyper-v option using_powershell
    try:
        if lib_clear_event_viewer_logs.clear_event_viewer_logs(test_case_id,    #functtion call to clear the event viewer logs
                                        script_id,vsm_token,loglevel,tbd):
            pass
        else:
            return False
        hyper_v_cmd = lib_constants.HYPER_V_ENABLE_CMD                          #command to enable the hyper-v option under windows feature
        powershell_com ="powershell.exe " + hyper_v_cmd
        output = subprocess.Popen(powershell_com, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE)                                #running powershell cmd using subprocess
        output_hyper = output.communicate()[0].strip()
        if "True" in output_hyper:
            library.write_log(lib_constants.LOG_INFO, "INFO: Hyper-V option is"
                " enabled in os under window features using powershell",
            test_case_id, script_id, "None", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to enable"
            "Hyper-V option in  os under window features using powershell",
            test_case_id, script_id, "None", "None", loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "enable_hyper_v_using_powershell()library function due to %s."%e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             # write error msg to log if Exception occurs in enable_hyper_v_using_powershell() library function
        return False
################################################################################
# Function Name : run_vsm_registry_file
# Parameters    : vsm_token,test case id,script id,loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : function to check hyper-v in event log file and run
#                 the registry file to enable the VBS
################################################################################
def run_vsm_registry_file(test_case_id,script_id,loglevel="ALL",tbd=None):
    try:
        cmd_to_run = lib_constants.EVENT_VIEWER_LOG_CMD                         #command to get the event viewer_log using powershell
        if library.run_powershell_cmd(cmd_to_run, test_case_id,script_id,
                                      loglevel, tbd):
            pass
        else:
            return False
        if verify_event_log(test_case_id, script_id,loglevel, tbd):             #To varify the string in the event log
            pass
        else:
            return False
        vsm_regedit_file_path = utils.ReadConfig("CONFIGURE_VSM",
                                                 "vsm_regedit_file_path")       #Read vsm_regedit_file_path from config which contains commands to enable the device guard status option
        if "FAIL" in vsm_regedit_file_path:                                     #if failed to read the vsm_regedit_file_path from config
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry is"
                " missing for tag 'vsm_regedit_file_path' port",
                    test_case_id,script_id,"None", "None", loglevel, tbd)
            return False
        if os.path.exists(vsm_regedit_file_path):                               #if vsm_regedit_file_path exists under tools folder
            library.write_log(lib_constants.LOG_INFO, "INFO: VSM_regedit.bat "
                "file is present in C:\\Automation\\tools folder",test_case_id,
                              script_id,"None", "None", loglevel, tbd)
        else:                                                                   #if vsm_regedit_file_path does not exist under tools folder
            library.write_log(lib_constants.LOG_INFO, "INFO: File "
                "vsm_regedit.bat does not exist in the tools folder",
                test_case_id,script_id,"None","None", loglevel, tbd)
            return False
        result = subprocess.Popen(vsm_regedit_file_path,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE)                                #To run the vsm_regedit.bat file using subprocess
        poutput = result.communicate()[0].strip()
        if "completed" in poutput or "Completed" in poutput:                    #if vsm_regedit.bat file executed successfully
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "run_vsm_registry_file()library function due to %s."%e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             # write error msg to log if Exception occurs in run_vsm_registry_file() library function
        return False
################################################################################
# Function Name : configure_vsm_in_os
# Parameters    : vsm_token,test case id,script id,loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : function to check and parse the Device guard status
#                 in msinfo32 log
################################################################################
def configure_vsm_in_os(test_case_id,script_id,loglevel="ALL",tbd=None):
    try:
        log_file = ((script_id.strip(".py")) + '_msinfo_log.txt')
        log_path = os.path.join(lib_constants.SCRIPTDIR, log_file)
        msinfocmd = 'msinfo32 /report '+ log_path                               #command to get the msinfo32 log
        os.chdir(lib_constants.SCRIPTDIR)
        result = subprocess.Popen(msinfocmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE)
        poutput = result.communicate()[0].strip()
        time.sleep(lib_constants.SIKULI_EXECUTION_TIME)
        device_guard_flag = False
        device_guard_status_flag = False
        with codecs.open(log_path,"r","windows-1252") as device_line:           #to iterate in file for the Device guard status
            for line in device_line:
                line = (''.join(re.split('\x00 |\x00',line))).split('\t')
                line = (''.join(line)).strip("\r")
                if "DeviceGuardVirtualizationbasedsecurity" in line:
                    device_guard_flag = True                                    #if Device Guard Virtualization based security option is found in file then set the device_guard_flag to true
                    line = line.split("security",1)[1]
                    if "Running" == line:
                        device_guard_status_flag = True                         #if Device Guard Virtualization based security is equal to 'running' is found in file then set the device_guard_status_flag to true
        if True == device_guard_flag and True == device_guard_status_flag:      #if required string for device guard found in file
            library.write_log(lib_constants.LOG_INFO, "INFO: VSM is configured"
                " successfully in os",test_case_id,script_id,"None", "None",
                              loglevel, tbd)
            return True
        else:                                                                   #if failed to find required string for device guard in file
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "configure the VSM in os",test_case_id,script_id,"None", "None",
                              loglevel,tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "configure_vsm_in_os()library function due to %s."%e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             # write error msg to log if Exception occurs in configure_vsm_in_os() library function
        return False
################################################################################
# Function Name : verify_event_log
# Parameters    : test_case_id is test case number, script_id is script_number,
#                  dev_name is device name, event is event type
# Return Value  : 'True' on successful action and 'False' on failure
# Functionality : verify event log for events e.g. error/info/warning
################################################################################
def verify_event_log(test_case_id, script_id, loglevel="ALL", tbd="None"):
    try:
        log_file = ((script_id.strip(".py")) + '.txt')
        log_path = os.path.join(lib_constants.SCRIPTDIR, log_file)
        if os.path.exists(log_path):                                            #To check the path for event log file
            library.write_log(lib_constants.LOG_INFO,
            "INFO : Event log file is found in the path %s"%(log_path),
            test_case_id,script_id, "None", "None",loglevel, tbd)               #Verified the log path of event log file
            pass
        else:
            library.write_log(lib_constants.LOG_INFO,
        "INFO : Failed to find the event lofg file in the path %s"%(log_path),
            test_case_id, script_id, "None", "None", loglevel, tbd)             #Verification of log path failed for event log file
            return False
        hyper_v_flag = False
        with open(log_path,"r") as fp:
            lines = fp.readlines()
            for line in lines:                                                  #loop to iterate for searhing the string 'hyper-v' in file
                if "Hyper-V" in line:
                    hyper_v_flag = True
        if True == hyper_v_flag:                                                #if required string 'hyper-v' is found in file
            library.write_log(lib_constants.LOG_INFO, "INFO: Hyper-v is found"
                " in the event viewer log",test_case_id,script_id,"None",
                "None", loglevel, tbd)
            return True
        else:                                                                   #if required string 'hyper-v' is not found in file
            library.write_log(lib_constants.LOG_INFO, "INFO: Hyper-v is not "
                "found in the event viewer log",test_case_id,
                script_id,"None","None", loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "verify_event_log()library function due to %s."%e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             # write error msg to log if Exception occurs in verify_event_log() library function
        return False
################################################################################