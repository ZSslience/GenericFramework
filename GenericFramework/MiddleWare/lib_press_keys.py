__author__ = r'kapilshx\hvinayx\surabh1x\tnaidux'

# General Python Imports
import os
import pyautogui
import subprocess
import time

# Local Python Imports
import lib_constants
import library
import utils
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations
import KBM_Emulation as kbm

################################################################################
# Function Name : press_special_keys
# Parameters    : token, test_case_id, script_id, type_text, last_part,
#                 log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : To press special characters
################################################################################


def press_special_keys(token, test_case_id, script_id, type_text, last_part,
                       log_level="ALL", tbd=None):

    try:
        if "PS2" in token.upper():
            type_text = library.press_keys_dictionary(type_text, test_case_id,
                                                      script_id, log_level, tbd)

            port = utils.ReadConfig("BRAINBOX", "PORT")                         # Read brainbox port from config
            if "FAIL" in port:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is missing for tag variable port",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            combikey_flag = False                                               # Set combikey_flag to false
            whitekeys_flag = False                                              # Set whitekeys_flag to false
            longstring_flag = False                                             # Set longstring_flag to false

            if "FOR" in last_part.upper():                                      # Check for FOR keyword in token
                try:
                    kb = library.KBClass(port)                                  # Instantiate Brainbox class from the library
                except Exception as e:
                    library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                                      "opening brian box com port library "
                                      "function due to %s." % e, test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    kb.close()
                    return False

                key_press_last_token = last_part.upper().split(" ")             # Split the last_part of the string with space
                if "TIMES" in key_press_last_token:                             # If last element of the string is times do the following
                    times_count, pos = library.\
                        extract_parameter_from_token(key_press_last_token,
                                                     "FOR", "TIMES",
                                                     log_level, tbd)

                    times_count = int(times_count)                              # Extract the times_counter from the last part of the string
                    if "+" in type_text:                                        # Check for combination of keys (separated by comma)in the keys
                        for x in range(times_count):                            # Loop to iterate for no. of times combination of keys to be pressed from brain box
                            kb.combiKeys(type_text)                             # Send combination of keys (separated by comma) from library
                            time.sleep(lib_constants.
                                       DEFAULT_RELAY_PRESS_DURATION)            # Sleep for two seconds it is time to send keys for sending keystrokes
                        library.write_log(lib_constants.LOG_INFO, 'INFO: "'
                                          'Sending "%s" Keystrokes %s is '
                                          'successful' % (type_text, last_part),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        for x in range(times_count):                            # Repeat for times_count times
                            kb.whiteKeys(type_text)                             # Send the whitekey from library
                            time.sleep(lib_constants.
                                       DEFAULT_RELAY_PRESS_DURATION)            # Sleep for two seconds
                        library.write_log(lib_constants.LOG_INFO, 'INFO: '
                                          '"Sending %s" Keystrokes %s is '
                                          'successful' % (type_text, last_part),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                elif ("SECONDS" in key_press_last_token) and \
                        ("HOLD" in key_press_last_token):                       # Check for seconds or secs keyword in token
                    hold_seconds, pos = library. \
                        extract_parameter_from_token(key_press_last_token,
                                                     "FOR", "SECONDS",
                                                     log_level, tbd)

                    hold_seconds = int(hold_seconds)
                    if "+" in type_text:                                        # Check for combination of keys (separated by comma)in the keys
                        for x in range(hold_seconds):
                            kb.combiKeys(type_text)                             # Send combination of keys (separated by comma) from library

                        library.write_log(lib_constants.LOG_INFO, 'INFO: '
                                          'Sending "%s" Keystrokes with %s '
                                          'successful' % (type_text, last_part),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        for x in range(hold_seconds):
                            kb.whiteKeys(type_text)

                        library.write_log(lib_constants.LOG_INFO, 'INFO: '
                                          'Sending "%s" Keystrokes with %s '
                                          'successful' % (type_text, last_part),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Input "
                                      "syntax is incorrect", test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return False
            else:
                if "+" in type_text:                                            # Checking if + in type_text
                    combikey_flag = True
                    return press_key_call(test_case_id, script_id,
                                          type_text, combikey_flag,
                                          whitekeys_flag, longstring_flag,
                                          log_level, tbd)
                else:
                    whitekeys_flag = True
                    return press_key_call(test_case_id, script_id,
                                          type_text, combikey_flag,
                                          whitekeys_flag, longstring_flag,
                                          log_level, tbd)
        else:
            input_device_name = \
                utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")     # Extract input device name from config.ini
            port = utils.ReadConfig("KBD_MOUSE", "PORT")

            if "FAIL:" in port or "FAIL:" in input_device_name:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get com port details or input device "
                                  "name from Config.ini", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                                  "input device name identified as %s and %s "
                                  "from config.ini" % (port, input_device_name),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

            k1 = kbm.USBKbMouseEmulation(input_device_name, port)
            type_text = type_text.upper()

            if 'DEL' in type_text:
                type_text = type_text.replace('DEL', 'DELETE')
            elif 'WINDOWS' in type_text:
                type_text = type_text.replace('WINDOWS', 'GUI')

            current_post_code = lib_ttk2_operations.\
                read_post_code(test_case_id, script_id, log_level, tbd)

            if current_post_code in lib_constants.BIOS_PAGE_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "BIOS Page", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
            elif current_post_code in lib_constants.EFI_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "EDK Shell", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                if type_text.upper() in lib_constants.KEY_PRESS_COMMANDS_IN_EFI:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Pressing "
                                      "command for to change Boot Order to OS",
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    k1.key_type(lib_constants.SET_BOOT_ORDER_CMD)               # Sending command to change boot order
                    k1.key_press("KEY_ENTER")                                   # Pressing enter key
                    time.sleep(lib_constants.SEND_KEY_TIME)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "OS", test_case_id, script_id, "None",
                                  "None", log_level, tbd)

            if "+" in type_text:
                type_text = type_text.split("+")
                if len(type_text[1]) > 1 and type_text[1].isalpha():
                    type_text_list = \
                        ["KEY_" + type_text[i] for i in range(len(type_text))]
                    press_keys = " ".join(type_text_list).upper()
                else:
                    press_keys = "KEY_" + type_text[0] +" "+ type_text[1].lower()
                    if press_keys == "KEY_ALT f4":
                        k1.key_press("KEY_GUI d")
                return k1.key_press(press_keys.upper())
            else:
                return k1.key_press(type_text)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : press_text_keys
# Parameters    : token, test_case_id, script_id, type_text, last_part,
#                 log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : To press text keys
################################################################################


def press_text_keys(token, test_case_id, script_id, type_text, log_level="ALL",
                    tbd=None):

    try:
        if "PS2" in token.upper():
            longstring_flag = True
            combikey_flag = False
            whitekeys_flag = False

            if "CONFIG-" in type_text.upper():                                  # Check config text in type_text
                new_type_text = utils.configtagvariable(type_text)              # Extract from configtagvariable the text to send through brainbox
                if "FAIL" in new_type_text:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Config "
                                      "entry is missing for tag variable "
                                      "new_type_text", test_case_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False

                return press_key_call(test_case_id, script_id, new_type_text,
                                      combikey_flag, whitekeys_flag,
                                      longstring_flag, log_level, tbd)
            else:
                return press_key_call(test_case_id, script_id, type_text,
                                      combikey_flag, whitekeys_flag,
                                      longstring_flag, log_level, tbd)
        else:
            input_device_name = \
                utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")     # Extract input device name from config.ini
            port = utils.ReadConfig("KBD_MOUSE", "PORT")

            if "FAIL:" in port or "FAIL:" in input_device_name:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get com port details or input device "
                                  "name from Config.ini", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                                  "input device name identified as %s and %s "
                                  "from config.ini" % (port, input_device_name),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

            kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)

            current_post_code = lib_ttk2_operations. \
                read_post_code(test_case_id, script_id, log_level, tbd)

            if current_post_code in lib_constants.BIOS_PAGE_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "BIOS Page", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
            elif current_post_code in lib_constants.EFI_POSTCODE:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "EDK Shell", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                if type_text.upper() in lib_constants.KEY_PRESS_COMMANDS_IN_EFI:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Pressing "
                                      "command for to change Boot Order to OS",
                                      test_case_id, script_id, "None",
                                      "None", log_level, tbd)
                    kb_obj.key_type(lib_constants.SET_BOOT_ORDER_CMD)           # Sending command to change boot order
                    kb_obj.key_press("KEY_ENTER")                               # Pressing enter key
                    time.sleep(lib_constants.SEND_KEY_TIME)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: System is in "
                                  "OS", test_case_id, script_id, "None",
                                  "None", log_level, tbd)

            return kb_obj.key_type(type_text)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : press_key_call
