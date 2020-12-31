__author__ = r'kvex\hvinayx\tnaidux'

# General Python Imports
import codecs
import getopt
import os
import shutil
import subprocess
import sys
import time

# Local Python Imports
import library
import lib_constants
import lib_read_bios
import lib_run_command
import lib_set_bios
import lib_ttk2_operations
import utils
sys.path.append(r"C:\Testing\GenericFramework\tools\pysvtools.xmlcli")
import pysvtools.xmlcli.XmlCli as cli

# Global Variables
image_type_path = None
image_address = None
mac_id = None

################################################################################
# Function Name     : initiate_fft_flashing
# Parameters        : token, tc_id, script_id, log_level, tbd
# Functionality     : will do the pre requisites for fft flashing
# Return Value      : returns True on success and False otherwise
################################################################################


def initiate_fft_flashing(type_param, tc_id, script_id, log_level="ALL",
                          tbd=None):

    if "CONFIG" not in type_param:
        type_param = type_param.replace(" ", "_")
        if "TEST" == type_param:                                                # If bios to be flashed is Test bios
            original_file = utils.ReadConfig("BIOS_IMAGES", type_param)         # Fetch the rom image to be test menu enabled
            if "FAIL" in original_file:                                         # Failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " bios image from Config.ini under tag section %s"%type_param,
                tc_id, script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%original_file, tc_id, script_id,
                "None", "None", log_level, tbd)

            dir_name, file_name = os.path.split(original_file)
            tool = lib_constants.TOOLPATH+"\\TestMenuEnabler_bios.exe"          # Test menu enabler tool path
            os.chdir(dir_name)
            command = tool+" "+file_name                                        # Tool path with bios as argument which has to be test enabled

            process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if len(stderr) > 0:
                return False                                                    # If error in executing the command
            else:
                file_to_flash_path = dir_name +"\\ "+ file_name.rstrip(".rom")+\
                "new.rom"
                if os.path.exists(file_to_flash_path):
                    file_to_flash = file_to_flash_path
                else:
                    file_to_flash = dir_name +"\\"+ file_name.rstrip(".rom") +\
                    "new.rom"                                                   # Creating new test menu enabled bios renamed as new as suffix
        else:
            file_to_flash = utils.ReadConfig("BIOS_IMAGES", type_param)

        if "FAIL" in file_to_flash:                                             #failed to get file information from config
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
            " file information from Config.ini under tag BIOS_IMAGES and "
            " variable %s"%type_param, tc_id, script_id, "None", "None",
            log_level, tbd)
            return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
            "flashed is identified as %s"%file_to_flash, tc_id, script_id,
            "None", "None", log_level, tbd)

    else:
        before_key, key, after_key = type_param.partition("CONFIG-")
        tag, key, variable = after_key.partition("-")

        file_to_flash = utils.ReadConfig(tag, variable)

        if "FAIL" in file_to_flash:                                             #failed to get file information from config
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
            " file information from Config.ini under tag section %s"%tag,
            tc_id, script_id, "None", "None", log_level, tbd)
            return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
            "flashed is identified as %s"%file_to_flash, tc_id, script_id,
            "None", "None", log_level, tbd)


    logical_drive = utils.ReadConfig("BIOS_FLASHING", "DRIVE")                  #if drive letter for logical drive is metioned explicitly , take that for creating logical drive

    if "FAIL" in logical_drive:
        logical_drive = "S"
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Drive letter "
        "for temporary drive has been taken as the default value S", tc_id,
        script_id, "None", "None", log_level, tbd)

    else:

        if ":" in logical_drive:                                                #chop off : from drive letter since we need to pass only drive letter to function for mounting logical drive
            logical_drive, key, after_key = logical_drive.partition(":")
        else:
            pass

        library.write_log(lib_constants.LOG_INFO, "INFO: Drive letter for "
        "temporary logical drive is identified as %s from Config.ini"
        %logical_drive, tc_id, script_id, "None", "None", log_level, tbd)

    if lib_run_command.create_logical_drive(logical_drive, tc_id, script_id,
                                            log_level, tbd):                    #Create logical drive. fn returns True on creating
        library.write_log(lib_constants.LOG_INFO, "INFO: Logical drive has been"
        " successfully created", tc_id, script_id, "None", "None", log_level,
        tbd)

        try:

            if os.path.exists(os.path.join(logical_drive + ":", "\FFT")):       #delete existing fft folder from logical drive, if any

                shutil.rmtree(os.path.join(logical_drive + ":", "\FFT"))

                library.write_log(lib_constants.LOG_INFO, "INFO: Existing files"
                " are removed from the logical drive", tc_id, script_id, "None",
                "None", log_level, tbd)

            else:                                                               #ignore exceptions
                pass

            fft_tool = utils.ReadConfig("BIOS_FLASHING", "FFT_FOLDER")          #read fft tool path
            fpt_tool = utils.ReadConfig("BIOS_FLASHING", "FPT_FOLDER")

            if "FAIL" in fft_tool:                                              #failed to get tool path
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " path of FFT tool from Config.ini under tag BIOS_FLASHING",
                tc_id, script_id, "FFT", "None", log_level, tbd)
                return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: FFT tools path"
                " is obtained as %s from Config.ini"%fft_tool, tc_id, script_id,
                "FFT", "None", log_level, tbd)
                cmd_copy_tool_fft = 'xcopy /i /e /s /y "' + fft_tool + "\*.*"\
                '" ' + logical_drive + ':\\'

                if ".rom" in file_to_flash:                                     #image to flash is rom file
                    cmd_copy_file = 'xcopy /i /y "' + file_to_flash + '" ' + \
                    logical_drive + ':\\rom_image.rom*'
                    file_name = "rom_image.rom"
                    command = "FPT.efi -f " + file_name + \
                              " -bios  >a fs0:\log.txt"
                    cmd_copy_tool_fpt = 'xcopy /i /e /s /y "' + fpt_tool + \
                            "\*.*" '" ' + logical_drive + ':\\'                 #fpt tool must be copied for .rom flashing

                elif ".bin" in file_to_flash:                                   #image to flash is bin file, not implemented
                    cmd_copy_file = 'xcopy /i /y "' + file_to_flash + '" ' + \
                    logical_drive + ':\\bin_image.bin*'
                    file_name = "bin_image.bin"
                    command = "FFT.efi batch spibios rompath:" + file_name + \
                              " -l >a fs0:\log.txt"

                else:
                    pass

                try:
                    path, dir, files = next(os.walk("s:"))
                    for f in files:
                        if "rom_image.rom" in f:
                            os.remove("s:\\rom_image.rom")
                except:
                    pass

                os.system(cmd_copy_tool_fft)                                    #copy tool folder
                os.system(cmd_copy_tool_fpt)
                os.system(cmd_copy_file)                                        #copy image file

            if ".rom" in file_to_flash:
                if (os.path.isfile(os.path.join(str(logical_drive) + ":",       #for .rom flashing, check for fpt and fft tools and image
                "\\FPT.efi")) and
                (os.path.isfile(os.path.join(str(logical_drive)
                + ":", "\\rom_image.rom")))) and\
                (os.path.isfile(os.path.join(str(logical_drive) + ":",
                "\\FFT.efi"))):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Required "
                    "files have been moved to logical drive", tc_id, script_id,
                    "None","None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "move the required files to logical drive", tc_id,
                    script_id, "FFT","None", log_level, tbd)
                    return False
            elif ".bin" in file_to_flash:                                       #for .bin image flashing, check for fft tool and image
                if (os.path.isfile(os.path.join(str(
                logical_drive) + ":", "\\FFT.efi")) and (os.path.isfile(
                os.path.join(str(logical_drive) + ":", "\\bin_image.bin")))):
                    library.write_log(lib_constants.LOG_INFO, "INFO: Required "
                    "files have been moved to logical drive", tc_id, script_id,
                    "None","None", log_level, tbd)

                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "move the required files to logical drive", tc_id,
                    script_id, "FFT","None", log_level, tbd)
                    return False

        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "file transfer from OS to Logical drive", tc_id, script_id, "None",
            "None", log_level, tbd)
            return False

        try:
            mac_address = utils.ReadConfig("BIOS_FLASHING", "MAC_ADDRESS")      #get mac address from config file

            if "FAIL" in mac_address:                                           #Failed to get value form config, give default value
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                "to get mac address from config.ini "
                "(MAC_ADDRESS under BIOS_FLASHING)", tc_id, script_id, "None",
                "None", log_level, tbd)
                mac_address = "888888888888"
            else:
                pass                                                            #mac address as default

            startup_nsh = open(os.path.join(str(logical_drive) + ":",
            "startup.nsh"), "w")                                                #create startup.nsh file
            startup_nsh.write("fs0:" + '\n' + command + '\n' + "stall 5000000" +
            '\n' + "bcfg boot mv 01 00" + '\n' + "FFT.efi flashmac:" +
            mac_address + " -l" + '\n' + "reset")                               #commands for flashing, making windows manager as first boot device and reset
            startup_nsh.close()

        except Exception as e:                                                  #exception means failed to create and update startup.nsh, thus INFO
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to"
            " create startup.nsh file in the logical drive", tc_id,
            script_id, "FFT", "None", log_level, tbd)
            return False

        try:

            if library.set_Multiple_bootorder(tc_id, script_id, log_level,
                                              tbd):                             #Make internal edk as first boot device
                library.write_log(lib_constants.LOG_INFO, "INFO: Internal "
                "EDK Shell is updated as the first boot device", tc_id,
                script_id, "BIOSConf", "None", log_level, tbd)
                return True

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "update Internal EDK Shell as the first boot device", tc_id,
                script_id, "BIOSConf", "None", log_level, tbd)
                return False

        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception "
            "in updating Internal EDK Shell as the first boot device", tc_id,
            script_id, "BIOSConf", "None", log_level, tbd)
            return False

    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: Failed to create "
        "logical drive", tc_id, script_id, "None", "None", log_level, tbd)
        return False


