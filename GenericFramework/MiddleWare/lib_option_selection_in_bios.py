__author__ = 'jbishtx/kapilshx'

############################General Python Imports##############################
import subprocess
import re
import os
############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_capture_screenshot
import time
import sys
################################################################################
# Function Name : option_selection_in_bios
# Parameters    : ostr - token, test_case_id-test case ID, script_id - script ID
# Functionality : option_selection_in_bios
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : select <Param1> from /bios in bios and choose <Param2>
################################################################################
def option_selection_in_bios(ostr, test_case_id, script_id, loglevel,tbd):
    try:
        if "reset" in ostr.lower():
            sikuli_path = utils.ReadConfig("sikuli",'sikuli_path')
            sikuli_exe = utils.ReadConfig("sikuli",'sikuli_exe')
            for item in [sikuli_path, sikuli_exe]:
                if "FAIL:" in item.strip():                                     #if config.ini entry is missing for any of the variable
                    library.write_log(lib_constants.LOG_INFO, "INFO :Config "
                        "entry is missing for tag variable sikuli_path,"
                        " sikuli_exe under section sikuli",test_case_id,
                        script_id, "None", "None", loglevel, tbd)
                    return False                                                # if the readconfig function returned fail it means no config entry is given
                else:
                    pass
            exe = sikuli_exe + ' Bios_screen.skl'
            bios_screen_file_path = sikuli_path + os.sep +"Bios_screen.skl"
            if os.path.exists(bios_screen_file_path):
                library.write_log(lib_constants.LOG_INFO, "INFO:"
                    " Bios_screen.skl file is present in given config "
                    "path",test_case_id,script_id, "None","None",loglevel, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Bios_screen.skl"
                    " file is not present in given config "
                    "path",test_case_id,script_id, "None","None",loglevel, tbd)
                return False
            if library.activate_kvm(test_case_id, script_id, loglevel, tbd):
                pass
            else:
                return False
            library.write_log(lib_constants.LOG_INFO, "INFO: KVM activate "
                "process is  initiated",test_case_id,script_id, "None",
                              "None",loglevel, tbd)        					    #Write to log "process initiated"
            os.chdir(sikuli_path)
            bios_screen_sikuli_output = subprocess.\
                Popen(exe, shell=True, stdout=subprocess.PIPE,
                      stdin=subprocess.PIPE, stderr=subprocess.PIPE)#Capturing screenshot using sikuli and KVM
            time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
            bios_screen_sikuli_output = bios_screen_sikuli_output.stdout.read()
            if "Pass" in bios_screen_sikuli_output:

                library.sendkeys_times("Enter",lib_constants.THREE)             #Pressing Enter Key to Continue
                time.sleep(lib_constants.TWO)

                library.write_log(lib_constants.LOG_INFO, "INFO: SUT is in BIOS"
                    " setup page and Reset button is clicked",test_case_id,
                    script_id, "None","None", loglevel, tbd)
                time.sleep(lib_constants.TWENTY)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: SUT is not in"
                    " BIOS setup page and G3 reboot cycle is started",
                    test_case_id, script_id,"None","None", loglevel,tbd)
                pass
            if True == library.g3_reboot_system(loglevel, tbd):                 # Does a g3 if system is not in os
                pass
            else:
                library.write_log(lib_constants.LOG_INFO, "ERROR: Reboot failed",
                test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT %s Process "
                                            "Completed"%((ostr.split(" "))[1]),
                              test_case_id,script_id, "None","None", loglevel, tbd)
            library.sendkeys_times("F2",lib_constants.TWENTY)						#Pressing F2 Keys to Enter in BIOS
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT boot to BIOS"
                                                      " Successfully",
                              test_case_id,script_id, "None","None", loglevel, tbd)
            library.sendkeys_times("Up_arrow",lib_constants.TWO)
            library.write_log(lib_constants.LOG_INFO, "INFO: %s Option"         #Reset Option Selection
                " Selected Successfully"%((ostr.split(" "))[1]),test_case_id,
                              script_id,"None","None",loglevel, tbd)
            time.sleep(lib_constants.TWO)
            os.chdir(sikuli_path)
            bios_screen_sikuli_output_new = subprocess.\
                Popen(exe, shell=True, stdout=subprocess.PIPE,
                      stdin=subprocess.PIPE, stderr=subprocess.PIPE)   #Capturing screenshot using sikuli and KVM
            time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
            bios_screen_sikuli_output_new = \
                bios_screen_sikuli_output_new.stdout.read()
            if "Pass" in bios_screen_sikuli_output_new:
                library.sendkeys_times("Enter",lib_constants.TWO)               #Pressing Enter Key to Continue
                time.sleep(lib_constants.TWO)
                library.write_log(lib_constants.LOG_INFO, "INFO: SUT is in BIOS"
                    " setup page and Reset button is clicked",test_case_id,
                    script_id, "None","None", loglevel, tbd)
                time.sleep(lib_constants.TWENTY)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: SUT is not in"
                    " BIOS setup page",test_case_id, script_id,"None","None",
                    loglevel,tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:Input syntax is "
                "incorrect or not implemented",test_case_id,script_id,
                "None","None",loglevel, tbd)
            return False
    except Exception as e:                                                  	#exception handled
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occurs in "
        "the library function option_selection_in_bios() due to "
        "%s"%e, test_case_id, script_id, "None", "None", loglevel, tbd)
        return False
################################################################################



