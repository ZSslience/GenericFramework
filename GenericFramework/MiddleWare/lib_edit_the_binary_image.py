__author__ = 'sharadth'
###########################General Python Imports##############################
import os
import binascii
import shutil
import subprocess
import time
############################Local Python Imports################################
import library
import lib_constants
import utils
################################################################################
# Function Name : extract_hex()
# Parameters    : Hexadecimal value
# Functionality : This code will convert Hexadecimal input in 0X format
# Return Value :  Hexadecimal value in the 0X format
################################################################################
def extract_hex(input_value):                                                   # function to extract valid hex value from the parameters
    if 'H' in input_value or 'h' in input_value:
        input_value = input_value.strip('h')
        input_value = input_value.strip('H')
        input_value = "0X"+input_value
        return input_value                                                      # returns parameter with'0x' embedded to input parameter
    else:
        input_value = input_value.upper()
        return input_value
################################################################################
# Function Name     : create_powershell_file()
# Parameters        : start_offset,end_offset,offset_size
# ,file_name,path,data,tc_id,
#                     script_id,log_level, tbd
# Functionality     : function to create powershell file
# Return Value      : Pass(if pass), False(if fail) and New edited file path
################################################################################
def create_powershell_file(start_offset_integer,new_bin_file_path,value,
                           offset_size_integer,tc_id,script_id,
                           log_level="ALL", tbd= None):                         # Creates powershell file with required commands to change the value of required file
    powershell_path= lib_constants.SCRIPTDIR + '\powershell.ps1'
    with open(powershell_path,'w') as powershell:                               # open new powershell file
        powershell.write('$bytes = [System.IO.File]::ReadAllBytes'              # read binary file using powershell
                        '("'+new_bin_file_path+'");\n')
        powershell.write("for ($i ="+str(start_offset_integer)+"; $i -le "      # loop for multiple changes in the file
            +str(start_offset_integer + offset_size_integer)+";$i++ )\n { \n")
        powershell.write('$bytes["$i"] = "'+str(value)+'"\n } \n')              # assign the value to be replaced
        powershell.write('[System.IO.File]::WriteAllBytes'                      # write back to the binary file
                                      '("'+new_bin_file_path+'", $bytes)')
        powershell.close()

    library.write_log(lib_constants.LOG_INFO,"INFO:Powershell script created"
                     "for binary image modification from start"
                     "offset: %d, offset_size: %d"
                      %(start_offset_integer, offset_size_integer),
                      tc_id,script_id,"None","None",log_level, tbd)

################################################################################
# Function Name     : edit_the_binary_image()
# Parameters        : start_offset,end_offset,offset_size
# ,file_name,path,data,tc_id,
#                     script_id,log_level, tbd
# Functionality     : function to get change binary image value
# Return Value      : Pass(if pass), False(if fail) and New edited file path
################################################################################
def execute_powershell(tc_id,script_id, log_level, tbd):
    power_shell_ter = lib_constants.POWERSHELL_PERMISSION                       # set the permission to run powershell
    subprocess.Popen(power_shell_ter, stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)                                           # start the subprocess of powershell
    library.write_log(lib_constants.LOG_INFO,"INFO : powershell.exe- "
                    "Execution Policy set for launching powershell",tc_id,
                    script_id, "None","None", log_level, tbd)
    time.sleep(lib_constants.FIVE)
    execute_file = "powershell.exe ./powershell.ps1"
    subprocess.Popen(execute_file, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)                                              # Execute using subprocess
    subprocess.Popen(power_shell_ter,close_fds=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)                            # close the subprocess
    time.sleep(lib_constants.TEN)
    library.write_log(lib_constants.LOG_INFO,"INFO : Powershell file executed"  # Log: powershell command executed successfully from the powershell file
                      "successfully",tc_id,script_id, "None","None", log_level,
                      tbd)
################################################################################
# Function Name     : verify_changes()
# Parameters        : new_bin_file_path,address_value,hex_value
# Functionality     : function to verify if changes were applied
#                     successfully or not
# Return Value      : True(if pass), False(if fail) and New edited file path
################################################################################
def verify_changes(new_bin_file_path,value,start_offset_integer,
                   offset_size_integer,tc_id,script_id,log_level,tbd):          # This function verifies whether the changes were implemented successfully or not
    with open(new_bin_file_path, 'rb') as bit_file_verify:                      # Open the new file
        address_value = value[2:]
        address_value = address_value*offset_size_integer
        address_value=address_value.lower()
        address = start_offset_integer
        bit_file_verify.seek(address)
        hex_value = binascii.hexlify(bit_file_verify.read(offset_size_integer)) # Returns hexadecimal representation of binary data
        bit_file_verify.close()
        if str(hex_value) != address_value:                                     # changes not matching, operation failed
            library.write_log(lib_constants.LOG_INFO,"INFO: Verification not "  # Info: changes were not successfully applied
                            "successfull",tc_id,script_id,
                            "None","None", log_level,tbd)
            return False, None
        else:
            library.write_log(lib_constants.LOG_INFO,"INFO: verification"
                            "passed.Bianry file edited successfully"            # Info: changes were successfully applied
                            ,tc_id,script_id,"None","None", log_level,tbd)
            return True, new_bin_file_path                                      # Return path of bin file
