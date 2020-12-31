__author__ = "skotasiv"

############################General library imports#############################
import sys
import os
import time
import glob
import shutil
################################################################################
############################Local library imports###############################
import library
import utils
import lib_set_bios
import lib_constants
import lib_run_command
import  lib_parse_log_file
################################################################################
################################################################################
# Function name       : copy_vtinfo_tool
# Description         : To create the .nsh file and copy the vtinfo tool
#                       and .nsh file to S:\
# Parameters          : cmd,tc_id,script_id,log_level='ALL',tbd= None
# Returns             : return true on success and false otherwise
# Dependent Functions : lib_run_command.nsh_file_gen()
#                       lib_run_command.create_logical_drive()
#                       library.set_Multiple_bootorder()
################################################################################

def copy_vtinfo_tool(cmd,tc_id,script_id,log_level='ALL',tbd= None):

    try:
        cwd = lib_constants.SCRIPTDIR
        data_ret = lib_run_command.nsh_file_gen(cmd,tc_id,script_id,            # Library function call to generate nsh file
                                                log_level,tbd)
        if False == data_ret:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO : Failed to generate "
                              "required .nsh files", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
        else:
            pass

        if lib_run_command.create_logical_drive('S', tc_id, script_id,          # Library function call to create logical drive
                                                log_level,tbd):
            tool_name = cmd.split(".efi")                                       # Extract the tool name
            tool_path = lib_constants.TOOLPATH
            tool_found = False
            if 0 != len(tool_name[0]):                                          # Search for efi tool in tools directory
                files = glob.glob(tool_path + "\\\\*")
                for f in files:
                    if tool_name[0].lower() in f.lower():                       # If the tool or tool folder is found
                        tool_found = True
                        if os.path.isdir(f):                                    # If found instance is a directory
                            files1 = glob.glob(f)                               # Copy  all subfolders and files to S drive
                            for g in files1:
                                if tool_name[0].lower() in g.lower():
                                    cmd_copy = "xcopy /S /Y /I /E " + g +\
                                               " S:\\\\" +tool_name[0]
                                    os.system(cmd_copy)
                                    library.write_log(lib_constants.LOG_INFO,
                                          "INFO : VTInfo tool copied to "
                                          "S drive from tools path ", tc_id,
                                          script_id,"None","None",log_level,tbd)

                        else:
                            shutil.copy(f,"S:\\\\")
                            library.write_log(lib_constants.LOG_INFO,
                                          "INFO : VTInfo tool copied to "
                                          "S drive from tools path", tc_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                    elif True == tool_found :
                        break
                    else:
                        pass

                if False == tool_found:                                         # Tool not found
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO : VTInfo tool not found in the "
                                      "tools path %s " % tool_path,
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False

            if os.path.exists('S:\\\\'):                                        # Check for logical drive
                shutil.copy("startup.nsh","S:\\\\")                             # Copy startup nsh to current working directory
                if os.path.exists(cwd + "\subscript.nsh"):
                    shutil.copy("subscript.nsh", "S:\\\\")

                library.write_log(lib_constants.LOG_INFO,"INFO : .nsh file "
                            "copied successfully to S drive",tc_id, script_id,
                            "None", "None", log_level, tbd)

            else:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO, "INFO : Logical drive"
                                  " could not be found",tc_id,
                                  script_id, "None", "None",log_level, tbd)
                return False

        else:
            library.write_log(lib_constants.LOG_INFO,                           # Failed to create logical drive
                              "INFO : Failed to create logical drive ",
                              tc_id, script_id, "None","None", log_level, tbd)
            return  False

        if library.set_Multiple_bootorder(tc_id, script_id,
                                          log_level, tbd):                      # Change bootorder to EDK shell first
            library.write_log(lib_constants.LOG_INFO, "INFO : Internal "
                            "EDK Shell is set as the first boot device",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return True

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Failed to set"
                                " internal EDK Shell as the first boot device",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function name       : copy_vtinfo_log
# Description         : To copy the vtinfo tool from S:\ to SCRIPTS folder
# Parameters          : logfile,tc_id,script_id,log_level='ALL',tbd= None
# Returns             : return true on success and false otherwise
# Dependent Functions : lib_run_command.create_logical_drive()
#                       lib_run_command.drive_cleanup()
################################################################################

def copy_vtinfo_log(logfile,tc_id,script_id,log_level='ALL',tbd= None):
    try:

        gen_log = os.path.join("S:\\\\", logfile)                               # Path of generated log file in S: drive
        log_path = os.path.join(lib_constants.SCRIPTDIR, logfile)               # Destination path

        if os.path.exists(log_path):                                            # Clear old logs in the destination
            os.unlink(log_path)
        else:
            pass

        if lib_run_command.create_logical_drive('S',tc_id, script_id,
                        log_level, tbd) :                                       # Library function call to create logical drive S: drive
            if os.path.exists(gen_log) :                                        # If log is present in S: drive
                shutil.copy(gen_log,lib_constants.SCRIPTDIR)                    # Copy log to Script directory
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO,"INFO : VTInfo test"
                        " log is generated in EFI shell", tc_id, script_id,
                        "None", "None",log_level, tbd)
                time.sleep(lib_constants.FIVE_SECONDS)                          # Delay after file copy
                if os.path.exists(os.path.join(lib_constants.
                                            SCRIPTDIR,logfile)):                # Log copied from S drive to scripts folder
                    library.write_log(lib_constants.LOG_INFO,"INFO : VTInfo"
                            " test log is copied to scripts folder successfully"
                            ,tc_id,script_id,"None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO : Copying " # Log copying failed
                    "VTInfo test log to scripts folder failed",
                    tc_id, script_id, "None", "None",log_level, tbd)
                    return  False


                final_result = lib_run_command.drive_cleanup(tc_id,
                                    script_id, log_level, tbd)                  # Library function call to cleanup shared drive
                if  final_result:
                    library.write_log(lib_constants.LOG_INFO,"INFO : .nsh files"
                    " removed successfully", tc_id, script_id, "None", "None",  # Removed all nsh files from S: drive
                    log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO : Failed to"# Failed to remove .nsh files in S: drive
                    " remove .nsh files", tc_id, script_id, "None",
                    "None", log_level, tbd)
                    return True

            else:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO,"INFO :  VTInfo log is"
                " not present in the logical drive", tc_id, script_id, "None",  # VTInfo log is not present in S: drive
                "None", log_level, tbd)
                return False
        else :
            library.write_log(lib_constants.LOG_INFO, "INFO : Failed to create "# Unable to create logical drive
            "logical drive", tc_id, script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_ERROR, "ERROR: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name : parse_vtinfo_log
# Parameters    : status,test_title, file_path to parse,test case id, script id
# Purpose       : Parsing vtinfo.efi tool log
# Return Value  : 'True' and result on successful action and 'False' and result
#                   on failure
# Syntax        : verify parse log for <parameter>{ <delimiter>
#                    <expected_value>} from<source>
################################################################################


def parse_vtinfo_log(status, test_title, file_path, test_case_id, script_id,
                     log_level="ALL", tbd="None"):
    try:
        if "none" == test_title.lower():                                        # Test title is not mentioned
            if "pass" == status.lower():                                        # To verify if status is PASS
                result = False
                with open(file_path, mode="r") as f1:
                    p = vt = False
                    f = w = True
                    for line in f1.readlines():
                        line= lib_parse_log_file.remove_spaces(line)
                        if "vtteststatus" in line.lower():
                            vt = True
                        if "vtteststatus:pass" in line.lower():                 # If test summary is PASS, fail|00 and warn|00 in the log
                            p = True
                        if "fail|00" in line.lower():
                            f = False
                        if "warn|00" in line.lower():
                            w = False
                        if False == vt:
                            continue
                        if True == vt and "warn" in line.lower():
                            if True == p  and False == w and False == f:
                                result = True
                                library.write_log(lib_constants.LOG_INFO,
                                  'VTInfo Test status is PASS',
                                  test_case_id, script_id,
                                  "None", "None", log_level,
                                  tbd)
                                return False,True                               #Test status matches parameter
                            else:
                                with open(file_path, mode="r") as f2:
                                    line1 = ''
                                    for linex in f2.readlines():
                                        line2 =  lib_parse_log_file.remove_spaces(linex)
                                        if "result:warn" in line2.lower():      # If WARN in test result log
                                            result = False
                                            library.write_log(
                                            lib_constants.LOG_INFO,
                                            "VTInfo Test status is 'WARNING'"
                                            " for test '" + line1.upper() + "'",
                                            test_case_id, script_id, "None",
                                            "None", log_level, tbd)
                                            return False,False                  # Test status does not match parameter
                                        elif "result:fail" in line2.lower():    # If FAIL in test result log
                                            result = False
                                            library.write_log(
                                            lib_constants.LOG_INFO,
                                            "VTInfo Test status is 'FAIL' for"
                                            " test '" + line1.upper() + "'",
                                            test_case_id, script_id, "None",
                                            "None", log_level, tbd)
                                            return False,False                  # Test status does not match parameter
                                        else:
                                            line1 = linex
                f1.close()
            elif "fail" == status.lower():                                      # Test title is not mentioned
                                                                                # To verify if test status is fail
                result = False
                with open(file_path, mode="r") as f1:
                    for line in f1.readlines():
                        line= lib_parse_log_file.remove_spaces(line)
                        if "vtteststatus:fail" in line.lower():                 # If test fails as expected
                            result = True
                            with open(file_path, mode="r") as f2:
                                line1 = ''
                                for linex in f2.readlines():                    # extract the test name
                                    line2 =  lib_parse_log_file.remove_spaces(linex)
                                    if "result:fail" in line2.lower():
                                        result = True
                                        library.write_log(
                                        lib_constants.LOG_INFO,
                                        "VTInfo Test status is 'FAIL' for test '"
                                        + line1.upper() + "'",
                                        test_case_id, script_id, "None",
                                        "None", log_level, tbd)
                                        return  False,True                      #Test status matches parameter
                                    else:
                                        line1 = linex                           # Search till the failing testname is encountered

                        else:
                            continue
                if False == result:                                             # If test has not failed as expected
                    library.write_log(lib_constants.LOG_INFO,
                          'VTInfo Test status is not FAIL.', test_case_id,
                          script_id, "None", "None", log_level, tbd)
                    return False, False                                         # Test status does not match parameter
                f1.close()

        else:                                                                   # Test title is mentioned
            test = lib_parse_log_file.remove_spaces(test_title)
            with open(file_path, mode="r") as f1:
                found = False
                for line in f1.readlines():
                    line =  lib_parse_log_file.remove_spaces(line)
                    if test.lower() in line.lower():                            # If test name is found
                        found = True
                        continue
                    if True == found:
                        if status.lower() in line.lower():                      # If expected status word is found
                            library.write_log(lib_constants.LOG_INFO,
                              " VTInfo Test status verified: '" + status.upper()
                                + " for test " + test_title.upper() + "'",
                              test_case_id, script_id, "None",
                              "None", log_level, tbd)
                            return True, True                                   # Test status matches parameter

                        else:
                            result = False
                            library.write_log(lib_constants.LOG_INFO,
                              "VTInfo Test verification failed for '" +
                              test_title.upper() + " : " + status.upper() + "'",
                              test_case_id, script_id, "None",
                              "None", log_level, tbd)
                            return True, False                                  # Test status does not match parameter


    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Failed due"
                                                   " to %s" % e, test_case_id,
                          script_id, "None", "None", log_level, tbd)
