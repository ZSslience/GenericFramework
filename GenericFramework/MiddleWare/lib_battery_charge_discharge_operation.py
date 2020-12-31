__author__ = "bchowdhx"

###########################General Imports######################################
import os
import wmi
import time
################################################################################

############################Local imports#######################################
import lib_constants
import library
import utils
import lib_connect_disconnect_power_source
################################################################################

################################################################################
# Function Name : write_to_file()
# Parameters    : status of battery, testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Writing to file the current state of battery
################################################################################


def write_to_file(status_to_write, test_case_id, script_id, log_level='ALL',
                  tbd='None'):

    try:
        os.chdir(lib_constants.SCRIPTDIR)
        with open("charge_discharge.txt", "w") as r:                            #write the status to write on a file in script directory(UP/DOWN)
            r.write(status_to_write)

        if os.path.exists(lib_constants.SCRIPTDIR + "\\charge_discharge.txt"):  #check for the file is present or not
            if os.path.getsize((lib_constants.SCRIPTDIR +
                                    "\\charge_discharge.txt")) > 0:             #if present check for the size of the file
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured"
                          "due to %s"%e,test_case_id, script_id, log_level, tbd)


################################################################################
# Function Name : perform_action()
# Parameters    : status of battery, testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Connect/disconnect AC/DC on requirement
################################################################################


def perform_action(test_case_id, script_id, log_level='ALL', tbd='None'):

    try:
        global charge, discharge
        SUT_IP = utils.ReadConfig("SUT_IP","IP")                                #read sut ip from config
        if "FAIL:" in SUT_IP:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: IP for sut "
                "is missing in the config file", test_case_id, script_id,
                              log_level, tbd)
        else:
            pass

        path = os.getcwd().split("C:\\")[1]

        file_path = "\\\\" + SUT_IP + "\\" + str(path) + "\\charge_discharge.txt"                                    #file path to the script folder in sut

        if os.path.exists(file_path):                                           #check for the file exists or not
            with open(file_path, 'r') as file:                                  # open the file
                for x in file:                                                  #iterate through the line
                    if "UP" in x:                                               #If up in file put charge to True
                        charge = True
                        discharge = False
                    elif "DOWN" in x:                                           #if down in file put discharge to false
                        discharge = True
                        charge = False
                    else:
                        library.write_log(lib_constants.LOG_WARNING,"Action "
                        "cannot be identified", script_id, test_case_id,
                                  "None", "None", log_level, tbd)
                        return False
            if charge:                                                          #if charging is to be done
                result_ac = lib_connect_disconnect_power_source.\
                        connect_disconnect_power_ttk("AC", "CONNECT",
                                                    test_case_id, script_id,
                                                    log_level, tbd)             #connect ac

                time.sleep(lib_constants.TEN_SECONDS)
                if result_ac:
                    library.write_log(lib_constants.LOG_INFO, "Successfully "
                        "AC Power source connected to SUT",
                     script_id, test_case_id, "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_INFO, "Connecting AC "
                        "Power source to SUT failed", script_id, test_case_id,
                                  "None", "None", log_level, tbd)
                    return False

            elif discharge:                                                     #if discharge to be done

                value_output = lib_connect_disconnect_power_source.\
                    connect_disconnect_power_ttk("AC", "DISCONNECT",
                                test_case_id, script_id, log_level, tbd)        #Disconnect AC
                time.sleep(lib_constants.TEN_SECONDS)
                if value_output:
                    library.write_log(lib_constants.LOG_INFO, "Successfully"
                "AC/DC connection done on SUT", script_id,
                            test_case_id, "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_INFO, "Connecting "
                        "AC/DC Power source to SUT failed", script_id,
                            test_case_id, "None", "None", log_level, tbd)
                    return False
            else:
                pass
        else:
            library.write_log(lib_constants.LOG_INFO, "Action [charging"
                "/discharging] could not be found",
                script_id,test_case_id,"None", "None", log_level, tbd)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured "
        "due to %s"%e, test_case_id, script_id, "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name : get_current_battery()
# Parameters    : ostr, testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Calculate the current charge and write to file accordingly
################################################################################


