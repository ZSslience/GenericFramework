__author__ = r'kvex/patnaikx/nareshgx/shivbalanx/hvinayx/skotasiv/sushil3x/' \
    r'tnaidux/jpuklatx'

# Global Python Imports
import codecs
import glob
import os
import re
import subprocess
import time
import wmi

# Local Python Imports
import library
import lib_boot_to_environment
import lib_constants
import lib_display_configuration_in_os
import lib_get_system_properties
import lib_set_bios
import lib_verify_device_enumeration
import lib_verify_display_with_display_properties
import utils
import lib_cswitch
import KBM_Emulation as kbm
import lib_set_power_plan

# Global Variables
flag = ""
ip_found = ""


################################################################################
# Function Name : plug_unplug
# Parameters    : tc_id, script_id, action, config, log_level, tbd
# Return Value  : True on performing relay action/False on Failure
# Purpose       : setGPIO() library in pyttk module used to turn on/off devices
################################################################################


def plug_unplug(tc_id, script_id, action, config, device, ostr, log_level="ALL",
                tbd=None):

    try:
        if "DISPLAY" in device:                                                 # If display in device continue to execution
            result = plug_unplug_display(tc_id, script_id, action, device,
                                         log_level, tbd)                        # Function to execute a command - plug & unplug the display

            if True == result:                                                  # If command is executed successfully then pass message is printed else false message is printed
                library.write_log(lib_constants.LOG_INFO, "INFO: %s device is "
                                  "successful %s using she tool"
                                  % (device, action), tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "device is un-successful %s using she tool"
                                  % (device, action), tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # If exception found in plug & unplug return false

    if "TYPE-C" in ostr.upper() or "TYPEC" in ostr.upper():
        config_entry = "CSWITCH_" + config.upper()
        cswitch_port = utils.ReadConfig("CSWITCH", config_entry)
        if "FAIL" in cswitch_port.upper() or 'NC' in cswitch_port.upper() \
                or 'NA' in cswitch_port.upper():
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: config entry for cswitch_port %s is not"
                              " proper under CSWITCH in config.ini" 
                              % config_entry,
                              tc_id, script_id, "None", "None",
                              log_level, tbd)                                   # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: config entry for cswitch_port %s is %s "
                              "found under CSWICH in config.ini"
                              % (config_entry, cswitch_port), tc_id,
                              script_id, "None", "None", log_level,
                              tbd)                                              # Continie to remaining steps as config entry is fetched
        return cswitch_plug_unplug(action, cswitch_port, config, script_id,
                                   tc_id, log_level, tbd)
    else:
        try:                                                                    # Get the config entry of port where device is connected
            config_entry = config.upper()
            port = utils.ReadConfig("PLUG_UNPLUG", config_entry)

            if "FAIL" in port or 'NC' in port.upper() or 'NA' in port.upper():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: config "
                                  "entry for port %s is not proper under "
                                  "PLUG_UNPLUG in config.ini" % config_entry,
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)                                          # If failed to get config info, exit
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: config entry for "
                                  "port %s is %s found under PLUG_UNPLUG in "
                                  "config.ini" % (config_entry, port), tc_id,
                                  script_id, "None", "None", log_level, tbd)    # Continie to remaining steps as config entry is fetched
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False

        try:
            if "HOT-UNPLUG" == action or "COLD-UNPLUG" == action:
                if 0 == library.ttk_set_relay("OFF", int(port), log_level, tbd):# Relay action OFF
                    library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                      "performed successfully", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                      "to perform TTK action", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
            elif "HOT-PLUG" == action or "COLD-PLUG" == action:
                if 0 == library.ttk_set_relay("ON", int(port), tc_id, script_id,
                                              log_level, tbd):                  # Relay action ON
                    library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                                      "performed successfully", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                      "to perform TTK action", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: TTK Action "
                                  "is not defined - %s" % action, tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False

################################################################################
# Function Name : check_device
# Parameters    : tc_id, script_id, device_name, log_level, tbd
# Return Value  : True on finding the device listed in device manager/False
# Purpose       : to check if a device is present in sut (device manager) or not
################################################################################