################################################################################
# Function Name     : verify_fft_flashing
# Parameters        : token, tc_id, script_id, log_level, tbd
# Functionality     : will verify whether flashing is successful or not
# Return Value      : returns True on success and False otherwise
################################################################################


def verify_fft_flashing(type_param, tc_id, script_id, log_level="ALL",
                        tbd=None):

    logical_drive = utils.ReadConfig("BIOS_FLASHING", "DRIVE")                  #read drive letter for logical drive from config.ini

    if "FAIL" in logical_drive:
        logical_drive = "S"
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Drive letter for"
        " temporary logical drive has been taken as the default value S", tc_id,
        script_id, "None", "None", log_level, tbd)                              #if not available, take default drive letter s

    elif ":" in logical_drive:                                                  #if drive letter is with :, remove it as only letter is required for the fn
        logical_drive, key, after_key = logical_drive.partition(":")

    else:
        pass

    if lib_run_command.create_logical_drive(logical_drive, tc_id, script_id,
                                            log_level, tbd):
        library.write_log(lib_constants.LOG_INFO, "INFO: Logical drive has "
        "been successfully created", tc_id, script_id, "None", "None",
        log_level, tbd)

        try:

            if os.path.isfile(os.path.join(str(logical_drive) + ":",
                                           "log.txt")):
                log_file = codecs.open(os.path.join(str(logical_drive) + ":",
                                                "log.txt"), "r", "utf-8")
                flag = False

                for line in log_file:
                    if "FPT Operation Successful".lower() in line.lower() or \
                       "PFAT operation is Successful." in line or \
                       "Result : Pass" in line:                                 #String for successful flashing
                        flag = True
                        library.write_log(lib_constants.LOG_INFO, "INFO: Log "
                        "file shows flashing as successful.'%s' "%line, tc_id,
                        script_id, "None", "None", log_level, tbd)
                    else:
                        pass

                if os.path.isfile(os.path.join(str(logical_drive) + ":",        #remove the startup.nsh file as a cleanup
                                           "startup.nsh")):
                    try:
                        os.remove(os.path.join(str(logical_drive) + ":",
                                           "startup.nsh"))
                    except Exception as e:                                      #ignore exception as this is cleanup
                        pass

                else:
                    pass

                if flag:                                                        #If string is found, pass
                    if tbd.upper() in lib_constants.TBD_PLATFORM:
                        if library.\
                           intel_bios_configuration_tool(tc_id, script_id,
                                                         log_level, tbd):       #Enable bios conf tool and update mac address
                            return True
                        else:
                            return False
                    else:
                        cli.clb._setCliAccess("winhwapi")
                        cli.clb.ConfXmlCli()
                        return True
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Log file"
                    " doesn't show message for successful flashing", tc_id,
                    script_id, "None", "None", log_level, tbd)
                    return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Log file isn't"
                " available for verification", tc_id, script_id, "None", "None",
                log_level, tbd)
                return False

        except:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            " verifying log", tc_id, script_id, "None", "None", log_level, tbd)
            return False