def get_current_battery(ostr, test_case_id, script_id, log_level='ALL',
                        tbd='None'):

    global charge_remaining
    try:

        c = wmi.WMI()
        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            charge_remaining = battery.EstimatedChargeRemaining

        if "UP" in ostr.upper():
            status_to_write = "UP"
            library.write_log(lib_constants.LOG_INFO, "INFO :The Current battery"
                            " status is: %s percent" %charge_remaining,
                        test_case_id, script_id, "None", "None", log_level, tbd)
            return status_to_write
        elif "DOWN" in ostr.upper():
            status_to_write = "DOWN"
            library.write_log(lib_constants.LOG_INFO, "INFO :The Current battery"
                            " status is: %s percent" %charge_remaining,
                        test_case_id, script_id, "None", "None", log_level, tbd)
            return status_to_write
        else:
            #ostr = ostr[:-1].strip()                                            #strip the percentage
            value = ostr.split()[4].strip()                                           #convert to integer
            print(value)
            library.write_log(lib_constants.LOG_INFO, "INFO :The Current battery"
                            " status is: %s percent" %charge_remaining,
                        test_case_id, script_id, "None", "None", log_level, tbd)

            if int(value) > charge_remaining:
                status_to_write = "UP"
                return status_to_write
            else:
                status_to_write = "DOWN"
                status_to_write = "DOWN"
                return status_to_write

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR :Exception occurred"
    " due to %s"%e, test_case_id, script_id, "None", "None", log_level, tbd)


################################################################################
# Function Name : battery_charge_discharge_operation()
# Parameters    : ostr, testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Call charge or discharge depending on the current scenario
################################################################################


def battery_charge_discharge_operation(ostr, test_case_id, script_id,
                               log_level = "ALL", tbd="None"):
    try:
        global charge
        os.chdir(lib_constants.SCRIPTDIR)
        with open("charge_discharge.txt", "r") as file:                         #read the text file
            for x in file:
                if "UP" in x:
                    charge = "UP"
                elif "DOWN" in x:
                    charge = "DOWN"

        #ostr = ostr[:-1].strip()                                                #strip the percentage
        value = ostr.split()[4].strip()

        library.write_log(lib_constants.LOG_INFO,"INFO : Expected Battery: %s "
        "percent" %value, test_case_id, script_id, "None", "None", log_level,
                          tbd)

        c = wmi.WMI()                                                           #create a wmi object

        global Name, charge_remaining
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
            return False, False, None

        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            charge_remaining = battery.EstimatedChargeRemaining

        library.write_log(lib_constants.LOG_INFO, "INFO :The Current battery"
                        " status is: %s percent" %charge_remaining,
                       test_case_id, script_id, "None", "None", log_level, tbd)

        if int(value) == charge_remaining:                                      #If value is equal to required value then return true and exit
            library.write_log(lib_constants.LOG_INFO, "INFO: The current "
                "battery charge is equal to the required charge %s"%value,
                    test_case_id,script_id, "None", "None", log_level, tbd)
            return True, True, value

        elif int(value) > charge_remaining and "UP" in charge:                   #if current value is greater or equal to current charge and UP in charge
            state, current_value = charging_battery(value, charge_remaining,
                                        test_case_id, script_id, log_level, tbd)
            if state:
                return True, False, current_value
            else:
                return False, False, current_value

        elif int(value) < charge_remaining and "DOWN" in charge:               #if current value is less or equal to current charge and DOWN in charge
            state, current_value = discharging_battery(value, charge_remaining,
                                        test_case_id, script_id, log_level, tbd)#library call to discharge battery
            if state:
                return False, True, current_value
            else:
                return False, False, current_value
        else:
            return False, False,None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occurred"
            " due to %s"%e, script_id, test_case_id, "None", "None", log_level,
                          tbd)
        return False, False, 0                                                  #return charge discharge values as false and current charge value as 0 as placeholder value


################################################################################
# Function Name : charging_battery()
# Parameters    : value, charge_remaining, test_case_id, script_id, log_level,
#                   tbd
# Return Value  : Current charge on success, 0 on failure
# Functionality : Charging battery
################################################################################


