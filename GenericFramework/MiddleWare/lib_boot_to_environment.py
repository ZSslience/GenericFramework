__author__ = "Automation Development Team"

# General Python Imports
import os
import subprocess
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_remote_reboot
import lib_verify_device_functionality
import KBM_Emulation as kbm
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations

################################################################################
# Function Name : checkcuros()
# Parameters    : None
# Return Value  : Returns the current system state (OS, EDK Shell, BIOS Setup)
# Functionality : check for current system state
################################################################################


def checkcuros(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        sut_ip = utils.ReadConfig("SUT_IP", "IP")                               # Reading IP from the config file section SUT_IP

        if "FAIL" in sut_ip:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the config entry IP under [SUT_IP]",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: config entry "
                              "IP under [SUT_IP] fetched", test_case_id,
                              script_id, "None", "None", log_level, tbd)

        os.chdir(os.getcwd())
        os.system("ping " + sut_ip + " > Result.txt")                           # Writing the ping status in result.txt file

        flag = 0
        with open('Result.txt', 'r') as file:                                   # Open Result.txt in read mode
            for line in file:
                if 'Destination host unreachable.' in line:
                    flag = 1
                    break
                elif 'could not find' in line:
                    flag = 1
                    break
                elif 'Request timed out.' in line:
                    flag = 1
                    break
            file.close()

        if flag == 1:                                                           # If flag ==1 system is either in edk shell or bios
            with open("Verify.txt", "w") as file:                               # Open Verify.txt in write mode
                file.write("SUT is in EDK")
                file.close()

                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current state is either EDK or BIOS",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return "EDK SHELL"
        else:
            result, current_post_code = lib_ttk2_operations.\
                check_for_post_code(lib_constants.OS_POSTCODE,
                                    lib_constants.TWO_MIN, test_case_id,
                                    script_id, log_level, tbd)
            if current_post_code not in lib_constants.NON_OS_POST_CODE and \
               current_post_code in lib_constants.OS_POSTCODE and result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Ping operation"
                                  " successful to target machine %s" % sut_ip,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current state is OS", test_case_id,
                                  script_id, "None", "None", log_level, tbd)

                with open("Verify.txt", "w") as file:                           # Open Verify.txt in write mode
                    file.write("SUT is in OS")
                    file.close()
                return "OS"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : change_bootorder_in_edkshell()
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Sets EDKas first boot order. Triggered from host
# Functionality : Changes boot order from edk shell
################################################################################


