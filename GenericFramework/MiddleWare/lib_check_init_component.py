__author__ = "singhd1x/kapilshx"

############################General Python Imports##############################
import os
import re
from xml.etree import ElementTree
import xml.etree.ElementTree as ET
############################Local Python Imports################################
import library
import lib_constants
import utils
import lib_tool_installation
################################################################################
# Function Name     : verify_init_component_time
# Parameters        : Component ( GOP/MRC)
#                     time ( time to check with the actual time)
#                     tc_id, script_id,loglevel, tbd
# Functionality     : Function to Check whether Component init time is less
#                     than given time
# Return Value      : GOP/MRC delta time if True
################################################################################

def check_init_component(component,time,step_value,tc_id,script_id,
                               log_level= "ALL",tbd = None):
    logfile = script_id.split(".")[0]
    log_path = lib_constants.SCRIPTDIR
    delta_value_table_path = log_path + r"\\" + logfile + \
                             "_delta_value.txt"
    search_value = {"mrcinit" : ["DeltaTime","GUID"],
                    "gopinit": ["DeltaTime","NameString"]}
    output = []

    try:
        if lib_tool_installation.install_Syscope(tc_id, script_id, log_level,
                                                 tbd):
            library.write_log(lib_constants.LOG_INFO, "INFO :SystemScope "
                                                      "is Installed", tc_id,
                              script_id, "system scope", "None", log_level,
                              tbd)                                              #installs the syscope tool
        else:
            library.write_log(lib_constants.LOG_INFO,
                "INFO : SystemScope tool fail to installed",
                tc_id,script_id, "system scope", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : " + str(e),
            tc_id, script_id, "system scope", "None", log_level,tbd)
        return False
    try:
        read_data = int(step_value)-1
        file_location = utils.read_from_Resultfile(read_data)
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR :Fail to read log file"
                "and get required file location "+str(e),tc_id, script_id,
                          "None","None",log_level,tbd )
        return False
    try:
        with open(file_location,
                  'rt')as xmlfile:                                              # open the system scope xml file
            tree = ElementTree.parse(xmlfile)                                   # get tree element
            sys_scope_root = tree.getroot()                                     # get root element
        for node in tree.iter('Module'):                                        # loop through the Module tags
            name = node.attrib.get('Name')                                      # get all the name mode values
            output.append(str(name))                                            # appending to output list
        if 'FPDT' in output:
            child_root = sys_scope_root.findall(
                ".//*[@Name='FPDT']/Group")                                     # find all the group tags values
            list_of_table_in_FPDT = []
            for item in child_root:
                all_tables_in_FPDT = item.attrib                                # get all the attribute of the tables
                for key, value in list(all_tables_in_FPDT.items()):                   # goop though each table attribute and store the value in list
                    list_of_table_in_FPDT.append(str(value))
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: FPDT table does "
                "not exist in generated xml log file", tc_id,script_id,
                              "system scope", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: " + str(e),
            tc_id, script_id, "system scope", "None", log_level,tbd)
        return False
    search_table = utils.ReadConfig("SEARCH_TABLE","table_name")
    if search_table.strip().upper() in list_of_table_in_FPDT:                   # checking for child table name in FPDT branch
        try:
            if os.path.exists(delta_value_table_path):
                os.remove(delta_value_table_path)                               # checks if older log file exists then removes the older logs
            tree = ET.parse(file_location)
            getroot = tree.getroot()                                            # get root node of the xml tree
            fpdt_content = getroot.findall(".//*[@Na"
                            "me='" + search_table.strip().upper() + "']/Item")  # search for the table name and get all the items of the table
            for expectedtable in fpdt_content:                                  # loop through matching table elements content
                table_content = expectedtable.attrib                            # find the attribute of the content
                for key, value in list(table_content.items()):                        # iterate through each of the attribute items
                    try:
                        if "GOP" == component.upper() :
                            with open(delta_value_table_path,
                                      "a+") as table:                           # opens the file and writes the value of table content
                                for keys in search_value["gopinit"]:
                                    if key == keys:
                                        table.write(key + "=" + value +"\n")
                        elif "MRC" == component.upper():
                            with open(delta_value_table_path,
                                      "a+") as table:                           # opens the file and writes the value of table content
                                for keys in search_value["mrcinit"]:
                                    if key == keys:
                                        table.write(key + "=" + value + "\n")
                        else:
                            pass
                    except Exception as e:
                        library.write_log(lib_constants.LOG_ERROR, "ERROR" +
                                          str(e),tc_id, script_id, "None",
                                          "None", log_level,tbd)
                        return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: " + str(e),
                      tc_id, script_id, log_level, tbd)
            return False
    total_init_time = 0
    if "GOP" == component.upper():
        pattern = re.compile("((?:GopDriver)((\w+)+)?)", re.I)
    elif "MRC" == component.upper():
        pattern = re.compile(lib_constants.APL_MRC, re.I)
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO: input syntax is "
            "incorrect",tc_id, script_id, "system scope", "None",log_level, tbd)
        return False
    with open(delta_value_table_path,"a+") as file:
        read_line = file.readlines()
    file.close()
    for (index_point,line) in enumerate(read_line):
        if re.search(pattern, line):
            init_value = ((read_line[index_point + 1]).split("=")[1])
            total_init_time += int(init_value)
    if total_init_time < int(time):
        library.write_log(lib_constants.LOG_INFO,"INFO: %s init completes in "
            "less than %d ms %d i.e. ms "%(component , int(time),total_init_time),
            tc_id, script_id, "system scope", "None",log_level, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO: %s init failed to "
            "completes in less than %d ms i.e. %d ms "
            %(component, int(time), total_init_time),
            tc_id, script_id, "system scope", "None",log_level, tbd)
        return False

