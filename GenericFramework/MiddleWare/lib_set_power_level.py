__author__ = "jkmody"

###########################General Imports######################################
import os
import time
################################################################################

############################Local imports#######################################
import lib_constants
import library
import utils
import lib_tool_installation

################################################################################
# Function Name : set_power_level
# Parameters    : test_case_id, script_id, ori_token,log_level,tbd
# Return Value  : Power level,value and (True on success, False on failure)
# Functionality : Setting the power level value
################################################################################

def set_power_level(test_case_id,script_id, ori_token, log_level,tbd):
    try:
        token=utils.ProcessLine(ori_token)
        if "LIMIT" in ori_token.upper():                                        #Checking optional parameter limit is present in step or not
            power_limit,index=utils.extract_parameter_from_token(token,"SET",
                                                                 "LIMIT")       #Extracting the power level (PL1/PL2/PL3)
        else:
            power_limit,index=utils.extract_parameter_from_token(token,"SET",
                                                                 "=")           #Extracting the power level (PL1/PL2/PL3)
        value,index=utils.extract_parameter_from_token(token,"=","")
        peci_value=value

        if lib_tool_installation.peci_install_check(test_case_id,script_id,
                                                    log_level,tbd):             #Installing the PECI to0l
            pass
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO:Unable to install "
             "PECI Tool",test_case_id,script_id,"PECI","None",log_level, tbd)   #Write the fail message to log
            return False,power_limit,value

        peci_path = utils.ReadConfig("PECI_TOOL", "InstalledPath")              #Getting the peci tool path from config
        peci_exe = utils.ReadConfig("PECI_TOOL", "Run_Cmd")                     #Getting the peci tool exe from config
        data_lines = ""

        if "PL1" == power_limit:
            peci_index = lib_constants.PL1_INDEX                                #setting the index for PL1
        elif "PL2" == power_limit:
            peci_index = lib_constants.PL2_INDEX                                #setting the index for PL1
        elif "PL3" == power_limit:
            peci_index = lib_constants.PL3_INDEX                                #setting the index for PL1
        else:
            return False,power_limit,value

        library.write_log(lib_constants.LOG_INFO, "INFO: Setting %s = %s W"
                %(str(power_limit),str(peci_value)),test_case_id,script_id,
                          "PECI","None",log_level, tbd)                         #Write the information message to log

        value=int(value)*8                                                      #Power Limit is (Value*1/8) Watt so multiplying it with 8
        value=hex(int(value))[2:].replace("L","")                               #Converting to Hexa from Decimal
        power_value = "00" + "DC8" + str(value)                                 #Time window is 28 seconds so appendig DC8
        power_value_check = "0x" + "DC8" + str(value)
        log_name=script_id.replace(".py",".csv")
        log_path=lib_constants.SCRIPTDIR+"\\"+log_name

        os.chdir(peci_path)

        command = peci_exe +" wrpkgconfig index:"+str(peci_index)+" parameter:0"\
                    "  data:"+str(power_value)+" log:"+log_path+" unattended"   #Command for setting the power level value
        try:
            os.system(command)                                                  #Executing command for setting the power level value
            time.sleep(lib_constants.TEN_SECONDS)                               #waiting for 10 seconds
            os.chdir(lib_constants.SCRIPTDIR)
        except Exception:
            return False,power_limit,value

        if os.path.exists(log_path):                                            #Checking if log file generated or not
            with open(log_path,"r") as f:
                data_lines = f.readlines()                                      #Reading the contents of generated log file
                for line in data_lines:
                    if power_value_check in line:
                        if str(value) in line and "Command passed" in line:     #Checking whether value is successfully set or not
                            return True,power_limit,peci_value
                        else:
                            return False,power_limit,peci_value
                    else:
                        pass
        else:
            return False,power_limit,peci_value
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
            test_case_id, script_id, "None", "None", log_level, tbd)            #Write the error message to log
        return False,"None","None"