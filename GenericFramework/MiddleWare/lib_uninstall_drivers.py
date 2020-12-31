__author__ = 'Ashax/kapilshx/sushil3x/patnaikx/kashokax'
import sys
#reload(sys)                                                                     #setting value to remove all the ascii characters
#sys.setdefaultencoding('utf-8')
################################################################################
# Function Name : Uninstall_drivers
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This checks the driver in device manager
# Return Value  :  True/False
################################################################################
import lib_tool_installation
import library
import lib_constants
import utils
######################### General Imports ######################################
import os
import time
import subprocess
def uninstall_drivers(driver,tc_id, script_id,loglevel= "ALL",tbd = None):      # calls the function for verifying the name in device manager
    try:
        setup = utils.ReadConfig("Uninstall_drivers","setup")                   # reads the driver name from the config file
        setup_command = setup + " -s -uninstall"
        if "graphics" in driver.lower() or "graphic" in driver.lower() or \
                        "gfx" in driver.lower():
            try:
                gfx_setup_name =utils.ReadConfig\
                    ("Uninstall_drivers","gfx_setup_name")                      # reads the gfx_setup from the config file
                gfx_setup_path=utils.ReadConfig\
                    ("Uninstall_drivers","gfx_setup_path")                      ## reads the gfx_setup_path from the config file
                if "FAIL:" in [gfx_setup_name, gfx_setup_path]:
                    library.write_log(lib_constants.LOG_WARNING,
                    "WARNING: Config.ini value for gfx_setup_name & "
                    "gfx_setup_path are not present under [Uninstall_drivers]",
                                      tc_id, script_id, "None", "None",
                                      loglevel, tbd)                           #Writing log warning message to the log file
                    return False
                else:
                    pass
                os.chdir(os.path.join(lib_constants.TOOLPATH, gfx_setup_path))
                setup_command = gfx_setup_name + " -s -uninstall"
                uninstallation_proc = subprocess.Popen(setup_command,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,shell=False,
                                                       stdin=subprocess.PIPE)
                uninstallation_proc.communicate()                               # executes to install the driver in silent mode
                output = uninstallation_proc.returncode                         # checking for the name of the driver
                library.write_log(lib_constants.LOG_INFO,
                "INFO:Driver %s uninstalled"%driver,tc_id,script_id,
                                  "None","None",loglevel,tbd)                   # write msg to log
            except Exception as e:
                output =1
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e,
                              tc_id,script_id,"None","None",loglevel,tbd)       #write error msg to log

        elif "csme" in driver.lower() or "me" in driver.lower():
            try:                                                             # reads the gfx_tool_name from the config file
                csme_setup_path=utils.ReadConfig\
                    ("Uninstall_Drivers","csme_setup_path")                      ## reads the gfx_setup_path from the config file
                os.chdir(os.path.join(lib_constants.TOOLPATH, csme_setup_path))
                csme_setup = utils.ReadConfig("Uninstall_Drivers","csme_setup")
                setup_command = csme_setup + " -s -uninstall"


                uninstallation_proc = subprocess.Popen(setup_command,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,shell=False,
                                                       stdin=subprocess.PIPE)
                uninstallation_proc.communicate()                               # executes to install the driver in silent mode
                output = uninstallation_proc.returncode
                time.sleep(15)# checking for the name of the driver
                library.write_log(lib_constants.LOG_INFO,
                "INFO:Driver %s uninstalled"%driver,tc_id,script_id,
                                  "None","None",loglevel,tbd)                   # write msg to log
            except Exception as e:
                output =1
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e,
                              tc_id,script_id,"None","None",loglevel,tbd)
        elif "txei" in driver.lower():
            try:
                txei_setup_path=utils.ReadConfig\
                    ("Uninstall_drivers","txei_setup_path")                     # reads the txei_setup_path from the config file
                if "FAIL:" in txei_setup_path:                                  # if fail to fetch the config entry for txei setup path
                    library.write_log(lib_constants.LOG_INFO,
                    "INFO: Config value not fetched from tag"
                    " unistall_driver",tc_id,script_id,"None","None",loglevel,
                    tbd)
                    return False
                else:
                    pass
                os.chdir(txei_setup_path)                                       # change the txei driver path
                uninstallation_proc = subprocess.Popen(setup_command,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,shell=False,
                                                       stdin=subprocess.PIPE)
                uninstallation_proc.communicate()                               # execute to uninstall the txei driver
                output = uninstallation_proc.returncode
                library.write_log(lib_constants.LOG_INFO,
                "INFO:Driver %s uninstalled"%driver,tc_id,script_id,
                                  "None","None",loglevel,tbd)                   # write msg to log
            except Exception as e:
                output =1
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e,
                              tc_id,script_id,"None","None",loglevel,tbd)
        elif "gmm" in driver.lower():
            gmm_hwid = utils.ReadConfig("Uninstall_drivers","gmm_hw_id")        # reads hardware id of the gmm driver from config file
            devcon_path = utils.ReadConfig("Uninstall_drivers","devcon_path")   # reads devcon_path from config file
            for item in [gmm_hwid,devcon_path]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_INFO,
                    "INFO: Config ini value not present",tc_id,script_id,
                            "None","None",loglevel,tbd)                         #write msg to log
                    return False
                else:
                    pass
            output = inf_file_uinstallation(gmm_hwid,devcon_path,
                                    driver,tc_id,script_id,loglevel,tbd)        #library function call of inf_file_uinstallation() function
        elif "gna" in driver.lower():
            gna_hwid = utils.ReadConfig("Uninstall_drivers","gna_hw_id")        # reads hardware id of the gmm driver from config file
            devcon_path = utils.ReadConfig("Uninstall_drivers","devcon_path")   # reads devcon_path from config file
            for item in [gna_hwid,devcon_path]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_INFO,
                    "INFO: Config ini value not present",tc_id,script_id,
                            "None","None",loglevel,tbd)                         #write msg to log
                    return False
                else:
                    pass
            output = inf_file_uinstallation(gna_hwid,devcon_path,
                                    driver,tc_id,script_id,loglevel,tbd)        #library function call of inf_file_uinstallation() function
        elif "gpio" in driver.lower():                                          #if gpio is the driver
            gpio_hwid = utils.ReadConfig("Uninstall_Drivers","gpio_hw_id")      #reads the hardware id of the gpio driver from config file
            devcon_path = utils.ReadConfig("Uninstall_Drivers","devcon_path")   #read devcon path from config file
            if "FAIL:" in  gpio_hwid or "FAIL:" in devcon_path:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "not found under Install_Drivers tag ", tc_id, script_id,
                                  "None", "None", loglevel, tbd)                #write info to log file if config entry is missing
                return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Install_Drivers tag ", tc_id, script_id, "None",
                                  "None", loglevel, tbd)                        #write info to log file if config entry is present

            output = inf_file_uinstallation(gpio_hwid,devcon_path,
                                    driver,tc_id,script_id,loglevel,tbd)        #function call to perform driver uninstallation

        elif "i2c" in driver.lower() or "i2c1" in driver.lower():               #if i2c is the driver name
            i2c_hwid = utils.ReadConfig("Uninstall_Drivers","i2c_hw_id")        #reads the hardware id of the i2c driver from config file
            devcon_path = utils.ReadConfig("Uninstall_Drivers","devcon_path")   #read devcon path from config file
            if "FAIL:" in  i2c_hwid or "FAIL:" in devcon_path:                  #if config entry is missing
                library.write_log(lib_constants.LOG_INFO,"INFO: Config ini"
                    "value not present",tc_id,script_id,"None","None",
                    loglevel,tbd)                                               #write to log file
                return False
            else:
                pass
            output = inf_file_uinstallation(i2c_hwid,devcon_path,
                                    driver,tc_id,script_id,loglevel,tbd)        #function call to perform driver uninstallation

        elif "avstream" in driver.lower() or "sky cam" in driver.lower()\
                or "skycam" in driver.lower():
            avstream_hwid = utils.ReadConfig("Uninstall_drivers","avstream_hw_id")# reads hardware id of the avstream driver from config file
            devcon_path = utils.ReadConfig("Uninstall_drivers","devcon_path")   # reads devcon folder path from config file
            for item in [avstream_hwid,devcon_path]:
                if "FAIL:" in item:
                    library.write_log(lib_constants.LOG_INFO,
                        "INFO: Config ini value not present",tc_id,
                         script_id,"None","None",loglevel,tbd)                  #write msg to log
                    return False
                else:
                    pass

            output = inf_file_uinstallation(avstream_hwid,devcon_path,driver,
                                       tc_id,script_id,loglevel,tbd)            #library function call of inf_file_uinstallation() function
        elif "irmt"== driver.lower():                                           #if irmt is the driver to be uninstalled
            iRMT_setup_path = utils.ReadConfig("Uninstall_Drivers",
                                               "iRMT_setup_path")               #read irmt setup path from config entry
            iRMT_setup = utils.ReadConfig("Uninstall_Drivers",
                                               "iRMT_setup")                    #read irmt setup file from config entry
            iRMT_installed_path = utils.ReadConfig("Uninstall_Drivers",
                                               "iRMT_installed_path")           #read the path created after irmt installation from config entry
            iRMT_cmd = iRMT_setup + " " +"/x"+" "+"/s"                          #cmd to uninstall irmt
            if "FAIL:" in iRMT_setup_path or "FAIL:" in iRMT_setup or \
                "FAIL:" in iRMT_installed_path :
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "not found under Uninstall_Drivers tag ", tc_id, script_id,
                                  "None", "None", loglevel, tbd)                #write info to log file if config entry is missing
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found under Uninstall_Drivers tag ", tc_id, script_id, "None",
                                  "None", loglevel, tbd)                        #write info to log file if config entry is present
            try:
                os.chdir(iRMT_setup_path)                                       #change directory to irmt setup path
                uninstallation_proc = subprocess.Popen(iRMT_cmd,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,shell=False,
                                                       stdin=subprocess.PIPE)
                if "" == uninstallation_proc.communicate()[0]:                  #executes cmd to uninstall the driver in silent mode and verifies whether the command is executed successfully
                    if os.path.exists(iRMT_installed_path):                     #if the installation path contents exists even after executing uninstallation command then return false
                        return False
                    else:
                        return True                                             #confirms irmt uninstallation by verifying the installed path contents are removed successfully after executing the command
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                    "execute the command for irmt uninstallation", tc_id,
                                      script_id, "None", "None" ,loglevel, tbd) #write message to log file if there is an error in executing uninstallation command
                    return False
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
                "iRMT uninstallation due to %s"%e, tc_id, script_id, "None",
                                  "None", loglevel, tbd)                        #write exception message to log file
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Invalid Input",
                              tc_id,script_id,"None","None",loglevel,tbd)       #write msg to log
            return False

        try:
            if 1 != output  :
                library.write_log(lib_constants.LOG_INFO,
                    "INFO: %s Driver is uninstalled in device"
                    " manager"%driver,tc_id,script_id,"None","None",loglevel,tbd)#write msg to log
                return  True                                                    # returns true if driver listed in device manager successfully
            else:
                library.write_log(lib_constants.LOG_INFO,
                "INFO:Driver %s fail to install"%driver,tc_id,script_id,
                                  "None","None",loglevel,tbd)
                return False                                                    # if not return code then driver failed to install
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
                    "inf_file_installation functiondue to %s"%e,
                              tc_id,script_id,"None","None",loglevel,tbd)       #write error msg to log
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Due to %s"%e,tc_id,
                          script_id,"None","None",loglevel,tbd)
        return False
