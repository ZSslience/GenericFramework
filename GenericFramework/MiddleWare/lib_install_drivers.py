__author__ = 'Ashax\kapilshx\sushil3x\Anil\kashokax\sivakisx\tnaidux'

##########################General Imports#######################################
import codecs
import os
import subprocess
import sys                                                                      #This will clear all ascii charaters in the script
#reload(sys)
#sys.setdefaultencoding('utf-8')
import time
import wmi
import shutil
################################################################################
import lib_constants
import lib_set_bios
import library
import utils
################################################################################
# Function Name : install_drivers
# Parameters    : driver, test_case_id, script_id, log_level and tbd
# Functionality : This checks the driver in device manager
# Return Value  : True on successful action, False otherwise
################################################################################


def install_drivers(driver, test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        setup = utils.ReadConfig("Install_Drivers","setup")                     # reads the setup file name from the config file
        setup_command = setup + " -s"                                           # this is the generic silent installation command for driver to install
        if "graphics" in driver.lower() or "graphic" in driver.lower() or \
           "gfx" in driver.lower():                                             #Checks if graphics string is present in the driver name
            try:
                gfx_setup_name = utils.ReadConfig("Install_Drivers",
                                                 "gfx_setup_name")
                gfx_setup_path = utils.ReadConfig("Install_Drivers",
                                                  "gfx_setup_path")
                if "FAIL:" in [gfx_setup_name, gfx_setup_path]:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Config.ini value for gfx_setup_name & "
                    "gfx_setup_path are not present under [Install_Drivers]",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)                           #Writing log warning message to the log file
                    return False
                else:
                    pass
                if win_security_pop_up_handler(test_case_id, script_id,
                                               log_level, tbd):
                    pass                                                        #Function calling for to accept windows security popup
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Failed to execute win security exe to handle "
                    "windows popup", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             #Writing log warning message to the log file
                    return False
                setup_command = gfx_setup_name + " -s"
                os.chdir(os.path.join(lib_constants.TOOLPATH, gfx_setup_path))
                installation_proc = subprocess.Popen(setup_command,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     shell=False,
                                                     stdin=subprocess.PIPE)
                installation_proc.communicate()                                 #Executes to install the driver in silent mode
                output = installation_proc.returncode                           #Checking for the name of the driver

            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception "
                "in graphics driver installation due to %s"%e, test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing exception message to the log file

        elif "txei" in driver.lower():                                          #Checks if txei string is present in the driver name
            try:
                txei_tool_name = utils.ReadConfig("Install_Drivers",
                                                  "txei_tool_name")
                txei_setup_path = utils.ReadConfig("Install_Drivers",
                                                   "txei_setup_path")           #Config entries for tool name & tool path
                if "FAIL:" in [txei_tool_name, txei_setup_path]:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Config.ini value not present", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  #Writing log warning message to the log file
                    return False
                else:
                    pass
                setup_command = txei_tool_name + " -s"                          # command to install the driver
                os.chdir(os.path.join(lib_constants.TOOLPATH, txei_setup_path)) # change the directory to tool directory
                installation_proc = subprocess.Popen(setup_command,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     shell=False,
                                                     stdin=subprocess.PIPE)
                installation_proc.communicate()                                 #Executes to install the driver in silent mode
                output = installation_proc.returncode                           #Checking for the name of the driver
                library.write_log(lib_constants.LOG_INFO, "INFO: Txei driver "
                "installation command ran sucessfully", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log_info message to the log file

            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception "
                "in trusted execution engine driver installation due to %s"%e,
                test_case_id, script_id, "None", "None", log_level, tbd)        #Writing exception message to the log file

        elif "gmm" in driver.lower():
            gmm_inf = utils.ReadConfig("Install_Drivers", "gmm_inf")
            gmm_tool_name = utils.ReadConfig("Install_Drivers", "gmm_tool_name")#Reads the gmm tool name from the config file
            gmm_setup_path = utils.ReadConfig("Install_Drivers",
                                              "gmm_setup_path")                 #Reads the gmm setup path where driver has to installed from the config file
            gmm_hwid = utils.ReadConfig("Install_Drivers", "gmm_hw_id")         #Reads hardware id of the gmm driver from config file

            if "FAIL:" in [gmm_inf, gmm_tool_name, gmm_setup_path, gmm_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config"
                ".ini value not present", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
            else:
                pass

            output = inf_file_installation(gmm_setup_path, gmm_inf, gmm_hwid,
                                            driver, test_case_id, script_id,
                                           log_level, tbd)                      #Function calling for to perform inf file installation
        elif "gna" in driver.lower():
            gna_inf = utils.ReadConfig("Install_Drivers", "gna_inf")
            gna_tool_name = utils.ReadConfig("Install_Drivers", "gna_tool_name")#Reads the gmm tool name from the config file
            gna_setup_path = utils.ReadConfig("Install_Drivers",
                                              "gna_setup_path")                 #Reads the gmm setup path where driver has to installed from the config file
            gna_hwid = utils.ReadConfig("Install_Drivers", "gna_hw_id")         #Reads hardware id of the gmm driver from config file

            if "FAIL:" in [gna_inf, gna_tool_name, gna_setup_path, gna_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config"
                ".ini value not present", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
            else:
                pass

            output = inf_file_installation(gna_setup_path, gna_inf, gna_hwid,
                                            driver, test_case_id, script_id,
                                           log_level, tbd)                      #Function calling for to perform inf file installation
        elif "gpio" in driver.lower():                                          #if gpio is the driver to be installed
            gpio_setup_path = utils.ReadConfig("Install_Drivers",
                                               "gpio_setup_path")               #Read setup path from config file
            gpio_inf = utils.ReadConfig("Install_Drivers", "gpio_inf")          #Read .inf file from config file
            gpio_hwid = utils.ReadConfig("Install_Drivers", "gpio_hw_id")       #Read hardware id from config file

            if "FAIL:" in [gpio_setup_path, gpio_inf, gpio_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            output = inf_file_installation(gpio_setup_path, gpio_inf, gpio_hwid,
                                           driver, test_case_id,
                                           script_id, log_level, tbd)           #Function calling for to perform inf file installation

        elif "i2c" in driver.lower() or "i2c1" in driver.lower():               #if i2c is the token
            i2c_setup_path = utils.ReadConfig("Install_Drivers",
                                              "i2c_setup_path")                 #Extracting i2c setup path from config file
            i2c_inf = utils.ReadConfig("Install_Drivers", "i2c_inf")            #Extracting i2c inf file from config file
            i2c_hwid = utils.ReadConfig("Install_Drivers", "i2c_hw_id")         #Extracting i2c hardware id from config file

            if "FAIL:" in [i2c_setup_path, i2c_inf, i2c_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to get the config entry for i2c_setup_path, i2c_inf& i2c_hwid",
                                  test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 #Writing log warning message to the log file
                return False
            else:
                pass

            output = inf_file_installation(i2c_setup_path, i2c_inf, i2c_hwid,
                                           driver, test_case_id,
                                           script_id, log_level, tbd)           #Function calling for to install the inf file of i2c driver

        elif "avstream" in driver.lower() or "skycam" in driver.lower() or \
             "sky cam" in driver.lower():                                       #If AStream or Skycam is the driver to be installed
            avstream_tool_name = utils.ReadConfig("Install_Drivers",
                                                  "avstream_tool_name")         #Extracting avstream or skycam tool name from config file
            avstream_setup_path = utils.ReadConfig("Install_Drivers",
                                                   "avstream_setup_path")       #Extracting avstream or skycam setup path from config file
            avstream_hwid = utils.ReadConfig("Install_Drivers",
                                             "avstream_hw_id")                  #Extracting avstream or skycam driver hardware id from config file
            avstream_inf = utils.ReadConfig("Install_Drivers", "avstream_inf")  #Extracting avstream or skycam inf file from config file

            if "FAIL:" in [avstream_tool_name, avstream_setup_path,
                           avstream_hwid, avstream_inf]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to get the config entry for avstream_tool_name, "
                "avstream_setup_path, avstream_hwid, and avstream_inf from "
                "config file", test_case_id, script_id, "None", "None",
                                  log_level, tbd)                               #Writing log warning message to the log file
                return False
            else:
                pass

            output = inf_file_installation(avstream_setup_path, avstream_inf,
                                           avstream_hwid, driver,
                                           test_case_id, script_id, log_level,
                                           tbd)                                 #Function calling for to perform avstream or skycam driver inf file installation

        elif "csme" in driver.lower() or "me" in driver.lower():
            csme_setup_path = utils.ReadConfig("Install_Drivers",
                                               "csme_setup_path")
            csme_setup = utils.ReadConfig("Install_Drivers", "csme_setup")
            csme_command = csme_setup + " " + "-s"

            if "FAIL:" in [csme_setup_path, csme_setup]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry is missing for csme_setup_path & csme_setup under "
                "[Install_Drivers] tag", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False

            try:
                utils.filechangedir(csme_setup_path)
                installation_proc = subprocess.Popen(csme_command,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     shell=False,
                                                     stdin=subprocess.PIPE)
                installation_proc.communicate()                                 #Executes to install the driver in silent mode
                output = installation_proc.returncode
                time.sleep(lib_constants.TEN_SECONDS)                           #Checking for the name of the driver
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
                test_case_id, script_id, "None", "None", log_level, tbd)        #Writing exception message to the log file

        elif "ISH" == driver.upper():                                           #If ish is the driver to be installed
            ish_setup_path = utils.ReadConfig("Install_Drivers",
                                              "ish_setup_path")                 #Read ish_setup path from config entry
            ish_setup = utils.ReadConfig("Install_Drivers", "ish_setup")        #Read setup file from config entry
            ish_command = ish_setup + " " + "/s"                                #Command to install ish driver

            if "FAIL:" in [ish_setup_path, ish_setup]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log_info message to the log file

            try:
                os.chdir(ish_setup_path)                                        #Change the current working directory to setup path
                installation_proc = subprocess.Popen(ish_command,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     shell=False,
                                                     stdin=subprocess.PIPE)
                installation_proc.communicate()                                 #Executes command  to install the ish driver in silent mode
                output = installation_proc.returncode                           #Assign return code after executing command to output

            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception "
                "in ish driver installation due to %s"%e, test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing exception message to the log file

        elif "irmt" == driver.lower():                                          #If irmt is the driver to be installed
            iRMT_setup_path = utils.ReadConfig("Install_Drivers",
                                               "iRMT_setup_path")               #read irmt setup path from config entry
            iRMT_setup = utils.ReadConfig("Install_Drivers","iRMT_setup")       #read irmt setup file from config entry
            iRMT_installed_path = utils.ReadConfig("Install_Drivers",
                                                   "iRMT_installed_path")       #Read the path created after irmt installation from config entry
            iRMT_cmd = iRMT_setup + " " + "-s"                                  #Command to install irmt app

            if "FAIL:" in [iRMT_setup_path, iRMT_setup, iRMT_installed_path]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag ", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            try:
                os.chdir(iRMT_setup_path)                                       #change current working directory to irmt setup path
                installation_proc = subprocess.Popen(iRMT_cmd,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     shell=False,
                                                     stdin=subprocess.PIPE)
                if "" == installation_proc.communicate()[0]:                    #executes cmd  to install the driver in silent mode and verifies whether the command is executed successfully
                    if os.path.exists(iRMT_installed_path):                     #confirms irmt installation by verifying the installed path generated after executing the command
                        return True
                    else:
                        return False                                            #if installed path is not found then irmt is not installed
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Failed to execute the command for irmt "
                    "installation", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             #Writing log warning message to the log file
                    return False
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " iRMT installation due to %s"%e, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing exception message to the log file
                return False

        
        elif "ITH" in driver.upper():                                           #If ith is the driver to be installed
            ith_setup_path = utils.ReadConfig("Install_Drivers",
                                              "ith_setup_path")                 #Read ith_setup_path from config file
            ith_inf = utils.ReadConfig("Install_Drivers", "ith_inf")            #Read .inf file from config file
            ith_hwid = utils.ReadConfig("Install_Drivers", "ith_hwid")          #Read hardware id of ith driver from config file

            if "FAIL:" in [ith_setup_path, ith_inf, ith_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            output = inf_file_installation(ith_setup_path, ith_inf, ith_hwid,
                                            driver, test_case_id,
                                           script_id, log_level, tbd)           #Function calling for to perform inf file installation

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
            "driver name or UDL not in production", test_case_id, script_id,
                              "None",  "None", log_level, tbd)                  #Writing log warning message to the log file
            return False
        try:
            if 1 != output:
                if verify_dev_manager(driver, test_case_id, script_id,
                                      log_level, tbd):                          #Function calling for to verify driver presence in device manager
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s Driver"
                    " installed and listed in device manager"%driver,
                    test_case_id, script_id, "None", "None", log_level, tbd)    #Writing log info message to the log file
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Driver %s is not installed properly or failed to"
                    " list in device manager"%driver, test_case_id, script_id,
                    "None", "None", log_level, tbd)                             #Writing log warning message to the log file
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Driver "
                "%s fail to install"%driver, test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
            test_case_id, script_id, "None", "None", log_level, tbd)            #Writing exception message to the log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return False

