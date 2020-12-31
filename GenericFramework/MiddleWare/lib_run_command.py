__author__ = 'bchowdhx/kvex/Sneha Pingle/skotasiv/tnaidux/surabh1x'                      # Modified on 24 May 2019

# Global Python Imports
import fnmatch
import glob
import os
import re
import shutil
import subprocess
import sys
import time
from threading import Thread

# Local Python Imports
import library
import lib_constants
import lib_parse_log_file
import KBM_Emulation as kbm
import utils
import lib_remote_reboot
import lib_ttk2_operations

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={},
                 Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return

################################################################################
# Function Name : powershell_script()
# Description   : powershell script generation
# Parameters    : command, test_case_id, script_id, loglevel and tbd
# Returns       : True on successful operation, False otherwise
# Purpose       : Generate powershell script
################################################################################


def powershell_script(command, test_case_id, script_id, loglevel="ALL",
                      tbd=None):

    try:
        for filename in os.listdir("."):                                        # Check for filename in directory for nsh
            if filename.endswith("ps1"):                                        # If any nsh file is there unlink the file
                f = open(filename, "r")
                f.close()                                                       # Close before unlink
                os.unlink(filename)

        if ".ps1" in command.lower():                                           # If command contains a powershell based tool
            command_new = ""

            for item in command.split(" "):
                if ".ps1" in item.lower():
                    toolpath = library.find_file(item, "C:\\", test_case_id,
                                                 script_id, loglevel, tbd)
                    item = toolpath + "\\" + item                               # Prefix the tool namme with the toolpath
                command_new = command_new + " " + item
            command = command_new

        f = open(lib_constants.SCRIPTDIR + "\\psquery.ps1", 'w')                # File operation

        if 0 != len(command):
            if command in lib_constants.PWR_SHELL_CMD:
                if "$" in command and "." in command:                           # If any object is there in command then execute
                    command_query = command.split(".")[1]
                    command = "$ptt." + command_query                           # Replace $ptt object in input command which is we are creating in powershell
                    f.write(lib_constants.PWR_SHELL_CMD)                        # Command to create object $ptt
                    f.write(command)                                            # writes command to file
                else:
                    f.write(command)                                            # writes command to file
            else:
                f.write(command)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "write command to ps1 file failed", test_case_id,
                              script_id, "None","None", loglevel, tbd)
            pass

        f.close()
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False

    ps_file = lib_constants.SCRIPTDIR + "\\psquery.ps1"
    ps_size = os.path.getsize(ps_file)                                          # Check for file size

    if '0' == ps_size:                                                          # Return false if size == 0
        library.write_log(lib_constants.LOG_WARNING, "WARNING: 'Psquery' file "
                          "created with zero data", test_case_id, script_id,
                          "None","None",loglevel, tbd)
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: 'Psquery' file "
                          "created successfully with data", test_case_id,
                          script_id, "None","None", loglevel, tbd)
        return True

################################################################################
# Function Name : nsh_file_gen()
# Description   : generating nsh file
# Parameters    : command, test_case_id, script_id, loglevel and tbd
# Returns       : True on successful nsh file creation, False otherwise
# Purpose       : To generate nsh file
################################################################################


