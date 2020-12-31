__author__ = 'jkmody'

############################General Python Imports##############################
import time
import subprocess
############################Local Python Imports################################
import library
import lib_constants

################################################################################
# Function Name : clear_event_viewer_logs
# Parameters    : TC_id-test case ID, script_id  - script ID,
#                 token - token
# Functionality : Clear all event viewer logs
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : Clear all event viewer logs
################################################################################

def clear_event_viewer_logs(tc_id , script_id , token ,  log_level , tbd=None ):

    try:
        cmd= '''powershell.exe wevtutil el | ForEach-Object {Write-Host "Clearing $_"; wevtutil cl "$_"}'''                         # Command to clear the event viwer logs
        library.write_log(lib_constants.LOG_INFO, "INFO : Clearing Event Viewer"
                " Logs",tc_id, script_id, "None", "None", log_level, tbd)
        p=subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)              # Executing Command to clear the event viwer logs
        output =  p.stdout.read()
        log_file=script_id.replace(".py",".log")
        with open(log_file,"w") as f_:
            f_.write(output)                                                    #Writing the events which are cleared from event viewer logs
        f_.close()
        time.sleep(lib_constants.TEN_SECONDS)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
            tc_id, script_id, "None", "None", log_level, tbd)
        return False
