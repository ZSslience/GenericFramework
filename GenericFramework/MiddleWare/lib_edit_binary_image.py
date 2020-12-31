__author__ = 'singhd1x'

############################General Python Imports##############################
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
# Function Name     : edit_binary_image
# Parameters        : tc_id, script_id, device, loglevel, tbd
# Functionality     : function to get change binary image value
# Return Value      : Pass(if pass), False(if fail)
################################################################################

def edit_binary_image(offset_one,offset_two,size,file_name,path,data,tc_id,
                      script_id,log_level = "ALL",tbd = None):

    filename= utils.ReadConfig('Config-Security-BGUP', file_name )               #reading bin file name from config file
    path = utils.ReadConfig('Config-Security-BGUP', path)                      #reading bin file path from config file
    log_path =lib_constants.SCRIPTDIR
    os.chdir(log_path)                                                          #set the current directory as script directory
    library.write_log(lib_constants.LOG_INFO,"INFO :Current Directory : "       #write the current working directory information to log file
                +os.getcwd(),tc_id,script_id, "None", "None", log_level, tbd)
    try:
        bin_file_path = path + "\\" + filename
        orignial_bin_file_path = bin_file_path
        new_bin_file_path = path +  "\\" + "new"+filename
        shutil.copy(orignial_bin_file_path,new_bin_file_path)                   #makeing copy of bin file
        if offset_two == 'None'and size == 'None':
            with open("create_powershell_script.ps1","w") as power_shell:       #genearte  power shell script file
                power_shell.write('$bytes = [System.IO.File]::ReadAllBytes'     #readubg binary file using powershell
                         '("'+new_bin_file_path+'");\n')
                value = str(data)                                               #asign the value to be replace
                index = str(offset_one)                                         #asign the offset where the value has to be edited
                power_shell.write("$bytes["+index+"] = "+value+";\n")           #write to binary file
                power_shell.write('[System.IO.File]::WriteAllBytes'             #modify the file and close
                                  '("'+new_bin_file_path+'", $bytes);')
                power_shell.close()
        library.write_log( lib_constants.LOG_INFO,"INFO : "
            "create_powershell_script.ps1 script  created successfully",
                           tc_id,script_id, "None", "None", log_level, tbd)
        power_shell_ter="powershell.exe Set-ExecutionPolicy Unrestricted -force"
        subprocess.Popen(power_shell_ter, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        library.write_log(lib_constants.LOG_INFO,"INFO : powershell.exe "
                "Set-ExecutionPolicy Unrestricted -force executed to launch "
                "powershell ",tc_id,script_id, "None", "None", log_level, tbd)
        time.sleep(lib_constants.FIVE)
        execute_file = "powershell.exe ./create_powershell_script.ps1"
        subprocess.Popen(execute_file, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        library.write_log(lib_constants.LOG_INFO,"INFO :"
            " cmd powershell.exe ./data.ps1 executed to modify the offset in "
            "binary file ",tc_id,script_id, "None", "None", log_level, tbd)
        time.sleep(lib_constants.FIVE)
        with open(new_bin_file_path, 'rb') as bit_file_verify:
            if 'H' in data or 'h' in data:
                address_value = data.strip('H')                                 # Strip the 'H' from the input Hex address
                print(address_value)
            elif '0x' in data:
                address_value = data.strip('0x')                                # Strip the '0X' from the input Hex address
                print(address_value)
            else:
                pass
            address = int(offset_one, base=16)
            bit_file_verify.seek(address)
            bytes = str(binascii.hexlify(bit_file_verify.read(1)))
            bit_file_verify.close()
            bytes = int(bytes)
        if bytes != int(address_value):
            return False
        else:
            shutil.copy(new_bin_file_path,orignial_bin_file_path)
            return True

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR : %s " %e,
            tc_id, script_id, "None", "None", log_level, tbd)
        return False
