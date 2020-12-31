__author__ = "kapilshx"
###########################General Imports######################################
import os
import subprocess
import time
import SendKeys
import pywinauto
import shutil
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_boot_to_environment
import lib_capture_screenshot
import lib_run_command
import lib_set_bios
################################################################################
# Function Name : set_hdd_bios_password
# Parameters    : hdd_token, test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : setting the HDD bios password in the
################################################################################
def set_hdd_bios_password(hdd_token, test_case_id, script_id,
                               loglevel="ALL", tbd="None"):                     #function to set the HDD_user password
    try:
        new_pwd = ""
        old_pwd = ""
        pwd = ""
        unlock_pwd_popup_flag = False
        if "from" in hdd_token.lower() and "to" in hdd_token.lower():           #extract the new and old password from token
            hdd_token =  hdd_token.split(" ")
            new_pwd, pos = library.extract_parameter_from_token(hdd_token, "to", 
                                                        "from", loglevel, tbd)
            old_pwd, pos = library.extract_parameter_from_token(hdd_token, 
                                                "from", "using", loglevel, tbd)
            unlock_pwd_popup_flag = True
        elif "from" not in hdd_token.lower() and "to" in hdd_token.lower():     #extract the password from token
            hdd_token =  hdd_token.split(" ")
            pwd, pos = library.extract_parameter_from_token(hdd_token, "to", 
                                                    "using", loglevel, tbd)
        else:                                                                   #if "from" & "to" are present in token
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG:Input syntax is "
            "incorrect for HDD/BIOS pssword", test_case_id, script_id, "None", 
                              "None", loglevel, tbd)
            return False
        mode, pos = library.extract_parameter_from_token(hdd_token, "the",
                                                "password", loglevel, tbd)      #extract mode from the token
        kvm_name = utils.ReadConfig("kvm_name", "name")                         # KVM is read from the config file
        kvm_title = utils.ReadConfig("kvm_name", "kvm_title")                   # kvm_title exe name fetched from config file
        activate_path = utils.ReadConfig("sikuli", "Activexe")                  # activate_path exe name fetched from config file
        sikuli_path = utils.ReadConfig("sikuli", "sikuli_path")                 # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli", "sikuli_exe")                   # Sikuli exe name fetched from config file
        port = utils.ReadConfig("BRAINBOX", "PORT")                             #Read brainbox port from config
        for item in [kvm_name, kvm_title, activate_path, port, sikuli_path, 
        sikuli_exe]:
            if "FAIL:" in item.strip():                                         #if config.ini entry is missing for any of the variable
                library.write_log(lib_constants.LOG_INFO, "INFO :Config entry is"
                " missing for tag variable under section sikuli, kvm_name and "
            "BRAINBOX", test_case_id, script_id, "None", "None", loglevel, tbd)
                return False                                                    # if the readconfig function returned fail it means no config entry is given
            else:
                pass

        if True == library.g3_reboot_system(loglevel, tbd):                     # Does a g3 if system is not in os
            pass
        else:
            library.write_log(lib_constants.LOG_INFO, "ERROR: Reboot failed",
            test_case_id, script_id, "None", "None", loglevel, tbd)
            return False

        if True == unlock_pwd_popup_flag:
            result_sendkeys = sendkeys_f2_specific("F2", loglevel, tbd)         #function to send keys F2 while system is restarting
        else:
            result_sendkeys = library.sendkeys("F2", loglevel, tbd)             #function to send keys F2 while system is restarting
        if True == result_sendkeys:
            library.write_log(lib_constants.LOG_INFO, "INFO: Key strokes "
            "sent", test_case_id, script_id, "None", "None", loglevel, 
            tbd)
            cur_os = lib_boot_to_environment.checkcuros(loglevel, tbd)                   #check whether system is in os or bios
            if ("EDK SHELL" == cur_os ):                                        # checks for the current state after pinging
                library.write_log(lib_constants.LOG_INFO, 
                "INFO: System boot to bios", test_case_id, script_id, 
                "None", "None", loglevel, tbd)
            else:                                                               #if system is still in OS
                library.write_log(lib_constants.LOG_DEBUG, 
                "DEBUG: Failed to send keys or system is still in OS", 
                 test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
        else:                                                                   #if fails to send the brainbix keys such as "F2"
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "send keys", test_case_id, script_id, "None", "None", 
            loglevel, tbd)
            return False
        if "hdd_user" in mode.lower():                                          #if mode is equals to the hdd_user
            if library.activate_kvm(test_case_id, script_id, loglevel, tbd):
                pass
            else:
                return False
            os.chdir(lib_constants.SCRIPTDIR)                                   #changing directory from tool dir to script dir
            if True == unlock_pwd_popup_flag:
                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)
                unlock_pwd_popup_flag = False
                if "unlock_pwd" in pwd_result:
                    pwd_result = "set_old"
                    if set_hdd_bios_pwd_type(pwd_result, old_pwd, test_case_id,
                                             script_id, loglevel, tbd):         #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False
            app = pywinauto.application.Application()                           #activate the KVM window using pywinauto
            time.sleep(lib_constants.FIVE_SECONDS)
            bios_cmd_list = ["{UP 3}", "{ENTER}", "{DOWN 3}", "{ENTER}",
                             "{ENTER}"]
            for command in bios_cmd_list:
                SendKeys.SendKeys(command)                                      #to go to boot maintainance manager menu option in bios and then go to set HDD security option in bios
                time.sleep(lib_constants.TWO)
            time.sleep(lib_constants.TWO)
            null_flag = False
            pwd_change_flag = False
            pwd_flag = False
            pwd_status = image_to_txt(test_case_id, script_id, loglevel, tbd)   #function call to capture the bios image and convert into text
            if "pwd_installed" == pwd_status:                                   #if password is set to some password
                if "null" == new_pwd.lower():                                   #new_pwd is equals to null in token
                    null_flag = True                                            # set the null_flag
                elif len(new_pwd.lower()) > 0:                                  #new_pwd is equals to some value in token
                    pwd_change_flag = True                                      # set the pwd_change_flag
                else:                                                           #input syntax is incorrect
                    library.write_log(lib_constants.LOG_INFO, "INFO:Input"
                        " syntax is incorrect ", test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)
                    return False
            elif "pwd_uninstalled" == pwd_status:                               #if password is set to null password
                if len(pwd.lower()) > 0:                                        #pwd is equals to some value in token
                    pwd_flag = True                                             #set the pwd_flag
                else:                                                           #input syntax is incorrect
                    library.write_log(lib_constants.LOG_INFO, "INFO:Input"
                        " syntax is incorrect ", test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)
                    return False
            else:                                                               #if unable the find the password status from image_to_txt() funtion call
                library.write_log(lib_constants.LOG_DEBUG, "DEBUG:Unable the "
                "find the password status from image_to_txt() funtion call", 
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
            pwd_status = ""
            time.sleep(lib_constants.TWO)
            kb = library.KBClass(port)
            kb.whiteKeys("Enter")                                               #send the whitekey from library
            kb.close()
            time.sleep(lib_constants.TWO)
            if True == pwd_flag:                                                #if only password is given in token
                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                       test_case_id,script_id, loglevel, tbd)   #function call to check the HDD_user password_popup
                if "set_new" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, pwd, test_case_id, 
                                                    script_id, loglevel, tbd):  #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                        test_case_id,script_id, loglevel, tbd)   #function call to check the HDD_user password_popup
                if "set_confirm" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, pwd, test_case_id, 
                                             script_id, loglevel, tbd):         #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False

            if True == null_flag:                                               #if null password is given in token

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                        test_case_id,script_id, loglevel, tbd)  #function call to check the HDD_user password_popup
                if "set_old" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, old_pwd, test_case_id, 
                                             script_id, loglevel, tbd):         #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)      #function call to check the HDD_user password_popup
                kb = library.KBClass(port)
                if "set_new" in pwd_result:
                    kb.whiteKeys("Enter")                                       #send the whitekey from library
                    time.sleep(lib_constants.TWO)
                    library.write_log(lib_constants.LOG_INFO, "INFO:New "
                    "password is set to null", test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)            #To set again new password
                else:
                    return False

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)      #function call to check the HDD_user password_popup
                if "set_confirm" in pwd_result:
                    kb.whiteKeys("Enter")                                       #send the whitekey from library
                    time.sleep(lib_constants.TWO)
                    library.write_log(lib_constants.LOG_INFO, "INFO:Confirm new "
                    "password is set to null", test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)            #To confirm new password
                else:
                    return False
                kb.close()
            if True == pwd_change_flag:                                         #if two passwtord (old and new) is given in token

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)      #function call to check the HDD_user password_popup
                if "set_old" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, old_pwd, test_case_id, 
                                             script_id, loglevel, tbd):         #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)      #function call to check the HDD_user password_popup
                if "set_new" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, new_pwd, test_case_id, 
                                             script_id, loglevel, tbd):         #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False

                pwd_result = set_hdd_bios_password_popup(unlock_pwd_popup_flag,
                                    test_case_id,script_id, loglevel, tbd)      #function call to check the HDD_user password_popup
                if "set_confirm" in pwd_result:
                    if set_hdd_bios_pwd_type(pwd_result, new_pwd, test_case_id, 
                                            script_id, loglevel, tbd):          #function call to set the password using brainbox
                        pass
                    else:
                        return False
                else:
                    return False
            if True == pwd_change_flag:                                         #if two password (old and new) is given in token
                pwd_status = image_to_txt(test_case_id, script_id, loglevel, tbd)
                if "pwd_installed" == pwd_status:                               #if password is showing installed in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Password is"
    " set to %s from %s successfully"%(new_pwd, old_pwd), test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)
                else:                                                           #if password is not showing installed in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Failed to "
    "verify that password is set to %s from %s "%(new_pwd, old_pwd), 
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                    return False
            if True == pwd_flag:                                                #if one password is given in token
                pwd_status = image_to_txt(test_case_id, script_id, loglevel, tbd)
                if "pwd_installed" == pwd_status:                               #if password is showing installed in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Password is"
                    " set to %s successfully"%(pwd), test_case_id, script_id, 
                                      "None", "None", loglevel, tbd)
                else:                                                           #if password is not showing installed in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Failed to "
                                "verify that password is set to %s"%(pwd), 
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                    return False
            if True == null_flag:                                               #if null password is given in token
                pwd_status = image_to_txt(test_case_id, script_id, loglevel, tbd)
                if "pwd_uninstalled" == pwd_status:                             #if password is showing uninstalled in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Password is"
                    " set to %s from %s successfully"%(new_pwd, old_pwd), 
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                else:                                                           #if password is not showing uninstalled in bios screen
                    library.write_log(lib_constants.LOG_INFO, "INFO:Failed to "
                "verify the password is set to %s from %s"%(new_pwd, old_pwd), 
                    test_case_id, script_id, "None", "None", loglevel, tbd)
                    return False
            bios_option_cmd_list = ["{F4}", "{Y}", "{ESC}", "{ESC}", "{ESC}",
                                    "{UP 2}", "{ENTER}"]
            for command in bios_option_cmd_list:                                #Loop to go back to bios setup starting menu
                SendKeys.SendKeys(command)
                time.sleep(lib_constants.TWO)
            time.sleep(lib_constants.TWENTY)
        else:                                                                   #if Input syntax is incorrect
            library.write_log(lib_constants.LOG_INFO, "INFO:Input syntax "
            "is wrong", test_case_id, script_id, "None", "None", loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in library"
        " function set_hdd_bios_password as %s"%e,
    test_case_id, script_id, "None", "None", loglevel, tbd)                     #if error occurs in library function set_hdd_bios_password
        return False
