__author__ = 'patnaikx'

############################General Python Imports##############################
import subprocess
import csv
import re
import os
import time
import shutil
############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_tool_installation
################################################################################
# Function Name : execute_compliance_verification_tool
# Parameters    : TC_id-test case ID, script_id  - script ID,
#                 tool - tool name, value - parameter to be verify
# Functionality : verify system parameter using compliance verification tool
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : RUN <SELFTEST/PETS/BVT tool> <VALUE>
################################################################################


def execute_compliance_verification_tool(value, tool,test_case_id, script_id,
                                         log_level="ALL", tbd=None):

    try:
        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        log_path = lib_constants.SCRIPTDIR + "\\" + log_file
        excel_log = new_script_id + ".csv"
        excel_log_path = lib_constants.SCRIPTDIR + "\\" + excel_log
        tool_path = utils.ReadConfig(tool, "Tooldir")                           #tool path after installation
        exe_name = utils.ReadConfig(tool, "Exe_name")                           #tool exe name for execution
        setup_path = utils.ReadConfig(tool, "setup_path")                       #set-up path for installing the tool
        setup = utils.ReadConfig(tool, "setup")                                 #set-up exe for installing

        flag = False                                                            #flag value set to false
        regx = " "                                                              #content to be checked in compliance tool

        if "FAIL:" in [tool_path, exe_name, setup_path,setup]:
            library.write_log(lib_constants.LOG_WARNING,
            "WARNING: Config entry for tool is missing",
            test_case_id, script_id, "%s"%tool, "None",log_level, tbd=None)     #fail if config entry is missing
            return False

        else:
            library.write_log(lib_constants.LOG_INFO,
            "INFO: Config entry for tool found",
            test_case_id, script_id, "%s"%tool, "None", log_level, tbd=None)   #pass if config entry is correct

        if os.path.exists(tool_path):                                           #checking for exe dircetory path
            library.write_log(lib_constants.LOG_INFO,
            "INFO: %s tool is already installed"%setup,
            test_case_id, script_id, "%s"%tool, "None",log_level, tbd=None)
        else:
            try:                                                                #installing tool if it is not installed before
                if lib_tool_installation.install_selftest(exe_name,
                            test_case_id,script_id,log_level):                  #checking for EXE file
                    library.write_log(lib_constants.LOG_INFO,
                    "INFO: %s tool installed successfully"%setup,
                    test_case_id, script_id, "%s"%tool, "None",log_level,
                    tbd=None)
                else:
                    library.write_log(lib_constants.LOG_FAIL,
                    "FAIL: %s tool installation got failed"%setup,
                    test_case_id, script_id, "%s"%tool, "None",log_level,
                    tbd=None)
                    return False
            except Exception as e:                                              #error handling for file exist or not
                    library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception"
                    " in installing the compliance tool due to %s"%e,
                    test_case_id, script_id, "%s"%tool, "None",log_level, tbd)
                    return False

        if "SELFTEST" in tool:
            try:

                cmd_for_run_windc = "windc -o dump.stx"
                new_tool_path = tool_path + "\\" + "datacollector"              #path for the windc.exe
                utils.filechangedir(new_tool_path)

                os.system(cmd_for_run_windc)

                time.sleep(lib_constants.FIVE_SECONDS)
                file = new_tool_path + "\\" + "dump.stx"                        #path for dump file
                if utils.check_file(file):
                    try:
                        shutil.copy(file, tool_path)                            #copy dump file to tool_path
                        time.sleep(lib_constants.FIVE_SECONDS)
                        if os.path.exists(tool_path + "\\" + "dump.stx"):       #if dump file prsent or not inside the tool_path
                            library.write_log(lib_constants.LOG_INFO,
                            "INFO: File copied to %s tool_path "
                            "successfully"%tool_path, test_case_id,
                            script_id, "SELFTEST", "None",log_level, tbd=None)
                        else:
                            library.write_log(lib_constants.LOG_FAIL,
                            "FAIL: Failed to copy the file to %s tool_path"
                            %tool_path,test_case_id,script_id, "SELFTEST",
                            "None",log_level, tbd=None)
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR: "
                        "Exception in running the command for copy due to %s"%e,
                        test_case_id,script_id, "None", "None", log_level,tbd)

                else:                                                           #if unable to create the dump file in stx extension
                    library.write_log(lib_constants.LOG_FAIL,
                    "FAIL: Failed to run the command for creating dump file",
                    test_case_id,script_id, "SELFTEST", "None",log_level,
                    tbd=None)
                dump_file_stx = "dump.stx"
                dump_file_excel = excel_log
                utils.filechangedir(tool_path)
                time.sleep(lib_constants.FIVE_SECONDS)
                cmd_for_create_excel_file = "AnalyzerCmd.exe %s %s" % (
                                            dump_file_stx,dump_file_excel)      #command for converting dump file to excel sheet
                subprocess.Popen(cmd_for_create_excel_file, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                if utils.check_file(dump_file_excel):
                    try:
                        shutil.copy(dump_file_excel, lib_constants.SCRIPTDIR)   #copy excel sheet to script directory
                        time.sleep(lib_constants.FIVE_SECONDS)
                        if utils.check_file(excel_log_path):                    #checking for excel sheet inside script directory
                            library.write_log(lib_constants.LOG_INFO,
                            "INFO: File copied successfully to script "
                            "Directory", test_case_id,
                            script_id, "SELFTEST", "None",log_level, tbd=None)
                        else:
                            library.write_log(lib_constants.LOG_FAIL,
                            "FAIL: failed to copy the file to Script "
                            "directory", test_case_id,
                            script_id, "SELFTEST", "None",log_level, tbd=None)
                    except Exception as e:                                      #error handling for excel sheet copy
                        library.write_log(lib_constants.LOG_ERROR, "ERROR: "
                        "Exception in copying file due to %s"%e,
                        test_case_id,script_id, "SELFTEST", "None",
                        log_level, tbd)

                else:
                   library.write_log(lib_constants.LOG_FAIL,
                   "FAIL: Failed to run the command", test_case_id,
                   script_id, "SELFTEST", "None",log_level, tbd=None)
                os.chdir(lib_constants.SCRIPTDIR)
                f = open(log_path, 'w')
                f.close()
                if value.upper() in lib_constants.SELFTEST_VALUE:

                    with open(dump_file_excel, 'rt') as f:                      #read the excel sheet
                        reader = csv.reader(f, delimiter = ',')
                        for row in reader:
                            for field in row:
                                if re.match("(.*)%s(.*)"%value, field, re.IGNORECASE):
                                    library.write_log(lib_constants.LOG_INFO,
                                    "INFO: Value for %s fetched as %s"%(value,row[3]),
                                      test_case_id, script_id, "SELFTEST",
                                    "None",log_level, tbd=None)
                                    return row[4]
                                    break
                                else:
                                    pass
                    f.close()
                    library.write_log(lib_constants.LOG_FAIL,
                        "FAIL: Failed to fetch valiue for %s"%value,
                        test_case_id, script_id, "SELFTEST", "None",log_level, tbd=None)
                    return False
                else:
                    with open(dump_file_excel, 'rt') as f:                      #read the excel sheet
                        reader = csv.reader(f)
                        for row in reader:
                            if row != None:
                                f = open(log_path, 'ab')
                                if value.upper() in str(row).upper():
                                    f.write(str(row).split("', '")[3]+"\n")     #if  parameter has error
                                f.close()
                    f.close()
                    if utils.check_file(log_path):
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Log file for %s generated"%value,
                          test_case_id, script_id, "SELFTEST", "None",log_level, tbd=None)
                        return log_path
                    else:
                        library.write_log(lib_constants.LOG_FAIL,
                        "FAIL: Failed to get the log for %s"%value,
                        test_case_id, script_id, "SELFTEST", "None",log_level, tbd=None)
                        return False
            except Exception as e:                                              #error handling for running the command
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception"
                " in running the command due to %s"%e,test_case_id,
                script_id, "SELFTEST", "None", log_level, tbd)

        else:
            library.write_log(lib_constants.LOG_INFO,
              "INFO: Wrong input for tool name for verification"%tool,
              test_case_id, script_id, "None", "None",log_level, tbd=None)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "running the compliance tooldue to %s"%e,test_case_id, script_id,
        "None","None",log_level, tbd)
        return False