def change_bootorder_in_edkshell(test_case_id, script_id, log_level="ALL",
                                 tbd=None):                                     # Boot order change in EDK shell

    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get com port details or input device name from "
                              "Config.ini ", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           # Failed to get info from config file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name is identified as is "
                              "identified as %s %s from config.ini"
                              % (port, input_device_name), test_case_id,
                              script_id, "None", "None", log_level, tbd)

        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        time.sleep(lib_constants.SEND_KEY_TIME)
        k1.key_type("bcfg boot mv 1 0")                                         #sending command to change boot order
        k1.key_press("KEY_ENTER")                                               #pressing enter key
        time.sleep(lib_constants.SEND_KEY_TIME)
        k1.key_type("reset")                                                    #sending command to reset
        k1.key_press("KEY_ENTER")                                               #pressing enter key
        time.sleep(lib_constants.LONG_TIME)
        library.write_log(lib_constants.LOG_INFO, "INFO: Keys sent from "
                          "keyboard-mouse simulator to change boot order in "
                          "EDK successfully", test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : change_bootorder_in_os()
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Changes OS as first boot order. Triggered from host
# Functionality : Changing boot order in os level
################################################################################


def change_bootorder_in_os(test_case_id, script_id, log_level="ALL",
                           tbd=None):                                           # Boot order change in OS

    try:
        if library.set_multiple_bootorder(test_case_id, script_id, log_level,
                                          tbd) is True:
            library.write_log(lib_constants.LOG_INFO, "INFO: Boot order "
                              "changed to EDK shell in OS", test_case_id,
                              script_id, "None", "None", log_level, tbd)        # Checking if multiple boot order set function returns true
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "change bootorder to edk in OS", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name  : boot_to_mebx
# Parameters     : test_case_id, script_id, log_level and tbd
# Functionality  : for to boot to mebx
# Return Value   : True on Successful action, False Otherwise
################################################################################


def boot_to_mebx(test_case_id, script_id, log_level="ALL", tbd="None"):

    try:
        port = utils.ReadConfig("BRAINBOX", "PORT")                             #Extracting port for brainbox activation from config file

        k1 = library.KBClass(port)

        for num in range(1, 25):                                                #Sends the 'Ctrl+P' keys in the range(1,25) times
            k1.combiKeys("Ctrl+p")

        library.write_log(lib_constants.LOG_INFO, "INFO: 'Ctrl+p' Key sent "
                          "successfully", test_case_id, script_id, "None",
                          "None", log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : simics_sendkeys
# Parameters    : test_case_id, script_id, tool, key
# Return Value  : Returns True if key send successfully else False
# Functionality : To send key signals to Simics environment
################################################################################


def simics_sendkeys(tool, key):

    time.sleep(lib_constants.THREE)
    cmd = tool + " " + key                                                      # Getting the command with tool name and actual key
    time.sleep(lib_constants.THREE)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, stdin=subprocess.PIPE)   # Executing the command
    stdout, stderr = process.communicate()                                      # Getting command output and error information

    if len(stderr) > 0:
        return False                                                            # Function exists by Returning False if error occurs
    else:
        return True                                                             # Function exists by Returning True if no error occurs

################################################################################
# Function Name : system_in_os
# Parameters    : test_case_id, script_id, delay
# Return Value  : Returns True if Ping is successful else False
# Functionality : Ping the system for n iterations to confirm whether
#                 system is in OS
################################################################################


def system_in_os(delay):

    for i in range(int(delay)):
        target_ip = utils.ReadConfig("SUT_IP", "IP")                            # Getting system name from Config file
        if "incorrect or Config.ini does not contain" in target_ip:
            return False                                                        # Function exists by Returning False if Config file is not updated
        else:
            cmd = "ping ", target_ip                                            # Getting command to ping with sut name
            response = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdin=subprocess.PIPE)                  # Executing Ping command
            stdout, stderr = response.communicate()                             # Getting command output and error information

            if stdout != None and stdout.count("Reply from") == 4:              # Verifying whether Ping is successful
                if stdout != None and stdout.count(": bytes=32") == 4:          # Verifying whether Ping is successful
                    return True                                                 # Function exists by Returning True if Ping is successful
            else:
                pass                                                            # Continues the loop if Ping is unsuccessful till delay
    return False                                                                # Returning False if ping was not successful in the given delay


################################################################################
# Function Name : boot_from_bios
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if system is in OS else False
# Functionality : To boot the system to OS from BIOS
################################################################################


def boot_from_bios(test_case_id, script_id, log_level="ALL", tbd=None):

    tool = lib_constants.TOOLPATH + "\\simicscmd.exe"

    if simics_sendkeys(tool, "cold-reset"):                                     # Calling send keys function to reboot Simics setup when Ping fails
        if system_in_os(lib_constants.SIXTY_ONE):                               # Calling Ping function to confirm whether system is in OS after cold-reset
            library.write_log(lib_constants.LOG_INFO, "INFO: System booted to "
                              "OS from BIOS", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return True                                                         # Function exists by Returning True if sendkey is successful
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "boot the Simics setup from BIOS", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False                                                        # Function eixsts by Returning True if sendkey is unsuccessful

################################################################################
# Function Name : boot_from_efi
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if system is in OS else False
# Functionality : To boot the system to OS from EFI Shell
################################################################################


def boot_from_efi(test_case_id, script_id, log_level="ALL", tbd=None):

    tool = lib_constants.TOOLPATH + "\\Mouse_Click.exe"                         # Calling Mouse-Click function to activate Simics HAS setup
    process = subprocess.Popen(tool, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, stdin=subprocess.PIPE)   # Executing Mouse_Click utility
    stdout, stderr = process.communicate()                                      # Getting command output and error information

    tool = lib_constants.TOOLPATH + "\\simicssut.exe"

    if simics_sendkeys(tool, '"bcfg boot mv 1 0"'):                             # Calling send keys function to boot Simics setup from EDK shell when Cold-Reset fails
        if simics_sendkeys(tool, "{ENTER}"):
            if simics_sendkeys(tool, "reset"):
                if simics_sendkeys(tool, "{ENTER}"):
                    if system_in_os(lib_constants.DEFAULT_SX_TIME):             # Calling Ping function to confirm whether system is in OS after booting from EDK Shell
                        time.sleep(lib_constants.LONG_TIME)
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System booted to OS from EFI Shell",
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True                                             # Function exists by Returning True if system booted to OS from EDK Shell
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Unable to Boot to OS",
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False                                            # Function exists by Returning False if system is not booting to OS from EDK Shell
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Booting from "
                          "EDK Shell Failed", test_case_id, script_id, "None",
                          "None", loglevel, tbd)
        return False

