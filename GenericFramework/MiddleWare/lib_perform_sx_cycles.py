__author__ = r'kvex\tnaidux\sshedgex'

# Global Python Imports
import os
import subprocess
import time

# Local Python Imports
import lib_constants
import library
import utils
import lib_press_button_on_board
import KBM_Emulation as kbm

################################################################################
# Function Name : perform_sx_rtc
# Parameters    : tc_id, script_id, sx_state, cycle_time, cycle_no, tdb1, tdb2
# Return Value  : returns True on successful sx cycles and False otherwise
# Purpose       : to perform required sx cycle
################################################################################


def perform_sx_rtc(tc_id, script_id, sx_state, cycle_time, cycle_no,
                   loglevel="ALL", tbd=None):

    valid = True

    if "-" in str(cycle_time):                                                  #read time from config if required
        tag, key, variable = cycle_time.partition("-")                          #splitting the cycle time and initialising it to varisbles
        cycle_time = utils.ReadConfig(tag, variable)                            #Cycle time is read from the config variable section name

    try:
        cycles = int(cycle_no)                                                  #make sure than cycle no and cycle time as int values
        duration = int(cycle_time)

        if "S3" == sx_state or "S4" == sx_state or \
           "CONNECTED-MOS" == sx_state or "DISCONNECTED-MOS" == sx_state:       #Check for s3/s4/s5 are valid sx state

            if duration >= lib_constants.POWER_TEST_MIN_TIME:
                valid = True
            else:
                valid = False
                library.write_log(lib_constants.LOG_WARNING, "WARNING: The "
                                  "duration for sx cycle should be at least "
                                  "30 seconds", tc_id, script_id, "None",
                                  "None", loglevel, tbd)                        #write fail msg to the log
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Given sx "
                              "state is not valid", tc_id, script_id, "None",
                              "None", loglevel, tbd)                            #write to result file
            valid = False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", loglevel, tbd)      #write fail exception error to log
        valid = False

    if valid:
        system_cycling_tool_path = \
            utils.ReadConfig("System_Cycling_Tool", "tool_path")

        system_cycling_exe = \
            utils.ReadConfig("System_Cycling_Tool", "system_cycling_exe")

        target_sut_ip = utils.ReadConfig("SUT_IP", "target_sut_ip")

        if "FAIL:" in system_cycling_tool_path or \
           "FAIL:" in system_cycling_exe or "FAIL:" in target_sut_ip:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the required config entries", tc_id,
                              script_id, "None", "None", loglevel, tbd)
            return False

        if "CONNECTED-MOS" == sx_state or "DISCONNECTED-MOS" == sx_state:       # based on the sx state required set sx value. for Connected-MOS, Disconnected-MOS s3 should be run
            sx = "S3"
        else:
            sx = sx_state

        command = '"' + str(system_cycling_exe).strip() + '"' + ' -al -ip ' + \
            str(target_sut_ip) + ' -' + str(sx) + ' i:' + str(cycles) + \
            ' tw:' + str(duration) + ' ts:' + str(lib_constants.SX_TIME)        # command to execute SX state from ICT tool

        library.write_log(lib_constants.LOG_INFO, "INFO: Command to Perform "
                          "Cycling: %s " % command, tc_id, script_id, "None",
                          "None", loglevel, tbd)

        if os.path.exists(system_cycling_tool_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: System Cycling "
                              "tool path exists in the system", tc_id,
                              script_id, "None", "None", loglevel, tbd)

            os.chdir(system_cycling_tool_path)

            library.write_log(lib_constants.LOG_INFO, "INFO: Changed current "
                              "directory path to System Cycling Tool path ",
                              tc_id, script_id, "None", "None", loglevel, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: System "
                              "Cycling Tool does not exist", tc_id, script_id,
                              "None", "None", loglevel, tbd)
            return False

        total_cycles = "Total No Of Cycles:" + str(cycles)
        passed_cycles = "Passed Cycles:" + str(cycles)
        failed_cycles = "Failed Cycles:0"
        ignored_cycles = "Ignored Cycles:0"

        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.communicate()[0]

        output_text_file = lib_constants.SCRIPTDIR + "\\" + \
            script_id.replace(".py", ".log")
        if os.path.exists(output_text_file):
            os.remove(output_text_file)

        with open(output_text_file, "w") as output_file:
            output_file.write(str(output))
            library.write_log(lib_constants.LOG_INFO, "INFO: Created %s file "
                              "and wrote the output to the file successfully"
                              % output_text_file, tc_id, script_id, "None",
                              "None", loglevel, tbd)

        if total_cycles in str(output) and passed_cycles in str(output) and \
                failed_cycles in str(output) and ignored_cycles in str(output):
            library.write_log(lib_constants.LOG_INFO, "Output Of System "
                              "Cycling Tool:\n%s\n%s\n%s\n%s"
                              % (str(total_cycles), str(passed_cycles),
                                 str(failed_cycles), str(ignored_cycles)),
                              tc_id, script_id, "None", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "complete %s cycles" % str(cycles), tc_id,
                              script_id, "None", "None", loglevel, tbd)

            library.write_log(lib_constants.LOG_INFO, "Output Of System "
                              "Cycling Tool:\n%s" % str(output), tc_id, script_id,
                              "None", "None", loglevel, tbd)
            return False
    else:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to perform "
                          "sx cycle", tc_id, script_id, "None", "None",
                          loglevel, tbd)                                        #Write fail exception error msg to log
        return False

