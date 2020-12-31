__author__ = 'NARESHGX'

############################General Python Imports##############################
import utils
import os
import subprocess
import time
############################Local Python Imports################################
import lib_constants
import library
import lib_boot_to_environment
import lib_capture_screenshot
from PIL import Image
import KBM_Emulation as kbm
################################################################################
#   Function name   : boot_to_dest_from_bootmanager()
#   description     : boot to destination from boot manager
#   parameters      : 'test_case_id' is test case id
#                          'script_id' is script id
#                          'token ' is original string
#   Returns         : True/False
######################### Main script ##########################################
def boot_to_dest_from_bootmanager(token, test_case_id, script_id,
                               loglevel="ALL", tbd="None"):                     #function call boot to destination from F7 screen
    re_split = token.split(' ')
    re_fetch = library.extract_parameter_from_token(re_split, 'to', 'from')[0]
    kvm_name = utils.ReadConfig("kvm_name", "name")                             # KVM is read from the config file
    kvm_title = utils.ReadConfig("kvm_name", "kvm_title")                       # kvm_title exe name fetched from config file
    activate_path = utils.ReadConfig("sikuli", "Activexe")                      # activate_path exe name fetched from config file
    if 'FAIL' in kvm_name or 'FAIL' in kvm_title or '' == activate_path:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: KVM details in "
        "config.ini not found", test_case_id, script_id, "None", "None",
                          loglevel, tbd)
        return False,re_fetch
    tesseract_path = utils.ReadConfig('Benchmark', 'Tesseract_path')
    tesseract_exe = utils.ReadConfig('Benchmark', 'Tesseract_exe')
    title = kvm_name + " - "+ kvm_title                                         # KVM command for activating the kvm window
    window_path = activate_path + " " + title
    kvm_activate = subprocess.Popen(window_path, stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE)        # KVM window is activated from the host
    time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
    kvm_activate = kvm_activate.communicate()[0]
    if "Failed" in kvm_activate:                                                #if failed to activate the KVM may be due to host is minimised
        library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
        "activate the KVM window", test_case_id, script_id, "None", "None",
                          loglevel, tbd)
        return False,re_fetch
    else:                                                                       #if KVM window is activated successful
        library.write_log(lib_constants.LOG_INFO, "INFO: KVM window is"
            " activated", test_case_id, script_id, "None", "None",
                          loglevel, tbd)
    if True == library.g3_reboot_system(loglevel, tbd):                         # Does a g3
        if True == library.sendkeys("F7", loglevel, tbd):                       #function to send keys F7 while system is restarting
            library.write_log(lib_constants.LOG_INFO, "INFO: Key F7 "
            "sent", test_case_id, script_id, "None", "None", loglevel,
            tbd)
            cur_os = lib_boot_to_environment.checkcuros(loglevel, tbd)                   #check whether system is in os or bios
            if ("EDK SHELL" == cur_os ):                                        # checks for the current state after pinging
                library.write_log(lib_constants.LOG_INFO,
                "INFO: System boot to F7 menu", test_case_id, script_id,
                "None", "None", loglevel, tbd)
            else:                                                               #if system is still in OS
                library.write_log(lib_constants.LOG_INFO,
                "INFO: Failed to boot to F7 or system is still in OS",
                 test_case_id, script_id, "None", "None", loglevel, tbd)
                return False,re_fetch
        else:                                                                   #if fails to send the command keys such as "F7"
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "send F7 key", test_case_id, script_id, "None", "None",
            loglevel, tbd)
            return False,re_fetch
    else:                                                                       #if fails to reboot the system
        library.write_log(lib_constants.LOG_INFO, "INFO: Reboot failed",
            test_case_id, script_id, "None", "None", loglevel, tbd)
        return False,re_fetch
    try:
        if os.path.exists(script_id.replace('.py', '.png')):
            os.remove(script_id.replace('.py', '.png'))
            library.write_log(lib_constants.LOG_INFO,"INFO: Old logs deleted"
                ,test_case_id, script_id, "TESSERACT", "None", loglevel, tbd)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in file "
        "deletion", test_case_id, script_id, "TESSERACT", "None", loglevel, tbd)
        return False,re_fetch

    status,result_file = lib_capture_screenshot.capture_screen(test_case_id,
                                                    script_id, loglevel, tbd)
    if status:
        col = Image.open(result_file)
        gray = col.convert('L')
        bw = gray.point(lambda x: 0 if x<128 else 255, '1')
        bw.save(result_file)
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Image captured and "
        "converted to extract text",test_case_id, script_id, "PIL", "None",
                          loglevel, tbd)
    else:
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Failed to capture image"
            ,test_case_id, script_id, "PIL", "None",loglevel, tbd)
        return False,re_fetch
    if os.path.exists(tesseract_path):                                          # check for tesseract application
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Tesseract Path exists"
            ,test_case_id, script_id, "TESSERACT", "None", loglevel, tbd)
    else:                                                                       # if not fail
        library.write_log(lib_constants.LOG_INFO,"INFO: Tesseract Path "
        "doesn't exists",test_case_id, script_id, "TESSERACT", "None",
                          loglevel, tbd)
        return False,re_fetch
    os.chdir(tesseract_path)
    cmd_tes = tesseract_exe+" "+result_file+" "+test_case_id
    cmd_exe = subprocess.Popen(cmd_tes, shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE)     # execute bat file in subprocess
    exec_out = cmd_exe.communicate()[0]
    if "error" in exec_out or 'Cannot open' in exec_out:                        # if error in teseract log then fail
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Image file not "
        "found %s"%exec_out, test_case_id, script_id, "Tesseract", "None",
                          loglevel, tbd)
        return False,re_fetch
    else:                                                                       # else continue
        library.write_log(lib_constants.LOG_DEBUG,"DEBUG: Log %s"
        %exec_out, test_case_id, script_id, "Tesseract", "None", loglevel, tbd)
    try:
        fp = open(tesseract_path+'\\'+test_case_id+'.txt','r')
        boot_data_list=[]
        for line in fp:
            if "" == line or " " == line or "\n" == line:
                pass
            elif 'select boot' in line:
                pass
            elif 'move selection' in line:
                break
            else:
                boot_data_list.append(line.strip())
        fp.close()
        library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device List %r"
        %boot_data_list, test_case_id, script_id, "None", "None", loglevel, tbd)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in opening "
            "file %s"%e, test_case_id, script_id, "None", "None", loglevel, tbd)
        status = fail_boot_to_os(test_case_id,script_id,loglevel,tbd)
        if status:
            library.write_log(lib_constants.LOG_INFO,"INFO: Send key 'ESC' boot"
            " to OS for cleanup", test_case_id, script_id, "Keyboard-Mouse Simulator",
                              "None", loglevel, tbd)
        return False,re_fetch
    index_to_boot = ""
    for index,list_item in enumerate(boot_data_list):
        if 'Storage' in list_item and 'usb-pendrive' in re_fetch.lower():
            index_to_boot = index
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
        "%s"%str(index), test_case_id, script_id, "None", "None", loglevel, tbd)
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
        "%s not supported"%str(index), test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            status = fail_boot_to_os(test_case_id,script_id,loglevel,tbd)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Send key 'ESC' "
                "boot to OS for cleanup", test_case_id, script_id, "Keyboard-Mouse Simulator",
                              "None", loglevel, tbd)
            return False,re_fetch
        elif 'EFI' in list_item and 'UEFI' not in list_item and 'emmc' in \
                re_fetch.lower():
            index_to_boot = index
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
        "%s"%str(index), test_case_id, script_id, "None", "None", loglevel, tbd)
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
        "%s not supported"%str(index), test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            status = fail_boot_to_os(test_case_id,script_id,loglevel,tbd)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Send key 'ESC' "
                "boot to OS for cleanup", test_case_id, script_id, "Keyboard-Mouse Simulator",
                              "None", loglevel, tbd)
            return False,re_fetch
        elif 'SSD' in list_item and 'sata-ssd' in re_fetch.lower():
            index_to_boot = index
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
        "%s"%str(index), test_case_id, script_id, "None", "None", loglevel, tbd)
        else:
            pass
    if "" == index_to_boot:
        library.write_log(lib_constants.LOG_INFO,"INFO: Boot device not "
            "supported",test_case_id, script_id, "None", "None", loglevel,tbd)
        status = fail_boot_to_os(test_case_id,script_id,loglevel,tbd)
        if status:
            library.write_log(lib_constants.LOG_INFO,"INFO: Send key 'ESC' "
                "boot to OS for cleanup", test_case_id, script_id, "Keyboard-Mouse Simulator",
                              "None", loglevel, tbd)
        return False,re_fetch
    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                         # Extract com port details from config.ini
        if "FAIL:" in port or "FAIL:" in input_device_name:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                                                 "com port details or "
                                                 "input device name from "
                                                 "Config.ini ", "None", "None",
                      "None", "None", loglevel, tbd)                         # Failed to get info from config file
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: COM Port and input "
                                              "device name is identified as "
                                              "is identified as %s %s from "
                                              "config.ini"
                      % (port, input_device_name), "None", "None", "None",
                      "None", loglevel, tbd)
        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        if index_to_boot > 1:
            for i in range(index_to_boot):
                k1.key_press("KEY_DOWN")                                      # Sending down keys to go to Bios page
            k1.key_press("KEY_ENTER")
            library.write_log(lib_constants.LOG_INFO,"INFO: Boot Device index "
            "selected", test_case_id, script_id, "None", "None", loglevel, tbd)
            return True,re_fetch
        else:
            k1.key_press("KEY_ENTER")
            return True,re_fetch
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "selecting boot destination %s"%str(index), test_case_id, script_id, "\
                                          ""None", "None", loglevel, tbd)
        status = fail_boot_to_os(test_case_id,script_id,loglevel,tbd)
        if status:
            library.write_log(lib_constants.LOG_INFO,"INFO: Send key 'ESC' "
                "boot to OS for cleanup", test_case_id, script_id, "Keyboard-Mouse Simulator",
                              "None", loglevel, tbd)
        return False,re_fetch