################################################################################
# Function Name : boot_to_os_presi
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if system is in OS else False
# Functionality : To boot the system to OS from BIOS / EDK Shell
################################################################################


def boot_to_os_presi(test_case_id, script_id, log_level="ALL", tbd=None):

    if system_in_os(lib_constants.TWO):                                         # Calling ping function for 2 iterations
        library.write_log(lib_constants.LOG_INFO, "INFO: System is already "
                          "in OS", test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return True                                                             # Function exists by Returning True if Ping is successful
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: System is not in OS, "
                          "Initiating reboot", test_case_id, script_id, "None",
                          "None", log_level, tbd)

        if boot_from_bios(test_case_id, script_id, log_level, tbd=None):        # Calling "boot_from_bios" function to boot the Simics setup to OS from BIOS
            return True                                                         # Function exists by Returning True if Simics setup is in OS
        elif boot_from_efi(test_case_id, script_id, log_level, tbd=None):       # Calling "boot_from_bios" function to boot the Simics setup to OS from BIOS
            return True                                                         # Function exists by Returning True if Simics setup is in OS
        else:
            return False                                                        # Function exists by Returning False if Simics setup is not in OS

################################################################################
# Function Name : boot_to_bios_setup_presi
# Parameters    : test_case_id= Test case id; script_id = Script id
# Return Value  : Returns True if system is in BIOS Setup else False
# Functionality : To boot the system to BIOS by sending F2 key
################################################################################