def check_device(device, tc_id, script_id, device_name, log_level="ALL",
                 tbd=None):
    status = "None"
    try:
        if "DISPLAY" in device.upper():
            time.sleep(lib_constants.TEN)
            device = device.split('-')[0]
            log_file = script_id.replace('.py', '.txt')
            log_path = lib_constants.SCRIPTDIR + '\\' + log_file

            if os.path.exists(log_path):
                os.remove(log_path)


            result, display_log_path = display_log(tc_id, script_id,
                                                   log_level, tbd)

            if result is True:
                display_log_path = display_log_path.decode('iso-8859-1')
                with codecs.open(display_log_path, 'r') as file:
                    f_obj = file.read()
                    res = re.findall(r'.*Output Type:.*', f_obj)
                    for item in res:
                        if 'Output Type:' in item and 'Internal' in item and \
                                "EDP" in device.upper():
                            library.write_log(lib_constants.LOG_INFO,
                                              "INFO: EDP-Display Verified in SUT",
                                              tc_id, script_id, "None", "None",
                                              log_level, tbd)
                            status = 'Connected'
                        elif 'Output Type:' in item.strip() and 'Displayport External' \
                                in item.strip() and "DP" == device.upper():
                            library.write_log(lib_constants.LOG_INFO,
                                              "INFO: DP-Display Verified in SUT",
                                              tc_id, script_id, "None", "None",
                                              log_level, tbd)
                            status = 'Connected'
                        elif 'Output Type:' in item and 'HDMI' in item \
                                and "HDMI" in device.upper():
                            library.write_log(lib_constants.LOG_INFO,
                                              "INFO: HDMI-Display Verified in SUT",
                                              tc_id, script_id, "None", "None",
                                              log_level, tbd)
                            status = 'Connected'
                        else:
                            pass

                if status == 'Connected':
                    return 'Connected'
                else:
                    library.write_log(lib_constants.LOG_WARNING,
                                      "WARNING: %s is not connected "
                                      "to SUT" % device,
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    return 'Not Connected'
        elif "PENDRIVE" in device.upper() or "HDD" in device.upper():
            device_mount_point = utils.ReadConfig("PLUG_UNPLUG",
                                                  "%s_MOUNT_POINT" % device)
            if "FAIL:" in device_mount_point:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to get the config entry for"
                                  " %s_MOUNT_POINT under [PLUG_UNPLUG]"
                                  % device, tc_id, script_id,
                                  "None", "None", log_level,
                                  tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Config entry found for "
                                  "%s_MOUNT_POINT under [PLUG_UNPLUG]" % device,
                                  tc_id, script_id, "None", "None",
                                  log_level,
                                  tbd)

            script_log_path = lib_constants.SCRIPTDIR + '\\' + \
                              script_id.replace(".py", ".txt")
            if os.path.exists(script_log_path):
                os.remove(script_log_path)

            os.chdir(lib_constants.USBTREEVIEW_PATH)
            command = lib_constants.USBTREEVIEW_EXE + " /R:" +\
                      os.path.join(script_log_path)
            result = os.system(command)

            if result == 1:
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: Command to get the USBTreeView"
                                  " log ran successfully",
                                  tc_id, script_id, "None", "None",
                                  log_level,
                                  tbd)

            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to run the usbtreeview"
                                  " command to get the device details",
                                  tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            if os.path.exists(script_log_path):
                with codecs.open(script_log_path, 'r', encoding='utf-16', errors='replace') as file:
                    for line in file:
                        if "Device Description" in line and\
                                "Mass Storage Device" in line:
                            for temp in range(100):
                                line = next(file)
                                if "Mountpoint" in line and\
                                        device_mount_point in line:
                                    status = "Connected"
                                    break
                                else:
                                    continue
                if status == "Connected":
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: %s is found in USBTreeViewLog"
                                      % device, tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return "Connected"
                else:
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: %s is not found in USBTreeViewLog"
                                     % device, tc_id, script_id,
                                     "None", "None", log_level, tbd)
                    return "Not Connected"

        elif device in lib_constants.WMI_CHECK:                                 # Check for device if it is  listed as device manager enumerated
            c = wmi.WMI()
            found = False
            for devices in c.Win32_PnPEntity():                                 # If device found in list
                if devices.Name is not None:
                    if device_name.upper() == devices.Name.upper():
                        found = True
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                          "is found in device manager list"
                                          % device_name, tc_id, script_id,
                                          "None", "None", log_level, tbd)
                        return "Connected"
            return "Not Connected"
        elif "DEAD-BATTERY" == device.upper():
            output = ""
            cmd_to_run = lib_constants.BATTERY_PERCENTAGE_CMD
            for filename in os.listdir("."):                                    # Check for filename in directory for nsh
                if filename.endswith("ps1"):                                    # If any nsh file is there unlink the file
                    os.unlink(filename)

            myFile = open("psquery.ps1", "w")
            myFile.write(cmd_to_run)
            myFile.close()
            time.sleep(lib_constants.FIVE_SECONDS)                              # Sleep for 5 seconds to generate power shell file
            powershell_path = utils.ReadConfig("WIN_POWERSHELL", "PATH")        # Read from power shell the value of power shell path

            if "FAIL" in powershell_path:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry of powershell_path is not proper",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)

            shell_script = 'psquery.ps1'                                        # Shell script should be placed in script directory
            exe_path = os.path.join(lib_constants.SCRIPTDIR, shell_script)

            final_command = 'powershell.exe ' + exe_path
            try:
                os.chdir(powershell_path)
                output = os.popen(final_command).read()
                output = int(re.search(r'\d+', output).group())
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to "
                                  "%s" % e, tc_id, script_id, "None", "None",
                                  log_level, tbd)

            if "" != output:
                if 0 == output:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Dead "
                                      "battery found", tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return "Connected"
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Dead battery not found", tc_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return "Not Connected"
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Dead "
                                  "battery not found", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return "Connected"
        elif "TPM" in device.upper():
            cmd_to_run = lib_constants.TPM_ENUMUERATION_CHECK
            new_script_id = script_id.strip(".py")
            log_file = new_script_id + '.txt'
            script_dir = lib_constants.SCRIPTDIR
            log_path = script_dir + "\\" + log_file
            cmd = cmd_to_run + ">" + log_path

            try:
                os.system(cmd)
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                                  "running command for getting tpm info %s"
                                  % e, tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            os.chdir(lib_constants.SCRIPTDIR)
            if os.path.exists(log_path):
                with codecs.open(log_path, 'r', "windows-1252") as f:           # For wmic tpm log, read with windows-1252
                    for line in f:
                        la = ''                                                 # Remove spaces in the log content
                        ls = ''
                        lg = ''
                        ls = re.split('\x00 |\x00', line)                       # Remove junk characters
                        la = la.join(ls)
                        line = la
                        ls = line.split('\t')
                        lg = lg.join(ls)
                        line = lg

                        if device_name.upper() in line.upper():
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "%s is found in device list"
                                              % device_name, tc_id, script_id,
                                              "None", "None", log_level, tbd)
                            return "Connected"
                return "Not Connected"
        elif "wifi-module" in device.lower() or "CNVI" in device.upper():
            flag = False
            os.system('netsh interface show interface > wifi_check.txt')

            with open("wifi_check.txt", "r") as f_:
                output = f_.readlines()
                for line in output:
                    if "Wi-Fi" in line:
                        flag = True
                        break

            if False == flag:
                return "Not Connected"
            else:
                return "Connected"
        else:
            if device in lib_constants.NONBOOTABLE_DEVICES or \
               device in lib_constants.BOOTABLE_DEVICES:                        # If device is in nonbootable or bootable devices
                result = lib_get_system_properties.\
                    get_device_properties(device, tc_id, script_id, log_level,
                                          tbd)                                  # Function calling to get the device property whether it is bootable or nonbootable
                if False == result or None == result:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to get %s properties" % device,
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)                           # Writing log info message to the log file
                    return "Not Connected"

            usb_view = utils.ReadConfig("USB_VIEW", "EXE_FILE")

            if "FAIL" in usb_view:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get the config entry EXE_FILE under "
                                  "[USB_VIEW]", tc_id, script_id, "None",
                                  "None", log_level, tbd)                       # If failed to get config info, exit
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: config entry "
                                  "EXE_FILE under [USB_VIEW] fetched", tc_id,
                                  script_id, "None", "None", log_level, tbd)    # Continue to remaining steps as config entry is fetched

            command = ""

            if os.path.exists(usb_view):
                command = usb_view + " /f /q /saveall:" + \
                    os.path.join(lib_constants.SCRIPTDIR,
                                 script_id.replace(".py", ".txt"))
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Path "
                                  "%s does not exists" % usb_view, tc_id,
                                  script_id, "None", "None", log_level, tbd)

            if os.path.isfile(script_id.replace(".py", ".txt")):
                os.remove(script_id.replace(".py", ".txt"))

            os.system(command)

            try:
                log_file = open(os.path.join(lib_constants.SCRIPTDIR,
                                             script_id.replace(".py", ".txt")),
                                "r")
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to "
                                  "%s" % e, tc_id, script_id, "None", "None",
                                  log_level, tbd)                               # Writing log error message to the log file
                return False

            for line in log_file:                                               # Parse through the log file
                if device_name.upper() in line.upper():                         # If device name is available in any line, pass
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s is "
                                      "found in device list" % device_name,
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)                           # Writing log info message to the log file
                    return "Connected"

            library.write_log(lib_constants.LOG_WARNING, "WARNING: %s is not "
                              "found in device list" % device_name, tc_id,
                              script_id, "None", "None", log_level, tbd)        # Writing log info message to the log file
            return "Not Connected"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)     # Writing log error message to the log file
        return False

################################################################################
# Function Name : sensor_hub_enumeration
# Parameters    : sensor, tc_id, script_id, log_level="ALL",tbd=None
# Return Value  : True/False
# Purpose       : To verify enumeration of sensor's in sensor hub
################################################################################


