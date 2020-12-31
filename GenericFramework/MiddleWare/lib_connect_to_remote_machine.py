__author__ = 'sharadth'
######################Global library############################################
from selenium import webdriver
from SendKeys import SendKeys
import time
import re
import os
##################### Local Library ############################################
import utils
import library
import lib_constants
import lib_boot_to_environment
import lib_read_mebx
################################################################################
# Function Name : extract_token
# Parameters    : token
# Functionality : extract the paramters from token
# Return Value  : Returns param1(connect_type) and param2(medium) to main
#                 function
################################################################################
def extract_token(token,test_case_id,script_id,log_level,tbd):
    regex = "(KVM|WEBUI)+( VIA+ (WIRED LAN|WIRELESS LAN))?"                     # Regex for connect remote machine
    match = re.search(regex,token.upper())                                      # Extract groups from Re
    print(match.group())
    if match != None:                                                           # If RE matches
        connect_type, optional, medium = map(None, match.groups())
        return connect_type,medium
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO : Parameter not handled",
            test_case_id, script_id, "None", "None", log_level, tbd)
        return False, False
################################################################################
# Function Name : boot_to_mebx
# Parameters    : token, script_id, test_case_id, log_level, tbd
# Functionality : To perform correct function as per option
# Return Value  : True on successfully connecting remotely False on faliure in
#                 connection
################################################################################
def boot_to_mebx(script_id, test_case_id, log_level, tbd):
    token =lib_constants.BOOT_TO_MEBX                                           # Boot to mebx environment
    try:
        mebx_cmd_path  = lib_constants.MEBX_FILE_PATH                           # Get mebx file path
        if os.path.exists(mebx_cmd_path):
            library.write_log(lib_constants.LOG_INFO, "INFO:"
                " Mebx_latest.sikuli file is present in sikuli folder",
                test_case_id, script_id, "None", "None", log_level, tbd)
            pass
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Mebx_latest.sikuli"
            " file is not present in sikuli folder", test_case_id, script_id,
            "None", "None", log_level, tbd)
            return False                                                        # Code exists if mebx_latest.sikuli does not exists in sikuli folder

        if lib_boot_to_environment.boot_to_mebx(test_case_id, script_id, log_level, tbd):# Function call to send 'Ctrl+P' key while system is booting to OS which halts the SUT in MEBX page
            time.sleep(lib_constants.FIVE)
            if library.activate_kvm(test_case_id, script_id, log_level, tbd):
                bios_output =lib_read_mebx.read_mebx(test_case_id, script_id,
                                                     token, log_level, tbd)     # Function call to verify MEBx page
                if bios_output:
                    library.write_log(lib_constants.LOG_INFO,"INFO: System "
                    "Booted to %s"%token.upper(),test_case_id,script_id, "None",
                    "None", log_level, tbd)
                    return True                                                 # Returns success if system booted to MEBx page
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO: System "
                    "FAILED to Boot to %s"%token.upper(),test_case_id,script_id,
                    "None", "None", log_level, tbd)
                    utils.write_to_Resultfile("FAIL",script_id)
                    return False                                                # Code exists if system failed to boot to MEBx
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                "activate KVM window", test_case_id, script_id, "None", "None",
                log_level, tbd)
                return False                                                    # Code exists if failed to activate KVM window
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL: Fail to boot to "
            "%s"%token,test_case_id,script_id,"None","None",log_level,tbd)
            utils.write_to_Resultfile("FAIL",script_id)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Fail to boot to"
        " %s"%token, test_case_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : set_mebx_options
