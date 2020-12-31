__author__ = 'patnaikx'

############################Local library imports###############################
import library
import lib_constants
import utils
import lib_clear_event_viewer_logs
###########################Global library imports###############################
import os
import time
import re
from SendKeys import SendKeys
import subprocess
import time
import win32gui
################################################################################
# Function Name : run_wmd_command
# Description   : run Windows Memory Diagnostics command in sut
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' on successful run of wmd command and 'false'
#                   on failure
# Purpose       : run the Windows Memory Diagnostics command
################################################################################

def run_wmd_command(token, test_case_id, script_id, loglevel="ALL", tbd=None):
    try:
        lib_clear_event_viewer_logs.clear_event_viewer_logs(test_case_id ,
                                    script_id , token ,  loglevel , tbd=None )
        time.sleep(lib_constants.TWO)
        cmd_to_run = lib_constants.WMD_COMMAND                                  # command for WMD
        res = subprocess.Popen(cmd_to_run, shell = True, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        if res:
            time.sleep(lib_constants.FIVE)
            status = SendKeys("{DOWN}{ENTER}{ENTER}",1)                         # sendkeys to select option on wmd window
            library.write_log(lib_constants.LOG_INFO,"INFO : Windows memory"
            " diagnostics command ran successfully",
            test_case_id,script_id,"None","None",loglevel,tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
                test_case_id, script_id, "None", "None", loglevel, tbd)         #exception error catch if failed
        return False

################################################################################
# Function Name : check_wmd_results
# Description   : verify system log for error due to wmd command run
# Parameters    : test_case_id is test case number, script_id is script number
# Returns       : 'true' if no error found after wmd run else 'false'
#                   on error in event viewer log
# Purpose       : verify system event viewer log for error after WMD run
################################################################################
def check_wmd_results(command, test_case_id, script_id, loglevel="ALL",
                                                                    tbd=None):
    try:
        cmd_to_run = lib_constants.WMD_ERROR_POWERSHELL
        for filename in os.listdir("."):                                        #check for filename in directory for nsh
            if filename.endswith("ps1"):                                        #if any nsh file is there unlink the file
                os.unlink(filename)

            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: No old "
                    "Powershell log exists", test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                pass
        myFile=open(lib_constants.SCRIPTDIR+"\\psquery.ps1","w")
        myFile.write(cmd_to_run)
        myFile.close()
        time.sleep(lib_constants.FIVE_SECONDS)                                  #sleep for 5 seconds
        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        script_dir = lib_constants.SCRIPTDIR
        log_path = script_dir + "\\" + log_file
        powershell_path = utils.ReadConfig("WIN_POWERSHELL", "PATH")            #Read from powershell the value of powershell path
        if "FAIL" in powershell_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                    "entry of powershell_path is not proper ", test_case_id,
                script_id, "None", "None", loglevel, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config "
                    "entry of powershell_path is fetched ", test_case_id,
                script_id, "None", "None", loglevel, tbd)
        shell_script = 'psquery.ps1'                                            #shell script should be placed in script directory
        exe_path = os.path.join(lib_constants.SCRIPTDIR, shell_script)

        final_command = 'powershell.exe '+ exe_path + ' > ' + log_path          #concat the commands along with the log path
        try:
            os.chdir(powershell_path)
            os.system(final_command)

        except Exception as e:
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Exception "
                "occurred due to %s"%e, test_case_id, script_id, "None",
                              "None", loglevel, tbd)
        os.chdir(lib_constants.SCRIPTDIR)
        found = False
        if (os.path.exists(log_path)):
            file_size = os.path.getsize(log_file)                               #get the size of the log file
            found = False
            string_to_find = lib_constants.WMD_LOG_STRING                       #string to be find in system output log for WMD
            with open(log_path, "r") as f:
                for line in f:
                    if re.search(string_to_find, line):
                        found = True
                        break
                    else:
                        continue
            if found:                                                           # if no error found in system log for wmd
                library.write_log(lib_constants.LOG_INFO,"INFO: Wmd got "
                "verified as error content was not found in system log",
                test_case_id, script_id, "None", "None", loglevel, tbd)
                return log_path

            else:                                                               # if error contains in system log for wmd
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                "verify wmd as error found in system log", test_case_id,
                script_id, "None", "None", loglevel, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING,"WARNING: System-log "
            "failed to get generate for WMD command.", test_case_id,
                            script_id, "None", "None", loglevel, tbd)
            return False                                                        #return FALSE if failed to generate log
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
                test_case_id, script_id, "None", "None", loglevel, tbd)         #exception error catch if failed

