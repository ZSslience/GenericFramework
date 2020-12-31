author = "Automation Team"

# General Python Imports
import os
import subprocess

# Local Python Imports
import lib_constants
import utils
import library

################################################################################
# Function name   : read_me_state
# Description     : To read current ME State using MEInfo Tool
# Parameters      : me_state, test_case_id, script_id, log_level, tbd
# Return Value    : Returns current ME State on successful action,
#                   False otherwise
################################################################################


def read_me_state(me_state, test_case_id, script_id, log_level="ALL",
                  tbd=None):

    try:
        meinfotoolpath = utils.ReadConfig("MEInfotool", "path")                 # Fetches ME info path from config file
        if "FAIL" in meinfotoolpath:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entries "
                              "not updated under section 'MEInfotool'",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

        os.chdir(meinfotoolpath)                                                # Changes directory to meinfo tool path as specified in config file
        if not os.path.exists("MEInfoWin64.exe"):
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Missing "
                              "'MEInfotool.exe' which is mentioned in config "
                              "path. check path under section "'MEInfotool'"",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False                                                        # Returns false if failed to find the tool path
        else:
            command_run = lib_constants.MEINFO_DUMP                             # Command for generating ME info dump
            handle = subprocess.Popen(command_run, shell=True,
                                      stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
            output = handle.communicate()[0]

            with open("MEInfodump.txt", 'r') as fp:
                for line in fp:
                    if "operationalstate" in line.lower() or \
                            "fw memory state" in line.lower():                  # Checking for Operational state or fw memory state for to get current me state
                        if me_state.lower() in line.lower():                    # checking for current me state
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "ME state is %s" % me_state,
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            return me_state
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to find ME "
                                              "state", test_case_id, script_id,
                                              "None", "None", log_level, tbd)
                            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