def sensor_hub_enumeration(sensor, tc_id, script_id, log_level="ALL",
                           tbd=None):

    try:
        global flag                                                             # To check all sensor flag is set to ""
        sensor_to_verify = ''

        if tbd.upper() == "KBL" or tbd.upper() == "KBLR":
            sensor_to_verify = lib_constants.SENSOR_HUB_KBL
        elif tbd.upper() == "APL":
            sensor_to_verify = lib_constants.SENSOR_HUB_APL
        elif tbd.upper() == "GLK":
            sensor_to_verify = lib_constants.SENSOR_HUB_GLK
        elif tbd.upper() == "CNL":
            sensor_to_verify = lib_constants.SENSOR_HUB_CNL
        elif tbd.upper() == "CFL":
            sensor_to_verify = lib_constants.SENSOR_HUB_CFL
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Platform "
                              "not handle", tc_id, script_id, "None", "None",
                              log_level, tbd)

        for sensor in sensor_to_verify:                                         # For each sensor call lib_verify_enumeration and verify
            sensor = sensor + '-SENSOR'
            status = lib_verify_device_enumeration.actionmanager_enumeration(
                sensor, tc_id, script_id, log_level, tbd)
            if status:                                                          # If true set flag to true
                flag = True
            else:                                                               # If false set flag to false and break
                flag = False
                break

        if not flag:                                                            # If flag is false return false
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Sensor "
                              "verification/enumeration failed", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
        else:                                                                   # Else return true
            library.write_log(lib_constants.LOG_INFO, "INFO: All sensor "
                              "enumeration verified", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return True
    except Exception as e:                                                      # If exception found in verifying return false
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : read_devcon_ip_address
# Parameters    : device,tc_id, script_id, action, config, loglevel, tbd
# Return Value  : true/false with ip
# Purpose       : to retrieve ip address of device
################################################################################


def read_devcon_ip_address(device, test_case_id, script_id, loglevel, tbd):

    global ip_found
    if 'usb-lan' in device.lower():                                             # Assign lan device name
        device = 'USB'
        lan_type = 'USB-LAN'
    elif 'usb-ethernet-dongle' in device.lower():
        device = utils.ReadConfig("WIFI", "usb_lan")
        lan_type = 'USB-LAN'
    elif 'pcie' in device.lower():
        device = 'Gigabit'
        lan_type = 'PCIE-LAN'
    elif 'onboard' in device.lower():
        if 'GLK' == tbd.upper():
            device = 'Realtek'
            lan_type = 'Onboard-LAN'
        else:
            device = 'Ethernet Connection'
            lan_type = 'Onboard-LAN'
    elif 'wifi' in device.lower():
        device = 'Wireless-AC'
        lan_type = 'WIFI'
    elif '' in device.lower() or ' ' in device.lower():
        if 'GLK' == tbd.upper():
            device = 'Realtek'
            lan_type = 'Onboard-LAN'
        else:
            device = 'Ethernet Connection'
            lan_type = 'Onboard-LAN'
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: LAN cold plug "
                          "for %s is not supported" % device, test_case_id,
                          script_id, "None", "None", loglevel, tbd)
        return False, 'FAIL'                                                    # Return false not supported

    devcon_path = utils.ReadConfig("Cold_Plug", "devcon_path")            # Read devcon path from
    if "FAIL" in devcon_path or "FAIL" in device:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Devcon path "
                          "entry is missing from config under the header %s"
                          % "Cold_Plug", test_case_id, script_id, "None",
                          "None", loglevel, tbd)
        return False, 'FAIL'                                                    # Return false if path is missing
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Devcon path Found %s "
                          "and device from config.ini" % devcon_path,
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)

    os.chdir(devcon_path)                                                       # Change to devcon path
    command = lib_constants.FIND_ALL_DEVICE_LIST_CMD                            # 'devcon.exe Find * > devices.txt'  , # finds all the displayed and existing device in device manager
    cmd_exe = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    time.sleep(lib_constants.THREE)                                             # Execute bat file in subprocess wait for 3 seconds

    if os.path.exists("devices.txt"):
        library.write_log(lib_constants.LOG_INFO, "INFO: Devcon log file "
                          "found %s " % (os.path.abspath("device.txt")),
                          test_case_id, script_id, "None", "None", loglevel,
                          tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Devcon log file"
                          " not found ", test_case_id, script_id, "None",
                          "None", loglevel, tbd)
        return False, "FAIL"

    with open("devices.txt", "r") as file:                                      # Read the first file
        wifi_module = utils.ReadConfig('WIFI', 'device_enumeration')
        for line in file:                                                       # Iterate through the lines
            if (device.upper() in line.upper()) and \
                    ("Ethernet" in line or "Adapter" in line):                  # Check for device in each line
                os.chdir(lib_constants.SCRIPTDIR)
                command = lib_constants.IP_DETAILS_CMD                          # Finds all the displayed and existing device in device manager
                cmd_exe = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stdin=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)            # Execute bat file in subprocess
                time.sleep(lib_constants.THREE)                                 # Wait for 3 seconds
                if os.path.exists("ipdetails.txt"):                             # Check for file
                    library.write_log(lib_constants.LOG_INFO, "INFO: IPconfig "
                                      "log file found %s "
                                      % (os.path.abspath("ipdetails.txt")),
                                      test_case_id, script_id, "None", "None",
                                      loglevel, tbd)
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "IPconfig log file not found",
                                      test_case_id, script_id, "None", "None",
                                      loglevel, tbd)
                    return False, "FAIL"

                with open("ipdetails.txt", "r") as file:                        # Read the first file
                    for line in file:
                        if device.upper() in line.upper():                      # If device id found in log file line continue else fail
                            for i, line in enumerate(file):
                                if 'IPv4 Address' in line and i <= \
                                        lib_constants.FOUR:                     # To retrieve ip address check for next 4 line if found pass and return true with ip address
                                    ip_found = (line.split(':')[1]).\
                                        replace('(Preferred)', '').strip()
                                    library.write_log(lib_constants.LOG_INFO,
                                                      "INFO: %s is plugged and "
                                                      "verified" % lan_type,
                                                      test_case_id, script_id,
                                                      "None", "None", loglevel,
                                                      tbd)
                                    return True, ip_found

                library.write_log(lib_constants.LOG_WARNING, "WARNING: Device "
                                  "ID not found in device manager",
                                  test_case_id, script_id, "None", "None",
                                  loglevel, tbd)
                return False, 'FAIL'                                            # If nothing found from device log then return false and fail
            elif device.upper() in line.upper() or wifi_module.upper() in \
                    line.upper():                                               # For wifi-module
                file_name = 'wlan_profile.xml'
                ap_name = utils.ReadConfig('WIFI', 'ap_name')
                ap_password = utils.ReadConfig('WIFI', 'ap_password')
                wlan_profile = lib_constants.WLAN_PROFILE_XML
                os.chdir(lib_constants.SCRIPTDIR)
                ap_name_hex = ap_name.encode("hex")
                f_name = re.search(r'<name>(.*?)</name>', wlan_profile)
                name_replace = map(str, f_name.groups())[0]
                f_hex = re.search(r'<hex>(.*?)</hex>', wlan_profile)
                hex_replace = map(str, f_hex.groups())[0]
                f_pass = re.search(r'<keyMaterial>(.*?)</keyMaterial>',
                                   wlan_profile)
                pass_replace = map(str, f_pass.groups())[0]
                wlan_profile = wlan_profile.replace(name_replace, ap_name)\
                    .replace(hex_replace, ap_name_hex).replace(pass_replace,
                                                               ap_password)
                s = open(file_name, mode='wb')
                s.write(wlan_profile)
                s.close()

                if os.path.exists(file_name):
                    cmd_profile = lib_constants.WLAN_NETSH_PROFILE_CMD + \
                        ' ' + file_name
                    cmd_out = subprocess.Popen(cmd_profile, shell=False,
                                               stdout=subprocess.PIPE,
                                               stdin=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)        # Check for Profile id if found continue
                    if 'Profile' in cmd_out.communicate()[0]:
                        library.write_log(lib_constants.LOG_INFO, "INFO: WLAN "
                                          "profile has been added "
                                          "successfully", test_case_id,
                                          script_id, "None", "None", loglevel,
                                          tbd)
                        cmd_connect = lib_constants.WLAN_NETSH_CONNECT_CMD + \
                            ' ' + ap_name
                        cmd_out = subprocess.Popen(cmd_connect, shell=False,
                                                   stdout=subprocess.PIPE,
                                                   stdin=subprocess.PIPE,
                                                   stderr=subprocess.STDOUT)    # Check for connection if found continue
                        if 'Connection' in cmd_out.communicate()[0]:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "WIFI connection established",
                                              test_case_id, script_id, "None",
                                              "None", loglevel, tbd)
                            time.sleep(lib_constants.TEN_SECONDS)               # Sleep for 10 seconds to get IP address of wifi module
                            command = lib_constants.IP_DETAILS_CMD              # Finds all the displayed and existing device in device manager
                            cmd_exe = subprocess.Popen(command, shell=True,
                                                       stdout=subprocess.PIPE,
                                                       stdin=subprocess.PIPE,
                                                       stderr=subprocess.STDOUT)# Execute bat file in subprocess
                            time.sleep(lib_constants.THREE)                     # Wait for 3 seconds to generate file
                            if os.path.exists("ipdetails.txt"):                 # Check for file
                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: IPconfig log file "
                                                  "found %s "
                                                  % (os.path.abspath
                                                     ("ipdetails.txt")),
                                                  test_case_id, script_id,
                                                  "None", "None", loglevel,
                                                  tbd)
                            else:
                                library.write_log(lib_constants.LOG_WARNING,
                                                  "WARNING: IPconfig log file "
                                                  "not found", test_case_id,
                                                  script_id, "None", "None",
                                                  loglevel, tbd)
                                return False, "FAIL"

                            with open("ipdetails.txt", "r") as file:            # Read the first file
                                for line in file:
                                    if device.upper() in line.upper():          # If device id found in log file line continue else fail
                                        for i, line in enumerate(file):
                                            if 'IPv4 Address' in line and i <= \
                                                    lib_constants.FIVE:         # To retrieve ip address check for next 4 line if found pass and return true with ip address
                                                ip_found = (line.split(':')
                                                            [1]).replace(
                                                    '(Preferred)', '').strip()
                                                library.write_log(lib_constants.
                                                                  LOG_INFO,
                                                                  "INFO: %s is"
                                                                  " plugged and"
                                                                  " verified"
                                                                  % lan_type,
                                                                  test_case_id,
                                                                  script_id,
                                                                  "None",
                                                                  "None",
                                                                  loglevel,
                                                                  tbd)
                                                return True, ip_found
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "WIFI profile file not found",
                                      test_case_id, script_id, "None", "None",
                                      loglevel, tbd)
                    return False, 'FAIL'

    library.write_log(lib_constants.LOG_WARNING, "WARNING: Device ID not found"
                      " in device manager", test_case_id, script_id, "None",
                      "None", loglevel, tbd)
    return False, 'FAIL'

