"""
Script Name  : lib_xmlcli.py
Version      : 1.0.0
Description  : To read and set the bios option using XmlCli tool.
Compatible   : 2.7x
"""

__author__ = 'smathikx/gpathirx/tnaidux/surabh1x/mmakhmox'

# Global Python Imports
try:
    import csv
    import os
    import re
    import shutil
    import sys
    import time
    import xml.etree.ElementTree as ET
    from xml.etree import ElementTree
except ImportError as ie:
    print((str(ie)))

# Local Python Imports
try:
    import library
    import lib_constants
    import utils
    sys.path.append(lib_constants.XMLCLI_TOOLPATH)
    import pysvtools.xmlcli.XmlCli as cli
except ImportError as ie:
    print((str(ie)))

# Global Variables
FREQUENCY = "DdrFreqLimit"
CHANNEL0 = "DisableDimmChannel0"
CHANNEL1 = "DisableDimmChannel1"
FREQ_AUTO = "Auto"
XMLCLI_PATH_LOG = os.path.join(lib_constants.XMLCLI_TOOLPATH, "pysvtools",
                               "xmlcli", "out", "PlatformConfig.xml")
STR_WINHWAPI = "winhwa"
STR_DONT_CARE = "don't care"
STR_BOOTCONFIGMENU = "Boot Configuration Menu"
STR_PLATFORM_INFO_MENU = "Platform Information Menu"
XML_CLI_ONLINE_LOGPATH = lib_constants.TOOLPATH + \
    r'\\pysvtools.xmlcli\pysvtools\\xmlcli\\out\\PlatformConfig.xml'
XML_CLI_OFFLINE_LOGPATH = lib_constants.TOOLPATH + \
    r'\\pysvtools.xmlcli\pysvtools\\xmlcli\\out\\PlatformConfig-offline.xml'
XMLCLI_LOGPATH = os.path.join(lib_constants.XMLCLI_TOOLPATH, "pysvtools",
                              "xmlcli", "out", "XmlCli.log")
STR_VERIFY_MSG = "VERIFY PASSED!"
STR_BIOSKNOBS = "biosknobs"
STR_OPTION = "option"
STR_TEXT = 'text'
STR_VALUE = 'value'
STR_OPTIONS = "options"
STR_KNOB = 'knob'
STR_NAME = 'name'
STR_SETUPPGPTR = "SetupPgPtr"
STR_CURRENT_VAL = "CurrentVal"
FLAG_SINGLE_OPT = ["0x00000000", "0x52EF", "0x30", "0x00"]
STR_XML_HEX_VALUE = '0x00000000'
STR_HEX_SYMBOL_X = 'x'
STR_HEX_SYMBOL_0 = '0'
NODE_ATTRIBUTE_OPTIONS = ["PowerLimit3DutyCycle", "PowerLimit3", "PowerLimit4",
                          "Custom1TurboActivationRatio", "CpuRatio",
                          "PcieRootPortGen3Uptp_0", "PcieRootPortGen3Dptp_0",
                          "RatioLimit1", "RatioLimit2",
                          "RatioLimit3", "RatioLimit4", "CpuFanSpeed",
                          "CpuTemp"]
STR_HEX_SPLIT = '0x0'
UNIQUE_DICT = {'memory rc version': 'Memory RC Version',
               'board id': 'Board ID', 'fab id': 'Fab ID', 'id': 'ID',
               'me fw version': 'ME FW Version', 'speed': 'Speed',
               'number of processors': 'Number of Processors',
               'ec fw version': 'EC FW Version',
               'lan phy revision': 'LAN PHY Revision',
               'igfx gop version': 'IGFX GOP Version'}
BIOS_FORM_OPTIONS_FILE = "comments.txt"
BIOS_INFO = "Bios Information"
FASP_INFO = "Fsp Information"
BOARD_INFO = "Board Information"
PROCESSOR_INFO = "Processor Information"
PCH_INFO = "Pch Information"
SYS_AGENT = "System Agent (SA) Configuration"
LAST_PARAM = "Debug Settings"
POWER_LEVEL = "Config Tdp Configurations"
CUSTOM_PARAM = "Custom Settings Nominal"
CPU_INFO = "Cpu Configuration"
CPU_SSE = "Cpu Smm Enhancement"
CPU_CONF = "Cpu Configuration"
MEM_CONF = "Memory Configuration"
GRAPHIC_CONF = "Graphics Configuration"
PTT_CONF = "Ptt Configuration"
COM_LIST = [BIOS_INFO, FASP_INFO, BOARD_INFO, PROCESSOR_INFO, PCH_INFO,
            SYS_AGENT, LAST_PARAM, POWER_LEVEL, CUSTOM_PARAM, CPU_INFO,
            CPU_SSE, CPU_CONF, MEM_CONF, GRAPHIC_CONF, PTT_CONF]
VERSION_TEMP = ['board id', 'memory rc version', 'fab id', 'me fw version',
                'id', 'number of processors', 'ec fw version', 'speed',
                'lan phy revision', 'igfx gop version']
STR_MEMORY_TIMINGS = "Memory Timings"
STR_MEMORY_CONFIGURATION = "MEMORY CONFIGURATION"
GREYED_OUT_OPTIONS = \
    ["HD AUDIO SUBSYSTEM CONFIGURATION SETTINGS", "GT SLICE DOMAIN",
     "GT UNSLICE DOMAIN", "AUDIO DSP NHLT ENDPOINTS CONFIGURATION",
     "STATICALLY SWITCHABLE BCLK CLOCK FREQUENCY CONFIGURATION",
     "AUDIO DSP FEATURE SUPPORT",
     "AUDIO DSP PRE/POST-PROCESSING MODULE SUPPORT"]
STR_STEP = "STEP "
STR_INTELADVMENU = "Intel Advanced Menu"
STR_INTELTESTMENU = "Intel Test Menu"
STR_TPV_EFI_DEV_MANAGER = "Tpv Efi Device Manager"
VERSION_INTELAM = ["Manufacturer", "Channel 0 Slot 0", "Memory Rc Version",
                   "Memory Timings", "Memory Frequency", "L1 Data Cache",
                   "L1 Instruction Cache", "L2 Cache", "L3 Cache", "L4 Cache",
                   "Microcode Revision", "Power Limit 1", "Power Limit 2",
                   "Memory Timings (Tcl-Trcd-Trp-Tras)", "Current Tpm Device",
                   "Me Firmware Status 1", "Me Firmware Status 2"]
SET_VALUES_OPTIONS = ['tCL', 'tRCDtRP', 'tRAS', 'tCWL', 'tFAW', 'tREFI',
                      'tRFC', 'tRRD', 'tRTP', 'tWTR', 'NModeSupport']
STR_NSH_FILE_NAME = "startup.nsh"
SDRIVE_PATH = "S:\\"
STR_EFI = "EFI"
STR_PYTHON_EFI_SCRIPT_FILE_NAME = "enable_disable_option.py"
STR_SET = "SET"
STR_READ = "READ"
POWER_AND_PERFORMANCE = "power & performance"
POWER_N_PERFORMANCE = "power n performance"

PYTHON_SCRIPT = '''
import sys
sys.path.append(r"FS0:\\EFI\\xmlcli")
import XmlCli as cli

if "UNCHECKED" == set_option_efi.strip().upper() and \\
   "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AttemptSecureBoot=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AttemptSecureBoot=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AttemptSecureBoot=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AttemptSecureBoot=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "acpi t-states" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TStatesEnable=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "acpi t-states" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TStatesEnable=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "acpi t-states" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TStatesEnable=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "acpi t-states" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TStatesEnable=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "pch temp" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "pch temp" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "pch temp" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "pch temp" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=1")
elif "bios_admin" == option_in_bios.strip().lower():
    cli.SetUserPwd("", set_option_efi)
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DTPM 2.0" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=2")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DTPM 2.0" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=2")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DTPM 1.2" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=1")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DTPM 1.2" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=1")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "PTT (FTPM)" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=3")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "PTT (FTPM)" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=3")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DISABLED" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=0")
elif "current selected tpm device" == option_in_bios.strip().lower() and \\
    "DISABLED" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshPdtUnlock=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshPdtUnlock=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshPdtUnlock=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshPdtUnlock=0")
elif "ENABLED" == set_option_efi.strip().upper() and \\
     "WWAN ENABLE" == option_in_bios.strip().upper():
    cli.CvProgKnobs("WwanEnable=1")
elif "DISABLED" == set_option_efi.strip().upper() and \\
     "WWAN ENABLE" == option_in_bios.strip().upper():
    cli.CvProgKnobs("WwanEnable=0")
elif "ENABLED" == read_option_efi.strip().upper() and \\
     "WWAN ENABLE" == option_in_bios.strip().upper():
    cli.CvReadKnobs("WwanEnable=1")
elif "DISABLED" == read_option_efi.strip().upper() and \\
     "WWAN ENABLE" == option_in_bios.strip().upper():
    cli.CvReadKnobs("WwanEnable=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "wake from thunderbolt(tm) devices" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TbtWakeupSupport=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "wake from thunderbolt(tm) devices" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TbtWakeupSupport=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "wake from thunderbolt(tm) devices" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TbtWakeupSupport=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "wake from thunderbolt(tm) devices" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TbtWakeupSupport=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "enable hibernation" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AcpiHibernate=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "enable hibernation" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AcpiHibernate=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "enable hibernation" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AcpiHibernate=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "enable hibernation" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AcpiHibernate=0")
elif "DISABLED" == set_option_efi.strip().upper() and \\
    "emmc 5.0 controller" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchScsEmmcEnabled=0")
elif "ENABLED" == set_option_efi.strip().upper() and \\
    "emmc 5.0 controller" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchScsEmmcEnabled=1")
elif "DISABLED" == read_option_efi.strip().upper() and \\
    "emmc 5.0 controller" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchScsEmmcEnabled=0")
elif "ENABLED" == read_option_efi.strip().upper() and \\
    "emmc 5.0 controller" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchScsEmmcEnabled=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "bluetooth sideband" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchHdAudioFeature_1=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "bluetooth sideband" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchHdAudioFeature_1=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "bluetooth sideband" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchHdAudioFeature_1=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "bluetooth sideband" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchHdAudioFeature_1=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "spi" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshSpiGpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "spi" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshSpiGpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "spi" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshSpiGpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "spi" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshSpiGpioAssign=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "uart0" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshUart0GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "uart0" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshUart0GpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "uart0" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshUart0GpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "uart0" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshUart0GpioAssign=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "uart1" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshUart1GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "uart1" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshUart1GpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "uart1" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshUart1GpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "uart1" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshUart1GpioAssign=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "i2c0" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c0GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "i2c0" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c0GpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "i2c0" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c0GpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "i2c0" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c0GpioAssign=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "i2c1" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c1GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "i2c1" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c1GpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "i2c1" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c1GpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "i2c1" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c1GpioAssign=0")
elif "CHECKED" == read_option_efi.strip().upper() and \\
     "i2c2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c2GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "i2c2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshI2c2GpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
     "i2c2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c2GpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
     "i2c2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshI2c2GpioAssign=0")
elif "gp_0" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp0GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp0GpioAssign=1")
elif "gp_1" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp1GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp1GpioAssign=1")
elif "gp_2" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp2GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp2GpioAssign=1")
elif "gp_3" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp3GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp3GpioAssign=1")
elif "gp_4" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp4GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp4GpioAssign=1")
elif "gp_5" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp5GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp5GpioAssign=1")
elif "gp_6" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp6GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp6GpioAssign=1")
elif "gp_7" == option_in_bios.strip().lower():
    try:
        cli.CvProgKnobs("PchIshGp7GpioAssign=0")
    except:
        cli.CvProgKnobs("PchIshGp7GpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "activate remote assistance process" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AmtCiraRequest=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "mebx hotkey pressed" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AmtbxHotKeyPressed=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "mebx selection screen" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AmtbxSelectionScreen=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "hide unconfigure me confirmation prompt" == option_in_bios.strip().lower():
    cli.CvReadKnobs("HideUnConfigureMeConfirm=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "mebx oem debug menu enable" == option_in_bios.strip().lower():
    cli.CvReadKnobs("MebxDebugMsg=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
     "unconfigure me" == option_in_bios.strip().lower():
    cli.CvReadKnobs("UnConfigureMe=0")
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "pch temp read" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "pch temp read" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "pch temp read" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "pch temp read" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=1")
elif "pch temp read" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=0, PCHTempReadEnable=1")

elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "vnns0i2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_0=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "vnns0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_0=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "vnns0i2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_0=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "vnns0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_0=1")
elif "vnns0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_0=0, ExternalVnnStateEnable_0=1")

elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "vnns0i3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_1=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "vnns0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_1=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "vnns0i3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_1=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "vnns0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_1=1")
elif "vnns0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_1=0, ExternalVnnStateEnable_1=1")

elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "vnns3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_2=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "vnns3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_2=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "vnns3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_2=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "vnns3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_2=1")
elif "vnns3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_2=0, ExternalVnnStateEnable_2=1")
    
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "vnns4" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_3=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "vnns4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_3=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "vnns4" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_3=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "vnns4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_3=1")
elif "vnns4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_3=0, ExternalVnnStateEnable_3=1")
    
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "vnns5" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_4=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "vnns5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_4=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "vnns5" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalVnnStateEnable_4=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "vnns5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_4=1")
elif "vnns5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalVnnStateEnable_4=0, ExternalVnnStateEnable_4=1")
    
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s0i2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_0=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_0=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s0i2" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_0=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_0=1")
elif "v1p05s0i2" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_0=0, ExternalV1p05StateEnable_0=1")

elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s0i3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_1=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_1=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s0i3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_1=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_1=1")
elif "v1p05s0i3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_1=0, ExternalV1p05StateEnable_1=1")

elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_2=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_2=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s3" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_2=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_2=1")
elif "v1p05s3" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_2=0, ExternalV1p05StateEnable_2=1")
    
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s4" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_3=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_3=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s4" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_3=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_3=1")
elif "v1p05s4" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_3=0, ExternalV1p05StateEnable_3=1")
    
elif "UNCHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s5" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_4=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_4=0")
elif "CHECKED" == set_option_efi.strip().upper() and \\
    "v1p05s5" == option_in_bios.strip().lower():
    cli.CvProgKnobs("ExternalV1p05StateEnable_4=1")
elif "CHECKED" == read_option_efi.strip().upper() and \\
    "v1p05s5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_4=1")
elif "v1p05s5" == option_in_bios.strip().lower():
    cli.CvReadKnobs("ExternalV1p05StateEnable_4=0, ExternalV1p05StateEnable_4=1")
    
else:
    pass
'''

