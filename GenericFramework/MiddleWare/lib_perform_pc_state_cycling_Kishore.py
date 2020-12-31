__author__ = 'bchowdhx/kapilshx'
############################General Python Imports##############################
import utils
import os
import subprocess
import time
import glob
import xml.etree.ElementTree as ET
import shutil

############################Local Python Imports################################
import lib_constants
import library
import lib_tat_tool_installation
################################################################################
# Function Name : px_cycling
# Parameters    : original string, test_case_id, script_id, loglevel, tbd
# Functionality : This code perform pstate cycling
# Return Value :  True/False
################################################################################


def px_cycling(ostr,test_case_id, script_id, loglevel="ALL", tbd="None"):

    try:
        change_delay = 0
        ostr = ostr.upper()
        token = ostr.split()                                                    #convert to list
        time_to_run = int(token[4])                                             #extract the time to run from token
        perc = (token[7])                                                       #extract load percentage from token
        perc = perc[:-1]                                                        #remove the % sign from percentage
        perc = int(perc)                                                        #convert to integer

        if percentage_calibration(perc, test_case_id, script_id, loglevel, tbd):#library call to check the percentage
            pass                                                                #continue
        else:
            return False

        dir = utils.ReadConfig("TAT_TOOL","installedpath")                      #read installed path of the tat tool from the config file
        pstate_ws = utils.ReadConfig("TAT_TOOL","pstate_workspace")             #get the location of workspace file from the config file
        cycling_script = utils.ReadConfig("TAT_TOOL","pstate_cycling_script")   #read the cycling script from the config file
        for item in [dir, pstate_ws, cycling_script]:
            if "FAIL:" in item:
                library.write_log(lib_constants.LOG_INFO, "INFO : Config entry "
            "for dir or pstats_ws or cycling_script is missing", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
                return False                                                    #if any of the config entry is missing return false
        else:
            pass

        if os.path.exists(dir):
            library.write_log(lib_constants.LOG_INFO, "INFO : TAT is already"
            " Installed", test_case_id, script_id, "None", "None", loglevel,
                                                                            tbd)#check for TAT installation
            try:
                installedpath = utils.ReadConfig('TAT_TOOL', 'installedpath' )
                installedpath_target = utils.ReadConfig('TAT_TOOL',
                                                        'installedpath_target' )
                for item in [installedpath,installedpath_target]:
                    if "FAIL:" in item:
                        library.write_log(lib_constants.LOG_INFO, "INFO: CONFIG ENTRY"
                        " for Installedpath or Installedpath_target of TAT is missing"
                        , test_case_id,script_id, "None", "None", loglevel, tbd)
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
                    " successfully",test_case_id, script_id, "None",
                                  "None", loglevel, tbd)
                pass
            except Exception as e:
                os.chdir(lib_constants.SCRIPTDIR)
                library.write_log(lib_constants.LOG_ERROR,
                "ERROR:Failed to start TAT Target service & TAT Host"
                " service due to %s"%(e),test_case_id, script_id,
                                  "None","None", loglevel, tbd)
                return False
        else:
            install = lib_tat_tool_installation.tat_tool_installation\
                    (test_case_id, script_id, loglevel,tbd)
            if install:
                pass
            else:
                return False

        tree = ET.parse(cycling_script)                                         #parse the cycling script
        pstate_script = lib_constants.SCRIPTDIR + "\\pstate_cycling_updated.xml"#store the name of the new script to run with edited settings
        root = tree.getroot()                                                   #get the root of the xml structure
        for i in range(1,10):                                                   #iterate through the root for 10 times
            if root[i][1].text == "StartWorkLoad":
                root[i][5].text = str(perc)                                     #append the required percentage to the file
            if root[i][4].text == "Time to run":
                root[i][5].text = str(time_to_run/lib_constants.SHORT_TIME) + \
                                                                        " Min"  #append the required time to run to the file
                change_delay = 1
            if root[i][1].text == "Delay" and change_delay == 1:
                root[i][4].text=str(((int(time_to_run)*
                lib_constants.THOUSAND))+(5*lib_constants.THOUSAND))                   #put delay and append to file
                change_delay = 0
        tree.write(pstate_script)                                               #write the updated script to the new script
        toolexe = dir + "\ThermalAnalysisToolCmd.exe"                           #store the toolexe location in a variable

        cmd = toolexe + " -AL -w=" + pstate_ws + " -s=" + pstate_script + \
              " -t=" +str(time_to_run)                                          #store the command to run in a variable which will run the tat tool
        os.chdir(dir)                                                           #change to tat installed directory
        for file in glob.glob("TATMonitor*.csv"):                               #look for Tatmonitor named file
           os.remove(file)                                                      #remove the file if its present
        subprocess.Popen(cmd)                                                   #run the tat command
        time.sleep(time_to_run)                                                 #wait for the given time
        time.sleep(lib_constants.FIVE_SECONDS)
        file = glob.glob("TATMonitor*.csv")
        file = file[0]                                                          #store the name of the tat file in a variable file as glob returns list
        tat_kill_cmd = r"TASKKILL /F /IM ThermalAnalysisToolCmd.exe /T"
        os.system(tat_kill_cmd)                                                 #run the command to kill tat process
        os.chdir(lib_constants.SCRIPTDIR)                                       #change to scriptdir
        file_name = script_id.replace(".py","")
        for tat in glob.glob(file_name + ".csv"):                               #look for the file ending with TAT_LOG.csv
           os.remove(tat)                                                       #remove the file if present
        if file==[]:                                                            #check for the file generate from tat command is empty or not
            library.write_log(lib_constants.LOG_INFO, "INFO : Not able to "
                "complete %s percentage Workload for %s sec duration."
                        %(str(perc), str(time_to_run)), test_case_id, script_id)

            return False                                                        #if empty return false
        else :
            pos = lib_constants.SCRIPTDIR

            shutil.copy(dir + "\\" + file, pos)                                 #copy the file from tat dir to scriptdir

            os.rename(lib_constants.SCRIPTDIR+"\\"+file, file_name +
                                                               ".csv")          #rename the file to standard name

            utils.write_to_Resultfile(lib_constants.SCRIPTDIR + "\\" +
                                    file_name + ".csv", script_id)              #write to result file the location of the file
            library.write_log(lib_constants.LOG_INFO,"INFO : %s percentage "
    "Workload for %s sec duration is completed." %(str(perc), str(time_to_run)),
                    test_case_id, script_id, "None", "None", loglevel, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR :Exception %s "%e,
                   test_case_id, script_id, "None", "None", loglevel, tbd)
        return False