################################################################################
# Function Name : plug_unplug_lid_donothing
# Parameters    : action, device,tc_id, script_id, action, config, log_level,
#                 tbd
# Return Value  : True on performing relay action/False on Failure
# Purpose       : to set the lid switch action to do nothing
################################################################################


def plug_unplug_lid_donothing(tc_id, script_id, log_level="ALL", tbd=None):

    try:
        pwrsettingname = "LID CLOSE ACTION"
        mysetting = 0

        ac_power_setting =\
            lib_set_power_plan.update_power_option_all(tc_id, script_id,
                                                       pwrsettingname,
                                                       mysetting,
                                                       "AC",
                                                       log_level, tbd)
        dc_power_setting = \
            lib_set_power_plan.update_power_option_all(tc_id, script_id,
                                                       pwrsettingname,
                                                       mysetting,
                                                       "DC",
                                                       log_level, tbd)
        if ac_power_setting is True and dc_power_setting is True:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Lid Close Action has set to Do Nothing"
                              " Scuccessfully",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR,
                              "ERROR: Failed to set Lid Close Action to"
                              " Do Nothing",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # Print the exception message, if any exception mails occured

################################################################################
# Function Name : run_plug_unplug_display_cmd1
# Parameters    : plug_unplug_cmd,tc_id, script_id, action, config, log_level,
#                 tbd
# Return Value  : True, if she tool command is executed  successfully or False,
#                 otherwise
# Purpose       : to run SHE tool command for hot - cold plug display
################################################################################


def run_plug_unplug_display_cmd1(plug_unplug_cmd, action, device, tc_id,
                                 script_id, log_level="ALL", tbd=None):         # Function to run SHE tool command

    she_tool_path = utils.ReadConfig("SHE_TOOL_DISPLAY", "she_tool_path")       # Taking she tool path from config
    if "FAIL" in she_tool_path:                                                 # Checking whether config entries provided or not
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Config entry "
                          "is not provided under tag [SHE_TOOL_DISPLAY]",
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Config entry is "
                          "provided under tag [SHE_TOOL_DISPLAY]", tc_id,
                          script_id, "None", "None", log_level, tbd)

    if os.path.exists(she_tool_path):                                           # Checking the path of she tool
        library.write_log(lib_constants.LOG_INFO, "INFO: SHE Tool path found",
                          tc_id, script_id, "None", "None", log_level, tbd)
        pass
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to find "
                          "SHE Tool path", tc_id, script_id, "None", "None",
                          log_level, tbd)
        return False

    os.chdir(she_tool_path)
    p = subprocess.Popen(plug_unplug_cmd, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True)                                            # Running the command for display
    out = p.communicate()[0]

    if "Success:" in out:
        library.write_log(lib_constants.LOG_INFO, "INFO: %s %s command "
                          "executed successfully" % (device, action), tc_id,
                          script_id, "None", "None", log_level, tbd)
        flag = True
        return flag                                                             # Return true if command is pass
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: %s %s "
                          "command execution is unsuccessful" %(device,
                                                                action),
                          tc_id, script_id, "None", "None", log_level, tbd)
        flag = False
        return flag                                                             # Return fail if command is not passed

################################################################################
# Function Name : plug_unplug_display
# Parameters    : tc_id, script_id, action, device, log_level, tbd
# Return Value  : True, if action is performed for hot-cold plug display or
#                 False, if action is not performed for hot-cold plug display
# Purpose       : to hot-cold display
################################################################################


def plug_unplug_display(tc_id, script_id, action, device, log_level="ALL",
                        tbd=None):                                              # Function to plug & un plug display

    try:
        time.sleep(lib_constants.SHORT_TIME)
        device = device.split('-')[0]

        if "HDMI" == device and "HOT-PLUG" == action:                           # HDMI - HOT PLUG command to run
            cmd_to_run = lib_constants.HDMI_PLUG_CMD
        elif "HDMI" == device and "HOT-UNPLUG" == action:                       # HDMI - HOT UNPLUG command to run
            cmd_to_run = lib_constants.HDMI_UNPLUG_CMD
        elif "DP" == device and "HOT-PLUG" == action:                           # DP - HOT PLUG command to run
            cmd_to_run = lib_constants.DP_PLUG_CMD
        elif "DP" == device and "HOT-UNPLUG" == action:                         # DP - HOT UNPLUG command to run
            cmd_to_run = lib_constants.DP_UNPLUG_CMD
        elif "HDMI" == device and "COLD-PLUG" == action:                        # HDMI - COLD PLUG command to run
            cmd_to_run = lib_constants.HDMI_PLUG_CMD
        elif "HDMI" == device and "COLD-UNPLUG" == action:                      # HDMI - COLD UNPLUG command to run
            cmd_to_run = lib_constants.HDMI_UNPLUG_CMD,
        elif "DP" == device and "COLD-PLUG" == action:                          # DP - COLD PLUG command to run
            cmd_to_run = lib_constants.DP_PLUG_CMD
        elif "DP" == device and "COLD-UNPLUG" == action:                        # DP - COLD UNPLUG command to run
            cmd_to_run = lib_constants.DP_UNPLUG_CMD
        elif "EDP" == device and "COLD-PLUG" == action:                         # EDP - COLD PLUG command to run
            cmd_to_run = lib_constants.EDP_PLUG_CMD
        elif "EDP" == device and "COLD-UNPLUG" == action:                       # EDP - COLD UNPLUG command to run
            cmd_to_run = lib_constants.EDP_UNPLUG_CMD
        elif "VGA" == device and "COLD-PLUG" == action:                         # VGA - COLD PLUG command to run
            vga_hdmi1_conv_plug = utils.ReadConfig("LID_SWITCH",
                                                   "HDMI1_CONV_PLUG")
            library.write_log(lib_constants.LOG_INFO, "INFO: VGA Converter "
                              "should be connected to HDMI", tc_id, script_id,
                              "None", "None", log_level, tbd)
            if "FAIL" in vga_hdmi1_conv_plug:                                   # Checking if config entries is provided or not
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is not provided under tag "
                                  "[LID_SWITCH]", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                                  "is provided under tag [LID_SWITCH]", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                pass
            cmd_to_run = lib_constants.VGA_PLUG_CMD
        elif "VGA" == device and "COLD-UNPLUG" == action:                       # VGA - COLD UNPLUG command to run
            vga_hdmi1_conv_unplug = utils.ReadConfig("LID_SWITCH",
                                                     "HDMI1_CONV_UNPLUG")
            library.write_log(lib_constants.LOG_INFO, "INFO: VGA Converter "
                              "should be connected to HDMI", tc_id, script_id,
                              "None", "None", log_level, tbd)
            if "FAIL" in vga_hdmi1_conv_unplug:                                 # Checking if config entries is provided or not
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is not provided under tag "
                                  "[LID_SWITCH]", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                                  "is provided under tag [LID_SWITCH]", tc_id,
                                  script_id,"None", "None", log_level, tbd)
            cmd_to_run = lib_constants.VGA_UNPLUG_CMD
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Given "
                              "parameters is not implemented", tc_id,
                              script_id, "None", "None", log_level, tbd)        # Return false if parameter is not implemented
            return False

        flag = run_plug_unplug_display_cmd1(cmd_to_run, action, device, tc_id,
                                            script_id, log_level, tbd)          # Function to run the she tool commands

        if flag == True:
            return True
        else:
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # To print exception message

