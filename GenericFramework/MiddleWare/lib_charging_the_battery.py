__author__ = 'dksingh'

############################General Python Imports##############################
                                                                                #inbuilt python import
import time
import wmi
############################Local Python Imports################################
                                                                                #Local import
import lib_constants
import library

################################################################################
# Function Name : charge_battery
# Parameters    : test case id,script id, log_level, tbd
# Functionality : This code charge the battery
# Return Value :  result value/false
################################################################################


def charge_battery(test_case_id, script_id, token, log_level="ALL", tbd="None"):#Charging battery function start

    input_token = token.split()
    pernum = input_token[4].strip('%')                                          #strip the percentage
    value = int(pernum)                                                         #convert to integer
    library.write_log(lib_constants.LOG_INFO,"INFO : Expected Battery: %s "
    "percent" %value, test_case_id, script_id, "None", "None", log_level, tbd)

    c = wmi.WMI()                                                               #create a wmi object

    try:
        global Name, charge_remaining
        time.sleep(lib_constants.FIVE_SECONDS)
        for n in c.Win32_Battery():
            Name = n.Name
        if 'Battery 0' not in Name:                                             #Checking if battery is connected to SUT
            library.write_log(lib_constants.LOG_INFO
                              ,"INFO : Battery is Connected.",test_case_id,
                              script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO : Battery is not "
                                "Connected to SUT", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False, 0
        if 2 == batteryinfo(test_case_id, script_id, log_level, tbd):           #Checking if SUT is in AC mode
            library.write_log(lib_constants.LOG_INFO, "INFO : It is verified "
                        "that, SUT is in AC + DC mode", test_case_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: AC source is not "
                            "connected to the SUT", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False, 0
        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            charge_remaining = battery.EstimatedChargeRemaining
        library.write_log(lib_constants.LOG_INFO, "INFO :The Current battery"
                        " status is: %s percent" %charge_remaining,
                       test_case_id, script_id, "None", "None", log_level, tbd)
        if charge_remaining < value:                                            #Looping throuh unless battery is charged to given percentage
            while True:
                for battery in c.Win32_Battery():                               #iterate through wmi battery call
                    charge_remaining = battery.EstimatedChargeRemaining         #check for current percentage of battery
                time.sleep(lib_constants.SHORT_TIME)                            #sleep for 60 seconds
                if charge_remaining >= value:
                    library.write_log(lib_constants.LOG_INFO,"INFO :The"
        " battery status reached to: %s percent" %charge_remaining,
                     test_case_id, script_id, "None", "None", log_level, tbd)
                    return True, charge_remaining
                Loop =+ 1
                if Loop == lib_constants.CLEAR_CMOS_WAIT_TIME:                  #wait till 3hours
                    library.write_log(lib_constants.LOG_INFO, "INFO : Timeout-"
        " Attempted to charge for 3 hours, target percentage not achieved",
                    test_case_id, script_id,  "None", "None", log_level, tbd)
                    return False, None
        else:
            library.write_log(lib_constants.LOG_INFO," INFO: Already achieved:"
                     " %s percent" %charge_remaining, test_case_id, script_id)  #Else check if the given percentage is already achieved

            return True, charge_remaining
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to Execute "
                                    "due to %s."%e, test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name : batteryinfo
# Parameters    : test case id,script id, log_level, tbd
# Functionality : This code charge the battery
# Return Value :  result value/false
################################################################################


def batteryinfo(test_case_id, script_id, token, log_level="ALL", tbd="None"):   #WMI query to get the battery information and its status
    WMIobj = wmi.WMI()
    battery = WMIobj.query("SELECT Availability FROM Win32_Battery")
    if battery:
        for values in battery:
            return values.Availability                                          #returns 2 when in Ac is connected and returns 3 when AC is not connected


                                                                                #Charging Battery Grammar section ends

################################################################################