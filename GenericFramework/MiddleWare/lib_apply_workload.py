__author__ = r"parthibax\kapilshx\tnaidux"

# General Python Imports
import glob
import os
import shutil
import time
import subprocess

# Local Python Imports
import lib_constants
import library
import utils
import lib_tat_tool_installation

################################################################################
# Function Name   : apply_workload
# Parameters      : ostr, test_case_id, script_id, log_level, tbd
# Functionality   : Applying load on gfx
# Return Value    : Returns the path on successful Action, 'False' on failure
################################################################################


def apply_workload(ostr, test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        if os.path.exists(lib_constants.PSTATE_WORKSPACE_APPLY_WORKLOAD):
            library.write_log(lib_constants.LOG_INFO, "INFO: P-State xml "
                              "already exists. Path: %s"
                              % lib_constants.PSTATE_WORKSPACE_APPLY_WORKLOAD,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: P-State xml"
                              " not found", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        os.chdir(lib_constants.SCRIPTDIR)

        if os.path.exists(lib_constants.TAT_TOOL_PATH):                         # Check for TAT installation
            library.write_log(lib_constants.LOG_INFO, "INFO: TAT Tool is "
                              "already installed", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            try:
                host_service_start_cmd = "net start Intel(R)TATHostService"
                target_service_start_cmd = "net start Intel(R)TATTargetService"
                os.chdir(lib_constants.TAT_TOOL_PATH)
                host_op = os.system(host_service_start_cmd)
                os.chdir(lib_constants.INSTALLEDPATH_TARGET)
                target_op = os.system(target_service_start_cmd)
                
                library.write_log(lib_constants.LOG_INFO, "INFO: TAT Target "
                                  "service & TAT Host service has started "
                                  "successfully", test_case_id, script_id, 
                                  "None", "None", log_level, tbd)
                pass
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None", 
                                  "None", log_level, tbd)
                return False
        else:                                                                   # Tat tool not installed, installing now
            install = lib_tat_tool_installation.\
                tat_tool_installation(test_case_id, script_id, log_level,tbd)

            if install:                                                         # Checking for tat tool installation
                library.write_log(lib_constants.LOG_INFO, "INFO: TAT Tool "
                                  "installed", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: TAT tool not "
                                  "installed", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

        if "GFX" in ostr.upper():                                               # Code for apply workload on gfx
            ostr = ostr.split()
            logfile_name = script_id.split(".")[0]
            duration = int(ostr[3]) * lib_constants.WORKLOAD_GFX_SECS           # Extract duration from the syntax
            load = int((ostr[6])[:-1])                                          # Extract the percentage of workload to apply from the syntax

            if (load >= lib_constants.MINIMUM_WORKLOAD_GFX and
                load <= lib_constants.MAXIMUM_WORKLOAD_GFX):                    # Check if load value is between 70 and 101
                library.write_log(lib_constants.LOG_INFO, "INFO: Load "
                                  "percentage is between 70 and 100",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Load "
                                  "percentage should be between 70 and 100",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            duration = str(int(duration))
            tat = r'<?xml version="1.0"?>' + "\n"                               # Store the xml command
            tat_script = tat + lib_constants.CPU_GFX % (load, duration)

            os.chdir(lib_constants.TAT_TOOL_PATH)

            with open("TatScript_Gfx.xml", "w") as handle:                      # Create an xml file
                handle.write(tat_script)                                        # Write to the script to the file

            handle.close()
            tat_gfx_cmd = "%s -s=TatScript_Gfx.xml -t=%s -m=gfxmonitor.csv" \
                % (lib_constants.TAT_CLI, duration)

            if os.path.exists(os.path.join(lib_constants.TAT_TOOL_PATH,
                                           "TatScript_Gfx.xml")):               # Check for xml file is there
                    library.write_log(lib_constants.LOG_INFO, "INFO: File "
                                      "TatScript_Gfx.xml is generated",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)                           # Write to log TAT script is generated
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to generate TatScript_Gfx File",
                                  test_case_id, script_id, "None", "None",
                                  log_level,tbd)
                return False

            os.chdir(lib_constants.SCRIPTDIR)

            for filename in glob.glob(logfile_name + ".csv"):
                os.remove(filename)                                             # Deleting old log files if exists

            os.chdir(lib_constants.TAT_TOOL_PATH)

            for log_file in glob.glob("gfxmonitor*"):
                os.remove(log_file)                                             # Deleting old log files if exists

            subprocess.Popen(tat_gfx_cmd, stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE)    # Use subprocess to run tat_cmd

            time.sleep(int(duration)/lib_constants.WORKLOAD_GFX_HALFSECS)

            tat_kill_cmd = r"TASKKILL /F /IM %s /T " % lib_constants.TAT_CLI

            res, err = subprocess.Popen('tasklist', shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdin=subprocess.PIPE).communicate()

            if "Ptu-Gfx.exe" in res:                                            # Checking Ptu-Gfx.exe is running
                time.sleep(int(duration)/lib_constants.WORKLOAD_GFX_HALFSECS)
                os.system(tat_kill_cmd)
                for filename in glob.glob("gfxmonitor*"):
                    logfilepath = lib_constants.SCRIPTDIR + os.sep + \
                        logfile_name + ".csv"
                    shutil.move(filename,logfilepath)

                    library.write_log(lib_constants.LOG_INFO, "INFO: Applied "
                                      "workload successfully", test_case_id,
                                      script_id, "None", "None", log_level, tbd)

                    log_filesize = os.path.getsize(logfilepath)
                    if not log_filesize == "":
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "Returning log file path %s"
                                          % logfilepath, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return logfilepath                                      # If log file generated successfully it returns the path
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Log file not generated",
                                          test_case_id, script_id, "None",
                                          "None", log_level,tbd)
                        return False
            else:
                os.system(tat_kill_cmd)
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to apply workload", test_case_id, script_id,
                                  "None", "None", log_level,tbd)
                return False
        else:                                                                   # Code for apply workload on cpu cores
            token_list = ostr.upper().split()

            if "CORE" in ostr.upper():                                          # Check for core in the syntax
                load, pos = utils.extract_parameter_from_token(token_list,
                                                               "WITH", "ON",
                                                               log_level, tbd)  # Extract the load from the syntax
            else:
                load, pos = utils.extract_parameter_from_token(token_list,
                                                               "WITH", "",
                                                               log_level, tbd)  # Extract the load from the syntax

            duration, pos = utils.extract_parameter_from_token(token_list,
                                                               "FOR",
                                                               "SECONDS",
                                                               log_level, tbd)  # Extract duration from the syntax

            if "%" in load:                                                     # If % in load remove the percentage
                load = load[:-1]
            else:
                load = load

            if "CORE" in ostr.upper():                                          # If CORE in syntax
                if "ALL" in ostr.upper():                                       # If all in syntax, for all core
                    core = "CPU-All"                                            # CPU all for core if ALL in syntax
                else:
                    core,pos = utils.extract_parameter_from_token(token_list,
                                                                  "ON",
                                                                  "CORES",
                                                                  log_level,
                                                                  tbd)          # Extract core from the syntax, ex for 2 cores/ for 3 cores
            else:
                core = "CPU-All"                                                # Default core all for core if no optional syntax is provided

            if int(load) not in lib_constants.C_STATE_PERC:                     # If load not in [0,50,60,70,80,90,100] list return false
                library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                  "Invalid workload: should be either 0, 50, "
                                  "60,70,80,90, or 100", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Workload to "
                                  "apply is %s percent for %s seconds on %s "
                                  "cores" % (load, duration, core),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                if "0" == load:                                                 # If load is 0 return true with out any workload
                    library.write_log(lib_constants.LOG_INFO, "INFO: Not "
                                      "applying any workload as workload to "
                                      "apply is 0 percent", test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return True

            cpu_core = library.logical_processors()

            if "CPU-All" == core:
                tat = r'<?xml version="1.0"?>' + "\n"
                tat_script = tat + \
                    lib_constants.CPU_CPU % (load, str(int(duration)*1000))     # Appending load and duration extracted from syntax in the script
            elif int(core) > int(cpu_core):
                library.write_log(lib_constants.LOG_WARNING, "WARNING: System "
                                  "does not support %s core, Default available"
                                  " cores of system is %s" % (cpu_core, core),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
            else:
                tat = r'<?xml version="1.0"?>' + "\n"

                start = r"<TatScript><Version>1.0</Version><CMD>" \
                        r"<ComponentName/><Command>StartLog</Command>" \
                        r"<NodeCount>0</NodeCount><CommandName/><Value>0" \
                        r"</Value></CMD>"

                start_workload = r""                                            # Initialise workload

                duration_xml = int(duration)*1000

                delay = r"<CMD><ComponentName/><Command>Delay</Command>" \
                        r"<NodeCount>0</NodeCount><CommandName/><Value>%s" \
                        r"</Value></CMD>" %(str(duration_xml))

                stop_workload = r""                                             # Initialise stop workload

                end = r"<CMD><ComponentName/><Command>StopLog</Command>" \
                      r"<NodeCount>0</NodeCount><CommandName/><Value>0" \
                      r"</Value></CMD></TatScript>"

                for i in range(0, int(core)):                                   # Iterate for number of cores
                    act_cores = "CPU" + str(i)                                  # Core name is CPU0/CPU1/CPU2 etc

                    start_workload += r"<CMD><ComponentName>CPU Component" \
                                      r"</ComponentName><Command>" \
                                      r"StartWorkLoad</Command><NodeCount>1" \
                                      r"</NodeCount><NodeArg>CPU-Utilization" \
                                      r"</NodeArg><CommandName>%s" \
                                      r"</CommandName><Value>%s</Value></CMD>" \
                                      % (act_cores, load)                       # Append corename and load in the script

                    stop_workload += r"<CMD><ComponentName>CPU Component" \
                                     r"</ComponentName><Command>StopWorkLoad" \
                                     r"</Command><NodeCount>1</NodeCount>" \
                                     r"<NodeArg>CPU Power</NodeArg>" \
                                     r"<CommandName>%s</CommandName></CMD>" \
                                     % act_cores                                # Append core name

                tat_script = tat + start + start_workload + delay + \
                    stop_workload + end

            os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)
            cmd = lib_constants.DELETE_CSV_FILE
            os.system(cmd)

            os.chdir(lib_constants.TAT_TOOL_PATH)
            with open("TatScript.xml", "w") as handle:                          # Write the appended script as Tatscript.xml in Tat installed directory
                handle.write(tat_script)

            tat_cmd = lib_constants.TAT_CLI + " -AL" + " -s=TatScript.xml" + \
                " -t=%s"%duration + " -w=" + \
                lib_constants.PSTATE_WORKSPACE_APPLY_WORKLOAD                   # Store the command to run in a variable

            process = subprocess.Popen(tat_cmd, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
            stdout, stderr = process.communicate()
            time.sleep(lib_constants.TEN_SECONDS)

            if "script failed" in stdout.lower():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to apply workload using TAT Tool",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            file_name_script = script_id.replace(".py", ".csv")

            try:
                os.chdir(lib_constants.TAT_TOOL_RESULT_PATH)

                for file in os.listdir(lib_constants.TAT_TOOL_RESULT_PATH):
                    file_name, file_ext = os.path.splitext(file)
                    os.rename(lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                              file_name + ".csv",
                              lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                              file_name_script)

                shutil.copy(lib_constants.TAT_TOOL_RESULT_PATH + "\\" +
                            file_name_script, lib_constants.SCRIPTDIR)
            except Exception as e:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            utils.write_to_Resultfile(lib_constants.SCRIPTDIR + "\\" +
                                      file_name_script, script_id)              # Write to result file the location of the log path

            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "generated log file from Tat tool", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
