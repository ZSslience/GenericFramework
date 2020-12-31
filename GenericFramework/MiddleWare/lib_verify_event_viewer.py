__author__ = "patnaikx"

##############################General Library import############################
import os
import utils
import time
import sys
import subprocess
import re
################################################################################

#########################Local library import###################################
import lib_constants
import lib_run_command
import library
################################################################################

################################################################################
# Function Name : verify_event_viewer
# Parameters    : test_case_id is test case number, script_id is script_number,
#                  dev_name is device name, event is event type
# Functionality : verify event log for events e.g. error/info/warning
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################
def verify_event_viewer(event, test_case_id, script_id,
                                        log_level="ALL", tbd="None"):
    try:
        if "ERROR" in event:
            event1 = "ERROR"
        elif "WARNING" in event:
            event1 = "WARNING"
        else:
            event1 = "INFO"
        cmd_to_run = '''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    Where-Object {$_.entryType -Match "'''+event1+'''"} '''
                                                                                #command for check error/event in event-viewer log
        for filename in os.listdir("."):                                        #check for filename in directory for nsh

            if filename.endswith("ps1"):                                        #if any nsh file is there unlink the file
                os.unlink(filename)
                library.write_log(lib_constants.LOG_INFO,"INFO: old "
                    "Powershell log deleted", test_case_id, script_id,
                                  "None","None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: No old "
                    "Powershell log exists", test_case_id, script_id,
                                  "None","None", log_level, tbd)
                pass
        myFile=open("psquery.ps1","w")
        myFile.write(cmd_to_run)
        myFile.close()
        time.sleep(lib_constants.FIVE_SECONDS)                                  #sleep for 5 seconds
        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        script_dir = lib_constants.SCRIPTDIR
        log_path = script_dir + "\\" + log_file

        powershell_path = lib_constants.PWRSHELL_PATH                           #Read from powershell the vaue of powershell path

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
                              "None", log_level, tbd)
        os.chdir(lib_constants.SCRIPTDIR)
        ignore_event_count = 0
        error_event_count = 0
        if (os.path.exists(log_path)):
            file_size = os.path.getsize(log_file)                               #get the size of the log file
            found1 = False
            found = False
            if "ERROR" == event:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)Error(.*)", line):
                            found = True
                            if lib_constants.EVENT_IGNORE in line:
                                ignore_event_count = ignore_event_count + 1
                            else:
                                error_event_count = error_event_count + 1
                                                                                #Return false value if log generated and
                                                                                #content found
                        else:
                                continue                                        #Return true value if log generated and content found
                f.close()
            elif "WARNING" == event:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)Warning(.*)", line):
                                found = True
                                break                                           #Return false value if log generated and
                                                                                #content found
                        else:
                                continue                                        #Return true value if log generated and content found
                f.close()
            elif "FAIL" in event:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)Fail(.*)", line):
                                found = True
                                break                                           #Return false value if log generated and
                                                                                #content found
                        else:
                                continue                                        #Return true value if log generated and content found
                f.close()
            elif "ERROR" in event and "HIBERNATE" in event:
                with open(log_path, "r") as f:
                    for line in f:
                        if "error" in line.lower() and "hibernate" in line.lower():
                                found = True
                                break                                           #Return false value if log generated and
                                                                                #content found
                        else:
                                continue                                        #Return true value if log generated and content found
                f.close()
            elif "ERROR" in event and "SLEEP" in event:
                with open(log_path, "r") as f:
                    for line in f:
                        if "error" in line.lower() and "sleep" in line.lower():
                                found = True
                                break                                           #Return false value if log generated and
                                                                                #content found
                        else:
                                continue                                        #Return true value if log generated and content found
                f.close()
            else:
                with open(log_path, "r") as f:
                    for line in f:
                        if re.match("(.*)42(.*)", line):
                                found1 = True
                                break                                           #Return false value if log generated and
                                                                                #content found
                        else:
                                continue
                if found1:
                    cmd_to_run1 = '''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    Where-Object {$_.Source -Match "Power-Troubleshooter"} '''  #command for check event in event-viewer log
                    for filename in os.listdir("."):                            #check for filename in directory for nsh

                        if filename.endswith("ps1"):                            #if any psh file is there unlink the file
                            os.unlink(filename)

                        else:
                            library.write_log(lib_constants.LOG_INFO,"INFO: "
                            "No old Powershell log exists", test_case_id,
                                      script_id, "None","None",log_level, tbd)
                            pass
                    myFile=open("psquery.ps1","w")
                    myFile.write(cmd_to_run1)
                    myFile.close()
                    shell_script = 'psquery.ps1'                                #shell script should be placed in script directory
                    exe_path = os.path.join(lib_constants.SCRIPTDIR,
                                            shell_script)
                    final_command = 'powershell.exe '+ exe_path + ' > ' \
                                    + log_path                                  #concate the commands along with the log path
                    try:
                        os.chdir(powershell_path)
                        os.system(final_command)
                    except Exception as e:
                        os.chdir(lib_constants.SCRIPTDIR)
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                            "Exception occurred due to %s"%e, test_case_id,
                                 script_id, "None", "None", log_level, tbd)
                    os.chdir(lib_constants.SCRIPTDIR)
                    if (os.path.exists(log_path)):                              #if file does not exist
                        file_size = os.path.getsize(log_file)
                        if file_size != 0:
                            found = True
                        else:
                            found = False
            if "ERROR" in event:                                                #if event is ERROR
                if found:
                    if ignore_event_count > 0 and error_event_count == 0:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Error"
                                          "event '%s' only found in Event viewer"
                                          " which can be ignored" %
                                          lib_constants.EVENT_IGNORE,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False

                    else:
                        library.write_log(lib_constants.LOG_INFO,"INFO: "
                             "%s content found in EVENT-VIEWER log" % event,
                            test_case_id, script_id, "None", "None", log_level,
                                          tbd)
                        return True
                else:                                                           #if event is Hibernate
                    library.write_log(lib_constants.LOG_INFO,"INFO: %s "
                    "content does not found in EVENT-VIEWER log" % event, test_case_id,
                            script_id, "None", "None", log_level, tbd)
                    return False
            elif "FAIL" in event:                                               #if event is ERROR
                if found:
                    library.write_log(lib_constants.LOG_INFO,"INFO: "
                         "%s content found in EVENT-VIEWER log % event",
                        test_case_id, script_id, "None", "None", log_level, tbd)
                    return True
                else:                                                           #if event is Hibernate
                    library.write_log(lib_constants.LOG_INFO,"INFO: %s "
                    "content does not found in EVENT-VIEWER log"% event, test_case_id,
                            script_id, "None", "None", log_level, tbd)
                    return False
            else:
                if found:                                                       #if system wake up from hibernation
                    library.write_log(lib_constants.LOG_INFO,"INFO: System"
                        " wake up from %s "% event, test_case_id,
                            script_id, "None", "None", log_level, tbd)
                    return True
                else:                                                           #if failed to wake up from hibernation
                    library.write_log(lib_constants.LOG_WARNING,"WARNING: "
                       "error in  wake-up from %s"% event, test_case_id,
                            script_id, "None", "None", log_level, tbd)
                    return False
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL:log failed to  "
                "get generate for command.", test_case_id,
                            script_id, "None", "None", log_level, tbd)
            return False                                                        #return FALSE if failed to generate log


    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
                test_case_id, script_id, "None", "None", log_level, tbd)        #exeception error catch if failed
        return False
