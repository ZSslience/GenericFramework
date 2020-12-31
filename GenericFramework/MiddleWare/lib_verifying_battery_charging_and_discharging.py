__author__ = "jkmody"

###########################General Imports######################################
import os
import wmi
import time
################################################################################

############################Local imports#######################################
import lib_constants
import library
import lib_perform_sx_cycles
################################################################################

################################################################################
# Function Name : battery_charge_discharge_operation()
# Parameters    : action(charge/discharge),Sx state(S0 is default),
#                 testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Charge or discharge depending on the current scenario in the
#                 desired Sx state and verify if sut is properly charging/
#                 discharging
################################################################################


def battery_charge_discharge_operation(action,state, test_case_id, script_id,
                                       log_level="ALL", tbd="None"):
    try:
        os.chdir(lib_constants.SCRIPTDIR)
        global initial_charge, final_charge, Name
        c = wmi.WMI()
        for n in c.Win32_Battery():
            Name = n.Name                                                       #WMI query for check if battery is detected in SUT

        if 'Battery 0' not in Name:                                             #Checking if battery is connected to SUT
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Battery is detected on SUT.",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: Battery is not detected to SUT",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False                                                        # Exiting if battery is not detected on target system

        for battery in c.Win32_Battery():                                       #Getting current battery charge status
            initial_charge = battery.EstimatedChargeRemaining
        initial_charge_data = os.path.join(lib_constants.SCRIPTDIR,
                                           "initial_charge_data.txt")           #File to store the current charge value
        f1 = open(initial_charge_data, "w")                                     #opening the file to write the data
        f1.write(str(initial_charge))
        f1.close()
        if initial_charge in range(lib_constants.CRITICAL_CHARGE+5,
                                   lib_constants.FULL_CHARGE - 1):              #if the current charge is less than critical battery level or nearing full charge
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: The current battery status %s is in range"
                              " of critical battery to full charge"
                              % str(initial_charge), test_case_id, script_id,
                              "None", "None", log_level, tbd)                   # proceeding to charge/discharge
        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: The Current battery status is less than"
                              " critical battery level or 100% charged hence"
                              " exiting", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #exiting the call as battery is not suitable to charge/discharge
            return False

        if state in ["S3", "S4", "S0"]:                                         #if Sx state in which charge/discharge to be done is S3/S4/S0
            if ("S3" == state) or ("S4" == state):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Detected battery charge as %s in"
                                  " the system" % initial_charge,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            elif "S0" == state:
                final_charge = verify_charging_discharging_in_S0(c, action,
                                                                 initial_charge)
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: System was set to idle state to verify"
                                  " battery is %s " % action, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
            else:
                pass
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Battery charge is %s after %s in %s state"
                              % (str(final_charge), action, state),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            if verify_charging_discharging(action, state, initial_charge,
                                           final_charge, test_case_id,
                                           script_id, log_level, tbd):          #verifying succesfull battery charge/discharge based on requiremnt
                return True
            else:
                return False
        elif "S5" == state:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: SUT will shutdown in 30 secs to verify"
                              " battery is %s " % action, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            os.system('start shutdown /s /t 30')                                #Shutdown SUT for S5 cycles
            return True
        else:
            pass                                                                #any future implementation to be handled

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "ERROR: Exception occurred due to %s" % e, script_id,
                          test_case_id, "None", "None", log_level, tbd)
        return False                                                            #Any exception to be handled here

################################################################################
# Function Name : verify_charge_after_s5()
# Parameters    : action(charge/discharge),Sx state(S0 is default),
#                 testcase id, script id, loglevel and tbd2
# Return Value  : True on success, False on failure
# Functionality : Compare current battery level to initial battery level before
#                 S5 state by checking the stored value
################################################################################


