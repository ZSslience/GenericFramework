__author__ = 'kapilshx\surabh1x'

############################General Python Imports##############################
import utils
import os
import subprocess
import time
############################Local Python Imports################################
import lib_constants
import library
import KBM_Emulation as kbm
################################################################################
# Function Name : authenticated_system_login_operation()
# Parameters    : login_token,test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to login the system using authenticated password
# Parameters implemented : text-password & bios
################################################################################
def authenticated_system_login_operation(login_token, test_case_id, script_id,
                               loglevel="ALL", tbd="None"):                     #function call boot to destination from F7 screen
    try:
        login_pwd = (login_token.split(" ")[-1]).strip(" ")
        sikuli_path = utils.ReadConfig("sikuli",'sikuli_path')
        sikuli_exe = utils.ReadConfig("sikuli",'sikuli_exe')
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")          # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                             # Extract com port details from config.ini
        if "FAIL:" in port or "FAIL:" in input_device_name:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                                                 "com port details or "
                                                 "input device name from "
                                                 "Config.ini ", "None", "None",
                      "None", "None", loglevel, tbd)                            # Failed to get info from config file
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: COM Port and input "
                                              "device name is identified as "
                                              "is identified as %s %s from "
                                              "config.ini"
                      % (port, input_device_name), "None", "None", "None",
                      "None", loglevel, tbd)
        for item in [sikuli_path, sikuli_exe,port]:
            if "FAIL:" in item.strip():                                         #if config.ini entry is missing for any of the variable
                library.write_log(lib_constants.LOG_INFO, "INFO :Config entry is"
                " missing for tag variable sikuli_path,"
                " sikuli_exe under section sikuli",
                test_case_id,script_id, "None", "None", loglevel, tbd)
                return False                                                    # if the readconfig function returned fail it means no config entry is given
            else:
                pass
        unlock_pwd_popup_file_path = sikuli_path + os.sep +"unlock_pwd_popup.skl"
        wrong_pwd_popup_file_path = sikuli_path + os.sep +"wrong_pwd_popup.skl"
        if os.path.exists(unlock_pwd_popup_file_path) and\
                    os.path.exists(wrong_pwd_popup_file_path):                  #to check if unlock_pwd_popup.skl and wrong_pwd_popup.skl are present in given config path
            library.write_log(lib_constants.LOG_INFO, "INFO:"
                " Unlock_pwd_popup.skl & wrong_pwd_popup.skl file are present"
                " in given config path",test_case_id,script_id, "None","None",
                              loglevel, tbd)
            pass
        else:                                                                   #if any one file unlock_pwd_popup.skl or  wrong_pwd_popup.skl is not present in given config path
            library.write_log(lib_constants.LOG_INFO, "INFO: Unlock_pwd_popup.skl"
                " or wrong_pwd_popup.skl file is not present in given config "
                "path",test_case_id,script_id, "None","None",loglevel, tbd)
            return False
        wrong_pwd_flag = False
        if run_sikuli_file(sikuli_path, sikuli_exe, wrong_pwd_flag, test_case_id,
                                script_id, loglevel, tbd):                      #function call to run the unlock_pwd_popup.skl file using subprocess
            pass
        else:
            return False
        pwd_list = []
        kb = kbm.USBKbMouseEmulation(input_device_name, port)                   #initialize the kbd-mouse class object
        try:
            if login_pwd is not None:
                for i in login_pwd:                                             #loop to send the password one by one character
                    kb.key_type(i)                                              #send the character one by one
                    time.sleep(lib_constants.TWO)
                    pwd_list.append(i)                                          #append the password to the list for displaying
                kb.key_press("KEY_ENTER")                                       #press enter
                time.sleep(lib_constants.TWO)
                library.write_log(lib_constants.LOG_INFO, "INFO:Login"
                    " password is set to %s"%(pwd_list), test_case_id,
                                  script_id, "None", "None", loglevel, tbd)     #To set again new password
                pass
            else:                                                               #Given password is invalid
                library.write_log(lib_constants.LOG_INFO,"INFO: Input password "
                    "%s is invalid"%(login_pwd),test_case_id, script_id, "None",
                                  "None",loglevel, tbd)
                return False

        except Exception as e:                                                  #exception occurs in sending keys through simulator
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in"
                " sending keys through simulator due to %s"%(e), test_case_id,
                    script_id, "None", "None",loglevel, tbd)
            return False
        wrong_pwd_flag = True
        if run_sikuli_file(sikuli_path, sikuli_exe, wrong_pwd_flag, test_case_id,
                                script_id, loglevel, tbd):                      #function call to run the wrong_pwd_popup.skl file using subprocess
            return True
        else:
            return False
    except Exception as e:                                                      #exception occurs in authenticated_system_login_operation() library function
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
            "authenticated_system_login_operation() library function  due"
            " to %s"%(e), test_case_id, script_id, "None", "None",loglevel, tbd)
        return False
################################################################################
# Function Name : run_sikuli_file
# Parameters    : sikuli_path,sikuli_exe,wrong_pwd_flag,test_case_id, script_id
#                 ,loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : to run the sikuli files using the subprocess
################################################################################
def run_sikuli_file(sikuli_path, sikuli_exe, wrong_pwd_flag, test_case_id,
                    script_id,loglevel="ALL", tbd="None"):                      #function to run the unlock_pwd_popup.skl and wrong_pwd_popup.skl file using subprocess
    try:
        if library.activate_kvm(test_case_id, script_id, loglevel, tbd):        #to activate the kvm
            pass
        else:
            return False
        os.chdir(sikuli_path)
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        if True == wrong_pwd_flag:                                              #if wrong_pwd_flag is true then run  wrong_pwd_popup.skl file
            cmd_for_password = sikuli_exe + " wrong_pwd_popup.skl"
        else:                                                                   #else run unlock_pwd_popup.skl file
            cmd_for_password = sikuli_exe + " unlock_pwd_popup.skl"
        output = subprocess.Popen(cmd_for_password, shell=False,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)                       # Executes the Sikuli file for verifying the password popup
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        output = output.stdout.read()
        if True == wrong_pwd_flag:
            if "FAIL" in output:                                                #if Given password is verified as valid password
                library.write_log(lib_constants.LOG_INFO, "INFO :Input password"
                    " is verified as valid password", test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return True
            else:                                                               #if Given password is verified as invalid password
                library.write_log(lib_constants.LOG_WARNING,"WARNING:Input "
                "password  is invalid", test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return False
        else:
            if "PASS" in output:                                                #if Unlock HDD password popup is confirmed in bios
                return True
            else:                                                               #if failed to get the Unlock HDD password popup in bios
                library.write_log(lib_constants.LOG_INFO, "INFO : Failed to get"
            " the Unlock HDD password popup in bios", test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return False
    except Exception as e:                                                      #exception occurs in run_sikuli_file() library function
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
            "run_sikuli_file() library function due to %s"%(e), test_case_id,
                          script_id, "None", "None", loglevel, tbd)
        return False
################################################################################