SUT_S_DRIVE_PATH = "S:\\\\"
FILE_COPY_COMMAND = "xcopy /I /S /E /Y "
PYTHON_FEI_FOLDER = "S:\\EFI"
EFI_LOGPATH = "S:\\EFI\\xmlcli\\out\\XmlCli.log"
STR_S_DRIVE = 'S:'
STR_MOUNT_VAL = "mountvol " + STR_S_DRIVE + " /s"
NSH_FILE_EXTENSION = "nsh"
PY_FILE_EXTENSION = "py"
XML_CLI_LOG_MESG = "Verify Passed!"
XML_CLI_LOG_MESG_PWD_ERR = "New password is not strong enough!"
XML_CLI_LOG_MESG_PWD_SET = "New password is updated successfully"
OPTION_AHCI = 'AHCI'
AHCI_CHECKLIST = \
    {'AHCI': '0x0',
     'SetupPgPtr': 'Intel Advanced Menu/PCH-IO Configuration/'
                   'SATA And RST Configuration/SATA Mode Selection',
     'name': 'SataInterfaceMode',
     'CurrentVal': '0x00',
     'Intel RST Premium With Intel Optane System Acceleration': '0x1'}
SATA_MODE_SELECTION_LIST = ['MSIX', 'MSI', 'LEGACY']
xml_cli_tool_path = r"C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli"
xml_cli_out_folder_path = r"C:\\Testing\\GenericFramework\\tools\\pysvtools." \
                          r"xmlcli\\pysvtools\\xmlcli\\out"
PLATFORM_INFORMATION_BIOS_VALUES = ["L1 Data Cache", "L1 Instruction Cache",
                                    "L2 Cache", "Me Firmware Version",
                                    "Me Firmware Mode", "Me Firmware Sku",
                                    "L3 Cache", "L4 Cache", "Id",
                                    "Cnvi Present"]
FORM_OPTIONS = ["driver health manager", "intel test menu", "configtdp level2",
                "configtdp nominal", "config tdp configurations",
                "configtdp level1", "cira configuration", "asf configuration",
                "secure erase configuration", "oem flags settings", "gt vr settings",
                "mebx resolution settings", "asf support", "system agent vr settings",
                "usb provisioning of amt", "cpu vr settings",
                "ia vr settings", "pch thermal throttling control", "mipi camera configuration"]
SKIP_DEPEX_STATUS_OPTIONS = ["primary display", "configurable tdp boot mode"]

UNIQ_PARAM_DICT = {"soundwire" : "SoundWire"}


def xmlcli_access_verify(tc_id, script_id,  log_level, tbd):

    """
    Function Name     : xmlcli_access_verify
    Parameters        : tc_id, script_id, log_level, tbd
    Functionality     : To verify the xmlcli support is enabled or not
    Function Invoked  : library.write_log()
    Return Value      : return True on success and False on Failure
    """
    
    try:
        cli.clb._setCliAccess(STR_WINHWAPI)
        xmlcli_enablement_check = cli.clb.ConfXmlCli()                          # Reads the XMLCLI enablement status on the current BIOS

        if xmlcli_enablement_check == lib_constants.RETURN_SUCCESS:             # Checks for the Intel CCG SDK and XMLCLI support enablement check
            library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli support "
                              "enabled in current BIOS", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: XmlCli "
                              "support not enabled in current BIOS", tc_id,
                              script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "xmlcli_access_verify() due to %s " % e, tc_id, 
                          script_id, lib_constants.TOOL_XMLCLI, 
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def xml_log_creation(log_path, tc_id, script_id,  log_level, tbd):

    """
    Function Name     : xml_log_creation
    Parameters        : log_path, tc_id, script_id,  log_level, tbd
    Functionality     : To create online and offline xml logs
    Function Invoked  : library.write_log()
    Return Value      : return True on success and False on Failure
    """

    try:
        if os.path.exists(XML_CLI_ONLINE_LOGPATH):                              # If old logs exits it will remove to create a new one
            os.remove(log_path)
            library.write_log(lib_constants.LOG_INFO, "INFO: Cleared old XML "
                              "logs", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
        cli.clb._setCliAccess(STR_WINHWAPI)
        result_save_xml = cli.savexml(XML_CLI_ONLINE_LOGPATH)                   # Command to save the offline XML file


        if lib_constants.RETURN_SUCCESS == result_save_xml and \
           os.path.exists(XML_CLI_ONLINE_LOGPATH):                              # Checks if offline xml is created and offline path exists ot not
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully run "
                              "command to generate log and log exist in path", 
                              tc_id, script_id, lib_constants.TOOL_XMLCLI, 
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "run command to save log", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI, 
                              lib_constants.STR_NONE, log_level, tbd)
            return False                                                        # If result_save_xml is failed to return output
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "xml_log_creation() due to %s " % e, tc_id, 
                          script_id, lib_constants.TOOL_XMLCLI, 
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def parse_offline_xml(string_in_bios, tc_id, script_id, log_level, tbd):

    """
    Function Name     : parse_offline_xml
    Parameters        : string_in_bios, option_in_bios, tc_id, script_id,
                        log_level, tbd
    Functionality     : To parse offline xml
    Function Invoked  : library.write_log()
    Return Value      : return True on success and False on Failure
    """

    try:
        checklist_offline = {}                                                  # Assign empty dict to store Checklist values from offline XML

        xml_log_creation_check_flag = xml_log_creation(XML_CLI_ONLINE_LOGPATH,
                                                       tc_id, script_id, 
                                                       log_level, tbd)
        if xml_log_creation_check_flag is False:
            return False, None                                                  # Returns False, if offline XML log creation failed

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as offline_xml_file:
            tree = ElementTree.parse(offline_xml_file)

        root = tree.getroot()
        knob = 0
        options = 0

        for child in root:
            if str(child.tag).lower() == STR_BIOSKNOBS:                         # Checks in the Offline XML file if child tag has kw biosknobs
                for node in child.iter():
                    if knob == lib_constants.ONE:                               # Checks if the knob value is ONE
                        if str(node.tag) == STR_OPTION:                         # Checks if the node tag value is option
                            checklist_offline[node.attrib[STR_TEXT]] = \
                                node.attrib[STR_VALUE]                          # Appends the hexa options availble in the offline xml under the bios to the checklist
                        elif str(node.tag) == STR_OPTIONS:                      # Checks if the node tag value is options
                            options = 1
                        else:
                            knob = 0
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Checked and Assigned values of "
                                              "bios_path, options and bios_"
                                              "name", tc_id, script_id, 
                                              lib_constants.TOOL_XMLCLI, 
                                              lib_constants.STR_NONE, 
                                              log_level, tbd)
                            return True, checklist_offline                      # Returns True and checklist from the offlinexml file

                    if str(node.tag) == STR_KNOB:
                        if STR_NAME in list(node.attrib.keys()) and \
                           STR_SETUPPGPTR in list(node.attrib.keys()):
                            bios_str = "/".join([item.strip(' ') for item in
                                                 str(node.attrib
                                                     [STR_SETUPPGPTR])
                                                 .split('/')])
                            if str(string_in_bios.replace(" ", "")).\
                               strip().lower() == \
                                    str(bios_str.replace(" ", "")).\
                                    strip().lower():                            # Checks if the input string_in_bios and bios_str from offlineXML matches
                                knob = 1
                                checklist_offline[STR_NAME] = \
                                    node.attrib[STR_NAME]                       # Assign the node attribute to name value in the checklist
                                checklist_offline[STR_SETUPPGPTR] = \
                                    node.attrib[STR_SETUPPGPTR]                 # Assign the bios string to SetupPgPtr bios string in the checklist
        return False, checklist_offline
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "parse_offline_xml() due to %s " % e, tc_id, 
                          script_id, lib_constants.TOOL_XMLCLI, 
                          lib_constants.STR_NONE, log_level, tbd)
        return False, False


