__author__ = 'AsharanX\parunacx'
################################################################################
# Function    : install_solar()
# Description : Installs the solar tool
# param       : TC_id,script_id,loglevel,tbd
# return      : True if tool installation is success else returns False
############################## General Imports #################################
import os
import sys
import time
import wmi
############################## Local Imports ###################################
import subprocess
import library
import lib_constants
import utils
################################################################################


def install_solar(tc_id=None,script_id=None,log_level="ALL",tbd=None):          # function for installing the solar tool
    solarpath = utils.ReadConfig("solar_tool","solar_path")
    if os.path.exists(solarpath):                                               # checks if the solar tool path is present
        c = wmi.WMI()
        result = c.query("Select * from Win32_Product where Caption "
        "like '%Microsoft Visual C++%'")                                        # query for getting the name of the tool
        if result:
             utils.filechangedir(lib_constants.TOOLPATH)                        # if the result is true from the above query it will change the directory to the tool environment path
                                                                                #install C++ distributable
             command1 = "vcredist_x86.exe /repair /quiet /norestart"
             command2 = "vcredist_x64.exe /repair /quiet /norestart"
             subprocess.Popen(command1, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE).communicate()                           # subprocess call to install the tool environment in 32bit os architecture
             subprocess.Popen(command2, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE).communicate()                           # subprocess call to install the tool environment in 32bit os architecture
             library.write_log(lib_constants.LOG_INFO,"INFO: System environment"
             " set for solar tool","Solar_tool","None",log_level,tbd)
             return True
             pass
        elif os.path.exists(lib_constants.TOOLPATH + "\System "
             "Environment Setup"):
             utils.filechangedir(lib_constants.TOOLPATH + "\System "
             "Environment Setup")                                               #install C++ distributable
             command1 = "vcredist_x86.exe /install /quiet /norestart"
             command2 = "vcredist_x64.exe /install /quiet /norestart"
             subprocess.Popen(command1, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE).communicate()
             subprocess.Popen(command2, stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE).communicate()                           # installs(elif condition) because the result query may return True and other value which is dynamic
             library.write_log(lib_constants.LOG_INFO,"INFO: System environment"
             " set for solar tool","Solar_tool","None",log_level,tbd)
             return True
        else:
             library.write_log(lib_constants.LOG_FAIL,"FAIL: System "
            "Environment Setup is not available in this SUT",tc_id,script_id,
                               "Solar_tool","None",log_level,tbd)
             return False
    else:
         library.write_log(lib_constants.LOG_WARNING,"WARNING: Solar tool is "
         "not available in this SUT","Solar_tool","None",log_level,tbd)
         return False


################################################################################
# Function    : get_solar_cpuid
# Description : Reads the CPU Ids for the required Data register
# param       : eaxvalue ,ecxvalue ,reg,TC_id,script_id,loglevel,tbd
# return      : returns the binary value of EAX/EBX/ECX
################################################################################


def get_solar_cpuid(eaxvalue ,ecxvalue ,reg,tc_id,script_id,
    log_level = "ALL",tbd ="None"):
    try:
        solar_path = utils.ReadConfig("SOLAR_TOOL","solar_path")
        os.chdir(solar_path)

        installation = install_solar(tc_id=None,script_id=None,log_level="ALL",
                                     tbd=None)

        if installation is True:
            os.chdir(solar_path)
            command = "Solar.exe /cpuid" + " " + eaxvalue + " " + ecxvalue +\
                      " > result.txt"                                           #command to get cpuid from solar tool

            hexval = utils.execute_with_command(command, tc_id, script_id,
                                                lib_constants.STR_NONE,
                                                shell_status=True)

        else:
            library.write_log(lib_constants.LOG_ERROR,"Installation of required"
                                                      " files is not successful",
                              tbd="None")

        os.chdir(solar_path)                                                    #changing directory to toolpath
        with open("result.txt", 'r') as f:
            fr = f.readlines()
            if "ECX" in fr[-1] and reg == "ECX":
                value = fr[-1].split(';')[2].split('=')[1].strip()
            if "EAX" in fr[-1] and reg == "EAX":
                value = fr[-1].split(';')[0].split('=')[1].strip()
            if "EBX" in fr[-1] and reg == "EBX":
                value = fr[-1].split(';')[2].split('=')[1].strip()
            if "EDX" in fr[-1] and reg == "EDX":
                value = fr[-1].split(';')[2].split('=')[1].strip()

            thelen = len(value)*4                                              # returns the hex value
            binval = bin(int(value, 16))[2:].zfill(thelen)                      # converts the hexa value to binary value
            library.write_log(lib_constants.LOG_INFO,"INFO : The value of %s "
            "is %s" %(reg,binval),tc_id,script_id,"Solar_tool","None",
            log_level,tbd)
            binval  = str(binval) + "'b"
            return binval                                                       # returns the binary value of the data register EAX,EBX and ECX
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR : due to %s"%e,
        tc_id,script_id,"Solar_tool","None",log_level,tbd)
        return  False
################################################################################
