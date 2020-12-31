__author__ = r"surajx/sushilx/tnaidux"

# Global Python Imports
import getopt
import os
import re
import shutil
import sys
import time
from xml.etree import ElementTree

# Local Python Imports
import library
import lib_constants
import lib_read_bios
import lib_run_command
import utils
import lib_xmlcli
sys.path.append(r"C:\Testing\GenericFramework\tools\pysvtools.xmlcli")
import pysvtools.xmlcli.XmlCli as cli

# Global Variables
checklist_offline = {}
bios_path = None

################################################################################
# Function Name   : xml_cli_set_bios
# Parameters      : ost, string_in_bios, tc_id, script_id, log_level, tbd
# Functionality   : to set the bios
# Return Value    : True if bios set successfully else false
################################################################################


def xml_cli_set_bios(ost, string_in_bios, tc_id, script_id, log_level="ALL",
                     tbd=None):

    try:
        bios_path = (str(string_in_bios.split("=")[0])).strip()
        params_value = (str(string_in_bios.split("=")[1])).strip()
        step = ost.strip()

        if "virtual sensor participant 1" in bios_path.lower() and \
           "active thermal trip point" in bios_path.lower():
            bios_path = \
                bios_path.lower().replace("virtual sensor participant 1/", "")

        if "virtual sensor participant 2" in bios_path.lower() and \
           "active thermal trip point" in bios_path.lower():
            bios_path = \
                bios_path.lower().replace("virtual sensor participant 2/", "")

        result = lib_xmlcli.set_bios_xml_cli(bios_path, params_value, step,
                                             tc_id, script_id, log_level, tbd)

        if result is True:
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name       : xmlcli_set_bios_security_option
# Description         : set the bios options from efi shell
# Parameters          : input, step_name, tc_id, script_id, log_level, tbd
# Returns             : True on successful action, False otherwise
# Dependent Function  : lib_run_command()
################################################################################


