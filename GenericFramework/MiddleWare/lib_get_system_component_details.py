__author__ = "Automation Development Team"

# General Python Imports
import csv
import glob
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict

# Local Python Imports
import lib_constants
import library
import utils
import lib_tool_installation
import lib_tat_tool_installation
import lib_xmlcli

################################################################################
# Function name  : get_component_details_from_bios()
# Description    : Code to get System (CPU/Memory) component info from BIOS
# Parameters     : input, tc_id, script_id, log_level, tbd
# Return Value   : cpu_component_bios.txt/memory_component_bios.txt/False
################################################################################


def get_component_details_from_bios(input, tc_id, script_id, log_level="ALL",
                                    tbd=None):

    try:

        logfile = script_id.split(".")[0]
        log_path = lib_constants.SCRIPTDIR

        sys.path.append(lib_xmlcli.xml_cli_tool_path)
        import XmlCli as cli
        cli.clb._setCliAccess("winsdk")
        result = cli.savexml()

        if 0 == result:
            if os.path.exists(lib_xmlcli.XMLCLI_PATH_LOG):
                library.write_log(lib_constants.LOG_INFO, "INFO: Online log "
                                  "generated successfully", tc_id, script_id,
                                  "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate Online log", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if "cpu" == input.lower():                                              # Checks if the input is cpu
            cpu_log_path = log_path + r"\\" + logfile + \
                "_cpu_component_bios.txt"

            if os.path.exists(cpu_log_path):                                    # Removes if the cpu log is already existing
                os.remove(cpu_log_path)

            cpu_type = cpu_id = micro_code_rev = physical_cores = ""

            with open(cpu_log_path, "a+") as cpu_data:                          # Creates new logfile to save the cpu details
                with open(lib_xmlcli.XMLCLI_PATH_LOG, "r") as f:                # Opens the XmlCli log to read the cpu details from the log
                    for index, line in enumerate(f):
                        if "<!-- Type:" in line:
                            cpu_type = \
                                line.split('//')[1].strip().split(':')[1]
                        if "<!-- ID:" in line:
                            cpu_id = line.split('//')[1].strip().\
                                split(':')[1].strip()
                        if "<!-- Microcode Revision:" in line:
                            micro_code_rev = line.split("//")[1].strip().\
                                split(':')[1].strip()
                        if "<!-- Number of Processors:" in line:
                            physical_cores = line.split("//")[1].strip().\
                                split(':')[1].strip().split('/')[0].strip().\
                                split('Core')[0].strip()                        # Checks for the string 'Type,microcode revesion and number processor' and writes to the log file

                    cpu_data.write("CPU Type: " + str(cpu_type) + "\n")
                    cpu_data.write("CPU ID: " + str(cpu_id) + "\n")
                    cpu_data.write("Microcode Revision: 0x" +
                                   str(micro_code_rev) + "\n")
                    cpu_data.write("Physical Cores: " +
                                   str(physical_cores) + "\n")
                    return cpu_log_path
        elif "memory" == input.lower() or "memory info" == input.lower():       # Checks if input is memory
            memory_log_path = log_path + r"\\" + logfile + \
                "_memory_component_bios.txt"

            if os.path.exists(memory_log_path):
                os.remove(memory_log_path)                                      # Removes if the file already existing

            size_index = 0
            frequency = size_gb = ""

            with open(memory_log_path, "a+") as mem_data:
                with open(lib_xmlcli.XMLCLI_PATH_LOG, "r") as f:                # Opens the EPCS log and searchs for the required memory string 'total memory'
                    for index, line in enumerate(f):
                        if "<!-- Total Memory:" in line:
                            size_index = index
                            size_mb = str(line.split(':')[1]).split("MB")[0]
                            size_gb = int(str(size_mb).strip())/1024
                        if "<!-- Memory Frequency:" in line:
                            if index > size_index:
                                frequency = str(line.split(':')[1]).strip()
                                if "-->" in frequency:
                                    frequency = \
                                        frequency.replace("-->", "").strip()

                    mem_data.write("Memory Frequency: " + frequency + "\n")
                    mem_data.write("Total Memory: " + str(size_gb) + " GB")
                    return memory_log_path
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Parameter "
                              "%s is not implemented", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name   : get_memory_from_os()
# Parameters      : tc_id, script_id, log_level, tbd
# Description     : Code to get System (Memory) component info from OS
# Return Value    : True/False
################################################################################


def get_memory_from_os(tc_id, script_id, log_level="ALL", tbd=None):            # Function to get cpu and memory details from os

    try:
        logfile = script_id.split(".")[0]
        log_path = lib_constants.SCRIPTDIR

        if lib_tool_installation.execute_syscope():                             # Executes the syscope tool command line and saves the log in the tool folder
            library.write_log(lib_constants.LOG_INFO, "INFO: Log has been "
                              "generated by System Scope Tool", tc_id,
                              script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Log has not"
                              " been generated by System Scope Tool", tc_id,
                              script_id, "None", "None", log_level, tbd)

        memory_os_path = log_path + r"\\" + logfile + \
            "_memory_component_os.txt"

        if os.path.exists(memory_os_path):
            os.remove(memory_os_path)

        system_scope_log = \
            lib_constants.SYSCOPE_TOOLDIR + "\\Logs\\syscope.xml"

        tree = ET.parse(system_scope_log)
        root = tree.getroot()
        root1 = root.findall(".//*[@Name='Physical Memory']/*")
        if len(root1) <= 0:
            root1 = root.findall(".//*[@Name='Physical Memory 0']/*")

        slot = slot_data = total_mem = speed = ''
        size = 0

        for items in root1:                                                     # Opens and reads the log and fetches the memory details required
            out = items.attrib
            out = out["Key"],out["Value"]
            if 'Device Locator' == out[0]:
                if "ChannelA-DIMM0" in out:
                    slot = "Channel 0 Slot 0: Populated & Enabled"
                elif "ChannelA-DIMM1" in out:
                    slot = "Channel 0 Slot 1: Populated & Enabled"
                elif "ChannelB-DIMM0" in out:
                    slot = "Channel 1 Slot 0: Populated & Enabled"
                elif "ChannelB-DIMM1" in out:
                    slot = "Channel 1 Slot 1: Populated & Enabled"
                else:
                    pass
                slot_data = slot_data+slot+"\n"                                 # Checks for the string channel and the DIM if present then it is written as populated and Enabled
            if 'Speed' in out:
                speed = "Memory Frequency: " + out[1]
            if ('Capacity' in out) > 1:                                         # Checks for the string 'Capacity' in the dictionary
                total_mem = out[1]
                total_mem = total_mem.split(".")[0]                             # splits and gets only the Numeric value
                size = int(size)+int(total_mem)
                total_mem = "Total Memory: "+ str(size) + " GB"
        with open(memory_os_path,"a+") as mem_os_data:                          # opens the file and writes the memory details into the txt file
            mem_os_data.write(slot_data)
            mem_os_data.write(speed + "\n")
            mem_os_data.write(total_mem)
        mem_os_data.close()
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# function    : get_cpu_from_os
# description : fetches cpu details from os using syscope log
# parameter   : tc_id,script_id,log_level and tbd
# Return      : True/False
################################################################################
def get_cpu_from_os(tc_id,script_id,log_level = "ALL",tbd= None):               # function to get cpu and memory details from os
    import xml.etree.ElementTree as ET                                          # importing Xml parsing module to extract the text from the xml
    logfile =script_id.split(".")[0]
    log_path =lib_constants.SCRIPTDIR
    sysscopepath = lib_constants.SYSCOPE_TOOLDIR                    # reads the config file to fetch the details of tool directory
    try:
        if lib_tool_installation.execute_syscope():                             # executes the syscope tool command line and saves the log in the tool folder
            library.write_log(lib_constants.LOG_INFO,
            "Log has been generated By System Scope tool",tc_id,
                              script_id,log_level,tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,
            "Log has not been generated By System Scope tool",
                              tc_id,script_id,log_level,tbd)
        os.chdir(sysscopepath)
        cpu_os_path = log_path+r"\\"+logfile+"_cpu_component_os.txt"
        if os.path.exists(cpu_os_path):
            os.remove(cpu_os_path)                                              # checks if older log file exists then removes the older logs
        tree = ET.parse(lib_constants.SYSCOPE_TOOLDIR + '\\syscope.xml')
        root = tree.getroot()

        root1 = root.findall(".//*[@Name='Processor Information']/*")
        max_clock_speed,cpu_type,physical_cores,micro_code_rev,cpu_id,\
        no_phy_cpu_processor,no_log_cpu_processor,stepping,no_of_core =\
            "", "", "", "", "", "", "", "", ""
        for items in root1:                                                     # opens and reads the log and fetches the memory details required
            out = items.attrib
            out = out.get('Name')
            input = './/*[@Name='+"'"+out+"']/*"
            root2 = root.findall(input)
            for items in root2:
                data = items.attrib
                data = list(data.keys()), list(data.values())
                if 'Name' == data[1][0]:
                    cpu_type = "Cpu Type: " + data[1][1]
                if 'Microcode Version' == data[1][0]:
                    s = data[1][1]
                    data = str(s).split("X")[1]
                    micro_code_rev = "Microcode Revision: "+ data
                if 'Maximum Clock Speed' == data[1][0]:
                    max_clock_speed = "Maximum Clock Speed: "+data[1][1]
                if 'Number of Physical Processor Cores' == data[1][0]:
                    no_phy_cpu_processor = "Number of Physical Processor Cores:"\
                                           +data[1][1]
                    no_of_core = "No of Cores:"\
                                           +data[1][1]
                if 'Number of Logical Processor Cores' == data[1][0]:
                    no_log_cpu_processor = "Number of Logical Processor Cores: "\
                                           + data[1][1]
                if 'CPU Internal Stepping' == data[1][0]:
                    stepping = 'Stepping:'+data[1][1]
        root1 = root.findall(".//*[@Name='Processor Family Details']/*")
        for items in root1:                                                     # opens and reads the log and fetches the memory details required
            out = items.attrib
            out = list(out.keys()), list(out.values())
            if 'CPUID'==out[1][0]:
                cpu_id = "Cpu Id: "+ out[1][1]
        root1 = root.findall(".//*[@Name='Topology Details']/*")
        for items in root1:                                                     # opens and reads the log and fetches the memory details required
            out = items.attrib
            out = list(out.keys()), list(out.values())

            if "Number of Physical Processor Cores" == out[1][0]:
                physical_cores="Physical Cores: "+out[1][1]

        with open(cpu_os_path, "a+") as cpu_os_data:                            # opens the file and writes the memory details into the txt file
            cpu_os_data.write(cpu_type+"\n")
            cpu_os_data.write(cpu_id+"\n")
            cpu_os_data.write(micro_code_rev+ "\n")
            cpu_os_data.write(physical_cores+"\n")
            cpu_os_data.write(max_clock_speed+"\n")
            cpu_os_data.write(no_phy_cpu_processor+"\n")
            cpu_os_data.write(no_of_core+"\n")
            cpu_os_data.write(no_log_cpu_processor+"\n")
            cpu_os_data.write(stepping+"\n")
            cpu_os_data.write(cpu_id+"\n")
            cpu_os_data.write(physical_cores + "\n")
        return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: "+str(e),
                          tc_id,script_id,log_level,tbd)
        return False