def nsh_file_gen(command, test_case_id, script_id, loglevel="ALL", tbd=None):

    try:
        os.chdir(lib_constants.SCRIPTDIR)
        disk_list_file = script_id.replace(".py", "_disk_list.txt")

        command_to_get_drive_list = \
            "wmic logicaldisk get caption, description, volumename > " + \
            disk_list_file

        os.system(command_to_get_drive_list)

        with open(disk_list_file, "r") as file_out:
            for line, l in enumerate(file_out):
                pass

        no_of_lines = line + 1
        if no_of_lines <= 4:
            log_file = script_id.replace(".py", ".txt")                         # Write to log file as txt file

            if "efi" in command and "FPT" not in command.upper():
                if "CHIPSEC" in command.upper():
                    command = 'cd EFI\chipsec' + " \n"+ command
                    gen_cmd_f = command + " > " + "fs0:\\" + log_file
                else:
                    tool_name = command.split(".efi")[0]
                    command = 'cd '+tool_name+" \n"+command
            if "vtinfo" in command.lower():                                     # Command to run vtinfo tests (verbose) in edk shell
                gen_cmd_f = command + " -t -v >a fs0:\\" + log_file
            else:
                gen_cmd_f = command + " > " + log_file

            if "SecurityInfo.efi" in command or "FFT.efi" in command:           # Securityinfo.efi or fft.efi command as a nested script
                f = open("subscript.nsh", 'w')

                if len(gen_cmd_f) != 0:
                    f.write(gen_cmd_f)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to write the command in nested "
                                      ".nsh file", test_case_id, script_id,
                                      "None", "None", loglevel, tbd)
                    pass
                f.close()

                gen_cmd_f = "subscript.nsh"
                library.write_log(lib_constants.LOG_INFO, "INFO: Command "
                                  "successfully nested", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
            else:
                gen_cmd_f = command + " > " + log_file

            gen_cmd_f = gen_cmd_f + " \n"
            gen_cmd_f = gen_cmd_f + "stall 1000000"+"\n"
            gen_cmd_f = gen_cmd_f + "rm fs1:\\" + log_file + " \n"
            gen_cmd_f = gen_cmd_f + "cp -r fs0:\\"+log_file + " fs1: \n"

            if os.path.exists("startup.nsh"):                                   # Check for startup.nsh file, if exist remove
                os.remove("startup.nsh")
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: startup.nsh "
                                  "does not exist", test_case_id, script_id,
                                  "None", "None", loglevel, tbd)
                pass

            f = open("startup.nsh", 'w')                                        # File operation
            f.write("bcfg boot mv 01 00" + '\n' + "fs0:" + '\n')

            if len(gen_cmd_f) != 0:
                f.write(gen_cmd_f)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to write the command in startup.nsh file",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                pass

            if "GRESET" in command.upper():
                pass
            else:
                f.write("reset")

            f.close()                                                           # File closing after writing to file
        else:
            drive = r"S:\\"
            os.chdir(drive)
            log_file = script_id.replace(".py", ".txt")                         # Write to log file as txt file
            dev_identifier_filename = test_case_id + ".log"
            dev_identifier_file = os.path.join(drive, dev_identifier_filename)

            create_file(dev_identifier_file, lib_constants.ONE_KB,
                        test_case_id, script_id, loglevel, tbd)

            mapped_drive = find_mapped_folder(dev_identifier_filename)

            log_path = drive + os.sep + log_file
            gen_cmd = generate_command(command, log_file)                       # Generates the command

            exec_cmd = mapped_drive + gen_cmd                                   # Complete command with mapping information and the command which will be written to startup.nsh file for execution
            os.chdir(lib_constants.SCRIPTDIR)
            if not os.path.exists("startup.nsh"):                               # Check for startup.nsh file, if exist remove
                library.write_log(lib_constants.LOG_INFO, "INFO: startup.nsh "
                                  "file does not exist", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
            else:
                os.remove("startup.nsh")

            with open("startup.nsh", "w+") as nsh_file:
                nsh_file.write(exec_cmd)

        nsh1_size = os.path.getsize("startup.nsh")

        if '0' == nsh1_size:                                                    # Check for startup nsh file sizes and return false if size is 0
            library.write_log(lib_constants.LOG_WARNING, "WARNING: .nsh file "
                              "is not generated properly", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: .nsh file "
                              "successfully created", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False

################################################################################
# Function name : generate_command
# Description   : Generates the EFI shell command (for non tool execution)
# Parameters    : command_list, log_file
# Purpose       : Generates the EFI shell command (for non tool execution)
# Returns       : True on successful action, False otherwise
################################################################################


def generate_command(command_list, log_file):

    try:
        command = ""
        if not "," in command_list:
            command_code = '''''' + command_list + ''' > ''' + log_file + '''   # Executes the command and redirects the log to output file in append mode
                    stall 500000                                                # Wait for 5 seconds
                    endif

                    :END
                    set -d myfs                                                 # Deletes the variable set
                    reset
                    '''
        else:
            for cmd in command_list:
                command_code = '''''' + cmd + ''' > ''' + log_file + '''        # Executes the command and redirects the log to output file in append mode
            stall 500000                                                        # Wait for 5 seconds
            endif
        
            :END
            set -d myfs                                                         # Deletes the variable set
            reset
            '''
        return command_code
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          "None", "None", "None", "None", "None", "None")
        return False

################################################################################
# Function name : create_file
# Description   : This class method creates or overwrites file based on
#                 specified file size
# Parameters    : file_name - Full path to the file,
#                 file_size - Size of the file bytes
# Purpose       : creates or overwrites file based on specified file size
# Returns       : True on successful action, False otherwise
################################################################################


def create_file(file_name, file_size, test_case_id, script_id, loglevel, tbd):

    try:
        # Create directory for file if missing
        if not os.path.isdir(os.path.dirname(file_name)):
            library.write_log(lib_constants.LOG_INFO, "INFO: Creating "
                              "Directory: %s" % (os.path.dirname(file_name)),
                              test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            os.makedirs(os.path.dirname(file_name), 0o777)

        library.write_log(lib_constants.LOG_INFO, "INFO: Creating file:%s "
                          "with size:%s bytes" % (file_name, file_size),
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)

        # Create empty file
        with open(file_name, 'wb') as output_file:
            output_file.truncate(file_size)

        library.write_log(lib_constants.LOG_INFO, "INFO: File:%s, size:%s "
                          "bytes created" % (file_name, file_size),
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False

###############################################################################
# Function name : find_mapped_folder
# Description   : Used to find the correct mapping details for the bootable
#                 drive in EFI shell
# Parameters    : identifier_fil
# Purpose       : To find the correct mapping details for the bootable drive
#                 in EFI shell
# Returns       : True on successful action, False otherwise
################################################################################


def find_mapped_folder(identifier_file):

    try:
        gen_cmd = '''
        bcfg boot mv 01 00                                                      # Reverts the boot order set
        set -v myfs 0                                                           # Initializing file system mapping to FS0:
        if exist FS0:\\''' + identifier_file + ''' then                         # Checks the identifier file in file system FS0:, if found FS0 is taken as the mapping
        FS0:
        goto FSFOUND
        endif
    
        for %a run (1 10)                                                       # To determine the FS<x> number, check goes up to FS10: the inner for loop)
        set -v myfs %a
        if exist FS%myfs%:\\''' + identifier_file + ''' then
        FS%myfs%:                                                               # Change the working directory to FS<myfs>:
        goto FSFOUND
        endif
        endfor
        goto END
    
        :FSFOUND
        if exists ''' + identifier_file + ''' then
        '''
        return gen_cmd
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          "None", "None", "None", "None", "None", "None")
        return False

################################################################################
# Function name : drive_map_ret
# Description   : To map a drive from the available free memory at hard disk
#                 and to place all .sh files to it
# Parameters    : None
# Purpose       : Drive map and copy
# Returns       : True on success to map drive, False otherwise
################################################################################


def drive_map_ret(test_case_id, script_id, loglevel="ALL", tbd=None):

    edk_pass_flag = False
    edk_path = "S:\\boot"                                                       # Set edk path as S:Boot

    edk_fail_flag = False
    log_file = script_id.replace(".py", ".txt")
    path1 = os.getcwd() + "\log" + "\\\\" + log_file
    time.sleep(lib_constants.POWER_TEST_MIN_TIME)                               # Sleep for 30 seconds

    if os.path.exists('S:'):                                                    # Check for S drive
        os.chdir(edk_path)

        for filename in os.listdir("."):                                        # Check for filename in directory
            if filename.endswith("txt"):
                if log_file in filename:
                    shutil.copy(filename, path1)                                # File operations copying
                    edk_fail_flag = True
                    break
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: No txt "
                                      "file exists", test_case_id, script_id,
                                      "None","None", loglevel, tbd)
                    pass
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: No txt file "
                                  "exists", test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                pass

        if edk_fail_flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: The drive is "
                              "mapped successfully", test_case_id, script_id,
                              "None", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "map the drive", test_case_id, script_id, "None",
                              "None", loglevel, tbd)
            return False
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to map "
                          "the drive", test_case_id, script_id, "None", "None",
                          loglevel, tbd)
        return False