################################################################################
# Function Name : inf_file_installation
# Parameters    : driver_setup_path,driver_hwid,devcon_path,loglevel,tbd
# Functionality : Funciton for .inf file installation
# Return Value  : On success return True, False on failure
################################################################################
def inf_file_uinstallation(driver_hwid,devcon_path,driver,tc_id,script_id,
                           loglevel= "ALL",tbd = None):
    try:
        os.chdir(devcon_path)
        logfile = script_id.split(".")[0]+"_driver_all_details.txt"             # assigning a name for the log
        driver_info_output = os.system("devcon_x64.exe drivernodes"+ " " +
                    '"'+driver_hwid+'"'+' > '+logfile)                          # executes the command to get the driver details and stores in log file in toolpath
        driver_oem_flag = 0
        with open(logfile,"r") as f:                                            # opens the log from toolpath and reads
            for line in f:
                if "Inf file" in line:
                    line = line.split("\\")[-1].strip("\n")
                    driver_oem_inf = line
                    driver_oem_flag = 1
                else:
                    pass
        if 0 == driver_oem_flag :
            library.write_log(lib_constants.LOG_INFO,"INFO:Logfile is not "
                       "generated or oem file name is not present in the file",
                tc_id,script_id,"None","None",loglevel,tbd)                     #write msg to log
            return False
        else:
            pass
        inf_command = "-f -d"
        os.chdir(lib_constants.TOOLPATH)
        if "gna" == driver.lower():
            driver_cmd = "PnPutil.exe /delete-driver" + " " + driver_oem_inf\
                         + " " + "/uninstall"
        else:
            driver_cmd = "PnPutil.exe"+ " "+inf_command+" "+driver_oem_inf       # command for installing driver - inf file
        output = subprocess.Popen(driver_cmd,stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,shell=False,
                                  stdin=subprocess.PIPE)
        time.sleep(lib_constants.SUBPROCESS_RETURN_TIME)
        output.communicate()                                                    # executes inf command to install the driver in silent mode
        output = output.returncode

        os.chdir(devcon_path)
        driver_remove_output = os.system("devcon_x64.exe remove"+ " " +
                    '"'+driver_hwid+'"')                                        # executes the command to get the driver details and stores in log file in toolpath

        os.chdir(devcon_path)
        driver_rescan_cmd = "devcon_x64.exe rescan"+ " " + '"'+driver_hwid+'"'
        verify_proc = subprocess.Popen(driver_rescan_cmd,
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False,
                                       stdin=subprocess.PIPE)              #Esecute the driver_rescan_command through subprocess method

        return output

    except Exception as e:
        output = 1                                                              #if exception occur in execution of command then set output to 1
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception in "
                "inf file installation for driver %s due to %s"%(e,driver),
                        tc_id,script_id,"None","None",loglevel,tbd)             #write msg to log
        return output