################################################################################
# function    : get_full_cpu_from_os
# description : fetches cpu details from os using syscope log
# parameter   : tc_id,script_id,log_level and tbd
# Return      : True/False
################################################################################
def get_full_cpu_from_os(tc_id, script_id, log_level="ALL", tbd=None):          # function to get cpu and memory details from os
    import xml.etree.ElementTree as ET                                          # importing Xml parsing module to extract the text from the xml
    logfile = script_id.split(".")[0]
    log_path = lib_constants.SCRIPTDIR
    sysscopepath = lib_constants.SYSCOPE_TOOLDIR                   # reads the config file to fetch the details of tool directory
    try:
        try:
            systemscopepath = lib_constants.SYSCOPE_TOOLDIR         # reading the config file to fetch the details of Systemscope tool
            if lib_tool_installation.install_Syscope(tc_id, script_id,
                                                     log_level, tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO :SystemScope"
                    "is Installed.", tc_id, script_id, "SystemScope","None",
                        log_level, tbd)                                         # Check if system scope is installed otherwise install the tool
            else:
                library.write_log(lib_constants.LOG_INFO,
                    "INFO : SystemScope is NOT installed, Installing Now", tc_id,
                        script_id, "system scope", "None", log_level, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: In Installation "
                ": " + str(e),tc_id, script_id, "system scope", "None",
                    log_level, tbd)
            return False

        if lib_tool_installation.execute_syscope():                             # executes the syscope tool command line and saves the log in the tool folder
            library.write_log(lib_constants.LOG_INFO,
                "Log has been generated By System Scope tool", tc_id,
                    script_id, log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,
                "Log has not been generated By System Scope tool",
                    tc_id, script_id, log_level, tbd)
            return False

        os.chdir(sysscopepath)
        tree = ET.parse(r'syscope.xml')
        root = tree.getroot()
        root1 = root.findall(".//*[@Name='Processor Information']/*")

        tag_subtable_list = []
        for item in root1:
            all_table_in_acpi = item.attrib                                     # get all the attribute of the tables
            for key, value in list(all_table_in_acpi.items()):                        # loop though each table attribute and store the value in list
                tag_subtable_list.append(str(value))


        for cpu_search_element in tag_subtable_list:                            # checking for child table name under ACPI
            try:
                os.chdir(sysscopepath)
                tag_table_path = log_path + r"\\" + logfile + "_fullcpu_component_os.txt"
                if os.path.exists(tag_table_path):
                    os.remove(tag_table_path)                                   # checks if older log file exists then removes the older logs
                tree = ET.parse(r'syscope.xml')
                getroot = tree.getroot()                                        # get root node of the xml tree
                cpu_content = getroot.findall(".//*[@Na"
                                    "me='" + cpu_search_element + "']/Item")    # search for the table name and get all the items of the table

                #with open(tag_table_path,"a+") as tag_table:
                 #   tag_table.write(cpu_search_element + "\n")

                for expectedtable in cpu_content:                               # loop through matching table elements content
                    table_content = expectedtable.attrib                        # find the attribute of the content
                                                                                #print table_content['Key'],table_content['Value']
                    try:
                        with open(tag_table_path,"a+") as tag_table:  # opens the file and writes the value of table content
                            tag_table.write(table_content['Key'] + ":" + table_content['Value'])
                            tag_table.write("\n")
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR,
                                          "ERROR: In creating Dump : " + str(e),
                                          tc_id, script_id, "None", "None",
                                          log_level, tbd)
                        return False

                return tag_table_path
            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: In parsing log:  " + str(e),
                                  tc_id, script_id, log_level, tbd)
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: " + str(e),
                          tc_id, script_id, log_level, tbd)
        return False

