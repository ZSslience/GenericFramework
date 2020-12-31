__author__ = 'NARESHGX'

############################General Python Imports##############################
import utils
############################Local Python Imports################################
import lib_constants
import library
################################################################################
#   Function name   : configure_jumper
#   description     : boot to destination from boot manager
#   parameters      : 'tc_id' is test case id
#                          'script_id' is script id
#                          'token ' is original string
#   Returns         : True/False
######################### Main script ##########################################
def configure_jumper(token,test_case_id, script_id,
                               loglevel="ALL", tbd="None"):                     #function to set required jumper settings
    try:
        token = token.split(' ')
        jumper_name = library.extract_parameter_from_token(token,'jumper',
                                                           'pins')[0]
        pins = library.extract_parameter_from_token(token,'pins','')[0]
        jumper_def = lib_constants.JUMPER_DEFAULT[jumper_name.upper()]          # get default jumper connection from lib_constants
        if jumper_def:
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper default "
            "pins are %s"%jumper_def, test_case_id, script_id,"None","None",
                                                            loglevel,tbd)
        else:                                                                   # Default jumper pins are not defined
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper "
            "default pins not found in lib constants ", test_case_id,
                                    script_id,"None","None",loglevel,tbd)
            return False
        if 'config' in jumper_name:                                             # if config in token then executed below code
            config_sc,operation = jumper_name.split(' ')
            section_name = config_sc.split('-')[1]
            opt_name = config_sc.split('-')[2]
            try:
                jumper_relay = utils.ReadConfig(section_name,opt_name)          # check relay connection from config.ini
                if 'FAIL:' in jumper_relay.upper():
                    library.write_log(lib_constants.LOG_INFO,"INFO: Jumper "
                    "rework is not connected to relay", test_case_id,script_id,
                                                "None","None",loglevel, tbd)
                    return False
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper rework "
                "is connected  to relay No. %s"%jumper_relay, test_case_id,
                                        script_id,"None","None",loglevel, tbd)
            except Exception as e:                                              # if exception found in retrieving relay no.
                library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception"
                " in retrieving relay No. %s"%e, test_case_id,script_id,"None",
                                                        "None",loglevel,tbd)
                return False
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper operation "
            "to perform %s"%operation+" pins %s"%pins, test_case_id, script_id,
                                                  "None","None",loglevel, tbd)
            status,opt = ttk_operation(operation,jumper_def,jumper_relay,pins,
                                   test_case_id,script_id,loglevel,tbd)         # call TTK function
            if status :
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper %s "
            %opt_name+"for pins %s"%pins +" are %s"%opt, test_case_id,
                                  script_id,"None","None",loglevel,tbd)
                return True
            else:                                                               # check for ttk operation status if false return false to main script
                library.write_log(lib_constants.LOG_WARNING,"WARNING: Warning "
                                "failed to %s Jumper pins"%opt, test_case_id,
                                  script_id,"None","None",loglevel,tbd)
                return False

        else:                                                                   # if config is not there in token and jumper is provided executed below code
            jumper_n,operation = jumper_name.split(' ')
            jumper_relay = utils.ReadConfig('JUMPER_RELAY',jumper_n)
            if 'FAIL:' in jumper_relay.upper():                                 # check for relay connection port
                    library.write_log(lib_constants.LOG_INFO,"INFO: Jumper "
                    "rework is not connected to relay", test_case_id,script_id,
                                                "None","None",loglevel, tbd)
                    return False
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper rework is "
            "connected  to relay No. %s"%jumper_relay, test_case_id, script_id,
                              "None","None",loglevel, tbd)
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper operation "
            "to perform %s"%operation+" pins %s"%pins, test_case_id, script_id,
                                                  "None","None",loglevel, tbd)
            status,opt = ttk_operation(operation,jumper_def,jumper_relay,pins,
                                   test_case_id,script_id,loglevel,tbd)
            if status :                                                         # check current ttk status and operation
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper %s "
            %jumper_n+"for pins %s"%pins +" are %s"%opt, test_case_id,
                                  script_id,"None","None",loglevel,tbd)
                return True
            else:                                                               # if status is false then return false to main script
                library.write_log(lib_constants.LOG_DEBUG,"DEBUG: failed to %s "
                "Jumper pins"%opt, test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "performing jumper setting", test_case_id, script_id,"None","None",
                          loglevel, tbd)
        return False
