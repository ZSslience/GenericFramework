__author__ = 'bisweswx/hvinayx/tnaidux'

# Global Python Imports
import getopt
import os
import sys
import time

# Local Python Imports
import lib_constants
import library
import utils
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations
import soundwave
import state
from state_transition import StateTransition
import lib_cswitch

################################################################################
# Function Name : connect_disconnect_power_ttk
# Parameters    : source, type, test_case_id, script_id, log_level, tbd
# Functionality : To connect/disconnect power source
# Inputs Params : type   : CONNECT/DISCONNECT
#                 source : Power source from Token(E.g AC, DC, USB Charger,
#                          TYPEC-PD-60W)
# Return Value  : True/False
################################################################################


def connect_disconnect_power_ttk(source, type, test_case_id, script_id,
                                 log_level, tbd):

    try:
        if "DISCONNECT" == type.upper():
            on_off_flag = 'OFF'
        else:
            on_off_flag = 'ON'

        if source in lib_constants.AC_SOURCES:                                  # If AC power sources to be connected/disconnected
            if library.ac_power(on_off_flag, test_case_id, script_id,
                                log_level, tbd):                                # AC power is turned on/off based on connect and disconnect criteria
                library.write_log(lib_constants.LOG_INFO, "INFO: %s %s source "
                                  "is successful using TTK" % (type, source),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                time.sleep(lib_constants.FIVE_SECONDS)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to %s %s source" % (type, source),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False
        elif "DC" == source:
            dc_power = utils.ReadConfig("TTK", "dc_power_port")
            dc_signal = utils.ReadConfig("TTK", "dc_signal_port")

            if "NC" in [dc_power, dc_signal]:
                library.write_log(lib_constants.LOG_INFO, "INFO: No Real "
                                  "battery is connected to SUT", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            elif "NA" in [dc_power, dc_signal]:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                  "power rework not Applicable for the target "
                                  "system" % source, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            elif "fail:" in dc_signal.lower() or "fail:" in dc_power.lower():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "power rework details are not available under"
                                  " the header %s for the values %s and %s in "
                                  "Config.ini" % (source, "TTK", "dc_power_port",
                                                  "dc_signal_port"), test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s power "
                                  "source rework is connected to Relay number "
                                  "%s and %s in TTK" % (source, dc_power,
                                                        dc_signal),
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)

                lib_ttk2_operations.kill_ttk2(test_case_id, script_id,
                                              log_level, tbd)
                time.sleep(10)

                result = lib_ttk2_operations.\
                    ttk_set_relay_dc(on_off_flag, dc_signal, dc_power,
                                     test_case_id, script_id, log_level, tbd)

                if result is True:
                    relay_action_signal, relay_action_power = 0, 0
                else:
                    relay_action_signal, relay_action_power = 1, 1

                time.sleep(lib_constants.TEN)

                if 0 == relay_action_power and 0 == relay_action_signal:
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s of %s "
                                      "source is successful using TTK"
                                      % (type, source), test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to  %s %s source" % (type,
                                                                   source),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
        elif source in lib_constants.TYPEC_SOURCES:
            config_entry = "CSWITCH_" + source.upper()
            cswitch_port = utils.ReadConfig("CSWITCH", config_entry)
            if "FAIL" in cswitch_port.upper() or 'NC' in cswitch_port.upper() \
                    or 'NA' in cswitch_port.upper():
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: config entry for cswitch_port %s is"
                                  " not proper under CSWITCH in config.ini"
                                  % config_entry,
                                  test_case_id, script_id, "None", "None",
                                  log_level,
                                  tbd)                                          # If failed to get config info, exit
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: config entry for cswitch_port %s is %s"
                                  " found under CSWICH in config.ini"
                                  % (config_entry, cswitch_port), test_case_id,
                                  script_id, "None", "None", log_level,
                                  tbd)
            return connect_disconnect_typec_sources(source, type, cswitch_port,
                                                    test_case_id, script_id,
                                                    log_level, tbd)
        else:
            relay = utils.ReadConfig("TTK", source)                             # Read Relay details from config for the source to connect

            if "NC" == relay:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "power rework not connected to TTK relay"
                                  % source, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            elif "NA" == relay:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "power rework not Applicable for the target "
                                  "system" % source, test_case_id, script_id,
                                  "None", "None", log_level, tbd)
                return True
            elif "fail:" in relay.lower():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "power rework details not updated in "
                                  "Config.ini" % source, test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s power "
                                  "source rework is connected to Relay number "
                                  "%s in TTK" % (source, relay), test_case_id,
                                  script_id, "None", "None", log_level, tbd)

                relay_action = library.ttk_set_relay(on_off_flag, int(relay),
                                                     test_case_id, script_id,
                                                     log_level, tbd)

                if 0 == relay_action:
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s of %s "
                                      "source is successful using TTK"
                                      % (type, source), test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    time.sleep(lib_constants.FIVE_SECONDS)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                      "of %s power failed" % (type, source),
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : connect_disconnect_ac_power_presi
# Parameters    : loglevel
# Functionality : This will connect or disconnect ac
# Return Value  : True/False
################################################################################


