__author__ = "kapilshx\sharadth\sushil"

###########################General Imports######################################
import os
import SendKeys
import time
import sys
############################Local imports#######################################
import lib_constants
import library
import utils
import lib_set_bios
from threading import Thread
import lib_read_bios
import lib_epcs
################################################################################
# Function Name :load_bios_mandatory_settings
# Parameters    :bios_setting_token_pf_pmf, test_case_id, script_id, 
#               loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality :To do load_bios_mandatory_settings for <RTD3/CS>
################################################################################
def load_bios_mandatory_settings(bios_setting_token_pf_pmf,platform, test_case_id,
                                 script_id, loglevel = "ALL", tbd="None"):
    if (("APL" == platform) and ("CS" in bios_setting_token_pf_pmf or
                    "S0I3" == bios_setting_token_pf_pmf)):                      # if 'CS' or 'SOi3' string in  bios_setting_token and platform is APL
        cs_apl_first_list = []
        for bios_path in lib_constants.MANDATORY_CS_SETTINGS_APL:               # loop to set the mandatory cs settings for apl
            cs_apl_first = lib_set_bios.lib_write_bios(bios_path,test_case_id,
                                                 script_id,loglevel, tbd)
            cs_apl_first_list.append(cs_apl_first)
        cs_apl_first_flag = True
        for item in cs_apl_first_list:                                          #loop to check whether all bios settings are properly updated or not
            if 3 != item:
                cs_apl_first_flag = False

        if False == cs_apl_first_flag:                                          #if all bios settings are not updated
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "Update mandatory cs settings in bios for APL ", test_case_id,
                              script_id,"None", "None", loglevel, tbd)
            return False
        else:                                                                   #if all bios settings are updated successfully
            library.write_log(lib_constants.LOG_INFO, "INFO: Update "
            "successful for mandatory cs settings in bios for APL ",
                     test_case_id,script_id,"None", "None", loglevel, tbd)
            return True
    else:
        pass
    if (("GLK" == platform) and ("CS" in bios_setting_token_pf_pmf or
                    "S0I3" == bios_setting_token_pf_pmf)):
        try:
            s0i3_settings_TURBOBOOSTTECHNOLOGY=lib_set_bios.\
                    lib_write_bios(lib_constants.TURBOBOOSTTECHNOLOGY,
                    test_case_id, script_id, loglevel , tbd)                    #to set the option of low power S0 IDLE capability in the bios
            s0i3_settings_PCIEXPRESS=lib_set_bios.\
                    lib_write_bios(lib_constants.PCIEXPRESS,
                    test_case_id, script_id, loglevel, tbd)                     #to set the option of low power IUER BUTTON ENABLE in the bios
            s0i3_settings_DPTF=lib_set_bios.\
                    lib_write_bios(lib_constants.DPTF_GLK,
                    test_case_id, script_id, loglevel , tbd)                    #to set the option of low power XDCI SUP
            s0i3_settings_KERNELDEBUGGER=lib_set_bios.\
                    lib_write_bios(lib_constants.KERNELDEBUGGER,
                    test_case_id, script_id, loglevel , tbd)
            s0i3_settings_LOWPOWERS0IDLE=lib_set_bios.\
                    lib_write_bios(lib_constants.LOWPOWERS0IDLE,
                    test_case_id, script_id, loglevel , tbd)
            s0i3_mandatory_settings_all =\
                    [s0i3_settings_TURBOBOOSTTECHNOLOGY,
                    s0i3_settings_PCIEXPRESS,s0i3_settings_DPTF,
                    s0i3_settings_KERNELDEBUGGER,s0i3_settings_LOWPOWERS0IDLE]  #To store all values in list
            s0i3_output_mandatory_flag = True                                   #To initialize the dmos_output_mandatory_flag
            for s0i3_output_mandatory in s0i3_mandatory_settings_all:
                if 3 != s0i3_output_mandatory:                                  #if option is not updated in bios
                        s0i3_output_mandatory_flag = False                      #To set the dmos_output_mandatory_flag
                        break
                else:
                        continue
            if True == s0i3_output_mandatory_flag :                             #if dmos_output_mandatory_flag is equal to True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                "successful for mandatory_%s settings in bios "
                %(bios_setting_token_pf_pmf), test_case_id, script_id,
                    "None", "None", loglevel, tbd)                              #write msg to log
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                "Update mandatory_%s settings in bios "
                %(bios_setting_token_pf_pmf), test_case_id, script_id,
                    "None", "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " load bios mandatory settings for %s library "
            "function as %s "%(bios_setting_token_pf_pmf, e), test_case_id,
            script_id, "None", "None", loglevel, tbd)                           # Write the exception error msg to log
            return False
    else:
        pass
    if 'TBT' in bios_setting_token_pf_pmf:                                      # if 'RTD3' string in  bios_setting_token
        try:
            THUNDERBOLT_SUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.THUNDERBOLT_SUPPORT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of CSM control in the bios
            if 3 == THUNDERBOLT_SUPPORT:
                return True
            else:
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " load bios mandatory settings for TBT function"
                " as %s " %e, test_case_id, script_id, "None", "None",
                    loglevel, tbd)                                              # Write the exception error msg to log
            return False

    if 'RTD3' in bios_setting_token_pf_pmf:                                     # if 'RTD3' string in  bios_setting_token
        try:
            rtd3_settings_LOWPOWERS0IDLECAPABILITY=lib_set_bios.\
                lib_write_bios(lib_constants.LOWPOWERS0IDLECAPABILITY,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power S0 IDLE capability in the bios
            rtd3_settings_RTD3SUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.RTD3SUPPORT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of RTD3 support in the bios

            rtd3_mandatory_settings_all = [rtd3_settings_RTD3SUPPORT,
            rtd3_settings_LOWPOWERS0IDLECAPABILITY]                             #To store all values in the list

            rtd3_output_mandatory_flag = True                                   #initialize a rtd3_output_mandatory_flag
            for rtd3_output_mandatory in rtd3_mandatory_settings_all:           #iterate the values in list
                if 3 != rtd3_output_mandatory:                                  #if option is not updated in bios
                    rtd3_output_mandatory_flag = False                          #set the rtd3_output_mandatory_flag
                    break
                else:                                                           #if option is updated in bios
                    continue
            if True == rtd3_output_mandatory_flag:                              #if rtd3_output_mandatory_flag is True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                    "successful for mandatory_rtd3 settings in bios ",
                    test_case_id, script_id, "None", "None", loglevel, tbd)     #write msg to log
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "Update mandatory_rtd3 settings in bios ", test_case_id,
                    script_id, "None", "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
        " load bios mandatory settings for rtd3 function"
        " as %s " %e, test_case_id, script_id, "None", "None", loglevel, tbd)   # Write the exception error msg to log
            return False

    elif 'CS' in bios_setting_token_pf_pmf:                                     # if 'CS' string in  bios_setting_token
        try:
            cs_settings_LOWPOWERS0IDLECAPABILITY=lib_set_bios.\
                lib_write_bios(lib_constants.LOWPOWERS0IDLECAPABILITY,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power LOW POWER S0 IDLE CAPABILITY in the bios
            cs_settings_RTD3SUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.RTD3SUPPORT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of low power RTD3 SUPPORT in the bios

            cs_mandatory_settings_all = [cs_settings_RTD3SUPPORT,
                cs_settings_LOWPOWERS0IDLECAPABILITY]                           #To store all values in list

            cs_output_mandatory_flag = True                                     #To initialize the cs_output_mandatory_flag
            for cs_output_mandatory in cs_mandatory_settings_all:
                if 3 != cs_output_mandatory:                                    #if option is not updated in bios
                    cs_output_mandatory_flag = False                            #To set the cs_output_mandatory_flag
                    break
                else:                                                           #if option is updated in bios
                    continue

            if True == cs_output_mandatory_flag:                                #if cs_output_mandatory_flag is True

                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                    "successful for mandatory cs settings in bios ",
                    test_case_id, script_id, "None", "None", loglevel, tbd)
                pass
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "Update mandatory cs settings in bios ", test_case_id,
                    script_id, "None", "None", loglevel, tbd)
                return False

            cs_settings_IUERBUTTONENABLE=lib_set_bios.\
                lib_write_bios(lib_constants.IUERBUTTONENABLE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of low power IUER BUTTON ENABLE in the bios
            cs_settings_XDCISUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.XDCISUPPORT,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power XDCI SUPPORT in the bios

            cs_primary_settings_all = [cs_settings_IUERBUTTONENABLE,
                                       cs_settings_XDCISUPPORT]                 #To store all values in list

            cs_output_primary_flag = True                                       #To initialize the cs_output_primary_flag
            for cs_output_primary in cs_primary_settings_all:
                if 3 != cs_output_primary:                                      #if option is not updated in bios
                    cs_output_primary_flag = False                              #To set the cs_output_primary_flag
                    break
                else:
                    continue
            if True == cs_output_primary_flag :                                 #if cs_output_primary_flag is equal to True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                    "successful for primary cs settings in bios ", test_case_id,
                    script_id, "None", "None", loglevel, tbd)
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to"
                    " Update primary cs settings in bios ", test_case_id,
                        script_id, "None", "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " load bios mandatory settings for cs function"
                    " as %s " %e, test_case_id, script_id, "None", "None",
                        loglevel, tbd)                                          # Write the exception error msg to log
            return False
    elif "DISCONNECTED MOS" == bios_setting_token_pf_pmf or \
            'CONNECTED MOS' == bios_setting_token_pf_pmf or \
                    "S0I3" == bios_setting_token_pf_pmf:                        # if 'DISCONNECTED MOS' or 'CONNECTED MOS'  or 'SOi3'string in  bios_setting_token
        try:
            dmos_settings_LOWPOWERS0IDLECAPABILITY=lib_set_bios.\
                lib_write_bios(lib_constants.LOWPOWERS0IDLECAPABILITY,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power S0 IDLE capability in the bios
            dmos_settings_IUERBUTTONENABLE=lib_set_bios.\
                lib_write_bios(lib_constants.IUERBUTTONENABLE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of low power IUER BUTTON ENABLE in the bios
            dmos_settings_XDCISUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.XDCISUPPORT,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power XDCI SUPPORT in the bios
            if lib_set_bios.set_bios_security_option\
                (lib_constants.EFI_SECURITY_ENABLE, test_case_id, script_id,
                            loglevel, tbd):
                pass
            else:
                return False
            dmos_settings_IUERSLATEENABLE=lib_set_bios.\
                lib_write_bios(lib_constants.IUERSLATEENABLE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of IUER SLATE ENABLE in the bios
            dmos_settings_IUERDOCKENABLE=lib_set_bios.\
                lib_write_bios(lib_constants.IUERDOCKENABLE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of IUER DOCK ENABLE in the bios
            dmos_settings_EXTERNALKIT=lib_set_bios.\
                lib_write_bios(lib_constants.EXTERNALKIT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of EXTERNAL KIT in the bios
            dmos_settings_HDAUDIOLINKFREQUENCY=lib_set_bios.\
                lib_write_bios(lib_constants.HDAUDIOLINKFREQUENCY,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of HD AUDIO LINK FREQUENCY in the bios
            curdir = lib_constants.SCRIPTDIR

            BOARDID = lib_read_bios.read_bios(lib_constants.BOARDID,            #to set the option of SDCARD SIDEBAND EVENTS in the bios
                test_case_id, script_id, curdir)
            BOARDID = str(BOARDID)
            if "RVP11" in BOARDID:
                dmos_mandatory_settings_all =\
                [dmos_settings_LOWPOWERS0IDLECAPABILITY,
                 dmos_settings_IUERBUTTONENABLE, dmos_settings_XDCISUPPORT,
                 dmos_settings_IUERSLATEENABLE, dmos_settings_IUERDOCKENABLE,
                 dmos_settings_EXTERNALKIT, dmos_settings_HDAUDIOLINKFREQUENCY]
                pass
            elif "KBLR" == platform:
                dmos_settings_THUNDERBOTSUPPORT = lib_set_bios.\
                lib_write_bios(lib_constants.THUNDERBOLTSUPPORT,                #to set the option of SDCARD SIDEBAND EVENTS in the bios
                test_case_id, script_id, loglevel, tbd)
                dmos_settings_SDCARDSIDEBANDEVENTSKBLR=lib_set_bios.\
                lib_write_bios(lib_constants.SDCARDSIDEBANDEVENTSKBLR,          #to set the option of SDCARD SIDEBAND EVENTS in the bios
                test_case_id, script_id, loglevel, tbd)
                dmos_mandatory_settings_all =\
                    [dmos_settings_LOWPOWERS0IDLECAPABILITY,
                    dmos_settings_IUERBUTTONENABLE, dmos_settings_XDCISUPPORT,
                     dmos_settings_IUERSLATEENABLE, dmos_settings_IUERDOCKENABLE,
                     dmos_settings_EXTERNALKIT, dmos_settings_HDAUDIOLINKFREQUENCY,
                     dmos_settings_THUNDERBOTSUPPORT,
                     dmos_settings_SDCARDSIDEBANDEVENTSKBLR]
            else:
                dmos_settings_SDCARDSIDEBANDEVENTS=lib_set_bios.\
                lib_write_bios(lib_constants.SDCARDSIDEBANDEVENTS,              #to set the option of SDCARD SIDEBAND EVENTS in the bios
                test_case_id, script_id, loglevel, tbd)
                dmos_mandatory_settings_all =\
                    [dmos_settings_LOWPOWERS0IDLECAPABILITY,
                    dmos_settings_IUERBUTTONENABLE, dmos_settings_XDCISUPPORT,
                     dmos_settings_IUERSLATEENABLE, dmos_settings_IUERDOCKENABLE,
                     dmos_settings_EXTERNALKIT, dmos_settings_HDAUDIOLINKFREQUENCY,
                     dmos_settings_SDCARDSIDEBANDEVENTS]                        #To store all values in list
            dmos_output_mandatory_flag = True                                   #To initialize the dmos_output_mandatory_flag
            for dmos_output_mandatory in dmos_mandatory_settings_all:
                if 3 != dmos_output_mandatory:                                  #if option is not updated in bios
                    dmos_output_mandatory_flag = False                          #To set the dmos_output_mandatory_flag
                    break
                else:
                    continue
            if True == dmos_output_mandatory_flag :                             #if dmos_output_mandatory_flag is equal to True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                    "successful for mandatory_%s settings in bios "
                    %(bios_setting_token_pf_pmf), test_case_id, script_id,
                        "None", "None", loglevel, tbd)                          #write msg to log
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
                    "Update mandatory_%s settings in bios "
                        %(bios_setting_token_pf_pmf), test_case_id, script_id,
                            "None", "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " load bios mandatory settings for %s library "
                "function as %s "%(bios_setting_token_pf_pmf, e),
                test_case_id, script_id, "None", "None", loglevel, tbd)         # Write the exception error msg to log
            return False
    else:                                                                       # if both RTD3/CS/DISCONNECTED MOS option is not present in toekn
        library.write_log(lib_constants.LOG_INFO, "INFO: Input token is "
            "incorrect", test_case_id, script_id, "None", "None", loglevel, tbd) # Write the exception error msg to log
        return False

################################################################################
# Function Name :load_bios_secondary_settings
# Parameters    :bios_setting_token_pf_pmf, test_case_id, script_id, loglevel, tbd
# Return Value  : True on success, False on failure
# Functionality :To do load bios secondary settings for <RTD3/CS>
################################################################################
def load_bios_secondary_settings(bios_setting_token_pf_pmf, platform,
              test_case_id, script_id, loglevel = "ALL", tbd="None"):
    if (("APL" == platform) and ("CS" in bios_setting_token_pf_pmf or
                    "S0I3" == bios_setting_token_pf_pmf)):                      # if 'CS' or 'SOi3' string in  bios_setting_token and platform is APL
        cs_apl_second_list = []
        for bios_path in lib_constants.SECONDARY_CS_SETTINGS_APL:               # loop to set the secondary cs settings for apl
            cs_apl_second = lib_set_bios.lib_write_bios(bios_path,test_case_id,
                                                  script_id, loglevel, tbd)
            cs_apl_second_list.append(cs_apl_second)
        cs_apl_second_flag = True
        for item in cs_apl_second_list:                                         #loop to check whether all bios settings are properly updated or not
            if 3 != item:
                cs_apl_second_flag = False
        if False == cs_apl_second_flag:                                         #if all bios settings are not updated
            library.write_log(lib_constants.LOG_INFO, "INFO: Failed to "
            "Update secondary cs settings in bios for APL ", test_case_id,
            script_id,"None", "None", loglevel, tbd)
            return False
        else:                                                                   #if all bios settings are updated successfully
            library.write_log(lib_constants.LOG_INFO, "INFO: Update "
            "successful for secondary cs settings in bios for APL ",
            test_case_id,script_id,"None", "None", loglevel, tbd)
            return True
    else:
        pass
    if (("GLK" == platform) and ("CS" in bios_setting_token_pf_pmf or
                    "S0I3" == bios_setting_token_pf_pmf)):
        library.write_log(lib_constants.LOG_INFO, "INFO: This setting is"
                    " not applicable for GLK platform ",
                     test_case_id,script_id,"None", "None", loglevel, tbd)
        return True
    if 'TBT' in bios_setting_token_pf_pmf:                                      # if 'TBT' string in  bios_setting_token
        try:
            port_option = lib_constants.TBT_ROOT_PORT_SELECTOR                  # assign bios option for the tbt_root_port_selector into port option
            sub_option = ((port_option.split("=")[0]).split("/")[-1]).strip()   # assign tbt root port selector into sub option
            option_port_1 = (port_option.split("=")[1]).strip()                 # assign PCH-PCI express port 1 into option_port_1
            option_port_9 = (((lib_constants.TBT_ROOT_PORT_SELECTOR_PORT_9)\
                              .split("=")[1]).split("/")[-1]).strip()           # assign PCH-PCI express port 9 into option_port_9
            if False != lib_epcs.readbios("epcs_log.txt", test_case_id,
                                          script_id, loglevel, tbd):            # read the bios option using biosconf tool
                pass
            else:                                                               # failed to read the bios option using biosconf tool
                return False
            result_q_id = lib_epcs.getquestionid(sub_option,
                            "epcs_log.txt", test_case_id, script_id, loglevel,
                                                 tbd, None)                     # to get the questionid of tbt_root_port_selector bios option
            if False != result_q_id and None != result_q_id:
                 pass
            else:                                                               # failed to get the questionid of tbt_root_port_selector bios option
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed "
                    "to get the quetion_id of TBT port selector option in bios",
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
            option_dict=lib_epcs.get_options(sub_option,
                test_case_id, script_id, None, None, None, None, result_q_id)   # to get the sub option of the tbt_root_port_selector bios option
            if False != option_dict and None != option_dict:
                 pass
            else:                                                               # failed to get the sub option of the tbt_root_port_selector bios option
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed "
                    "to get the bios option under TBT port selector",
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                return False
            if option_port_9 in list(option_dict.keys()):                             # if PCH-PCI express port 9 is present in the option_dict
                tbt_list = [lib_constants.AIC_SUPPORT, lib_constants.AR_AIC_SUPPORT,
    lib_constants.SECURITY_LEVEL, lib_constants.ENABLE_CLK_REQ,
    lib_constants.ENABLE_ASPM, lib_constants.GPIO_FILTER,
    lib_constants.TBT_ROOT_PORT_SELECTOR_PORT_9, lib_constants.TBT_HOST_ROUTER,
    lib_constants.ABOVE_4GB_MMIO_BIOS_ASSIGNMENT,
    lib_constants.ASPM_PORT_9, lib_constants.Ll_SUBSTATES_PORT_9,
    lib_constants.GEN3_EQ_PHASE3_METHOD_PORT_9, lib_constants.DPTP_PORT_9]
            elif option_port_1 in list(option_dict.keys()):                           # if PCH-PCI express port 1 is present in the option_dict
                tbt_list = [lib_constants.AIC_SUPPORT, lib_constants.AR_AIC_SUPPORT,
    lib_constants.SECURITY_LEVEL, lib_constants.ENABLE_CLK_REQ,
    lib_constants.ENABLE_ASPM, lib_constants.GPIO_FILTER,
    lib_constants.TBT_ROOT_PORT_SELECTOR, lib_constants.TBT_HOST_ROUTER,
    lib_constants.ABOVE_4GB_MMIO_BIOS_ASSIGNMENT,
    lib_constants.ASPM, lib_constants.Ll_SUBSTATES,
        lib_constants.GEN3_EQ_PHASE3_METHOD, lib_constants.DPTP]
            else:                                                               # if both the opitons PCH-PCI express port 1 and PCH-PCI express port 9 are not present
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed "
                    "to read the TBT port selector in bios ", test_case_id,
                        script_id, "None", "None", loglevel, tbd)
                return False
            tbt_result = []
            for tbt_setting in tbt_list:
                tbt_update=lib_set_bios.\
                    lib_write_bios(tbt_setting,
                    test_case_id, script_id, loglevel, tbd)                     #to set the options of tbt bios settings in the bios
                tbt_result.append(tbt_update)
            tbt_flag = True                                                     #initialize a tbt_flag
            for item in tbt_result:                                             #To iterate the value in list
                if 3 != item:                                                   #if option is not updated in bios
                    tbt_flag = False
                    break
                else:                                                           #if option is updated in bios
                    continue
            if True == tbt_flag:                                                # if tbt_flag is True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                    "successful for secondary tbt settings in bios ",
                        test_case_id, script_id, "None", "None", loglevel, tbd)
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed "
            "to Update secondary tbt settings in bios ", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " load bios secondary settings for TBT function"
                " as %s " %e, test_case_id, script_id, "None", "None",
                    loglevel, tbd)                                              # Write the exception error msg to log
            return False
    if 'RTD3' in bios_setting_token_pf_pmf:                                     # if 'RTD3' string in  bios_setting_token
        try:
            rtd3_settings_TENSECPOWERBUTTONOVR=lib_set_bios.\
                lib_write_bios(lib_constants.TENSECPOWERBUTTONOVR,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of TEN SEC POWER BUTTON OVR in the bios
            rtd3_settings_NATIVEASPM=lib_set_bios.\
                lib_write_bios(lib_constants.NATIVEASPM,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of NATIVE ASPM in the bios
            rtd3_settings_GFXLOWPOWERMODE=lib_set_bios.\
                lib_write_bios(lib_constants.GFXLOWPOWERMODE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of GFX LOW POWER MODE in the bios
            rtd3_settings_PMSUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.PMSUPPORT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of PM SUPPORT in the bios
            rtd3_settings_I2C0SENSORHUB=lib_set_bios.\
                lib_write_bios(lib_constants.I2C0SENSORHUB,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of I2C0 SENSOR HUB in the bios
            rtd3_settings_SATAPORT1=lib_set_bios.\
                lib_write_bios(lib_constants.SATAPORT1,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of SATA PORT 1 in the bios
            rtd3_settings_SATAPORT2=lib_set_bios.\
                lib_write_bios(lib_constants.SATAPORT2,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of SATA PORT 2 in the bios
            rtd3_settings_SATAPort1DevSlp=lib_set_bios.\
                lib_write_bios(lib_constants.SATAPort1DevSlp,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of SATAPort1DevSlp in the bios
            rtd3_settings_SATAPort2DevSlp=lib_set_bios.\
                lib_write_bios(lib_constants.SATAPort2DevSlp,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of SATAPort2DevSlp in the bios

            rtd3_secondary_settings_all = [rtd3_settings_TENSECPOWERBUTTONOVR,
                        rtd3_settings_NATIVEASPM, rtd3_settings_GFXLOWPOWERMODE,
            rtd3_settings_PMSUPPORT, rtd3_settings_I2C0SENSORHUB,
                        rtd3_settings_SATAPORT1, rtd3_settings_SATAPORT2,
            rtd3_settings_SATAPort1DevSlp, rtd3_settings_SATAPort2DevSlp]       #To store all values in the list
            rtd3_output_secondary_flag = True                                   #initialize a rtd3_output_secondary_flag
            for rtd3_output_secondary in rtd3_secondary_settings_all:           #To iterate the value in list
                if 3 != rtd3_output_secondary:                                  #if option is not updated in bios
                    rtd3_output_secondary_flag = False
                    break
                else:                                                           #if option is updated in bios
                    continue
            if True == rtd3_output_secondary_flag:                              # if rtd3_output_secondary_flag is True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
    "successful for secondary rtd3 settings in bios ", test_case_id, script_id,
                                  "None", "None", loglevel, tbd)
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed "
            "to Update secondary rtd3 settings in bios ", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
                return False

            rtd3_vbs = utils.ReadConfig("RTD3_VBS_FILE", "vbs_file_name")       #reading the config file
            if "Fail" in rtd3_vbs:
                library.write_log(lib_constants.LOG_INFO, "INFO:Config entry "
                 "is missing for tag variable rtd3_vbs ", test_case_id,
                                  script_id, "None", "None", loglevel, tbd)
                return False
            else:
                pass

            os.chdir(lib_constants.TOOLPATH)
            rtd3_obj = Thread(target=rtd3_time_delay, args=( ))                 #Create thread object to send keys in background
            rtd3_obj.start()                                                    #To call the start() using thread object
            rtd3_cmd_result = os.system(rtd3_vbs)                               #executes the .vbs file in cmd prompt
            if 0 == rtd3_cmd_result :                                           #if rtd3_vbs executed successfully
                library.write_log(lib_constants.LOG_INFO, "INFO:RTD3 registry "
                "command executed successfully", test_case_id, script_id, "None",
                "None", loglevel, tbd)
                return True
            else:                                                               #returns False if rtd3_vbs command failed to execute
                library.write_log(lib_constants.LOG_WARNING, "Warning:failed"
                "to execute rtd3 registry command", test_case_id, script_id,
                "None", "None", loglevel, tbd)
                return False

        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " load bios secondary settings for rtd3 function"
            " as %s " %e, test_case_id, script_id, "None", "None", loglevel,
                tbd)                                                            # Write the exception error msg to log
            return False

    elif 'CS' in bios_setting_token_pf_pmf:                                     # if 'CS' string in  bios_setting_token
        try:
            cs_settings_TENSECPOWERBUTTONOVR=lib_set_bios.\
                lib_write_bios(lib_constants.TENSECPOWERBUTTONOVR,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of low power TEN SEC POWER BUTTON OVR in the bios
            cs_settings_PEPSATA=lib_set_bios.\
                lib_write_bios(lib_constants.PEPSATA,
                test_case_id, script_id, loglevel , tbd)                        #to set the option of low power PEP SATA in the bios

            cs_secondary_settings_all = [cs_settings_TENSECPOWERBUTTONOVR,
                                         cs_settings_PEPSATA]                   #To store all values in list

            cs_output_secondary_flag = True                                     #To initialize the cs_output_secondary_flag
            for cs_output_secondary in cs_secondary_settings_all:
                if 3 != cs_output_secondary:                                    #if option is not updated in bios
                    cs_output_secondary_flag = False                            #To set the cs_output_secondary_flag
                    break
                else:                                                           #if option is updated in bios
                    continue
            if True == cs_output_secondary_flag :                               #If cs_output_secondary_flag is equal to  True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                "successful for secondary cs settings in bios ", test_case_id,
                    script_id, "None", "None", loglevel, tbd)
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed to"
                " Update secondary cs settings in bios ", test_case_id,
                    script_id, "None", "None", loglevel, tbd)
                return False

        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
                " load bios secondary settings for cs function as %s " %e,
                test_case_id, script_id, "None", "None", loglevel, tbd)         # Write the exception error msg to log
            return False
    elif 'DISCONNECTED MOS' == bios_setting_token_pf_pmf or \
                    'CONNECTED MOS' == bios_setting_token_pf_pmf or\
                    "S0I3" == bios_setting_token_pf_pmf:                        # if 'DISCONNECTED MOS' or 'CONNECTED MOS' or 'S0I3' string in  bios_setting_token
        try:
            dmos_secondary_settings_all = []
            dmos_settings_CONNECTEDDEVICE=lib_set_bios.\
                lib_write_bios(lib_constants.CONNECTEDDEVICE,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of CONNECTED DEVICE serial I2C1 settings in the bios
            dmos_settings_SPI1CONTROLLER=lib_set_bios.\
                lib_write_bios(lib_constants.SPI1CONTROLLER,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of SPI1 CONTROLLER in the bios
            dmos_settings_FINGERPRINTSENSOR=lib_set_bios.\
                lib_write_bios(lib_constants.FINGERPRINTSENSOR,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of FINGER PRINT SENSOR in the bios
            dmos_settings_DPTFSUPPORT=lib_set_bios.\
                lib_write_bios(lib_constants.DPTFSUPPORT,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of DPTF SUPPORT in the bios
            curdir = lib_constants.SCRIPTDIR

            BOARDID = lib_read_bios.read_bios(lib_constants.BOARDID,            #to set the option of SDCARD SIDEBAND EVENTS in the bios
                test_case_id, script_id, curdir)
            BOARDID = str(BOARDID)
            if "RVP11" in BOARDID:
                pass
            else:
                dmos_settings_TENSECPOWERBUTTONOVR=lib_set_bios.\
                    lib_write_bios(lib_constants.TENSECPOWERBUTTONOVR,
                    test_case_id, script_id, loglevel, tbd)                     #to set the option of TEN SEC POWER BUTTON OVR in the bios
            dmos_settings_PEPSATA=lib_set_bios.\
                lib_write_bios(lib_constants.PEPSATA,
                test_case_id, script_id, loglevel, tbd)                         #to set the option of PEP SATA in the bios
            dmos_secondary_settings_all = [dmos_settings_CONNECTEDDEVICE,
                dmos_settings_SPI1CONTROLLER, dmos_settings_FINGERPRINTSENSOR,
                dmos_settings_DPTFSUPPORT]                                      #To store all values in the list

            if 'CONNECTED MOS' == bios_setting_token_pf_pmf or\
                            "S0I3" == bios_setting_token_pf_pmf:                # if only 'CONNECTED MOS' or 'S0I3'string in  bios_setting_token
                dmos_settings_CONNECTEDDEVICEI2C1=lib_set_bios.\
                    lib_write_bios(lib_constants.CONNECTEDDEVICEI2C1, 
                    test_case_id, script_id, loglevel, tbd)                     #to set the option of CONNECTED DEVICE serial I2C1 settings in the bios
                dmos_secondary_settings_all.\
                    append(dmos_settings_CONNECTEDDEVICEI2C1)
            else:
                pass
            dmos_output_secondary_flag = True                                   #To initialize the dmos_output_secondary_flag
            for dmos_output_secondary in dmos_secondary_settings_all:
                if 3 != dmos_output_secondary:                                  #if option is not updated in bios
                    dmos_output_secondary_flag = False                          #To set the dmos_output_secondary_flag
                    break
                else:                                                           #if option is updated in bios
                    continue
            if True == dmos_output_secondary_flag :                             #If dmos_output_secondary_flag is equal to  True
                library.write_log(lib_constants.LOG_INFO, "INFO: Update "
                "successful for secondary %s settings in bios "
                %(bios_setting_token_pf_pmf), test_case_id, script_id,
                    "None", "None", loglevel, tbd)
                return True
            else:                                                               #if option is not updated in bios
                library.write_log(lib_constants.LOG_WARNING, "Warning: Failed to"
                " Update secondary %s settings in bios "
                %(bios_setting_token_pf_pmf), test_case_id, script_id, "None",
                    "None", loglevel, tbd)
                return False
        except Exception as e:
            library.write_log(lib_constants.LOG_ERROR, "ERROR: Exception in"
            " load bios secondary settings for %s function as %s "
            %(bios_setting_token_pf_pmf, e), test_case_id, script_id,
                "None", "None", loglevel, tbd)                                          # Write the exception error msg to log
            return False
    else:                                                                       # if both RTD3/CS/DISCONNECTED MOS option is not present in token
        library.write_log(lib_constants.LOG_INFO, "INFO: Input token is "
            "incorrect", test_case_id, script_id, "None", "None", loglevel, tbd)# Write the exception error msg to log
        return False
################################################################################
# Function Name : rtd3_time_delay()
# Parameters    : no parameter
# Return Value  : True on success, False on failure
# Functionality : Send keys in background to handle the popup
################################################################################
def rtd3_time_delay():
    count = 0
    while count<5:
        SendKeys.SendKeys("{ESC}")                                              #sending Esc key
        time.sleep(1)                                                           # one sec delay
        count += 1
################################################################################

################################################################################
# Function Name : virtual_dc_settings()
# Parameters    : bios_setting_token_pf_pmf, test_case_id, script_id, loglevel,
#                  platform
# Return Value  : True on success, False on failure
# Functionality : Enabling of Virtual Battery
################################################################################

def virtual_dc_settings(bios_setting_token_pf_pmf,platform,test_case_id,
                        script_id,log_level):                                   # function for virtual dc enablement
    if "S0I3" == bios_setting_token_pf_pmf:
        port = utils.ReadConfig("TTK", "VIRTUAL BATTERY")
        if "FAIL" in port or 'NC' in port.upper() or 'NA' in port.upper():
            library.write_log(lib_constants.LOG_WARNING, "WARNING: config entry"
                " for port is not proper",test_case_id, script_id, "TTK", "None",
                log_level, platform)                                            #if failed to get config info, exit
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: config entry for "
                "port is %s in config.ini"% port, test_case_id,
                    script_id, "TTK", "None",log_level, platform)               #continue to remaining steps as config entry is fetched

            relay_set = library.ttk_set_relay("ON", [int(port)])
            pass_flag = 0
            if relay_set == pass_flag:                                              # relay action ON
                library.write_log(lib_constants.LOG_INFO, "INFO: TTK action "
                    "performed successfully", test_case_id, script_id, "TTK",
                        "None", log_level, platform)
                return True
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                    "to perform TTK action",test_case_id, script_id, "TTK",
                        "None", log_level,platform)
                return False
    else:
        return True

################################################################################
# Function Name  : xml_cli_load_bios_options
# Parameters     : bios_setting_token_pf_pmf, platform, test_case_id,
#                  script_id, log_level and tbd
# Functionality  : to load the bios default
# Return Value   : true if successful else false
################################################################################


def xml_cli_load_bios_options(bios_setting_token_pf_pmf, platform, test_case_id,
                              script_id, log_level="ALL", tbd="None"):

    try:
        if "CFL" == platform and \
           ("CONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
           "DISCONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
           "S0I3" == bios_setting_token_pf_pmf.upper() or
           "CS" == bios_setting_token_pf_pmf.upper()):
            cfl_u = lib_constants.CFL_U
            cfl_s_cnl_pch_h = lib_constants.CFL_S_CNL_PCH_H
            cfl_h_cnl_pch_h = lib_constants.CFL_H_CNL_PCH_H

            if platform == "CFL":
                string_in_bios = lib_constants.BOARD_NAME
                result1, board_name = lib_read_bios.\
                    xml_cli_read_bios(string_in_bios, test_case_id,
                                      script_id, log_level, tbd)
                if "CoffeeLake U" in board_name:
                    for string_in_bios in cfl_u:
                        ret = lib_set_bios.\
                            xml_cli_set_bios(string_in_bios, test_case_id,
                                             script_id, log_level, tbd)
                        if ret == 3:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                            "Bios option successfully set", test_case_id,
                            script_id, "None", "None", log_level, tbd)
                        else:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                            "Unable to set bios option", test_case_id,
                            script_id, "None", "None", log_level, tbd)
                            return False
                    return True

                if "CFL-S" in board_name or "CFL-H" in board_name:
                    string_in_bios = lib_constants.BOARD_PCH_NAME
                    result2, pch_name = lib_read_bios.\
                        xml_cli_read_bios(string_in_bios, test_case_id,
                                          script_id, log_level, tbd)
                    if "CFL-S" in board_name and "CNL PCH-H" in pch_name:
                        for string_in_bios in cfl_s_cnl_pch_h:
                            ret = lib_set_bios.\
                                xml_cli_set_bios(string_in_bios, test_case_id,
                                                 script_id, log_level, tbd)
                            if ret == 3:
                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Bios option successfully set",
                                test_case_id, script_id, "None", "None",
                                log_level, tbd)
                            else:
                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Unable to set bios option",
                                test_case_id, script_id, "None", "None",
                                log_level, tbd)
                                return False
                        return True

                    elif "CFL-H" in board_name or "CNL PCH-H" in pch_name:
                        for string_in_bios in cfl_h_cnl_pch_h:
                            ret = lib_set_bios.\
                                xml_cli_set_bios(string_in_bios, test_case_id,
                                                 script_id, log_level, tbd)
                            if ret == 3:
                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Bios option successfully set",
                                test_case_id, script_id, "None", "None",
                                log_level, tbd)
                            else:
                                library.write_log(lib_constants.LOG_INFO,
                                "INFO: Unable to set bios option",
                                test_case_id, script_id, "None", "None",
                                log_level, tbd)
                                return False
                        return True

            else:
                library.write_log(lib_constants.LOG_INFO,
                "INFO: Unable to set setting for platform", test_case_id,
                script_id, "None", "None", log_level, tbd)
                return False

        elif "CNL" == platform and \
             ("CONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
             "DISCONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
             "S0I3" == bios_setting_token_pf_pmf.upper() or
             "CS" == bios_setting_token_pf_pmf.upper()):
            cnl_cmos_dmos = lib_constants.CNL_CMOS_DMOS

            for string_in_bios in cnl_cmos_dmos:
                ret = lib_set_bios. \
                    xml_cli_set_bios(string_in_bios, test_case_id,
                                     script_id, log_level, tbd)
                if ret == 3:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Bios "
                    "option successfully set", test_case_id, script_id, "None",
                    "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO, "INFO: Unable "
                    "to set bios option", test_case_id, script_id, "None",
                    "None", log_level, tbd)
                    return False
            return True

        elif "KBL" == platform and \
             ("CONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
             "DISCONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
             "S0I3" == bios_setting_token_pf_pmf.upper() or
             "CS" == bios_setting_token_pf_pmf.upper()):
            string_in_bios = lib_constants.BOARD_NAME
            result, board_name = lib_read_bios. \
                xml_cli_read_bios(string_in_bios, test_case_id,
                                  script_id, log_level, tbd)

            board_name = board_name.strip()
            if "KABYLAKE ULT" == board_name.upper() or \
               "KABYLAKE ULX" == board_name.upper():
                kbl_u_y = lib_constants.KBL_U_Y
                for string_in_bios in kbl_u_y:
                    ret = lib_set_bios. \
                        xml_cli_set_bios(string_in_bios, test_case_id,
                                         script_id, log_level, tbd)
                    if ret == 3:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Bios option successfully set", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                    else:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Unable to set bios option", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                        return False

                if "KABYLAKE ULX" == board_name.upper():
                    string_in_bios = lib_constants.RVP3_SD_CARD
                    ret = lib_set_bios. \
                        xml_cli_set_bios(string_in_bios, test_case_id,
                                         script_id, log_level, tbd)
                    if ret == 3:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Bios option successfully set", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                    else:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Unable to set bios option", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                        return False
                return True

            elif "KABYLAKE HALO" == board_name.upper():
                kbl_h = lib_constants.KBL_H
                for string_in_bios in kbl_h:
                    ret = lib_set_bios. \
                        xml_cli_set_bios(string_in_bios, test_case_id,
                                         script_id, log_level, tbd)
                    if ret == 3:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Bios option successfully set", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                    else:
                        library.write_log(lib_constants.LOG_INFO,
                        "INFO: Unable to set bios option", test_case_id,
                        script_id, "None", "None", log_level, tbd)
                        return False
                return True

            elif "KABYLAKE DT" == board_name.upper():
                library.write_log(lib_constants.LOG_INFO, "INFO: CMOS\DMOS or "
                "S0i3 or CS cycling not applicable for DT boards",
                test_case_id, script_id, "None", "None", log_level, tbd)
                return False
            else:
                library.write_log(lib_constants.LOG_INFO,"INFO: Platform not "
                "handled", test_case_id, script_id, "None", "None", log_level,
                tbd)
                return False
        elif "KBLR" == platform.upper() and \
                ("CONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
                "DISCONNECTED MOS" == bios_setting_token_pf_pmf.upper() or
                "S0I3" == bios_setting_token_pf_pmf.upper() or
                "CS" == bios_setting_token_pf_pmf.upper()):
            kbl_r = lib_constants.KBL_R
            for string_in_bios in kbl_r:
                ret = lib_set_bios. \
                    xml_cli_set_bios(string_in_bios, test_case_id,
                                     script_id, log_level, tbd)
                if ret == 3:
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: Bios option successfully set",
                                      test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                else:
                    library.write_log(lib_constants.LOG_INFO,
                                      "INFO: Unable to set bios option",
                                      test_case_id,
                                      script_id, "None", "None", log_level, tbd)
                    return False
            return True

        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Pram not handle",
            test_case_id, script_id, "None", "None", log_level, tbd)
            return False

    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "Error: due to %s" % e,
        test_case_id, script_id, log_level, tbd)
    return False