################################################################################
# Function Name : plug_unplug_display_verification
# Parameters    : device,tc_id, script_id, action, config, log_level, tbd
# Return Value  : True, if display is found or False, if display is not found
# Purpose       : to check which display is connected
################################################################################


def plug_unplug_display_verification(tc_id, script_id, device, log_level="ALL",
                                     tbd=None):

    try:
        time.sleep(lib_constants.TEN)
        device = device.split('-')[0]

        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")
        cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")                         # Read the tools directory path from the config and store in tool_dir

        if "FAIL:" in [tool_dir, cmd_to_run]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "value is missing in 'DISPLAY' section", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        if "VGA" in device:
            library.write_log(lib_constants.LOG_INFO, "INFO: VGA display "
                              "verified in HDMI", tc_id, script_id, "None",
                              "None", log_level, tbd)
            device = "HDMI"

        library.write_log(lib_constants.LOG_INFO, "INFO: Checking for "
                          "Connected display device", tc_id, script_id, "None",
                          "None", log_level, tbd)

        utils.filechangedir(tool_dir)                                           # Set controller to tools directory
        process = subprocess.Popen(cmd_to_run, shell=True,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()                                                          # Executing the command to get the connected display device
        process_output = process.communicate()

        if 0 == process_output:                                                 # If command is unsuccessfully
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Empty file "
                              "created fail to write the display information",
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False                                                        # Return "False"
        else:
            file = glob.glob("DisplayInfo.txt")                                 # Check for displayinfo.txt in the directory

            if [] == file:                                                      # If file is empty
                return False                                                    # Return "false"
            else:
                utils.filechangedir(tool_dir)                                   # Change to tools directory where tool is kept
                with open("DisplayInfo.txt", "r") as displayfile:               # File operation open file in utf-8 mode and save the texts in handle
                    filetext = displayfile.read()
                    displayfile.close()

                display_matches = re.findall("HDMI|EDP|DP|MIPI", filetext)      # Regular expression for checking different display type
                found_display_list = set(display_matches)                       # Creating set of found different display type

                if device in found_display_list:
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s is "
                                      "verified in SUT" % device, tc_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return "Connected"
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                      "is not verified in SUT" % device, tc_id,
                                      script_id, "None", "None", log_level, tbd)
                    return "Not Connected"
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False                                                            # To print exception message

################################################################################
# Function Name : plug_unplug_presi
# Parameters    : test_case_id, script_id, action, config, loglevel, tbd
# Return Value  : Return True when simics are successful else False
# Purpose       : To send commands to Simics console
################################################################################


