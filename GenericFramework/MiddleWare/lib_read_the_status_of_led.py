__author__ = r'patnaikx/tnaidux'

# Global Python Imports
import os
import sys
import time

# Local Python Imports
import lib_constants
import library
import utils
sys.path.append(lib_constants.TOOLPATH)

# Global Variables
PVALUE_S0 = "S0"
PVALUE_SLEEP_STATE = "S3"
PVALUE_HIBERNATE_STATE = "S4"
PVALUE_SHUTDOWN_STATE = "S5"
DEEPSX = ["DEEPS3", "DEEPS4", "DEEPS5"]
PVALUE_BLINKING = "BLINKING"
STR_LOW = "LOW"
STR_HIGH = "HIGH"
STR_ON = "ON"
STR_OFF = "OFF"
SX_LED_LIST = [PVALUE_S0, PVALUE_SLEEP_STATE, PVALUE_HIBERNATE_STATE,
               PVALUE_SHUTDOWN_STATE, DEEPSX[0], DEEPSX[1], DEEPSX[2]]          # created a list which has all the sx states used the above mentioned varaiables
sleep_time = 30
wait_time = lib_constants.FIVE_MIN                                              # we will wait for maximum 5 minutes for led status to reach expected status
STR_DEEP = "DEEP"
STR_D = "D"

################################################################################
# Function Name : lib_read_the_status_of_led
# Parameters    : token is test case step ,test_case_id is test case number,
#                 script_id is script number, log_level, tbd
# Functionality : To get LED status ON/OFF using LSD device
# Return Value  : 'True' on successful action and 'False' on failure
################################################################################


def read_led_status(token, test_case_id, script_id, log_level="ALL",
                    tbd="None"):                                                # Function  to read the LED status

    try:
        token_lwr = token.lower()                                               # Converting step to lower case
        token_str = token_lwr.split(" ")                                        # Splitting step based on space and converting into list
        sx_state, pos = \
            library.extract_parameter_from_token(token_str, "read", "led")      # Calling function to get parameter 1 (LED name)
        led_status, pos = \
            library.extract_parameter_from_token(token_str, "=", "")            # Calling function to get parameter 2 (LED status)

        library.write_log(lib_constants.LOG_INFO, "INFO: Performing operations"
                          " to read the status of the LED by using LSD device",
                          test_case_id, script_id, "LSD", "None", log_level,
                          tbd)

        if "SLP-S0" == sx_state.upper():
            if "GLK" == tbd.upper():
                library.write_log(lib_constants.LOG_INFO, "INFO: The platform "
                                  "is used to read the status of %s LED is %s"
                                  % (sx_state, tbd), test_case_id,
                                  script_id, "LSD", "None", log_level, tbd)
                command = "CSS"                                                 # Command to read the status of the LED SLP-S0
                return read_led_status_using_lsd_device(sx_state, led_status,
                                                        command, test_case_id,
                                                        script_id, log_level,
                                                        tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: The platform "
                                  "is used to read the status of %s LED is %s"
                                  % (sx_state, tbd), test_case_id,
                                  script_id, "LSD", "None", log_level, tbd)
                command = "CSB"                                                 # Command to read the status of the LED SLP-S0
                return read_led_status_using_lsd_device(sx_state, led_status,
                                                        command, test_case_id,
                                                        script_id, log_level,
                                                        tbd)
        elif sx_state.upper() in SX_LED_LIST:
            return read_sx_led_status_using_lsd_device(sx_state, led_status,
                                                       test_case_id,
                                                       script_id, log_level,
                                                       tbd)
        else:
            sx_command = sx_state
            if sx_command:
                return read_sx_led_status_using_lsd_device(sx_state, led_status,
                                                           test_case_id,
                                                           script_id, log_level,
                                                           tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to fetch the LSD command for the given LED "
                                  "%s" % sx_state, test_case_id, script_id,
                                  "LSD", "None", log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s " % e,
                          test_case_id, script_id, "LSD", "None", log_level,
                          tbd)
        return False


def read_led_status_using_lsd_device(sx_state, led_status, command,
                                     test_case_id, script_id, log_level, tbd):

    """
    Function Name   : read_led_status_using_lsd_device
    Parameters      : sx_state, led_status, command, test_case_id, script_id,
                      tools, target_os, log_level, opt
    Functionality   : To read LED status ON/OFF/BLINKING with the help of LSD
                      tool
    Function Invoked: library.write_log(), utils.execute_with_command()
    Return Value    : (Bool)'True' on successful action and 'False' on
                      failure
    """

    try:
        library.write_log(lib_constants.LOG_INFO, "INFO: Performing operations"
                          " to read the given LED %s state %s"
                          % (sx_state, led_status), test_case_id, script_id,
                          "LSD", "None", log_level, tbd)

        if led_status == STR_OFF:                                               # Checking the status of the LED
            status = STR_HIGH
        elif led_status == STR_ON or led_status == PVALUE_BLINKING:
            status = STR_LOW
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid LED"
                              " status %s is given, Expected LED status is "
                              "ON/OFF/BLINKING" % led_status, test_case_id,
                              script_id, "LSD", "None", log_level, tbd)
            return False

        lsd_exe_path = utils.ReadConfig("LSD", "LSD_EXE_PATH")
        if "FAIL:" in lsd_exe_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the config entry for lsd_exe_path under LSD "
                              "tag from config file", test_case_id, script_id,
                              "LSD", "None", log_level, tbd)
            return False

        lsd_command = lsd_exe_path + " " + command

        library.write_log(lib_constants.LOG_INFO, "INFO: Executing the command"
                          " %s to read the given LED %s state %s "
                          % (lsd_command, sx_state, led_status), test_case_id,
                          script_id, "LSD", "None", log_level, tbd)

        result = execute_lsd_command(sx_state, lsd_command, led_status, status,
                                     test_case_id, script_id, log_level, tbd)
        return result
    except Exception as ex:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in read_led_"
                          "status_using_lsd_device() error due to : %s" % ex,
                          test_case_id, script_id, "LSD", "None", log_level,
                          tbd)
        return False