def connect_disconnect_ac_power_presi(type, source, test_case_id, script_id,
                                      loglevel="ALL", tbd=None):

    if "DISCONNECT" == type:
        on_off_flag = 'OFF'
    else:
        on_off_flag = 'ON'

    try:
        if "OFF" == on_off_flag:
            cmd = lib_constants.TOOLPATH + \
                "\\simicscimport utilsmd.exe detach-ac"
            process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: Disconnect AC"
                                  "power source fails using simics cmd",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return False
            else:
                time.sleep(lib_constants.SHORT_TIME)
                library.write_log(lib_constants.LOG_INFO, "INFO: Disconnected "
                                  "AC power source using simics cmd",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return True
        elif "ON" == on_off_flag:
            cmd = lib_constants.TOOLPATH + "\\simicscmd.exe attach-ac"
            process = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if len(stderr) > 0:
                library.write_log(lib_constants.LOG_INFO, "INFO: Connecting "
                                  "AC power source fails using simics cmd",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return False
            else:
                time.sleep(lib_constants.SHORT_TIME)
                library.write_log(lib_constants.LOG_INFO,"INFO: Connected AC "
                                  "power source using simics cmd",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
        return False


def AC_POWER_ON_SOUNDWAVE():
    current_state = StateTransition().get_state()
    if current_state != state.POWER_STATE_S0:
        library.write_log(lib_constants.LOG_INFO, "Current Power state is not S0 So AC powering ON..", "None", "None",
                          "None", "None", "None", "None")
        ret = soundwave.SoundWave()
        ret.ac_power_on()
        library.write_log(lib_constants.LOG_INFO, "Ac power ON success", "None", "None", "None", "None", "None", "None")
        return True
    else:
        library.write_log(lib_constants.LOG_INFO, "Ac power ON is Not success", "None", "None", "None", "None", "None",
                          "None")


def AC_POWER_OFF_SOUNDWAVE():
    current_state = StateTransition().get_state()
    if current_state != state.POWER_STATE_S0:
        library.write_log(lib_constants.LOG_INFO, "Current Power state is not S0 So AC powering ON..", "None", "None",
                          "None", "None", "None", "None")
        ret = soundwave.SoundWave()
        ret.ac_power_off()
        library.write_log(lib_constants.LOG_INFO, "Ac power ON success", "None", "None", "None", "None", "None", "None")
        return True
    else:
        library.write_log(lib_constants.LOG_INFO, "Ac power ON is Not success", "None", "None", "None", "None", "None",
                          "None")


def DC_POWER_PRESS_SOUNDWAVE():
    ret = soundwave.SoundWave()
    ret.press_power_button()
    ret.release_power_button()
    library.write_log(lib_constants.LOG_INFO, "press power button and Success..", "None", "None",
                      "None", "None", "None", "None")


def connect_disconnect_typec_sources(source, type, cswitch_port, test_case_id,
                                     script_id, log_level, tbd):
    try:
        cswitch_device_id = "CSWITCH_ID_" + source.upper()
        cswitch_id = utils.ReadConfig("CSWITCH", cswitch_device_id)
        if "FAIL" in cswitch_id.upper() or 'NC' in cswitch_id.upper() or \
                        'NA' in cswitch_id.upper():
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: config entry for "
                              "%s is not proper under CSWITCH in "
                              "config.ini" % cswitch_device_id,
                              test_case_id, script_id, "None", "None",
                              log_level,
                              tbd)                                              # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: config entry for %s is %s "
                              "found under CSWICH in config.ini"
                              % (cswitch_device_id, cswitch_id), test_case_id,
                              script_id, "None", "None", log_level,
                              tbd)                                              # Continie to remaining steps as config entry is fetched
        if "DISCONNECT" == type.upper():
            if lib_cswitch.cswitch_unplug(cswitch_id, test_case_id, script_id,
                                          log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Disconnected %s successfully" % source,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to disconnect %s" % source,
                                  test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "CONNECT" == type.upper():
            if lib_cswitch.cswitch_plug(cswitch_id, cswitch_port, test_case_id,
                                        script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Connected %s successfully" % source,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to connect %s" % source,
                                  test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: CSwitch Action is not defined - %s"
                              % type,
                              test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s"
                          % e_obj, test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return False


def power_source_actions(tool_name, power_source, action, test_case_id,
                         script_id, log_level, tbd):                            # Function calling for to Connect/Disconnect or ON/OFF AC/DC

    try:
        if "TTK" == tool_name.upper():
            return connect_disconnect_power_ttk(power_source, action,
                                                test_case_id, script_id,
                                                log_level, tbd)
        elif "SOUNDWAVE" == tool_name.upper():
            if "AC" == power_source and "ON" == action:
                return AC_POWER_ON_SOUNDWAVE()
            elif "AC" == power_source and "OFF" == action:
                return AC_POWER_OFF_SOUNDWAVE()
            elif "DC" == power_source:
                return DC_POWER_PRESS_SOUNDWAVE()
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Connect or "
                              "Disconnect Power Source using tool is not "
                              "implemented", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "ht:s:a:",)
    except getopt.GetoptError:
        print("Please use -h command for Help Message")
        print("Usage: lib_connect_disconnect_power_source.py -h")
        return False

    try:
        if 0 == len(opts):
            print("Please use -h command for Help Message")
            print("Usage: lib_connect_disconnect_power_source.py -h")
            return False
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print("##################################################\n")
                    print("Description:\n\tThis API aims to do ON/OFF or " \
                          "Connect/Disconnect Power source like AC or DC " \
                          "using Tools like TTK, Soundwave etc.\n")

                    print("Arguments:\n-h\n\t For printing the help message\n")

                    print("-t\n\t Tool name e.g TTK, SoundWave\n")

                    print("-s\n\t Power Source like AC, DC\n")

                    print("-a\n\t action e.g ON, OFF, Connect, Disconnect\n")

                    print("Usage:\n\tlib_connect_disconnect_power_source.py " \
                          "-t <Tool Name> -s <Power_source> -a <Action>\n")
                    print("####################################################")
                    return True
                elif opt in "-t":
                    tool_name = arg
                elif opt in "-s":
                    power_source = arg
                elif opt in "-a":
                    action = arg
                else:
                    return False
            power_source_actions(tool_name, power_source, action, "None",
                                 "None", "ALL", "None")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
