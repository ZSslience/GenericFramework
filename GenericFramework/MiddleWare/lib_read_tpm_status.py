__author__ = "kapilshx"

###########################General Imports######################################
import os
import platform
import string
import subprocess
import shutil
import time
import sys
import parser
############################Local imports#######################################
import lib_constants
import library
import utils
import subprocess
import codecs
################################################################################
# Function Name : read_tpm_status
# Parameters    : tpm_token,test_caseid, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : Open TPM.msc snap in & Check for Status
################################################################################
def read_tpm_status(tpm_token,test_case_id, script_id,
                               loglevel = "ALL", tbd="None"):
    try:
        if os.path.exists(lib_constants.TOOLPATH + os.sep + "tpm.txt"):
            os.remove(lib_constants.TOOLPATH + os.sep + "tpm.txt")
        else:
            pass
        log_file = script_id.split(".")[0]
        log_path = lib_constants.SCRIPTDIR+r"\\"+ log_file+".txt"               #to give the generated log_path
        if os.path.exists(lib_constants.TOOLPATH + os.sep + "TPM-Status.exe"):
            library.write_log(lib_constants.LOG_INFO,"INFO:Setup file "
                "TPM-Status.exe is placed properly in this path"
                " C:\\Automation\\tools\\TPM-Status.exe ",
                    test_case_id,script_id,"None","None",loglevel,tbd)
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL:Setup file "
                "TPM-Status.exe is not placed in this path"
                " C:\\Automation\\tools\\TPM-Status.exe ",
                    test_case_id,script_id,"None","None",loglevel,tbd)
            return False
        os.chdir(lib_constants.TOOLPATH)
        tpm_output = subprocess.Popen("TPM-Status.exe",
            stdout=subprocess.PIPE,stdin=subprocess.PIPE,shell=True,stderr=subprocess.PIPE)            #run the TPM-Status.exe using subprocess
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        tpm_output = tpm_output.communicate()[0]


        os.chdir(lib_constants.TOOLPATH)
        tpm_status_flag = False
        tpm_status_fp = open("tpm.txt","r")                                     #open tpm.txt file in read mode
        tpm_status = tpm_status_fp.readlines()
        for item in tpm_status:
            if "The TPM is ready for use." == item.strip():                     #if "TPM is ready for use" string is found in data_tpm
                tpm_status_flag = True
                break
            else:
                pass
        tpm_status_fp.close()

        tpm_status_fp = open("tpm.txt","r")                                     #open tpm.txt file in read mode
        tpm_status = tpm_status_fp.readlines()
        tpm_final_data = ""
        tpm_final_list  = ""
        for item in tpm_status:
            tpm_final_data  = item.strip('\n').strip(' ')
            tpm_final_list+=tpm_final_data
        tpm_status_fp.close()
        tpm_final_list = repr(tpm_final_list)
        tpm_status_fp = open("tpm.txt","w")                                     #open tpm.txt file in read mode
        tpm_status_fp.write(tpm_final_list)
        tpm_status_fp.close()

        src_tpm_file_path = lib_constants.TOOLPATH + os.sep + "tpm.txt"
        shutil.copyfile(src_tpm_file_path,log_path)                             #copy tpm.txt to script directory with script name

        if True == tpm_status_flag:                                             #If TPM is ready for use then true
            library.write_log(lib_constants.LOG_INFO,"INFO: TPM is in "
            "ready status",test_case_id,script_id,"None","None",loglevel,tbd)
            return True
        else:                                                                   #If TPM is not ready for use then it goes to else part
            library.write_log(lib_constants.LOG_FAIL,"FAIL: TPM is Not in  "
                "ready status",test_case_id,script_id,"None","None",loglevel,tbd)
            return False
    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in library"
        " function reading TPM status as %s " %e,
    test_case_id, script_id, "None", "None", loglevel, tbd)                     #Write the exception error msg to log
        return False