def check_name_online_log(common_checklist, tc_id, script_id, log_level, tbd):

    """
    Function Name     : check_name_online_log
    Parameters        : common_checklist, tc_id, script_id, log_level, opt
    Functionality     : To set the bios
    Function Invoked  : library.write_log(),xml_log_creation()
    Return Value      : return True on success and False on Failure
    """

    try:
        xml_log_creation_check_flag = xml_log_creation(XML_CLI_ONLINE_LOGPATH,
                                                       tc_id, script_id, 
                                                       log_level, tbd)
        if xml_log_creation_check_flag is False:
            return False, None                                                  # Returns False, if online XML log creation failed

        if len(common_checklist) != lib_constants.ZERO:                         # Check if the list is not empty
            library.write_log(lib_constants.LOG_INFO, "INFO: Common_checklist "
                              "have been verified", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Common_"
                              "checklist is empty", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False, None

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as f:
            tree = ElementTree.parse(f)

        root = tree.getroot()

        for child in root:
            if child.tag.lower() == STR_BIOSKNOBS:
                for node in child.iter():                                       # Iterate all the nodes in the XML file
                    if node.tag == STR_KNOB:
                        if common_checklist[STR_NAME].lower() == \
                                node.attrib[STR_NAME].lower():                  # Checks the common_checklist name with the online log if its present or not
                            common_checklist[STR_CURRENT_VAL] = \
                                node.attrib[STR_CURRENT_VAL]                    # Assign the name to common_checklist after comparing
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Checks and compares the name "
                                              "values of bios", tc_id,
                                              script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)
                            return True, common_checklist                       # Returns True and the checklist
        return False, None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "check_name_online_log() due to %s" % e, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False, None


def parse_online_xml(option_in_bios, common_checklist, tc_id, script_id,
                     log_level, tbd):

    """
    Function Name     : parse_online_xml
    Parameters        : option_in_bios, common_checklist, tc_id, script_id,
                        log_level, opt
    Functionality     : To parse online xml
    Function Invoked  : library.write_log(), check_single_bios_option(),
                        check_bios_path(), read_multiple_bios_options(),
                        xml_log_creation()
    Return Value      : return True on success and False on Failure
    """

    try:
        flag_single_opt = ''
        flag_mul_opt = ''
        flag_bios_path = ''

        xml_log_creation_check_flag = xml_log_creation(XML_CLI_ONLINE_LOGPATH,
                                                       tc_id, script_id,
                                                       log_level, tbd)
        if xml_log_creation_check_flag is False:
            return False, None                                                  # Returns False, if online XML log creation failed

        if len(common_checklist) == lib_constants.ZERO:
            return False, None

        if option_in_bios == lib_constants.STR_NONE:
            flag_bios_path, current_bios_value = \
                check_bios_path(common_checklist, tc_id, script_id,
                                log_level, tbd)                                 # Returns true, if bios path is valid, else False
        elif "," in option_in_bios:                                             # Checks when multiple bios option is passed
            option_in_bios = \
                [item.strip() for item in option_in_bios.split(',')]            # Splits the multiple options and converting into list
            flag_mul_opt = \
                read_multiple_bios_options(option_in_bios, common_checklist,
                                           tc_id, script_id, log_level, tbd)    # Checks for multiple BIOS option check
        else:
            flag_single_opt = \
                check_single_bios_option(option_in_bios, common_checklist,
                                         tc_id, script_id, log_level, tbd)      # Returns the True if current bios and option to compare is same, else False

        if flag_single_opt in FLAG_SINGLE_OPT or \
           flag_bios_path in FLAG_SINGLE_OPT:                                   # Checks whether flag_single_opt or flag_bios_path is exists in FLAG_SINGLE_OPT
            if flag_single_opt:                                                 # Condition will be true, if flag_single_opt(string data type) value is exists in FLAG_SINGLE_OPT
                return flag_single_opt
            else:
                return flag_bios_path                                           # Returns flag_bios_path, If flag_single_opt is not exists, but flag_bios_path string value exists in FLAG_SINGLE_OPT
        elif flag_single_opt is True or flag_mul_opt is True or \
             flag_bios_path is True or STR_XML_HEX_VALUE == flag_bios_path:
            if STR_XML_HEX_VALUE == flag_bios_path:
                return STR_XML_HEX_VALUE                                        # Returns '0x00000000' hex value if flag_bios_path is same as '0x00000000'
            elif option_in_bios == lib_constants.STR_NONE:
                return True, current_bios_value                                 # Returns True and bios value, if option to compare is none
            else:
                if str(option_in_bios).upper() in SATA_MODE_SELECTION_LIST:     #Search for MSIX, MSI, LEGACY value to current_bios_value
                    state = check_single_bios_option(OPTION_AHCI,
                                                     AHCI_CHECKLIST, tc_id,
                                                     script_id, log_level,
                                                     tbd)                       #check for AHCI bios path
                    if True == state:
                        return False, None                                      # Return false if AHCI is enabled
                    else:
                        return True, option_in_bios                             # Returns True and option to compare, if option to compare is not none
                else:
                    return True, option_in_bios
        else:
            return False, None                                                  # Returns False, if bios option comparison un-successful
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "parse_online_xml() due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)               # logs if any exception occurs
        return False, False


def check_single_bios_option(option_in_bios, common_checklist, tc_id,
                             script_id, log_level, tbd):

    """
    Function Name     : check_single_bios_option
    Parameters        : option_in_bios, common_checklist, tc_id, script_id,
                        log_level, tbd
    Functionality     : To check single bios option
    Function Invoked  : library.write_log()
    Return Value      : return True on success and False on Failure
    """

    try:
        if " & " in option_in_bios:
            option_in_bios = option_in_bios.replace("&", "N")

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as file_read:                   # Reads the online xml path
            tree = ElementTree.parse(file_read)

        root = tree.getroot()                                                   # Get the xml root object using getroot() method
        knob = 0
        common_checklist_temp = \
            {key.title(): value for key, value in common_checklist.items()}

        for child in root:
            if str(child.tag).lower().strip() == STR_BIOSKNOBS:                 # Compares the child bios string with the online xml knobs
                for node in child.iter():
                    if STR_NAME in list(node.attrib.keys()) and \
                       STR_CURRENT_VAL in list(node.attrib.keys()):                   # Checks whether name and current val string in the child node
                        if common_checklist[STR_NAME] == node.attrib[STR_NAME]:
                            cur_val = node.attrib[STR_CURRENT_VAL].\
                                split(STR_HEX_SYMBOL_X)                         # Splits the current value from hex suffix
                            pad_zero = str(cur_val[-1])                         # Converting the integer to string

                            if STR_HEX_SYMBOL_0 in pad_zero[0]:
                                pad_strip = pad_zero.lstrip(STR_HEX_SYMBOL_0)   # Strips the STR_HEX_SYMBOL_0
                                if pad_strip == '':
                                    pad_zero = STR_HEX_SYMBOL_0
                                    cur_val[-1] = pad_zero
                                else:
                                    cur_val[-1] = pad_strip

                            cur_val = STR_HEX_SYMBOL_X.\
                                join([value for value in cur_val])              # Reads the current value of a BIOS
                            checklist_dict = {}

                            for key, val in common_checklist_temp.items():
                                checklist_dict[re.sub('\s+', ' ', str(key))] = \
                                    re.sub('\s+', ' ', str(val))                # Checks for the bios option

                            if option_in_bios.isalpha():
                                checklist_dict_value = checklist_dict.\
                                    get(option_in_bios.title())
                                if checklist_dict_value is None:
                                    library.write_log(lib_constants.LOG_WARNING,
                                                      "WARNING: Bios value to "
                                                      "check is invalid and it "
                                                      "does not exist in the "
                                                      "XMLCLI logs", tc_id,
                                                      script_id,
                                                      lib_constants.TOOL_XMLCLI,
                                                      lib_constants.STR_NONE,
                                                      log_level, tbd)
                                    return False
                                elif checklist_dict_value.lower() == \
                                        cur_val.lower():                        # Checks BIOS option to compare and current bios title is same or not
                                    return True
                                else:
                                    return False
                            else:
                                hex_flag = False
                                if STR_HEX_SYMBOL_X in option_in_bios.lower():  # Compare hex symbol of current bios option with the hex value suffix 'x'
                                    if STR_HEX_SYMBOL_0 == option_in_bios.\
                                       lower().split(STR_HEX_SYMBOL_X)[0]:
                                        hex_option_in_bios = \
                                            option_in_bios.upper()              # Convert the hex_option_in_bios into upper case
                                        hex_flag = True

                                if not hex_flag:
                                    try:
                                        try:
                                            if (checklist_dict[option_in_bios.
                                               title()]).lower == \
                                               cur_val.lower():                 # Checks BIOS option to compare and current bios hex value is same or not
                                                return True
                                        except:
                                            hex_option_in_bios = \
                                                hex(int(option_in_bios))
                                            hex_option_in_bios = \
                                                str(hex_option_in_bios).upper()
                                            if hex_option_in_bios == \
                                                    cur_val.upper():            # Checks BIOS option to compare and current bios hex value is same or not
                                                return True
                                        hex_option_in_bios = \
                                            hex(int(option_in_bios))            # Converting the hex value of option_in_bios to int
                                        hex_option_in_bios = \
                                            str(hex_option_in_bios).upper()     # Converting the hex value of option_in_biosto string upper case

                                    except:
                                        option_in_bios = re.sub('\s+', ' ',
                                                                option_in_bios) # Reads the BIOS option by strip its value
                                        hex_option_in_bios = \
                                            str(checklist_dict[option_in_bios.
                                                title()]).upper()               # Reads the option_in_bios from checklist dictionary to read hex value of current enabled BIOS option
                                        hex_option_in_bios = re.sub('\s+', ' ',
                                                            hex_option_in_bios) # Checks for the hex_option_in_bios

                                if hex_option_in_bios == str(cur_val).upper():
                                    if cur_val in FLAG_SINGLE_OPT:
                                        return cur_val                          # Returns the current bios value
                                    else:
                                        return True
                                else:
                                    return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "check_single_bios_option() due to %s" % e_obj,
                          tc_id, script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)               # logs if any exception occurs
        return False, False


def check_bios_path(common_checklist, tc_id, script_id, log_level, tbd):

    """
    Function Name     : check_bios_path
    Parameters        : common_checklist, tc_id, script_id, log_level, tbd
    Functionality     : To check bios path
    Function Invoked  : library.write_log(), xml_log_creation()
    Return Value      : return True on success and False on Failure
    """

    try:
        value_in_bios = None
        xml_log_creation_check_flag = xml_log_creation(XML_CLI_ONLINE_LOGPATH,
                                                       tc_id, script_id,
                                                       log_level, tbd)

        if xml_log_creation_check_flag is False:
            return False, None                                                  # Returns False, if online XML log creation failed

        if len(common_checklist) == lib_constants.ZERO:                         # If common checklist is zero, then bios path is not found in online xml log
            return False, None

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as file_read:
            tree = ElementTree.parse(file_read)                                 # Reads the online xml path log path

        root = tree.getroot()                                                   # Reads the XML tree using getroot() XML element tree method
        knob = 0

        for child in root:
            if str(child.tag).lower() == STR_BIOSKNOBS:                         # Checks whether child tag has BIOSKNOBS string
                for node in child.iter():                                       # Iterates through child node from root node of an online XML log file
                    if str(node.tag) == STR_KNOB:                               # Checks the common_checklist name with the online log if its present or not
                        if common_checklist[STR_NAME] == \
                                node.attrib[STR_NAME]:                          # Checks for the name string in the common checklist dictionary of particular bios path
                            if node.attrib[STR_NAME] in NODE_ATTRIBUTE_OPTIONS \
                               or node.attrib[STR_NAME] in SET_VALUES_OPTIONS:
                                return True, node.attrib[STR_CURRENT_VAL]
                            else:
                                current_bios_value = (STR_HEX_SYMBOL_0 +
                                                      STR_HEX_SYMBOL_X).\
                                    join(node.attrib[STR_CURRENT_VAL].
                                         split(STR_HEX_SPLIT))
                                for key, value in common_checklist.items():
                                    if current_bios_value.lower().strip() == \
                                            key.lower().strip():                # Compare and assign its BIOS value or key into value_in_bios
                                        value_in_bios = value.tilte()
                                        return True, value_in_bios
                                    elif current_bios_value.lower().strip() ==\
                                            value.lower().strip():
                                        value_in_bios = key.title()
                                        return True, value_in_bios
        return False, None
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "check_bios_path() due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)               # logs if any exception occurs
        return False, False


