__author__ = 'dparthix/tnaidux'

# General Python Imports
import csv
import getopt
import os
import re
import subprocess
import sys
import time

# Local Python Imports
import library
import lib_constants
import lib_connect_disconnect_power_source
import lib_perform_g3
import lib_plug_unplug
import lib_ttk2_operations
import utils
sys.path.append(r"C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli")
import pysvtools.xmlcli.XmlCli as cli

# Global Variables
image_type_path = None
mac_id = None

################################################################################
# Function Name   : updatemacaddress
# Parameter       : tc_id, script_id, log_level, tbd
# Functionality   : updating mac address on SUT
# Return Value    : 'True' on successful action and 'False' on failure
################################################################################


def updatemacaddress(tc_id, script_id, log_level="ALL",tbd=None):
    try:
        macaddress  =  utils.ReadConfig("IFWI_IMAGES","macaddress")             #Reading macaddress of SUT from config file
        macaddress  = str.replace(macaddress,":"," ")                           #Converting MAC Address to TTK format
        macaddunicode = unicode(macaddress,"utf-8")                             #Converting to UTF-8 encoding
        try:
            thumbking = library.initialize_ttk(log_level, tbd)                  #Initializing TTK
        except IndexError:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: No TTK device is"
                " detected ", tc_id, script_id, "None", "None",
                    log_level, tbd)                                             #If TTK device not detected or initialized exception will be handled
            return False
        thumbking.spiInitChips()                                                #Detect Chip - Initialize the SPI bus
        topology = thumbking.spiGetTopology()                                   #Read the SPI device topology previously detected by InitChips
        strings = thumbking.spiGetStrings()
        macaddresstowrite = bytearray.fromhex(macaddunicode)
        library.write_log(lib_constants.LOG_INFO, "INFO: Reading SPI Chip[s] "
        "for getting mac address", tc_id, script_id, "None", "None",
                          log_level, tbd)
        thumbking.spiBeginRead(lib_constants.FOUR_KB,
                               lib_constants.FOUR*lib_constants.ONE_KB)         #to get current macaddress data block
        while True:
            status = thumbking.spiStatus()                                      #Getting the status of SPI read
            if 0 == status[1]['status']  :
                library.write_log(lib_constants.LOG_INFO, "INFO: SPI Read"
                     "Successfully ", tc_id, script_id, "None", "None",
                    log_level, tbd)
                break
            time.sleep(lib_constants.FIVE_SECONDS)
        readdata = thumbking.spiReadData(lib_constants.FOUR*lib_constants.ONE_KB)
        current_macaddress = hex(readdata[1][0])[2:]+":"+ hex(readdata[1][1])[2:]\
                + ":"+ hex(readdata[1][2])[2:] + ":"+ hex(readdata[1][3])[2:] +\
                ":"+ hex(readdata[1][4])[2:] + ":"+ hex(readdata[1][5])[2:]
        library.write_log(lib_constants.LOG_INFO, "INFO: Current macaddress %s"
                  " erased Successfully"%current_macaddress, tc_id, script_id,
                          "None", "None",log_level, tbd)
        thumbking.spiErase(lib_constants.FOUR_KB,
                           lib_constants.FOUR*lib_constants.ONE_KB)             #print "Erasing a portion of SPI Chip[s]......"
        while True:
            status = thumbking.spiStatus()
            if 0 == status[1]['status'] :
                library.write_log(lib_constants.LOG_INFO, "INFO: Current Mac "
                    "Address erased Successfully", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                break
            time.sleep(lib_constants.FIVE_SECONDS)
        for i in range (0,6):                                                   #to write the data block back to the Chip
            readdata[1][i] = macaddresstowrite[i]
        thumbking.spiWrite(lib_constants.FOUR_KB,
                           lib_constants.FOUR*lib_constants.ONE_KB,readdata[1])
        time.sleep(lib_constants.FIVE_SECONDS)
        while True:                                                             #wait for SPI update to complete
            status = thumbking.spiStatus()
            if 0 == status[1]['status']:
                break
            time.sleep(lib_constants.FIVE_SECONDS)
        library.write_log(lib_constants.LOG_INFO, "INFO: macaddress %s updated "
             "Successfully "%macaddress, tc_id, script_id, "None", "None",
                    log_level, tbd)
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception occured "
                "due to %s"%e, tc_id, script_id, "None", "None",log_level, tbd)
        return False

