__author__ = 'singhd1x'

################################Global Imports##################################
import sys
import os
import re
########################## Local Imports #######################################
import lib_epcs
import utils
import library
import lib_constants
import lib_read_bios

################################################################################
# Function name  : connect_memory_module
# Description    : connect memory module of <size> and frequency <MHz> to
#                  channel <n> and slot <n>
# Parameters     : mem_size, mem_freq, mem_channel, slot_num, step_value,
#                  tc_id, script_id, log_level and tbd
# Returns        : True/False
################################################################################
def connect_memory_module(mem_size,mem_freq,mem_channel,slot_num,step_value,
                          tc_id,script_id,log_level = "ALL",tbd = None):
    cur_dir = os.getcwd()
    try:
        if tbd.upper() in lib_constants.TBD_PLATFORM:
            bios_string = lib_constants.MEMORY_CONFIGURATION_FH                 #setting path for reading frequency from bios
            lib_read_bios.read_bios(bios_string, tc_id, script_id, cur_dir,
                                    log_level, tbd)                             #read bios value for given string_inbios from biosconf tool
            bios_frequency = utils.read_from_Resultfile(step_value)             #reading frequency value from result file
            frequency_output = str(bios_frequency).replace(" ", "")             #out put stored in frequency_output variable

            library.write_log(lib_constants.LOG_INFO, "INFO: On board frequency"
            " of memory is : %s"%frequency_output, tc_id, script_id, "None",
            "None", log_level, tbd)

            slot_string = lib_constants.MEMORY_CONFIGURATION_SZ + "Channel" + \
                " " + mem_channel + " " + "Slot" + " " + slot_num               #setting path for reading slot value from bios using
            lib_read_bios.read_bios(slot_string, tc_id, script_id, cur_dir,
                                    log_level, tbd)                             #read bios value for given string_inbios from bios conf tool
            bios_slot = utils.read_from_Resultfile(step_value)                  #reading slot value from result file

            library.write_log(lib_constants.LOG_INFO, "INFO: On board bios slot"
            " of memory is : %s"%bios_slot, tc_id, script_id, "None", "None",
            log_level, tbd)                                                     #out put stored in bios_slot variable

            dimm_size = lib_constants.MEMORY_CONFIGURATION_SZ + "Channel" + \
                " " + mem_channel + " " + "Slot" + " " + slot_num + "/" + "Size"#setting path for reading dimm size from bios using
            lib_read_bios.read_bios(dimm_size, tc_id, script_id, cur_dir,
                                    log_level, tbd)                             #read bios value for given string_inbios from biosconf tool
            size_mb = utils.read_from_Resultfile(step_value)                    #reading memo size value from result file
                                                                                #out put stored in bios_slot variable
            library.write_log(lib_constants.LOG_INFO, "INFO: On board size of "
            "memory is : %s"%size_mb, tc_id, script_id, "None", "None",
            log_level, tbd)

            if frequency_output == str(mem_freq) + "MHz":                       #checking for input frequency matches with the frequency found in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: The Memory "
                "frequency connected  %s is matching with input %s"%(mem_freq,
                frequency_output), tc_id, script_id, "None", "None", log_level,
                tbd)                                                            #if yes then print frequency matches
            else:                                                               #else print frequency mismatch
                library.write_log(lib_constants.LOG_INFO, "INFO: The Memory "
                "frequency connected is not %s"%(mem_freq), tc_id, script_id,
                "None", "None", log_level, tbd)
                return False                                                    #return false

            if "Populated & Enabled" == str(bios_slot):                         #checking if given slot is enabled and populated
                library.write_log(lib_constants.LOG_INFO, "INFO: The Memory "
                "channel and slot is in enable state, proceeding for next "
                "match", tc_id, script_id, "None", "None", log_level, tbd)
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: Channel %s "
                "Slot %s not in Populated & Enabled it is in %s"%(mem_channel,
                slot_num, bios_slot), tc_id, script_id, "None", "None",
                log_level, tbd)
                return False

            bio_size_mb = re.findall('\d+', size_mb)                            #getting the memory size
            mb_output = int(bio_size_mb[0])
            convert_gb = mb_output / lib_constants.GB_SIZE                      #convert the memory output in GB

            if int(convert_gb) == int(re.findall('\d+', mem_size)[0]):          #checking if given memory size is matching with given output of bios
                library.write_log(lib_constants.LOG_INFO, "INFO: The connected"
                " memory size is matching with %s as specified"%(mem_size),
                tc_id, script_id, "None", "None", log_level, tbd)               #if yes write to log file
                return True                                                     #return true for all the parameter matches successfully
            else:                                                               #else return false
                library.write_log(lib_constants.LOG_INFO, "INFO: The connected"
                " memory size is not %s as specified"%(mem_size), tc_id,
                script_id, "None", "None", log_level, tbd)
                return False

        else:
            freq_channel = lib_constants.MMEMORY_CHANNEL_FREQUENCY
            if "0" == mem_channel and "0" == slot_num:
                bios_channel = lib_constants.CHANNEL_0_SLOT_0
                size_channel = lib_constants.CHANNEL_0_SLOT_0_SIZE
            elif "0" == mem_channel and "1" == slot_num:
                bios_channel = lib_constants.CHANNEL_0_SLOT_1
                size_channel = lib_constants.CHANNEL_0_SLOT_1_SIZE
            elif "1" == mem_channel and "0" == slot_num:
                bios_channel = lib_constants.CHANNEL_1_SLOT_0
                size_channel = lib_constants.CHANNEL_1_SLOT_0_SIZE
            elif "1" == mem_channel and "1" == slot_num:
                bios_channel = lib_constants.CHANNEL_1_SLOT_1
                size_channel = lib_constants.CHANNEL_1_SLOT_1_SIZE
            else:
                library.write_log(lib_constants.LOG_INFO, "INFO: %s is not a "
                "valid channal or slot is wrong"%mem_channel, tc_id, script_id,
                "None", "None", log_level, tbd)
                return False

            try:
                ret, result = lib_read_bios.\
                    xml_cli_read_bios(bios_channel, tc_id, script_id, log_level,
                                      tbd)

                if lib_constants.SEVEN != ret and lib_constants.THREE != ret:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Memory is"
                    " not connected to channel %s slot %s"%(mem_channel,
                    slot_num), tc_id, script_id, "None", "None", log_level, tbd)
                    return False
                else:
                    ret1, size = lib_read_bios.\
                        xml_cli_read_bios(size_channel, tc_id, script_id,
                                          log_level, tbd)
                    ret2, freq = lib_read_bios.\
                        xml_cli_read_bios(freq_channel, tc_id, script_id,
                                          log_level, tbd)

                    if lib_constants.SEVEN != ret1 and \
                       lib_constants.SEVEN != ret2:
                        library.write_log(lib_constants.LOG_INFO, "INFO: Failed"
                        " to get memory size and frequency from bios", tc_id,
                        script_id, "None", "None", log_level, tbd)
                        return False
                    else:
                        pass

                    library.write_log(lib_constants.LOG_INFO, "INFO: Connected"
                    " memory = %s, Frequency = %s"%(size, freq), tc_id,
                    script_id, "None", "None", log_level, tbd)

                    temp = re.sub("\D", "", mem_size)
                    size_gb = int(size.split("MB")[0].strip()) / \
                              lib_constants.GB_SIZE

                    if str(temp) == str(size_gb) and \
                       mem_freq.strip() == freq.split(" ")[0].strip():
                        return True
                    else:
                        return False

            except Exception as e:
                library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e,
                tc_id, script_id, "None", "None", log_level, tbd)
                return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "ERROR: Due to %s"%e, tc_id,
        script_id, "None", "None", log_level, tbd)
        return False