def read_multiple_bios_options(option_in_bios, checklist_offline, tc_id,
                               script_id, log_level, tbd):

    """
    Function Name     : read_multiple_bios_options
    Parameters        : option_in_bios, checklist_offline, tc_id, script_id,
                        log_level, tbd
    Functionality     : To check multiple option of bios
    Function Invoked  : library.write_log()
    Return Value      : return True on success and False on Failure
    """

    try:
        if len(checklist_offline) != lib_constants.ZERO:                        # Check if the list is not empty
            library.write_log(lib_constants.LOG_INFO, "INFO: Common_checklist "
                              "have been verified", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
        else:                                                                   # Return False if Checklist is empty
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Common_"
                              "checklist is empty", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE,log_level, tbd)
            return False

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as file_read:
            tree = ElementTree.parse(file_read)

        root = tree.getroot()
        knob = 0
        checklist_online = {}

        for child in root:
            if str(child.tag).lower() == STR_BIOSKNOBS:                         # Filter it if the child has only biosknobs tag
                for node in child.iter():
                    if knob == 1:                                               # If knob value is one
                        if str(node.tag) == STR_OPTION:
                            checklist_online[node.attrib[STR_TEXT]] = \
                                node.attrib[STR_VALUE]                          # Assign the XML value to the checklist
                        elif str(node.tag) == STR_OPTIONS:
                            continue                                            # If the node tag header is options it will go next iteror to find the options below it
                        else:
                            break                                               # After finding options it will break the loop
                    if str(node.tag) == STR_KNOB:
                        if checklist_offline[STR_NAME] == \
                           node.attrib[STR_NAME]:                               # Checks the common_checklist name with the online log if its present or not
                            knob = 1

        if len(option_in_bios) <= 1:                                            # If len of the option_list is one it will return True
            return True

        checklist_online_temp = \
            {key.title(): value for key, value in checklist_online.items()}

        amp_flag = False
        for key, value in checklist_online_temp.items():
            if " N " in key or " N " in value:                                  # Checks if any "?" in the checklist_online_temp of bios and set flag
                amp_flag = True

        final_flag = False
        for item in option_in_bios:
            if "&" in str(item):                                                # Checks if any "&" in option_in_bios and set flag
                final_flag = True

        option_in_bios_temp = []
        if amp_flag is True and final_flag is True:                             # Checks if amp_flag and final_flag flag is True
            for item in option_in_bios:
                if "&" in str(item):
                    replace_value = str(item).replace("&", "n")                 # If "&" in option_in_bios replaces with "?" and append to option_in_bios_temp
                    option_in_bios_temp.append(replace_value)
                else:
                    option_in_bios_temp.append(item)

            for item in option_in_bios_temp:
                if item.title() not in checklist_online_temp:             # If checklist_online_temp doest have item key in option_in_bios_temp
                    return False
            return True
        else:
            for item in option_in_bios:
                if item.title() not in checklist_online_temp:             # If checklist_online_temp doest have item key in option_in_bios_temp
                    return False
            return True
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "read_multiple_bios_options() due to %s" % e,
                          tc_id, script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False, False                                                     # Return False when Exception occurs and logs the message


def read_bios_platform_information(string_in_bios, tc_id, script_id,
                                   log_level, tbd):

    """
    Function Name     : read_bios_platform_information
    Parameters        : string_in_bios, tc_id, script_id, log_level, opt
    Functionality     : To read BIOS platform information
    Function Invoked  : library.write_log(), xml_log_creation()
    Return Value      : return True on success and False on Failure
    """

    try:
        if '/' not in string_in_bios:
            child_bios_string = string_in_bios
        else:
            string_in_bios = string_in_bios.split('/')
            parent_bios_string, child_bios_string = \
                string_in_bios[-2], string_in_bios[-1]                          # Slice to extract the parent and child string to compare

        if child_bios_string.lower() in FORM_OPTIONS:
            library.write_log(lib_constants.LOG_INFO, "INFO: '%s' Form option "
                              "is available in BIOS Page" % child_bios_string,
                              tc_id, script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return True, True

        unique_dict = UNIQUE_DICT
        xml_log_creation_check_flag = xml_log_creation(XML_CLI_ONLINE_LOGPATH,
                                                       tc_id, script_id,
                                                       log_level, tbd)

        if xml_log_creation_check_flag is False:
            return False, None                                                  # Returns False, if online XML log creation failed

        with open(XML_CLI_ONLINE_LOGPATH, 'rt') as \
                online_log_file:                                                # Reads the XML cli online log file
            content = online_log_file.read()

        re_find = re.finditer(r'<!--(.*?)-->', content)                         # re_find object which holds the list of BIOS platform information menu
        log = lib_constants.SCRIPTDIR + lib_constants.PATH_SEP + \
            BIOS_FORM_OPTIONS_FILE                                              # Comments.txt log file path

        if os.path.exists(log):
            os.remove(log)                                                      # Removes the existing BIOS form "comments.txt" log file

        os.chdir(lib_constants.SCRIPTDIR)
        for data in re_find:
            with open(BIOS_FORM_OPTIONS_FILE, "a") as file_write:
                file_write.writelines(str(data.groups(1)[0]).strip() + "\n")    # Appends the BIOS form options into comment.txt log file

        comment_list = COM_LIST                                                 # Get the BIOS platform level COM informations
        if parent_bios_string.title().strip() in comment_list:                  # Compares the parent bios string wiht comment list values
            comment_list.remove(parent_bios_string.title().strip())

        comment_dict = {}
        comment_list_data = []
        match_found = lib_constants.ZERO                                        # Match found initialisation value
        stop = lib_constants.ZERO                                               # Match check stop variable initialisation

        with open(BIOS_FORM_OPTIONS_FILE, "r")as file_read:                     # Reads the comments.txt BIOS form option file
            for line in file_read:
                if stop == lib_constants.ONE:
                    break
                if match_found == lib_constants.ZERO:
                    if parent_bios_string.title() in line.title():              # Compare the parent string and BIOS form option string
                        match_found = lib_constants.ONE
                elif match_found == lib_constants.ONE:
                    if ":" in line:
                        comment_dict[line.split(":")[0].strip()] = \
                            ":".join([data for data in line.strip().split(":")
                                     [1:]])                                     # Split the string based on : and appends in the comment_list_data list
                        comment_list_data.append(line)
                    elif parent_bios_string.upper().strip() == \
                            line.upper().strip():                               # if the parent bios string appears again in the line without ":"
                        continue
                    else:
                        for data in comment_list:
                            if data in line.title().strip():                    # If data in comment_list list, searching stop variable will be set to one
                                stop = lib_constants.ONE

        comment_dict_temp = {key.title(): value for key, value in
                             comment_dict.items()}

        if child_bios_string.lower() in VERSION_TEMP:                           # Checks the firmware temperature details
            child_bios_string = unique_dict.get(child_bios_string.lower())
            result = comment_dict.get(child_bios_string)
        elif STR_MEMORY_TIMINGS == child_bios_string.strip().title():           # Compares the child string with BIOS Memory timings string option
            result = comment_dict.get(child_bios_string.title())
            for key, value in comment_dict.items():
                if child_bios_string.title() in key:
                    result = value
                    break
                else:
                    result = None
        elif STR_MEMORY_CONFIGURATION in parent_bios_string.upper():
            if "&" in child_bios_string:
                child_option_in_bios = child_bios_string.replace("&", "?")      # Replaces the "&", "?" child_option_in_bios
            for value in comment_list_data:
                if child_bios_string.upper() in value.upper():
                    result = value.split(":")[1].strip()
                    break
                else:
                    result = None
        else:
            result = comment_dict_temp.get(child_bios_string.title())           # Reads the child_bios_string from comment_dict using .get dict method

        if result and (result is not None):
            return True, result
        else:
            return False, None
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "read_bios_platform_information() due to %s" % e,
                          tc_id, script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)               # logs if any exception occurs
        return False, False