################################################################################
# Function Name : put_system_sx_idle_wait_time
# Parameters    : test_case_id, script_id, sx_state, source, log_level, tbd
# Return Value  : returns True on successful, False otherwise
# Purpose       : put system to sx after idle wait time
################################################################################


def put_system_sx_idle_wait_time(test_case_id, script_id, sx_state, source,
                                 idle_wait_time, log_level="ALL", tbd=None):

    try:
        put_system_sleep = lib_constants.AC_POWERCFG_CMD_PUT_SYSTEM_SLEEP       #extracting powercfg command for to put the system to sleep on AC
        minute_time = int(idle_wait_time) / 60                                  #converting idle wait time seconds in to minutes
        system_sleep_cmd = put_system_sleep + " " + str(minute_time)            #appending put_system_sleep command and idle wait time

        utils.filechangedir(lib_constants.SYSTEM_PATH)                          #changing directory to system_path directory
        system_sleep_cmd_output = subprocess.Popen(system_sleep_cmd,
                                                   shell=False)                 #running command to set the value for put the system to sleep option
        system_sleep_cmd_output.communicate()

        if not system_sleep_cmd_output.returncode:                              #check if return code is True from the subprocess output
            library.write_log(lib_constants.LOG_INFO, "INFO: Put the computer "
                              "to sleep has been set to %d minutes "
                              "successfully" % minute_time, test_case_id,
                              script_id, "None", "None", log_level, tbd)        #writing log_info message to the log file
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "set time for ut the computer to sleep",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #writing log_info message to the log file
            return False

        time.sleep(int(idle_wait_time))                                         #system waiting for given input time
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #writing exception message to the log file
        return False

################################################################################
# Function Name : perform_sx_cycle_using_power_button
# Parameters    : test_case_id, script_id, sx_state, post_code, led_code,
#                 log_level, tbd
# Return Value  : returns True on successful, False otherwise
# Purpose       : Perform Sx cycle using power button
################################################################################


