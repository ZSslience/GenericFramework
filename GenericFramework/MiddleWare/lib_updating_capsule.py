__author__ = "sushil3x"

###########################General Imports######################################
import os
import subprocess
import shutil
import glob
import codecs
import time
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_set_bios
import lib_read_bios
import lib_run_command
################################################################################
# Function Name : load_bios_mandatory_settings_updatecapsule
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To do pre-requisties for capsule update
################################################################################
def load_bios_mandatory_settings_updatecapsule(test_case_id,script_id,
        log_level = "ALL", tbd="None"):                                         # Function to do pre-requesties in BIOS & OS
    try:
        
        if "GLK" == tbd.upper():
            library.write_log(lib_constants.LOG_INFO, "INFO: Pre-Requisties "
                "settings for update Capsule in BIOS ", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # Print log message

            cmd = lib_constants.EFI_SECURITY_DISABLE                            # command to disbale secure boot

            if lib_set_bios.\
                    set_bios_security_option(cmd, test_case_id, script_id,
                        log_level, tbd):                                        # function call disbale secure boot


                create_update_bios_lock = lib_set_bios.\
                    lib_write_bios(lib_constants.GLK_BIOS_LOCK, test_case_id,
                        script_id, log_level, tbd)                              # Mandatory setting's in Bios
                capsule_update_flash_protection_range = lib_set_bios.\
                    lib_write_bios(lib_constants.GLK_FlASH_PROTECTION,
                        test_case_id, script_id, log_level, tbd)

                capsule_update_pre_requesties = [create_update_bios_lock,
                                        capsule_update_flash_protection_range]  # Checking return status
                capsule_update_flag = True

                for capsule_update_option in capsule_update_pre_requesties:
                    if 3 != capsule_update_option:
                        capsule_update_flag = False                             # Fail to set bios, then return with false message to main function
                        break
                    else:
                        continue

                if True == capsule_update_flag :                                # If bios is set successful,then continue execution
                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                        "Pre-Requisties settings for update Capsule in OS is "
                        "completed",
                            test_case_id, script_id, "None", "None", log_level,
                                tbd)                                            # Write true info log
                    return True

                else:

                    library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                        "set bios in & other pre-requesties",
                            test_case_id, script_id, "None", "None",
                                log_level, tbd)                                 # Write false info log
                    return False

            else:

                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "do pre-Requisties settings for update Capsule in OS ",
                    test_case_id, script_id, "None", "None", log_level, tbd)    # Write false info log
                return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Not "
            "applicable for this platform", test_case_id,
            script_id,"None", "None", log_level, tbd)                           # Write false info log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " load bios mandatory settings for Capsule update"
                " as %s " %e, test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write error log
        return False