################################################################################
# Function Name : drive_cleanup()
# Description   : drive cleanup function
# Parameters    : test_case_id, script_id, loglevel and tbd
# Returns       : True on successful removal of all .nsh files, False otherwise
# Purpose       : Cleans up nsh file from the logical drive
################################################################################


def drive_cleanup(test_case_id, script_id, loglevel="ALL", tbd=None):

    flag_clean = 0

    if os.path.exists('S:'):                                                    # Check for path exists or not
        os.chdir('S:\\')                                                        # Navigate to s:
        for filename in os.listdir("."):                                        # Check for filename in directory for nsh
            if filename.endswith("nsh"):                                        # If any nsh file is there unlink the file
                flag_clean += 1
                os.unlink(filename)

        os.chdir(lib_constants.SCRIPTDIR)                                       # Navigate back to script dir

        if 0 == flag_clean:
            library.write_log(lib_constants.LOG_INFO, "INFO: No .nsh files "
                             "are available in the directory", test_case_id,
                              script_id, "None", "None", loglevel, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s .nsh file(s) "
                              "successfully removed" % flag_clean,
                              test_case_id, script_id, "None", "None",
                              loglevel, tbd)
            return True
    else:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Exception in "
                          "removing .nsh files", test_case_id, script_id,
                          "None","None", loglevel, tbd)
        return False