################################################################################
# Function Name : clear tpm
# Parameters    : tpm_token,test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to clear the tpm
################################################################################
def clear_tpm(tpm_token,test_case_id, script_id,
                               loglevel = "ALL", tbd="None"):
    try:
        kvm_name = utils.ReadConfig("kvm_name","name")                          # KVM is read from the config file
        sikuli_path = utils.ReadConfig("sikuli","sikuli_path")                  # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli","sikuli_exe")                    # Sikuli exe name fetched from config file
        kvm_title = utils.ReadConfig("kvm_name","kvm_title")                    # kvm_title exe name fetched from config file
        activate_path = utils.ReadConfig("sikuli","Activexe")                   # activate_path exe name fetched from config file
        for item in  [kvm_name, sikuli_path, sikuli_exe,kvm_title,activate_path]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_FAIL,"FAIL :Config entry is"
                " missing for tag name :kvm_name or sikuli_path or sikuli_exe",
                test_case_id,script_id,"None","None",loglevel,tbd)
                return False                                                    # if the readconfig function returned fail it means no config entry is given
            else:
                pass
        sikuli_cmd_for_clear_tpm = " clear_tpm_display.skl"                     # Sikuli file for clear tpm
        os.chdir(os.getcwd())
        time.sleep(lib_constants.SIKULI_EXECUTION_TIME)
        title = kvm_name + " - "+ kvm_title                                     # KVM command for activating the kvm window
        window_path = activate_path + " " + title
        kvm_activate = subprocess.Popen(window_path , stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, stdin=subprocess.PIPE)   # KVM window is activated from the host
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        kvm_activate = kvm_activate.communicate()[0]
        if "Failed" in kvm_activate:
            library.write_log(lib_constants.LOG_FAIL,"FAIL Failed to activate"
                " the KVM window",test_case_id,script_id,
                              "None","None",loglevel,tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO KVM window is"
                " activated",test_case_id,script_id,
                              "None","None",loglevel,tbd)
            pass
        output = []
        os.chdir(sikuli_path)
        cmd_for_clear_tpm = sikuli_exe + sikuli_cmd_for_clear_tpm               # sikuli command to verify the clear tpm
        library.write_log(lib_constants.LOG_INFO,"INFO clear TPM process"
            " is initiated",test_case_id,script_id,"None","None",loglevel,tbd)
        output_for_clear_tpm = subprocess.Popen(cmd_for_clear_tpm ,shell = True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                stdin=subprocess.PIPE)                            # Executes the Sikuli file for verifying clear tpm
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        output = output_for_clear_tpm.stdout.read()
        if "PASS" in output:
            library.write_log(lib_constants.LOG_INFO,"INFO All commands for "
                "clear_tpm executed successfully",test_case_id,script_id,
                              "None","None",loglevel,tbd)
            return True                                                         # returns True if all commands of clear tpm executed successfully
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL : Failed to execute"
                " All commands for clear_tpm or HOST machine "
                "is either minimised or closed or SUT "
                "is not opened inside the respective HOST machine",
                test_case_id,script_id,"None","None",loglevel,tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in library"
            " function clear_tpm as %s " %e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             #Write the exception error msg to log
        return False
################################################################################
# Function Name : tpm_msc_cmd
# Parameters    : testcaseid, scriptid, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to open the tpm.msc
################################################################################
def tpm_msc_cmd(test_case_id,script_id, loglevel ="ALL",tbd = None):
    try:
        os.chdir(lib_constants.SCRIPTDIR)
        if not os.system("start tpm.msc"):                                      #command to open tpm.msc file
            library.write_log(lib_constants.LOG_INFO,"INFO : Tpm.msc cmd"
                " executed successfully",test_case_id,script_id,
                              "None","None",loglevel,tbd)                       #Write the pass msg to log
            return True
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL : Failed to"
                " execute tpm.msc cmd",test_case_id,script_id,
                              "None","None",loglevel,tbd)                       #Write the fail msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in library"
            " function tpm_msc_cmd as %s " %e,
            test_case_id, script_id, "None", "None", loglevel, tbd)             #Write the exception error msg to log
        return False
################################################################################