################################################################################
# Function Name     : update_bios_fft_stage_one
# Parameters        : fw_type, test_case_id, script_id, log_level, tbd
# Functionality     : will update bios options required for fft flashing
# Return Value      : returns True on success and False otherwise
################################################################################


def update_bios_fft_stage_one(fw_type, image_type, test_case_id, script_id,
                              log_level="ALL", tbd=None):

    try:
        if "CNL" == tbd.upper():
            if "BGUP" == fw_type:
                if 3 == lib_set_bios.\
                        xml_cli_set_bios(lib_constants.ENABLE_BIOS_GUARD_CNL,
                                         test_case_id, script_id, log_level,
                                         tbd):                                  #Enable bios guard, output comes from library
                    pass
                else:
                    return False
            elif "BIOS" == fw_type or "TEST" == fw_type:
                if 3 == lib_set_bios.\
                        xml_cli_set_bios(lib_constants.BIOS_GUARD_CNL,
                                         test_case_id, script_id, log_level,
                                         tbd):                                  #Disable bios guard, output comes from library
                    pass
                else:
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
                "FW Type. BiosGuard option remains unchanged", test_case_id,
                script_id, "None", "None", log_level, tbd)
                return False

            if 3 == lib_set_bios.\
                    xml_cli_set_bios(lib_constants.ENABLE_TOOLS_INTERFACE_CNL,
                                     test_case_id, script_id,log_level, tbd):   #Enable tools ineterface ,output comes from library
                return True
            else:
                return False

        else:
            if "BGUP" == fw_type:
                if 3 == lib_set_bios.\
                        xml_cli_set_bios(lib_constants.ENABLE_BIOS_GUARD,
                                         test_case_id, script_id, log_level,
                                         tbd):                                  #Enable bios guard, output comes from library
                    pass
                else:
                    return False
            elif "BIOS" == fw_type or "TEST" == fw_type:
                if 3 == lib_set_bios.xml_cli_set_bios(lib_constants.BIOS_GUARD,
                                                      test_case_id, script_id,
                                                      log_level, tbd):          #Disable bios guard, output comes from library
                    pass
                else:
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid"
                " FW Type. BiosGuard option remains unchanged", test_case_id,
                script_id, "None", "None", log_level, tbd)
                return False

        if 3 == lib_set_bios.\
                xml_cli_set_bios(lib_constants.FLASH_WEAR_OUT_PROTECTION,
                                 test_case_id, script_id, log_level, tbd):      #Disable flash wear out protection, output comes from library
            pass
        else:
            return False

        if 3 == lib_set_bios.xml_cli_set_bios(lib_constants.RTC_LOCK,
                                              test_case_id, script_id,
                                              log_level, tbd):                  #Diable rtc lock, output comes from library
            return True
        else:
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        " updating bios", test_case_id, script_id, "BiosConf", "None",
        log_level, tbd)
        return False


