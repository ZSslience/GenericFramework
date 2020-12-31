__author__ = 'karthic1'

#############################Global Imports ####################################
import os
import datetime
import time
import xml.etree.ElementTree as ET
#########################Local Imports #########################################
import lib_epcs
import utils
import lib_tool_installation
import library
import lib_constants

################################################################################
# Function name   : get_val
# Description     : retrieves the value from syscope log and calculates time
#                   difference for some params
# Parameters      : name,path,field,flag,boot_type,test_case_id,
#                   scriptid,boot_type, destination, loglevel
# Returns         : returns true or false
##############################general imports###################################


def get_val(name,path,field,flag,
            test_case_id,script_id,boot_type
            ,destination,loglevel= "ALL",tbd = "None"):
  try:
    count_log = 0
    value = []
    tree = ET.parse(path)                                                       #Opens the xml, searches from the root.
    root = tree.getroot()
    root1 =root.findall(name)
    for items in root1:
     out = items.attrib
     out = out["Key"],out["Value"]
     for n in field :
      if n in out:
       tStamp = items.get('Value')
       tStamp = tStamp[:13]
       count_log += 1
       value.append(datetime.datetime.fromtimestamp(int(tStamp)/1e3))

      else:
            pass
    if flag :
     diff = (value[1]-value[0]).total_seconds()                                #converting to seconds
     value[0]=diff
    else :
     value[0].strftime('%H:%M:%S')
    if count_log > 0:
         library.write_log(lib_constants.LOG_INFO,"INFO: "\
                                  +boot_type+" Time  is %s seconds"%((value[0]))
                ,test_case_id,script_id,
                "None","None", loglevel="ALL", tbd = "None")                  #opens the log file to write the retrieved time
         return value
    else:
        library.write_log(lib_constants.LOG_INFO,"INFO: Unable to get "\
                                  +boot_type+" time."
                ,test_case_id,script_id,"None","None",
                loglevel="ALL", tbd = "None")                                 #opens the log to write that the time was not retrived
        return False
  except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "change_bios_setting function due to "+str(e),test_case_id
                          ,script_id,"None","None"
                          , loglevel="ALL", tbd = "None")




################################################################################
# Function name   : change_bios_setting
# Description     : sets boot mode to fast boot
# Parameters      : boot_type,test_case_id,scriptid,boot_type, destination, loglevel
# Returns         : returns true or false
# Dependent Function: updatebios()
##############################general imports###################################



def change_bios_setting(boot_type,test_case_id,script_id,
                        loglevel="ALL",tbd = "None"):
 try:
   if "FASTBOOT" == boot_type :
       boot = "FAST BOOT"
       status = lib_constants.ENABLE
   elif "FULLBOOT" == boot_type:
       boot = "FAST BOOT"
       status = lib_constants.DISABLE
   elif "BIOS COLD BOOT" == boot_type:
       boot = "FAST BOOT"
       status = lib_constants.DISABLE
   elif "BIOS S3 RESUME" == boot_type:
       boot = "FAST BOOT"
       status = lib_constants.DISABLE
   elif "BIOS S3 SUSPEND" == boot_type:
       boot = "FAST BOOT"
       status = lib_constants.DISABLE

   specific="Form: Boot Configuration Menu"
   value = lib_epcs.updatebios(boot,status,
               test_case_id,script_id,specific,loglevel,tbd = "None")   #Update bios changes the boot mode to full boot or fast boot
   return value
 except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "change_bios_setting function due to "+str(e),test_case_id
                          ,script_id,"None","None"
                          , loglevel="ALL", tbd = "None")



################################################################################
# Function name   : verify_boot_time_till_destination
# Description     : reads syscope.xml and gets fpdt details
# Parameters      : test_case_id,scriptid,boot_type, destination, loglevel
# Returns         : returns true or false
# Dependent Function:install_Syscope(test_case_id,script_id,loglevel,tbd = "None")
#                    execute_syscope()
################################################################################