################################################################################
# Function Name : image_to_txt
# Parameters    : test_case_id, script_id, loglevel and tbd
# Return Value  : password status on success, False on failure
# Functionality : conversion image to txt file and parse the password status
#                 from txt file content
################################################################################
def image_to_txt(test_case_id, script_id, loglevel = "ALL", tbd = "None"):
    try:
        log_path = utils.ReadConfig("HDD_Password", "log_path")                 #read the log file path from config.ini file
        extract_file_path = utils.ReadConfig("HDD_Password", "extract_file_path")#read the extract.py file path from config.ini file
        extract_path = utils.ReadConfig("HDD_Password", "extract_path")         #read the extract folder path from config.ini file
        image_file_path = lib_constants.SCRIPTDIR + os.sep + \
                          script_id.split(".")[0] + ".png"
        image_file_name = script_id.split(".")[0] + ".png"
        for item in [log_path, extract_file_path, extract_path]:                #loop to check if config is missing for any of the tag variable
            if "FAIL:" in item.strip():
                library.write_log(lib_constants.LOG_INFO, "INFO :Config entry is"
                " missing for tag variable under section HDD_password", 
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                return False                                                    # if the readconfig function returned fail it means no config entry is given
            else:
                pass
        result, filename = lib_capture_screenshot.capture_screen(test_case_id, 
                                                        script_id, loglevel, tbd)#function to capture the screen of bios
        if os.path.exists(image_file_path):                                     #if image file already exists then removing it
            os.remove(image_file_path)
        os.rename(filename, image_file_path)
        if "True" == result:                                                    #if capture screen is done properly
            pass
        else:                                                                   #if capture screen is not done properly
            return False
        if os.path.exists(log_path):                                            #if log file already exists then removing it
            os.remove(log_path)
        os.chdir(extract_path)
        if os.path.exists(image_file_name):                                     #if image file already exists in extract folder then removing it
            os.remove(image_file_name)
        if os.path.exists(extract_path):                                        #checks if extract_path exists or not
            pass
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO :In the tools path "
            "tessa folder is not present under Extract_text_from_image", 
                    test_case_id, script_id, "None", "None", loglevel, tbd)
            return False
        shutil.copy(image_file_path, extract_path)                              #copy image file from script directory to extract_path
        cmd_for_image =  "C:\Python27\python.exe" +" " + extract_file_path \
                         +" " + image_file_name
        try:
            os.system(cmd_for_image)                                            #passing image file name as parameter for extract.py file
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                "running the extract.py file using command prompt due to %s " %e, 
                test_case_id, script_id, "None", "None", loglevel, tbd)         #if error occurs in running the extract.py file using command prompt
            return False
        time.sleep(lib_constants.THREE)
        os.chdir(lib_constants.SCRIPTDIR)
        pwd_uninstalled_flag = False
        pwd_installed_flag = False
        with open(log_path) as fp_pwd_status:                                   #loop to parse to password status in the log file
            fp_pwd = fp_pwd_status.readlines()
            for line in fp_pwd:
                if "HDD User Password Status" in line.strip():                  #if password status is found properly
                    if "NOT" in line.strip() or "NUT" in line.strip() or\
                                    "HUT" in line.strip():
                        pwd_uninstalled_flag  = True
                    else:
                        pwd_installed_flag = True
                else:                                                           #if password status is not found
                    pass
        if True == pwd_uninstalled_flag:                                        #if password status is found as not installed
            library.write_log(lib_constants.LOG_INFO, "INFO :Password not "
"installed, installing now", test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            return "pwd_uninstalled"
        elif True == pwd_installed_flag:                                        #if password status is found as installed
            library.write_log(lib_constants.LOG_INFO, "INFO :Password is "
    "installed already", test_case_id, script_id, "None", "None", loglevel, tbd)
            return "pwd_installed"
        else:                                                                   #if password status is not found
            library.write_log(lib_constants.LOG_INFO, "INFO :Failed to convert "
    "image file to text format file", test_case_id, script_id, "None", "None", 
                              loglevel, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "library function image_to_txt() due to %s " %e, 
            test_case_id, script_id, "None", "None", loglevel, tbd)             #if error occurs in library function image_to_txt
        return False
################################################################################
# Function Name : set_hdd_bios_password_popup
# Parameters    : unlock_pwd_popup_flag, test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : setting the HDD bios password in the
################################################################################
def set_hdd_bios_password_popup(unlock_pwd_popup_flag,test_case_id, script_id,
                               loglevel="ALL", tbd="None"):                     #function to set the HDD_user password_popup
    try:
        sikuli_path = utils.ReadConfig("sikuli", "sikuli_path")                 # Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli", "sikuli_exe")                   # Sikuli exe name fetched from config file
        os.chdir(sikuli_path)
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        if True == unlock_pwd_popup_flag:
            cmd_for_password = sikuli_exe + " unlock_pwd_popup.skl"
        else:
            cmd_for_password = sikuli_exe + " set_new_hdd_password.skl"
        output = subprocess.Popen(cmd_for_password, shell=False,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE)                       # Executes the Sikuli file for verifying clear tpm
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        output = output.stdout.read()
        if True == unlock_pwd_popup_flag:
            if "PASS" in output:
                return "unlock_pwd"
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO : Failed to get"
            " the Unlock HDD password popup in bios", test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return False
        else:
            if "set_new" in output:
                return "set_old"
            elif "set_again" in output:
                return "set_new"                                                    # returns True if all commands of clear tpm executed successfully
            elif "set_confirm" in output:
                return "set_confirm"
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO : Failed to get the "
                    "HDD password popup in bios", test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "library function set_hdd_bios_password_popup() due to %s " %e, 
            test_case_id, script_id, "None", "None", loglevel, tbd)             #if error occurs in library function image_to_txt
        return False