def boot_to_bios_setup_presi(test_case_id, script_id, log_level="ALL",
                             tbd=None):

    tool = lib_constants.TOOLPATH + "\\simicscmd.exe"
    if simics_sendkeys(tool, "cold-reset"):                                     # Calling send keys function to reboot Simics setup
        library.write_log(lib_constants.LOG_INFO, "INFO: Cold-Reset done",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        time.sleep(lib_constants.THREE)

        tool = lib_constants.TOOLPATH + "\\simicssut.exe"
        for i in range(lib_constants.SHORT_TIME):
            simics_sendkeys(tool, "{F2}")                                       # Calling send keys function to send [F2] key for 50 iterations

        time.sleep(lib_constants.THREE)
        simics_sendkeys(tool, "Y")                                              # Calling send keys function to send [Y] key

        library.write_log(lib_constants.LOG_INFO, "INFO: Booting to BIOS "
                          "Setup successful", test_case_id, script_id,
                          log_level, tbd)
        return True                                                             # Function exists by Returning True if Send Keys are successful
    else:
        library.write_log(lib_constants.LOG_WARNING, "INFO: Booting to BIOS "
                          "Setup Failed", test_case_id, script_id, "None",
                          "None", log_level, tbd)
        return False                                                            # Function exists by Returning False if Send Keys are unsuccessful

################################################################################
# Function Name : cold_reset_with_ping
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if system is not in OS else False
# Functionality : To confirm System is not in OS after reboot
################################################################################


def cold_reset_with_ping(test_case_id, script_id, log_level="ALL", tbd=None):

    tool = lib_constants.TOOLPATH + "\\simicscmd.exe"

    if simics_sendkeys(tool, "cold-reset"):                                     # Calling send keys function to reboot Simics setup
        if not system_in_os(lib_constants.SHORT_TIME):                          # Calling ping function for 50 iterations
            library.write_log(lib_constants.LOG_INFO, "INFO: System is not in "
                              "OS", test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True                                                         # Function exists by Returning True if ping is unsuccessful
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: System is in OS",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False                                                        # Function exists by Returning False if ping is successful

################################################################################
# Function Name : boot_to_state_presi
# Parameters    : token, test_case_id, script_id, log_level, tbd
# Return Value  : Returns True and False w.r.t token and function
# Functionality : To call respective function for token "OS" and "SETUP"
################################################################################


def boot_to_state_presi(token, test_case_id, script_id, log_level="ALL",
                        tbd=None):

    try:
        if token != "bios setup":
            return boot_to_os_presi(test_case_id, script_id, log_level, tbd)    # Calling "boot_to_os_presi" function if token is "OS" or "SETUP"
        if token == "bios setup":
            return boot_to_bios_setup_presi(test_case_id, script_id, log_level,
                                            tbd)                                # Calling "boot_to_bios_setup_presi" function if token is "BIOS SETUP"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : boot_to_state_presi2
# Parameters    : token,test_case_id, script_id, log_level, tbd
# Return Value  : Returns True and False w.r.t token and function
# Functionality : To call respective function for token "EDK SHELL"
################################################################################


def boot_to_edk_presi(token, test_case_id, script_id, log_level, tbd):

    try:
        if token == "edk shell" or token == "EFI":
            return cold_reset_with_ping(test_case_id, script_id, log_level,
                                        tbd)                                    # Calling "cold_reset_with_ping" function if token is "EDK SHELL"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False                                                            # Function exists by Returning False when Exception arises


def boot_to_os_setup(original_string, test_case_id, script_id,
                     log_level="ALL", tbd=None):

    try:
        parameter = str(original_string.split(" ")[-1])

        current_postcode = lib_ttk2_operations.\
            read_post_code(test_case_id, script_id, log_level, tbd)

        if current_postcode in lib_constants.OS_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System current "
                              "post code is %s" % str(current_postcode),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

            time.sleep(30)

            current_environment = checkcuros(test_case_id, script_id,
                                             log_level, tbd)

            if "OS" == current_environment.upper() and \
               ("setup" == parameter.lower() or "os" == parameter.lower()):
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "desired %s" % parameter, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True

            elif current_postcode in lib_constants.EFI_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current post code is %s and it is in EDK "
                                  "Shell" % str(current_postcode),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                if change_bootorder_in_edkshell(test_case_id, script_id,
                                                log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Changed "
                                      "boot order in EDK Shell successfully to"
                                      " boot to %s" % parameter, test_case_id,
                                      script_id, "None", "None", log_level, tbd)

                    if lib_remote_reboot.\
                        monitor_service_up(test_case_id, script_id, log_level,
                                           tbd):
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System booted to %s successfully"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " System not booted to %s"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to change boot order in EDK "
                                      "Shell to boot to %s" % parameter,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            elif current_postcode in lib_constants.BIOS_PAGE_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current post code is %s and it is in BIOS "
                                  "Setup" % str(current_postcode),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                if lib_verify_device_functionality.\
                    press_keys("KB Simulator", "BIOS", test_case_id, script_id,
                               log_level, tbd):
                    if lib_remote_reboot.\
                        monitor_service_up(test_case_id, script_id, log_level,
                                           tbd):
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System booted to %s successfully"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: System not booted to %s"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to press keys in BIOS Setup for "
                                      "to boot to %s" % parameter,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                if "FFFF" == current_postcode.upper() or \
                   "B505" == current_postcode.upper():
                    library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                      "current post code is %s and it is in "
                                      "Shutdown State" % str(current_postcode),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)

                    if library.g3_reboot_system(test_case_id, script_id,
                                                log_level, tbd):
                        if lib_remote_reboot.\
                            monitor_service_up(test_case_id, script_id,
                                               log_level, tbd):
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "System booted to %s successfully"
                                              % parameter, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return True
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: System not booted to "
                                              "%s" % parameter, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return False
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "Failed to perform G3 remote reboot",
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
        elif current_postcode in lib_constants.EFI_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System current "
                              "post code is %s and it is in EDK Shell"
                              % str(current_postcode), test_case_id, script_id,
                              "None", "None", log_level, tbd)

            if change_bootorder_in_edkshell(test_case_id, script_id,
                                            log_level, tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: Changed boot "
                                  "order in EDK Shell successfully to boot to "
                                  "%s" % parameter, test_case_id, script_id,
                                  "None", "None", log_level, tbd)

                if lib_remote_reboot.\
                    monitor_service_up(test_case_id, script_id, log_level,
                                       tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                      "booted to %s successfully" % parameter,
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "System not booted to %s" % parameter,
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to change boot order in EDK Shell to boot "
                                  "to %s" % parameter, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        elif current_postcode in lib_constants.BIOS_PAGE_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System current "
                              "post code is %s and it is in BIOS Setup"
                              % str(current_postcode), test_case_id, script_id,
                              "None", "None", log_level, tbd)

            if lib_verify_device_functionality.\
                press_keys("KB Simulator", "BIOS", test_case_id, script_id,
                           log_level, tbd):
                if lib_remote_reboot.\
                    monitor_service_up(test_case_id, script_id, log_level,
                                       tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: System"
                                      " booted to %s successfully" % parameter,
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "System not booted to %s" % parameter,
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to press keys in BIOS Setup for to boot to "
                                  "%s" % parameter, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
        elif current_postcode in lib_constants.S3_POSTCODE or current_postcode \
                in lib_constants.S4_POSTCODE:
            power = utils.ReadConfig("TTK", "POWER")
            if "FAIL:" in power:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to get config entry for "
                                  "Power button from Config.ini",
                                  test_case_id, script_id, "TTK2",
                                  "NONE", log_level, tbd)
                return False
            power_button_press = lib_ttk2_operations.\
                press_release_button(int(1), int(1), power,int(30),
                                     test_case_id, script_id, log_level, tbd)
            if power_button_press:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Power button pressed successfully ",
                                  test_case_id, script_id,
                                  "TTK2", "None", log_level, tbd)
                if lib_remote_reboot. \
                        monitor_service_up(test_case_id, script_id,
                                           log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: System booted to %s successfully"
                                      % parameter, test_case_id,
                                      script_id, "None", "None",
                                      log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                                      "WARNING: System not booted to "
                                      "%s" % parameter, test_case_id,
                                      script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_ERROR,
                                  "Failed to press Power button ",
                                  test_case_id, script_id, "TTK2", "None",
                                  log_level, tbd)
                return False
        else:
            if "FFFF" == current_postcode.upper() or \
               "B505" == current_postcode.upper() or \
               "B503" == current_postcode.upper():
                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current post code is %s and it is in "
                                  "Shutdown State" % str(current_postcode),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                if library.g3_reboot_system(test_case_id, script_id,
                                            log_level, tbd):
                    time.sleep(50)
                    current_postcode = lib_ttk2_operations. \
                        read_post_code(test_case_id, script_id, log_level, tbd)

                    if current_postcode in lib_constants.EFI_POSTCODE:
                        library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                          "current post code is %s and it is in"
                                          " EDK Shell" % str(current_postcode),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)

                        if change_bootorder_in_edkshell(test_case_id, script_id,
                                                    log_level, tbd):
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Changed boot order in EDK Shell "
                                              "successfully to boot to "
                                              "%s" % parameter, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)

                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to change boot "
                                              "order in EDK Shell to boot to %s"
                                              % parameter, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return False

                    if lib_remote_reboot.\
                        monitor_service_up(test_case_id, script_id,
                                           log_level, tbd):
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System booted to %s successfully"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: System not booted to %s"
                                          % parameter, test_case_id, script_id,
                                          "None", "None", log_level, tbd)
                        return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to perform G3 remote reboot",
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    return False
            else:
                result = lib_remote_reboot.\
                    monitor_service_up(test_case_id, script_id, log_level, tbd)

                if result:
                    library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                      "booted to %s successfully"
                                      % parameter, test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                                      "WARNING: System not booted to %s"
                                      % parameter, test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def boot_to_bios_setup(original_string, test_case_id, script_id,
                       log_level="ALL", tbd=None):

    try:
        parameter = str(original_string.split("to")[-1]).strip()

        current_postcode = lib_ttk2_operations.\
            read_post_code(test_case_id, script_id, log_level, tbd)

        if current_postcode in lib_constants.OS_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System current "
                              "post code is %s and it is in OS"
                              % str(current_postcode), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            if library.g3_reboot_system(test_case_id, script_id, log_level,
                                        tbd):
                if library.sendkeys("F2", test_case_id, script_id, log_level,
                                    tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: F2 Key "
                                      "pressed successfully for to boot to "
                                      "%s" % parameter, test_case_id,
                                      script_id, "None", "None", log_level, tbd)

                    current_environment = checkcuros(test_case_id, script_id,
                                                     log_level, tbd)

                    if "OS" == current_environment.upper():
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: Failed to boot to %s"
                                          % parameter, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return False
                    else:
                        current_postcode = lib_ttk2_operations. \
                            read_post_code(test_case_id, script_id, log_level,
                                           tbd)

                        if current_postcode in lib_constants.EFI_POSTCODE:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "System current post code is %s "
                                              "and it is in EDK Shell"
                                              % current_postcode, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)

                            if change_bootorder_in_edkshell(test_case_id,
                                                            script_id,
                                                            log_level, tbd):
                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: Changed boot order in"
                                                  " EDK Shell successfully to "
                                                  "boot to %s" % parameter,
                                                  test_case_id, script_id,
                                                  "None", "None", log_level,
                                                  tbd)

                                if library.sendkeys("F2", test_case_id,
                                                    script_id, log_level, tbd):
                                    library.write_log(lib_constants.LOG_INFO,
                                                      "INFO: F2 Key pressed "
                                                      "successfully for to "
                                                      "boot to %s" % parameter,
                                                      test_case_id, script_id,
                                                      "None", "None", log_level,
                                                      tbd)

                                    current_postcode = lib_ttk2_operations.\
                                        read_post_code(test_case_id, script_id,
                                                       log_level, tbd)

                                    if current_postcode in \
                                            lib_constants.BIOS_PAGE_POSTCODE:
                                        library.write_log(lib_constants.
                                                          LOG_INFO, "INFO: "
                                                          "System booted to %s"
                                                          % parameter,
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)
                                        return True
                                    else:
                                        library.write_log(lib_constants.
                                                          LOG_WARNING,
                                                          "WARNING: Failed to "
                                                          "boot to %s"
                                                          % parameter,
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)
                                        return False
                                else:
                                    library.write_log(lib_constants.
                                                      LOG_WARNING, "WARNING: "
                                                      "Failed to press F2 "
                                                      "keys", test_case_id,
                                                      script_id, "None", "None",
                                                      log_level, tbd)
                                    return False
                            else:
                                library.write_log(lib_constants.LOG_WARNING,
                                                  "WARNING: Failed to change "
                                                  "boot order in EDK Shell",
                                                  test_case_id, script_id,
                                                  "None", "None", log_level,
                                                  tbd)
                                return False
                        elif current_postcode in \
                                lib_constants.BIOS_PAGE_POSTCODE:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "System booted to %s" % parameter,
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            return True
                        else:
                            if "FFFF" == current_postcode.upper() or \
                               "B505" == current_postcode.upper():
                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: System current post "
                                                  "code is %s and it is in "
                                                  "Shut down State"
                                                  % str(current_postcode),
                                                  test_case_id,
                                                  script_id, "None", "None",
                                                  log_level, tbd)
                                if library.g3_reboot_system(test_case_id,
                                                            script_id,
                                                            log_level, tbd):
                                    if library.sendkeys("F2", test_case_id,
                                                        script_id, log_level,
                                                        tbd):
                                        library.write_log(lib_constants.
                                                          LOG_INFO, "INFO: F2 "
                                                          "Key pressed "
                                                          "successfully for "
                                                          "to boot to %s"
                                                          % parameter,
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)

                                        current_postcode = lib_ttk2_operations.\
                                            read_post_code(test_case_id,
                                                           script_id,
                                                           log_level, tbd)

                                        if current_postcode in lib_constants.\
                                                BIOS_PAGE_POSTCODE:
                                            library.write_log(lib_constants.
                                                              LOG_INFO, "INFO:"
                                                              " System booted "
                                                              "to %s"
                                                              % parameter,
                                                              test_case_id,
                                                              script_id,
                                                              "None", "None",
                                                              log_level, tbd)
                                            return True
                                        else:
                                            library.write_log(lib_constants.
                                                              LOG_WARNING,
                                                              "WARNING: Failed"
                                                              " to boot to %s"
                                                              % parameter,
                                                              test_case_id,
                                                              script_id,
                                                              "None", "None",
                                                              log_level, tbd)
                                            return False
                                    else:
                                        library.write_log(lib_constants.
                                                          LOG_WARNING,
                                                          "WARNING: Failed to "
                                                          "press F2 keys",
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)
                                        return False
                                else:
                                    library.write_log(lib_constants.LOG_WARNING,
                                                      "WARNING: Failed to "
                                                      "perform G3 remote "
                                                      "reboot", test_case_id,
                                                      script_id, "None", "None",
                                                      log_level, tbd)
                                return False
        elif current_postcode in lib_constants.BIOS_PAGE_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System already in"
                              " desired %s" % parameter, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        elif current_postcode in lib_constants.EFI_POSTCODE:
            library.write_log(lib_constants.LOG_INFO, "INFO: System current "
                              "post code is %s and it is in EDK Shell"
                              % str(current_postcode), test_case_id,
                              script_id, "None", "None",
                              log_level, tbd)
            if change_bootorder_in_edkshell(test_case_id, script_id, log_level,
                                            tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: Changed boot "
                                  "order in EDK Shell successfully to boot to "
                                  "%s" % parameter, test_case_id, script_id,
                                  "None", "None", log_level, tbd)

                if library.sendkeys("F2", test_case_id, script_id, log_level,
                                    tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: F2 Key "
                                      "pressed successfully for to  boot to %s"
                                      % parameter, test_case_id, script_id,
                                      "None", "None", log_level, tbd)

                    current_postcode = lib_ttk2_operations.\
                        read_post_code(test_case_id, script_id, log_level, tbd)

                    if current_postcode in lib_constants.BIOS_PAGE_POSTCODE:
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System booted to %s" % parameter,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        if "FFFF" == current_postcode.upper() or \
                           "B505" == current_postcode.upper():
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "System current post code is %s "
                                              "and it is in Shut down State"
                                              % str(current_postcode),
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            if library.g3_reboot_system(test_case_id,
                                                        script_id, log_level,
                                                        tbd):
                                if library.sendkeys("F2", test_case_id,
                                                    script_id, log_level, tbd):
                                    library.write_log(lib_constants.LOG_INFO,
                                                      "INFO: F2 Key pressed "
                                                      "successfully for system "
                                                      "boot to %s" % parameter,
                                                      test_case_id, script_id,
                                                      "None", "None",
                                                      log_level, tbd)

                                    current_postcode = lib_ttk2_operations.\
                                        read_post_code(test_case_id, script_id,
                                                       log_level, tbd)

                                    if current_postcode in \
                                            lib_constants.BIOS_PAGE_POSTCODE:
                                        library.write_log(lib_constants.
                                                          LOG_INFO, "INFO: "
                                                          "System booted to %s"
                                                          % parameter,
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)
                                        return True
                                    else:
                                        library.write_log(lib_constants.
                                                          LOG_WARNING,
                                                          "WARNING: Failed to "
                                                          "boot to %s"
                                                          % parameter,
                                                          test_case_id,
                                                          script_id, "None",
                                                          "None", log_level,
                                                          tbd)
                                        return False
                                else:
                                    library.write_log(lib_constants.LOG_WARNING,
                                                      "WARNING: Failed to press"
                                                      " F2 keys", test_case_id,
                                                      script_id, "None", "None",
                                                      log_level, tbd)
                                    return False
                            else:
                                library.write_log(lib_constants.LOG_WARNING,
                                                  "WARNING: Failed to perform "
                                                  "G3 remote reboot",
                                                  test_case_id, script_id,
                                                  "None", "None",
                                                  log_level, tbd)
                                return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to press F2 Keys", test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to change boot order in EDK Shell",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
        else:
            if "FFFF" == current_postcode.upper() or \
               "B505" == current_postcode.upper():
                library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                  "current post code is %s and it is in Shut "
                                  "down State" % str(current_postcode),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                if library.g3_reboot_system(test_case_id, script_id, log_level,
                                            tbd):
                    if library.sendkeys("F2", test_case_id, script_id,
                                        log_level, tbd):
                        library.write_log(lib_constants.LOG_INFO, "INFO: F2 Key"
                                          " pressed successfully for to boot "
                                          "to %s" % parameter, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)

                        current_postcode = lib_ttk2_operations.\
                            read_post_code(test_case_id, script_id, log_level,
                                           tbd)

                        if current_postcode in lib_constants.BIOS_PAGE_POSTCODE:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "System booted to %s" % parameter,
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            return True
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to boot to %s"
                                              % parameter, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return False
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Failed to press F2 keys",
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to perform G3 remote reboot",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                if library.g3_reboot_system(test_case_id, script_id, log_level,
                                            tbd):
                    if library.sendkeys("F2", test_case_id, script_id,
                                        log_level,tbd):
                        library.write_log(lib_constants.LOG_INFO,
                                          "INFO: F2 Key pressed successfully "
                                          "for to boot to %s" % parameter,
                                          test_case_id,
                                          script_id, "None", "None",
                                          log_level, tbd)
                    time.sleep(30)
                    current_postcode = lib_ttk2_operations. \
                        read_post_code(test_case_id, script_id, log_level,
                                       tbd)

                    if current_postcode in lib_constants.EFI_POSTCODE:
                        library.write_log(lib_constants.LOG_INFO,
                                          "INFO: System current post code is %s"
                                          " and it is in EDK Shell"
                                          % current_postcode, test_case_id,
                                          script_id, "None", "None",
                                          log_level, tbd)

                        if change_bootorder_in_edkshell(test_case_id,
                                                        script_id,
                                                        log_level, tbd):
                            library.write_log(lib_constants.LOG_INFO,
                                              "INFO: Changed boot order in"
                                              " EDK Shell successfully to "
                                              "boot to %s" % parameter,
                                              test_case_id, script_id,
                                              "None", "None", log_level,
                                              tbd)

                            if library.sendkeys("F2", test_case_id,
                                                script_id, log_level, tbd):
                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: F2 Key pressed "
                                                  "successfully for to "
                                                  "boot to %s" % parameter,
                                                  test_case_id, script_id,
                                                  "None", "None", log_level,
                                                  tbd)

                                current_postcode = lib_ttk2_operations. \
                                    read_post_code(test_case_id, script_id,
                                                   log_level, tbd)

                                if current_postcode in \
                                        lib_constants.BIOS_PAGE_POSTCODE:
                                    library.write_log(lib_constants.
                                                      LOG_INFO, "INFO: "
                                                                "System booted to %s"
                                                      % parameter,
                                                      test_case_id,
                                                      script_id, "None",
                                                      "None", log_level,
                                                      tbd)
                                    return True
                                else:
                                    library.write_log(lib_constants.
                                                      LOG_WARNING,
                                                      "WARNING: Failed to "
                                                      "boot to %s"
                                                      % parameter,
                                                      test_case_id,
                                                      script_id, "None",
                                                      "None", log_level,
                                                      tbd)
                                    return False
                            else:
                                library.write_log(lib_constants.
                                                  LOG_WARNING,
                                                  "WARNING: Failed to press F2 "
                                                  "keys", test_case_id,
                                                  script_id, "None", "None",
                                                  log_level, tbd)
                                return False
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to change "
                                              "boot order in EDK Shell",
                                              test_case_id, script_id,
                                              "None", "None", log_level,
                                              tbd)
                            return False
                    elif current_postcode in \
                            lib_constants.BIOS_PAGE_POSTCODE:
                        library.write_log(lib_constants.LOG_INFO,
                                          "INFO: System booted to %s"
                                          % parameter,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: Failed to boot to %s"
                                          % parameter, test_case_id,
                                          script_id, "None",
                                          "None", log_level, tbd)
                        return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