################################################################################
# Function Name     : update_bios_fft_stage_two
# Parameters        : fw_type, test_case_id, script_id, log_level, tbd
# Functionality     : will update bios options required for fft flashing
# Return Value      : returns True on success and False otherwise
################################################################################


def update_bios_fft_stage_two(fw_type, image_type, test_case_id, script_id,
                              log_level="ALL", tbd=None):

    try:

        if "BGUP" == fw_type:
            pass                                                                #nothing to do if bgup
        elif "BIOS" == fw_type or "TEST" == fw_type:
            if 3 == lib_set_bios.xml_cli_set_bios(lib_constants.BIOS_LOCK,
                                                  test_case_id, script_id,
                                                  log_level, tbd):              #Diable bios lock, output comes from library
                pass
            else:
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid FW "
            "Type. Bios not updated", test_case_id, script_id, "None", "None",
            log_level, tbd)
            return False

        if 3 == lib_set_bios.xml_cli_set_bios(lib_constants.FTRR, test_case_id,
                                              script_id, log_level, tbd):       #Diable rtc lock, output comes from library
            return True
        else:
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        " updating bios", test_case_id, script_id, "BiosConf", "None",
        log_level, tbd)
        return False

################################################################################
# Function Name     : fft_flashing_in_os
# Parameters        : fw_type(BGUP),image_type(Release/review), test_case_id,
#                     , log_level, tbd
# Functionality     : will flash Bgup image using FFT tool in OS level
#                     cmd : FFT.exe batch spibios rompath:<image path> -l
# Return Value      : returns True on success and False otherwise
################################################################################