################################################################################
# Function Name : set_hdd_bios_pwd_type
# Parameters    : pwd_result, pwd_type, test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : To set the hdd_user password using brain box sendkeys
################################################################################
def set_hdd_bios_pwd_type(pwd_result, pwd_type, test_case_id, script_id, 
                               loglevel="ALL", tbd="None"):                     #function to set the HDD_user password_popup
    try:
        pwd_list = []
        port = utils.ReadConfig("BRAINBOX", "PORT")                             #Read brainbox port from config
        kb = library.KBClass(port)
        if "set_new" in pwd_result:
            for i in pwd_type:                                                  #loop to send the password one by one character
                kb.whiteKeys(i)                                                 #send the whitekey from library
                time.sleep(lib_constants.TWO)
                pwd_list.append(i)                                              #append the password to the list for displaying
            kb.whiteKeys("Enter")                                               #send the whitekey from library
            time.sleep(lib_constants.TWO)
            library.write_log(lib_constants.LOG_INFO, "INFO:New"
                " password is set to %s"%(pwd_list), test_case_id, 
                              script_id, "None", "None", loglevel, tbd)         #To set again new password
            kb.close()
            return True
        elif "set_confirm" in pwd_result:
            for i in pwd_type:                                                  #loop to send the password one by one character
                kb.whiteKeys(i)                                                 #send the whitekey from library
                time.sleep(lib_constants.TWO)
                pwd_list.append(i)                                              #append the password to the list for displaying
            kb.whiteKeys("Enter")                                               #send the whitekey from library
            time.sleep(lib_constants.TWO)
            library.write_log(lib_constants.LOG_INFO, "INFO:Confirm new "
                "password is set to %s"%(pwd_list), test_case_id,
                              script_id, "None", "None", loglevel, tbd)         #To confirm new password
            kb.close()
            return True
        elif "set_old" in pwd_result:
            for i in pwd_type:                                                  #loop to send the old password one by one character
                kb.whiteKeys(i)                                                 #send the whitekey from library
                time.sleep(lib_constants.TWO)
                pwd_list.append(i)                                              #append the password to the list for displaying
            kb.whiteKeys("Enter")                                               #send the whitekey from library
            time.sleep(lib_constants.TWO)
            library.write_log(lib_constants.LOG_INFO, "INFO:Old password"
                " is set to %s"%(pwd_list), test_case_id, script_id, 
                              "None", "None", loglevel, tbd)                    #To give old HDD user password
            kb.close()
            return True
    except Exception as e:
        kb.close()
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "library function set_hdd_bios_pwd_type() due to %s " %e, 
            test_case_id, script_id, "None", "None", loglevel, tbd)             #if error occurs in library function image_to_txt
        return False