################################################################################
# Function Name : run_bcdedit
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To do run bcdedit command
################################################################################
def run_bcdedit(test_case_id, script_id, log_level="ALL", tbd=None):            # Function to run bcdedit command
    try:

        command = lib_constants.CAPSULE_UPDATE_TESTSIGNING                      # Command to run bcdedit
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out = process.communicate()[0]

        if "successfully" in out.lower():
            library.write_log(lib_constants.LOG_INFO, "INFO: Command Executed "
                "successfully for setting testsigning-yes", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # Write pass info to log
            return True

        else:

            library.write_log(lib_constants.LOG_INFO, "INFO: Command Executed "
                "un-successfully for setting testsigning-yes ", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # Write fail info to log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception while "
            "running bcdedit  %s " %e, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # Write error info to log
        return False


################################################################################
# Function Name : verification_bcdedit
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To do run bcdedit command
################################################################################
def verification_bcdedit(test_case_id, script_id, log_level = "ALL", tbd="None"):
    try:

        library.write_log(lib_constants.LOG_INFO, "INFO: Verifying of "
            "bcdedit", test_case_id, script_id,"None", "None", log_level, tbd)

        list_file = glob.glob('*.txt')                                          # Delete older log if any
        for file in list_file:
            if file.startswith("bcdedit"):
                os.remove(file)

        command = lib_constants.CAPSULE_UPDATE_TESTSIGNING_VERIFY               # Command to run verification of bcdedit
        process = subprocess.Popen(command, stdout=subprocess.PIPE,shell=True,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        out = process.communicate()[0]

        with open('bcdedit.txt','r') as filepointer:                            # log parsing to check if verifiation is successful
            for line in filepointer:
                if "testsigning" in line.lower() and "yes" in line.lower():
                    library.write_log(lib_constants.LOG_INFO, "INFO: Command  "
                    " bcdedit is set successful", test_case_id, script_id,
                        "None", "None",log_level, tbd)                          # Write pass info to log
                    return True
                else:
                    pass

            library.write_log(lib_constants.LOG_INFO, "INFO: bcdedit is "
            "not set", test_case_id, script_id, "None", "None", log_level, tbd) # Write fail info to log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "verification of bcdedit %s " %e, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # Write Fail info to log
        return False



################################################################################
# Function Name : create_capsule
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To create capsule
################################################################################
def create_capsule(test_case_id,script_id, log_level = "ALL", tbd="None"):
    try:
        flag = False
        capsule_path = "None"
        path = utils.ReadConfig("capsule_create","capsule_create_path")         # Reading config details
        image_file_path = utils.ReadConfig("capsule_create","image_file_path")
        image_file_name = utils.ReadConfig("capsule_create","file_name")
        ver = utils.ReadConfig("capsule_create","version")
        arch = utils.ReadConfig("capsule_create","architecture")
        log_path = utils.ReadConfig("capsule_create","capsule_log_path")
        gencapsule_path = path

        if "FAIL:" in [path,image_file_path,image_file_name,
                       ver,arch,log_path,gencapsule_path]:                      # checking config entries provided or not
            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "not found under [capsule_create]", test_case_id, script_id,
                    "None", "None", log_level, tbd)                             # write log info that config not present
            return False
        else:

            library.write_log(lib_constants.LOG_INFO, "INFO: Config entry "
                "found", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # write log info that config is present

        os.chdir(path)                                                          # Deleting old files
        for file in os.listdir(path):
            if file.startswith(lib_constants.CAPSULE_FILE) :
                os.remove(file)
            elif file.startswith(lib_constants.CAPSULE_FOLDER):
                shutil.rmtree(file)

        if os.path.exists(path):
            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule create "
                "tool found", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write pass info to log

            if os.path.exists(image_file_path):
                library.write_log(lib_constants.LOG_INFO, "INFO: Capsule Image "
                    "file found", test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         # Write pass info to log

                os.chdir(path)
                command = "CreateCapsule.bat" + " -b " + image_file_name + \
                " -ver " + ver + " -arch " + arch + " > capsule_command_log.txt"

                process_out = subprocess.Popen(command,
                                    stdout=subprocess.PIPE, shell=False,
                                               stdin=subprocess.PIPE,
                                               stderr=subprocess.PIPE)        # Command to create capsule
                output = process_out.communicate()[0]
                time.sleep(lib_constants.TEN_SECONDS)                           # Delay provided to completed the execution of command

                list_file = glob.glob('*.txt')                                  # Checking for log & parsing for successful message
                for file in list_file:
                    if file.startswith(lib_constants.CAPSULE_FILE):
                        with codecs.open(file,"r","utf-8", errors="ignore") as \
                                fileponter:
                            for line in fileponter:
                                if None != line:
                                    if lib_constants.CAPSULE_SEARCH_PARAM in\
                                            line.lower().strip():
                                        library.write_log(lib_constants.LOG_INFO
                                        , "INFO: Capsule created successfull "
                                            , test_case_id, script_id,
                                            "None", "None", log_level, tbd)     # Write pass info to log
                                        for dirname in os.listdir(path):
                                            if dirname.startswith("SysFwCapsule_"):

                                                capsule_path = \
                                                    os.path.join(path, dirname)
                                                if os.path.exists(capsule_path):
                                                    library.\
                                                    write_log(lib_constants.
                                                    LOG_INFO,"INFO: Capsule "
                                                    "folder found",
                                                    test_case_id, script_id,
                                                    "None", "None", log_level,
                                                        tbd)                    # Write pass info to log
                                                    break

                                                else:

                                                    library.\
                                                    write_log(lib_constants.
                                                    LOG_INFO, "INFO: Capsule "
                                                    "folder not found",
                                                    test_case_id, script_id,
                                                    "None", "None", log_level,
                                                        tbd)                    # Write fail info to log

                                                return False

                                            else:
                                                pass

                                        else:
                                            library.write_log(lib_constants.
                                                LOG_INFO, "INFO: Capsule folder "
                                                "not created", test_case_id,
                                                script_id, "None", "None",
                                                log_level, tbd)                 # Write fail info to log
                                            return False
                                else:
                                    pass

                    else:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Unable"
                        " to create the capsule", test_case_id,
                            script_id, "None", "None", log_level, tbd)          # Write fail info to log
                        return False


                os.chdir(capsule_path)                                          # Changing a directory
                for dirname in os.listdir(capsule_path):
                    if dirname.endswith('bin'):
                        os.rename(dirname,lib_constants.CAPSULE_BIN)            # Changing the name of file
                        flag = True

                if flag == True:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Bin "
                        "File name changed to biosupdate.fv", test_case_id,
                            script_id, "None", "None",log_level, tbd)           # Write pass info to log
                    return True

                else:

                    library.write_log(lib_constants.LOG_INFO, "INFO: Bin file "
                        "not found", test_case_id, script_id, "None", "None",
                            log_level, tbd)                                     # Write fail info to log
                    return False

            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Capsule "
                    "Image file not found", test_case_id, script_id,
                        "None", "None", log_level, tbd)                         # Write fail info to log
                return False

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule "
                "create tool not found", test_case_id, script_id, "None",
                    "None", log_level, tbd)                                     # Write fail info to log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " creating an capsule update %s " %e, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # Write error info to log
        return False


