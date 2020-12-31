__author__ = "kashokax"

############################General Python Imports##############################
import subprocess
import os
import io
import shutil
############################Local Python Imports################################
import library
import lib_constants
import utils
################################################################################
# Function Name : file_transfer
# Parameters    : devicea ,deviceb, test_case_id, script_id, log_level, tbd
# Functionality : transfers file between connected devices
# Return Value  : returns True on success and False otherwise
################################################################################

global file_to_transfer

def file_transfer(devicea, deviceb, test_case_id, script_id, log_level="ALL",
                  tbd=None):                                                    #function to perform file transfer

    try:
        file_to_transfer = utils.ReadConfig("FILE_TRANSFER","FILE")             #read file to be transferred from config file
        devicea_name = utils.ReadConfig("FILE_TRANSFER",devicea)                #read source device from config file
        deviceb_name = utils.ReadConfig("FILE_TRANSFER",deviceb)                #read destination device from config file

        if "FAIL:" in [file_to_transfer,devicea_name ,deviceb_name]:
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "read the config entry from config file ", test_case_id,
                              script_id, "None", "None", log_level, tbd)        #write fail message to log file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry read "
            "successfully from config file ", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #write pass message to log file


        cmd = lib_constants.GET_INFO + script_id.split(".")[0] + ".txt"         #cmd to get drive letter of connected device in sut
        cmd_to_run = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, shell=True,
                                      stdin=subprocess.PIPE)
        if cmd_to_run.communicate()[0]!= "":                                    #check the command  to get drive letter of connected device ,is successfully executed
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to execute "
            "command", test_case_id, script_id, "None", "None", log_level, tbd) #write fail message to log file
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Command executed "
            "successfully ", test_case_id, script_id, "None", "None", log_level,
                              tbd)                                              #write pass message to log file

        if ("HOST" in devicea.upper() or "HOST" in deviceb.upper()) and\
            ("SUT" in devicea.upper() or "SUT" in deviceb.upper()):             #if source and dest is SUT/HOST or HOST/SUT
            if "HOST" in devicea.upper():                                       #if host is the source
                devicea_drivename = devicea_name                                #location of file to be transferred in the host
                deviceb_drivename = get_drive_letter(deviceb_name, test_case_id,
                                                     script_id, log_level, tbd) #get the drive letter of sut
                if not deviceb_drivename:                                       #if destination  device is not present
                    library.write_log(lib_constants.LOG_INFO, "INFO: %s does "
                    "not exist or config entry is incorrect"%deviceb,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)                           #write fail message to log file
                    return False
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Drive "
                    "letter of %s is read from the log file"%deviceb,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd )                          #write pass message to log file

                result = verify_file_transfer(devicea_drivename,
                                              deviceb_drivename, test_case_id,
                                              script_id, log_level, tbd)        #function call to verify file transfer

                if result:
                    library.write_log(lib_constants.LOG_INFO, "INFO: File "
                "transferred successfully", test_case_id, script_id, "None",
                                  "None", log_level, tbd)                       #write pass message to log file
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                    "Transferred file is corrupted ", test_case_id, script_id,
                                      "None", "None", log_level, tbd)           #write fail message  to log file

                    return False

            elif "SUT" in devicea.upper():                                      #if source is sut
                deviceb_drivename = deviceb_name                                #location of the file to be transferred in the host
                devicea_drivename = get_drive_letter(devicea_name, test_case_id,
                                                     script_id, log_level, tbd )#get the drive letter of sut
                if not devicea_drivename:                                       #verify whether sut driver letter is obtained or not
                    library.write_log(lib_constants.LOG_INFO, "INFO: Sut is not"
                    " mapped to host or config entry is incorrect",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)                           #write fail message to log file
                    return False
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Drive "
                    "letter of %s is read from the log file"%devicea,
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd )                          #write pass message to log file

                result = verify_file_transfer(devicea_drivename,
                                              deviceb_drivename, test_case_id,
                                              script_id, log_level, tbd)        #function call to verify file transfer

                if result:
                    library.write_log(lib_constants.LOG_INFO, "INFO: File "
                "transferred successfully", test_case_id, script_id, "None",
                                  "None", log_level, tbd)                       #write pass message to log file
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                    "Transferred file is corrupted ", test_case_id, script_id,
                                      "None", "None", log_level, tbd)           #write fail message  to log file

                    return False

        elif "SUT" in devicea.upper():                                          #if sut is the source
            file_in_sut = utils.ReadConfig("FILE_TRANSFER","FILE_IN_SUT")       #read the location of the file to be transferred in sut from config file
            if "FAIL:" in file_in_sut :                                         #if config entry does not exist
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "read the config entry from config file ", test_case_id,
                                  script_id, "None", "None", log_level, tbd)    #write fail message to log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Config entry"
                " read successfully from config file", test_case_id, script_id,
                                  "None", "None", log_level, tbd)               #write pass message to log file

            deviceb_drivename = get_drive_letter(deviceb_name, test_case_id,
                                                 script_id, log_level, tbd)     #get the drive letter of destination device

            if not deviceb_drivename:                                           #if destination device is not present
                library.write_log(lib_constants.LOG_INFO, "INFO: %s does not "
                "exist or config entry is incorrect"%deviceb, test_case_id,
                                  script_id, "None","None", log_level, tbd)     #write fail message to log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Drive letter "
                "of %s is read from the log file"%deviceb, test_case_id,
                                  script_id, "None", "None", log_level, tbd )   #write fail message to log file

            result = verify_file_transfer(file_in_sut, deviceb_drivename,
                                          test_case_id, script_id, log_level,
                                          tbd)                                  #function call to verify file transfer

            if result:
                library.write_log(lib_constants.LOG_INFO, "INFO: File "
                "transferred successfully", test_case_id, script_id, "None",
                                  "None", log_level, tbd)                       #write pass message to log file
                return True

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Transferred "
                "file is corrupted ", test_case_id, script_id, "None", "None",
                                  log_level, tbd)                               #write fail message  to log file

                return False

        else:
            devicea_drivename = get_drive_letter(devicea_name, test_case_id,
                                                 script_id, log_level ,tbd )    #function call to get the drive letter of source device
            deviceb_drivename = get_drive_letter(deviceb_name, test_case_id,
                                                 script_id, log_level ,tbd )    #function call to get the drive letter of destination device

            if not devicea_drivename or not deviceb_drivename:                  #verify the drive letter of both source and destination is obtained
                library.write_log(lib_constants.LOG_INFO, "INFO: Device "
                "does not exist or config entry is incorrect", test_case_id,
                                  script_id, "None","None", log_level, tbd)     #write fail message to log file
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Drive "
                "letter of devices is read from the log file", test_case_id,
                                  script_id, "None", "None", log_level, tbd)    #write pass message to log file if the drive letter is obtained
                result = verify_file_transfer(devicea_drivename,
                                              deviceb_drivename , test_case_id,
                                              script_id, log_level ,tbd )       #function call to verify file transfer
                if result:                                                      #if file transfer is successfull
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                    "File transferred successfully", test_case_id, script_id,
                                      "None", "None", log_level, tbd)           #write pass message to log file
                    return True

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                        "Transferred file is corrupted ", test_case_id,
                                          script_id, "None", "None", log_level,
                                          tbd)                                  #write fail message  to log file

                    return False

    except Exception as e:                                                      #exception
            library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