################################################################################
################################################################################
# Function Name : verify_dev_manager
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This checks the driver in device manager
# Return Value  :  True/False
################################################################################
def verify_dev_manager(driver_name,tc_id,script_id,loglevel = "ALL",tbd = None):# calls the function for verifying the driver name in device manager
    import wmi
    import codecs
    try:
        Gfx_string = utils.ReadConfig("Uninstall_drivers","Gfx_name_in_devmgmt")# reads the driver name from the config file
        Bt_string = utils.ReadConfig("Uninstall_drivers","Bt_name_in_devmgmt")
        Wlan_string = utils.ReadConfig("Uninstall_drivers","Wlan_name_in_devmgmt")
        gmm_string = utils.ReadConfig("Uninstall_drivers","gmm_name_in_devmgmt")
        gna_string = utils.ReadConfig("Uninstall_drivers","gna_name_in_devmgmt")
        avstream_string = utils.ReadConfig("Uninstall_drivers",
                                           "avstream_name_in_devmgmt")
        csme_string = utils.ReadConfig("Uninstall_Drivers","csme_name_in_devmgmt")
        txei_string = utils.ReadConfig("Install_Drivers","txei_name_in_devmgmt")
        SG_string = utils.ReadConfig("Uninstall_Drivers","SG_name_in_devmgmt")
        gpio_string = utils.ReadConfig("Uninstall_Drivers","gpio_in_devmgmt")
        i2c_string = utils.ReadConfig("Uninstall_Drivers","i2c_in_devmgmt")
        ish_string = utils.ReadConfig("Uninstall_Drivers","ish_in_devmgmt")
        '''lst= []
        c = wmi.WMI ()                                                          # executes the wmi query to get the  device name from the device manager
        for device in c.Win32_PnPEntity():
            print str(device.Description)
            str(device.Description).replace("\xae","(R)")
            if device.Description != None:
                lst.append(str(device.Description))                             #all device list of device manager stored in the lst
            else:
                pass'''
        dev_listfile = library.get_entire_device_list(script_id,tc_id,loglevel,tbd)
        if False == dev_listfile:
            return False
        else:
            with open(dev_listfile,"r") as f_:
                data = f_.readlines()
        driver_dict = {"graphics":Gfx_string,"bt":Bt_string,
                "wlan":Wlan_string,"gmm":gmm_string,"avstream":avstream_string,
                       "csme":csme_string,"me":csme_string,"txei":txei_string,
                       "sg":SG_string,"gpio":gpio_string,"i2c":i2c_string,
                       "ish":ish_string,"gna":gna_string,"gfx":Gfx_string}      #initialize the dictionary for driver name in token & driver name in device manager
        if "avstream" in driver_name.lower() or "sky cam" in driver_name.lower()\
                or "skycam" in driver_name.lower():
            driver_name = "avstream"
        else:
            pass
        driver_flag = False
        for driver_item in list(driver_dict.keys()):                                  #Iterate the driver_item in driver_dict.keys()
            if driver_item.lower() in driver_name.lower():
                for item in data:
                    if driver_dict.get(driver_item).strip() in item.strip():    # checks for the driver name if it is present in the wmi list created from device manager
                        driver_flag = True
                    else:
                        pass
            else:
                pass
        if True == driver_flag:
            library.write_log(lib_constants.LOG_INFO,
                "INFO:%s Driver is found in device manager"%(driver_name),
                  tc_id,script_id,"None","None",loglevel,tbd)
            return "found"
        else:
            library.write_log(lib_constants.LOG_INFO,
                "INFO:%s Driver is not found in device manager "
            "or %s Driver name in incorrect"%(driver_name,driver_name),
                  tc_id,script_id,"None","None",loglevel,tbd)
            return False
    except Exception as e:                                                      #write error msg to log
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
                "verify_dev_manager due to %s"%e,tc_id,
                          script_id,"None","None",loglevel,tbd)
        return False
