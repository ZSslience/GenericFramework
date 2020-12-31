__author__ = 'tnaidux'

# Global Python Imports
import os
import subprocess
import time

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : remote_reboot
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True on successful restart action, False otherwise
# Purpose       : To perform restart on target machine
################################################################################


def remote_reboot(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        sx_state = "WR"
        cycles = 1
        duration = 30

        system_cycling_tool_path = \
            utils.ReadConfig("System_Cycling_Tool", "tool_path")

        system_cycling_exe = \
            utils.ReadConfig("System_Cycling_Tool", "system_cycling_exe")

        target_sut_ip = utils.ReadConfig("SUT_IP", "target_sut_ip")

        if "FAIL:" in system_cycling_tool_path or \
           "FAIL:" in system_cycling_exe:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entries under tag"
                              " [System_Cycling_Tool]", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully got "
                              "config entries under tag [System_Cycling_Tool]",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        if "FAIL:" in target_sut_ip:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entries under tag [SUT_IP] for "
                              "target_sut_ip", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully got "
                              "config entries under tag [SUT_IP] as "
                              "%s" % target_sut_ip, test_case_id, script_id,
                              "None", "None", log_level, tbd)

        command = '"' + str(system_cycling_exe).strip() + '"' + ' -al -ip ' + \
            str(target_sut_ip) + ' -' + str(sx_state) + ' i:' + str(cycles) + \
            ' tw:' + str(duration) + ' ts:' + str(30)                           # Command to execute Warm Reset using Intel System Cycling Tool

        library.write_log(lib_constants.LOG_INFO, "INFO: Command to Perform "
                          "remote reboot is %s " % command, test_case_id,
                          script_id, "None", "None", log_level, tbd)

        if os.path.exists(system_cycling_tool_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: System Cycling "
                              "tool path exists in the system", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            os.chdir(system_cycling_tool_path)

            library.write_log(lib_constants.LOG_INFO, "INFO: Changed current "
                              "directory path to System Cycling Tool path ",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: System "
                              "Cycling Tool does not exist", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.PIPE)

        output = result.communicate()[0]

        output_log = script_id.replace(".py", ".log")

        if os.path.exists(output_log):
            os.remove(output_log)

        with open(output_log, "w") as file_out:
            file_out.write(str(output))

        returncode = int(result.returncode)

        os.chdir(os.getcwd())
        os.system("ping " + target_sut_ip + " > Result.txt")                    # Writing the ping status in result.txt file

        flag = 0
        with open("Result.txt", "r") as file_out:                               # Open Result.txt in read mode
            for line in file_out:
                if "destination host unreachable." in line.lower():
                    flag = 1
                    break
                elif "could not find" in line.lower():
                    flag = 1
                    break
                elif "Request timed out." in line.lower():
                    flag = 1
                    break

        if 1 == flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: System is "
                              "BIOS or EDK Shell", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            if 1 != flag and 0 == returncode or 5 == returncode:
                library.write_log(lib_constants.LOG_INFO, "INFO: Ping "
                                  "operation to target System is successful",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                library.write_log(lib_constants.LOG_INFO, "INFO: System is "
                                  "in OS", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                                  "perform Ping operation to target System, "
                                  "SUT is not in OS", test_case_id, script_id,
                                  "None", "None",
                                  log_level, tbd)

                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to perform Remote Reboot operation",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : monitor_service_up
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if SUT is in OS else False
# Purpose       : To Check sut is in OS
################################################################################


def monitor_service_up(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        post_code = ["0000", "ab03", "ab04", "abc5"]
        if library.check_for_post_code(post_code, 250, test_case_id, script_id,
                                       log_level, tbd):                         # If post code found, pass

            library.write_log(lib_constants.LOG_INFO, "INFO: Post code read "
                              "successfully for OS", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            time.sleep(40)
            target_sut_ip = utils.ReadConfig("SUT_IP", "IP")
            if "FAIL:" in target_sut_ip:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get config entries under tag [SUT_IP] "
                                  "for IP", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            time.sleep(60)
            os.chdir(os.getcwd())
            os.system("ping " + target_sut_ip + " > Result.txt")                # Writing the ping status in result.txt file

            flag = 0
            with open("Result.txt", "r") as file_out:                           # Open Result.txt in read mode
                for line in file_out:
                    if "destination host unreachable." in line.lower():
                        flag = 1
                        break
                    elif "could not find" in line.lower():
                        flag = 1
                        break
                    elif "Request timed out." in line.lower():
                        flag = 1
                        break

            if 1 == flag:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to ping check for SUT", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: successfully "
                                  "pinged SUT and SUT is in OS", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to read "
                          "desired post code for OS", test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : monitor_service_down
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True if SUT is in shutdown state else False
# Purpose       : To Check sut is in Shutdown state
################################################################################

def monitor_service_down(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        post_code = ["b505", "ffff"]
        if library.check_for_post_code(post_code, 600, test_case_id, script_id,
                                       log_level, tbd):                         # If post code found, pass

            library.write_log(lib_constants.LOG_INFO, "INFO: Post code read"
                              " successfully for S5", test_case_id, script_id,
                              "None", "None", log_level, tbd)

            target_sut_ip = utils.ReadConfig("SUT_IP", "IP")

            if "FAIL:" in target_sut_ip:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                 "to get config entries under tag [SUT_IP] for "
                                  "IP", test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
            #time.sleep(30)
            os.chdir(os.getcwd())
            time.sleep(10)
            os.system("ping " + target_sut_ip + " > Result.txt")                # Writing the ping status in result.txt file
            time.sleep(10)
            flag = 0
            with open("Result.txt",
                      "r") as file_out:                                         # Open Result.txt in read mode
                for line in file_out:
                    if "Received = 4" not in line.lower():
                        flag = 1
                        break
                    elif "destination host unreachable." in line.lower():
                        flag = 1
                        break
                    elif "could not find" in line.lower():
                        flag = 1
                        break
                    elif "Request timed out." in line.lower():
                        flag = 1
                        break
            if 1 == flag:
                library.write_log(lib_constants.LOG_INFO, "INFO: Unable "
                                  "to ping check for SUT and SUT is in shutdowm"
                                  " state", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Able to "
                                  "ping SUT sut is not in OFF state",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to read "
                          "desired post code for shutdown", test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