def fft_flashing_in_os(image_type, fw_type,test_case_id, script_id,
                       log_level="ALL", tbd=None):

    try:
        if "BGUP" == fw_type:                                                   #the command is applicable to flash BGUP bin image
            fft_path = utils.ReadConfig("BIOS_FLASHING","FFT_INSTALLED_PATH")   #FFT installed path
            file_to_flash = utils.ReadConfig("BGUP_IMAGE", fw_type)          #BGUP image path
            log_path = os.path.join(fft_path,'fft_flash_log.txt')               #path to store log generated
            if os.path.exists(log_path):
                os.remove(log_path)                                             #delete any older logs
            else:
                pass
            os.chdir(fft_path)
            cmd = "FFT.exe batch spibios rompath:" + file_to_flash + \
                  " -l > fft_flash_log.txt"
            os.system(cmd)
            time.sleep(lib_constants.SHORT_TIME)                                #Waiting for 60 secs after flashing
            os.chdir(lib_constants.SCRIPTDIR)
            with open(log_path,"r") as log:
                for lines in log:
                    if "Batch operation completed." in lines:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Log "
                        "file verified flashing as successful.'%s' "%lines,
                        test_case_id,script_id, "FFT", log_path, log_level, tbd)#If batch operation is successful from the log generated, flashing is successful
                        return True
                    else:
                        pass
            library.write_log(lib_constants.LOG_INFO, "INFO: Log file indicates"
            "flashing is failed", test_case_id, script_id, "FFT", log_path,
            log_level, tbd)                                                     #Fail if log shows any error
            return False

        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: FFT Flashing"
            " in OS implemened for BGUP only", test_case_id, script_id, "FFT",
            "None", log_level, tbd)                                             #To be implemented for future requirements
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
        "flashing bios", test_case_id, script_id, "FFT", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : verify_ifwi
# Parameters      : tc_id, script_id
# Functionality   : Verifying IFWI flashed successfully on SUT
# Return Value    : 'True'on successful action and 'False' on failure
################################################################################


def verify_bios_version(type_param, tc_id, script_id, log_level="ALL",
                        tbd=None):                                              #Verifying bios version after successful IFWI flashing

    try:
        if "CONFIG" not in type_param:
            type_param = type_param.replace(" ", "_")
            file_to_flash = utils.ReadConfig("BIOS_IMAGES", type_param)

            if "FAIL" in file_to_flash:                                         #failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " file information from Config.ini under tag BIOS_IMAGES and "
                " variable %s"%type_param, tc_id, script_id, "None", "None",
                log_level, tbd)
                return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%file_to_flash, tc_id, script_id,
                "None", "None", log_level, tbd)

        else:
            before_key, key, after_key = type_param.partition("CONFIG-")
            tag, key, variable = after_key.partition("-")

            file_to_flash = utils.ReadConfig(tag, variable)

            if "FAIL" in file_to_flash:                                         #failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " file information from Config.ini under tag section %s"%tag,
                tc_id, script_id, "None", "None", log_level, tbd)
                return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%file_to_flash, tc_id, script_id,
                "None", "None", log_level, tbd)

        curdir = lib_constants.SCRIPTDIR
        file_dir,file_name = os.path.split(file_to_flash)
        build_colour = file_name.split(tbd)[1][0]
        bios_version_file = file_name.split(build_colour)[1][:3].strip()
        bios_version_path = ""

        if tbd in lib_constants.BIGCORE:
            bios_version_path = lib_constants.BIGCORE_BIOSVERSION
        elif tbd in lib_constants.SMALLCORE:
            bios_version_path = lib_constants.SMALLCORE_BIOSVERSION
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Given platform "
            "not handled for bios version check" % file_to_flash, tc_id,
            script_id, "None", "None", log_level, tbd)

        if tbd.upper in lib_constants.TBD_PLATFORM:
            ret, bios_version_epcs = lib_read_bios.read_bios(bios_version_path,
                                                         tc_id, script_id,
                                                         curdir)
            bios_version_epcs = str(bios_version_epcs).strip()

            if tbd in bios_version_epcs and bios_version_file in \
                    bios_version_epcs:
                #if bios_version_epcs == bios_version_file or "0"+ \
                #bios_version_epcs == bios_version_file:
                library.write_log(lib_constants.LOG_INFO, "INFO: Bios Version "
                "matches between epcs log and filename", tc_id, script_id, "None",
                "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Bios Version not "
                "matching between epcs log and filename", tc_id, script_id,
                "None", "None", log_level, tbd)
                return False
        else:
            ret, bios_version_xml = lib_read_bios.xml_cli_read_bios(bios_version_path,
                                                             tc_id, script_id,
                                                             curdir)
            if tbd in bios_version_xml and bios_version_file in bios_version_xml:
                library.write_log(lib_constants.LOG_INFO, "INFO: Bios Version "
                "matches between config and BIOS ", tc_id, script_id, "None",
                "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Bios Version "
                "not matched between config and BIOS ", tc_id, script_id, "None",
                "None", log_level, tbd)
                return False


    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Verification of bios"
        " fails due to  %s."%e, tc_id ,script_id)
        return False