################################################################################
# Function Name : uninstall_dptf
# Parameters    : tc_id,script_id,loglevel,tbd
# Functionality : This function unistalls the DPTF driver
# Return Value  : True/False
################################################################################
def uninstall_dptf(input,tc_id,script_id,loglevel,tbd):
    try:
        if "dptf" == input.lower():
            path_driver = utils.ReadConfig("DPTF", "DPTFDrvPath")                   # driver installed path reading from config file
            dptf_setup_path = utils.ReadConfig("DPTF", "DPTF_Setup_Path")           # driver setup path reading from config file
            setup = utils.ReadConfig("DPTF", "Setup")                               # setup file extension reading from config file
            path_ui = utils.ReadConfig("DPTF", "DPTFUIPath")                        # ESIF driver installed path reading from config filr
            ui_setup_path = utils.ReadConfig("DPTF", "UI_Setup_Path")               # ESIF driver setup path reading from config file
            command_uninstall = setup + " -s -uninstall"                            # command for silent uninstalling driver
            if not os.path.exists(path_driver):                                     # checks if the driver is already installed by verifying the installed path
                library.write_log(lib_constants.LOG_INFO,"INFO: DPTF driver is not "
                "installed ",tc_id,script_id,"None","None",loglevel,tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: DPTF already "
                "installed. Uninstalling now..",tc_id,script_id,"None","None",
                                 loglevel,tbd)
                os.chdir(dptf_setup_path)
                uninstall_out = os.system(command_uninstall)                        # if the installed path is present then it executes the silent uninstallation command
                time.sleep(lib_constants.TEN_SECONDS)                               # waits/Sleeps for 10 seconds for completion of driver installation
                if not os.path.exists(path_driver):
                    library.write_log(lib_constants.LOG_INFO,"INFO: DPTF "
                    "uninstalled",tc_id,script_id,"None","None",loglevel,tbd)
                else:
                    library.write_log(lib_constants.LOG_FAIL,"FAIL: DPTF failed to"
                    " uninstalled",tc_id,script_id,"None","None",loglevel,tbd)
                    return False

            if not os.path.exists(path_ui):                                         # checks for the esif driver installation path
                library.write_log(lib_constants.LOG_INFO,"INFO: ESIF driver"
                "is not installed",tc_id,script_id,"None","None",
                loglevel,tbd)
                return False
            else:
                os.chdir(ui_setup_path)
                uninstall_out = os.system(command_uninstall)                        # executes silent uninstallation if the driver is installed
                time.sleep(lib_constants.TEN_SECONDS)
                if not os.path.exists(path_ui) :
                    library.write_log(lib_constants.LOG_INFO,"INFO: ESIF "
                    "uninstalled ",tc_id,script_id,"None","None",loglevel,tbd)
                    return True                                                     # returns True if both DPTF and ESIF driver package is installed successfully
                else:
                    library.write_log(lib_constants.LOG_FAIL,"FAIL: ESIF failed to"
                    " uninstalled",tc_id,script_id,"None","None",loglevel,tbd)
                    return False

        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL: Driver name is not "
            "DPTF",tc_id,script_id,"None","None",loglevel,tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e,tc_id,
                          script_id,"None","None",loglevel,tbd)
        return False
