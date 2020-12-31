###########################Local library imports################################
import os
import lib_constants
import library
import time
import subprocess
################################################################################
from utils import *
################################################################################
# Function Name : lib_capture_screenshot
# Parameters    : token-capture screenshot,\
#                 tc_id-test case ID, script_id  - script ID,
#                 action- compare screenshot
# Functionality : Compare screeshot
# Return Value  : 'True'/Filename on successful \
#                 action and 'False'/Filename on failure
################################################################################


def capture_screen(tc_id, script_id, loglevel=None, tbd=None):

    scrpt = script_id.split(".")
    scrpt1 = scrpt[0].split("-")
    filename = tc_id + '-' + scrpt1[-1]
    path = lib_constants.SCRIPTDIR
    finalPath=os.path.join(path,filename)
    finalPath = finalPath + '.png'
    finalPathwex = finalPath
    
    if os.path.exists(finalPathwex):                                            # Checking for existing screenshot. if available, remove
        os.remove(finalPathwex)
    os.chdir(path)

    kvm_name = ReadConfig("kvm_name",'name')
    kvm_title = ReadConfig("kvm_name",'kvm_title')
    sikuli_path = ReadConfig("sikuli",'sikuli_path')
    sikuli_exe = ReadConfig("sikuli",'sikuli_exe')
    exe = sikuli_exe + ' CaptureScreens.skl' + ' ' + finalPath 
    title = kvm_name + ' - ' + kvm_title
    activate_path = ReadConfig("sikuli",'Activexe')
    window_path = activate_path + " " + title
    p = subprocess.Popen(window_path, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE)                  #Activating selected KVM screen
    library.write_log(lib_constants.LOG_INFO, "INFO: The captured screen shot"
                                              " process initiated",
                      tc_id,script_id, "None","None", loglevel, tbd)            #Write to log "process initated"
    time.sleep(lib_constants.TWO)

    os.chdir(sikuli_path)
    p = subprocess.Popen(exe, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)             #Captjuring screenshot using skuli and KVM
    time.sleep(lib_constants.SX_TIME)
    library.write_log(lib_constants.LOG_INFO, "INFO: The captured screen shot"
                                              " process finished",
                      tc_id,script_id, "None","None", loglevel, tbd)          #Write to log "process finished"
   
    time.sleep(lib_constants.SHORT_TIME)
    if os.path.exists(finalPathwex):                                            #check for the path of the file exists
        file_size = os.path.getsize(finalPathwex)                               #get the file size
        if "0" == file_size:                                                    #Condition to check the size of the file
            library.write_log(lib_constants.LOG_INFO, "INFO: The captured "
                                                      "screen shot failed to "
                                                      "get generated", tc_id,
                              script_id, "None","None", loglevel, tbd)          #Write to log "failed" if file size is 0

            return "False",finalPathwex                                         #return "False" and filename

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: The screen "
                                                      "shot was captured ",
                              tc_id, script_id,"None", "None",
                                          loglevel, tbd)                        #Write to file "captured" if file size is not 0
            return "True", finalPathwex                                         #return "True" and filename

    else:
        library.write_log(lib_constants.LOG_ERROR, "FAIL: Capture screenshot "
                                                   "failed", tc_id,
                          script_id,  "None","None", loglevel, tbd)
        return "False", finalPathwex                                            #return "False" and filename


################################################################################
