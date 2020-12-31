################################################################################
# Function name   : C_P_T_state_capture()
# description     : to start/stop tool based on the required states
# parameters      : 'tc_id' is test case id
#                  'script_id' is script id
#                  'status' is start/stop
# Returns         : 'True' on successfully performed on status, 'False' on
#                   failure to perform the status
################################################################################
def C_P_S_T_state_capture(status, state, tc_id, script_id,
                          loglevel="ALL", tbd="None"):
############################# Local Imports ####################################
    import utils
    import lib_constants
    import library
############################# General Imports ##################################
    try:
        if 'start' == status.lower():                                           # if the capture status is 'start'
            ret = library.run_socwatch(status,state,tc_id,script_id)            # calls the function for running the socwatch tool and returns true if started capture is success
            if ret:
                library.write_log(lib_constants.LOG_INFO,"INFO: SOC watch "
                "started capturing",tc_id,script_id,"None","None",loglevel,tbd)
                return ret
            else :
                library.write_log(lib_constants.LOG_FAIL,"FAIL: Fail to start "
                "%s capturing"%state,tc_id,script_id,"None","None",loglevel,tbd)
                return False
        else:
            status = library.run_socwatch(status, state, tc_id, script_id)
            if status:
                library.write_log(lib_constants.LOG_INFO,"INFO: Successfully"
                " %sed %s capturing and saved log file path in "
                "result.ini"%(status,state),tc_id,script_id,"None","None",
                loglevel,tbd)
                return status
            else :
                library.write_log(lib_constants.LOG_FAIL,"FAIL: Fail to stop "
                "%s capturing"%state,tc_id,script_id,"None","None",loglevel,tbd)
                return False                                                   # returns the log file capture state is stopped successfully
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Due to %s"%e,
        tc_id,script_id,"None","None",loglevel,tbd)
        return False

################################################################################