def verify_boot_time_till_destination(test_case_id,script_id,boot_type
                                      ,destination,loglevel,tbd = "None"):


    try:
        if not (("BIOS FIRST BOOT" == boot_type.strip())):
            lib_tool_installation.install_Syscope(test_case_id,script_id
                                                  ,loglevel,tbd = "None")
            sysscopepath = utils.ReadConfig("Systemscope","Tooldir")             #reads the directory from config
            #result = lib_tool_installation.execute_syscope()                     #creates sysscope log
            result = True
            if result:
                library.write_log(lib_constants.LOG_INFO
                ,"Log has been generated By System Scope tool"
                ,test_case_id,script_id,"None","None", loglevel="ALL", tbd = "None")
            else:
                library.write_log(lib_constants.LOG_ERROR
                ,"Log has not been generated By System Scope tool"
                ,test_case_id,script_id,"None","None", loglevel="ALL", tbd = "None")
        else:
            pass

        if ( (("FASTBOOT" == boot_type.strip())
              or("FULLBOOT" == boot_type.strip() )
              or("BIOS COLD BOOT" == boot_type.strip()))
              and( "OS" == destination.strip()) ):
            os.chdir(sysscopepath)
            name = ".//*[@Name='FPDTLog']/*"
            path = "syscope.xml"
            field = "ExitBootServiceExit","ExitBootServiceEntry"
            flag = True
            get_val(name,path,field,flag,test_case_id,script_id,boot_type
                                      ,destination,
                                      loglevel="ALL",tbd = "None")             # reads the code from syscope and finds the difference


        elif ( (("BIOS FIRST BOOT" == boot_type.strip()))
             and (destination.strip() == "OS") ):
            off = script_id.split(".")[0]                                       # steps to extract the step number from script_id
            off = off[-1:]
            step = int(off) - 1
            path = utils.read_from_Resultfile(step)
            library.write_log(lib_constants.LOG_INFO
                ,"path obtained from result.ini file for syscope log = %s"%(path)
                ,test_case_id,script_id,"None","None"
                , loglevel="ALL", tbd = "None")
            name = ".//*[@Name='FPDTLog']/*"
            path = "syscope.xml"
            field = "ExitBootServiceExit","ExitBootServiceEntry"
            flag = True
            get_val(name,path,field,flag,test_case_id,script_id,boot_type
                                      ,destination,loglevel="ALL",tbd = "None")# reads the code from syscope and finds the difference

        elif ( ("BIOS S3 RESUME" == boot_type.strip())                          # Condition for s3 resume
             and (destination.strip() == "OS") ):
            os.chdir(sysscopepath)
            count_log = 0
            value = ""
            name = ".//*[@Name='(0): BASIC_S3_RESUME_PERF_TYPE']/*"
            path = "syscope.xml"
            field = "FullResume",
            flag = False
            get_val(name,path,field,flag,test_case_id,script_id,boot_type
                                      ,destination,loglevel="ALL",tbd = "None")# reads the code from syscope and finds the difference

        elif ( (("BIOS S3 SUSPEND" == boot_type.strip()))                       #condition for s3 suspend
             and (destination.strip() == "OS") ):
            os.chdir(sysscopepath)
            count_log = 0
            value = ""
            name = ".//*[@Name='(1): BASIC_S3_SUSPEND_PERF_TYPE']/*"
            path = "syscope.xml"
            field = "SuspendStart",
            flag = False
            get_val(name,path,field,flag,test_case_id,script_id,boot_type
                                      ,destination,loglevel="ALL",tbd = "None") # reads the code from syscope and finds the difference
        else:
            library.write_log(lib_constants.LOG_FAIL
                              ,"FAIL: Invalid Input Token."
            ,test_case_id,script_id,"None","None", loglevel="ALL", tbd = "None")
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR,"ERROR: Exception in "
        "verify_boot_time_till_destination function due to "+str(e),test_case_id
                          ,script_id,"None","None"
                          , loglevel="ALL", tbd = "None")
        return False
