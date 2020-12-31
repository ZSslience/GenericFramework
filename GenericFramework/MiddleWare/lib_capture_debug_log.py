__author__ = r'kvex\hvinayx\tnaidux'

# General Python Imports
import mmap
import os
import shutil
import subprocess
import time
from threading import Thread

# Local Python Imports
import library
import utils
import lib_constants


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def restart_and_capture_debug_log(token_string, tool, baudrate, test_case_id,
                                  script_id, log_level="ALL", tbd=None):

    try:
        thread1 = ThreadWithReturnValue(target=capture_debug_log,
                                        args=(tool, baudrate, test_case_id,
                                              script_id, log_level, tbd))
        thread2 = ThreadWithReturnValue(target=restart_target_using_ict,
                                        args=(test_case_id, script_id,
                                              log_level, tbd))

        thread1.start()
        thread2.start()

        if thread1.join() and thread2.join():
            library.write_log(lib_constants.LOG_INFO, "INFO: %s initiated "
                              "successfully" % token_string, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "initiate %s" % token_string, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name   : capture_debug_log
# Parameters      : tool, baudrate, tc_id, script_id, log_level and tbd
# Functionality   : Capture debug log
# Return Value    : Returns True on success and False otherwise
################################################################################


def capture_debug_log(tool, baudrate, tc_id, script_id, log_level="ALL",
                      tbd=None):

    try:
        if "PUTTY" == tool and (lib_constants.BAUDRATE1 == baudrate or
                                lib_constants.BAUDRATE2 == baudrate):           # If putty in tool name and baudrate value is valid

            capture_log = capture_debug_log_putty(tool, baudrate, tc_id,
                                                  script_id, log_level, tbd)    # Function call for to capture debug log using putty

            if capture_log:
                library.write_log(lib_constants.LOG_INFO, "INFO: Debug Log "
                                  "capture initiated successfully using "
                                  "putty", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to initiate Debug Log capture", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "TERATERM" == tool and (lib_constants.BAUDRATE1 == baudrate or
                                     lib_constants.BAUDRATE2 == baudrate):
            capture_log = capture_debug_log_teraterm(tool, baudrate, tc_id,
                                                     script_id, log_level,
                                                     tbd)                       # Function call for to capture debug log using teraterm

            if capture_log:
                library.write_log(lib_constants.LOG_INFO, "INFO: Debug Log "
                                  "capture initiated successfully using "
                                  "teraterm", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to initiate Debug Log capture", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "WINDBG" == tool and (lib_constants.BAUDRATE1 == baudrate):
            capture_log = capture_debug_log_windbg(tool, baudrate, tc_id,
                                                   script_id, log_level, tbd)   # Function call for to capture debug log using Windbg

            if capture_log:
                library.write_log(lib_constants.LOG_INFO, "INFO: Debug Log "
                                  "capture initiated successfully using "
                                  "windbg", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to initiate Debug Log capture", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: tool or "
                              "baudrate is not handled", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : capture_debug_log_putty
# Parameters      : tool, baudrate, tc_id, script_id, log_level and tbd
# Functionality   : Will capture debug log using putty
# Return Value    : Returns True on success and False otherwise
################################################################################


def capture_debug_log_putty(tool, baudrate, tc_id, script_id, log_level="ALL",
                            tbd=None):

    try:
        baudrate = str(baudrate)
        file_name = str(script_id).replace(".py", ".log")
        file_name = os.path.join(lib_constants.SCRIPTDIR, file_name)

        if os.path.exists(file_name):
            os.remove(file_name)

        com_port = utils.ReadConfig("CAPTURE_DEBUG_LOG",
                                    "SERIAL_CABLE_COM_PORT")                    # Get the com port details from config file
        if "FAIL:" in com_port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "fetch com port for serial cable from "
                              "Config.ini", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            com_port = "COM" + str(com_port)
            library.write_log(lib_constants.LOG_INFO, "INFO: Com port for "
                              "serial cable is found as %s" % com_port,
                              tc_id, script_id, "None", "None", log_level, tbd)

        service_name = lib_constants.PLINK_SERVICE
        if kill_service(service_name, tc_id, script_id, log_level, tbd):
            pass

        if os.path.exists(lib_constants.PLINK_EXE):                             # If putty path exists in os
            library.write_log(lib_constants.LOG_INFO, "INFO: plink.exe is "
                              "found as given: %s" % lib_constants.PLINK_EXE,
                              tc_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Plink.exe "
                              "is not found: %s" % lib_constants.PLINK_EXE,
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False

        command = lib_constants.PLINK_EXE + " -v -serial " + com_port + \
            " -sercfg " + str(baudrate) + ',8,n,1,X > "' + \
            file_name + '" 2>&1'                                                # Open the putty application and start capturing debug log

        library.write_log(lib_constants.LOG_INFO, "INFO: Command for to "
                          "capture debug log using putty is '%s'" % command,
                          tc_id, script_id, "None", "None", log_level, tbd)

        subprocess.Popen(command, shell=True, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name     : capture_debug_log_teraterm
# Parameters        : token, tc_id, script_id, log_level, tbd
# Functionality     : will capture debug log using teraterm
# Return Value      : returns True on success and False otherwise
################################################################################


def capture_debug_log_teraterm(tool, baudrate, tc_id, script_id,
                               log_level="ALL", tbd=None):

    try:
        log_name = script_id.replace(".py", ".log")
        if os.path.exists(log_name):
            os.remove(log_name)

        serial_port = utils.ReadConfig("CAPTURE_DEBUG_LOG",
                                       "SERIAL_CABLE_COM_PORT")
        if "FAIL:" in serial_port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry missing for serial port", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Serial port for "
                              "serial cable is found as %s" % serial_port,
                              tc_id, script_id, "None", "None", log_level, tbd)

        if os.path.exists(lib_constants.TERATERM_PATH):
            library.write_log(lib_constants.LOG_INFO, "INFO: Tera Term tool "
                              "is available in the system", tc_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Tera Term "
                              "tool is not available in the system", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        service_name = lib_constants.TERATERM_SERVICE
        if kill_service(service_name, tc_id, script_id, log_level, tbd):
            pass

        command = '"' + lib_constants.TERATERM_PATH + '\\ttermpro.exe" /c=' + \
            serial_port + " /BAUD=" + baudrate + " /l=" + \
            os.path.join(lib_constants.SCRIPTDIR, log_name)

        library.write_log(lib_constants.LOG_INFO, "INFO: Command for to "
                          "capture debug log using TeraTerm is '%s'" % command,
                          tc_id, script_id, "None", "None", log_level, tbd)

        subprocess.Popen(command, shell=True, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name    : copy_log_file
# Parameters       : file_name, tc_id, script_id, log_level, tbd
# Functionality    : will move log to sut
# Return Value     : returns True on success and False otherwise
################################################################################


def copy_log_file(file_name, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        sut_ip = utils.ReadConfig("SUT_IP", "IP")

        if "FAIL:" in sut_ip:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry for under SUT_IP", tc_id,
                              script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: SUT is identified"
                              " as %s" % sut_ip, tc_id, script_id, "None",
                              "None", log_level, tbd)

        file_name = os.path.join(lib_constants.SCRIPTDIR, file_name)
        destination_path = file_name.split("\\")[1:-1]
        destination_path = "\\".join(destination_path)
        path = file_name.split("\\")[2:-1]
        path = "\\".join(path)

        try:
            destination = "\\\\" + sut_ip + "\\" + destination_path
            try:
                shutil.copy(file_name, destination)
            except:
                cmd_to_run = "xcopy " + file_name + " " + destination + " " + "/E /Y /Q /R"
                result = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=True).communicate()
                if "0 File(s) copied" in str(result):
                    return False
                else:
                    print("File/Files Copied Successfully from %s to %s" % (
                        file_name, destination))
                    print(str(result))
                    return True
        except:
            destination = "Z:\\" + path
            try:
                shutil.copy(file_name, destination)
            except:
                cmd_to_run = "xcopy " + file_name + " " + destination + " " + "/E /Y /Q /R"
                result = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=True).communicate()
                if "0 File(s) copied" in str(result):
                    return False
                else:
                    print("File/Files Copied Successfully from %s to %s" % (
                        file_name, destination))
                    print(str(result))
                    return True

        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

##############################################################################
# Function Name     : terminate_plink
# Parameters        : tool, file_name, tc_id, script_id, log_level, tbd
# Functionality     : will terminate plink process and checks for log
#  Return Value     : returns True on success and False otherwise
################################################################################


def terminate_plink(tool, file_name, tc_id, script_id, log_level="ALL",
                    tbd=None):

    try:
        time.sleep(lib_constants.ONE_EIGHTY_ONE)
        copy_log_file(file_name, tc_id, script_id, log_level, tbd)
        time.sleep(lib_constants.TEN_SECONDS)
        if library.check_for_post_code(lib_constants.S5_WAKE_POSTCODE,
                                       250, tc_id, script_id, log_level, tbd):

            if "PUTTY" == tool.upper():
                service_name = lib_constants.PLINK_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Plink.exe"
                                      " has been terminated", tc_id, script_id,
                                      "None", "None", log_level, tbd)
            elif "TERATERM" == tool.upper():
                service_name = lib_constants.TERATERM_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Tera Term"
                                      " has been terminated", tc_id, script_id,
                                      "None", "None", log_level, tbd)
            elif "WINDBG" == tool:
                service_name = lib_constants.WINDBG_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Windbg "
                                      "has been terminated", tc_id, script_id,
                                      "None", "None", log_level, tbd)
            else:
                pass

            time.sleep(lib_constants.NORMAL_FLASH_DELAY)                        # Wait for proper network mapping
            copy_log_file(file_name, tc_id, script_id, log_level, tbd)
            time.sleep(lib_constants.TEN_SECONDS)

            return True
        else:
            if "PUTTY" == tool:
                service_name = lib_constants.PLINK_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    pass
            elif "TERATERM" == tool:
                service_name = lib_constants.TERATERM_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    pass
            elif "WINDBG" == tool:
                service_name = lib_constants.WINDBG_SERVICE

                if kill_service(service_name, tc_id, script_id, log_level, tbd):
                    pass
            else:
                pass

            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name     : capture_debug_log_windbg
# Parameters        : tool, baudrate, tc_id, script_id, log_level, tbd
# Functionality     : will capture debug log using windbg
# Return Value      : returns True on success and False otherwise
################################################################################


def capture_debug_log_windbg(tool, baudrate, tc_id, script_id, log_level="ALL",
                             tbd="None"):

    try:
        com_port = utils.ReadConfig("CAPTURE_DEBUG_LOG",
                                    "SERIAL_CABLE_COM_PORT")                    # Get the com port details from config file
        if "FAIL:" in com_port:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "fetch com port for serial cable from "
                              "Config.ini", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            com_port = "COM" + str(com_port)
            library.write_log(lib_constants.LOG_INFO, "INFO: Com port for "
                              "serial cable is found as %s" % com_port,
                              tc_id, script_id, "None", "None", log_level, tbd)

        windbg_path = utils.ReadConfig("WINDBG_PATH", "path")                   # Windbg tool path
        if "FAIL:" in windbg_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the config entry for windbg_path", tc_id,
                              script_id, "None", "None", log_level, tbd)

        if os.path.exists(windbg_path):                                         # Verify if Windbg path exists or not
            library.write_log(lib_constants.LOG_INFO, "INFO: WinDbg tool is "
                              "available on the system", tc_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Windbg tool"
                              " is not available on the system", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        log_name = script_id.replace(".py", ".log")
        if os.path.exists(log_name):                                            # Checking if the log already exists in given path
            os.remove(log_name)                                                 # Check for log to be generated is already present, remove if found

        command = '"' + windbg_path + '\\windbg.exe" -k com:port=' + com_port \
            + ",baud=" + baudrate + " -logo " + \
            os.path.join(lib_constants.SCRIPTDIR, log_name)                     # Command to get the windbg log from host machine

        library.write_log(lib_constants.LOG_INFO, "INFO: command for to "
                          "capture debug log using WinDbg tool is '%s'"
                          % command, tc_id, script_id,
                          "None", "None", log_level, tbd)

        subprocess.Popen(command, shell=True, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : restart_target_using_ict
# Parameters      : tool, baudrate, tc_id, script_id, log_level and tbd
# Functionality   : Capture debug log
# Return Value    : Returns True on success and False otherwise
################################################################################


def restart_target_using_ict(test_case_id, script_id, log_level="ALL",
                             tbd="None"):

    try:
        sx_state = "WR"
        cycles = 1
        duration = 30

        system_cycling_tool_path = \
            utils.ReadConfig("System_Cycling_Tool", "tool_path")
        system_cycling_exe = \
            utils.ReadConfig("System_Cycling_Tool", "system_cycling_exe")
        target_sut_ip = utils.ReadConfig("SUT_IP", "target_sut_ip")

        if "FAIL:" in [system_cycling_tool_path, system_cycling_exe,
                       target_sut_ip]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entries for system_cycling_tool_path"
                              " or system_cycling_exe or target_sut_ip",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        command = '"' + str(system_cycling_exe).strip() + '"' + ' -al -ip ' + \
            str(target_sut_ip) + ' -' + str(sx_state) + ' i:' + str(cycles) + \
            ' tw:' + str(duration) + ' ts:' + str(30)                           # Command to execute Restart using Intel System Cycling Tool

        library.write_log(lib_constants.LOG_INFO, "INFO: Command to Perform "
                          "restart is %s " % command, test_case_id,
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

        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def kill_service(service_name, test_case_id, script_id, log_level="ALL",
                 tbd=None):

    try:
        task_list_text_file_path = r"C:\Testing\task_list.txt"

        if os.path.exists(task_list_text_file_path):
            os.remove(task_list_text_file_path)

        command = 'tasklist /FI "IMAGENAME eq %s" > %s' % \
            (service_name, task_list_text_file_path)

        os.system(command)
        f = open(task_list_text_file_path)
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        if s.find("%s" % service_name) != -1:
            library.write_log(lib_constants.LOG_INFO, "INFO: plink.exe service"
                              " is running, killing now", test_case_id,
                              script_id, lib_constants.TOOL_TTK2, "None",
                              log_level, tbd)

            result = os.system("taskkill /F /IM %s" % service_name)
            if 0 == result:
                time.sleep(1)
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: plink.exe service killed "
                                  "successfully", test_case_id, script_id,
                                  lib_constants.TOOL_TTK2, "None", log_level,
                                  tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to kill TTK2_Server.exe "
                                  "service", test_case_id, script_id,
                                  lib_constants.TOOL_TTK2, "None", log_level,
                                  tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