################################################################################
# Function Name : inf_file_installation
# Parameters    : driver_setup_path, driver_inf, driver_hwid, devcon_path,
#                 driver, test_case_id, script_id, log_level and tbd
# Functionality : function for .inf file installation
# Return Value  : On success return True, False on failure
################################################################################


def inf_file_installation(driver_setup_path, driver_inf, driver_hwid,
                          driver, test_case_id, script_id, log_level="ALL",
                          tbd=None):

    try:
        inf_command = "-i -a"
        os.chdir(lib_constants.TOOLPATH)
        driver_cmd = "PnPutil.exe" + " " + inf_command + " " + \
                     driver_setup_path + "\\" + driver_inf                      #Command for installing driver - inf file

        output = subprocess.Popen(driver_cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, shell=False,
                                  stdin=subprocess.PIPE)
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        output.communicate()                                                    # executes inf command to install the driver in silent mode
        output = output.returncode
        os.chdir(lib_constants.DEVCON_PATH)
        driver_rescan_cmd = "devcon_x64.exe rescan" + " " + '"'+driver_hwid+'"'
        subprocess.Popen(driver_rescan_cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=False,
                         stdin=subprocess.PIPE)                                 #Execute the driver_rescan_command through subprocess method
        return output
        
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "inf file installation for driver %s due to %s"%(e, driver),
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return output
################################################################################
# Function Name : verify_dev_manager
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This checks the driver in device manager
# Return Value  : True/False
################################################################################