def xmlcli_set_bios_security_option(input, step_name, tool, tc_id, script_id,
                                    log_level='ALL', tbd=None):

    try:
        set_option_efi = ''
        read_option_efi = ''
        option_in_bios = ''
        set_option = ''
        read_option = ''

        efi_python = r"C:\Testing\GenericFramework\tools\PythonEFI"
        cur_script_dir = lib_constants.SCRIPTDIR
        nsh_file_path = lib_constants.SCRIPTDIR + os.sep + "startup.nsh"
        sdrive_path = lib_constants.SDRIVE_PATH
        efi_python_path = efi_python + os.sep + "EFI"
        xmlcli_logpath = lib_constants.EFI_LOGPATH

        python_script_efi = \
            lib_constants.SCRIPTDIR + os.sep + "enable_disable_option.py"

        if os.path.exists(efi_python):
            library.write_log(lib_constants.LOG_INFO, "INFO: Python EFI tool "
                              "exists", tc_id, script_id, "None", "None",
                              log_level, tbd)
            pass
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Python EFI "
                              "tool does not exists", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        step_name_split = step_name.split('=')[0]
        step_last_str = step_name_split.split('/')[-1].lower().strip()
        step_first_str = step_name.split(" ")[0].upper().strip()
        bios_option = input.upper().strip()
        
        if step_last_str in lib_constants.EFI_OPTION_LIST:
            try:
                if "vnn" in step_name_split.split("/")[5].strip().lower():
                    if step_last_str == "s0i2":
                        step_last_str = "vnns0i2"
                    elif step_last_str == "enable rail in s0i3":
                        step_last_str = "vnns0i3"
                    elif step_last_str == "enable rail in s3":
                        step_last_str = "vnns3"
                    elif step_last_str == "enable rail in s4":
                        step_last_str = "vnns4"
                    elif step_last_str == "enable rail in s5":
                        step_last_str = "vnns5"
                elif "v1p05" in step_name_split.split("/")[5].strip().lower():
                    if step_last_str == "s0i2":
                        step_last_str = "v1p05s0i2"
                    elif step_last_str == "enable rail in s0i3":
                        step_last_str = "v1p05s0i3"
                    elif step_last_str == "enable rail in s3":
                        step_last_str = "v1p05s3"
                    elif step_last_str == "enable rail in s4":
                        step_last_str = "v1p05s4"
                    elif step_last_str == "enable rail in s5":
                        step_last_str = "v1p05s5"
            except Exception as e:
                pass
            
            if "SET" == step_first_str:
                generate_str = 'set_option_efi = "%s"\n'\
                               'option_in_bios = "%s"\n'\
                               'read_option_efi = ""\n' %\
                               (bios_option, step_last_str)

            elif "READ" == step_first_str:
                generate_str = 'set_option_efi = ""\n' \
                               'option_in_bios = "%s"\n' \
                               'read_option_efi = "%s"\n' \
                               % (step_last_str, bios_option)

            else:
                generate_str = False
        else:
            generate_str = False

        if not generate_str:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: BIOS Path "
                              "parameter is not handled", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if os.path.exists(nsh_file_path):
            os.remove(nsh_file_path)

        os.chdir(cur_script_dir)
        create_logical_drive = lib_run_command.\
            create_logical_drive("S", tc_id, script_id, log_level, tbd)
        time.sleep(10)
        os.chdir(cur_script_dir)
        nsh_file_generation = nsh_file_gen(tc_id, script_id, log_level, tbd)

        if create_logical_drive is True and nsh_file_generation is True:
            library.write_log(lib_constants.LOG_INFO, "INFO: Logical Drive "
                              "is created and nsh file created", tc_id,
                              script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "create logical drive or Failed to create nsh "
                              "file", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        with open("enable_disable_option.py", "w") as filedes_wr:
            filedes_wr.write(generate_str)
            filedes_wr.write('\n')
            filedes_wr.write(lib_xmlcli.PYTHON_SCRIPT)
            filedes_wr.write('\n')
            filedes_wr.close()
        time.sleep(10)

        if os.path.exists(sdrive_path) and \
           os.path.exists(nsh_file_path) and \
           os.path.exists(efi_python_path) and \
           os.path.exists(python_script_efi):
            time.sleep(lib_constants.FIVE_SECONDS)
            shutil.copy2(nsh_file_path, "S:\\\\")
            add_path = lib_constants.PYTHON_FEI_FOLDER
            command = "xcopy /I /S /E /Y " + efi_python_path + " " + add_path

            os.system(command)
            time.sleep(10)
            shutil.copy2(python_script_efi, "S:\\\\")

            library.write_log(lib_constants.LOG_INFO, "INFO: 1.startup.nsh "
                              "file copied to S drive, 2.EFI files copied to "
                              "S drive, 3.python script copied to S drive",
                              tc_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "perform following operation 1.startup.nsh file "
                              "copied to S drive, 2.EFI files copied to S "
                              "drive, 3.python script copied to S drive",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False

        if library.set_multiple_bootorder(tc_id, script_id, log_level, tbd):    # Set the internal edk shell as first boot order
            library.write_log(lib_constants.LOG_INFO, "INFO: Internal EDK "
                              "Shell set as the first boot device", tc_id,
                              script_id, "None", "None", log_level, tbd)

            if os.path.exists(xmlcli_logpath):
                os.unlink(xmlcli_logpath)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "set Internal EDK Shell as the first boot "
                              "device", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name       : xmlcli_cleanup
# Description         : To remove the nsh & py files from s drive after nsh
#                       file running in EDK Shell
# Parameters          : tc_id, script_id, log_level and tbd None
# Returns             : True on successful action, False otherwise
################################################################################


def xmlcli_cleanup(tc_id, script_id, log_level='ALL', tbd=None):

    try:
        time.sleep(lib_constants.SLEEP_TIME)
        flag_clean_nsh = 0
        flag_clean_py = 0

        if os.path.exists('S:'):                                                # Check for Logica drive
            os.chdir('S:\\')                                                    # Navigate to s:
            for filename in os.listdir("."):                                    # Check for filename in directory for nsh
                if filename.endswith("nsh"):                                    # If any nsh file is there unlink the file
                    flag_clean_nsh += 1
                    os.unlink(filename)

                if filename.endswith("py"):                                     # If any py file is there unlink the file
                    flag_clean_py += 1
                    os.unlink(filename)

            os.chdir(lib_constants.SCRIPTDIR)

            if 0 == flag_clean_nsh and 0 == flag_clean_py:
                library.write_log(lib_constants.LOG_INFO, "INFO: No nsh and "
                                  "py files are available in the directory",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: nsh and "
                                  "py files successfully removed", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Logical "
                              "drive does not exists for use", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : nsh_file_gen
# Parameters    : tc_id, script_id, log_level, tbd
# Return Value  : True on success, False on failure
# Functionality : To create startup.nsh file
################################################################################


def nsh_file_gen(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        f = open("startup.nsh", 'w')                                            # File operation
        f.write("bcfg boot mv 01 00" + '\n')
        f.write('fs0:' + '\n')
        f.write("Python.efi fs0:\enable_disable_option.py")
        f.write('\n')
        f.write("reset")
        f.close()                                                               # File closing after writing to file

        nsh1_size = os.path.getsize("startup.nsh")
        if 0 == int(nsh1_size):                                                 # Check for startup nsh file sizes and return false if size is 0
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate .nsh file properly", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: .nsh file is "
                              "generated successfully", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name       : xmlci_efi_logparsing
# Description         : xml efi log parsing for to verify the pass message for
#                       the bios option which set in EDK Shell
# Parameters          : tc_id, script_id, log_level, tbd
# Returns             : True on successful action, False otherwise
################################################################################


def xmlci_efi_logparsing(tc_id, script_id, log_level='ALL', tbd=None):

    try:
        time.sleep(lib_constants.FIVE_SECONDS)
        flag_xml_cli_mesg = False
        xml_cli_log_mesg = lib_constants.XML_CLI_LOG_MESG
        xml_cli_log_mesg_pwd_err = lib_constants.XML_CLI_LOG_MESG_PWD_ERR
        xml_cli_log_mesg_pwd_set = lib_constants.XML_CLI_LOG_MESG_PWD_SET
        xmlcli_logpath = lib_constants.EFI_LOGPATH

        if os.path.exists('S:'):                                                # Check for path exists or not
            os.chdir('S:\\')                                                    # Navigate to s:
            if os.path.exists(xmlcli_logpath):
                with open (xmlcli_logpath,'r') as file_read_des:
                    for line in file_read_des:
                        if xml_cli_log_mesg == line.strip():
                            flag_xml_cli_mesg = True
                            break
                        elif xml_cli_log_mesg_pwd_err == line.strip():
                            flag_xml_cli_mesg = False
                            break
                        elif xml_cli_log_mesg_pwd_set == line.strip():
                            flag_xml_cli_mesg = True
                            break
                        else:
                            flag_xml_cli_mesg = False

                if True == flag_xml_cli_mesg:
                    os.unlink(xmlcli_logpath)
                    return True
                else:
                    os.unlink(xmlcli_logpath)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                  "XmlCli.log file does not exists", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : set_bios
# Parameters    : ostr, tool_name, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To set required bios path
################################################################################


def set_bios(ost, tool_name, tc_id, script_id, log_level="ALL", tbd=None):

    try:
        if "XMLCLI" == tool_name.upper():
            string_inbios = ost.lower().replace("set bios ", "")
            return xml_cli_set_bios(ost, string_inbios, tc_id, script_id,
                                    log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Set Bios "
                              "using %s tool is not implemented" % tool_name,
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hb:t:",)
    except getopt.GetoptError:
        print("Please use -h command for Help Message")
        print("Usage: lib_set_bios.py -h")
        return False

    try:
        if 0 == len(opts):
            print("Please use -h command for Help Message")
            print("Usage: lib_set_bios.py -h")
            return False
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print("##################################################\n")
                    print("Description:\n\tThis API aims at to set bios " \
                          "value for the required knob using Tools like " \
                          "XmlCli etc. This API internally performs set bios " \
                          "and verifies the value is set properly or not.\n")

                    print("Arguments:\n-h\n\t For printing the help message")

                    print("-b\n\t bios path e.g Set Bios /Bios/Intel advanced" \
                          " menu/ACPI settings/Low Power S0 Idle Capability =" \
                          " Disabled")

                    print("-t\n\t Tool name using which needs to set BIOS " \
                          "e.g XmlCli")

                    print("Usage:\n\tlib_set_bios.py -b '<bios_path>' " \
                          "-t <Tool Name> \n")
                    print("####################################################")
                    return True
                elif opt in "-b":
                    global bios_path
                    bios_path = arg
                elif opt in "-t":
                    tool_name = arg
                else:
                    return False
            set_bios(bios_path, tool_name, "Set_Bios", "Set_Bios",
                     log_level="ALL", tbd=None)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
