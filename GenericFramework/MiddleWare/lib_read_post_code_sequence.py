__author__ = r"kvex/asharanx/kapilshx/tnaidux"

# General Python Imports
import os
import time
from threading import Thread

# Local Python Imports
import lib_constants
import library
import utils
if os.path.exists(lib_constants.TTK2_INSTALL_FOLDER):
    import lib_ttk2_operations


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={},
                 Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None

    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)

    def join(self):
        Thread.join(self)
        return self._return


def read_verify_post_code_sequence(input_sequence, end_point, boot_type,
                                   test_case_id, script_id, log_level="ALL",
                                   tbd=None):

    try:
        import lib_ttk2_operations
        lib_ttk2_operations.kill_ttk2(test_case_id, script_id, log_level, tbd)
        ttk_device = lib_ttk2_operations.gpio_initialize(test_case_id, script_id, log_level, tbd)
        thread1 = ThreadWithReturnValue(target=get_verify_post_code_sequence,
                                        args=(input_sequence, end_point,
                                              boot_type, test_case_id,
                                              script_id, log_level, tbd))
        thread2 = ThreadWithReturnValue(target=g3_reboot_system_for_postcode,
                                        args=(test_case_id, script_id,
                                              log_level, tbd))

        thread1.start()
        thread2.start()

        if thread1.join() and thread2.join():
            library.write_log(lib_constants.LOG_INFO, "INFO: Read & verify "
                              "post code sequence by doing g3_reboot_cycle "
                              "till %s successfully" % end_point, test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "read & verify post code sequence by doing "
                              "g3_reboot_cycle till %s" % end_point,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False

################################################################################
# Function Name : get_verify_post_code_sequence
# Parameters    : input_sequence, end_point, boot_type, tc_id, script_id,
#                 log_level, tbd
# Functionality : To get the postcode sequence while boot to OS/EDK shell
# Return Value  : True on successful action, False otherwise
################################################################################


def get_verify_post_code_sequence(input_sequence, end_point, boot_type, tc_id,
                                  script_id, log_level="ALL", tbd=None):

    try:
        if "config-" in input_sequence.lower():
            tag = str(input_sequence.split("-")[1])
            value = str(input_sequence.split("-")[2])
            input_sequence = utils.ReadConfig(tag, value)
            if "None" == input_sequence:
                sequence = None
            else:
                input_sequence = input_sequence.split(",")
                sequence = []
                for element in input_sequence:
                    sequence.append(element.strip())

        if sequence is None:
            defined_post_code_list = []                                         # Defining an empty list
            if "OS" == end_point:                                               # Checks if string is 'OS'. It is the state for which the final post code has to be read
                if "FAST BOOT" in boot_type:                                    # If boot type to os is fast boot
                    if "ICL" == utils.ReadConfig("Platform", "Name"):
                        defined_post_code_list = \
                            lib_constants.POSTCODE_ICL_OS_FASTBOOT_LIST         # Gets the post code of OS from lib_constants if the platform is ICL
                    elif "CML" == utils.ReadConfig("Platform", "Name"):
                        defined_post_code_list = \
                            lib_constants.POSTCODE_CML_OS_FASTBOOT_LIST         # Gets the post code of OS from lib_constants if the platform is CML
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Not implemented for given "
                                          "platform", tc_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
                else:                                                           # If boot type to os is full boot
                    if "ICL" == utils.ReadConfig("Platform", "Name"):
                        defined_post_code_list = \
                            lib_constants.POSTCODE_ICL_OS_FULLBOOT_LIST         # Gets the post code of OS from lib_constants if the platform is ICL
                    elif "CML" == utils.ReadConfig("Platform", "Name"):
                        defined_post_code_list = \
                            lib_constants.POSTCODE_CML_OS_FULLBOOT_LIST         # Gets the post code of OS from lib_constants if the platform is CML
                    else:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                          " Not implemented for given "
                                          "platform", tc_id, script_id, "None",
                                          "None", log_level, tbd)
                        return False
            elif "EDK SHELL" == end_point:                                      # Checks if string is 'EDK Shell'. It is the state for which the final post code has to be read
                if "ICL" == utils.ReadConfig("Platform", "Name"):
                    defined_post_code_list = \
                        lib_constants.POSTCODE_ICL_EDK_LIST                     # Gets the post code of EDK Shell from lib_constants if the platform is KBL
                elif "CML" == utils.ReadConfig("Platform", "Name"):
                    defined_post_code_list = \
                        lib_constants.POSTCODE_CML_EDK_LIST                     # Gets the post code of EDK Shell from lib_constants if the platform is APL
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Not implemented for given platform",
                                      tc_id, script_id, "None", "None",
                                      log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid"
                                  " parameter for end point for reading post "
                                  "code sequence", tc_id, script_id, "None",
                                  "None", log_level, tbd)
                return False
        else:
            defined_post_code_list = sequence
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

    try:
        defined_post_code_list_log = \
            (' - '.join(defined_post_code_list)).upper()                        # Appending post codes with - and convert in to upper case

        library.write_log(lib_constants.LOG_INFO, "INFO: Defined Post code "
                          "sequence for %s till %s is as: %s"
                          % (boot_type, end_point, defined_post_code_list_log),
                          tc_id, script_id, "None", "None", log_level, tbd)

        post_code_list = []                                                     # Empty list has been initialised
        counter = 0

        initial_post_code = lib_ttk2_operations.\
            read_post_code(tc_id, script_id, log_level, tbd)                    # Calls the function to read the post code from he library
        previous_post_code = initial_post_code

        library.write_log(lib_constants.LOG_INFO, "INFO: postcode reading got "
                          "initiated", tc_id, script_id, "None", "None",
                          log_level, tbd)

        counter_power_down = 0
        while True:                                                             # Loop to iterate till we get the postcode "ffff" which is shutdown postcode
            current_post_code = lib_ttk2_operations.\
                read_post_code(tc_id, script_id, log_level, tbd)

            if "ffff" == current_post_code.lower():                             # If current_post_code is equal to the "ffff" then append to post_code_list
                post_code_list.append(current_post_code)
                break
            else:
                counter_power_down += 1
                pass

        counter_power_down = 0
        while True:                                                             # Loop to iterate till we get the postcode "ffff" and "0000"
            current_post_code = lib_ttk2_operations.\
                read_post_code(tc_id, script_id, log_level, tbd)

            if "0000" != current_post_code.lower() and \
               "ffff" != current_post_code.lower():                             # If current_post_code is equal to the "ffff" and "0000" then append to post_code_list
                post_code_list.append(current_post_code)
                break
            else:
                counter_power_down += 1
                pass

        while True:                                                             # Loop to iterate till we get the postcode which is given in lib_constants
            current_post_code = lib_ttk2_operations.\
                read_post_code(tc_id, script_id, log_level, tbd)
            counter = counter + 1

            if current_post_code == previous_post_code:                         # Checks if the cuirrent and previous post code is same
                pass                                                            # Do nothing. only changed post codes should be written to file
            else:
                post_code_list.append(current_post_code)
                previous_post_code = current_post_code                          # Appends the new postcode into the list and writes into the file

            if current_post_code == defined_post_code_list[-1]:                 # Checks if the current postcode is same as requested
                post_code_list.append(current_post_code)
                break

            if counter > lib_constants.DEBUG_COUNTER:                           # If postcode checks counter goes beyond the value (lib_constants.DEBUG_COUNTER)
                library.write_log(lib_constants.LOG_INFO, "INFO: Postcode "
                                  "sequence is read as: %s"
                                  % ' - '.join(post_code_list), tc_id,
                                  script_id, "None", "None", log_level, tbd)

                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to read post code sequence. Post code is "
                                  "not found for %s till %s in the sequence"
                                  % (boot_type, end_point), tc_id, script_id,
                                  "None", "None", log_level, tbd)
                return False

        post_code_list = list(set(post_code_list))                              # To remove the duplicate entries in the list
        post_code_list_log = (' - '.join(post_code_list)).upper()

        library.write_log(lib_constants.LOG_INFO, "INFO: Post code sequence "
                          "has been read for %s till %s is as: %s"
                          % (boot_type, end_point, post_code_list_log), tc_id,
                          script_id, "None", "None", log_level, tbd)

        matching_counter = 0
        for item in post_code_list:
            if item.strip() in defined_post_code_list:
                matching_counter += 1
            else:
                pass

        library.write_log(lib_constants.LOG_INFO, "INFO: Matched post code "
                          "sequence counter is %s & defined post sequence "
                          "counter is %s" % (matching_counter,
                                             len(defined_post_code_list)),
                          tc_id, script_id, "None", "None", log_level, tbd)

        if matching_counter >= (len(defined_post_code_list)/4):                 # If 25% percent postcode matches from the defined_post_code_list in the lib_constant file
            library.write_log(lib_constants.LOG_INFO, "INFO: post code "
                              "sequence is verified as subset of defined post "
                              "code list successfully", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return True
        else:                                                                   # If failed to match 25% percent postcode from the defined_post_code_list in the lib_constant file
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "verify post code sequence as subset of defined "
                              "post code list", tc_id, script_id, "None",
                              "None", log_level, tbd)
            return False
    except Exception as e:                                                      #If exception occurs in read_post code sequence() function
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        return False

################################################################################
# Function Name : g3_reboot_system_for_postcode
# Parameters    : tc_id, script_id, log_level, tbd
# Functionality : Performs G3 followed by power button press for to boot to OS
#                 or EDK Shell
# Return Value  : True on successful action, False otherwise
################################################################################


def g3_reboot_system_for_postcode(tc_id, script_id, log_level="None",
                                  tbd="None"):

    try:
        dc_signal_port = utils.ReadConfig("TTK", "dc_signal_port")
        dc_power_port = utils.ReadConfig("TTK", "dc_power_port")
        typec_power_port = utils.ReadConfig("TTK", "typec_power_port")

        result = lib_ttk2_operations.\
            perform_g3_reboot(dc_signal_port, dc_power_port, typec_power_port,
                              tc_id, script_id, log_level, tbd)

        if result:
            time.sleep(lib_constants.TWENTY)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "Reboot", tc_id, script_id, "None", "None",
                              log_level, tbd)
            time.sleep(lib_constants.TWENTY)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", "None", log_level, tbd)
        time.sleep(lib_constants.TWENTY)
        return False