def perform_sx_cycle_using_power_button(test_case_id, script_id, sx_state,
                                        post_code, led_code, log_level, tbd):

    try:
        lib_press_button_on_board.press_button(1, "POWER", lib_constants.ON,
                                               test_case_id, script_id,
                                               log_level, tbd)                  # press power button to put system to Sx
        counter = lib_constants.ZERO

        while True:
            counter = counter + 1
            current_post_code = library.read_post_code(log_level, tbd)          # Read post code

            if current_post_code in post_code:                                  # check for Sx post code to verify system is in Sx
                if sx_state in lib_constants.DEEPSX:                            # If sx state id deeps3/deeps4/deeps5
                    if library.get_led_status(led_code,
                                              lib_constants.DEBUG_COUNTER,
                                              test_case_id, script_id,
                                              log_level, tbd):                  # Check for LED status
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "System is in %s state. Post code "
                                          "%s is captured successfully"
                                          % (sx_state, current_post_code),
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return True
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "Failed to get the led status",
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)               # When LED capture fails
                        return False
                else:                                                           # If not DEEPSx then it is CS cycle
                    library.write_log(lib_constants.LOG_INFO, "INFO: System "
                                      "is in %s state. Post code %s is "
                                      "captured successfully"
                                      % (sx_state, current_post_code),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return True
            else:
                if counter > lib_constants.DEBUG_COUNTER:                       # If system doesn't show post code for cs after 5000 cycles (> 5 mins), fail step
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to put SUT to %s. Post code %s "
                                      "is not captured"
                                      % (sx_state, lib_constants.CS_POSTCODE),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
                else:
                    pass                                                        # Do nothing. continue in the loop
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #writing exception message to the log file
        return False

################################################################################
# Function Name : perform_sx_cycle
# Parameters    : test_case_id, script_id, sx_state, post_code, log_level, tbd
# Return Value  : returns True on successful, False otherwise
# Purpose       : Perform Sx cycles[DeepS3, DeepS4, DeepS5, CS,
#                 CONNECTED-MOS, DISCONNECTED-MOS, S0I3] using power button
################################################################################


def perform_sx_cycle(test_case_id, script_id, sx_state, log_level="ALL",
                     tbd=None):

    try:
        if "DEEPS3" == sx_state:
            post_code = str(lib_constants.S3_POSTCODE)                          # Postcode when it enters into DeepS3
            led_code = str(lib_constants.DEEPS3_LED)                            # LED status when it enters DeepS3
            wake_postcode = str(lib_constants.S3_WAKE_POSTCODE)                 # Postcode when it wakes from DeepS3
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # LED status when it wakes from DeepS3
        elif "DEEPS4" == sx_state:
            post_code = str(lib_constants.S4_POSTCODE)                          # Postcode when it enters into DeepS4
            led_code = str(lib_constants.DEEPS4_LED)                            # LED status when it enters DeepS4
            wake_postcode = str(lib_constants.S4_WAKE_POSTCODE)                 # Postcode when it wakes from DeepS4
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # LED status when it wakes from DeepS4
        elif "DEEPS5" == sx_state:
            post_code = str(lib_constants.S5_POSTCODE)                          # Postcode when it enters into DeepS5
            led_code = str(lib_constants.DEEPS5_LED)                            # LED status when it enters DeepS5
            wake_postcode = str(lib_constants.S5_WAKE_POSTCODE)                 # Postcode when it wakes from DeepS5
            wake_led_code = str(lib_constants.SX_LED_OFF)                       # LED status when it wakes from DeepS5
        elif "CS" == sx_state or "CONNECTED-MOS" == sx_state or \
             "DISCONNECTED-MOS" == sx_state or "CMOS" == sx_state or \
             "DMOS" == sx_state:
            post_code = str(lib_constants.CS_POSTCODE)                          # Postcode when it enters into CMOS state
            wake_postcode = str(lib_constants.CS_WAKE_POSTCODE)                 # Postcode when it wakes from CMOS state
            led_code = None
            wake_led_code = None
        else:                                                                   # If Sx state is not mentioned
            post_code = None
            led_code = None
            wake_led_code = None
            wake_postcode = None

        value = perform_sx_cycle_using_power_button(test_case_id, script_id,
                                                    sx_state, post_code,
                                                    led_code, log_level, tbd)   # To put system to Sx

        if value != True:                                                       # when fails to put system to sx state
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "put system to %s" % sx_state, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        time.sleep(lib_constants.SLEEP_TIME)                                    # delay for short interval before waking system

        value = perform_sx_cycle_using_power_button(test_case_id, script_id,
                                                    sx_state, wake_postcode,
                                                    wake_led_code, log_level,
                                                    tbd)                        # To wake system from Sx

        if value != True:                                                       # when fails to put system to sx state
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "wake system from %s" % sx_state, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        time.sleep(lib_constants.SLEEP_TIME)                                    # delay for short interval before waking system
        return True                                                             # Returns True after successful completion of sx cycle
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)                                                  #writing exception message to the log file
        return False


def perform_action_to_avoid_windows_issue(test_case_id, script_id,
                                          log_level="ALL", tbd=None):           # Function for perform SendKeys action to avoid Windows RTC Issue

    try:
        input_device_name = utils.ReadConfig("KBD_MOUSE",
                                             "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                              "to get com port details or input device "
                              "name from Config.ini", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name is identified as is "
                              "identified as %s %s from config.ini"
                              % (port, input_device_name), test_case_id,
                              script_id, "None", "None", log_level, tbd)

        time.sleep(10)
        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("F5")                                                  # Press F5 button in OS
        kb_obj.key_press("KEY_ENTER")                                           # Press enter
        library.write_log(lib_constants.LOG_INFO, "INFO: Hard Ware interaction"
                          " performed successfully for to avoid the Windows "
                          "RTC Issue", test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False