def verify_dev_manager(driver_name, test_case_id, script_id, log_level="ALL",
                       tbd=None):                                               #Function calling for to verify the driver name in device manager

    try:
        Gfx_string = utils.ReadConfig("Install_Drivers","Gfx_name_in_devmgmt")  # reads the driver name from the config file
        Bt_string = utils.ReadConfig("Install_Drivers","Bt_name_in_devmgmt")
        Wlan_string = utils.ReadConfig("Install_Drivers","Wlan_name_in_devmgmt")
        gmm_string = utils.ReadConfig("Install_Drivers","gmm_name_in_devmgmt")
        gna_string = utils.ReadConfig("Install_Drivers","gna_name_in_devmgmt")
        avstream_string = utils.ReadConfig("Install_Drivers",
                                           "avstream_name_in_devmgmt")
        csme_string = utils.ReadConfig("Install_Drivers","csme_name_in_devmgmt")
        txei_string = utils.ReadConfig("Install_Drivers","txei_name_in_devmgmt")
        SG_string = utils.ReadConfig("Install_Drivers","SG_name_in_devmgmt")
        gpio_string = utils.ReadConfig("Install_Drivers","gpio_in_devmgmt")
        i2c_string = utils.ReadConfig("Install_Drivers","i2c_in_devmgmt")
        ish_string = utils.ReadConfig("Install_Drivers","ish_in_devmgmt")
        ith_string = utils.ReadConfig("Install_Drivers","ith_in_devmgmt")
        '''lst= []
        c = wmi.WMI ()                                                          # executes the wmi query to get the  device name from the device manager
        for device in c.Win32_PnPEntity():
            print str(device.Description)
            str(device.Description).replace("\xae","(R)")
            if device.Description != None:
                lst.append(str(device.Description))                             #all device list of device manager stored in the lst
            else:
                pass'''

        dev_listfile = library.get_entire_device_list(test_case_id, script_id,
                                                      log_level, tbd)
        if False == dev_listfile:
            return False
        else:
            with open(dev_listfile,"r") as f_:
                data = f_.readlines()
        driver_dict = {"graphics":Gfx_string,"bt":Bt_string,"wlan":Wlan_string,
                       "gmm":gmm_string,"avstream":avstream_string,
                       "csme":csme_string,"me":csme_string,"txei":txei_string,
                       "sg":SG_string,"gpio":gpio_string,"i2c":i2c_string,
                       "ish":ish_string,"ith":ith_string, "gna":gna_string,
                       "gfx":Gfx_string}                                        #initialize the dictionary for driver name in token & driver name in device manager
        if "avstream" in driver_name.lower() or "sky cam" in driver_name.lower()\
                or "skycam" in driver_name.lower():
            driver_name = "avstream"

        driver_flag = False
        for driver_item in list(driver_dict.keys()):                                  #Iterate the driver_item in driver_dict.keys()
            if driver_item in driver_name.lower():
                for item in data:
                    if driver_dict.get(driver_item).strip().lower() in \
                       item.strip().lower():
                        driver_flag = True

        if True == driver_flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s driver is found"
            " in device manager"%driver_name, test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log info message to the log file
            return "found"
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s Driver is"
            " not found in device manager or %s Driver name in incorrect"
            %(driver_name, driver_name), test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log warning message to the log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return False