################################################################################
# function    : get_full_memory_from_os
# description : fetches cpu details from os using syscope log
# parameter   : tc_id,script_id,log_level and tbd
# Return      : True/False
################################################################################
def get_full_memory_from_os(tc_id, script_id, log_level="ALL",tbd=None):        # function to get cpu and memory details from os
    import xml.etree.ElementTree as ET                                          # importing Xml parsing module to extract the text from the xml
    logfile = script_id.split(".")[0]
    log_path = lib_constants.SCRIPTDIR
    sysscopepath = lib_constants.SYSCOPE_TOOLDIR                   # reads the config file to fetch the details of tool directory
    try:
        try:
            systemscopepath = lib_constants.SYSCOPE_TOOLDIR         # reading the config file to fetch the details of Systemscope tool
            if lib_tool_installation.install_Syscope(tc_id, script_id,
                                                     log_level, tbd):
                library.write_log(lib_constants.LOG_INFO, "INFO :SystemScope"
                    "is Installed.", tc_id, script_id, "SystemScope", "None",
                        log_level, tbd)                                         # Check if system scope is installed otherwise install the tool
            else:
                library.write_log(lib_constants.LOG_INFO,
                    "INFO : SystemScope is NOT installed, Installing Now", tc_id,
                        script_id, "system scope", "None", log_level, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: In Installation "
                ": " + str(e), tc_id, script_id, "system scope", "None",
                    log_level, tbd)
            return False

        if lib_tool_installation.execute_syscope():                             # executes the syscope tool command line and saves the log in the tool folder
            library.write_log(lib_constants.LOG_INFO,
                "Log has been generated By System Scope tool", tc_id,
                    script_id, log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_INFO,
                "Log has not been generated By System Scope tool",
                    tc_id, script_id, log_level, tbd)
            return False


        os.chdir(sysscopepath)
        tree = ET.parse(r'syscope.xml')
        root = tree.getroot()
        tag_memory_subtable_list = []
        root1 = root.findall(".//*[@Name='Memory']/*")

        for items in root1:  # opens and reads the log and fetches the memory details required
            table_content = items.attrib
            for key, value in list(table_content.items()):  # loop though each table attribute and store the value in list
                tag_memory_subtable_list.append(str(value))

        for tag_search_element in tag_memory_subtable_list:  # checking for child table name under ACPI
            try:
                os.chdir(sysscopepath)
                tag_log_path = log_path + r"\\" + logfile + "_fullcpu_component_os.txt"

                tree = ET.parse(r'syscope.xml')
                getroot = tree.getroot()                                        # get root node of the xml tree
                tag_content = getroot.findall(".//*[@Name='" + tag_search_element + "']/Item")  # search for the table name and get all the items of the table

                for expectedtable in tag_content:                               # loop through matching table elements content
                    table_content = expectedtable.attrib                        # find the attribute of the content
                                                                                #print table_content['Key'],table_content['Value']
                    try:
                        with open(tag_log_path,"a+") as tag_table:  # opens the file and writes the value of table content
                            tag_table.write(table_content['Key'] + ":" + table_content['Value'])
                            tag_table.write("\n")
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR,
                            "ERROR: In creating Dump : " + str(e),
                                tc_id, script_id, "None", "None",
                                    log_level, tbd)
                        return False

            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR,
                                  "ERROR: In parsing log:  " + str(e),
                                  tc_id, script_id, log_level, tbd)
                return False
        flag = True
        if flag  == True:
            return tag_log_path                                                 # Return the Table dump created from Systemscope log
        else:
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: " + str(e),
                          tc_id, script_id, log_level, tbd)
        return False