def charging_battery(value, charge_remaining, test_case_id, script_id,
                               log_level = "ALL", tbd="None"):

    c = wmi.WMI()                                                               #create a wmi object

    if str(lib_constants.TWO) == str(batteryinfo(test_case_id, script_id, log_level, tbd)):               #Checking if SUT is in AC mode
        library.write_log(lib_constants.LOG_INFO, "INFO : It is verified "
                    "that, SUT is in AC mode", test_case_id, script_id,
                          "None", "None", log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: SUT is not in "
                                        "AC mode", test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False,False, 0
    if charge_remaining < int(value):                                           #looping through unless battery is charged to given percentage
        while True:
            time.sleep(lib_constants.SHORT_TIME)                                #sleep for 60 seconds
            for battery in c.Win32_Battery():                                   #iterate through wmi battery call
                charge_remaining = battery.EstimatedChargeRemaining             #check for current percentage of battery
            if charge_remaining >= int(value):
                library.write_log(lib_constants.LOG_INFO,"INFO :The"
    " battery status reached to: %s percent" %charge_remaining,
                 test_case_id, script_id, "None", "None", log_level, tbd)
                return True, charge_remaining
            loop = + 1
            if lib_constants.ONE_EIGHTY_ONE == loop:                            #wait till 3hours
                library.write_log(lib_constants.LOG_INFO, "INFO : Timeout"
    " Charged for 3 hours, Target not achieved", test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return False, 0                                                 #return False and placeholder value which wont be of use in the script
    else:
        library.write_log(lib_constants.LOG_INFO," INFO: Already achieved:"
                 " %s percent" %charge_remaining, test_case_id, script_id)      #Else check if the given percentage is already achieved

        return True, charge_remaining                                           #returns True and current sut charge


################################################################################
# Function Name : discharging_battery()
# Parameters    : value, charge_remaining, testcase id, script id, loglevel,tbd2
# Return Value  : True on success, False on failure
# Functionality : Discharging the battery using heavy load tool
################################################################################


def discharging_battery(value, charge_remaining, test_case_id, script_id,
                               loglevel = "ALL", tbd="None"):

    c = wmi.WMI()                                                               #creating an instance of wmi function from wmi module
    if lib_constants.THREE == batteryinfo(test_case_id, script_id, loglevel, tbd):                #Checking if SUT is in AC mode 3 means AC disconnected with DC mode on
        library.write_log(lib_constants.LOG_INFO, "INFO : It is verified "
                    "that, SUT is in DC mode with AC disconnected",
                      test_case_id, script_id, "None", "None", loglevel, tbd)
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: SUT is in "
                                        "AC mode", test_case_id, script_id,
                          "None", "None", loglevel, tbd)
        return False, 0

    os.chdir(lib_constants.TOOLPATH+"\\heavyload")
    heavyload_cmd="START " + lib_constants.HEAVY_LOAD     #Start heavyload in a different thread

    if charge_remaining > int(value):                                           #if current charge is greater than required value
        os.system(heavyload_cmd)                                                #run the heavyload tool
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_INFO, "Starting heavy load tool,"
            "to discharge the battery", test_case_id, script_id, "None", "None",
                          loglevel, tbd)

        while True:
            for battery in c.Win32_Battery():                                   #iterate through wmi battery call
                charge_remaining = battery.EstimatedChargeRemaining             #check for current percentage of battery
            if int(value) > int(charge_remaining):                                  #check for charge remaining equals to required value
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_INFO,"INFO :Stopping the"
    "load tool as battery status reached to: %s percent" %charge_remaining,
                 test_case_id, script_id, "None", "None", loglevel, tbd)
                os.system("TASKKILL /F /IM heavyload.exe")                      #kills the heavyload tool from task manager
                time.sleep(lib_constants.TEN_SECONDS)                           #sleep for 10 seconds
                break

        return True, charge_remaining                                           #return true and the current battery charge

################################################################################
# Function Name : batteryinfo
# Parameters    : test case id,script id, log_level, tbd
# Functionality : This checks the status of the battery
# Return Value :  result value/false
################################################################################


def batteryinfo(test_case_id, script_id, token, log_level="ALL", tbd="None"):   #WMI query to get the battery information and its status
    WMIobj = wmi.WMI()
    battery = WMIobj.query("SELECT Availability FROM Win32_Battery")
    if battery:
        for values in battery:
            return values.Availability
                                                                                # Charging Battery Grammar section ends

################################################################################
