__author__ = "kashokax/tnaidux"

# General Python Imports
import os
import re
import shutil
import socket
import subprocess
import time

# Local Python Imports
import library
import lib_constants
import utils

################################################################################
# Function Name : preload_os
# Parameters    : original_string, test_case_id, script_id, log_level and tbd
# Return Value  : True/false
# Purpose       : To Preload OS from specific source with Initial Setup
#                 Installations
################################################################################


def preload_os(original_string, test_case_id, script_id, log_level="All",
               tbd="None"):

    try:
        re_fetch = re.findall('.*Preload OS from(.*)', original_string, re.I)   # Re for fetching media type
        params = (re_fetch[0]).strip()

        if ("network" in params.lower() and "config" not in params.lower()) or \
                        "preload os" == original_string.lower():
            network_path = utils.ReadConfig("WIMIMAGER", "server_root")         # Get the share location path from config entry
            server_user = utils.ReadConfig("WIMIMAGER", "user")                 # Get the share location path user name  from config entry
            server_password = utils.ReadConfig("WIMIMAGER", "password")         # Get the share location path password  from config entry
            wim_file_path = utils.ReadConfig("WIMIMAGER", "wim_file_path")      # Get the wimimager tool path from config entry
            wimimager_path = utils.ReadConfig("WIMIMAGER", "wimimager_path")    # Get the location of wim file path from config entry
        elif 'config' in params.lower():
            config_tag, sec_name, option = params.split('-')
            sec_name = sec_name.strip()
            option = option.strip()
            network_path = utils.ReadConfig(sec_name, "server_root")            # Get the share location path  from config entry
            server_user = utils.ReadConfig(sec_name, "user")                    # Get the share location path user name  from config entry
            server_password = utils.ReadConfig(sec_name, "password")            # Get the share location path password  from config entry
            wim_file_path = utils.ReadConfig(sec_name, "wim_file_path")         # Get the wimimager tool path from config entry
            wimimager_path = utils.ReadConfig(sec_name, "wimimager_path")       # Get the location of wim file path from config entry
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Preload OS "
                              "using %s is not supported" % params,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False

        if "FAIL:" in [network_path, server_user, server_password,
                       wim_file_path, wimimager_path]:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get the required config entries from config.ini"
                              " file", test_case_id, script_id, "None",
                              "None", log_level, tbd)
            return False

        cmd_unmap_z_drive = lib_constants.delete_z_drive                        # Get command to delete Z drive

        map_z_drive = lib_constants.map_z_drive % (network_path, server_user,
                                                   server_password)             # Get command to map z drive

        map_z_drive_without = \
            lib_constants.map_z_drive_without % (network_path)                  # Get command to map z drive without user name and password

        cmd = subprocess.Popen(cmd_unmap_z_drive, shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE)                        # Command Run in subprocess to unmount the z drive
        exec_out = cmd.communicate()[0]

        if "not be found" in exec_out or "successfully" in exec_out:
            library.write_log(lib_constants.LOG_INFO, "INFO: Z: drive "
                              "deleted successfully", test_case_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "delete network drive", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        cmd = subprocess.Popen(map_z_drive, shell=True,
                               stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.STDOUT)                        # Command Run in subprocess to map z drive
        exec_out = cmd.communicate()[0]

        if "Multiple connections" in exec_out:
            cmd = subprocess.Popen(map_z_drive_without, shell=True,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)                    # Command Run in subprocess for creating network path
            exec_out = cmd.communicate()[0]

            if "successfully" in exec_out or "already in use" in exec_out:
                library.write_log(lib_constants.LOG_INFO, "INFO: Network "
                                  "path created successfully", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to create network drive", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        elif "successfully" in exec_out:
            library.write_log(lib_constants.LOG_INFO, "INFO: Network path "
                              "created successfully", test_case_id, script_id,
                              "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "map Wimimager network path", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        wimimager_complete_path = os.path.join(network_path, wimimager_path)    # Wimimager complete path
        wim_installer_path = os.path.join(network_path, wim_file_path)          # Wim file path

        if os.path.exists(wimimager_complete_path) and \
           os.path.exists(wim_installer_path):
            library.write_log(lib_constants.LOG_INFO, "INFO: Wimimager and "
                              "wim installer file path accessible from Z: "
                              "drive", test_case_id, script_id, "None",
                              "None", log_level, tbd)

            host_name = utils.ReadConfig("WIMIMAGER", "host_ip")                # Get the config entry for host ip from config file

            try:
                host_ip = socket.gethostbyname(host_name)
                sut_ip = socket.gethostname()

                cmd = subprocess.Popen("ping " + host_ip, shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE)                # Command Run in subprocess for ping operation
                exec_out = cmd.communicate()[0]

                if "timed out" in exec_out or "unreachable" in exec_out or \
                   "could not find" in exec_out:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Host connectivity unreachable",
                                      test_case_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to "
                                  "%s" % e, test_case_id, script_id, "None",
                                  "None", log_level, tbd)
                return False

            command_for_preload = wimimager_complete_path + ' /WimImage:' + \
                wim_installer_path + lib_constants.BATCH_SCRIPT                 # Command to preload OS with Initial Setup Installations

            cmd = subprocess.Popen(command_for_preload, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE)                    # Command Run in subprocess to preload OS with Initial Setup Installations
            exec_out = cmd.communicate()[0]

            if "with error 0" in exec_out or "with error 11" in exec_out:
                library.write_log(lib_constants.LOG_INFO, "INFO: OS Preload "
                                  "initiated successfully", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to initiate OS Preload", test_case_id,
                                  script_id, "None", "None", log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Wimimager "
                              "and wiminstaller file are not accessible",
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