################################################################################
# Function Name : driver_version
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This functions gives the driver version installed currently
# Return Value  : True/False
################################################################################


def driver_version(driver_name, test_case_id, script_id, log_level="ALL",
                   tbd=None):

    try:
        if "gmm" in driver_name.lower():                                        # checks if driver is gmm
            logfile = script_id.split(".")[0]+"_driver_details.txt"             # assigning a name for the log
            gmm_hwid = utils.ReadConfig("Install_Drivers","gmm_hw_id")          # reads the hardware id of the gmm driver from config file
            devcon_path = utils.ReadConfig("Install_Drivers","devcon_path")
            for item in [devcon_path,gmm_hwid]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Config.ini value not present", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  #Writing log warning message to the log file
                    return False
                else:
                    pass
            os.chdir(devcon_path)
            driver_output = os.system("devcon_x64.exe drivernodes"+ " " +
                        '"'+gmm_hwid+'"'+' > '+logfile)                         # executes the command to get the driver details and stores in log file in toolpath
            with open(logfile,"r") as f:                                        # opens the log from toolpath and reads
                for line in f:
                    if "Driver version" in line:
                        library.write_log(lib_constants.LOG_INFO, "INFO: GMM "
                        "%s"%line, test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         #Checks for the driver version in the log created and returns True if found
                        return True
                    else:
                        pass
        elif "gna" in driver_name.lower():                                      # checks if driver is gmm
            logfile = script_id.split(".")[0]+"_driver_details.txt"             # assigning a name for the log
            gna_hwid = utils.ReadConfig("Install_Drivers","gna_hw_id")          # reads the hardware id of the gmm driver from config file
            devcon_path = utils.ReadConfig("Install_Drivers","devcon_path")
            for item in [devcon_path,gna_hwid]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Config.ini value not present", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  #Writing log warning message to the log file
                    return False
                else:
                    pass
            os.chdir(devcon_path)
            driver_output = os.system("devcon_x64.exe drivernodes"+ " " +
                        '"'+gna_hwid+'"'+' > '+logfile)                         # executes the command to get the driver details and stores in log file in toolpath
            with open(logfile,"r") as f:                                        # opens the log from toolpath and reads
                for line in f:
                    if "Driver version" in line:
                        library.write_log(lib_constants.LOG_INFO, "INFO: GNA "
                        "%s"%line, test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         #Checks for the driver version in the log created and returns True if found
                        return True
                    else:
                        pass

        elif "avstream" in driver_name.lower() or \
             "skycam" in driver_name.lower() or \
             "sky cam" in driver_name.lower():                                  #If avstream or skycam is the driver
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Assigning a name for the log
            avstream_hwid = utils.ReadConfig("Install_Drivers",
                                             "avstream_hw_id")                  #Extracting avstream or skycam driver hardware id from config file
            devcon_path = utils.ReadConfig("Install_Drivers", "devcon_path")    #Extracting devcon path from config file

            if "FAIL:" in [avstream_hwid, devcon_path]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to get the config entry for avstream_hwid and devcon_path from"
                " config file", test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 #Writing log warning message to the log file
                return False
            else:
                pass

            os.chdir(devcon_path)
            os.system("devcon_x64.exe drivernodes" + " " +
                      '"'+avstream_hwid+'"'+' > '+logfile)                      #Executing the command for to get the driver details and stores in log file in devcon path
            with open(logfile, "r") as f:                                       #Opens the log from toolpath and reads
                for line in f:
                    if "Driver version" in line:
                        temp = line.strip()                                     #Removing white spaces
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                        "AVstream %s"%temp, test_case_id, script_id, "None",
                        "None", log_level, tbd)                                 #Writing log_info message to the log file
                        return True
                    else:
                        pass

        elif "gpio" in driver_name.lower():                                     #If gpio is the driver
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Assigning a name for the log
            gpio_hwid = utils.ReadConfig("Install_Drivers", "gpio_hw_id")       #Reads the hardware id of the gpio driver from config file
            devcon_path = utils.ReadConfig("Install_Drivers", "devcon_path")    #Read devcon path from config file

            if "FAIL:" in [devcon_path, gpio_hwid]:                             #Store config entries in a list
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            os.chdir(devcon_path)                                               #change directory to devcon path
            driver_output = os.system("devcon_x64.exe drivernodes"+ " " +
                        '"'+gpio_hwid+'"'+' > '+logfile)                        #executes the command to get the driver details and stores in log file in toolpath
            with open(logfile,"r") as f:                                        #opens the log from toolpath and reads
                drive_ver = ""
                for line in f:                                                  #read file
                    if "Driver version" in line:                                #get the driver version
                        drive_ver = line                                        #get the driver version of installed driver
                    else:
                        pass
                library.write_log(lib_constants.LOG_INFO, "INFO: GPIO %s"
                %drive_ver, test_case_id, script_id, "None", "None", log_level,
                tbd)                                                            #Writing log_info message to the log file
                return True

        elif "i2c" in driver_name.lower():                                      #If i2c is the driver
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Appending the script_id log file with _driver_details
            i2c_hwid = utils.ReadConfig("Install_Drivers", "i2c_hw_id")         #Extracting i2c hardware id from config file

            if "FAIL:" in [i2c_hwid]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to get the config entry for i2c_hwid and devcon_path",
                test_case_id, script_id, "None", "None", log_level, tbd)        #Writing log warning message to the log file
                return False
            else:
                pass

            utils.filechangedir(lib_constants.DEVCON_PATH)                      #Changing directory to the devcon path
            os.system("devcon_x64.exe drivernodes" + " " +
                      '"'+i2c_hwid+'"'+' > '+logfile)                           #Executing the command to get the driver details and stores in log file in devcon path

            with open(logfile, "r") as output_file:                             #File operation, opens the log file from devcon path as in read mode and saves in to output_file
                drive_ver = ""
                for line in output_file:                                        #Iterating through the lines
                    if "DriverNode #0" in line:                                 #If driver node #0 in line
                        for constants in range(lib_constants.SEVEN):            #Iterating to next seven lines
                            line = next(output_file)
                            if "Driver version" in line:                        #if driver version in line
                                drive_ver = line.strip()                        #Get the driver version of installed driver

                library.write_log(lib_constants.LOG_INFO, "INFO: I2C %s"
                %drive_ver, test_case_id, script_id, "None", "None", log_level,
                tbd)                                                            #Writing log_info message to the log file
                return True

        elif "sg" in driver_name.lower():                                       #if sg is the token
            logfile = script_id.split(".")[0]+"_driver_details.txt"             #assigning a name for the log
            SG_hwid = utils.ReadConfig("Install_Drivers","SG_hwid")             #reads the hardware id of the sg driver from config file
            devcon_path = utils.ReadConfig("Install_Drivers","devcon_path")     #reads the devocn_path from config file
            for item in [devcon_path,SG_hwid]:                                  #Iterate the loop to throw error if config.ini file entries are not proper
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_INFO,
            "INFO: Config ini value not present",test_case_id,script_id,
                                      "None","None",log_level,tbd)
                    return False
                else:
                    pass
            os.chdir(devcon_path)                                               #change directory to devcon_path
            driver_output = os.system("devcon_x64.exe drivernodes"+ " " +
                        '"'+SG_hwid+'"'+' > '+logfile)                          #executes the command to get the driver details and stores in log file in toolpath
            with open(logfile,"r") as f:                                        #opens the log from toolpath and reads
                for line in f:                                                  #read each line
                    if "Driver version" in line:                                #if driver version is present in the line
                        library.write_log(lib_constants.LOG_INFO,"INFO: "
                        "SG %s"%line,test_case_id,script_id,"None","None",
                                          log_level,tbd)                        #checks for the driver version in the log created and returns True if found
                        return True
                    else:
                        pass

        elif "ish" in driver_name.lower():                                      #If ish is the driver
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Assigning a name for the log
            ish_hwid = utils.ReadConfig("Install_Drivers", "ish_hwid")          #Reads the hardware id of the ish driver from config file

            if "FAIL:" in ish_hwid:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                                  script_id, "None", "None", log_level, tbd)    #Writing log warning message to the log file
                return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            os.chdir(lib_constants.DEVCON_PATH)                                 #Change directory to devcon_path
            cmd = lib_constants.device_info + " " + '"'+ish_hwid+'"'+' > ' +\
                  logfile                                                       #Get the device info from device manager
            cmd_to_run = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True,
                                          stdin=subprocess.PIPE)                #Executes the command to get the driver node details and stores in log file in toolpath

            if "" != cmd_to_run.communicate()[0]:                               #Checks if the command is executed successfully
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to execute the command to get the drivenodes using devcon "
                "tool", test_case_id, script_id, "None", "None", log_level, tbd)#Writing log warning info message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command to get"
                " the drivenodes executed successfully using devcon tool",
                test_case_id, script_id, "None", "None", log_level, tbd)        #Writing log info message to the log file

            with open(logfile, "r") as f:                                       #Opens the log from toolpath and read file
                for line in f:                                                  #Read each line
                    if "Driver version" in line:                                #If driver version is present in the line
                        library.write_log(lib_constants.LOG_INFO, "INFO: ISH "
                        "driver version is %s"%line, test_case_id, script_id,
                        "None", "None", log_level, tbd)                         #Writing log info message to the log file
                        return True
                    else:
                        pass

            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "get ish driver version", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #Writing log warning message to the log file
            return False

        elif "ith" in driver_name.lower():
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Assigning a name for the log
            ith_hwid = utils.ReadConfig("Install_Drivers", "ith_hwid")          #Reads the hardware id of the ith driver from config file

            if "FAIL:" in ith_hwid:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                "entry not found under Install_Drivers tag", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag", test_case_id, script_id,
                "None", "None", log_level, tbd)                                 #Writing log info message to the log file

            os.chdir(lib_constants.DEVCON_PATH)                                 #Change curent working directory devcon path
            cmd = lib_constants.device_info + " " + '"' +ith_hwid+'"'+' > ' +\
                  logfile                                                       #Get the device info from device manager
            cmd_to_run = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, shell=True,
                                          stdin=subprocess.PIPE)                #Executes the command to get the driver node details and stores the log file in toolpath

            if "" != cmd_to_run.communicate()[0]:                               #Checks if the command is executed successfully
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to execute the command to get the drivenodes using devcon "
                "tool", test_case_id, script_id, "None", "None", log_level, tbd)#Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Command to "
                "get the drive nodes executed successfully using devcon tool",
                test_case_id, script_id, "None", "None", log_level, tbd)        #Writing log info message to the log file

            with open(logfile, "r") as f:                                       #Opens the log from toolpath and reads
                drive_ver = ""
                for line in f:                                                  #Read file
                    if "Driver version" in line:                                #Get the driver version
                        drive_ver = line                                        #Get the driver version of installed driver
                    else:
                        pass
                library.write_log(lib_constants.LOG_INFO, "INFO:ITH %s"
                %drive_ver, test_case_id, script_id, "None", "None", log_level,
                tbd)                                                            #Writing log info message to the log file
                return True
        else:
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in driver"
        " version due to %s"%e, test_case_id, script_id, "None", "None",
        log_level, tbd)                                                         #Writing exception message to the log file
        return False