# Parameters    : token,script_id,test_case_id, log_level,tbd
# Functionality : To perform correct function as per option
# Return Value  : True on successfully connecting remotely False on faliure in
#                 connection
################################################################################
def set_mebx_options(token, script_id, test_case_id, log_level, tbd):
    try:
        bios_output =lib_read_mebx.read_mebx(test_case_id,script_id,token,
                                            log_level,tbd)                      # Library call for writing the management engine bios variables from bios
        if bios_output != False and None != bios_output :
            library.write_log(lib_constants.LOG_INFO,"INFO: Bios option "
            "successfully set for MEBX", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return True                                                         # Returns true if the bios variables written successful
        else:
            library.write_log(lib_constants.LOG_FAIL,"FAIL: Failed to set bios"
            " option for mebx ", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False                                                        # Returns False if failed to write the bios option
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception occurs in "
        "due to %s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # Exception occurs if failed in reading/error in reading the bios
################################################################################
# Function Name : connect_to_remote_machine
# Parameters    : token,script_id,test_case_id, log_level;tbd
# Functionality : To perform correct function as per option
# Return Value  : True on successfully connecting remotely False on faliure in
#                 connection
################################################################################
def connect_webui(test_case_id, script_id, log_level, tbd ):
    try:
        try:
            browserdriver = webdriver.Chrome(lib_constants.chromedriverpath)    # Check for Chromedriver.exe is present or not
        except Exception as e:
            library.write_log(lib_constants.LOG_INFO,"INFO : Failed to open"
            " browser, put the chromedriver.exe at given location: "
            "C:\Python27\Lib\site-packages\selenium-2.7.0-py2.7.egg\selenium\
            webdriver\chrome\chromedriver.exe", test_case_id, script_id, "None",
            "None", log_level, tbd)
            return False
        webuiurl = utils.ReadConfig("WEBUI","URL")                              # Read config entry for URL
        if 'FAIL:' in webuiurl.upper():
            library.write_log(lib_constants.LOG_INFO,"INFO: Config entry"
                             " missing for URL", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        library.write_log(lib_constants.LOG_INFO,"INFO : Sut URL read from "
                          "config entry is %s"%webuiurl, test_case_id,
                          script_id, "None", "None", log_level, tbd)
        browserdriver.get(webuiurl)                                             # Open the URL in the browser
        if browserdriver.find_element_by_css_selector\
                    (lib_constants.logonbutton):                                # Search Logon Button
            library.write_log(lib_constants.LOG_INFO,"INFO : Logon button found",
            test_case_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : logon button not "
                             "found", test_case_id, script_id, "None", "None",
                             log_level, tbd)
            return False
        time.sleep(lib_constants.TWO)
        SendKeys('''{TAB}{ENTER}''')                                            # Sendkey command for selecting
        time.sleep(lib_constants.TWO)
        SendKeys('''
                    admin
                    {TAB}
                    +admin@98
                    {ENTER}''')                                                 # Sendkey command for loging in
        time.sleep(lib_constants.TWO)
        SendKeys('''{ESC}''')
        time.sleep(lib_constants.TWO)
        if browserdriver.find_element_by_css_selector\
                    (lib_constants.refreshbutton):                              # Search Refresh Button
            library.write_log(lib_constants.LOG_INFO,"INFO : Refresh button "
                              "found, login succesful", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : Refresh button not"
                              " found, login unsuccesful", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception occured"
                         "due to %s"%e, test_case_id, script_id, "None", "None",
                         log_level, tbd)
        return False
################################################################################
# Function Name : connect_to_remote_machine
# Parameters    : token,script_id,test_case_id, log_level;tbd
# Functionality : To perform correct function as per option
# Return Value  : True on successfully connecting remotely False on faliure in
#                 connection
################################################################################
def connect_to_remote_machine(token, test_case_id, script_id, log_level = "ALL",
                              tbd = None):
    try:
        para1, para2 = extract_token(token.upper(),test_case_id,script_id,
                                     log_level,tbd)                             # Extract token
        library.write_log(lib_constants.LOG_INFO,"INFO : Para1 is %s and para2 "
                         "is %s"%(para1,para2), test_case_id, script_id, "None",
                          "None", log_level, tbd)
        if "WEBUI" == para1.upper():                                            # Check for type of remote connection needed to be established
            if boot_to_mebx(script_id, test_case_id, log_level, tbd):           # Boot to mebx
                library.write_log(lib_constants.LOG_INFO,"INFO : Boot to Mebx "
                "successful handled", test_case_id, script_id, "None", "None",
                log_level, tbd)
                if set_mebx_options(token, script_id, test_case_id, log_level,  # Set mebx options
                                    tbd):
                    library.write_log(lib_constants.LOG_INFO,"INFO : Required "
                    "MEBX options set for WebUi", test_case_id, script_id,
                    "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_INFO,"INFO : Failed to "
                    "set MEBX options set for WebUi", test_case_id, script_id,
                    "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO : Failed to Boot"
                " to Mebx page", test_case_id, script_id, "None", "None",
                log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO : Input paramter not "
                              "handled", test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception occured"
                         "due to %s"%e, test_case_id, script_id, "None", "None",
                         log_level, tbd)
        return False
################################################################################