################################################################################
# Function Name : get_component_details_from_os
# description   : fetches cpu and memory details from os using syscope log
# Parameters    : input, tc_id, script_id, log_level and tbd
# Return value  : cpu_component_os.txt/False
################################################################################


def get_component_details(input, level, tc_id, script_id, log_level="ALL",
                          tbd=None):

    try:
        if "os" == level.lower():
            if "full cpu info" == input.lower():
                full_cpu_os = get_full_cpu_from_os(tc_id, script_id, log_level,
                                                   tbd)

                full_memory_os = get_full_memory_from_os(tc_id, script_id,
                                                         log_level, tbd)

                if full_cpu_os:
                    if full_memory_os:
                        return "fullcpu_component_os.txt"                       # Returns log file for cpu details
                    else:
                        return False
            elif "cpu info" == input.lower():                                   # Executes get cpu_from_os function to get the cpu details from os
                cpu_os = get_cpu_from_os(tc_id, script_id, log_level, tbd)

                if cpu_os:
                    return "cpu_component_os.txt"                               # Returns log file for cpu details
                else:
                    return False
            elif "memory" in input.lower():
                memory_os = get_memory_from_os(tc_id, script_id, log_level,
                                               tbd)                             # Executs memory_from_os function to get memory details from os
                if memory_os:
                    return "memory_component_os.txt"                            # Returns logfile for memory details
                else:
                    return False
            else:
                return False
        elif "bios" == level.lower():                                           # Checks if the device level is bios. then calls the function to fetch the component details from bios
            component_details = \
                get_component_details_from_bios(input, tc_id, script_id,
                                                log_level, tbd)
            if component_details:
                return component_details
            else:
                return False                                                    # Returns component details from bios.
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : Source_check
# Description   : checks for the source where the system details is fetched
# Parameter     : variable, tc_id, script_id, log_level and tbd
# Return Value  : True/False
################################################################################