def plug_unplug_presi(test_case_id, script_id, action, config, log_level="ALL",
                      tbd=None):

    suspend_simics = '"stop"'
    cmp_no = ""

    try:
        tbd = utils.ReadConfig('Platform', 'Name')
        if "FAIL" in tbd:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for platform is not proper", test_case_id,
                              script_id, "None", "None", log_level, tbd)        # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for "
                              "platform is %s in config.ini" % tbd,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Continue to remaining steps as config entry is fetched

        tool = lib_constants.TOOLPATH + "\\simicscmd.exe"                       # Getting simics tool path
        craff_image = utils.ReadConfig('Craff_image', 'location')

        if "FAIL" in craff_image:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for craff_image is not proper",
                              test_case_id, script_id, "None", "None",
                              log_level, craff_image)                           # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for "
                              "craff_image is %s in config.ini" % tbd,
                              test_case_id, script_id, "None", "None",
                              log_level, craff_image)                           # Continue to remaining steps as config entry is fetched

        if "USB-KEYBOARD" == config:                                            # Determining the device type
            comp = "keyboard"
            comp_name = "kbd1"
            if lib_boot_to_environment.simics_sendkeys(tool, suspend_simics):            # Pause simics session
                if lib_boot_to_environment.simics_sendkeys(tool, "icl.recorder.keyboard"
                                                        "_out.status"):         # Send "icl.recorder.keyboard_out.status" command to simics console
                    cmp_no = check_simicslog('cmp', comp, test_case_id,
                                             script_id, log_level, tbd)         # Check simics log if "Connections : icl.usb3_keyboard.connector_keyboard" is present
                    if cmp_no == "icl.usb3_keyboard":
                        library.write_log(lib_constants.LOG_INFO, "INFO: "
                                          "Keyboard already connected as %s "
                                          "skipping hot-plug " % cmp_no,
                                          test_case_id, script_id, "None",
                                          "None", log_level, "None")
                        if lib_boot_to_environment.simics_sendkeys(tool, 'c'):           # Resume simics session by sending 'c'
                            return True                                         # Return True if keyboard is already connected
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to send resume "
                                              "command to simics console",
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            return False                                        # Function exits by Returning False if Send Keys are unsuccessful
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " keyboard is not connected",
                                          test_case_id, script_id, "None",
                                          "None", log_level, "None")            # Continue to remaining steps as config entry is fetched
        elif "USB-MOUSE" == config:
            comp = "mouse"
            comp_name = "mouse1"

            if lib_boot_to_environment.simics_sendkeys(tool, suspend_simics):            # Pause simics session
                if lib_boot_to_environment.simics_sendkeys(tool, "icl.recorder.mouse_ou"
                                                        "t.status"):            # Send "icl.recorder.mouse_out.status" command to simics console

                    cmp_no = check_simicslog('cmp', comp, test_case_id,
                                             script_id, log_level, tbd)         # Check simics log if "Connections : icl.usb3_mouse.connector_mouse" is present
                    if cmp_no == "icl.usb3_mouse":
                        library.write_log(lib_constants.LOG_INFO, "INFO: mouse"
                                          " already connected as %s skipping "
                                          "hot-plug" % cmp_no, test_case_id,
                                          script_id, "None", "None", log_level,
                                          "None")
                        if lib_boot_to_environment.simics_sendkeys(tool, 'c'):           # Resume simics session by sending 'c'
                            return True                                         # Return True if mouse is already connected
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to send resume "
                                              "command to simics console",
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)
                            return False                                        # Function exits by Returning False if Send Keys are unsuccessful
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " keyboard is not connected",
                                          test_case_id, script_id, "None",
                                          "None", log_level, "None")            # Continue to remaining steps as config entry is fetched
        elif "USB3.0-PENDRIVE" == config:
            Craff_image = utils.ReadConfig('Craff_image', 'location')
            print(Craff_image)
            comp = "pendrive3.0"
        elif "USB2.0-PENDRIVE" == config or \
                "USB2.0-PENDRIVE_USB2.0-TYPE-A" == config:
            comp = "pendrive2.0"
        else:
            return False

        if "HOT-UNPLUG" == action:                                              # This block for Hot-UnPlug device
            if "mouse" == comp or "keyboard" == comp:
                cmd = lib_constants.\
                    DISCONNECT_MOUSE_KEYBOARD_PRESI % (comp_name, tbd.lower())  # Getting Simics command for Hot-unplug device
            elif "pendrive3.0" == comp or "pendrive2.0" == comp:
                fopen = open("usb_connector.log",mode='r')                      # Open usb_connector log file and read log
                loginfo = fopen.read()
                cmp_no = loginfo.split(":")[0]                                  # Fetch connector info from the usb_connector log
                port_no = loginfo.split(":")[1]                                 # Fetch port info from the usb_connector log
                if "pendrive2.0" == comp:
                    if "LKF" == tbd:
                        cmd = lib_constants.DISCONNECT_PENDRIVE2_PRESI_LKF % \
                            (cmp_no, port_no)                                   # Assign connector id and port no to cmd for disconnecting usb
                    else:
                        cmd = lib_constants.DISCONNECT_PENDRIVE2_PRESI % \
                            (cmp_no, port_no)                                   # Assign connector id and port no to cmd for disconnecting usb
                elif "pendrive3.0" == comp:
                    if "LKF" == tbd:
                        cmd = lib_constants.DISCONNECT_PENDRIVE3_PRESI_LKF % \
                            (cmp_no, port_no)                                   # Assign connector id and port no to cmd for disconnecting usb
                    else:
                        cmd = lib_constants.DISCONNECT_PENDRIVE3_PRESI % \
                            (cmp_no, port_no)                                   # Assign connector id and port no to cmd for disconnecting usb
                fopen.close()
            else:
                return False

            if lib_boot_to_environment.simics_sendkeys(tool, cmd):                       # Calling send keys function to send Hot-UnPlug command to Simics console
                library.write_log(lib_constants.LOG_INFO, "INFO: Hot-unplug "
                                  "command sent successfully to simics "
                                  "console", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                time.sleep(lib_constants.SLEEP_TIME)
                return True                                                     # Function exits by Returning True if Send Keys are successful
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to send hot-unPlug command to simics "
                                  "console", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False                                                    # Function exits by Returning False if Send Keys are unsuccessful
        elif "HOT-PLUG" == action:                                              # This block for Hot-Plug device
            if "mouse" == comp or "keyboard" == comp:
                cmd1 = lib_constants.CREATE_COMP_NAME_KBD_MOUSE_PRESI % \
                    (comp, comp_name)                                           # Getting Simics commands for Hot-Plug device
                cmd2 = lib_constants.CREATE_CONNECTOR_KBD_MOUSE_PRESI % \
                    (comp_name, tbd.lower())                                    # Getting connector id  command for Hot-Plug device
                cmd3 = lib_constants.INSTANTIATE_COMPONENTS_PRESI               # Command for instantiating components
            elif "pendrive2.0" == comp:
                cmd1 = lib_constants.LOAD_MODULE_PRESI                          # Assign load module command for usb2.0 pendrive
                cmd2 = lib_constants.CREATE_DISK_PENDRIVE2_PRESI % craff_image  # Create disk command for usb2.0 pendrive
            elif "pendrive3.0" == comp:
                cmd1 = lib_constants.LOAD_MODULE_PRESI                          # Assign load module command for usb2.0 pendrive
                cmd2 = lib_constants.CREATE_DISK_PENDRIVE3_PRESI % craff_image  # Create disk command for usb2.0 pendrive

            if lib_boot_to_environment.simics_sendkeys(tool, suspend_simics):            # Calling send keys function to send stop command to Simics console to suspend simics simulation
                if lib_boot_to_environment.simics_sendkeys(tool, cmd1):                  # Calling send keys function to send Hot-Plug command to Simics console
                    if lib_boot_to_environment.simics_sendkeys(tool, cmd2):
                        if "pendrive2.0" == comp or "pendrive3.0" == comp:      # To get connector id value to pass it to 3rd command for usb 3.0 hotplug
                            cmp_no = check_simicslog('cmp', comp, test_case_id,
                                                     script_id, log_level,
                                                     tbd)                       # Calling check_simicslog function to get the connector information for usb from simics log
                            port_no = disconnect_usb_presi(test_case_id,
                                                           script_id,
                                                           log_level, tbd)      # Calling disconnect_usb_presi function to get the port_no
                            if "pendrive2.0" == comp:
                                if "LKF" == tbd:
                                    cmd3 = lib_constants.\
                                        CONNECT_USB2_COMMAND_PRESI_LKF % \
                                        (cmp_no, port_no)                       # Assigning connector id and port number of usb 2.0 disk to cmd3
                                else:
                                    cmd3 = lib_constants.\
                                        CONNECT_USB2_COMMAND_PRESI % \
                                        (cmp_no, port_no)                       # Assigning connector id and port number of usb 2.0 disk to cmd3
                            else:
                                cmd3 = lib_constants.\
                                    CONNECT_USB3_COMMAND_PRESI_LKF % \
                                    (cmp_no, port_no)                           # Assigning connector id and port number of usb 3.0 disk to cmd3
                        else:
                            pass

                        if lib_boot_to_environment.simics_sendkeys(tool, cmd3):
                            if "pendrive3.0" == comp or "pendrive2.0" == comp:  # If device is usb 2.0 or 3.0 pendrive get the port number
                                port_no = check_simicslog('port', comp,
                                                          test_case_id,
                                                          script_id,
                                                          log_level, tbd)       # Calling check_simicslog function to get the port number for usb from simics log after executing 3rd command
                            else:
                                pass

                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "hot-plug command sent "
                                              "successfully to simics console",
                                              test_case_id, script_id, "None",
                                              "None", log_level, tbd)

                            if lib_boot_to_environment.simics_sendkeys(tool, 'c'):       # Resume simics session by sending 'c'
                                if "pendrive3.0" == comp or \
                                   "pendrive2.0" == comp:
                                    fopen = open("usb_connector.log",
                                                 mode='w')                      # Create usb_connector log file
                                    fopen.write(cmp_no + ":" + port_no)         # Write connector name and port no used to hotplug usb. Required to unplug usb
                                    fopen.close()
                                else:
                                    pass

                                library.write_log(lib_constants.LOG_INFO,
                                                  "INFO: resume command sent "
                                                  "successfully to simics "
                                                  "console", test_case_id,
                                                  script_id, "None", "None",
                                                  log_level, tbd)
                                time.sleep(lib_constants.SHORT_TIME)            # Wait time given to make sure tws service is up in sut after resuming simics session
                                return True                                     # Function exits by Returning True if Send Keys are successful
                            else:
                                library.write_log(lib_constants.LOG_WARNING,
                                                  "WARNING: Failed to send "
                                                  "resume command to simics "
                                                  "console", test_case_id,
                                                  script_id, "None", "None",
                                                  log_level, tbd)
                                return False                                    # Function exits by Returning False if Send Keys are unsuccessful
                        else:                                                   # Failed to connect usb3_hs_disk_dev_%s.connector_usb
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to send %s "
                                              "hot-plug command to simics "
                                              "console" % cmd3, test_case_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return False                                        # Function exits by Returning False if Send Keys are unsuccessful
                    else:
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: Failed to send %s command "
                                          "to simics console" % cmd2,
                                          test_case_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False                                            # Function exits by Returning False if Send Keys are unsuccessful
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Failed to send %s hot-plug command to "
                                      "Simics console" % cmd1, test_case_id,
                                      script_id, "None", "None", log_level,
                                      tbd)
                    return False                                                # Function exits by Returning False if Send Keys are unsuccessful
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to send stop command to simics console",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False                                                    # Function exits by Returning False if Send Keys are unsuccess
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Action is "
                              "not defined - %s" % action, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : check_device_presi