def verify_charge_after_s5(action, state, test_case_id, script_id,
                           log_level="ALL", tbd="None"):
    c = wmi.WMI()
    for battery in c.Win32_Battery():                                           #Getting latest battery charge status
        final_charge = battery.EstimatedChargeRemaining

    initial_charge_data = os.path.join(lib_constants.SCRIPTDIR,
                                       "initial_charge_data.txt")               ##reading the stored charge value before S5
    f1 = open(initial_charge_data, "r")
    initial_charge = f1.read()
    f1.close()

    if verify_charging_discharging(action, state, initial_charge, final_charge,
                                   test_case_id, script_id, log_level, tbd):    #calling function to determine charge/discharge is successfull
        return True
    else:
        return False


################################################################################
# Function Name : verify_charging_discharging()
# Parameters    : action,state,initial_charge,final_charge,
#                 test_case_id,script_id,log_level,tbd
# Return Value  : True on verification Pass, False on verification failed
# Functionality : Compare the initial charge to the current charge percentage
################################################################################

def verify_charging_discharging(action, state, initial_charge, final_charge,
                                test_case_id, script_id, log_level, tbd):
    if "CHARGING" == action and (int(final_charge) > int(initial_charge)):
        library.write_log(lib_constants.LOG_PASS,
                          "PASS: SUT battery has charged from %s to %s in %s"
                          " state" % (str(initial_charge), str(final_charge),
                                      state), test_case_id,
                          script_id, "None", "None", log_level, tbd)
        return True
    elif "DISCHARGING" == action and (int(final_charge) < int(initial_charge)):
        library.write_log(lib_constants.LOG_PASS,
                          "PASS: SUT battery has discharged to %s from %s in %s"
                          " state" % (str(final_charge), str(initial_charge),
                                      state), test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_FAIL,
                          "FAIL: SUT battery is not %s in %s state"
                          % (action, state), test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : verify_charging_discharging_in_S0
# Parameters    : wmi object,action,initial_charge
# Return Value  : charge
# Functionality : return the charge once the charge is >= 3 if charging and
#                   <= 3 in discharging
################################################################################


def verify_charging_discharging_in_S0(c, action, init_charge):
    time_count = 0
    charge = init_charge
    while(True):
        if "CHARGING" == action and (int(charge) >=
               int(init_charge + lib_constants.BATTERY_CHARGE_DISCHARGE_DELTA)):
            return charge
        elif "DISCHARGING" == action and (int(charge) <=
               int(init_charge - lib_constants.BATTERY_CHARGE_DISCHARGE_DELTA)):
            return charge
        else:
            time.sleep(lib_constants.BATTERY_CHARGE_DISCHARGE_WAIT_TIME)        #waiting for configured time to let battery charge/discharge in OS
            for battery in c.Win32_Battery():                                   #Getting latest battery charge status after idle wait
                charge = battery.EstimatedChargeRemaining
        time_count = time_count + 1

        if lib_constants.BATTERY_CHARGE_DISCHARGE_COUNT == time_count:
            return charge                                                       #Waiting for 10 minutes and then returning the charge


################################################################################
# Function Name : verify_charge_after_sx
# Parameters    : action, state, test_case_id, script_id, log_level, tbd
# Return Value  : True/False
# Functionality : return True/False after comparing the initial charge
#                 and final charge
################################################################################


def verify_charge_after_sx(action, state, test_case_id, script_id,
                           log_level="ALL", tbd="None"):

    try:
        c = wmi.WMI()
        for battery in c.Win32_Battery():                                       #Getting latest battery charge status
            final_charge = battery.EstimatedChargeRemaining

        initial_charge_data = os.path.join(lib_constants.SCRIPTDIR,
                                           "initial_charge_data.txt")           #reading the stored charge value before Sx
        f1 = open(initial_charge_data, "r")
        initial_charge = f1.read()
        f1.close()

        if verify_charging_discharging(action, state, initial_charge,
                                       final_charge, test_case_id, script_id,
                                       log_level, tbd):                         #calling function to determine charge/discharge is successfull
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,
                          "ERROR: Exception occurred due to %s" % e, script_id,
                          test_case_id, "None", "None", log_level, tbd)
        return False