################################################################################
#   Function name   : fail_boot_to_os
#   description     : if error occurs or test case fail then as clean up this
#                     function is implemented to boot to OS
#   parameters      : 'test_case_id' is test case id
#                          'script_id' is script id,loglevel and tbd
#   Returns         : True/False
######################### Main script ##########################################
def fail_boot_to_os(test_case_id, script_id, loglevel, tbd):
    try:
        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")            # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                               # Extract com port details from config.ini
        if "FAIL:" in port or "FAIL:" in input_device_name:
            write_log(lib_constants.LOG_WARNING, "WARNING: Failed to get "
                                                 "com port details or "
                                                 "input device name from "
                                                 "Config.ini ", "None", "None",
                      "None", "None", loglevel, tbd)                               # Failed to get info from config file
            return False
        else:
            write_log(lib_constants.LOG_INFO, "INFO: COM Port and input "
                                              "device name is identified as "
                                              "is identified as %s %s from "
                                              "config.ini"
                      % (port, input_device_name), "None", "None", "None",
                      "None", loglevel, tbd)
        k1 = kbm.USBKbMouseEmulation(input_device_name, port)
        k1.key_press("KEY_ESC")
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "sending commands from simulator %s"%e, test_case_id, script_id, "\
                                          ""None", "None", loglevel, tbd)
        return False