# Parameters    : test_case_id, script_id, device_name, log_level, tbd
# Return Value  : Returns True / False w.r.t device action and device status
# Purpose       : to check if a device is present in sut (device manager) or not
################################################################################


def check_device_presi(config, action, test_case_id, script_id,
                       log_level="ALL", tbd=None):

    try:
        config_entry = config + "_DEVICE-NAME"
        device_name = utils.ReadConfig("PLUG_UNPLUG", config_entry)             # Getting device name from config file

        if "FAIL" in device_name:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for device_name is not proper",
                              test_case_id, script_id, "None", "None",
                              log_level, device_name)                           # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for "
                              "device_name is %s in config.ini" % tbd,
                              test_case_id, script_id, "None", "None",
                              log_level, device_name)                           # Continie to remaining steps as config entry is fetched

        if "incorrect or Config.ini does not contain" in device_name:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s name is not "
                              "found in config file" % config, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False                                                        # Function exists by Returning False if config entry is missing

        if "UNPLUG" in action:                                                  # Determining the device action
            flag = True
        elif "HOT-UNPLUG" in action:
            flag = True
        else:
            flag = False

        if ("USB3.0-PENDRIVE" or "USB2.0-PENDRIVE" in
            lib_constants.WMI_CHECK_PRESI) and flag:                            # Check for device if it is  listed as device manager enumerated
            command = lib_constants.DELETE_DISK_PRESI
            remove_disk = subprocess.Popen(command, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           stdin=subprocess.PIPE)
            c = wmi.WMI()
            found = False

            for devices in c.Win32_PnPEntity():                                 # If device found in list
                if devices.Name is not None:
                    if device_name.upper() == devices.Name.upper():
                        found = True
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                          "is found in device manager list"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        flag = False
                        return flag                                             # Function exists by Returning False when Device device is connected
                    else:
                        pass
            return flag                                                         # Function exists by Returning True when Device device is not connected

        if "USB3.0-PENDRIVE" or "USB2.0-PENDRIVE" in \
                lib_constants.WMI_CHECK_PRESI:                                  # Check for device if it is  listed as device manager enumerated
            c = wmi.WMI()
            found = False

            for devices in c.Win32_PnPEntity():                                 # If device found in list
                if devices.Name is not None:
                    if device_name.upper() == devices.Name.upper():
                        found = True
                        library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                          "is found in device manager list"
                                          % device_name, test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)
                        return True
                    else:
                        pass
            return False

        device_status = check_device(config, test_case_id, script_id,
                                     device_name, log_level, tbd)               # Calling Check_Device function to find out device status in OS

        if "Connected" == device_status and flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is %s"
                              % (config, device_status), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False                                                        # Function exists by Returning False when Device_Status = Connected but Action = Disconnect
        elif "Not Connected" == device_status and not flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is %s"
                              % (config, device_status), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False                                                        # Function exists by Returning False when Device_Status = Not Connected but Action = Connect
        elif "Not Connected" == device_status and flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is %s "
                              % (config, device_status), test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True                                                         # Function exists by Returning True when Device_Status = Not Connected and Action = Disconnect
        elif "Connected" == device_status and not flag:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s is %s" %
                              (config, device_status), test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return True                                                         # Function exists by Returning True when Device_Status = Connected and Action = Connect
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Device status is "
                              "unknown", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False                                                        # Function exists by Returning False when Device_Status is not defined
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : check_simicslog
# Parameters    : test_case_id, script_id, device_name, log_level, tbd
# Return Value  : Returns connector value, port number from the simics log
# Purpose       : To get the connector id and port id to pass it to next command
################################################################################


def check_simicslog(inf, comp, test_case_id, script_id, log_level="ALL",
                    tbd=None):

    try:
        time.sleep(lib_constants.FIVE)
        with open(lib_constants.SIMICS_LOG_PATH, 'r') as f:                     # Open simics log in host machine for reading
            f.seek(0, 2)
            fsize = f.tell()
            f.seek(max(fsize-100, 0), 0)                                        # Read last 1 kb data
            lines = f.readlines()
            f.close()

            if "cmp" == inf:
                if "pendrive2.0" == comp:
                    for i in lines:
                        if "usb3_hs_disk_dev_cmp" in i:
                            cmp_no = i.split(" ")[4].split("_")[4].\
                                replace("'\n", "")
                            return cmp_no                                       # Returns connector id from the simics log
                elif "pendrive3.0" == comp:
                    for i in lines:
                        if "usb3_disk_cmp" in i:
                            cmp_no = i.split(" ")[4].split("_")[2].\
                                replace("'\n", "")
                            return cmp_no                                       # Returns connector id from the simics log
                elif "keyboard" == comp:
                    for i in lines:
                        if "Connections: icl.usb3_keyboard.connector_keyboard" \
                                in i:
                            return "icl.usb3_keyboard"                          # Returns keyboard connection name from the simics log
                elif "mouse" == comp:
                    for i in lines:
                        if "Connections: icl.usb3_mouse.connector_mouse" in i:
                            return "icl.usb3_mouse"                             # Returns connector id from the simics log
            else:
                port_no = lines[len(lines)-1].split("=")[1].split("_")[1]
                return port_no                                                  # Returns port number from the simics log

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False                                                            # Function exists by Returning False when Exception arises

################################################################################
# Function Name : disconnect_usb
# Parameters    : test_case_id, script_id, device_name, log_level, tbd
# Return Value  : Returns connector value, port number from the simics log
# Purpose       : To get the connector id to pass it to next command
################################################################################


def disconnect_usb_presi(test_case_id, script_id, log_level="ALL", tbd=None):

    usb_count =0
    count = 0
    usb_connectors = []
    tool = lib_constants.TOOLPATH + "\\simicscmd.exe"
    components = '"list-components"'

    if lib_boot_to_environment.simics_sendkeys(tool, components):                        # Sending simics sendkeys "list-components" to fetch the list of connected deviices
        try:
            with open(lib_constants.SIMICS_LOG_PATH, 'r') as f:                 # Open simics log file
                f.seek(0, 2)
                fsize = f.tell()
                f.seek(max(fsize-1500, 0), 0)
                lines = f.readlines()
                f.close()

                for i in lines:
                    if "usb3_hs_disk_dev" in i and "top: icl" in i:
                        usb_count += 1                                          # Increase usb_count by 1
                        cmp_no = i.split(" ")[0].split("_")[4]
                        usb_connectors.append(cmp_no)
                usb_connectors.sort()
                return usb_count                                                # Function returns the port numbers connected

        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s"
                              % e, test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

################################################################################
# Function Name : sd_card_sideband_disable
# Parameters    : test_case_id, script_id, log_level, tbd
# Return Value  : Returns True for successful bios option setting, else false
# Purpose       : To disable the sd card sideband events option
################################################################################


