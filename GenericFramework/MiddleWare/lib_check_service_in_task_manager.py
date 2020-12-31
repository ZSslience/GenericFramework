__author__ = "jkmody"

###########################General Imports######################################
import os
import time
################################################################################

############################Local imports#######################################
import lib_constants
import library
import utils
################################################################################

################################################################################
# Function Name : check_service_in_task_manager
# Parameters    : test_case_id, script_id, ostr,log_level,tbd
# Return Value  : Service Name,(True on success, False on failure)
# Functionality : To Check whether a service is running in task manager
################################################################################

def check_service_in_task_manager(test_case_id,script_id,ostr,log_level,tbd):
    token=utils.ProcessLine(ostr)
    service_name,index=utils.extract_parameter_from_token(token,"IF","IS")
    if "CONFIG" in service_name:                                                #Check if service_name is a config var and retrieve its value from config.ini
        (config, section, key) = service_name.split("-")
        service_name = utils.ReadConfig(section, key)
        if "FAIL" in service_name:
            library.write_log(lib_constants.LOG_INFO,"INFO: Config Entry is not"
                            " updated.", test_case_id,script_id,"none","none",
                              log_level,tbd)
            return False,"None"
        else:
            pass
    else:
        pass
    try:
        if ".EXE" in service_name.upper():
            pass
        else:
            service_name=service_name.upper()+".EXE"

        flag_check=False
        services = os.popen('tasklist /v').read().strip().split('\n')           #Getting the list of services available in task manager
        for i in range(len(services)):
            if service_name.lower() in services[i].lower():                     #checking if service available in task manager
                service=services[i].lower()
                flag_check=True
                break
            else:
                pass
        time.sleep(lib_constants.TEN_SECONDS)
        if True == flag_check:
            if "not responding" in service:                                     #Checking If service is not responding
                library.write_log(lib_constants.LOG_INFO,"INFO: %s is Not "
                            "Responding"%str(service_name), test_case_id,
                                  script_id,"none","none",log_level,tbd)
                return False,service_name
            elif "running" in service:                                          #Checking If service is running
                return True,service_name
            else:
                pass
        elif False == flag_check:                                               #Checking If service is not running
            return False,service_name
        else:
            pass

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
        test_case_id, script_id, "None", "None", log_level, tbd)
    return False,service_name