# Parameters    : test case id,script id,combikey_flag,whitekeys_flag,
#                 longstring_flag,type_text,last_part,log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : Set the virtual battery charging_percentage to 50%
################################################################################
def press_key_call(test_case_id,script_id,type_text,combikey_flag,whitekeys_flag,
                                    longstring_flag,log_level="ALL",tbd = None):

    try:
        port = utils.ReadConfig("BRAINBOX",
                                "PORT")  # Read brainbox port from config
        if "FAIL" in port:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Config entry is"
                              " missing for tag variable port",
                              test_case_id, script_id,
                              "None", "None", log_level,
                              tbd)  # write error msg for config entry missing
            return False
        else:
            pass
        try:
            kb = library.KBClass(
                port)  # instantiate Brainbox class from the library
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Exception in "
                              "opening brian box com port library function due to "
                              "%s." % e, test_case_id, script_id, "None",
                              "None", log_level,
                              tbd)  # write error msg to log
            kb.close()  # closing the brain box comport
            return False
        time.sleep(
            lib_constants.DEFAULT_RELAY_PRESS_DURATION)  # sleep for two seconds it is time to send keys for sending keystrokes
        if True == combikey_flag:
            kb.combiKeys(type_text)  # send combination of keys (separated by comma) from library
        elif True == whitekeys_flag:
            kb.whiteKeys(type_text)
        elif True == longstring_flag:
            kb.longString(
                type_text)  # send the text through brainbox to SUT using longString function of KBClass
        else:
            pass
        time.sleep(
            lib_constants.DEFAULT_RELAY_PRESS_DURATION)  # sleep for two seconds it is time to send keys for sending keystrokes
        library.write_log(lib_constants.LOG_INFO, 'INFO "%s" Keystrokes'
                                                  ' successful' % type_text,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
        kb.close()  # closing the brain box comport
        return True  # if sending keystroke is successful
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
                                                   "press_key_call library function due to "
                                                   "%s." % e, test_case_id,
                          script_id, "None", "None", log_level,
                          tbd)  # write error msg to log if Exception occurs in press_key_call library function
        kb.close()  # closing the brain box comport
        return False