def sd_card_sideband_disable(test_case_id, script_id, log_level, tbd):          # Disable sd card side band events for SD card 3.0

    try:
        if "KBL" == tbd.upper() or "KBLR" == tbd.upper():                       # If platform is big core
            sd_card_sideband_events = \
                lib_constants.SD_CARD_SIDEBAND_EVENTS_BIG_CORE
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Given platform "
                              "is not applicable for sd card bios setting",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True

        ret = lib_set_bios.lib_write_bios(sd_card_sideband_events,
                                          test_case_id, script_id, log_level,
                                          tbd)                                  # Set bios option for sd card sideband events to disabled

        if 3 != ret:                                                            # If successfully set the bios option
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "disable SD card sideband events in bios",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: SD card sideband "
                              "events disabled successfully in bios",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Write msg to log
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, None, None, log_level, tbd)
        return False

################################################################################
# Function Name : display_type_verify
# Parameters    : device, test_case_id, script_id, log_level="ALL", tbd=None
# Return Value  : True/False
# Purpose       : To verify enumeration of display type
################################################################################


def display_type_verify(device, test_case_id, script_id, log_level="ALL",
                        tbd=None):

    try:
        if "-DISPLAY" in device.upper():
            device = device.replace('-DISPLAY', '')

        tool_dir = utils.ReadConfig("DISPLAY", "tooldir")                       # Read the tools directory path from the config and store in tool_dir
        cmd_to_run = utils.ReadConfig("DISPLAY", "cmd")

        if "FAIL:" in [tool_dir, cmd_to_run]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "values under DISPLAY section are missing",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False, None
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config values "
                              "under DISPLAY section are found", test_case_id,
                              script_id, "None", "None",log_level, tbd)

        if '4K' in device.upper():
            token = "setup single display using hdmi-display"
            status = lib_display_configuration_in_os.\
                display_configuration_in_os(token, test_case_id, script_id,
                                            log_level, tbd)

            if status:
                token = "verify hdmi display with resolution 4096x2160"
                status = lib_verify_display_with_display_properties.\
                    verify_display_with_display_properties(token, test_case_id,
                                                           script_id,
                                                           log_level, tbd)
                if status:
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s "
                                      "Display is configured" % device,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return True, device                                         # Return "True", device name when display property is found
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                      "Display is not configured" % device,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False, None                                          # Return "True", device name when display property is found
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: %s "
                                  "Display is not configured" % device,
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return False, None                                              # Return "True", device name when display property is found
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: SD card sideband "
                              "events disabled successfully in bios",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # Write msg to log
            return True, device
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : cswitch_plug_unplug
# Parameters    : action, cswitch_port, device, script_id, tc_id,
#                 log_level="ALL", tbd=None
# Return Value  : True/False
# Purpose       : To plug and unplug the Type C devices
################################################################################


def cswitch_plug_unplug(action, cswitch_port, config, script_id, test_case_id,
                        log_level="ALL", tbd=None):
    try:
        cswitch_device_id = "CSWITCH_ID_" + config
        cswitch_id = utils.ReadConfig("CSWITCH", cswitch_device_id)
        if "FAIL" in cswitch_id.upper() or 'NC' in cswitch_id.upper() or \
                        'NA' in cswitch_id.upper():
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: config entry for "
                              "%s is not proper under CSWITCH in "
                              "config.ini" % cswitch_device_id,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   # If failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: config entry for %s is %s "
                              "found under CSWICH in config.ini"
                              % (cswitch_device_id, cswitch_id), test_case_id,
                              script_id, "None", "None", log_level,
                              tbd)                                              # Continie to remaining steps as config entry is fetched
        if "HOT-UNPLUG" == action or "COLD-UNPLUG" == action:
            if lib_cswitch.cswitch_unplug(cswitch_id,test_case_id, script_id,
                                          log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: CSwitch action performed successfully",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to perform CSwitch action",
                                  test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "HOT-PLUG" == action or "COLD-PLUG" == action:
            if lib_cswitch.cswitch_plug(cswitch_id, cswitch_port, test_case_id,
                                        script_id, log_level, tbd):
                library.write_log(lib_constants.LOG_INFO,
                                  "INFO: CSwitch action performed successfully",
                                  test_case_id, script_id, "None", "None",
                                  log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING,
                                  "WARNING: Failed to perform CSwitch action",
                                  test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: CSwitch Action is not defined - %s"
                              % action,
                              test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def display_log(tc_id, script_id, log_level, tbd):
    try:
        display_log_path = "Z:\GenericFramework\dxdiag.txt"
        if os.path.exists(display_log_path):
            os.remove(display_log_path)
        input_device_name = utils.ReadConfig("KBD_MOUSE",
                                             "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE",
                                "PORT")                                         # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:                     # "FAIL:" in config details
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: Failed to get com port details and"
                              " input device name under KBD_MOUSE from "
                              "Config.ini", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("KEY_GUI")                                             # Press Windows button
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("cmd")                                                  # Send cmd command
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("python")                                               # Send python
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type(
            "import os, subprocess, lib_constants")                             # Send python modules
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type(
            "os.chdir(r'C:\\Testing\\GenericFramework')")                       # Send cmd for to change directory
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("subprocess.Popen('start cmd', shell=True, "
                        "stdout=subprocess.PIPE, stdin=subprocess.PIPE, "
                        "stderr=subprocess.PIPE)")                              # Send cmd for to open command prompt
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("python")                                               # Send python
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("import os")                                            # Send os module
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type(
            "os.system('dxdiag /t /whql:off')")                                 # Send cmd for to create keyboard_functionality text file
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.TWO)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.TWO)
        kb_obj.key_press("KEY_ENTER")
        time.sleep(lib_constants.TWO)

        if os.path.exists(r"Z:\GenericFramework\dxdiag.txt"):
            library.write_log(lib_constants.LOG_INFO,
                              "INFO: Log for verifying displays generated"
                              " scuccessfully", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return True, display_log_path
        else:
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: Failed to generated log for verifying"
                              " displays", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:                                                      # Exception handling for KBD operation
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False


def shutdown_using_kbd(tc_id, script_id, log_level, tbd):
    try:
        input_device_name = utils.ReadConfig("KBD_MOUSE",
                                             "KEYBOARD_MOUSE_DEVICE_NAME")      # Extract input device name from config.ini
        port = utils.ReadConfig("KBD_MOUSE",
                                "PORT")                                         # Extract com port details from config.ini

        if "FAIL:" in port or "FAIL:" in input_device_name:                     # "FAIL:" in config details
            library.write_log(lib_constants.LOG_WARNING,
                              "WARNING: Failed to get com port details and"
                              " input device name under KBD_MOUSE from "
                              "Config.ini", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        kb_obj = kbm.USBKbMouseEmulation(input_device_name, port)               # kb_obj object of USBKbMouseEmulation class
        kb_obj.key_press("KEY_GUI")                                             # Press Windows button
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("cmd")                                                  # Send cmd command
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        kb_obj.key_type("python")                                               # Send python
        time.sleep(lib_constants.ONE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.ONE)
        kb_obj.key_type("import os")                                            # Send python modules
        time.sleep(lib_constants.ONE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.ONE)
        kb_obj.key_type(
            "os.system('start shutdown /s /f /t 10')")                          # Send cmd to shutdown the system
        time.sleep(lib_constants.THREE)
        kb_obj.key_press("KEY_ENTER")                                           # Press Enter key
        time.sleep(lib_constants.ONE)
        kb_obj.key_type("exit()")                                               # Send exit
        time.sleep(lib_constants.ONE)

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: Shutting down the system", tc_id, script_id,
                          "None", "None", log_level, tbd)
        return True

    except Exception as e:                                                      # Exception handling for KBD operation
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False