################################################################################
#   Function name   : ttk_operation
#   description     : boot to destination from boot manager
#   parameters      : operation,jumper_def,relay,jumper,test_case_id,script_id,
#                                                                log_level,tbd
#   Returns         : True/False with operation performed
######################### Main script ##########################################
def ttk_operation(operation,jumper_def,relay,jumper,test_case_id,script_id,
                                                                log_level,tbd):
    try:
        aDevice = library.initialize_ttk(log_level,tbd)                         # get object of ttk
        direc,state = aDevice.getGPIO(0)                                        # get state and direction of ttk relay
        tempValue = (0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80)                       # initialize relay no
        if(direc & tempValue[int(relay)] == tempValue[int(relay)]):
            if(state & tempValue[int(relay)] == tempValue[int(relay)]):         # get relay status
                current_status = "High"
            else:
                current_status = "Low"
        else:
            current_status = "Input"

        library.write_log(lib_constants.LOG_INFO,"INFO: Current status of TTK "
        "realy is %s"%current_status, test_case_id, script_id,"None","None",
                                                                log_level,tbd)
    except Exception as e:                                                      # exception found in ttk read
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception"
                " in TTK operation"%e,test_case_id,script_id,"TTK","setGPIO()",
                                  log_level,tbd)
        return False,'Fail'

    if ('connect' == operation) and (jumper_def == jumper) and ('Input' == \
                                    current_status or 'High' == current_status):# if operation is connect and jumper is default pin and status of relay is input or high no operation required
            library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins are"
            " by default connected", test_case_id, script_id,"None","None",
                                                            log_level,tbd)
            return True,'connected'
    elif ('connect' == operation) and (jumper_def == jumper) and ('Low' != \
                                                            current_status):
        try:
            release = library.ttk_set_relay('OFF',[int(relay)])                 # Pressing the button using ttk to turn off to make default relay jumper settings
            if release == 0:
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins %s"
                %jumper+" are connected",test_case_id,script_id,"TTK",
                                  "setGPIO()",log_level,tbd)
                return True,'connected'
        except Exception as e:                                                  # if exception found in ttk relay operation
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception "
            "in TTK operation"%e,test_case_id,script_id,"TTK","setGPIO()",
                              log_level,tbd)
            return False,'Fail'
    elif ('disconnect' == operation) and (jumper_def == jumper) and ('Low' == \
                                                        current_status):        # if disconnect and default jumper and ttk relay status is low the
        try:
            press = library.ttk_set_relay('ON',[int(relay)])                    #Pressing the button using ttk to turn on to make default settings disconnected
            if press == 0:
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins %s"
                %jumper+" are disconnected",test_case_id,script_id,"TTK",
                                  "setGPIO()",log_level,tbd)
                return True,'disconnected'
        except Exception as e:                                                  # exception found in ttk operation return fail
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception "
            "in TTK operation"%e,test_case_id,script_id,"TTK","setGPIO()",
                              log_level,tbd)
            return False,'Fail'
    elif ('connect' == operation) and (jumper_def != jumper) and ('Low' == \
                                                        current_status):        # if operation is connect and not a default jumper connection and current relay state is low
        library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins %s are "
        "connected"%jumper, test_case_id, script_id,"None","None",log_level,tbd)
        return True,'connected'
    elif ('disconnect' == operation) and (jumper_def != jumper) and \
            ('Input' == current_status or 'High' == current_status):            # if operation is disconnect and not a default connection and current relay status is input or high no operation has to be done on ttk
        library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins are "
        "disconnected", test_case_id, script_id,"None","None",log_level,tbd)
        return True,'disconnected'
    elif ('disconnect' == operation) and (jumper_def != jumper) and ('Low' == \
                                                        current_status):
        try:
            release = library.ttk_set_relay('OFF',[int(relay)])                 #Pressing the button using ttk to turn off and make default connection on
            if release == 0:
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins %s"
                %jumper+" are disconnected",test_case_id,script_id,"TTK",
                                  "setGPIO()",log_level,tbd)
                return True,'disconnected'
        except Exception as e:                                                  # exception in ttk operation
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception "
            "in TTK operation"%e,test_case_id,script_id,"TTK","setGPIO()",
                              log_level,tbd)
            return False,'Fail'
    elif ('connect' == operation) and (jumper_def != jumper) and ('Input' == \
                                    current_status or 'High' == current_status):# if operation is connect and not default connection and relay state
        try:
            press = library.ttk_set_relay('ON',[int(relay)])                    #Pressing the button using ttk to turn on to connect
            if press == 0:
                library.write_log(lib_constants.LOG_INFO,"INFO: Jumper pins %s"
                %jumper+" are connected",test_case_id,script_id,"TTK",
                                  "setGPIO()",log_level,tbd)
                return True,'connected'
        except Exception as e:                                                  # if ttk exception is found return false
            library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception "
            "in TTK operation"%e,test_case_id,script_id,"TTK","setGPIO()",
                              log_level,tbd)
            return False,'Fail'