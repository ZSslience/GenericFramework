__author__ = "AsharanX/kapilshx/hvinayx"

#############################Python Imports#####################################
import library
import lib_constants
import utils
import time
import subprocess
import os
################################################################################
# Function Name : read_mebx
# Parameters    : tc_id, script_id, token, log_level and tbd
# Functionality : reads the mebx variables from bios
# Return Value  : True on option available in bios/False on missing options in
#                 Bios
################################################################################


def read_mebx(tc_id, script_id, token, log_level="ALL", tbd=None):

    try:
        bios_option = token.upper()
        kvm_name = utils.ReadConfig("kvm_name", "name")                         #KVM is read from the config file
        sikuli_path = utils.ReadConfig("sikuli", "sikuli_path")                 #Sikuli path fetched from the config file
        sikuli_exe = utils.ReadConfig("sikuli", "sikuli_exe")                   #Sikuli exe name fetched from config file

        if "FAIL:" in [kvm_name, sikuli_path, sikuli_exe]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "get th config entry for kvm_name, sikuli_path & sikuli_exe",
            tc_id, script_id, "None", "None", log_level, tbd)
            return False

        sikuli_cmd_for_mebx_all_options = " mebx_latest.skl"                    #Sikuli file for verifying storage redirection option in bios
        sikuli_cmd_for_mebx_login = " mebx_latest.skl"+" "+"mebx_login"         #Sikuli file for verifying Mebx Login page
        sikuli_cmd_for_mebx_page = " mebx_latest.skl"+" "+"mebx"                #Sikuli file for verifying Mebx interface page

        os.chdir(os.getcwd())
        time.sleep(lib_constants.SIKULI_EXECUTION_TIME)

        kvm_title = utils.ReadConfig("kvm_name", "kvm_title")
        title = kvm_name + " - " + kvm_title                                    #KVM command for activating the kvm window

        activate_path = utils.ReadConfig("sikuli", "Activexe")
        window_path = activate_path + " " + title
        kvm_activate = subprocess.Popen(window_path, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdin=subprocess.PIPE)    #KVM window is activated from the host

        os.chdir(sikuli_path)
        output = None

        if bios_option == "MEBX":
            cmd_for_mebx_page = sikuli_exe + sikuli_cmd_for_mebx_page
            sikuli_execution = subprocess.Popen(cmd_for_mebx_page, shell=False,
                                                stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE,
                                                stderr=subprocess.PIPE)

            output = sikuli_execution.stdout.read()
            if "MEBx boot is successful" in output:
                library.write_log(lib_constants.LOG_INFO, "INFO: Verified MEBx"
                " Page", tc_id, script_id, "None", "None", log_level, tbd)
                return True                                                     #Returns True if the home button functionality is verified succesfully
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to verify MEBx Page", tc_id, script_id, "None", "None",
                log_level, tbd)
                return False

        cmd_for_mebx_login = sikuli_exe + sikuli_cmd_for_mebx_login
        sikuli_execution = subprocess.Popen(cmd_for_mebx_login, shell=False,
                                            stdout=subprocess.PIPE,
                                            stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

        mebx_login = sikuli_execution.stdout.read()
        if "MEBx login successful" in mebx_login:
            library.write_log(lib_constants.LOG_INFO, "INFO: MEBX Login "
            "successfull", tc_id, script_id, "None", "None", log_level, tbd)  	#Returns True if option is present in bios

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Mebx login "
            "failed", tc_id, script_id, "None", "None", log_level, tbd)
            os.chdir(lib_constants.SCRIPTDIR)
            return False                                                        #Returns False if option is not available in bios
        
        if "MANAGEABILITY FEATURE" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "manageability_feature"

        elif "PASSWORD POLICY" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "Password_policy"

        elif "READ MEBX LOCAL FW UPDATE" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "local_fw_update"

        elif "LOCAL FW UPDATE = ENABLED, DISABLED, PASSWORD PROTECTED" in \
                bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "local_fw_update_all_option_verify"

        elif "DHCP" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "dhcp"

        elif "READ MEBX FW UPDATE" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "fw_update"

        elif "FW UPDATE = ENABLED, DISABLED, PASSWORD PROTECTED" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "fw_update_all_option_verify"

        elif "IDLE TIMEOUT" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "idle_timeout"

        elif "AMT ON IN HOST SLEEP STATES" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "intel_amt_on_host_sleep_states"

        elif "AMT CONFIGURATION MENU" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "amt_menu"                                   #Sikuli command to verify amt configuration menu

        elif "CURRENT PROVISIONING MODE" in bios_option:
            cmd_for_sikuli = sikuli_exe + sikuli_cmd_for_mebx_all_options + \
                             " " + "cpm"                                        #Sikuli command to verify current provisioning mode

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Input syntax"
            " is incorrect", tc_id, script_id, "None", "None", log_level, tbd)
            return False                                                        #Returns False if option is not available in bios

        sikuli_execution = subprocess.Popen(cmd_for_sikuli, shell=False,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE)
        output = sikuli_execution.stdout.read()
        
        if "PASS" in output:
            with open("log.txt", "w") as fwr:
                fwr.writelines(output)

            with open("log.txt", "r") as fin:
                fout = fin.readlines()
                for line in fout:
                    if "PASS" in line:
                        out = (line.split(":")[1]).strip("\n").\
                            strip("\r").strip(" ")
                        break

            os.remove("log.txt")

            library.write_log(lib_constants.LOG_INFO, "INFO: %s bios option is"
            " equal to %s"%(bios_option, out), tc_id, script_id, "None", "None",
            log_level, tbd)
            utils.write_to_Resultfile(out, script_id)
            os.chdir(lib_constants.SCRIPTDIR)
            return True                                                         #Returns True if option is present in bios
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is "
            "unsuccessful in bios"%bios_option, tc_id, script_id, "None",
            "None", log_level, tbd)
            os.chdir(lib_constants.SCRIPTDIR)
            return False                                                        #Returns False if option is not available in bios

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e, tc_id,
        script_id, "None", "None", log_level, tbd)                              #Write the exception error msg to log
        os.chdir(lib_constants.SCRIPTDIR)
        return False