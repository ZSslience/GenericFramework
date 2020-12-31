##########################General python Imports################################
import os
########################Local python Imports####################################
import library
import lib_constants
################################################################################

Epcsdir = lib_constants.EPCSTOOLPATH
os.chdir(Epcsdir)
################################################################################
# Function    : get_bootorder()
# Parameter   : test_case_id is test case number, script_id is script number
# Description :	This function gives boot.txt in which booting device list is
#                  available.
# Return      :	returns true if txt generated or returns False
################################################################################

def get_bootorder(test_case_id,script_id,loglevel="ALL",tbd = None):

    os.chdir(Epcsdir)                                                           #change to EPCS tool directory
    command = "epcsutilwin.exe bootorder get > boot.txt"
    flag = os.system(command)                                                   #run the command in command prompt
    if 0 == flag:
        os.chdir(lib_constants.SCRIPTDIR)                                       #change back to Script directory and write in log if successful
        library.write_log(lib_constants.LOG_INFO,"Pass : Booting device is "
                                                 "listed.",
                          test_case_id, script_id)
        return True                                                             #return True
    else:
        os.chdir(lib_constants.SCRIPTDIR)                                       #change back to script directory and write in log if not successful
        library.write_log(lib_constants.LOG_INFO,"Fail : Not able to create"
                                                 " Booting device list",
                          test_case_id, script_id)
        return False                                                            #return False


################################################################################
# Function    : get_current_bootorder()
# Parameter   : None
# Description :	This function gives list of current bootorder
# Return      :	returns list of current bootorder
################################################################################


def get_current_bootorder(loglevel="ALL", tbd=None):

    global bootorder
    os.chdir(Epcsdir)                                                           #change to EPCS tools directory
    with open('boot.txt', 'r') as log:                                          #open boot.txt in read mode as log
        for line in log:                                                        #iterate through the log
            if "The Current Boot Order" in line:                                #check for string "The current Boot Order"
                bootorder = line.split("-")[1].strip()                          #save the boot order
    order=[]
    for i in range(0, len(bootorder)-1):
        if 0 == i % 2:
            order.append(bootorder[i:i+2])
    return order                                                                #return list after storing the orders of the connected devices


################################################################################
# Function    : get_selection(BootOrder)# NOt Useful - its in support
#                       for other function
# Parameter   :	BootOrder = Name of the device which is to be updated as first
#                   boot device(Name must be same as in BIOS)
# Description :	This function makes makes the selection of first boot device
# Return      :	returns selected device ID
################################################################################


def get_selection(BootOrder, loglevel="ALL", tbd=None):

    global selection
    os.chdir(Epcsdir)                                                           #change directory to EPCS installed directory

    with open('boot.txt','r') as log:                                           #open boot.txt file in read mode as log
        for line in log:                                                        #iterate through the lines
            if BootOrder in line:                                               #search for bootorder in line
                selection=line.split()[0]                                       #save the line and split the line, then save the 0th element of the list in the selection variable
    return selection


################################################################################
# Function      : bootorder()# NOt Useful - its in support for other function
# Parameter     : N/A
# Description   : gets current bootorder
# Return        : bootorder
################################################################################


def bootorder(loglevel="ALL", tbd=None):

    bootorder = get_current_bootorder()                                         #call the get_current_bootorder function and store in bootorder
    selected = selection                                                        #store the current selection in selected variable
    count=-1
    for i in bootorder:                                                         #iterate through the bootorder
        count += count                                                          #increase the count at each iteration
        if selected == i:                                                       #if selected matches with iterating variable
            temp = bootorder[0]                                                 #store bootorder number in temp variable
            bootorder[0] = selected                                             #exchange the bootorder of selected with current
            bootorder[count] = temp
    return bootorder                                                            #return the bootorder as list


################################################################################
# Function      : bootorder()# NOt Useful - its in support for other function
# Returns       : string
# Description   : Hyphen separated
###############################################################################


def hyphenseparated(loglevel="ALL", tbd=None):

    hypen = bootorder()                                                         #calls bootorder and stores the result in hypen variable
    count = len(hypen)                                                          #store the length of the bootorder in count
    cnt = 0
    strng = ""
    for order in hypen:                                                         #iterate through the bootorder
        cnt = cnt+1
        if cnt<count:                                                           # operations to handle the hyphen in the string
            strng = strng + hypen[cnt-1] + '-'
        else:
            strng = strng + hypen[cnt-1]
    return strng


################################################################################
# Function      : 	set_bootorder() # to use this function first use
#                   get_selection(BootOrder)
# Description   :	This function sets the selected device as a first boot
#                   option in BIOS
# Return        :	returns list of current bootorder
# Parameter     :   test_case_id is test case number, script_id is script number
################################################################################


def set_bootorder(test_case_id,script_id,loglevel="ALL", tbd=None):

    os.chdir(Epcsdir)                                                           #change to EPCS tool installed location
    efiorder = hyphenseparated()                                                #calls hyphenseparated function
    command = "epcsutilwin.exe bootorder set " + efiorder

    if os.system(command):                                                      #run the command in command prompt
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_INFO,"Fail : selected device is"
                    " not set to first boot device",test_case_id,script_id, "None",
                          "None",loglevel,str(tbd))                            #write to log as Fail if the operation fails
        return False
    else:
        os.chdir(lib_constants.SCRIPTDIR)
        library.write_log(lib_constants.LOG_INFO, "Pass : selected device is "
                "set to first boot device", test_case_id, script_id,
                          "None", "None", loglevel, str(tbd))                  #write to log as Pass if the operation passes
        return True
