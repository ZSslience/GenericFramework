__author__ = "patnaikx"

###########################General Imports######################################
import os
import time
import subprocess
import wmi
import codecs

############################Local imports#######################################
import lib_constants
import library
import utils

################################################################################
# Function Name : updating_driver_in_device_manager
# Parameters    : test_case_id, script_id, ostr,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To update driver in device manager
################################################################################

def updating_driver_in_device_manager(ostr, test_case_id, script_id, log_level,
                                      tbd):
    try:
        ostr = ostr.upper()
        first_string = "DRIVER"
        last_string = "WITH"
        start_index = ostr.index( first_string ) + len( first_string )          #extracting driver name displayed in device manager
        end_index = ostr.index( last_string, start_index )
        driver_name = ostr[start_index:end_index]
        ostr = utils.ProcessLine(ostr)
        driver_name = driver_name.lower().lstrip()

        driver_file_name, pos = utils.extract_parameter_from_token(ostr,
                                            "WITH", "IN")                       #extracting driver file name to be update
        inf_name = utils.ReadConfig("Update_Drivers", "inf_name")               #reads the inf file name from config
        inf_setup_path=utils.ReadConfig("Update_Drivers", "inf_setup_path")     #reads the inf setup path where driver has to installed from config
        update_driver_name = utils.ReadConfig("Update_Drivers",
                                              "update_driver_name")             # reads updated driver name in device manager from config file
        devcon_path = utils.ReadConfig("Update_Drivers", "devcon_path")         # reads devcon path from config file
        driver_hwid = utils.ReadConfig("Update_Drivers","driver_hwid")          # reads hardware id of driver from config file
        for item in [inf_name, inf_setup_path, devcon_path, driver_hwid,
                                                        update_driver_name]:
            if "FAIL:" in item:                                                 # if failed to get driver update details from config
                library.write_log(lib_constants.LOG_INFO,
                "INFO: Config ini value for %s under Update_Driver tag not "
                "present"%item, test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                "INFO: Config ini value under Update_Driver tag fetched",
                test_case_id, script_id, "None", "None", log_level, tbd)
                pass

            if library.verify_dev_manager(update_driver_name, test_case_id,
                                    script_id, log_level, tbd):                 # calls the function to verify driver presence of updated driver in device manager
                library.write_log(lib_constants.LOG_INFO,
                "INFO: %s driver is already updated and listed in device"
                " manager"%update_driver_name, test_case_id, script_id,
                "None", "None", log_level, tbd)

                library.write_log(lib_constants.LOG_INFO,
                "INFO: Checking for any new update.....", test_case_id,
                script_id, "None", "None", log_level, tbd)

                status, logfile = inf_file_update(inf_setup_path, inf_name,
                    driver_hwid, devcon_path, driver_file_name, test_case_id,
                    script_id, log_level,tbd)                                   # Update files on updated driver

                parse_string1 = "Failed to install the driver on any of the " \
                            "devices on the system : No more data is available."# if no new update file is available, string to be parsed from registry log
                parse_string2 = "Driver package added successfully"             # if any update is there, string to be parsed from registry log
                if True == status:
                    if (library.parse_log(parse_string1, logfile, test_case_id,
                        script_id, tbd) or library.parse_log(parse_string2,
                        logfile, test_case_id, script_id, tbd)):
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: No new update file is available for "
                        "%s driver; driver is already updated"%driver_file_name,
                        test_case_id, script_id, "None", "None", log_level, tbd)#write msg to log
                        return True
                    else:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: %s Driver failed to update"%driver_file_name,
                        test_case_id, script_id, "None", "None", log_level,
                                          tbd)                                  #write msg to log
                        return False
            elif library.verify_dev_manager(driver_name, test_case_id, script_id,
                                    log_level, tbd):                            # calls the function to verify driver presence of original driver(with out any update) in device manager
                    library.write_log(lib_constants.LOG_INFO,
                    "INFO: Wait for the driver update.....", test_case_id,
                    script_id, "None", "None", log_level, tbd)
                    status, logfile = inf_file_update(inf_setup_path, inf_name,
                    driver_hwid, devcon_path, driver_file_name, test_case_id,
                    script_id, log_level, tbd)
                    parse_string = "Driver package added successfully"          # if any update is there, string to be parsed from registry log
                    if True == status:
                        if library.parse_log(parse_string, logfile, test_case_id,
                                     script_id, tbd):
                            library.write_log(lib_constants.LOG_INFO,
                            "INFO: Driver update successfull for "
                            "%s driver"%driver_file_name,test_case_id,
                            script_id, "None", "None", log_level, tbd)          #write pass message to log
                            return True
                        else:
                            library.write_log(lib_constants.LOG_INFO,
                            "INFO: %s Driver failed to update"%driver_file_name,
                            test_case_id, script_id, "None", "None", log_level,
                            tbd)                                                #write Fail message to log
                            return False

            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Driver "
                "%s is not installed properly or failed to list in "
                "device manager"%driver_file_name, test_case_id, script_id,
                "None", "None", log_level,tbd)
                return False
    except Exception as e:                                                      # returns false if any exception occurred
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
        "install_drivers function due to %s"%e,
        test_case_id, script_id, "None","None", log_level ,tbd)                 # returns false if any exception occurred during updating driver

################################################################################
# Function Name : inf_file_update
# Parameters    : driver_setup_path, driver_inf, driver_hwid, devcon_path,
#                 driver, loglevel, tbd
# Functionality : Function for .inf file update
# Return Value  : On success return True, False on failure
################################################################################


def inf_file_update(driver_setup_path, driver_inf, driver_hwid, devcon_path,
                    driver, test_case_id, script_id, loglevel = "ALL",
                    tbd = None):
    try:
        new_script_id = script_id.strip(".py")
        log_file = new_script_id + '.txt'
        script_dir = lib_constants.SCRIPTDIR
        log_path = script_dir + "\\" + log_file
        inf_command = lib_constants.INF_COMMAND
        driver_cmd = inf_command+" "+driver_setup_path+\
                 "\\"+driver_inf+ " > "+ log_path                               # command for updating driver - inf file
        os.system(driver_cmd)
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        os.chdir(devcon_path)
        driver_rescan_cmd = "devcon_x64.exe rescan"+ " " + '"'+driver_hwid+'"'
        verify_proc = subprocess.Popen(driver_rescan_cmd,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False,
                                       stdin=subprocess.PIPE)              #Esecute the driver_rescan_command through subprocess method
        if os.path.exists(log_path):                                            #check for logfile generated
            file_size = os.path.getsize(log_path)                               #check for size of the file
            if 0 != file_size:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO, "INFO: Driver update"
                " command ran successfully",test_case_id,script_id,"None","None",
                loglevel, tbd)
                return True, log_file                                           # return True and file path if command ran
            else:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "run driver update command", test_case_id, script_id, "None",
                "None", loglevel, tbd)
                return False, "None"                                            # return false and None if failed to run command

    except Exception as e:                                                      #if exception occur in execution of command then set output to 1
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
                "inf file installation for driver %s due to %s"%(e,driver),
                        test_case_id,script_id,"None", "None", loglevel, tbd)   #write msg to log
        return False, "None"