def read_bios_xmlcli(string_in_bios, option_in_bios, step, tc_id, script_id,
                     log_level, tbd):

    """
    Function Name     : read_bios_xmlcli
    Parameters        : string_in_bios, option_in_bios, step, ifwi_file, tc_id,
                        script_id, log_level, tbd
    Functionality     : To Read the BIOS information using XMLCLI tool
    Function Invoked  : library.write_log(), utils.read_config_file(),
                        parse_offline_xml(), parse_online_xml()
                        read_bios_platform_information(),xmlcli_access_verify(),
                        mount_drive_to_xmlcli_bios()
    Return Value      : return True on success or False on failure
    """

    try:
        xmlcli_enablement_check = xmlcli_access_verify(tc_id, script_id,
                                                       log_level, tbd)          # Checks whether XMLCLI Support is enabled or not, also checks whether Intel CCG SDK is Installed or not
        if xmlcli_enablement_check is False:
            return False, False

        if step.lower().strip() == \
                lib_constants.STR_MOUNT_DRIVE.lower().strip():
            mount_drive_to_xmlcli_bios_check = \
                mount_drive_to_xmlcli_bios(tc_id, script_id, log_level, tbd)    # Calls the mount drive function to verfiy the EFI shell mode BIOS executed log
            if mount_drive_to_xmlcli_bios_check is True:
                return True, lib_constants.STR_PASS
            else:
                return False, False
        else:
            if STR_STEP in option_in_bios.upper():
                step_no = option_in_bios.split(" ")[-1]
                option_in_bios = utils.read_from_Resultfile(step_no)            # To read step value from result.ini
            string_in_bios = string_in_bios.lower()
            string_in_bios = string_in_bios.replace(POWER_AND_PERFORMANCE,
                                                    POWER_N_PERFORMANCE)        # Temporary fix for handling xmlcli related tool issue
            string_in_bios = string_in_bios.split("/")
            for string in string_in_bios:
                if string.upper() in GREYED_OUT_OPTIONS:                        # checks the existence of string in bios in greyed out options
                    string_in_bios.remove(string)
            string_in_bios = "/".join(string_in_bios).title().strip()           # Splitting string in bios after removing GREYED_OUT_OPTIONS
            string_in_bios_param = [bios_string.lower().strip() for
                                    bios_string in string_in_bios.split('/')]
            for bios_check in lib_constants.EFI_OPTION_LIST:
                if bios_check.lower().strip() in string_in_bios_param:
                    xml_cli_bios_security_option_efi_check = \
                        xmlcli_bios_security_option_efi(string_in_bios,
                                                        option_in_bios, step,
                                                        tc_id, script_id,
                                                        log_level, tbd)

                    if xml_cli_bios_security_option_efi_check is True:
                        return True, lib_constants.STR_PASS
                    else:
                        return False, lib_constants.STR_FAIL

            if STR_BOOTCONFIGMENU.title() in string_in_bios.title():            # Checks for the BOOt configuration menu BIOS Form
                string_in_bios = "/".join([string_in_bios.split('/')[itr].
                                           strip() for itr in range(3,
                                           len(string_in_bios.split('/')))])    # If bios_path string contains "Boot Configuration Menu" it will split and remove first two strings
                if STR_STEP.upper() in option_in_bios.upper():                  # check for the Step keyword in bios string
                    step_no = option_in_bios.split(" ")[-1]
                    option_in_bios = utils.read_from_resultfile(step_no,
                                                                tc_id,
                                                                script_id)
                    if "'d" or "'D" in option_in_bios:
                        option_in_bios = \
                            str(int(round(float(option_in_bios.replace("'d",
                                                                       "")))))
            elif STR_PLATFORM_INFO_MENU.title() in string_in_bios or \
                STR_INTELADVMENU.title() in string_in_bios or \
                STR_INTELTESTMENU.title() in string_in_bios or \
                STR_TPV_EFI_DEV_MANAGER.title() in string_in_bios.title():      # Checks for the Intel Advanced Menu or Intel Test Menu or Tpv Efi Device Manager BIOS Form
                string_in_bios = "/".join([string_in_bios.split('/')[itr].
                                          strip() for itr in range(2,
                                          len(string_in_bios.split('/')))])     # If bios_path string contains Intel Advanced Menu or Intel Test Menu or Tpv Efi Device Manager, it will split and remove first two strings
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                  "Invalid BIOS path", tc_id, script_id,
                                  lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)       # Logs message for Invalid bios path
                return False, False

            if STR_PLATFORM_INFO_MENU.title() in string_in_bios.title() or \
               STR_INTELADVMENU.title() in string_in_bios.title() or \
               STR_INTELTESTMENU.title() in string_in_bios.title() or \
               STR_TPV_EFI_DEV_MANAGER.title() in string_in_bios.title() or \
               STR_BOOTCONFIGMENU in string_in_bios.title():
                search_string = string_in_bios.split("/")
                for i in range(0, len(search_string)):
                    if i == len(search_string)-1:
                        search_string = str(search_string[i])
                if search_string in VERSION_INTELAM:                            # Checks for the Intel Advanced Menu string in string_in_bios and platform version details in child bios string
                    platform_result, result = \
                        read_bios_platform_information(string_in_bios, tc_id,
                                                       script_id, log_level,
                                                       tbd)
                    if option_in_bios == "None":
                        return platform_result, result                          # Returns true, if BIOS platform option read is success and result value
                    else:
                        if option_in_bios.lower().strip() == result.lower().strip():
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "BIOS read value is same as "
                                              "expected string in BIOS %s = %s"
                                              % (result, option_in_bios),
                                              tc_id, script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)

                            return platform_result, result
                        else:
                            library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                              " BIOS read value is not same as "
                                              "expected string in BIOS %s = %s"
                                              % (result, option_in_bios),
                                              tc_id, script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)

                            return False, None
                else:
                    depex_value = verify_depex_value(string_in_bios, STR_READ,
                                                     tc_id, script_id,
                                                     log_level, tbd)
                    if depex_value is not True:
                        return False, None

                    if "active thermal trip point" in step.lower():
                        if "virtual sensor participant 1" in step.lower() or \
                           "virtual sensor participant 2" in step.lower():
                            if "virtual sensor participant 1" in step.lower() \
                               and "read bios" in step.lower():
                                param_readknobs = \
                                    "ActiveThermalTripPointVS1 = " + \
                                    str(option_in_bios)

                            if "virtual sensor participant 2" in step.lower() \
                                    and "read bios" in step.lower():
                                param_readknobs = \
                                    "ActiveThermalTripPointVS2 = " + \
                                    str(option_in_bios)

                            result = cli.CvProgKnobs(param_readknobs)
                            if not result:                                      # Checks if result returns zero and log pass message
                                with open(XMLCLI_LOGPATH, "r") as file_desc:
                                    data = file_desc.readlines()

                                verify_string = data[-1]                        # Extracting last line from XmlCli.log file to verify pass

                                if STR_VERIFY_MSG == \
                                        str(verify_string).upper().strip():     # Checks log pass message
                                    library.write_log(lib_constants.LOG_INFO,
                                                      "INFO: Bios option read "
                                                      "successfully", tc_id,
                                                      script_id, "XmlCli",
                                                      "None", log_level, tbd)
                                    return True, result
                                else:
                                    library.write_log(lib_constants.LOG_WARNING,
                                                      "WARNING: Failed to read "
                                                      "Bios option", tc_id,
                                                      script_id, "XmlCli",
                                                      "None", log_level, tbd)
                                    return False

                    flag_offline, common_checklist = \
                        parse_offline_xml(string_in_bios, tc_id, script_id,
                                          log_level, tbd)                       # Returns offline log returns if offline log creation is successful along with the options dictionary
                    if flag_offline is True and common_checklist is not None:
                        flag_online, current_bios_value = \
                            parse_online_xml(option_in_bios, common_checklist,
                                             tc_id, script_id, log_level,
                                             tbd)
                        if flag_online is True and current_bios_value is\
                                not None:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "BIOS Read success and the "
                                              "Current BIOS value is %s" %
                                              current_bios_value, tc_id,
                                              script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)
                            return True, current_bios_value                     # Returns true and current BIOS value
                        elif flag_online is True and current_bios_value is None:
                            return False, None                                  # Returns true, if option to compare is not none for single and multiple bios option
                        elif flag_online in FLAG_SINGLE_OPT:
                            return True, flag_online
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: BIOS verification "
                                              "failed, Due to Current BIOS "
                                              "option is different", tc_id,
                                              script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)
                            return False, None                                  # Returns False, if bios option to compare fails
                    else:
                        platform_result, result = \
                            read_bios_platform_information(string_in_bios,
                                                           tc_id, script_id,
                                                           log_level, tbd)

                        if platform_result is True:
                            if option_in_bios == "None":
                                return platform_result, result  # Returns true, if BIOS platform option read is success and result value
                            else:
                                if option_in_bios.lower().strip() == result.lower().strip():
                                    library.write_log(lib_constants.LOG_INFO, "INFO: "
                                                                              "BIOS read value is same as "
                                                                              "expected string in BIOS %s = %s"
                                                      % (result, option_in_bios),
                                                      tc_id, script_id,
                                                      lib_constants.TOOL_XMLCLI,
                                                      lib_constants.STR_NONE,
                                                      log_level, tbd)

                                    return platform_result, result
                                else:
                                    library.write_log(lib_constants.LOG_WARNING, "WARNING:"
                                                                                 " BIOS read value is not same as "
                                                                                 "expected string in BIOS %s = %s"
                                                      % (result, option_in_bios),
                                                      tc_id, script_id,
                                                      lib_constants.TOOL_XMLCLI,
                                                      lib_constants.STR_NONE,
                                                      log_level, tbd)

                                    return False, None


                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: '%s' path does not "
                                              "exist in BIOS, Please verify "
                                              "the BIOS path" % string_in_bios,
                                              tc_id, script_id,
                                              lib_constants.TOOL_XMLCLI,
                                              lib_constants.STR_NONE,
                                              log_level, tbd)
                            return False, None                                      # Returns False, if offline log creation failed
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "due to bios path is not valid %s"
                                  % string_in_bios, tc_id, script_id,
                                  lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False, None                                              # Returns False, if biospath is invalid
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "read_bios_xmlcli() due to %s" % e, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False, False


