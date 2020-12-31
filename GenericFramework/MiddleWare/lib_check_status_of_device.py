__author__ = 'kapilshx'
########################## General Imports #####################################
import os
import platform
######################### Local Imports ########################################
import lib_constants
import library
import utils
################################################################################
# Function Name : check_status_of_device
# Parameters    : device_name, test_case_id, script_id , loglevel,tbd
# Functionality : returns True if required device with no yellow bang is found
#                 and False otherwise
# Return Value  : To verify yellow bang for particular device in device manager
################################################################################
def check_status_of_device(device_name,test_case_id,script_id,loglevel="ALL",
                           tbd=None):


    try:
        if "CONFIG-" in device_name:                                            # Check if device_name is in config.ini
            (config, section, key) = device_name.split("-")
            device_name = utils.ReadConfig(section, key)

        req_string = search_parent(device_name,test_case_id,script_id,loglevel,
                                   tbd)
        if (False != req_string and 2 != req_string):                           #if parent device name is given as input
            library.write_log(lib_constants.LOG_INFO,"INFO: given input "
            "device '%s' : is found as parent device in device"
            " manager"%(device_name),test_case_id,script_id,"None","None",
                              loglevel,tbd)
            if search_child_under_parent(req_string,
                                         test_case_id,script_id,loglevel,tbd):  #if child device is not having yellow bang in device manager
                return True
            else:                                                               #if return value of search_child_under_parent() is False
                return False
        elif (2 == req_string):                                                 #if child device name is given as input
            ret = library.check_device_status(device_name,
                                            test_case_id,script_id,loglevel,tbd)
            if (2 ==ret):                                                       #if given input device name is not found in device manager
                return 2
            elif(False == ret):                                                 #if child device is having yellow bang in device manager
                return False
            else:                                                               #if child device is not having yellow bang in device manager
                return True
        else:                                                                   #if given input device name is not found in device manager
            return False
    except Exception as e:                                                      #error msg to write_log() if exception in function check_status_of_device() occurs
        library.write_log(lib_constants.LOG_ERROR,"ERROR:Exception"
        " in checking yellow bang due to %s . "%e,test_case_id,
        script_id,"None","None",loglevel,tbd)
        return False
################################################################################
# Function Name : search_child_under_parent
# Parameters    : req_string, test_case_id, script_id , loglevel,tbd
# Functionality : returns True if required device under parent with no yellow
#                 bang is found
#                 and False otherwise
# Return Value  : To verify yellow bang for particular device under parent
#                 in device manager
################################################################################
def search_child_under_parent(req_string,
                              test_case_id,script_id,loglevel="ALL",tbd=None):
    try:
        result_path = os.getcwd()
        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path,'devcon')
        child_dev_list =  get_child_device_in_devicemanager(test_case_id,
                                        script_id, req_string, loglevel, tbd)   # TO get device manager child device list and save it in text file

        os.chdir(result_path)
        if child_dev_list:                                                      # if return value from get_child_device_in_devicemanager() is true
            library.file_text_to_upper(devcon_path,
                                        "child_device_list.txt",loglevel , tbd)
            devcon_file_path_upper_child = os.path.join(path,
                                        'devcon\child_device_list_upper.txt')
        else:                                                                   # if child device list command is not executed
            library.write_log(lib_constants.LOG_INFO,
            "INFO : Child device list Command not executed ",
            test_case_id, script_id,"None", "None", loglevel, tbd)
            return False

        with open(devcon_file_path_upper_child,"r") as f:                       #To open the child device list file in read mode
            lines = f.readlines()
            for line in lines:                                                  #To iterate the no. of child present in child device list under given parent device
                if "MATCHING DEVICE" in line:
                    break
                child_name = line.split(':')[1].strip()
                ret = library.check_device_status(child_name,
                                        test_case_id,script_id,loglevel,tbd)
                if (False == ret):                                              #if child is having yellow bang in device manager
                    return False
            if (True == ret):                                                   #if child is having no yellow bang in device manager
                return True

    except Exception as e:                                                      #write error msg to log if exception in search of child under parent
        library.write_log(lib_constants.LOG_ERROR,
        "ERROR: Exception in search of child "
        "under parent as %s "%e,test_case_id,
        script_id,"None","None",loglevel,tbd)
        return False