################################################################################
# Function Name   : generate_test_bios
# Parameters      : tc_id, script_id
# Functionality   : Verifying IFWI flashed successfully on SUT
# Return Value    : 'True'on successful action and 'False' on failure
################################################################################
"""

def verify_bios_version(type_param, tc_id, script_id, log_level="ALL",
                        tbd=None):                                              #Verifying bios version after successful IFWI flashing

    try:
        if "CONFIG" not in type_param:
            type_param = type_param.replace(" ", "_")
            file_to_flash = utils.ReadConfig("BIOS_IMAGES", type_param)
            if "FAIL" in file_to_flash:                                         # Failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " file information from Config.ini under tag BIOS_IMAGES and "
                " variable %s"%type_param, tc_id, script_id, "None", "None",
                log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%file_to_flash, tc_id, script_id,
                "None", "None", log_level, tbd)
        elif "BGUP" in type_param:
            file_to_flash = utils.ReadConfig("BGUP_IMAGE", "BGUP")
            if "FAIL" in file_to_flash:                                         # Failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " file information from Config.ini under tag section %s"%tag,
                tc_id, script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%file_to_flash, tc_id, script_id,
                "None", "None", log_level, tbd)
        else:
            before_key, key, after_key = type_param.partition("CONFIG-")
            tag, key, variable = after_key.partition("-")
            file_to_flash = utils.ReadConfig(tag, variable)
            if "FAIL" in file_to_flash:                                         # Failed to get file information from config
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to get"
                " file information from Config.ini under tag section %s"%tag,
                tc_id, script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: File to be "
                "flashed is identified as %s"%file_to_flash, tc_id, script_id,
                "None", "None", log_level, tbd)
        curdir = lib_constants.SCRIPTDIR
        file_dir,file_name = os.path.split(file_to_flash)
        bios_version_file = file_name.split("X")[1][:3].strip()
        bios_version_path = ""

        if tbd in lib_constants.BIGCORE:
            bios_version_path = lib_constants.BIGCORE_BIOSVERSION
        elif tbd in lib_constants.SMALLCORE:
            bios_version_path = lib_constants.SMALLCORE_BIOSVERSION
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Given platform "
            "not handled for bios version check"%file_to_flash, tc_id,
            script_id, "None", "None", log_level, tbd)

        ret, bios_version_epcs = lib_read_bios.read_bios(bios_version_path,
        tc_id, script_id, curdir)
        bios_version_epcs = str(bios_version_epcs).strip()
        if bios_version_epcs == bios_version_file or "0"+bios_version_epcs == \
            bios_version_file:
            library.write_log(lib_constants.LOG_INFO, "INFO: Bios Version "
            "matches between epcs log and filename", tc_id, script_id, "None",
            "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: Bios Version not "
            "matching between epcs log and filename", tc_id, script_id,
            "None", "None",log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Verification of bios"
        " fails due to  %s."%e, tc_id ,script_id)
        return False
"""

################################################################################
# Function Name : flashing_bios_ttk
# Parameters    : original_string, image_type, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To flash the required BIOS image using TTK
################################################################################