def read_sx_led_status_using_lsd_device(sx_state, led_status, test_case_id,
                                        script_id, log_level, tbd):

    """
    Function Name   : read_sx_led_status_using_lsd_device
    Parameters      : sx_state, led_status, test_case_id, script_id,
                      log_level, tbd
    Functionality   : To read LED status ON/OFF with the help of LSD
                      tool
    Function Invoked: library.write_log()
    Return Value    : 'True' on successful action and 'False' otherwise
    """

    try:
        time.sleep(5)
        library.write_log(lib_constants.LOG_INFO, "INFO: Performing operations"
                          " to read the given %s LED status" % sx_state.upper(),
                          test_case_id, script_id, "LSD", "None", log_level,
                          tbd)

        if os.path.exists(lib_constants.SUT_INTERFACE_FOLDER_PATH):
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT Interface "
                              "folder exists in Tools path", test_case_id,
                              script_id, "LSD", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: SUT "
                              "Interface folder does not exists in Tools path",
                              test_case_id, script_id, "LSD", "None",
                              log_level, tbd)
            return False

        for root, dirs, files in os.walk(lib_constants.SCRIPTDIR):
            for temp in files:
                if temp.startswith("sutinterface"):
                    os.remove(temp)

        library.write_log(lib_constants.LOG_INFO, "INFO: Extracting the "
                          "current system power state", test_case_id,
                          script_id, "LSD", "None", log_level, tbd)

        import sutinterface as sut
        sut.get_system_power_state()
        time.sleep(10)

        if STR_DEEP in sx_state.upper():
            sx_state = sx_state.upper().replace(STR_DEEP, STR_D)

        for root, dirs, files in os.walk(lib_constants.SCRIPTDIR):
            for temp in files:
                if temp.startswith("sutinterface") and \
                        "main" not in temp.lower():
                    sut_interface_log_path = os.path.join(root, temp)

        flag = False
        with open(sut_interface_log_path, "r") as f:
            for line in f:

                if "system power state is" in line.lower():
                    current_state = line.strip().split(" ")[-1]
                    flag = True

        if flag is True:
            if sx_state.upper() == current_state and \
               led_status.upper() != STR_ON and \
               led_status.upper() != STR_OFF:                                   # Checking the return code and stdout value and checking LED ON/OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: Led status "
                                  "for %s is verified successfully"
                                  % sx_state.upper(), test_case_id, script_id,
                                  "LSD", "None", log_level, tbd)
                return True
            elif sx_state.upper() == current_state and \
                    led_status.upper() == STR_ON:                               # Checking the return code and stdout value and checking LED ON/OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: Led status "
                                  "for %s is verified successfully and LED is "
                                  "in %s state" % (sx_state.upper(),
                                                   led_status.upper()),
                                  test_case_id, script_id, "LSD", "None",
                                  log_level, tbd)
                return True
            elif sx_state != current_state and \
                    led_status.upper() == STR_OFF:                              # Checking the return code and stdout value and checking LED ON/OFF
                library.write_log(lib_constants.LOG_INFO, "INFO: Led status "
                                  "for %s is verified successfully and LED is "
                                  "in %s state" % (sx_state.upper(),
                                                   led_status.upper()),
                                  test_case_id, script_id, "LSD", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to verify Led status for %s state"
                                  % sx_state.upper(), test_case_id, script_id,
                                  "LSD", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                              "to generate the sut interface log properly",
                              test_case_id, script_id, "LSD", "None",
                              log_level, tbd)
            return False
    except Exception as ex:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in read_sx_led_"
                          "status_using_lsd_device() error due to : %s" % ex,
                          test_case_id, script_id, "LSD", "None",
                          log_level, tbd)
        return False


def execute_lsd_command(sx_state, lsd_command, led_status, led_expected_status,
                        test_case_id, script_id, log_level, tbd):

    """
    Function Name   : execute_lsd_command
    Parameters      : lsd_command, led_status, led_expected_status, tc_id,
                      script_id, log_level, opt
    Functionality   : Execute the lsd_command and evaluates with expected led
                      status
    Function Invoked: utils.write_log(), utils.execute_with_command()
    Return Value    : (Bool)'True' on successful action and 'False' on
                          failure
    """

    while wait_time != 0:
        result = utils.execute_with_command(lsd_command, test_case_id,
                                            script_id, "LSD", log_level, tbd)   # Executing the command to read the status of LED CS/S0i3
        if result is False:
            utils.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                            "execute command: %s" % lsd_command, test_case_id,
                            script_id, "LSD", "None", log_level, tbd)
            return False
        elif led_expected_status in result.stdout and result.returncode == 0:   # Checking the return code and stdout value
            utils.write_log(lib_constants.LOG_INFO, "INFO: Led status for %s "
                            "is verified successfully and status is as "
                            "expected %s" % (sx_state, led_status),
                            test_case_id, script_id, "LSD", "None", log_level,
                            tbd)
            return True
        else:
            time.sleep(sleep_time)
            wait_time = wait_time - sleep_time

    library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to verify "
                      "LED status for %s and status is %s"
                      % (sx_state, led_status), test_case_id, script_id, "LSD",
                      "None", log_level, tbd)
    return False
