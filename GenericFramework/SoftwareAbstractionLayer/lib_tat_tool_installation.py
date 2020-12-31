
#########################General library imports################################
import os
import sys
import time
import subprocess
import filecmp
################################################################################


#########################Local library imports##################################
import library
import lib_constants
import utils
################################################################################

################################################################################
#  Function     : tat_tool_installation
#  Description  : installs the tat tool
#  Param        : testcase id, script id, loglevel and tbd
#  Purpose      : Installs the tat tool if its not present in sut
#  Return       : Return True if no difference found after comparing two files
################################################################################


def tat_tool_installation(test_case_id, script_id, loglevel="012345",
                          tbd="None"):
    try:
        installedpath = utils.ReadConfig('TAT_TOOL', 'installedpath' )
        if "FAIL:" in installedpath:
            library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG ENTRY"
                " for Installedpath of TAT is missing" , test_case_id,script_id,
                                      "None", "None", loglevel, tbd)
        else:
            pass
        installedpath_target = utils.ReadConfig('TAT_TOOL',
                                                'installedpath_target' )
        if "FAIL:" in installedpath_target:
            library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG ENTRY"
                " for installedpath_target of TAT is missing" , test_case_id,
                              script_id, "None", "None", loglevel, tbd)
        else:
            pass
        host_service_start_cmd = "net start Intel(R)TATHostService"
        target_service_start_cmd = "net start Intel(R)TATTargetService"
        if not os.path.exists(installedpath):
            try:
                setup = utils.ReadConfig('TAT_TOOL', 'setup')                   #read tat setup name from config file
                if "FAIL:" in setup:
                    library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG "
                "ENTRY for setup of TAT is missing" , test_case_id, script_id,
                                              "None", "None", loglevel, tbd)
                else:
                    pass

                setup_path = utils.ReadConfig('TAT_TOOL', 'setup_path')         #read setup_path name from config file
                if "FAIL:" in setup_path:
                    library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG "
            "ENTRY for setup_path of TAT is missing" , test_case_id, script_id,
                                              "None", "None", loglevel, tbd)
                else:
                    pass
                auto_tool = utils.ReadConfig('TAT_TOOL', 'auto_tool')
                if "FAIL:" in auto_tool:
                    library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG "
            "ENTRY for auto_tool of TAT is missing" , test_case_id, script_id,
                                              "None", "None", loglevel, tbd)
                else:
                    pass

                install_cmd = setup + ' -s'                                     #store the command in a variable
                os.chdir(setup_path)
                subprocess.Popen(install_cmd, stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE).communicate()                     #run the cmd on a subprocess
                time.sleep(lib_constants.SX_TIMEOUT)                            #sleep for 200 seconds
                if os.path.exists(installedpath):
                    subprocess.Popen(auto_tool, stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE)                                 #run the auto it file to accept the
                    time.sleep(lib_constants.SLEEP_TIME)                        #sleep for 15 seconds
                    library.write_log(lib_constants.LOG_INFO, "INFO: Tool"
                        " Installed Successfully" , test_case_id,script_id,
                                      "None", "None", loglevel, tbd)
                    try:
                        os.chdir(installedpath)
                        host_op = os.system(host_service_start_cmd)
                        os.chdir(installedpath_target)
                        tareget_op = os.system(target_service_start_cmd)
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: TAT Target service & TAT Host service has started"
                            " successfully",test_case_id, script_id, "None",
                                          "None", loglevel, tbd)
                        pass
                    except Exception as e:
                        os.chdir(lib_constants.SCRIPTDIR)
                        library.write_log(lib_constants.LOG_ERROR,
                        "ERROR:Failed to start TAT Target service & TAT Host"
                        " service due to %s"%(e),test_case_id, script_id,
                                          "None","None", loglevel, tbd)
                        return False
                    return True
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Tool Not "
                        "Installed", test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                    return False
            except Exception as err:
                error = 'Tool Not Installed due %s\n'%err
                library.write_log(lib_constants.LOG_ERROR,"ERROR:"+ error
                                  ,test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Tool is Already "
            "Installed", test_case_id, script_id, "None", "None",loglevel, tbd)

            try:
                os.chdir(installedpath)
                host_op = os.system(host_service_start_cmd)
                os.chdir(installedpath_target)
                tareget_op = os.system(target_service_start_cmd)
                library.write_log(lib_constants.LOG_INFO,
                "INFO: TAT Target service & TAT Host service has started"
                    " successfully",test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                pass
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR,
                "ERROR:Failed to start TAT Target service & TAT Host"
                " service due to %s"%(e),test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return False

            return True
    except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Failed due "
            "to %s"%e, test_case_id, script_id, "None", "None", loglevel, tbd)
            return False