def verify_depex_value(step, read_or_set, tc_id, script_id, log_level, tbd):

    """
    Function Name     : verify_depex_value()
    Parameters        : step, read_or_set, tc_id, script_id, log_level, tbd
    Functionality     : to verify the depex value for bios_path
    Return Value      : True on successful action and False on failure
    """

    try:
        option = step.split("/")[-1].strip()
        if STR_PLATFORM_INFO_MENU.lower() in step.lower() or \
           option in PLATFORM_INFORMATION_BIOS_VALUES or \
           option.lower() in SKIP_DEPEX_STATUS_OPTIONS or \
           option.lower() in FORM_OPTIONS:
            return True

        if 0 == cli.savexml():
            library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli log file "
                              "got generated successfully", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate the XmlCli log file", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False

        xmlcli_dictionary = {}
        xmlcli_csv_file_path = os.path.join(lib_constants.TOOLPATH,
                                            "pysvtools.xmlcli", "pysvtools",
                                            "xmlcli", "out",
                                            "PlatformConfig.csv")

        if 0 == cli.prs.EvalKnobsDepex(lib_constants.XMLCLI_PATH,
                                       xmlcli_dictionary,
                                       xmlcli_csv_file_path):
            if os.path.exists(xmlcli_csv_file_path):
                library.write_log(lib_constants.LOG_INFO, "INFO: csv file got "
                                  "generated successfully and exist in the "
                                  "csv_file_path", tc_id, script_id,
                                  lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generated the csv file", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False

        step_val = step.lower().replace(" ", "")

        if STR_READ == read_or_set:
            if "=" in step:
                bios_path = step_val.lower().replace("/bios/", "").\
                    split("=")[0].strip(" ")
            else:
                bios_path = step_val.lower().replace("/bios/", "")
            bios_path = '"' + bios_path + '"'
        else:
            bios_path = step_val.lower().replace("/bios/", "").\
                split("=")[0].strip(" ")
            bios_path = '"' + bios_path + '"'

        with open(xmlcli_csv_file_path, "r") as csv_file:
            for line in csv_file:
                if bios_path.lower() in \
                        line.lower().replace(" ", ""):
                    if "active" in line.lower():
                        library.write_log(lib_constants.LOG_INFO, "INFO: The "
                                          "BIOS path physically exist and BIOS"
                                          " option is Active in BIOS page",
                                          tc_id, script_id,
                                          lib_constants.TOOL_XMLCLI,
                                          lib_constants.STR_NONE, log_level,
                                          tbd)
                        return True
                    elif ("suppressed" in line.lower() or
                          "grayedout" in line.lower()) and \
                            STR_SET in read_or_set:
                        library.write_log(lib_constants.LOG_WARNING,
                                          "WARNING: The BIOS path does not "
                                          "exist physically or BIOS path is "
                                          "not visible and BIOS Option is "
                                          "Grayedout or Suppressed in BIOS "
                                          "page. Due to this reason, can not "
                                          "set the BIOS value", tc_id,
                                          script_id, lib_constants.TOOL_XMLCLI,
                                          lib_constants.STR_NONE,
                                          log_level, tbd)
                        return False
                    elif "suppressed" in line.lower() and \
                            STR_READ in read_or_set:
                        library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                          "The BIOS path does not exist "
                                          "physically or BIOS path is not "
                                          "visible and BIOS Option is "
                                          "Suppressed in BIOS page. Due to "
                                          "this reason, can not read the BIOS "
                                          "value", tc_id, script_id,
                                          lib_constants.TOOL_XMLCLI,
                                          lib_constants.STR_NONE, log_level,
                                          tbd)
                        return False
                    elif "grayedout" in line.lower() and \
                            STR_READ in read_or_set:
                        library.write_log(lib_constants.LOG_INFO, "INFO: The "
                                          "BIOS Option is Grayedout in BIOS "
                                          "Page", tc_id, script_id,
                                          lib_constants.TOOL_XMLCLI,
                                          lib_constants.STR_NONE, log_level,
                                          tbd)
                        return True

        library.write_log(lib_constants.LOG_INFO, "INFO: The BIOS path does "
                          "not exist in the generated CSV file. Need to "
                          "check test step BIOS path w.r.to BIOS page or The "
                          "specified BIOS path is not applicable for the "
                          "running platform", tc_id, script_id,
                          lib_constants.TOOL_XMLCLI, lib_constants.STR_NONE,
                          log_level, tbd)
        return False
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "verify_depex_value() due to %s" % e_obj, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def set_bios_xml_cli(bios_path, params_value, step, tc_id, script_id,
                     log_level, tbd):

    """
    Function Name     : set_bios_xml_cli()
    Parameters        : bios_path, params_value, step, tc_id, script_id,
                        log_level, opt
    Functionality     : write the bios value
    Function Invoked  : parse_offline_xml(), check_name_online_log()
                        mount_drive_to_xmlcli_bios(), xmlcli_access_verify()
    Return Value      : True on successful action and False on failure
    """

    try:
        xmlcli_enablement_check = xmlcli_access_verify(tc_id, script_id,
                                                       log_level, tbd)          # Checks whether XMLCLI Support is enabled or not, also checks whether Intel CCG SDK is Installed or not
        if xmlcli_enablement_check is False:
            return False

        if step == lib_constants.STR_MOUNT_DRIVE:
            mount_drive_to_xmlcli_bios_check = \
                mount_drive_to_xmlcli_bios(tc_id, script_id, log_level, tbd)    # Calls the mount drive function to verfiy the EFI shell mode BIOS executed log

            if mount_drive_to_xmlcli_bios_check is True:
                return True
            else:
                return False
        else:
            bios_path = bios_path.lower()
            bios_path = bios_path.replace(POWER_AND_PERFORMANCE,
                                          POWER_N_PERFORMANCE)                  # Temporary fix for handling xmlcli related tool issue
            bios_path = bios_path.split("/")                                    # Splits bios_path by "/"
            for bios_itr in bios_path:
                if bios_itr.upper() in GREYED_OUT_OPTIONS:
                    bios_path.remove(bios_itr)                                  # If any string in that GREYED_OUT_OPTIONS list and removes that string from the bios_path
            bios_path = "/".join(bios_path)                                     # Join the list back to the string after removal
            if params_value:
                if "&" in params_value:
                    params_value = params_value.replace("&", "n")
                else:
                    pass
                if STR_STEP.lower() in params_value.lower():
                    step_no = params_value.split()[1]
                    step_value = utils.read_from_Resultfile(step_no)          # Reads the step value from the Result.ini file
                    if "'d" or "'D" in step_value:
                        step_value = str(int(round(float(step_value.
                                                         replace("'d", "")))))
                    params_value = step_value
                elif STR_DONT_CARE in params_value.lower():
                    params_value = 'don?t care'
            string_in_bios_param = [bios_string.lower().strip()
                                    for bios_string in bios_path.split('/')]

            for bios_check in lib_constants.EFI_OPTION_LIST:
                if bios_check.lower().strip() in string_in_bios_param:
                    xml_cli_bios_security_option_efi_check = \
                        xmlcli_bios_security_option_efi(bios_path,
                                                        params_value, step,
                                                        tc_id, script_id,
                                                        log_level, tbd)
                    if xml_cli_bios_security_option_efi_check is True:
                        return True
                    else:
                        return False

            if STR_BOOTCONFIGMENU.title() in bios_path.title():
                bios_path = "/".join([bios_path.split('/')[itr].strip() for itr
                                      in range(3, len(bios_path.split('/')))])  # If bios_path string contains "Boot Configuration Menu" it will split and remove first two strings
            elif STR_INTELADVMENU.title() in bios_path.title() or \
                STR_INTELTESTMENU.title() in bios_path.title():
                 bios_path = "/".join([bios_path.split('/')[itr].strip() for itr
                                      in range(2, len(bios_path.split('/')))])  # If bios_path string contains "Intel advanced menu" or "Intel Test Menu" it will split and remove first two strings
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: BIOS "
                                  "path not handled", tc_id, script_id,
                                  lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False                                                    # If biospath not handled in above two headers will return False

            if verify_depex_value(bios_path, STR_SET, tc_id, script_id,
                                  log_level, tbd):
                pass
            else:
                return False

            if "active thermal trip point" in step.lower():
                if "virtual sensor participant 1" in step.lower() or \
                   "virtual sensor participant 2" in step.lower():
                    if "virtual sensor participant 1" in step.lower() and \
                       "set bios" in step.lower():
                        param_setknobs = \
                            "ActiveThermalTripPointVS1 = " + str(params_value)

                    if "virtual sensor participant 2" in step.lower() and \
                            "set bios" in step.lower():
                        param_setknobs = \
                            "ActiveThermalTripPointVS2 = " + str(params_value)

                    result = cli.CvProgKnobs(param_setknobs)
                    if not result:                                              # Checks if result returns zero and log pass message
                        with open(XMLCLI_LOGPATH, "r") as file_desc:
                            data = file_desc.readlines()

                        verify_string = data[-1]                                # Extracting last line from XmlCli.log file to verify pass

                        if STR_VERIFY_MSG == \
                                str(verify_string).upper().strip():             # Checks log pass message
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Bios option successfully set",
                                              tc_id, script_id, "XmlCli",
                                              "None", log_level, tbd)
                            return True
                        else:
                            library.write_log(lib_constants.LOG_WARNING,
                                              "WARNING: Failed to set Bios "
                                              "option", tc_id, script_id,
                                              "XmlCli", "None", log_level, tbd)
                            return False

            flag_offline, common_checklist = parse_offline_xml(bios_path,
                                                               tc_id,
                                                               script_id,
                                                               log_level,
                                                               tbd)             # Returns True or False and common_checklist from the offlineXML
            flag_online, common_checklist = \
                check_name_online_log(common_checklist, tc_id, script_id,
                                      log_level, tbd)                           # Returns True or False and common_checklist from the onlineXML

            if not flag_online:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed "
                                  "to find name in online xml", tc_id,
                                  script_id, lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False

            if flag_online:
                for key, value in list(common_checklist.items()):
                    keys = re.sub(" +", " ", key)                               # Removing extra spaces in a string from common_checklist
                    common_checklist[keys] = common_checklist.pop(key)

            if common_checklist[STR_NAME] in SET_VALUES_OPTIONS:
                if not STR_HEX_SYMBOL_X in params_value.lower():
                    int_num = int(params_value)
                    knob_value = hex(int_num)
            elif params_value.isalpha():
                if params_value.lower() in list(UNIQ_PARAM_DICT.keys()):
                    params_value = UNIQ_PARAM_DICT[params_value.lower()]
                    knob_value = common_checklist.get(params_value)
                else:
                    knob_value = common_checklist.get(params_value.title())
                    if knob_value is None:
                        if params_value.upper() in common_checklist:
                            knob_value = common_checklist.get(params_value.upper())
                        else:
                            knob_value = common_checklist.get(params_value)
            else:
                hex_flag = False
                if STR_HEX_SYMBOL_X in params_value.lower():                    # Checking for hexadecimal value
                    if STR_HEX_SYMBOL_0 == params_value.lower().\
                       split(STR_HEX_SYMBOL_X)[0]:
                        knob_value = params_value.upper()                       # If value option_in_bios is hexadecimal then directly passing that value
                        hex_flag = True

                if not hex_flag:
                    common_checklist_value = dict()
                    for key, value in common_checklist.items():
                        common_checklist_value[key.lower()] = value.lower()     # Converting the dictionary key, value to lower case for comparison

                    try:
                        knob_value = common_checklist_value.get(params_value.
                                                                lower())
                        if not knob_value:
                            int_val = int(params_value)
                            if int_val < 0:
                                knob_value = str(int_val)
                            else:
                                knob_value = hex(int(params_value))
                    except:
                        knob_value = common_checklist_value.get(params_value.
                                                                lower())
            param_setknobs = common_checklist.get(STR_NAME) + "=" + knob_value
            result = cli.CvProgKnobs(param_setknobs)

            if not result:                                                      # Checks if result returns zero and log pass message
                with open(XMLCLI_LOGPATH, "r") as file_desc:
                    data = file_desc.readlines()

                verify_string = data[-1]                                        # Extracting last line from XmlCli.log file to verify pass

                if STR_VERIFY_MSG == str(verify_string).upper().strip():        # Checks log pass message
                    library.write_log(lib_constants.LOG_INFO, "INFO: Bios "
                                      "option successfully set", tc_id,
                                      script_id, lib_constants.TOOL_XMLCLI,
                                      lib_constants.STR_NONE, log_level, tbd)
                    return True
                else:
                    library.write_log(lib_constants.LOG_WARNING, "WARNING: "
                                      "Unable to set bios option", tc_id,
                                      script_id, lib_constants.TOOL_XMLCLI,
                                      lib_constants.STR_NONE, log_level, tbd)
                    return False
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable "
                                  "to set bios option", tc_id, script_id,
                                  lib_constants.TOOL_XMLCLI,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False
    except Exception as e:
        library.write_log(lib_constants.LOG_WARNING, "EXCEPTION: in "
                          "set_bios_xml_cli() due to %s" % e, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False                                                            # Return False Exception error is written to log


def load_default_xmlcli(tc_id, script_id, tools, log_level, tbd):

    """
    Function Name : load_default_xmlcli
    Parameters    : tc_id, script_id, log_level, tbd
    Functionality : Load Bios Default Setting for Tool (XMLCLI)
    Return Value  : True if BIOS set to default else False
    """

    try:
        tool_path = utils.parse_variable(lib_constants.TOOL_PATH_XML,
                                         script_id, tc_id)

        if lib_constants.STR_FAIL in tool_path:                                 # "Fail" in tool_path
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Config "
                              "entry for [xml_cli] tag is missing", tc_id,
                              script_id, tools, lib_constants.STR_NONE,
                              log_level, tbd)
            return False

        set_xml_cli_access(STR_WINHWAPI, tc_id, script_id, tools,
                           log_level, tbd)

        verify_status_xml_cli(tc_id, script_id, tools, log_level, tbd)

        result = cli.CvLoadDefaults()                                           # Loading the BIOS to Default

        if 0 == result:                                                         # if result is "0" BIOS is set to default
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully set "
                              "the default bios settings", tc_id, script_id,
                              tools, lib_constants.STR_NONE, log_level, tbd)
            return True
        else:                                                                   #if result is not "0" BIOS is not set to default
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "set default setting Result %s" % result, tc_id,
                              script_id, tools, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e:                                                      #Exception for ERROR
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in load_default"
                          "_xmlcli() dut to %s " % e, tc_id, script_id,
                          tools, lib_constants.STR_NONE, log_level, tbd)
        return False


def set_xml_cli_access(mode, tc_id, script_id, tool, log_level, tbd):

    """
    Function Name : set_xml_cli_access
    Parameters    : mode
    Return Value  : True/False
    Purpose       : Set the required Xml Cli access via Win SDK
    """

    if None == cli.clb._setCliAccess(mode):
        library.write_log(lib_constants.LOG_INFO, "INFO: Cli Access set for "
                          "Mode: %s" % mode, tc_id, script_id, tool,
                          lib_constants.STR_NONE, log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Cli Access "
                          "failed to set for Mode: %s" % mode, tc_id,
                          script_id, tool, lib_constants.STR_NONE, log_level,
                          tbd)
        return False