################################################################################
# Function Name : get_drive_letter
# Parameters    : device ,test_case_id, script_id, log_level, tbd
# Functionality : get the drive letter of the device
# Return Value  : returns drive letter on success and False otherwise
################################################################################
def get_drive_letter(device, test_case_id, script_id, log_level = "ALL",
                     tbd = "None"):

    try:
        flag = False
        with io.open(script_id.split(".")[0] + ".txt", "r",
                     encoding='utf-16-le') as file:                             #read the log generated after executing cmd to get drive letter
            for lines in file:
                if device in lines:                                             #check if device is present in line
                    text = lines.split(device)                                  #split the line with device
                    tval = text[0].strip()                                      #get the drive letter of device
                    device = tval[-2] + ":"                                     #get the drive letter of device
                    flag  = True
                    break

        if flag:                                                                #if drive letter is obtained
            return device
        else:
            return False                                                        #if drive letter is unavailable

    except Exception as e:                                                      #exception
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)                                       #exception message to log file
        return False

################################################################################
# Function Name : verify_file_transfer
# Parameters    : device ,test_case_id, script_id, log_level, tbd
# Functionality : transfer the file from source to destination and check if the
#                  file is transferred
# Return Value  : returns True on success and False otherwise
################################################################################


def verify_file_transfer(source, destination, test_case_id, script_id,
                         log_level="All", tbd="None"):
    try:
        if os.path.exists(source + "\\" + file_to_transfer):                    #check for the availability of file to be copied in source
            shutil.copy(source + "\\" + file_to_transfer ,destination + "\\")   #copy file from source to destination
            if os.path.exists(destination + "\\" + file_to_transfer):           #check if the transferred file exists in the destination device
                if os.path.getsize(destination + "\\" + file_to_transfer) == \
                   os.path.getsize(source +"\\" + file_to_transfer):            #verify the size of the transferred file in destination is same as source file
                    return True
                else:
                    return False                                                #return false
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Failed to "
                "transfer file ", test_case_id, script_id, "None","None",
                                  log_level, tbd)                               #write fail message to log file
                return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
            "transfered does not exist in the source", test_case_id, script_id,
                              "None", "None", log_level, tbd)                   #if file is not present in the source
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: due to %s"%e,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)                                   #write exception message to log file
        return False