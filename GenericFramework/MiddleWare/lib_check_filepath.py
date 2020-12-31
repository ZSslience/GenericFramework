###########################Global Library imports###############################
import sys
import os
import time
###########################Local Library imports################################
import library
import lib_constants
import utils
################################################################################


################################################################################
# Function Name : check_filepath
# Parameters    : test_case_id ,script_id,ostr,log_level,tbd
# Return Value  : Returns True if "PASS" and False if "FAIL"
# Functionality : Checking if filepath exists or not
################################################################################

def check_filepath(test_case_id,script_id,ostr,loglevel,tbd):                   #Function definition for checking filepath existence
    token=utils.ProcessLine(ostr)
    filepath,index=utils.extract_parameter_from_token(token,"IF","EXIST")       #Extracting filepath
    if "config" in filepath:
        file_name = filepath.split('-')[1]
        filepath = filepath.split('-')[2]
        if "FAIL:" in [filepath, file_name]:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Config entry for filepath is incorrect",
                test_case_id, script_id, "None", "None", loglevel, tbd=None)   #fail if config entry is missing
            return False
    if "\"" in filepath:
        filepath=filepath.replace("\"","")
    elif "'" in filepath:
        filepath=filepath.replace("'","")
    else:
        pass

    if os.path.exists(filepath):                                                #Checking whether path exists or not
        return True,filepath
    else:
        return False,filepath