################################################################################
# Function Name : create_logical_drive()
# Description   : creates a logical partition in the system with the drive
#                 letter provided as the parameter
# Parameters    : driver letter(drive name without ":"), tc_id, script_id,
#                 loglevel, tbd
# Returns       : True on successful logical drive creation, False otherwise
# Purpose       : Creates logical drive
################################################################################


def create_logical_drive(drive_letter, tc_id, script_id, loglevel="ALL",
                         tbd=None):

    try:
        if os.path.exists(drive_letter + ":"):                                  # Check for path exist or not
            library.write_log(lib_constants.LOG_INFO, "INFO: Drive %s: is "
                              "already available for use" % drive_letter,
                              tc_id, script_id, "None", "None", loglevel, tbd)
            return True
        else:
            command = "mountvol " + drive_letter + ": /s"                       # Command to mountvol

            if not os.system(command):                                          # Run in command prompt
                time.sleep(lib_constants.POWER_TEST_MIN_TIME)                   # Sleep for 45 seconds it may take up to 30 seconds for the new drive to be accessible
                if os.path.exists(drive_letter + ":"):                          # Check for path for drive exists or not
                    library.write_log(lib_constants.LOG_INFO, "INFO: Drive %s:"
                                      " is available for use" % drive_letter,
                                      tc_id, script_id, "None", "None",
                                      loglevel, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to create logical partition %s"
                                      % drive_letter, tc_id, script_id, "None",
                                      "None", loglevel, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to create logical partition %s"
                                  % drive_letter, tc_id, script_id, "None",
                                  "None", loglevel, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None","None", loglevel, tbd)
        return False

################################################################################
# Function Name : run_command()
# Description   : run the command given in command prompt
# Parameters    : cmd_to_run, tc_id, script_id, loglevel and tbd
# Returns       : True on successful command execution and log verification,
#                 False otherwise
# Purpose       : To run command in command prompt
################################################################################


def run_command(cmd_to_run, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if "config-file-bios" in cmd_to_run.lower():
            config_value = utils.ReadConfig("FILE", "BIOS")
            config_value = config_value.split("\\")[-1]
            cmd_to_run = cmd_to_run.replace("config-file-bios", config_value)

        if "config-usbdebug-bdf" in cmd_to_run.lower():
            config_value = utils.ReadConfig("USBDEBUG", "BDF")
            config_value = config_value.split("\\")[-1]
            cmd_to_run = cmd_to_run.replace("config-usbdebug-bdf", config_value)


        log_path = script_id.replace(".py", ".log")

        if "PECI" in cmd_to_run.upper():
            log = script_id.replace(".py", ".csv")
            try:
                if os.path.exists(lib_constants.PECI_LOG):                      # If log pre exists
                    try:
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "Deleting older/existing temperature"
                                          " log file", tc_id, script_id,
                                          "PECI", "None", log_level, tbd)
                        os.remove(lib_constants.PECI_LOG)                       # Deleting older log
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION:"
                                          " Exception in deleting old log due "
                                          "to %s." % e, tc_id, script_id,
                                          "PECI",  "None", log_level, tbd)
                        return False

                os.chdir(lib_constants.PECI_INSTALLED_PATH)
                cmd_to_run = lib_constants.PECI_APP + \
                    cmd_to_run.split(lib_constants.PECI_APP)[1]
                subprocess.Popen(cmd_to_run, shell=True, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)                        # Run the command to get temperature using PECI tool
                time.sleep(lib_constants.TEN_SECONDS)
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, tc_id, script_id, "PECI", "None",
                                  log_level, tbd)                               # Write exception message to log file
                return False

            time.sleep(lib_constants.DELAY)                                     # Wait till the log is generated

            if os.path.exists(lib_constants.PECI_LOG):                          # Checking path for the log file generated using tool
                try:
                    shutil.copy(lib_constants.PECI_LOG, lib_constants.SCRIPTDIR)
                    os.rename(lib_constants.SCRIPTDIR + "\\" +"log.csv",
                              lib_constants.SCRIPTDIR+"\\"+log)                 # Rename the log file
                    return lib_constants.SCRIPTDIR + "\\" + log
                except Exception as e:
                    library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due"
                                      " to %s" % e, tc_id, script_id, "PECI",
                                      "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to generate  the log file using PECI tool",
                                  tc_id, script_id, "PECI",  "None", log_level,
                                  tbd)                                          # Write fail message to log file if log is not generated
                return False
        elif ".EXE" in cmd_to_run.upper():
            exe_file_name, key, after_key = cmd_to_run.upper().partition(".EXE")
            exe_file_name = exe_file_name + ".EXE"
            exe_file_in_sut = library.\
                find_file(exe_file_name, "C:\\", tc_id, script_id, log_level,
                          tbd)                                                  # Find the location of file under c drive

            if exe_file_in_sut:                                                 # Find file, message from fn
                os.chdir(exe_file_in_sut)
            else:
                return False
        else:
            pass                                                                # No specific tool need to be used

        if cmd_to_run.lower() == "msinfo32 /report":
            path_file = os.path.join(lib_constants.SCRIPTDIR, log_path)
            command = '"' + cmd_to_run + ' ' + path_file + '"'
        elif "PTTBAT" in cmd_to_run.upper():                                    # For PTTBAT commands
            try:
                ptt_log_path = lib_constants.PTTBATPATH                         # Remove old PTTBAT logs
                cmd_items = cmd_to_run.split(" ")
                index = cmd_items.index('-test')                                # Extract the test name from the command
                test_name = cmd_items[index+1]

                if os.path.isdir(ptt_log_path):                                 # Check if log folder exists
                    for list_item in os.listdir(ptt_log_path):                  # Check for subfolders
                        filepath = os.path.join(ptt_log_path, list_item)        # Clear previous logs
                        if os.path.isdir(filepath):                             # Remove subfolders
                            shutil.rmtree(filepath)
                        elif os.path.isfile(filepath):                          # Remove files
                            os.remove(filepath)
                        else:
                            pass
                    else:
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "PTTBAT log folder is empty", tc_id,
                                          script_id, "None", "None", log_level,
                                          tbd)                                  # Subfolders already removed

                    library.write_log(lib_constants.LOG_INFO, "INFO: Cleared "
                                      "previous PTTBAT logs", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "PTTBAT log folder is missing", tc_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, tc_id, script_id, "None", "None",
                                  log_level, tbd)

            ret = ptt_log_path + '$' + test_name                                # Return value holds the PTT log location and test name
            command = cmd_to_run

            if os.system(command) == 0:                                         # Check if cmd runs without error
                return ret
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Run "
                                  "command failed", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        elif "powercfg /sleepstudy" in cmd_to_run.lower():
            command = cmd_to_run + ' /output ' + \
                os.path.join(lib_constants.SCRIPTDIR, log_path) + '"'           # Framing command with log redirection
        elif "pepbioschecker.exe" in cmd_to_run.lower():
            command = "echo y | " + cmd_to_run + ' > "' + \
                os.path.join(lib_constants.SCRIPTDIR, log_path) + '"'
        elif "fpt.exe" in cmd_to_run.lower():
            command = cmd_to_run + ' -y > "' + \
                os.path.join(lib_constants.SCRIPTDIR, log_path) + '"'
        elif "anc_bios_gen.exe" in cmd_to_run.lower():
            boot_guard_path = utils.ReadConfig("FILE", "boot_guard_path")
            utils.filechangedir(boot_guard_path)
            command = cmd_to_run + ' > "' + \
                os.path.join(lib_constants.SCRIPTDIR, log_path) + '"'
        elif "chipsec" in cmd_to_run.lower():
            if os.path.exists(log_path):
                os.remove(log_path)
            chipsec_path = lib_constants.TOOLPATH + os.sep + "Chipsec"
            os.chdir(chipsec_path)
            ret = \
                subprocess.Popen(cmd_to_run, shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            ret.stdin.write("yes")                                              #typing yes to command prompt
            output = ret.communicate()[0]
            ret.stdin.close()
            os.chdir(lib_constants.SCRIPTDIR)
            logfile = open(log_path, 'a')
            logfile.write(output)
            logfile.close()
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Log file output is %s" % output,
                              tc_id, script_id, "None", "None", log_level, tbd)
        else:
            command = cmd_to_run + ' > "' + \
                os.path.join(lib_constants.SCRIPTDIR, log_path) + '"'           # Framing command with log redirection

        if "chipsec" in cmd_to_run.lower():
            with open(log_path) as logfile:
                for line in logfile.readlines():
                    if "error: service 'chipsec' didn't start" in line.lower():
                        library.write_log(lib_constants.LOG_INFO,
                                          "INFO: service 'chipsec' didn't start",
                                          tc_id, script_id, "None", "None",
                                          log_level, tbd)                       #Checking for errors in running chipsec tool in log
                        return False
        else:
            os.system(command)
            os.chdir(lib_constants.SCRIPTDIR)                                   # Move back to script directory

        if os.path.isfile(log_path):                                            # If file is generated, pass and return file path
            if "shutdown" in cmd_to_run.lower() or \
               "reset" in cmd_to_run.lower():
                with open(log_path, "w") as f_:
                    f_.write("Command Executed Successfully")
            else:
                pass

            if 0 == os.path.getsize(log_path):                                  # If file is 0kb size, fail
                library.write_log(lib_constants.LOG_INFO, "INFO: Log file is "
                                  "generated with 0KB size", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command "
                                  "executed successfully and log file is "
                                  "saved", tc_id, script_id, "None", "None",
                                  log_level, tbd)

                if "pepbioschecker.exe" in cmd_to_run:
                    with open(lib_constants.SCRIPTDIR + "\\" + log_path, "r") \
                            as f:
                        for line in f:
                            if line is not None:
                                if re.match("Report", line):
                                    p = re.compile('written to (.*)')
                                    return p.findall(line)[0]
                return os.path.join(lib_constants.SCRIPTDIR, log_path)          # Return log file pat
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to save "
                              "log file, Log file does not exists", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None","None", log_level, tbd)
        return False

