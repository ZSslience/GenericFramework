__author__ = "Automation Development Team"

# General Python Imports
import os
import shutil
import subprocess
import time
import winreg as winreg

# Local Python Imports
import lib_constants
import library
import utils

################################################################################
# Description  : This function checks if the driver/tool has already been
#                installed in the system or not
# Parameter    : Path of the installed tool/driver
# Return       : 1/0
################################################################################


def Installed(path, log_level="ALL", tbd=None):

    if os.path.exists(path):
        return 1
    else:
        return 0

################################################################################
#   For checking the installation and logging
################################################################################


def check_installation(path, tool, already=True, log_level="ALL", tbd=None):

    if Installed(path, log_level, tbd):
        return True
    elif not already:
        return False
    else:
        pass

################################################################################
#    Function checking and installing tools
#    path(string) : installed path of tool including exe name
#    tool_name(string) : name of the tool
#    setup path(string) : Tool folder name in TOOLPATH, except TOOLPATH
#    setup_commad(list) : a list with setup exe name and silent command
################################################################################
def install_tool(path, tool_name, setup_path, setup_command,log_level= "ALL",
                 tbd = None):
    try:
        if check_installation(path, tool_name):
            return True

        os.chdir(setup_path)
        installation_proc = subprocess.Popen(setup_command,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             stdin=subprocess.PIPE)
        installation_proc.communicate()
        if check_installation(path, tool_name, False):
            syscope_license_path = lib_constants.SYSCOPE_LICENSE
            subprocess.Popen(syscope_license_path, tdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             stdin=subprocess.PIPE)                              #run the auto it file to accept the
            time.sleep(3*(lib_constants.SLEEP_TIME))                            #sleep for 15 seconds
            library.write_log(lib_constants.LOG_INFO, "INFO: Tool"
            " Installed Successfully" ,"None", "None", log_level, tbd)
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception "
            "occurs in install_tool() function in the"
            " lib_tool_installation.py file"%e, "None","None", log_level, tbd)
        return False


################################################################################
# Function    : install_Syscope(self)
# Description : It installs the system scope Tool
################################################################################


def install_Syscope(tc_id, script_id, log_level="ALL", tbd=None):

    path = lib_constants.SYSCOPE_PATH

    if check_installation(path, "Systemscope"):
        library.write_log(lib_constants.LOG_INFO, "INFO: System Scope Tool "
                          "is already installed", tc_id, script_id, "None",
                          "None", log_level, tbd)

        copy_license_syscope(tc_id, script_id, log_level, tbd)
        return True
    else:
        tool_name = lib_constants.SYSCOPE_TOOL_NAME
        setup_path = lib_constants.SYSCOPE_SETUP_PATH
        setup = lib_constants.SYSCOPE_SETUP

        setup_command = [setup, "-s"]
        if install_tool(path, tool_name, setup_path, setup_command):
            copy_license_syscope("None", "None", log_level, tbd)
            return True
        else:
            return False
################################################################################
# Function      : execute_syscope
# Description   : Method for executing systemscope commands
# command(list) : systemscope command and options
# filename      : filename of the xml log
################################################################################


def execute_syscope(tc_id="None", script_id="None", log_level="None",
                    tbd="None"):

    Tooldir = lib_constants.SYSCOPE_TOOLDIR
    sys_exe = lib_constants.SYSCOPE_EXE

    if install_Syscope(tc_id, script_id, log_level, tbd):

        if os.path.exists(Tooldir + os.sep + 'syscope.xml'):
            os.remove(Tooldir + os.sep + 'syscope.xml')
        else:
            pass

        command_run = sys_exe + ' -log "' + Tooldir + '\\syscope.xml"'
        os.chdir(Tooldir)
        handle = subprocess.Popen(command_run, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        handle.communicate()

        while not os.path.exists(Tooldir + os.sep + 'syscope.xml'):
            pass
        time.sleep(5)

        if "log" in command_run:
            time.sleep(10)
        else:
            pass

        os.chdir(Tooldir)
        if os.path.exists(Tooldir + '\\syscope.xml'):
            return True
        else:
            return False
    else:
        return False

################################################################################
################################################################################
# Function Name : install_peci
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on Success, False on Failure
# Functionality : To install PECI Tool
################################################################################

def install_peci(test_case_id,script_id,log_level,tbd):

    peci_setup = utils.ReadConfig("PECI_TOOL", "Install_Cmd")                   #Getting the peci installation exe name from config
    os.chdir(utils.ReadConfig("PECI_TOOL", "ToolDir"))
    try:
        command = peci_setup + " -s"                                            #command for installing peci tool
        if not os.system(command):                                              #executing command to install peci tool
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
            test_case_id, script_id, "None", "None", log_level, tbd)            #Write the error message to log
        return False

################################################################################
# Function Name : peci_install_check
# Parameters    : test_case_id, script_id, ori_token, log_level, tbd
# Return Value  : True on Success, False on Failure
# Functionality : To check PECI is installed or not
################################################################################