################################################################################
# Function Name : applying_workload
# Parameters    : ostr, testcase id, script id, loglevel, tbd
# Functionality : This code will apply workload on the CPU
# Return Value  : True/False
################################################################################


def applying_workload(ostr, test_case_id, script_id, loglevel="ALL",
                                                                    tbd="None"):

    token = ostr.split()                                                        #convert to list from string
    duration = str(int(token[4]))                                               #extract duration from the syntax
    perc = (token[7])                                                           #extract the percentage of workload to apply from the syntax

    perc = perc[:-1]                                                            #remove the percentage symbol
    perc = int(perc)                                                            #convert to integer
    if percentage_calibration(perc, test_case_id, script_id, loglevel, tbd):    #library call to check the percentage
        pass                                                                    #continue
    else:
        return False

    if 0 == perc:
        result = cstate_monitor(duration, perc, test_case_id, script_id,
                                loglevel, tbd)
        if result:
            return True
        else:
            return False
    else:
        pass
    try:
        dir = utils.ReadConfig("TAT_TOOL","installedpath")                      #read installed path of the tat tool from the config file
        pstate_ws = utils.ReadConfig("TAT_TOOL","pstate_workspace")             #get the location of workspace file from the config file

        for items in [dir,pstate_ws]:
            if "Fail:" in items:
                library.write_log(lib_constants.LOG_INFO, "INFO : CONFIG entry "
                " missing for dir and pstate_ws", test_case_id, script_id,
                                                "None", "None", loglevel, tbd)
                return False                                                    #return False if config entries
            else:
                pass

        if os.path.exists(dir):
            library.write_log(lib_constants.LOG_INFO, "INFO : TAT is already"
            " Installed", test_case_id, script_id, "None", "None", loglevel,
                                                                            tbd)#check for TAT installation
        else:
            install = lib_tat_tool_installation.tat_tool_installation\
                    (test_case_id, script_id, loglevel,tbd)
            if install:
                pass
            else:
                return False

        tat = r'<?xml version="1.0"?>' + "\n"                                   #create the workload xml with input percentage and time
        tat_script = tat + r"<TatScript><Version>1.0</Version><CMD>" \
                               r"<ComponentName/><Command>StartLog</Command>" \
                               r"<NodeCount>0</NodeCount><CommandName/>" \
                               r"<Value>0</Value></CMD><CMD><ComponentName>" \
                               r"CPU Component</ComponentName><Command>" \
                               r"StartWorkLoad</Command><NodeCount>1" \
                               r"</NodeCount><NodeArg>CPU Power</NodeArg>" \
                               r"<CommandName>CPU-All</CommandName><Value>%s" \
                               r"</Value></CMD><CMD><ComponentName/><Command>" \
                               r"Delay</Command><NodeCount>0</NodeCount>" \
                               r"<CommandName/><Value>%s</Value></CMD><CMD>" \
                               r"<ComponentName>CPU Component" \
                               r"</ComponentName><Command>StopWorkLoad" \
                               r"</Command><NodeCount>1</NodeCount><NodeArg>" \
                               r"CPU Power</NodeArg><CommandName>CPU-All" \
                               r"</CommandName></CMD><CMD><ComponentName/>" \
                               r"<Command>StopLog</Command><NodeCount>0" \
                               r"</NodeCount><CommandName/><Value>0</Value>" \
                               r"</CMD></TatScript>" %(perc, duration)


        os.chdir(dir)
        with open("TatScript.xml", "w") as handle:                              #write the appended script as Tatscript.xml in Tat installed directory
            handle.write(tat_script)
        toolexe = dir + "\ThermalAnalysisToolCmd.exe"                           #store the name of the Tool in toolexe variable
        os.chdir(dir)
        tat_cmd = toolexe + " -AL" + " -s=TatScript.xml" + " -t=%s" \
                                %duration + " -w=" + pstate_ws                  #store the command to run in a variable
        subprocess.Popen(tat_cmd)                                               #run the command

        if cstate_monitor(duration, perc, test_case_id, script_id, loglevel,
                                                                     tbd):      #library call to monitor cstate while workload is applied
            return True
        else:
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_INFO, "INFO : Unable to Execute "
                                    "due to %s."%e, test_case_id, script_id)
        return False