################################################################################
# Function Name : create_nsh_file_copy_bin_file
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To copy necessary file to S drive (Logical Drive)
################################################################################
def create_nsh_file_copy_bin_file(test_case_id,script_id,
                            log_level = "ALL", tbd="None"):
    try:
        capsule_path = "None"
        flash_file = "None"

        gencapsule_path = utils.ReadConfig("capsule_create",
                                           "capsule_create_path")               # Reading config details

        gensdrive_create = lib_run_command.\
            create_logical_drive('S', test_case_id, script_id, log_level, tbd)  # fucntion to create logical drive

        if True == gensdrive_create:
            library.write_log(lib_constants.LOG_INFO,
                "INFO: Logical Drive is created", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # Write pass info to log

        else:

            library.write_log(lib_constants.LOG_INFO,
                "INFO: Logical Drive is unable create", test_case_id,
                    script_id, "None", "None", log_level, tbd)                  # Write fail info to log
            return False

        cwd = lib_constants.SCRIPTDIR                                           # Script dir path
        os.chdir(cwd)
        if os.path.exists('S:\\'):                                              # check for new logical drive
            time.sleep(lib_constants.FIVE_SECONDS)                              # sleep for 5 seconds
            shutil.copy("startup.nsh","S:\\\\")                                 # copy startup nsh to current working directory
            if os.path.exists(cwd + "\subscript.nsh"):
                time.sleep(lib_constants.FIVE_SECONDS)                          # sleep for 5 seconds
                shutil.copy("subscript.nsh", "S:\\\\")

        os.chdir(gencapsule_path)                                               # Changing the directory
        for dirname in os.listdir(gencapsule_path):
            if dirname.startswith("SysFwCapsule"):
                capsule_path = os.path.join(gencapsule_path,dirname)
                library.write_log(lib_constants.LOG_INFO, "INFO: Capsule "
                    "folder found", test_case_id, script_id, "None", "None",
                        log_level, tbd)                                         # Write pass info to log
                break
            else:
                pass

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule folder "
                "not found", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write fail info to log
            return False


        os.chdir(capsule_path)                                                  # Moving neccessary file to S drive
        for dirname in os.listdir(capsule_path):
            if dirname.endswith('fv'):
                flash_file = os.path.join(capsule_path,dirname)
                shutil.copy2(flash_file,"S:\\\\")

        capsule_ifwi_path = lib_constants.CAPSULE_FILE_SDRIVE                  # ifwi file path

        if os.path.exists(capsule_ifwi_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule file is "
                "found in S drive", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write pass info to log
            return True

        else:

            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule file is "
                "not found in S drive", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write fail info to log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " copying files to Sdrive %s " %e, test_case_id, script_id, "None",
                "None", log_level, tbd)                                         # Write error info to log
        return False

################################################################################
# Function Name : nsh_file_gen
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To create startup.nsh file
################################################################################
def nsh_file_gen(test_case_id, script_id, log_level="ALL", tbd=None):
    try:
        f = open("startup.nsh", 'w')                                            # file operation
        f.write("bcfg boot mv 01 00" + '\n')
        f.write('fs0:' + '\n')
        f.write("reset")
        f.close()                                                               # file closing after writing to file
        nsh1_size = os.path.getsize("startup.nsh")

        if '0' == nsh1_size:                                                    # check for startup nsh file sizes and return false if size is 0
            library.write_log(lib_constants.LOG_INFO, "INFO: .nsh file is "
                "not generated properly", test_case_id, script_id, "None",
                    "None", log_level, tbd)                                     # Write pass info to log
            return False

        else:

            library.write_log(lib_constants.LOG_INFO, "INFO: .nsh file is "
                "successfully created", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write Fail info to log
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in "
            "creating a nsh file due to %s " % e, test_case_id, script_id,
                "None", "None", log_level, tbd)                                 # Write error info to log
        return False

################################################################################
# Function Name : cleanup_nshdrive_osdrive
# Parameters    : test_case_id,script_id,log_level,tbd
# Return Value  : True on success, False on failure
# Functionality : To do cleanup activity in OS
################################################################################
def cleanup_nshdrive_osdrive(test_case_id, script_id, log_level="ALL", tbd=None):
    try:

        flag_ifwi = False
        flag_nsh = False
        sdrive_path = "S:\\"
        fv_path = " "
        startup_path = " "
        cmd = lib_constants.EFI_SECURITY_ENABLE                                 # Pass command to function

        gensdrive_create = lib_run_command.\
            create_logical_drive('S', test_case_id, script_id, log_level, tbd)  # Function call to mount sdrive

        if True == gensdrive_create:
            library.write_log(lib_constants.LOG_INFO, "INFO: Logical Drive is "
                "created", test_case_id, script_id, "None", "None", log_level,
                    tbd)                                                        # Write pass info to log
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Logical Drive is "
                "unable create", test_case_id, script_id, "None", "None",
                    log_level, tbd)                                             # Write fail info to log
            return False


        os.chdir(sdrive_path)                                                   # Removing file from Sdrive
        for dirname in os.listdir(sdrive_path):
            if dirname.endswith('fv'):
                fv_path = os.path.join(sdrive_path, dirname)
                os.remove(dirname)
            elif dirname.startswith('startup'):
                startup_path = os.path.join(sdrive_path, dirname)
                os.remove(dirname)

        time.sleep(lib_constants.TEN_SECONDS)                                   # Delay in execution

        if not (os.path.exists(fv_path) and os.path.exists(startup_path)):      # Checking the path of files
            flag_ifwi = True
            flag_nsh = True

        if True == flag_ifwi and True == flag_nsh:                              # If files are removed
            library.write_log(lib_constants.LOG_INFO, "INFO: Capsule file i.e. "
                "biosupdate.fv & startup.nsh deleted from S drive",
                    test_case_id, script_id, "None", "None", log_level, tbd)    # Write Pass info to log

            if lib_set_bios.set_bios_security_option(cmd, test_case_id,
                script_id, log_level, tbd):                                     # Library call to enable secure boot
                library.write_log(lib_constants.LOG_INFO, "INFO: Secure Boot "
                    "enable initiated successfully. ", test_case_id, script_id,
                        "None", "None", log_level, tbd)                         # Write Pass info to log
                return True

            else:

                library.write_log(lib_constants.LOG_INFO, "INFO: Secure Boot "
                    "enable could not be initiated", test_case_id, script_id,
                        "None", "None", log_level, tbd)                         # Write Fail info to log
                return False

        else:

            library.write_log(lib_constants.LOG_INFO, "INFO: Unable to delete "
                "capsule file from S drive", test_case_id, script_id, "None",
                    "None", log_level, tbd)                                     # Write Fail info to log
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in clean "
            "up activity due to %s " % e, test_case_id, script_id, "None",
                "None", log_level, tbd)                                         # Write erro info to log
        return False