################################################################################
# Function Name     : edit_the_binary_image()
# Parameters        : start_offset,end_offset,offset_size
# ,file_name,path,data,tc_id,
#                     script_id,log_level, tbd
# Functionality     : function to get change binary image value
# Return Value      : Pass(if pass), False(if fail) and New edited file path
################################################################################
def edit_the_binary_image(start_offset,end_offset,offset_size                   # _main_
                          ,file_name,file_path,data,tc_id,script_id,
                          log_level,tbd):
    try:

        start_offset = extract_hex(start_offset)                                # Extract valid hex value
        end_offset = extract_hex(end_offset)
        data = extract_hex(data)
        offset_size = extract_hex(offset_size)

        library.write_log(lib_constants.LOG_INFO,"Converted the input values "
                        "into valid hexadecimal value", tc_id, script_id,"None",
                        "None", log_level,tbd)

        start_offset_integer = int(start_offset,lib_constants.HEX_BASE_VALUE)   # convert string hex to integer value, lib_constant(hex base value)

        if end_offset != "NONE" and offset_size != "NONE":                      # check if offset_size
                offset_size_integer = int(offset_size,lib_constants.
                                          HEX_BASE_VALUE)
                end_offset_integer = int(end_offset,lib_constants.
                                         HEX_BASE_VALUE)
                difference = end_offset_integer - start_offset_integer
                if difference == offset_size_integer:
                    pass
                else:
                     offset_size_integer = difference                           # offset difference is given priority
                     library.write_log(lib_constants.LOG_INFO,"INFO:Offset_size"# offset_size and difference are not equal
                                      "and offset difference do not match"
                                       ",priority given to offset_difference",
                                       tc_id,script_id,"None","None",
                                       log_level,tbd)
        elif end_offset == "NONE" and offset_size != "NONE":
                offset_size_integer = int(offset_size,lib_constants.
                                          HEX_BASE_VALUE)
                library.write_log(lib_constants.LOG_INFO,"INFO:End_offset not "
                                  "present", tc_id, script_id,"None","None",
                                  log_level,tbd)
        else:
                offset_size_integer = 0                                         # only one value to be changed

        if file_name == "BGUP" or end_offset == "NONE":
            # file_path = utils.ReadConfig("BGUP_IMAGE", "BGUP")
            step = script_id.split("-")[3]
            if "py" in step:
                step = step.split(".")[0]

            step_no = int(step) - 1
            file_path = utils.read_from_Resultfile(str(step_no))

            if "FAIL" in file_path or "PASS" in file_path:
                file_path = utils.ReadConfig("BGUP_IMAGE", "BGUP")        # BGUP image path
            else:
                pass

            bin_file_path = file_path

        elif (file_name != "NONE" and file_path != "NONE"):                       # search for file name and file path
            search_config_file_path = file_path.split("-")
            if(search_config_file_path[0] == "CONFIG"):                         # checking if file path contains config entry or not
                file_path = file_path.lstrip("CONFIG-")
                file_path = utils.ReadConfig(search_config_file_path[1],
                                            search_config_file_path[2])
                bin_file_path = file_path +"\\" + file_name

            else:
                bin_file_path = file_path + "\\" + file_name

        elif (file_name == "NONE" and file_path != "NONE"):                     # condition where only file path is there
            search_config_file_path = file_path.split("-")
            if(search_config_file_path[0] == "CONFIG"):
                file_path = file_path.lstrip("CONFIG-")
                file_path = utils.ReadConfig(search_config_file_path[1],
                                            search_config_file_path[2])
                bin_file_path = file_path

            else:
                bin_file_path = file_path

        else:
            library.write_log(lib_constants.LOG_INFO,"INFO:Required parameter "
                                  "not present", tc_id, script_id,"None","None",
                                  log_level,tbd)

        original_bin_file_path = bin_file_path
        parent_dir, child_dir = os.path.split(original_bin_file_path)           # splitting file path in parent and chil directory
        new_bin_file_path = parent_dir + "\\new-" +child_dir                    # path of new file on which operation is to be performed
        shutil.copy(original_bin_file_path,new_bin_file_path)

        create_powershell_file(start_offset_integer,new_bin_file_path,data,
                               offset_size_integer,tc_id,script_id)             # declaration of create_powershell_file function

        execute_powershell(tc_id,script_id,log_level,tbd)                       # declaration of execute powershell file

        verify_result, output_file_path = verify_changes(new_bin_file_path,data,
                                          start_offset_integer,
                                          offset_size_integer,tc_id,script_id,
                                          log_level,tbd)
        if  True == verify_result:
            return True, output_file_path                                       # if verification successful than returns true
        else:
            return False,output_file_path

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,            # Return Exception if any failure is there
        tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