################################################################################
# Function Name : run_command_efi_shell
# Parameters    : cmd_to_run, cwd, tc_id, script_id, log_level and tbd
# Return Value  : True on the run command setup successfully limit, False
#                 otherwise
# Purpose       : To run command in efi shell
################################################################################


def run_command_efi_shell(cmd_to_run, cwd, tc_id, script_id, log_level="ALL",
                          tbd=None):

    try:
        txtfile_path = " "
        flag_fparts = False

        data_ret = nsh_file_gen(cmd_to_run, tc_id, script_id, log_level, tbd)   # Calling library function to generate nsh file

        if False == data_ret:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate required .nsh files", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if create_logical_drive('S', tc_id, script_id, log_level, tbd):         # Library call to create logical drive
            time.sleep(lib_constants.FIVE_SECONDS)                              # Sleep for 5 seconds
            efi_python_path = r"C:\Testing\GenericFramework\tools\PythonEFI\EFI"
            add_path = lib_constants.PYTHON_FEI_FOLDER
            command = "xcopy /I /S /E /Y " + efi_python_path + " " + add_path
            os.system(command)                                                  # Copy the python efi folder to s drive

            tool_name = cmd_to_run.split(".efi")                                # Save the toolname by splitting with .EFI
            if "fpt" in cmd_to_run.lower():
                for file in lib_constants.FPT_EFI:
                    if os.path.exists(lib_constants.TOOLPATH + "\\" + file):
                        shutil.copy(lib_constants.TOOLPATH + "\\" + file,
                                    "S:\\")
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " FPT tool is not available in tool "
                                          "directory", tc_id, script_id,
                                          "None", "None", log_level, tbd)
                        return False

            tool_path = lib_constants.TOOLPATH

            if len(tool_name[0]) != 0:                                          # Search for efi file in tools directory
                files = glob.glob(tool_path + "\\*")
                for f in files:
                    if tool_name[0].lower() in f.lower():
                        if os.path.isdir(f):
                            files1 = glob.glob(f)
                            for g in files1:
                                if tool_name[0].lower() in g.lower():
                                    cmd = "xcopy /S /Y /I /E " + g + " S:\\" \
                                        + tool_name[0]
                                    os.system(cmd)                              # Copy to Shared drive from tools directory
                        else:
                            shutil.copy(f, "S:\\")                              # Copy to shared drive in the other condition
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Tools copied", tc_id, script_id,
                                              "None", "None", log_level, tbd)
                    else:
                        pass

            if "closemnf" in cmd_to_run.lower():
                tool_name = cmd_to_run.split(".efi")                            # Save the toolname by splitting with .EFI
                tool_path = lib_constants.TOOLPATH

                if len(tool_name[0]) != 0:                                      # Search for efi file in tools directory
                    tool_dir = glob.glob(tool_path + "\\*")
                    for dir in tool_dir:
                        if tool_name[0].lower() in dir.lower():
                            dir_tool = os.listdir(dir)
                            for txt_file in dir_tool:
                                txtfile_path = os.path.join(dir, txt_file)
                                file_name = os.path.basename(txtfile_path)
                                if "fparts.txt" == file_name.lower().strip():
                                    cmd = "xcopy /S /Y /I /E " + txtfile_path \
                                        + " S:\\"
                                    os.system(cmd)                              # Copy to Shared drive from tools directory
                                    time.sleep(lib_constants.FIVE_SECONDS)      # Sleep for 5 seconds
                                    flag_fparts = True
                                    break

                                library.write_log(lib_constants.LOG_WARNING,
                                                  "WARNING: fpaprt file is "
                                                  "missing in fpt directory",
                                                  tc_id, script_id, "None",
                                                  "None", log_level, tbd)
                                return False

            if os.path.exists('S:\\'):                                          # Check for new logical drive
                time.sleep(lib_constants.FIVE_SECONDS)                          # Sleep for 5 seconds
                cmd = "xcopy /S /Y /I /E " + "startup.nsh" + " S:\\"
                os.system(cmd)                                                  # Copy to Shared drive from tools directory

                if os.path.exists(cwd + "\subscript.nsh"):
                    sub_script = cwd + "\subscript.nsh"
                    cmd = "xcopy /S /Y /I /E " + sub_script + " S:\\"
                    os.system(cmd)                                              # Copy to Shared drive from tools directory

                library.write_log(lib_constants.LOG_INFO, "INFO: The Logical "
                                  "drive created", tc_id, script_id, "None",
                                  "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed"
                                  "to create logical drive", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            if library.set_multiple_bootorder(tc_id, script_id, log_level,
                                              tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: Internal EDK "
                                  "Shell is set as the first boot device",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to set Internal EDK Shell as the first "
                                  "boot device", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "create logical drive", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None","None", log_level, tbd)
        return False

################################################################################
# Function Name : disable_driver()
# Description   : disable the drivers to run chipsec command and verify it
# Parameters    : tc_id, script_id, log_level and tbd
# Returns       : True on successful command execution and log verification,
#                 False otherwise
# Purpose       : To disbale drivers using KBD simulator
################################################################################

def disable_driver(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        import lib_ttk2_operations
        lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)  # Kill old TTK2 services
        ttk_device = lib_ttk2_operations.gpio_initialize(test_case_id,
                                                         script_id,
                                                         log_level, tbd)        # Initialize TTk2

        result = lib_remote_reboot.monitor_service_up(test_case_id, script_id,
                                                      log_level="ALL", tbd=None)

        if result:
            thread1 = ThreadWithReturnValue(target=verify_driver_disablement,
                                            args=(test_case_id, script_id,
                                                  log_level, tbd))              # Thread for verifying the driver disablement steps
            thread2 = ThreadWithReturnValue(target=perform_driver_disablement,
                                            args=(test_case_id, script_id,
                                                  log_level,tbd))               # Thread to perform driver disablement

            thread1.start()
            thread2.start()

            if thread1.join() and thread2.join():
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                                  "disabled the drivers and verified it",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Unsuccessful"
                                  " in disabling the drivers", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: System is not in "
                              "OS", test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None",
                          log_level,
                          tbd)
        return False

################################################################################
# Function Name : perform_driver_disablement()
# Description   : disable the drivers to run chipsec command
# Parameters    : tc_id, script_id, log_level and tbd
# Returns       : True on successful command execution and log verification,
#                 False otherwise
# Purpose       : To disbale drivers using KBD simulator
################################################################################

def perform_driver_disablement(test_case_id, script_id, log_level="ALL",
                               tbd=None):
    try:

        input_device_name = \
            utils.ReadConfig("KBD_MOUSE", "KEYBOARD_MOUSE_DEVICE_NAME")         # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE", "PORT")                            # Extract com port details from config.ini

        if "FAIL:" in [input_device_name, port]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get required config entries from Config.ini",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: COM Port and "
                              "input device name identified as %s and %s from "
                              "Config.ini" % (port, input_device_name),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        library.write_log(lib_constants.LOG_INFO, "INFO: System is in OS, "
                          "Start peforming steps to disable driver",
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)

        k1 = kbm.USBKbMouseEmulation(input_device_name, port)                   #Performing Steps to disable drivers
        k1.key_press("KEY_GUI d")
        k1.key_press("KEY_GUI x")
        time.sleep(1)
        k1.key_press("KEY_MENU u")
        time.sleep(1)
        k1.key_press("KEY_SHIFT r")
        time.sleep(10)
        k1.key_press("KEY_DOWN")
        time.sleep(1)
        k1.key_press("KEY_DOWN")
        time.sleep(1)
        k1.key_press("KEY_ENTER")
        time.sleep(5)
        k1.key_press("KEY_DOWN")
        time.sleep(1)
        k1.key_press("KEY_ENTER")
        time.sleep(5)
        k1.key_press("KEY_DOWN")
        time.sleep(1)
        k1.key_press("KEY_ENTER")
        time.sleep(5)
        k1.key_press("KEY_ENTER")
        time.sleep(30)
        k1.key_press("F7")
        time.sleep(30)
        result = lib_remote_reboot.monitor_service_up(test_case_id,
                                    script_id, log_level="ALL", tbd=None)       #Verifying the system has booted to OS
        if result:
            return True
        else:
            return False

    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s"
                          %e_obj, test_case_id, script_id, "None","None",
                          log_level, tbd)
        return False

################################################################################
# Function Name : verify_driver_disablement()
# Description   : verifying the driver disablement by checking postcode
# Parameters    : tc_id, script_id, log_level and tbd
# Returns       : True on getting multiple postcodes False otherwise
# Purpose       : To verify driver disablement using postcode change
################################################################################

def verify_driver_disablement(test_case_id, script_id, log_level="ALL",
                              tbd=None):

    end_time = time.time() + 300
    postcode_lst = list()

    while time.time() < end_time:
        time.sleep(.5)
        curr_postcode = lib_ttk2_operations.read_post_code(test_case_id,
                                               script_id, log_level="ALL",
                                               tbd=None)
        postcode_lst.append(curr_postcode)                                      # Monitoring postcode while restarting the system
        postcode_set = set(postcode_lst)
        if (len(postcode_set) >= 3) and \
                (postcode_lst[-1] in lib_constants.OS_POSTCODE):
            library.write_log(lib_constants.LOG_INFO, "INFO: Postcode observed"
                              " %s" % postcode_set, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        continue
    else:
        return False