################################################################################
# Function Name : cstate_monitor
# Parameters    : time, percentage, testcase id, script id , loglevel, tbd
# Functionality : Generate log from socwatch
# Return Value :  True/False
################################################################################


def cstate_monitor(time_to, perc, test_case_id, script_id, loglevel="ALL",
                   tbd="None"):
    try:
        script_dir = lib_constants.SCRIPTDIR
        dir = utils.ReadConfig("SOC_WATCH","tooldir")

        if "FAIL:" in dir:
            library.write_log(lib_constants.LOG_INFO, "Config entry for soc "
                 "watch tooldir is not there", test_case_id, script_id,
                              loglevel, tbd)                                    #check if config entry for socwatch is given
            return False
        else:
            pass

        os.chdir(dir)
        file = glob.glob("SOCWatchOutput*.csv")                                 #search for the out put log file

        if file == []:
            pass
        else:
            file_name = file[0]
            if os.path.exists(dir+"\\"+file_name):
                os.remove(file_name)
        time_to_run = int(time_to)                                              #convert  time_to_run to integer
        cmd_to_run = "socwatch.exe -f cpu-cstate -t " + str(time_to_run)        #run the command for socwatch after appending with new time

        for file in glob.glob("monitor*.csv"):                                  #search for monitor file
            os.remove(file)                                                     #if exist remove
        output, err = subprocess.Popen(cmd_to_run, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE).communicate()    #start the process

                                                             #store the name of the file
        file = glob.glob("SOCWatchOutput*.csv")                                 #search for the out put log file
        if file == []:
            return False
        else:
            file_name = file[0]
        os.chdir(script_dir)                                                    #change to scriptdir
        file_name_script = script_id.replace(".py","")
        for var_name  in glob.glob(file_name_script+"_SOC_LOG.csv"):            #check for existing soc_loc.csv file in scriptdir
            os.remove(var_name)                                                 #remove if found
        if file == []:                                                          #if the log file is empty
          pass                                                          # fail case
        else :
            shutil.copy(dir + "\\" + file_name, script_dir)                     #copy the file from tat dir to scriptdir

            os.rename(lib_constants.SCRIPTDIR+"\\"+file_name, file_name_script
                                                             + "_SOC_LOG.csv")  #rename the file to standard name

            utils.write_to_Resultfile(lib_constants.SCRIPTDIR + "\\" +
                                file_name_script + "_SOC_LOG.csv", script_id)   #write to result file the location of the log path
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully  "
                "generated log file from socwatch tool", test_case_id,
                             script_id, loglevel, tbd)
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR :Exception %s "%e,
                   test_case_id, script_id, "None", "None", loglevel, tbd)
        return False


################################################################################
# Function Name : percentage_calibration
# Parameters    : percentage, testcase id, script id, loglevel, tbd
# Functionality : This code will check the percentage of load
# Return Value  : True/False
################################################################################


def percentage_calibration(perc, test_case_id, script_id, loglevel="ALL",
                   tbd="None"):

    counter = False
    for item in lib_constants.C_STATE_PERC:
        if item == perc:
            counter = True
            break
        else:
            counter = False
    if counter:
        library.write_log(lib_constants.LOG_INFO, "INFO :Current percentage "
            "to be applied is %s percentage"%str(perc), test_case_id,
                          script_id, "None", "None", loglevel, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO : Load percentage"
        " should be either 0,50,60,70,80,90 or 100 percent", test_case_id,
                      script_id, "None", "None", loglevel, tbd)
        return False                                                            #return False if value is not proper
