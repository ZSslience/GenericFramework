############################General Python Imports##############################
import os
import csv
import subprocess
import time
import shutil
import codecs
import io
################################################################################

############################Local Python Imports################################
import utils
import library
import lib_constants
################################################################################


################################################################################
# Function Name : copy_file_host_sut
# Parameters    : drivea, driveb, test_case_id-test case ID, script_id,
#                 log_level and tbd
# Purpose       : Copy file from host to sut
# Return Value  : 'True' on successful action and 'False' on failure
# Syntax        : Copy file from <source> to <destination>
################################################################################


drivea_drivename = driveb_drivename = ""
def copy_file_host_sut(drivea, driveb, test_case_id, script_id, log_level="ALL",
                       tbd="None"):
    try:
        if ("HOST" in drivea or "HOST" in driveb) and ("SUT" in drivea or "SUT"
                                                        in driveb):

            file_name = utils.ReadConfig("File_Copy", "sut_file")               #read from config the filename to copy
            file_loc_host = utils.ReadConfig("File_Copy", "file_loc_host")      #read from config file location in host
            file_loc_sut = utils.ReadConfig("File_Copy", "file_loc_sut")        #read the file location in sut
            if "FAIL:" in [file_name, file_loc_host, file_loc_sut]:
                library.write_log(lib_constants.LOG_INFO,
                              "INFO: Config entry for file_name not proper1",
                    test_case_id, script_id, "None", "None", log_level, tbd)    #fail if config entry is missing
                return False
            else:
                pass

            if "HOST" == drivea:                                                #if drivea is Host
                if os.path.exists(file_loc_host + "\\" + file_name):            #check if os path exists to the copied files then return True
                    library.write_log(lib_constants.LOG_INFO, "INFO: File to be"
                    " copied is found", test_case_id, script_id, "None",
                                  "None", log_level, tbd)

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: File to be"#else return False
                    " copied is not found", test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                    return False

                shutil.copy(file_loc_host + "\\" + file_name, file_loc_sut)     #copy from source to destination
                if os.path.exists(file_loc_sut + "\\" + file_name):             #check if os path exists to the copied files
                    return True
                else:
                    return False

        else:
            global drivea_drivename, driveb_drivename
            cmd  = "wmic logicaldisk get deviceid, volumename, description > " \
                   "log.txt"                                                    #command to get all device letter from device manager
            if "HOST" in drivea.upper():                                        #if host is the source
                drivea_name = utils.ReadConfig("File_Copy","drive_name")
                driveb_name = utils.ReadConfig("File_Copy", driveb)
                os.chdir(lib_constants.SCRIPTDIR)
                os.system(cmd)
                drivea_drivename = drivea_name
                with io.open("log.txt", "r", encoding='utf-16-le') as file:
                    for lines in file:
                        if driveb_name in lines:
                            text = lines.split(driveb_name)
                            tval = text[0].strip()
                            driveb_drivename = tval[-2] + ":"
            elif "SUT" in drivea.upper():                                       #if SUT is the source
                drivea_name = utils.ReadConfig("File_Copy","drive_name_sut")
                driveb_name = utils.ReadConfig("File_Copy", driveb)
                drivea_drivename = drivea_name
                os.chdir(lib_constants.SCRIPTDIR)
                os.system(cmd)
                with io.open("log.txt", "r", encoding='utf-16-le') as file:
                    for lines in file:
                        if driveb_name in lines:
                            text = lines.split(driveb_name)
                            tval = text[0].strip()
                            driveb_drivename = tval[-2] + ":"
            elif "HOST" in driveb.upper():                                      #if host is the Destination
                drivea_name = utils.ReadConfig("File_Copy", drivea)
                driveb_name = utils.ReadConfig("File_Copy", "drive_name")
                driveb_drivename = driveb_name
                os.chdir(lib_constants.SCRIPTDIR)
                os.system(cmd)                                                  #run the command in subprocess
                with io.open("log.txt", "r", encoding='utf-16-le') as file:
                    for lines in file:
                        if drivea_name in lines:
                            text = lines.split(drivea_name)
                            tval = text[0].strip()
                            drivea_drivename = tval[-2] + ":"
            elif "SUT" in driveb.upper():                                       #if SUT is the destination
                drivea_name = utils.ReadConfig("File_Copy", drivea)
                driveb_name = utils.ReadConfig("File_Copy", "drive_name_sut")
                os.chdir(lib_constants.SCRIPTDIR)
                driveb_drivename = driveb_name
                os.system(cmd)
                with io.open("log.txt", "r", encoding='utf-16-le') as file:
                    for lines in file:
                        if drivea_name in lines:
                            text = lines.split(drivea_name)
                            tval = text[0].strip()
                            drivea_drivename = tval[-2] + ":"

            elif "SATA-SSD" in drivea.upper():                                  #if sata-ssd is the source
                devcon_path = utils.ReadConfig("Install_Drivers","devcon_path") #get the location of devcon tool
                if "FAIL:" in devcon_path:
                    library.write_log(lib_constants.LOG_INFO,"INFO:Config entry"#if devcon toolpath is incorrect
                     "not present under the tag [Install_Drivers]", test_case_id
                      ,script_id, "None", "None", log_level, tbd)
                    return False
                else:
                    os.chdir(devcon_path)
                    os.system(lib_constants.FIND_ALL_DEVICE_LIST_CMD)           #get the device info from device manager
                    flag_device = 0
                    if os.path.exists('devices.txt'):                           #check if .txt is present
                        with open("devices.txt","r") as file:                   #read the contents of .txt file
                            for line in file:
                                if "SSD" in line.upper():                       #check if ssd is present
                                    flag_device = 1                             #put flag to 1 and break from the loop
                                    break
                                else:
                                    flag_device = 0                             #put flag to 0
                    else:
                        library.write_log(lib_constants.LOG_INFO,"INFO:"        #if .txt file does not exist
			             "Failed to generate the device list log file ",
                          test_case_id, script_id,"None","None",log_level,tbd)
                        return False
                    if 1==flag_device:                                          #confirms ssd is the booting device
                        library.write_log(lib_constants.LOG_INFO,
                              "INFO: Verified ssd cold-plug ",
                         test_case_id, script_id, "None", "None", log_level,tbd)#if sata-ssd is present
                        drivea_name = utils.ReadConfig("File_Copy",drivea)      #read the drive name from config
                        driveb_name = utils.ReadConfig("File_Copy", driveb)     #read the drive name from config
                        if "FAIL:" in drivea_name or "FAIL:" in driveb_name:
                            library.write_log(lib_constants.LOG_INFO,"INFO:"     #if config entriy is missing
                                "Config entry not present under the tag "
                                "[File_Copy]", test_case_id,script_id,
                                                  "None", "None", log_level,tbd)
                        else:
                            library.write_log(lib_constants.LOG_INFO,"INFO:"     #if config entry is present
                                "Config entry found under the tag "
                                "[File_Copy]", test_case_id,script_id,
                                                  "None", "None", log_level,tbd)
                        os.chdir(lib_constants.SCRIPTDIR)                       #change cwd to script directory
                        os.system(cmd)                                          #cmd to get the list of drives
                        with io.open("log.txt","r",encoding='utf-16-le') as f:
                            for lines in f:
                                  if driveb_name in lines:                      #verify the drive name of deviceb
                                     text = lines.split(driveb_name)            #get the drive name of deviceb
                                     tval = text[0].strip()                     #get the drive name of deviceb
                                     driveb_drivename = tval[-2] + ":"          #get the drive letter  of deviceb
                        file_name = utils.ReadConfig("File_Copy","Copy_file")   #read the file to be copied
                        source = os.path.join(drivea_name+"\\"+file_name)       #get the source path
                        if not os.path.exists(source):
                            library.write_log(lib_constants.LOG_ERROR,"ERROR"
                            "file to copy does not exist in the source",
                             test_case_id,script_id,"None","None",log_level,tbd)#if source path not found
                            return False
                        else:
                             if driveb_drivename !="" :                         #if driveb is present
                                 shutil.copy(drivea_name + "\\" + file_name,    #copy file to destination
                                 driveb_drivename + "\\")
                                 if os.path.exists(driveb_drivename + "\\" +    #confirms file in destination
						            file_name):
                                     library.write_log(lib_constants.LOG_INFO,  #if file copied successfully
				                       "INFO:File successfully copied  ",
                                        test_case_id,script_id, "None",
                                        "None", log_level, tbd)
                                     return True                                #return true if file copied successfully
                                 else:
                                     library.write_log(lib_constants.LOG_INFO,  #fail if file is not copied
				                     "INFO: File copying failed",
				                      test_case_id, script_id,"None", "None",
                                      log_level, tbd)
                                     return False
                             else:
                                 library.write_log(lib_constants.LOG_INFO,      #if destination is unavailable
				                       "INFO:Destination device doesnot exists",
                                        test_case_id,script_id, "None",
                                        "None", log_level, tbd)
                                 return False
                    else:
                        library.write_log(lib_constants.LOG_INFO,               #if sata-ssd is not connected
				                       "INFO:Fail to verify sata-ssd cold-plug",
                                        test_case_id,script_id, "None",
                                        "None", log_level, tbd)
                        return False
            else:
                drivea_name = utils.ReadConfig("File_Copy", drivea)             #read the drive name from config
                driveb_name = utils.ReadConfig("File_Copy", driveb)

                os.chdir(lib_constants.SCRIPTDIR)
                os.system(cmd)
                with io.open("log.txt", "r", encoding='utf-16-le') as file:
                    for lines in file:
                        if drivea_name in lines:
                            text = lines.split(drivea_name)
                            tval = text[0].strip()
                            drivea_drivename = tval[-2] + ":"
                        elif driveb_name in lines:
                            text = lines.split(driveb_name)
                            tval = text[0].strip()
                            driveb_drivename = tval[-2] + ":"

            file_name = utils.ReadConfig("File_Copy", "sut_file")

            if not os.path.exists(drivea_drivename + "\\" + file_name):
                library.write_log(lib_constants.LOG_ERROR,"ERROR: File to copy "
                "doesnot exist in the source", test_case_id, script_id, "None",
                              "None", log_level, tbd)                           #if file path not found
                return False

            else:
                if os.path.exists(driveb_drivename + "\\" + file_name):
                    os.remove(driveb_drivename + "\\" + file_name)
                shutil.copy(drivea_drivename + "\\" + file_name,
                            driveb_drivename + "\\")
                if os.path.exists(driveb_drivename + "\\" + file_name):
                    library.write_log(lib_constants.LOG_INFO,"INFO:File "
                    "successfully copied to destination", test_case_id,
                            script_id, "None", "None", log_level, tbd)          #return TRUE if file copied successfully
                    return True
                else:
                    library.write_log(lib_constants.LOG_ERROR,"ERROR: Copying "
                        "file failed from source to destination",
                        test_case_id, script_id,"None", "None", log_level, tbd) #return FALSE if file does not copy
                    return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
                test_case_id, script_id, "None", "None", log_level, tbd)        #exeception error catch if failed