################################################################################
# Function Name : press_special_keys_presi
# Parameters    : test_case_id,script id, type_text,last_part,log_level, tbd
# Functionality : checks keyboard triggering through Host
# Return Value  : returns True on success and Fail otherwise
################################################################################
def press_special_keys_presi(test_case_id,script_id,type_text,last_part,
                                                    log_level="ALL",tbd=None):
    try:
        spl_text = type_text.lower()
        time.sleep(lib_constants.THREE)                                         # Sleep time for 3 seconds to make sure command prompt window is opened in sut
        process = subprocess.Popen((lib_constants.ACTIVATE_SIMICS_WINDOW),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)                         # Executing app_activation_has utility
        stdout, stderr = process.communicate()                                  # Getting command output and error information
        if len(stderr) > 0:                                                     # If any error found in executing exe
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "activate simics console window", test_case_id, script_id,
                log_level, tbd)
                return False                                                    # Function exists by Returning False if error occurs in activating simics console
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "activated simics console window", test_case_id, script_id,
                log_level, tbd)
            time.sleep(lib_constants.THREE)                                     # Wait for 3 seconds before the simics console is activated
            process = subprocess.Popen((lib_constants.MOUSE_DOUBLE_CLICK),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)                     # Executing double_click_mouse utility
            stdout, stderr = process.communicate()                              # Getting command output and error information
            if len(stderr) > 0:                                                 # If any error found in sending mouse double click
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "send double click to simics console window", test_case_id,
                    script_id, log_level, tbd)
                    return False                                                # Function exists by Returning False if error occurs in sending mouse_click signals
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "sent double click to simics console window", test_case_id,
                script_id, log_level, tbd)
                time.sleep(lib_constants.THREE)                                 # Wait for 3 seconds  before the commands are in sut command prompt
                pyautogui.press(spl_text)                                       # Send enter to simics console
                return True                                                     # Returns true if Keypress is sent

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "sending key signal to simics setup:%s"%e, test_case_id, script_id,
        "None", "None", log_level, tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : press_text_keys_presi
# Parameters    : test_case_id,script_id, type_text,last_part,log_level, tbd
# Return Value  : True on success, False on failure
################################################################################
def press_text_keys_presi(test_case_id,script_id,type_text,log_level="ALL",
    tbd=None):

    try:
        plain_text = type_text
        time.sleep(lib_constants.THREE)                                         # Sleep time for 3 seconds to make sure command prompt window is opened in sut
        process = subprocess.Popen((lib_constants.ACTIVATE_SIMICS_WINDOW),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)                         # Executing app_activation_has utility
        stdout, stderr = process.communicate()                                  # Getting command output and error information
        if len(stderr) > 0:                                                     # If any error found in executing exe
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "activate simics console window", test_case_id, script_id,
                log_level, tbd)
                return False                                                    # Function exists by Returning False if error occurs in activating simics console
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "activated simics console window", test_case_id, script_id,
                log_level, tbd)
            time.sleep(lib_constants.THREE)                                     # Wait for 3 seconds before the simics console is activated
            process = subprocess.Popen((lib_constants.MOUSE_DOUBLE_CLICK),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)                     # Executing double_click_mouse utility
            stdout, stderr = process.communicate()                              # Getting command output and error information
            if len(stderr) > 0:                                                 # If any error found in sending mouse double click
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "send double click to simics console window", test_case_id,
                    script_id, log_level, tbd)
                    return False                                                # Function exists by Returning False if error occurs in sending mouse_click signals
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                "sent double click to simics console window", test_case_id,
                script_id, log_level, tbd)
                time.sleep(lib_constants.THREE)                                 # Wait for 3 seconds  before the commands are in sut command prompt
                pyautogui.typewrite(plain_text)                                 # Send enter to simics console
                return True                                                     # Returns true if Keypress is sent

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "sending key signal to simics setup:%s"%e, test_case_id, script_id,
        "None", "None", log_level, tbd)
        return False                                                            # Function exists by Returning False when Exception arises