def peci_install_check(test_case_id, script_id, log_level, tbd):

    try:
        peci_path = utils.ReadConfig("PECI_TOOL", "InstalledPath")              #Getting the peci tool path from config
        registry_path = utils.ReadConfig('PECI_TOOL','reg_path')                #Getting the registry path from config

        if os.path.exists(peci_path):                                           #checking whether PECI tool is already installed or not
            return True
        else:
            if install_peci(test_case_id, script_id, log_level, tbd):           #Checking whether PECI tool is properly installed or not
                library.write_log(lib_constants.LOG_INFO, "INFO:PECI Tool "
                "Installed Successfully ", test_case_id, script_id, "PECI",
                                  "None", log_level, tbd)                       #Write the info message to log

                try:
                    key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                                           registry_path , 0,
                                           winreg.KEY_ALL_ACCESS)
                    winreg.SetValueEx(key, 'License', '', winreg.REG_DWORD,0x1) #Disabling the licence agreement for PECI Tool
                    return True
                except Exception:
                    try:
                        key = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,
                                registry_path, 0,winreg.KEY_ALL_ACCESS)
                        winreg.SetValueEx(key, 'License', '', winreg.REG_DWORD,
                                          0x1)
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s "
                                          %e, test_case_id, script_id, "None",
                                          "None", log_level, tbd)               #Write the error message to log
                        return False
            else:
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
                          test_case_id, script_id, log_level, tbd)

################################################################################
################################################################################
#   Function      : execute_syscope_New
#   Description   : Method for executing systemscope commands
#   command(list) : systemscope command and options
#   filename      : filename of the xml log
################################################################################


def execute_syscope_New(tc_id="None",script_id="None",log_level="None",
                        tbd="None"):

    sys_exe = lib_constants.SYSCOPE_EXE
    Tooldir = lib_constants.SYSCOPE_TOOLDIR

    if os.path.exists(Tooldir + os.sep + 'syscope.xml'):
        os.remove(Tooldir + os.sep + 'syscope.xml')
    else:
        pass

    log_path = Tooldir + os.sep + 'syscope.xml'
    if install_Syscope(tc_id, script_id, log_level, tbd):
        command_run = sys_exe + ' -log "' + log_path + '" -acpi'
        os.chdir(Tooldir)
        result = utils.execute_with_command(command_run, tc_id, script_id, "None",
                                           log_path, tbd)
        result = bool(result)
        if not result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to execute "
                                                      "the command %s "
                              % command_run, tc_id, script_id, "None",
                              log_level, tbd)
        while not os.path.exists(Tooldir + os.sep + 'syscope.xml'):
           pass
        time.sleep(5)
        if "log" in command_run:
            print("Waiting 10 seconds for generating syscope log...")
            time.sleep(10)
        else:
            pass
        os.chdir(Tooldir)
        if os.path.exists(Tooldir + os.sep + 'syscope.xml'):
            return True
        else:
            return False

################################################################################
# Function Name : install_selftest
# Parameters : exe_set_up path
# Functionality: checks if application is installed or not
# Return Value : True if installed or return False
################################################################################
def install_selftest(exe_name,test_case_id, script_id,log_level):
    tool_path = utils.ReadConfig("SELFTEST", "Tooldir")                         #tool path after installation
    exe_name = utils.ReadConfig("SELFTEST", "Exe_name")                         #tool exe name for execution
    setup_path = utils.ReadConfig("SELFTEST", "setup_path")                     #set-up path for installing the tool
    setup = utils.ReadConfig("SELFTEST", "setup")
    utils.filechangedir(setup_path)
    set_cmd=setup + " /q"

    if os.path.exists(tool_path):                                               #checking for exe dircetory path

        if os.path.exists(exe_name):                                            #checking for EXE file
            library.write_log(lib_constants.LOG_INFO,
            "INFO: %s tool installed successfully"%setup,
            test_case_id, script_id, "SELFTEST", "None",log_level,
            tbd=None)
            return True
    else:
        os.system(set_cmd)
        time.sleep(lib_constants.TEN_SECONDS)
        if os.path.exists(tool_path):                                           #checking for exe dircetory path
            if os.path.exists(exe_name):                                        #checking for EXE file
                library.write_log(lib_constants.LOG_INFO,
                "INFO: %s tool installed successfully"%setup,
                test_case_id, script_id, "SELFTEST", "None",log_level,
                tbd=None)
                return True
        else:
            library.write_log(lib_constants.LOG_FAIL,
            "FAIL: %s tool installation got failed"%setup,
            test_case_id, script_id, "SELFTEST", "None",log_level,
            tbd=None)
            return False


def copy_license_syscope(test_case_id, script_id, log_level="ALL", tbd="None"):

    try:
        telemetry = lib_constants.SYSCOPE_TELEMETRY
        license = lib_constants.SYSCOPE_LICENSEAGREEMENT
        binaries_tele = lib_constants.SYSCOPE_BINARIES_TELE
        binaries_lice = lib_constants.SYSCOPE_BINARIES_LICE

        shutil.copyfile(telemetry, binaries_tele)
        shutil.copyfile(license, binaries_lice)

        library.write_log(lib_constants.LOG_INFO, "INFO: copied license "
                          "supported files successfully", test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
