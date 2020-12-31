__author__ = 'kapilshx'
###########################General Imports######################################
import time
import os
import wmi
import glob
import csv
############################Local imports#######################################
import library
import lib_constants
import utils
import lib_start_stop_capture
################################################################################
# Function Name : read_residency
# Parameters    : residency_token,device_name, state,test case id,script id,
#                 loglevel, tbd
# Return Value  : percentage_residency & state on success,False & state on failure
# Functionality : function to read residency status
################################################################################
def read_residency(residency_token,device_name,state,test_case_id,script_id,
                                    loglevel="ALL",tbd=None):
    try:
        if "FROM" in residency_token.upper():
            step_num = ""
            residency_list = residency_token.upper().split(" ")
            state,end_pos = library.\
                extract_parameter_from_token(residency_list,"IN","FROM",
                                             loglevel,tbd)                      #extract parameter to get the device state in token
            step_num,pos = library.extract_parameter_from_token(residency_list,
                                                "STEP","LOG",loglevel,tbd)      #extract parameter to get the device name in token
            log_file_path = utils.read_from_Resultfile(step_num)
        else:
            state_capture = ""

            if os.path.exists(lib_constants.SCRIPTDIR+os.sep +"SOCWatchOutput.csv"):
                os.remove(lib_constants.SCRIPTDIR+os.sep +"SOCWatchOutput.csv")
            else:
                pass

            if "S3" == state:                                                   #if S3 is present in state variable
                state_capture = "S-STATE"
            elif "D" in state.upper():                                          #if D (i.e. - D- state residency) in state variable
                state_capture = "D-STATE"
            status = "START"
            if True == lib_start_stop_capture.C_P_S_T_state_capture(status,
                        state_capture,test_case_id, script_id,loglevel, tbd):
                time.sleep((lib_constants.SHORT_TIME)*2)                        #2 min log generation time delay
                status = "STOP"
                if True == lib_start_stop_capture.C_P_S_T_state_capture(status,
                        state_capture,test_case_id,script_id,loglevel, tbd):
                    pass
                else:
                    return False,state
            else:
                return False,state
            time.sleep((lib_constants.TWENTY)*3)
            if os.path.exists\
                        (lib_constants.SCRIPTDIR+os.sep +"SOCWatchOutput.csv"):
                log_file = script_id.split(".")[0]+"_"+"SOCWatchOutput.csv"     # log name is defined
                log_file_path = lib_constants.SCRIPTDIR + os.sep + log_file
                if os.path.exists(log_file_path):
                    os.remove(log_file_path)                                    # removes the old/existing log
                else:
                    pass
                os.chdir(lib_constants.SCRIPTDIR)
                time.sleep(lib_constants.FIVE_SECONDS)
                os.rename\
            (lib_constants.SCRIPTDIR+os.sep +"SOCWatchOutput.csv",log_file_path)# renames the new log with script id
                time.sleep(lib_constants.TWO)
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                    "generate the log from Socwatch tool",test_case_id,script_id,
                                  "Socwatch_tool","None",loglevel,tbd)
        residency_flag = False
        percentage_residency  = ""
        if os.path.exists(log_file_path):
            library.write_log(lib_constants.LOG_INFO, "INFO : "
                "Socwatch log file is present",test_case_id,
                script_id, "Socwatch_tool", "None", loglevel, tbd)              # write info msg to log if SOCWatchOutput.csv file is present
            pass
        else:
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG : "
                "Socwatch log file is not present",test_case_id,
                script_id, "Socwatch_tool", "None", loglevel, tbd)              # write info msg to log if SOCWatchOutput.csv file is not present
            return False,state
        if "S3" in state:                                                       #if S3 is present in state variable
            with open(log_file_path, "rb") as file:                             # open the .csv log_file in read mode for parsing residency
                lines = csv.reader(file)
                for line in lines:                                              #loop to iterate through lines in the file
                    if line != []:
                        if "System S-State (OS) Summary: Residency" in line[0]:                      #if "S State Residency" string found in file
                            line = next(file)                                   #move to next line
                            for line in lines:
                                if "S3" in line[0]:                             #if "S3" string found in file
                                    percentage_residency = \
                                        (line[1].split("%")[0]).strip()         #assign S3 residency value to variable percentage_residency
                                    residency_flag = True                       #if residency parsing is successfull then set the residency_flag to true
                                    break
                                else:                                           #if "S3" string does not found in file then move to next line of file
                                    pass
                        else:                                                   #if "S State Residency" string does not found in file then move to next line of file
                            pass
                    else:
                        pass
        elif "D" in state.upper():                                              #if D (i.e. - D- state residency) in state variable
            state_list = {"d0": lib_constants.COL_TWO,
                "d1": lib_constants.COL_THREE, "d2": lib_constants.COL_FOUR,
            "d3hot": lib_constants.COL_FIVE ,"d3cold": lib_constants.COL_SIX}   #Creating a dictionary for d-states
            d_state = False
            state = state.lower()
            for keys in state_list:
                if state in keys:
                    d_state = state_list[state]                                 #if getting the column number of respective d-states
            if "CONFIG-" in device_name:                                        #if "CONFIG-" is present in device_name
                device_name = utils.ConfigTagVariable(device_name)
                device_name = device_name.upper()
            else:
                pass
            with open(log_file_path, "rb") as file:                             # open the .csv log_file in read mode for parsing residency
                lines = csv.reader(file)
                for line in lines:                                              #loop to iterate through lines in the file
                    if line != []:
                        if "D-state Residency" in line[0]:                      #if "D State Residency" string found in file
                            line = next(file)                                   #move to next line
                            for line in lines:
                                if device_name in line[1].upper():              #if device_name string found in file
                                    percentage_residency  = \
                                        (line[d_state].split("%")[0]).strip()   #assign S3 residency value to variable percentage_residency
                                    residency_flag = True                       #if residency parsing is successfull then set the residency_flag to true
                                    break
                                else:                                           #if device_name string does not found in file then move to next line of file
                                    pass
                        else:                                                   #if "D State Residency" string does not found in file then move to next line of file
                            pass
                    else:
                        pass
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO :Input Syntax is"
           " incorrect ",test_case_id, script_id, "None", "None", loglevel, tbd)# write info msg to log if Input Syntax is incorrect
            return False,state
        if True == residency_flag:                                              #if parsing of residency file is successfull
            library.write_log(lib_constants.LOG_INFO, "INFO :Residency "
                "of %s device in %s state is equals to"
                " %s percentage"%(device_name,state,percentage_residency),
                test_case_id, script_id, "Socwatch_tool", "None", loglevel, tbd)# write info msg to log if Read residency of device in given state
            return percentage_residency,state
        else:                                                                   #if Failed to Read residency of device in given state
            library.write_log(lib_constants.LOG_DEBUG, "DEBUG :Failed to "
"read residency of %s device in %s state or may be residency of %s device is"
    " not present for %s state in the log file"%(device_name,state,device_name,state),
                test_case_id, script_id, "Socwatch_tool", "None", loglevel, tbd)# write info msg to log if Failed to Read residency of device in given state
            return False,state
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "read_residency() library function due to %s."%e,
            test_case_id, script_id,"Socwatch_tool", "None", loglevel, tbd)     # write error msg to log if Exception occurs in read_residency() library function
        return False,state
################################################################################