def source_check(variable, tc_id, script_id, log_level="ALL", tbd="None"):

    try:
        if "device manager" == variable.lower():                                # Checks for the enivironment where the components has been verified
            library.write_log(lib_constants.LOG_INFO, "INFO: System details "
                              "is fetched from %s" % variable, tc_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        elif "WITHOUT_USING" == variable.upper():
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Fail to "
                              "get system details, source %s parameter not "
                              "implemented" % variable, tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# function    : getMSR_Power_Limit
# description : checks for the getMSR_Power_Limit details from TAT
# parameter   : tc_id,input,script_id,log_level and tbd
# Return      : True/False
################################################################################


def getMSR_Power_Limit(device_input,tc_id,script_id,log_level ="ALL",tbd="None"):
    try:
        
        os.chdir(lib_constants.SCRIPTDIR)
        tat_dir = utils.ReadConfig("TAT_TOOL", "installedpath")
        tat_cli_exe = utils.ReadConfig("TAT_TOOL", "tat_cli")
        for item in [tat_dir, tat_cli_exe]:
            if "Fail:" in item:
                library.write_log(lib_constants.LOG_INFO, "INFO : CONFIG "
                    "entry missing for tat_dir/tat_dir/ pstate_ws/tat_cli_"
                "exe", tc_id, script_id, "None", "None", log_level, tbd)
                return False
        if os.path.exists(tat_dir):                                             #check for TAT installation
            library.write_log(lib_constants.LOG_INFO, "INFO: TAT tool is "
            "already Installed.", tc_id, script_id, "None", "None",
                              log_level, tbd)
            try:
                installedpath = utils.ReadConfig('TAT_TOOL', 'installedpath' )
                installedpath_target = utils.ReadConfig('TAT_TOOL',
                                                        'installedpath_target' )
                for item in [installedpath,installedpath_target]:
                    if "FAIL:" in item:
                        library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG ENTRY"
                        " for Installedpath or Installedpath_target of TAT is missing"
                        , tc_id,script_id, "None", "None", log_level, tbd)
                    else:
                        pass
                host_service_start_cmd = "net start Intel(R)TATHostService"
                target_service_start_cmd = "net start Intel(R)TATTargetService"
                os.chdir(installedpath)
                host_op = os.system(host_service_start_cmd)
                os.chdir(installedpath_target)
                target_op = os.system(target_service_start_cmd)
                library.write_log(lib_constants.LOG_INFO,
                "INFO: TAT Target service & TAT Host service has started"
                    " successfully",tc_id, script_id, "None",
                                  "None", log_level, tbd)
                pass
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR,
                "ERROR:Failed to start TAT Target service & TAT Host"
                " service due to %s"%(e),tc_id, script_id,
                                  "None","None", log_level, tbd)
                return False
        else:                                                                   #Tat tool not installed , installing now
            install = lib_tat_tool_installation.tat_tool_installation\
                    (tc_id, script_id, log_level,tbd)
            if install:                                                         #checking for tat tool installation
                library.write_log(lib_constants.LOG_INFO, "INFO: TAT tool "
              "Installed", tc_id, script_id, "None", "None",
                                log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: TAT tool "
              "not Installed", tc_id, script_id, "None", "None",
                                  log_level,tbd)
                return False
        os.chdir(tat_dir)
        #print tat_dir
        tat_cmd = tat_cli_exe + " -AL -t=30"                                #store the command to run in a variable
        
        for file in glob.glob("TATMonitor*.csv"):                           #search for monitor file
            os.remove(file)
        #print tat_cmd
        process = subprocess.Popen(tat_cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        time.sleep(70)
        file = glob.glob("TATMonitor*.csv")                                 #search for the out put log file
        file_name = file[0]                                                 #store the name of the file
        os.chdir(lib_constants.SCRIPTDIR)                                   #change to scriptdir
        file_name_script = script_id.replace(".py",".csv")

        if file == []:                                                      #if the log file is empty
            os.chdir(lib_constants.SCRIPTDIR)
            library.write_log(lib_constants.LOG_WARNING, "Warning: "
                "Generated log file from Tat tool is empty",
                    tc_id, script_id, "None", "None", log_level, tbd)
            return False                                                    # fail case
        else:
            for file in glob.glob(file_name_script):
                os.remove(file)                                             #remove old csv file if present
            shutil.copy(tat_dir + "\\" + file_name, lib_constants.SCRIPTDIR)#copy the file from tat dir to scriptdir
            os.rename(lib_constants.SCRIPTDIR+"\\" + file_name,
                      file_name_script)                                     #rename the file to standard name

            for file in glob.glob("TATMonitor*.csv"):
                os.remove(file)                                         #remove the copied file


            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully  "
                "generated log file from Tat tool", tc_id,
                             script_id, "TAT","None", log_level, tbd)
            return lib_constants.SCRIPTDIR + "\\" + file_name_script
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to run "
            "TAT process to %s."%e, tc_id, script_id, "None",
                          "None", log_level,tbd)
        return False