################################################################################
# Function Name   : flashing_ifwi_ttk
# Parameters      : original_string, image_type, tc_id, script_id, log_level,
#                   tbd
# Functionality   : Flashing IFWI on SUT
# Return Value    : True on successful action, False otherwise
################################################################################


def flashing_ifwi_ttk(original_string, image_type, tc_id, script_id,
                      log_level="ALL", tbd=None):

    try:
        if "dnx" in original_string.lower():
            if "CONFIG-" in image_type:                                         # Checks Config- is present in imagetype
                dnx_image_file = utils.parse_variable(image_type, tc_id,
                                                      script_id)
                if not dnx_image_file:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "config entry missing for tag variable "
                                      "%s" % dnx_image_file, tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False
            else:
                dnx_image_file = utils.ReadConfig("IFWI_IMAGES", image_type)    # Reads bin file dnx_image_file based on image type
                if "FAIL:" in dnx_image_file:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "config entry missing for tag variable "
                                      "%s" % dnx_image_file, tc_id, script_id,
                                      "None", "None", log_level, tbd)
                    return False

            time.sleep(lib_constants.TEN_SECONDS)
            dnx_rework_1 = utils.ReadConfig("TTK", "DNX_REWORK_SW1_4")          # Config entry for the dnx switch
            dnx_rework_4 = utils.ReadConfig("TTK", "DNX_REWORK_TYPEC")          # Config entry for the typeC reworl

            if "NC" in dnx_rework_1 or "NC" in dnx_rework_4:                    # If DNX switch or typeC rework not connected to TTK relay
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DNX "
                                  "switch or TypeC rework not connected to "
                                  "TTK relay", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            elif "NA" in dnx_rework_1 or "NA" in dnx_rework_4:                  # If DNX switch or typeC rework not applicable for target system
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DNX "
                                  "switch or TypeC rework not applicable for "
                                  "the target system", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False
            elif "fail:" in dnx_rework_1.lower() or \
                    "fail:" in dnx_rework_4.lower():                            # If DNX switch or typeC rework details not updated in Config.ini
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DNX "
                                  "switch or TypeC rework details not updated "
                                  "in Config.ini", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
            else:                                                               # If DNX switch and typeC rework is connected to Relay number which is given in config
                library.write_log(lib_constants.LOG_INFO, "INFO: DNX switch "
                                  "and TypeC rework is connected to relay "
                                  "number %s, %s in TTK respectively"
                                  % (dnx_rework_1, dnx_rework_4), tc_id,
                                  script_id, "None", "None", log_level, tbd)
                pass

            relay_action_dnx_rework_1 = \
                library.ttk_set_relay('ON', [int(dnx_rework_1)])                # To make relay connection COM NC  -- it will make connection open, to make board in DNX mode
            time.sleep(lib_constants.FIVE_SECONDS)
            relay_action_dnx_rework_4 = \
                library.ttk_set_relay('ON', [int(dnx_rework_4)])                # To make relay connection COM NO  -- it will make connection open , to connect typeC cable from HOST to SUT

            if 0 == relay_action_dnx_rework_1 or 0 == relay_action_dnx_rework_4:
                library.write_log(lib_constants.LOG_INFO, "INFO: DNX switch "
                                  "has been set to DNX mode and TypeC cable "
                                  "is connected to system using TTK tool",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to set the DNX switch to DNX mode or failed "
                                  "to connect the TypeC cale to system using "
                                  "TTK tool", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            if lib_connect_disconnect_power_source.\
               connect_disconnect_power("CONNECT", "AC", tc_id, script_id,
                                        log_level, tbd):                        # Library calls to disconnect the DC power supply & DC signal
                time.sleep(lib_constants.SHORT_TIME)
                library.write_log(lib_constants.LOG_INFO, "INFO: Real battery "
                                  "disconnected successfully from SUT", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to disconnect real battery from SUT", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            device_name = utils.ReadConfig("IFWI_IMAGES", "DNX_DEVICE_NAME")    # config entry for typeC detection in device manager
            if "FAIL:" in device_name:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: config "
                                  "entry missing for tag variable %s"
                                  % device_name, tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            result = lib_plug_unplug.check_device("DNX", tc_id, script_id,
                                                  device_name, log_level, tbd)  # To check the device manager detection of TypeC in device manager
            if "Connected" == result:                                           # If TypeC detection is found in device manager
                library.write_log(lib_constants.LOG_INFO, "INFO: TypeC cable "
                                  "is detected in the Device manager", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                pass
            else:                                                               # If failed to detect the typeC cable in device manager
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to detect the TypeC cable in device "
                                  "manager", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            dnx_post_code = library.read_post_code()                            # Calls the function to read the post code from he library

            if "0000" == dnx_post_code:                                         # If system is in DNX mode then postcode will be "0000"
                library.write_log(lib_constants.LOG_INFO, "INFO: Post read "
                                  "value %s is matching precondition"
                                  % dnx_post_code, tc_id, script_id, "None",
                                  "None", log_level, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Post "
                                  "read value %s is not matching precondition"
                                  % dnx_post_code, tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            dnx_dir = utils.ReadConfig("IFWI_IMAGES", "dnx_dir")                # Reads bin file dnx_image_file based on image type
            if "FAIL:" in dnx_dir:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                                  "entry is missing for tag variable %s under "
                                  "section IFWI_IMAGES" % dnx_dir, tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            if not os.path.exists(dnx_dir):                                     # If path does not exists for DNX folder location
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DNX "
                                  "folder is not placed in c-automation-tools "
                                  "location", tc_id, script_id, "None", "None",
                                  log_level, tbd)
                return False

            os.chdir(dnx_dir)
            if not os.path.exists(dnx_image_file):                              # If path does not exists for dnx file image
                library.write_log(lib_constants.LOG_WARNING, "WARNING: DNX "
                                  "image file is missing in DNX folder path",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return False

            dnx_cmd = lib_constants.DNX_FLASHING_CMD + dnx_image_file           # Dnx command for DNX flashing in the system
            time.sleep(lib_constants.SIKULI_EXECUTION_TIME)

            dnx_output = subprocess.Popen(dnx_cmd, shell=False,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE)                # Flashing the dnx command in the system using subprocess
            time.sleep(lib_constants.TWENTY)
            dnx_output_all = dnx_output.stdout.read()

            if "success" in dnx_output_all.lower():
                library.write_log(lib_constants.LOG_INFO, "INFO: DNX image is "
                                  "flashed successfully", tc_id, script_id,
                                  "None", "None", log_level, tbd)
            elif "failed" in dnx_output_all.lower():
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to flash the DNX image on emmc in the "
                                  "system using type C to type A cable",
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to flash the DNX image on emmc in the "
                                  "system using type C to type A cable", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            if lib_perform_g3.perform_g3(tc_id, script_id, log_level, tbd):     # Performing G3, on success
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                                  "performed g3 cycle", tc_id, script_id,
                                  "None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to perform g3 cycle", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            time.sleep(lib_constants.FIVE_SECONDS)
            relay_action_dnx_rework_4 = \
                library.ttk_set_relay('OFF', [int(dnx_rework_4)])               # To make relay connection COM NO  -- it will make connection open, make the board to normal mode

            time.sleep(lib_constants.FIVE_SECONDS)
            relay_action_dnx_rework_1 = \
                library.ttk_set_relay('OFF', [int(dnx_rework_1)])               # To make relay connection COM NC  -- it will make connection close, typeC cable is disconnected

            if 0 == relay_action_dnx_rework_1 or \
               0 == relay_action_dnx_rework_4:                                  # If DNX switch is set to normal mode and typeC cable is disconnected
                library.write_log(lib_constants.LOG_INFO, "INFO: DNX switch "
                                  "set to normal mode and Type C cable is "
                                  "disconnected", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to DNX switch set to normal mode and Type C "
                                  "cable is disconnected", tc_id, script_id,
                                  "None", "None", log_level, tbd)               # If return value of ttk_set_relay() is false ,then connect action is Fail
                return False
                                                                                #code to connect AC make the board up
            if lib_connect_disconnect_power_source.\
               connect_disconnect_power("CONNECT", "AC", tc_id, script_id,
                                        log_level, tbd):                        # Library calls to disconnect the DC power supply & DC signal
                time.sleep(lib_constants.SHORT_TIME)
                library.write_log(lib_constants.LOG_INFO, "INFO: Real battery "
                                  "disconnected successfully from SUT", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                pass
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to disconnect real battery from SUT", tc_id,
                                  script_id, "None", "None", log_level, tbd)
                return False

            time.sleep(4 * lib_constants.SIXTY_ONE)
            return True
        else:
            global image_type_path
            global mac_id
            flash_address = "0000"

            original_string = original_string.split(" ")
            if 3 == len(original_string):
                flash_image = str(original_string[2])
            else:
                flash_image = "IFWI"

            if "CONFIG-" in image_type:                                         # Checks Config- is present in imagetype
                image_type_path = utils.parse_variable(image_type, tc_id,
                                                       script_id)
                if image_type_path is not False:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Image file "
                                                              "path is correctly given in the config entry %s"
                                      % image_type_path, tc_id, script_id, "None", "None", log_level, tbd)

                else:
                    library.write_log(lib_constants.LOG_ERROR, "Image path in the config entry"
                                                               "is not proper %s" % image_type_path, tc_id,
                                      script_id, "None", "None", log_level, tbd)
            elif image_type_path is None:
                image_type_path = utils.ReadConfig("IFWI_IMAGES", image_type)   # Reads bin file path based on image type

            if mac_id is None:
                mac_id = utils.ReadConfig("TTK", "mac_id")

            if "FAIL:" in [mac_id, image_type_path]:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to get the config entries for mac_id and "
                                  "image_type_path", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            log_file_size = os.path.getsize(image_type_path)                    # Checks for bin file size
            if not "" == log_file_size:
                library.write_log(lib_constants.LOG_INFO, "INFO: Image file "
                                  "size is %s" % log_file_size, tc_id,
                                  script_id, "None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Image "
                                  "file is not proper", tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

            result = lib_ttk2_operations.\
                flash_ifwi(flash_image, flash_address, image_type_path,
                           mac_id, tc_id, script_id, log_level, tbd)

            time.sleep(lib_constants.TWO_MIN)

            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                                  "flashed %s %s" % (image_type, flash_image),
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to flash %s %s" % (image_type, flash_image),
                                  tc_id, script_id, "None", "None", log_level,
                                  tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : verify_ifwi
# Parameters      : tc_id, script_id
# Functionality   : Verifying IFWI flashed successfully on SUT
# Return Value    : 'True'on successful action and 'False' on failure
################################################################################


def verify_ifwi(tc_id, script_id, log_level="ALL",tbd=None):                    #Verifying bios version after successful IFWI flashing
    try :
        bios_version_config = utils.ReadConfig("IFWI_IMAGES", "bios_version")
        cmd = "wmic bios get smbiosbiosversion"
        version = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()[0]
        sut_bios_version = version.split()[1].split(".")[2]
        if bios_version_config == sut_bios_version:                             #Verifying the bios version specified in Config file matches with value from OS
            library.write_log(lib_constants.LOG_INFO, "INFO: Bios Version matches"
                " between config file and SUT", tc_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Bios Version not "
                "matching between config file and SUT", tc_id, script_id, "None"
                              , "None",log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Verification of bios"
            " fails due to  %s."%e, tc_id ,script_id)
        return False
################################################################################
# Function Name   : store_proj_version
# Parameters      : tc_id, script_id
# Functionality   : Verifying IFWI flashed successfully on SUT
# Return Value    : 'True'on successful action and 'False' on failure
################################################################################
def store_proj_version(ostr, image_type, test_case_id,script_id, log_level="ALL",tbd=None):
    try:

        online_log_path = lib_constants.XML_CLI_ONLINE_LOGPATH

        if os.path.exists(online_log_path):
            os.remove(online_log_path)

        cli.clb._setCliAccess("winhwapi")

        result_save_xml = cli.savexml(online_log_path)
        time.sleep(5)
        if 0 == result_save_xml and os.path.exists(online_log_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully run "
                                                      "command to generate log and log exist in path",
                              test_case_id, script_id, "None", "None", log_level, tbd)
        elif 0 == result_save_xml and not os.path.exists(online_log_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully run "
                                                      "command to generate log and log doesn't exist in path",
                              test_case_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Unable to run "
                                                      "command to save log",
                              test_case_id, script_id, "None", "None", log_level, tbd)

        if os.path.exists(online_log_path):
            with open(online_log_path, 'rt') as f:
                content = f.read()
            child_bios_string = "Project Version"
            a = re.finditer(r'<!--(.*?)-->', content)
            log = lib_constants.SCRIPTDIR + "\\comments.txt"
            if os.path.exists(log):
                os.remove(log)

            for i in a:
                with open("comments.txt", "a") as fw:
                    fw.writelines(i.groups(1)[0].strip() + "\n")

            with open("comments.txt", "r") as fr:
                for line in fr:
                    if None != line:
                        if child_bios_string.lower() in line.strip().lower():
                            cur_proj_ver = line.split(':')[-1]

            cur_proj_ver = cur_proj_ver.strip()
            if "CONFIG-" in image_type.upper():
                image = image_type.split("-")
                ifwi_path = utils.ReadConfig(image[1], image[2])
                if "FAIL" in ifwi_path:
                    library.write_log(lib_constants.LOG_INFO, "INFO: failed entry not found under [%s]" % image[1],
                                      test_case_id, script_id, "None", "None", log_level, tbd)
                    return False

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: config entry found under [%s]" % image[1],
                                      test_case_id, script_id, "None", "None", log_level, tbd)
                    tool_path = utils.ReadConfig("xml_cli", "tool_path")
                    if "FAIL:" in tool_path:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for [xml_cli] tag is missing",
                                          test_case_id, script_id, "None", "None",
                                          log_level, tbd)
                        return False

                    xml_tool_path = tool_path + "\\out\\"
                    command = "xcopy /I /S /E /Y " + ifwi_path + " " + xml_tool_path
                    try:
                        os.system(command)
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR: failed to copy \
                                    IFWI due to %s" % e, test_case_id, script_id)
                        return False
                    library.write_log(lib_constants.LOG_INFO, "INFO: succefully copied IFWI ", test_case_id, script_id)
            else :
                ifwi_path = utils.ReadConfig("IFWI_IMAGES", image_type.lower())
                if "FAIL" in ifwi_path:
                    library.write_log(lib_constants.LOG_INFO, "INFO: failed entry not found under [IFWI_IMAGES]",
                                      test_case_id, script_id, "None", "None", log_level, tbd)
                    return False

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: config entry found under [IFWI_IMAGES]",
                                      test_case_id, script_id, "None", "None", log_level, tbd)
                    tool_path = utils.ReadConfig("xml_cli", "tool_path")
                    if "FAIL:" in tool_path:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Config entry for [xml_cli] tag is missing",
                                          test_case_id, script_id, "None",
                                          "None",
                                          log_level, tbd)
                        return False

                    xml_tool_path = tool_path + "\\out\\"
                    command = "xcopy /I /S /E /Y " + ifwi_path + " " + xml_tool_path
                    try:
                        os.system(command)
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR: failed to copy \
                                                    IFWI due to %s" % e, test_case_id, script_id)
                        return False
                    library.write_log(lib_constants.LOG_INFO, "INFO: succefully copied IFWI ", test_case_id, script_id)

            ifwi_name = ifwi_path.split("\\")[-1]

            csv_log_file = lib_constants.SCRIPTDIR + "\\" + test_case_id + ".csv"
            if os.path.exists(csv_log_file):
                with open(csv_log_file, "r") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        proj_ver = row['proj_version']
                        status = row['status']
                    csvfile.close()

                if cur_proj_ver.upper().strip() == proj_ver.upper().strip():
                    library.write_log(lib_constants.LOG_INFO, "INFO: Current flashed IFWI is same as previously  falshed IFWI ",
                                      test_case_id, script_id, "None", "None", log_level, tbd)
            else :
                csv_file = open(csv_log_file, "wb")
                row = "ifwi_name," + "proj_version," + "status\n"
                csv_file.write(row)
                csv_file.close()

            csv_file1 = open(csv_log_file, "ab")
            status = "success"
            row = ifwi_name + "," + cur_proj_ver + "," + status + "\n"
            csv_file1.write(row)
            csv_file1.close()
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: renaming of IFWI"
            " fails due to  %s."%e, test_case_id ,script_id)
        return False