################################################################################
# Function Name : sendkeys_f2_specific
# Parameters    : key, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality : sending the f2 key to boot to bios
################################################################################
def sendkeys_f2_specific(key, loglevel="ALL", tbd = None):
    try:
        port = utils.ReadConfig("BRAINBOX", "PORT")                             # reading port for brainbox activation from config file
        k1=library.KBClass(port)
        for num in range(1,80):                                                 # it sends the 'F2'keys in the range(1,80) times
            k1.whiteKeys(key)                                                   # Sending F2 keys to go to Bios page
            time.sleep(0.2)                                                     # Sending key strokes to load Bios
        time.sleep(5)
        k1.close()
        return True
    except Exception as e:
        k1.close()
        return False
################################################################################
# Function Name : xmlcli_set_hdd_bios_password
# Parameters    : hdd_token, test_case_id, script_id, loglevel and tbd
# Return Value  : True on success, False on failure
# Functionality : setting the HDD bios password in the
################################################################################
def xmlcli_set_hdd_bios_password(hdd_token, test_case_id, script_id,
                               log_level, tbd):                                  #function to set the HDD_user password
    try:
        new_pwd, pos1 = utils.extract_parameter_from_token(hdd_token, "to",
                                                           "using", tbd)
        mode, pos2 = utils.extract_parameter_from_token(hdd_token, "the" ,
                                                        "password", tbd)
        hdd_token = ' '.join(hdd_token)
        result = lib_set_bios.xmlcli_set_bios_security_option(new_pwd, mode,
                        test_case_id, script_id, log_level='ALL', tbd=None)
        if result == True:
            library.write_log(lib_constants.LOG_INFO,"INFO: Setting password ",
            "step is successfully executed" , test_case_id, script_id,
            log_level='All', tbd=None)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Setting password ",
            "step failed" , test_case_id, script_id, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Error: due to %s" % e,
                      test_case_id, script_id, log_level, tbd)
        return False