################################################################################
# Function Name : win_security_pop_up_handler
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This functions closes the windows security popup
#                 during installation of driver
# Return Value  :  True/False
################################################################################


def win_security_pop_up_handler(test_case_id, script_id, log_level="ALL",
                                tbd=None):                                      #Function calling for to execute windows popup to close the popup during installation

    try:
        cmd2="winsec.exe"                                                       # command to execute windows security pop up handler exeutable
        os.chdir(lib_constants.TOOLPATH)
        out = os.system(cmd2)                                                   #Executing the windows security command
        if not 0 == out:
            library.write_log(lib_constants.LOG_INFO, "INFO: Windows Security "
            "Popup Fail to accept", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #Writing log_info message to the log file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Windows Security "
            "Popup accepted succcessfully", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log_info message to the log file
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return False

################################################################################
# Function Name : bios_set_dptf
# Parameters    : test_case_id, script_id, log_level and tbd
# Functionality : This functions to set the BIOS for dptf driver installation
# Return Value  : True/False
################################################################################


def bios_set_dptf(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        flag = False

        if tbd.upper() in lib_constants.XML_CLI_TBD_PLATFORM:                   #Function calling for to set the dptf option in bios if tbd is in lib_constants.XML_CLI_TBD_PLATFORM
            if lib_constants.THREE == lib_set_bios.\
                xml_cli_set_bios(lib_constants.DPTF_KBL, test_case_id,
                                 script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO: DPFT option "
                "set successful", test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 #Writing log_info message to the log file
                flag = True

        elif tbd.upper() in lib_constants.TBD_PLATFORM:
            if lib_constants.THREE == lib_set_bios.\
                lib_write_bios(lib_constants.DPTF_GLK, test_case_id, script_id,
                               log_level, tbd):                                 #Function calling for to set the dptf option in bios if tbd is glk
                library.write_log(lib_constants.LOG_INFO, "INFO: DPFT option "
                "set successful", test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 #Writing log_info message to the log file
                flag = True

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Not "
            "implemented for this platform", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log warning message to the log file
            flag = False

        if True == flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: DPTF option is set"
            " in bios", test_case_id, script_id, "None", "None", log_level, tbd)#Writing log_info message to the log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: DPTF option"
            " is not set in bios", test_case_id, script_id, "None", "None",
            log_level, tbd)                                                     #Writing log warning message to the log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: due to %s" % e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return False

################################################################################
# Function Name : check_dptf_install
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This functions install the dpft driver
# Return Value  :  True/False
################################################################################


def check_dptf_install(input, test_case_id, script_id, log_level="ALL",
                       tbd="None"):

    if "dptf" == input.lower():                                                 #Dptf driver path is read from config file
        path_driver = utils.ReadConfig("DPTF", "DPTFDrvPath")
        setup_path = utils.ReadConfig("DPTF", "DPTF_Setup_Path")                #Dptf set up path is read from config file
        setup = utils.ReadConfig("DPTF", "Setup")                               #Dptf setup is read from the config file
        command_uninstall = setup + " -s -uninstall"                            #Silent command for uninstalling the driver
        command_install = setup + " -s"                                         #Silent command for installing the driver

        if not os.path.exists(path_driver):                                     #Checks if the driver is already installed. if not it will install
            library.write_log(lib_constants.LOG_INFO, "INFO: DPTF driver is "
            "not installed will be installing now", test_case_id, script_id,
            "None", "None", log_level, tbd)                                     #Writing log_info message to the log file

            os.chdir(setup_path)
            install_out = os.system(command_install)                            #Executes the command for installing the driver
            time.sleep(lib_constants.TEN_SECONDS)                               #Waits unless driver is installed
            if 0 == install_out:                                                #Checks for the command output
                library.write_log(lib_constants.LOG_INFO, "INFO: DPTF driver "
                "installed successfully", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log_info message to the log file
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to install DPTF driver", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: DPTF already "
            "installed, uninstalling now", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log_info message to the log file
            os.chdir(setup_path)                                                #Changes the directory to driver setup path
            uninstall_out = os.system(command_uninstall)                        #Executes the command for uninstallation
            time.sleep(lib_constants.TEN_SECONDS)                               #Waits for 10seconds unless the driver is installed
            shutil.rmtree(path_driver)
            if not os.path.exists(path_driver):                                 #Checks if the drier is successfully uninstalled the existing driver
                library.write_log(lib_constants.LOG_INFO, "INFO: DPTF "
                "uninstalled existing and reinstalling..", test_case_id,
                script_id, "None", "None", test_case_id, tbd)                   #Writing log_info message to the log file

                install_out = os.system(command_install)                        #Reinstalles the latest driver as per the requirement
                if os.path.exists(path_driver):
                    return True                                                 # returns True if the driver installation is successfull
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: DPTF"
                    " failed to install", test_case_id, script_id, "None",
                    "None", log_level, tbd)                                     #Writing log warning message to the log file
                    return False

            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DPTF "
                "failed to uninstalled", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Driver name is "
        "not DPTF", test_case_id, script_id, "None", "None", log_level, tbd)    #Writing log warning message to the log file
        return False

################################################################################
# Function Name : check_esif_install
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This functions install the dpft driver
# Return Value  :  True/False
################################################################################


def check_esif_install(driver, test_case_id, script_id, log_level, tbd):

    if "dptf" == driver.lower():                                                #If dptf is the driver
        path_UI = utils.ReadConfig("DPTF", "DPTFUIPath")                        #Extracitng esif driver path from config file
        setup_path = utils.ReadConfig("DPTF", "UI_Setup_Path")                  #Extracitng setup path of the dptf(ESIF) from config file
        setup = utils.ReadConfig("DPTF", "Setup")                               #Extracitng dptf the setup from the config file

        command_uninstall = setup + " -s -uninstall"                            #Command for uninstalling the driver
        command_install = setup + " -s "                                        #Command for installing the driver

        if not os.path.exists(path_UI):                                         #Checks if the driver is already installed
            os.chdir(setup_path)                                                #Changes the directory to the setup path
            install_out = os.system(command_install)                            #Executes the command for installing
            if 0 == install_out:                                                #If the command returns Zero then driver is installed successfully
                library.write_log(lib_constants.LOG_INFO, "INFO: ESIF driver "
                "installed successfully", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log_info message to the log file
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed"
                " to install ESIF driver", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: ESIF driver "
            "already installed, Uninstalling now", test_case_id, script_id,
            "None", "None", log_level, tbd)                                     #Writing log info message to the log file

            os.chdir(setup_path)                                                #Changes the directory of setup path
            uninstall_out = os.system(command_uninstall)                        #Executes command for uninstalling the driver
            time.sleep(lib_constants.TEN_SECONDS)                               #Waits for 10seconds for executing the command
            if not os.path.exists(path_UI):                                     #Checks for the driver installation path
                library.write_log(lib_constants.LOG_INFO, "INFO: ESIF "
                "uninstalled existing and reinstalling", test_case_id,
                script_id, "None", "None", log_level, tbd)                      #Writing log_info message to the log file

                install_out = os.system(command_install)                        #Installs the driver after uninstallation
                if os.path.exists(path_UI):
                    return True                                                 # returns True if driver is successfully installed
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Failed to install ESIF driver", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  #Writing log warning message to the log file
                return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: ESIF "
                "driver failed to uninstall", test_case_id, script_id, "None",
                "None", log_level, tbd)                                         #Writing log warning message to the log file
                return False