################################################################################
# Function Name : flashing_ifwi_dediprog
# Parameters    : ostr, image_type, tool_name, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To flash the required BIOS image
################################################################################


def flashing_ifwi_dediprog(image_type, tc_id="Flash_IFWI",
                           script_id="Flash_IFWI", log_level="ALL", tbd=None):  # Abstract method for Flashing IFWI using Dediprog

    try:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: IFWI flashing "
                          "using Dediprog is not Implemented", tc_id,
                          script_id, "None", "None", log_level, tbd)
        return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : flashing_ifwi
# Parameters    : ostr, image_type, tool_name, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To flash the required BIOS image
################################################################################


def flashing_ifwi(ostr, image_type, tool_name, tc_id, script_id, log_level,
                  tbd):                                                         # Function calling for to flash IFWI using TTK, Dediprog

    try:
        if "TTK" == tool_name.upper():
            return flashing_ifwi_ttk(ostr, image_type, tc_id, script_id,
                                     log_level="ALL", tbd=None)
        elif "DEDIPROG" == tool_name.upper():
            return flashing_ifwi_dediprog(image_type, tc_id, script_id,
                                          log_level="ALL", tbd=None)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Flashing "
                              "using tool is not implemented", tc_id,
                              script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def main(argv):

    try:
        opts, args = getopt.getopt(argv, "hi:t:p:m:",)
    except getopt.GetoptError:
        print("Please use -h command for Help Message")
        print("Usage: lib_flash_ifwi.py -h")
        return False

    try:
        if 0 == len(opts):
            print("Please use -h command for Help Message")
            print("Usage: lib_flash_ifwi.py -h")
            return False
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print("##################################################\n")
                    print("Description:\n\tThis API aims at flashing the FW " \
                          "image on the platform using Tools like TTK, Dedi" \
                          "prog etc. This API internally performs booting " \
                          "till OS after flashing operation is completed " \
                          "successfully.\n")

                    print("Arguments:\n-h\n\t For printing the help message")

                    print("-i\n\t image type e.g Release IFWI, Debug IFWI")

                    print("-t\n\t Tool name using which needs to Flash IFWI " \
                          "e.g TTK,Dediprog")

                    print("-p\n\t Image path from where needs to pick the " \
                          "FW image\n")

                    print("Usage:\n\tlib_flash_ifwi.py -i <image_type> " \
                          "-t <Tool Name> -p <IFWI/BIOS file Path> " \
                          "-m <Mac_id>\n")
                    print("####################################################")
                    return True
                elif opt in "-i":
                    image_type = arg
                elif opt in "-t":
                    tool_name = arg
                elif opt in "-p":
                    global image_type_path
                    image_type_path = arg
                elif opt in "-m":
                    global mac_id
                    mac_id = arg
                else:
                    return False
            flashing_ifwi("N/A", image_type, tool_name, "Flash_IFWI",
                          "Flash_IFWI", log_level="ALL", tbd=None)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