def verify_status_xml_cli(tc_id, script_id, tool, log_level="ALL", tbd=None):

    """
    Function Name : verify_status_xml_cli
    Parameters    : tc_id, script_id, tool, log_level, tbd
    Return Value  : True/False
    Purpose       : Verifying whether XmlCli feature Supported for current SUT
    """

    returncode = cli.clb.ConfXmlCli()

    if returncode == 0:
        library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli feature "
                          "already enabled in BIOS", tc_id, script_id, tool,
                          lib_constants.STR_NONE, log_level, tbd)
    elif returncode == 2:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: XmlCli feature "
                          "not enabled. Enabling Now. Need to restart", tc_id,
                          script_id, tool, lib_constants.STR_NONE, log_level,
                          tbd)
        return False
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: XmlCli support "
                          "is not available in current BIOS", tc_id, script_id,
                          tool, lib_constants.STR_NONE, log_level, tbd)
        return False


def get_current_bios_dump(xml_path, tc_id, script_id, tool, log_level, tbd):

    """
    Function Name : get_current_bios_dump
    Parameters    : tc_id, script_id, tool, log_level, tbd
    Return Value  : True/False
    Purpose       : Dump current BIOS settings as XML file
    """

    if cli.savexml(xml_path) == 0:                                              # Extract the XML data from desired BIOS
        library.write_log(lib_constants.LOG_INFO, "INFO: Successfully extract "
                          "the XML data from desired BIOS", tc_id, script_id,
                          tool, lib_constants.STR_NONE, log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                          "extract the XML data from desired BIOS", tc_id,
                          script_id, tool, lib_constants.STR_NONE, log_level,
                          tbd)
        return False


def get_boot_order(tc_id, script_id, log_level, tbd):

    """
    Function Name      : get_boot_order()
    Parameters         : tc_id, script_id, log_level, tbd
    Functionality      : gets the boot ordered list
    Functions Invoked  : library.write_log(), cli.clb._setCliAccess()
    Return Value       : Returns the ordered boot list if successful,
                         else False
    """

    try:
        set_xml_cli_access(STR_WINHWAPI, tc_id, script_id,
                           lib_constants.TOOL_XMLCLI, log_level, tbd)

        verify_status_xml_cli(tc_id, script_id, lib_constants.TOOL_XMLCLI,
                              log_level, tbd)

        boot_order_details = cli.GetBootOrder()

        if 1 == boot_order_details:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "fetch the Boot order details", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
        else:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "fetched the Boot order details", tc_id,
                              script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)

        boot_order_details_dict = cli.BootOrderDict['OptionsDict']

        if not len(boot_order_details_dict) == 0:
            script_name = script_id.replace(".py", ".txt")
            logpath = lib_constants.SCRIPTDIR + os.sep + script_name
            boot_value = ""
            with open(logpath, "w") as f_write:
                for (sequence, boot_order) in boot_order_details_dict.\
                        items():
                    for (boot_num, boot_name) in boot_order.items():
                        boot_value = boot_value + " " + str(boot_name)
                    f_write.write(str(boot_value))
                    f_write.write("\n")
                    boot_value = ""

            library.write_log(lib_constants.LOG_INFO, "INFO: Boot Order "
                              "Details successfully stored in Dictionary",
                              tc_id, script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return logpath
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "store Boot Order Details in Dictionary", tc_id,
                              script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in get_boot_"
                          "order function due to %s" % str(e), tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)               # write error msg to log
        return False


def set_boot_order(device_name, tc_id, script_id, tool, log_level, tbd):

    """
    Function Name : set_boot_order
    Parameters    : tc_id, script_id, tool, log_level, opt
    Return Value  : True/False
    Purpose       : set selected device as first booting device
    """

    set_xml_cli_access(STR_WINHWAPI, tc_id, script_id, tool, log_level, tbd)

    verify_status_xml_cli(tc_id, script_id, tool, log_level, tbd)

    boot_order_details = cli.GetBootOrder()

    if 1 == boot_order_details:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to fetch "
                          "the Boot order details", tc_id, script_id, tool,
                          lib_constants.STR_NONE, log_level, tbd)
        return False
    else:
        library.write_log(lib_constants.LOG_INFO, "INFO: successfully fetched "
                          "the Boot order details", tc_id, script_id, tool,
                          lib_constants.STR_NONE, log_level, tbd)

    boot_order_details_dict = cli.BootOrderDict['OptionsDict']

    if not len(boot_order_details_dict) == 0:
        library.write_log(lib_constants.LOG_INFO, "INFO: Boot Order Details "
                          "successfully stored in Dictionary", tc_id,
                          script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to stroe "
                          "Boot Order Details in Dictionary", tc_id, script_id,
                          tool, lib_constants.STR_NONE, log_level, tbd)
        return False

    option_val_list, option_text_list, new_option_text_list = [], [], []

    for key_index in range(len(boot_order_details_dict)):
        option_val_list.append(boot_order_details_dict[key_index]['OptionVal'])
        option_text_list.append(boot_order_details_dict[key_index]
                                ['OptionText'])

    if not len(option_val_list) == 0:
        library.write_log(lib_constants.LOG_INFO, "INFO: Boot Order Index "
                          "successfully stored in list: %s" % option_val_list,
                          tc_id, script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Boot Order "
                          "Index failed to stored in list", tc_id, script_id,
                          tool, lib_constants.STR_NONE, log_level, tbd)
        return False

    if not len(option_text_list) == 0:
        library.write_log(lib_constants.LOG_INFO, "INFO: Boot Order values "
                          "successfully stored in list: %s" % option_text_list,
                          tc_id, script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: Boot Order "
                          "values failed to stored in list", tc_id, script_id,
                          tool, lib_constants.STR_NONE, log_level, tbd)
        return False

    current_boot_order_dict = dict(list(zip(option_text_list, option_val_list)))
    dev_name_in_xml = ''

    for info in option_text_list:
        if device_name.lower() in info.lower():
            dev_name_in_xml = info

    current_order_of_device = current_boot_order_dict[dev_name_in_xml]
    index_boot = option_val_list.index(current_order_of_device)
    option_val_list[index_boot], option_val_list[0] = \
        option_val_list[0], option_val_list[index_boot]
    boot_order_to_set = "-".join([str(i) for i in option_val_list])

    returncode = cli.SetBootOrder(boot_order_to_set)

    if returncode == 0 or returncode == 2 or returncode == 3:
        library.write_log(lib_constants.LOG_INFO, "INFO: Successfully set %s "
                          "first in first boot order" % dev_name_in_xml, tc_id,
                          script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
        return True
    else:
        library.write_log(lib_constants.LOG_WARNING, "WARNING: %s failed to "
                          "set as first in boot order" % dev_name_in_xml,
                          tc_id, script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
        return False


def read_knobs_from_xml_cli_for_bios(mem_freq, channel_num, slot_num, tc_id,
                                     script_id, tool, log_level, tbd):

    """
    Function Name : read_knobs_from_xml_cli_for_bios
    Parameters    : mem_freq, channel_num, slot_num, tc_id, script_id, tool,
                    log_level, tbd
    Return Value  : True/False
    Purpose       : reads the frequency , channel and slot of memory module
                    from xml file
    """

    try:
        if int(channel_num) == lib_constants.ZERO:                              #checking for particular given slot for channel number 0
            if int(slot_num) == lib_constants.ZERO:
                dimm0 = str(lib_constants.ZERO)
                ret_code = cli.CvReadKnobs(CHANNEL0 + "=" + dimm0)              #calling readknobs for given channel and slot number
            elif int(slot_num) == lib_constants.ONE:
                dimm0 = str(lib_constants.THREE)
                ret_code = cli.CvReadKnobs(CHANNEL0 + "=" + dimm0)              #calling readknobs for given channel and slot number
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
                                  "slot number", tc_id, script_id, tool,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False

        elif int(channel_num) == lib_constants.ONE:                             #checking for particular given slot for channel number 1
            if int(slot_num) == lib_constants.ZERO:
                dimm1 = str(lib_constants.ZERO)
                ret_code = cli.CvReadKnobs(CHANNEL1 + "=" + dimm1)              #calling readknobs for given channel and slot number
            elif int(slot_num) == lib_constants.ONE:
                dimm1 = str(lib_constants.THREE)
                ret_code = cli.CvReadKnobs(CHANNEL1 + "=" + dimm1)              #calling readknobs for given channel and slot number
            else:
                library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
                                  "slot number", tc_id, script_id, tool,
                                  lib_constants.STR_NONE, log_level, tbd)
                return False
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Invalid "
                              "channel number", tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return False

        returncode = cli.CvReadKnobs(FREQUENCY + "=" + mem_freq)                #calling read knobs for frequency

        if returncode == 0 and ret_code == 0:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully read "
                              "the frequency, size of memory module at given "
                              "slot and channel", tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "read the frequency, size of memory module at "
                              "given slot and channel", tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in read_knobs_"
                          "from_xml_cli_for_bios() due to %s" % e, tc_id,
                          script_id, tool, lib_constants.STR_NONE, log_level,
                          tbd)
        return False


def connect_memory_module_xml_cli(memory_size, memory_frequency, channel, slot,
                                  tc_id, script_id, tool, log_level, tbd):

    """
    Function name   : connect_memory_module_xml_cli
    Parameter       : memory_size, memory_freq, memory_channel, slot_number,
                      tc_id, script_id,  tool, log_level, tbd
    Functionality   : reading bios memory size and frequency at given
                      channel and slot number
    Return Value    : (Bool) True in case of success and False in case of
                      failure
    """

    try:
        cur_dir = os.getcwd()
        os.chdir(lib_constants.XMLCLI_TOOLPATH)                                 # changing current directory to Xmlcli file path

        set_xml_cli_access(STR_WINHWAPI, tc_id, script_id, tool,
                           log_level, tbd)                                      # Calling set_xml_cli_access method for setting access of xmlcli tool

        verify_status_xml_cli(tc_id, script_id, tool, log_level, tbd)           # calling verify_status_xml_cli method for verifying the configuration status

        xml_path = XMLCLI_PATH_LOG

        get_current_bios_dump(xml_path, tc_id, script_id, tool, log_level,
                              tbd)                                              # calling get_current_bios_dump method for saving xml file of xmlcli tool
        time.sleep(1)

        split_mem_size = re.findall('\d+', memory_size)                         # spliting the given memory size for numeric and converting to int
        m_size = split_mem_size[0]
        m_size_in_int = int(m_size)

        if memory_frequency == FREQ_AUTO:                                       # checking if frequency in auto or numeric mode
            frequency = str(lib_constants.ZERO)
        else:
            freq_list = re.findall('\d+', memory_frequency)                     # fetching only the numeric value
            frequency = freq_list[0]

        with open(XMLCLI_PATH_LOG, 'r') as file_pointer:                        # opening xmlcli file to read the memory size
            data = file_pointer.readlines()

        size = re.search(r'Channel ' + channel + ' Slot ' + slot + ':'
                         '.*?(?P<size>Size: \d+ MB) \(DDR[0-9]\)',
                         str(data), re.DOTALL)                                  # Searching for given regular expression in xmlcli file

        size_in_str = (size.group('size'))
        size_after_split = size_in_str.split(":")[1]                            # spliting the fetched memory size from xml file for numeric and converting to int
        slot_size_split = re.findall('\d+', size_after_split)
        slot_size = slot_size_split[0]

        slot_size_in_int = int(slot_size) / lib_constants.ONE_KB                # converting MB to GB

        if slot_size_in_int == m_size_in_int:                                   # If bios slot size and given size is equal then continue for reading frequency and channel no
            pass
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "connected memory module of size %s "
                              % memory_size, tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return False

        result = read_knobs_from_xml_cli_for_bios(frequency, channel, slot,
                                                  tc_id, script_id, tool,
                                                  log_level, tbd)               # Function call for reading bios memory size and frequency from xmlcli tool
        os.chdir(cur_dir)
        if result is True:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "connected memory value of frequency %s & of "
                              "size %s at channel %s and slot %s "
                              % (memory_frequency, memory_size, channel, slot),
                              tc_id, script_id, tool,
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "connect memory value of frequency %s & of size "
                              "%s at channel %s and slot %s "
                              % (memory_frequency, memory_size, channel, slot),
                              tc_id, script_id, tool, lib_constants.STR_NONE,
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_WARNING, "EXCEPTION: in connect_"
                          "memory_module_xml_cli() due to %s" % e, tc_id,
                          script_id, tool, lib_constants.STR_NONE,
                          log_level, tbd)
        return False