def flashing_bios_ttk(original_string, image_type, tc_id, script_id,
                      log_level="ALL", tbd=None):

    try:
        global image_type_path
        global image_address
        global mac_id

        if "CONFIG-" in image_type:                                             # Checks Config- is present in image type
            image_type_path = utils.parse_variable(image_type, tc_id,
                                                   script_id)
        elif image_type_path is None:
            image_type_path = utils.ReadConfig("BIOS_IMAGES", image_type)       # Reads rom file path based on image type, otherwise reads from command line option

        if image_address is None:                                               # Reads flash address from config if it is None, otherwise reads from command line option
            image_address = utils.ReadConfig("BIOS_IMAGES", "image_address")

        if mac_id is None:
            mac_id = utils.ReadConfig("TTK", "mac_id")

        if "FAIL:" in [image_type_path, image_address, mac_id]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the values for image_type_path and "
                              "image_address", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        original_string = original_string.split(" ")
        if 3 == len(original_string):
            flash_image = str(original_string[2])
        else:
            flash_image = "BIOS"

        log_file_size = os.path.getsize(image_type_path)                        # Checks for bin file size
        if not "" == log_file_size:
            library.write_log(lib_constants.LOG_INFO, "INFO: %s image file "
                              "size is %s" % (flash_image, log_file_size),
                              tc_id, script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Image "
                              "file is not proper", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        result = lib_ttk2_operations.\
            flash_ifwi(flash_image, image_address, image_type_path, mac_id,
                       tc_id, script_id, log_level, tbd)

        if "debug" in image_type.lower():
            time.sleep(500)
        else:
            time.sleep(lib_constants.FIVE_MIN)

        if result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "flashed %s %s" % (image_type, flash_image),
                              tc_id, script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                              "to flash %s %s" % (image_type, flash_image),
                              tc_id, script_id, "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : flashing_bios_dediprog
# Parameters    : ostr, image_type, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To flash the required BIOS image using Dediprog
################################################################################


def flashing_bios_dediprog(ostr, image_type, tc_id, script_id,
                           log_level="ALL", tbd=None):                          # Abstract method for to flash BIOS using Dediprog
    pass

################################################################################
# Function Name : flashing_bios
# Parameters    : ostr, image_type, tool_name, tc_id, script_id, log_level, tbd
# Return Value  : True on successful action, False otherwise
# Purpose       : To flash the required BIOS image
################################################################################


def flashing_bios(ostr, image_type, tool_name, tc_id, script_id,
                  log_level="ALL", tbd=None):                                   # Function calling for to flash BIOS using TTK, Dediprog

    try:
        if "TTK" == tool_name.upper():
            return flashing_bios_ttk(ostr, image_type, tc_id, script_id,
                                     log_level, tbd)
        elif "DEDIPROG" == tool_name.upper():
            return flashing_bios_dediprog(ostr, image_type, tc_id, script_id,
                                          log_level, tbd)
        elif "FFT" == tool_name.upper():
            pass
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
        opts, args = getopt.getopt(argv, "hi:t:p:a:",)
    except getopt.GetoptError:
        print("Please use -h command for Help Message")
        print("Usage: lib_flash_bios.py -h")
        return False

    try:
        if 0 == len(opts):
            print("Please use -h command for Help Message")
            print("Usage: lib_flash_bios.py -h")
            return False
        else:
            for opt, arg in opts:
                if opt == '-h':
                    print("##################################################\n")
                    print("Description:\n\tThis API aims at flashing the " \
                          "BIOS image on the platform using Tools like TTK, " \
                          "Dediprog etc. This API internally performs " \
                          "booting till OS after flashing operation is " \
                          "completed successfully.\n")

                    print("Arguments:\n-h\n\t For printing the help message")

                    print("-i\n\t image type e.g Release BIOS, Debug BIOS")

                    print("-t\n\t Tool name using which needs to Flash BIOS " \
                          "e.g TTK, DediProg")

                    print("-p\n\t Image path from where needs to pick the " \
                          "FW image\n")

                    print("-a\n\t Address for to flash BIOS w.r.to Platform\n")

                    print("Usage:\n\tlib_flash_bios.py -i <image_type> " \
                          "-t <Tool Name> -p <IFWI/BIOS file Path> " \
                          "-a <Address>\n")
                    print("####################################################")
                    return True
                elif opt in "-i":
                    image_type = arg
                elif opt in "-t":
                    tool_name = arg
                elif opt in "-p":
                    global image_type_path
                    image_type_path = arg
                elif opt in "-a":
                    global image_address
                    image_address = arg
                else:
                    return False
            flashing_bios("N/A", image_type, tool_name, "Flash_BIOS",
                          "Flash_BIOS", log_level="ALL", tbd=None)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