################################################################################
        
################################################################################
# function    : fetchcsv
# description : Fetch the requied value from csv
# parameter   : tc_id,input,script_id,log_level and tbd
# Return      : True/False
################################################################################

def fetchcsv(csv_file,device_input,tc_id,script_id,log_level ="ALL",tbd="None"):

    try:
        os.chdir(lib_constants.SCRIPTDIR)
        columns = defaultdict(list)                                             # each value in each column is appended to a list
        
        with open(csv_file) as f:
            reader = csv.DictReader(f)                                          # read rows into a dictionary format
            for row in reader:                                                  # read a row as {column1: value1, column2: value2,...}
                for (k,v) in list(row.items()):                                       # go over each column name and value
                    columns[k.lower()].append(v.lower())                                        # append the value into the appropriate list
                                                                                # based on column name k

        col_Name = 'turbo parameters-'+ device_input.lower() +'(seconds)'
        l_Val = columns[col_Name]
        if eval(l_Val[1]) >= 0:
            library.write_log(lib_constants.LOG_INFO, "INFO: MSR PowerLimit_Time "
                                                      "generated from"
                                                      "Tat tool", tc_id,
                              script_id, "TAT","None", log_level, tbd)
            return eval(l_Val[1])

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Fail to fetch"
                                                      " MSR POWerLimit Time from "
                                                      "Tat tool", tc_id,script_id,
                              "TAT","None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Unable to fetch "
            "requested value due to %s."%e, tc_id, script_id, "None",
                          "None", log_level,tbd)
        return False


    