def read_image_version(image_file_path, ttk2_image_version, tc_id, script_id,
                       log_level="ALL", tbd=None):

    try:
        for root, dirs, files in os.walk(xml_cli_out_folder_path,
                                         topdown=False):
            for name in files:
                log = os.path.join(root, name)
                if log.endswith(".xml"):
                    os.remove(log)
                    library.write_log(lib_constants.LOG_INFO, "INFO: All xml "
                                      "files deleted successfully in %s"
                                      % xml_cli_out_folder_path, tc_id,
                                      script_id, "None", "None", log_level, tbd)

        sys.path.append(xml_cli_tool_path)
        import pysvtools.xmlcli.XmlCli as cli
        cli.clb._setCliAccess(STR_WINHWAPI)
        result = cli.savexml(0, image_file_path)

        if 0 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Offline XmlCli "
                              "log generated successfully for the image which "
                              "used for flashing", tc_id, script_id, "None",
                              "None", log_level, tbd)

            for root, dirs, files in os.walk(xml_cli_out_folder_path,
                                             topdown=False):
                for name in files:
                    log = os.path.join(root, name)
                    if log.endswith(".xml"):
                        offline_log = log
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate Offline XmlCli log for the image "
                              "which used for flashing", tc_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        tree = ET.parse(offline_log)
        root = tree.getroot()

        for child in tree.iter("SYSTEM"):
            for item in child.findall(".//BIOS"):
                for key, value in item.attrib.items():
                    if "version" in key.lower():
                        if ttk2_image_version in value:
                            library.write_log(lib_constants.LOG_INFO, "INFO: "
                                              "Flashed image version is "
                                              "matching with XmlCli offline "
                                              "log image version", tc_id,
                                              script_id, "None", "None",
                                              log_level, tbd)
                            return True

        library.write_log(lib_constants.LOG_WARNING, "WARNING: Flashed image "
                          "version is not matching with XmlCli offline log "
                          "image version", tc_id, script_id, "None", "None",
                          log_level, tbd)
        return False
    except Exception as e:
        library.write_log(lib_constants.LOG_WARNING, "EXCEPTION: Due to %s" % e,
                          tc_id, script_id, "None", lib_constants.STR_NONE,
                          log_level, tbd)
        return False


def enable_xmlcli(test_case_id, script_id, log_level="ALL", tbd=None):

    try:
        cli.clb._setCliAccess(STR_WINHWAPI)
        xmlcli_enablement_check = cli.clb.ConfXmlCli()                          # Reads the XMLCLI enablement status on the current BIOS

        if xmlcli_enablement_check == lib_constants.RETURN_SUCCESS:             # Checks for the Intel CCG SDK and XMLCLI support enablement check
            library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli support "
                              "enabled", test_case_id, script_id,
                              lib_constants.TOOL_XMLCLI, 
                              lib_constants.STR_NONE, log_level, tbd)
            return True, xmlcli_enablement_check
        elif xmlcli_enablement_check == 2:
            library.write_log(lib_constants.LOG_INFO, "INFO: XmlCli support "
                              "not enabled by default. XmlCli will enable "
                              "after restart", test_case_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return True, xmlcli_enablement_check
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Intel CCG"
                              "SDK is not installed and XMLCLI support not "
                              "enbled in Current BIOS", test_case_id,
                              script_id, lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def xmlcli_offline_log_creation(tc_id, script_id,  log_level, tbd):

    """
    Function Name     : xmlcli_offline_log_creation
    Parameters        : log_path, tc_id, script_id,  log_level, tbd
    Functionality     : To create offline xml log
    Function Invoked  : library.write_log()
    Return Value      : return True and log path on success and False on Failure
    """

    try:
        image_path = utils.ReadConfig("IMAGE_PATH", "IMAGE_PATH")               # Path of the image
        if "FAIL:" in image_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry for image_path under image_path"
                              " from Config.ini", tc_id, script_id, "None",
                              "None", log_level, tbd)

        if os.path.exists(XML_CLI_OFFLINE_LOGPATH):                             # If old logs exits it will remove to create a new one
            os.remove(XML_CLI_OFFLINE_LOGPATH)
            library.write_log(lib_constants.LOG_INFO, "INFO: Cleared old "
                              "Offline XmlCli log files", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
        cli.clb._setCliAccess(STR_WINHWAPI)
        result_save_xml = cli.savexml(XML_CLI_OFFLINE_LOGPATH,  image_path)     # Command to save the offline XML file

        if lib_constants.RETURN_SUCCESS == result_save_xml:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully run "
                              "command to generate offline log and log exist "
                              "in path", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)

            for root, dirs, files in os.walk(xml_cli_out_folder_path,
                                             topdown=False):
                for name in files:
                    log = os.path.join(root, name)
                    if log.split("\\")[-1].endswith(".xml") and \
                       "platformconfig-offline" in log.lower():
                        offline_log = log
                        return True, offline_log
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Unable to "
                              "run command to save log", tc_id, script_id,
                              lib_constants.TOOL_XMLCLI,
                              lib_constants.STR_NONE, log_level, tbd)
            return False                                                        # If result_save_xml is failed to return output
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "xml_log_creation() due to %s " % e, tc_id,
                          script_id, lib_constants.TOOL_XMLCLI,
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def set_bios_options_before_flash_using_xmlcli(tc_id, script_id,
                                               log_level="ALL", tbd=None):

    try:
        cli.clb._setCliAccess("winhwa")
        result = cli.CvProgKnobs("BiosGuard=0, FprrEnable=0, PchBiosLock=0")

        if 0 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Bios options set "
                              "successfully", tc_id, script_id, "XmlCli",
                              lib_constants.STR_NONE, log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "set Bios options", tc_id, script_id, "XmlCli",
                              lib_constants.STR_NONE, log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "set_bios_options_before_flash_using_xmlcli() due to"
                          " %s " % e, tc_id, script_id, "XmlCli",
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def ifwi_bios_flash_using_xmlcli(test_case_id, script_id, log_level="ALL",
                                 tbd=None):

    try:
        image_path = utils.ReadConfig("IMAGE_PATH", "IMAGE_PATH")               # Path of the image
        if "FAIL:" in image_path:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "get config entry for image_path under image_path"
                              " from Config.ini", test_case_id, script_id,
                              "None", "None", log_level, tbd)

        cli.clb._setCliAccess("winhwa")

        if image_path.endswith(".bin"):
            result = cli.SpiFlash("write", image_path)
        else:
            result = cli.SpiFlash("write", image_path, cli.fwp.BIOS_Region)

        if 0 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Successfully "
                              "flashed %s using XmlCli" % image_path,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "flash %s using XmlCli" % image_path,
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "ifwi_bios_flash_using_xmlcli() due to %s " % e,
                          test_case_id, script_id, "XmlCli",
                          lib_constants.STR_NONE, log_level, tbd)
        return False


def compare_offline_and_online_log_after_flash(test_case_id, script_id,
                                               log_level="ALL", tbd=None):

    try:
        if os.path.exists(XML_CLI_ONLINE_LOGPATH):                              # If old logs exits it will remove to create a new one
            os.remove(XML_CLI_ONLINE_LOGPATH)
            library.write_log(lib_constants.LOG_INFO, "INFO: Cleared old "
                              "online XmlCli log files", test_case_id,
                              script_id, "XmlCli", "None", log_level, tbd)

        cli.clb._setCliAccess("winhwa")
        result = cli.savexml()

        if 0 == result:
            library.write_log(lib_constants.LOG_INFO, "INFO: Online XmlCli "
                              "log generated successfully", test_case_id,
                              script_id, "None", "None", log_level, tbd)
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Failed to "
                              "generate Online XmlCli log", test_case_id,
                              script_id, "None", "None", log_level, tbd)
            return False

        if os.path.exists(XML_CLI_ONLINE_LOGPATH):
            with open(XML_CLI_ONLINE_LOGPATH, 'r') as xml_file:
                for line in xml_file:
                    if "firmwareversion" in line.lower():
                        line = line.split(" ")
                        for element in line:
                            if "firmwareversion" in element.lower():
                                online_log_image_version = \
                                    str(element).split("=")[-1]

            with open(XML_CLI_ONLINE_LOGPATH, 'r') as xml_file:
                for line in xml_file:
                    if "me fw version" in line.lower():
                        line = line.strip().split(":")[-1]
                        online_log_me_fw_version = \
                            str(line).strip("-->").strip()

        if os.path.exists(XML_CLI_OFFLINE_LOGPATH):
            with open(XML_CLI_OFFLINE_LOGPATH, "r") as xml_file:
                for line in xml_file:
                    if "bios version" in line.lower() and \
                       "tstamp" in line.lower():
                        line = line.lower().split("tstamp")
                        for element in line:
                            if "bios version" in element.lower():
                                offline_log_image_version = \
                                    str(element).split("=")[-1]

            with open(XML_CLI_OFFLINE_LOGPATH, "r") as xml_file:
                for line in xml_file:
                    if "me fw version" in line.lower():
                        line = line.strip().split(":")[-1]
                        offline_log_me_fw_version = \
                            str(line).strip("-->").strip()

        library.write_log(lib_constants.LOG_INFO, "INFO: Online log details "
                          "as image_version: %s, me_fw_version: %s"
                          % (online_log_image_version,
                             online_log_me_fw_version), test_case_id,
                          script_id, "XmlCli", "None", log_level, tbd)

        library.write_log(lib_constants.LOG_INFO, "INFO: Offline log details "
                          "as image_version: %s, me_fw_version: %s"
                          % (offline_log_image_version.upper(),
                             offline_log_me_fw_version), test_case_id,
                          script_id, "XmlCli", "None", log_level, tbd)

        if (offline_log_image_version.lower() !=
            offline_log_me_fw_version.lower()) or \
           (online_log_me_fw_version.lower() !=
            offline_log_me_fw_version.lower()):
            library.write_log(lib_constants.LOG_INFO, "INFO: Verified Image & "
                              "ME Fw Versions successfully after flashing",
                              test_case_id, script_id, "XmlCli", "None",
                              log_level, tbd)
            return True
        else:
            library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Failed to "
                              "verify Image & ME Fw Versions after flashing",
                              test_case_id, script_id, "XmlCli", "None",
                              log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: in "
                          "compare_offline_and_online_log_after_flash() due "
                          "to %s " % e, test_case_id, script_id, "XmlCli",
                          lib_constants.STR_NONE, log_level, tbd)
        return False