################################################################################


def install_screen_rec(driver, test_case_id, script_id, log_level="All",
                       tbd=None):

    if driver.lower() in "screen_rec":
        setup = utils.ReadConfig("media","screen_rec_exe")
        setup_path = utils.ReadConfig("media","screen_rec_path")
        os.chdir(setup_path)
        if not os.path.exists("C:\Program Files (x86)\screen Capturer Recorder"):
            command = setup + " /silent"
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)                      # execute bat file in subprocess
            exec_out = p.communicate()[0]
            return True
        else:
            return False

################################################################################
# Function Name : ith_bios_settings
# Parameters    : test_case_id, script_id, log_level and tbd
# Return Value  : return True if all bios settings are updated that are
#                 required for ith driver installation
# Purpose       : To set bios options to install ith driver
# Target        : SUT
################################################################################


def ith_bios_settings(test_case_id, script_id, log_level, tbd):

    try:
        # ith_bios = lib_set_bios.lib_write_bios(lib_constants.TRACEHUB,
        #                                        test_case_id, script_id,
        #                                        log_level, tbd)              #Function calling for to enable intel trace hub configuration in bios for KBL platform
        ith_bios = lib_set_bios.xml_cli_set_bios(lib_constants.TRACEHUB,
                                    lib_constants.TRACEHUB, test_case_id,
                                    script_id, log_level, tbd)

        if ith_bios:                                                            #Verifies if the bios settings are updated successfully
            library.write_log(lib_constants.LOG_INFO, "INFO: ITH bios settings "
            "updated successfully in bios", test_case_id, script_id, "None",
            "None", log_level, tbd)                                             #Writing log_info message to the log file
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
            "update ith settings in bios", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #Writing log_info message to the log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in load "
        "bios  settings to enable ith as %s"%e, test_case_id, script_id, "None",
        "None", log_level, tbd)                                                 #Writing exception message to the log file
        return False