################################################################################
# Function Name : driver_version_after_uninstall
# Parameters    : driver_name, test_case_id, script_id, log_level and tbd
# Functionality : This functions gives the "driver version" or "No drivernodes
#                 for device" after uninstallation
# Return Value  : True on successful action, False otherwise
################################################################################


def driver_version_after_uninstall(driver_name, test_case_id, script_id,
                                   log_level="ALL", tbd=None):
    try:
        if "avstream" in driver_name.lower() or \
           "skycam" in driver_name.lower() or \
           "sky cam" in driver_name.lower():                                    #If avstream or skycam is the driver
            logfile = script_id.split(".")[0] + "_driver_details.txt"           #Assigning a name for the log
            avstream_hwid = utils.ReadConfig("Install_Drivers",
                                             "avstream_hw_id")                  #Extracting avstream or skycam driver hardware id from config file
            devcon_path = utils.ReadConfig("Install_Drivers", "devcon_path")    #Extracting devcon path from config file

            if "FAIL:" in [avstream_hwid, devcon_path]:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " the config entry for avstream_hwid and devcon_path from "
                "config file", test_case_id, script_id, "None", "None",
                log_level, tbd)                                                 #Writing log_info message to the log file
                return False
            else:
                pass

            utils.filechangedir(devcon_path)
            os.system("devcon_x64.exe drivernodes" + " " +
                      '"'+avstream_hwid+'"'+' > '+logfile)                      #Executing the command for to get the driver details and stores in log file in devcon path

            with open(logfile, "r") as output:                                  #File operation
                for line in output:
                    if "NO DRIVERNODES FOUND FOR DEVICE" in line.upper():
                        return True
                    else:
                        pass
                return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: parameter driver "
            "not handled", test_case_id, script_id, "None", "None", log_level,
            tbd)                                                                #Writing log_info message to the log file
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
        test_case_id, script_id, "None", "None", log_level, tbd)                #Writing exception message to the log file
        return False