################################################################################
# Function Name : search_parent
# Parameters    : device_name, test_case_id, script_id ,loglevel,tbd
# Functionality : returns True if required device is found as parent
#                 device in device manager and False otherwise
# Return Value  : To verify input device is parent device or not
#                 in device manager
################################################################################
def search_parent(device_name,test_case_id,script_id,loglevel="ALL",tbd=None):
    try:
        result_path = os.getcwd()
        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path,'devcon')
        dev_list = library.device_list_under_class_devmgmt("classes",
                                                           loglevel,tbd)        # TO get device manager Parent device list and save it in text file
        os.chdir(result_path)
        if dev_list:                                                            # if return value from device_list_under_class_devmgmt() is true
            library.file_text_to_upper(devcon_path, "device_list.txt",loglevel
                                       , tbd)
            devcon_file_path_upper = os.path.join(path,
                                            'devcon\device_list_upper.txt')
            return_line_parent=library.\
                return_line_from_log(devcon_file_path_upper,device_name,
                                     loglevel , tbd)
            if not return_line_parent:                                          # if return value from return_line_from_log() is False
                library.write_log(lib_constants.LOG_INFO,
                "INFO: Given input device is not parent device in Device"
                " manager ", test_case_id, script_id,"None", "None", loglevel,
                                  tbd)
                return 2

            elif 2 == return_line_parent:                                       # if return value from return_line_from_log() is 2
                library.write_log(lib_constants.LOG_INFO, "INFO : Parent"
                " Device list  Not found in Device manager ", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
                return False
            else:                                                               # check if Parent device is present in Device manager
                if device_name.upper() in  return_line_parent:
                    req_string=return_line_parent.split(" ")
                    req_string=req_string[0]
                    return req_string
                else:                                                           # if Parent Device list  Not present in Device manager
                    library.write_log(lib_constants.LOG_INFO, "INFO:Parent"
                    " Device Not found in Device manager ",test_case_id,
                                      script_id, "None", "None", loglevel, tbd)
                    return 2
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:Parent"
            " device list Command not executed ",test_case_id,script_id,"None",
                              "None", loglevel, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "search of parent device name as :%s or may be there is no file "
        "exist in this location c:\Automation\tools\devcon\devcon.exe",
        test_case_id, script_id,"None", "None", loglevel, tbd)                  # write error msg to log if device not found in dev. manger
        return False
################################################################################
# Function Name : get_child_device_in_devicemanager
# Parameters    : child_device_name, test_case_id, script_id , loglevel,tbd
# Functionality : returns True if child device list is generated successfully
#                 and False otherwise
# Return Value  : To generate the child device list of device manager
################################################################################
def get_child_device_in_devicemanager(test_case_id, script_id,
                child_device_name, loglevel="ALL", tbd="None"):

    try:
        path = lib_constants.TOOLPATH
        devcon_path = os.path.join(path, 'devcon')                              #Tool path to devcon tool
        dev_listfile = os.path.join(devcon_path, 'child_device_list.txt')       #txt file joining with path
        os.chdir(devcon_path)
        if dev_listfile in path:                                                #check for list file in path
            os.remove(dev_listfile)                                             #remove the file if it exists
        else:
            pass

        if "64" in platform.uname()[4]:                                         #if platform is 64 bit
            devcon = 'devcon_x64.exe'                                           #use devcon 64 bit exe
            devcon_cmd = os.path.join(devcon_path, devcon)                      #join path with exe
            cmd = devcon_cmd + " find " + "="+child_device_name + \
                  " > child_device_list.txt"                                    #run the command

        else :
            devcon = 'devcon.exe'                                               #for other platform use devcon exe
            devcon_cmd = os.path.join(devcon_path,devcon)                       #join path and exe
            cmd = devcon_cmd + " find " + "=" + child_device_name + \
                  " > child_device_list.txt"                                    #list file

        temp = os.system(cmd)                                                   #run command using os.system

        if 0 == temp:
            return True                                                         #return true if successful
        else:
            return False                                                        #return false if not successful
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
         "generating child device list as: %s"%e, test_case_id,
                        script_id, "None", "None",loglevel, tbd)
        return False
################################################################################











