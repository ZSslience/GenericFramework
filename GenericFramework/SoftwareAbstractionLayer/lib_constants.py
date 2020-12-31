__author__ = "Automation Development Team"

"""
All the constant variable are defined in this file
"""

# GLobal Python Imports
import platform
import os
import socket
import sys
import time

BOARDID = "/Bios/Platform Information Menu/Board ID"
BIOS_TEST_IMAGE = "TEST"
BAUDRATE1 = "115200"
BAUDRATE2 = "230400"
KILL_TASK_PUTTY = 'taskkill /f /im plink.exe'
KILL_TASK_TERATERM = 'taskkill /f /im ttermpro.exe'
KILL_TASK_WINDBG = 'taskkill /f /im windbg.exe'
HOMEDRIVE = 'C:'                                                                #  Homedrive information EX: C:
DEBUGLOG = "debuglog.txt"                                                       #  Debug log file name used for debugging inforamtion
EPCSLOG = "epcs_log.txt"                                                        #  EPCS log file for bios reading
VTINFOCOMMAND = "vtinfo.efi" 							                        #  Command for running VTInfo Tool
IVE_UTR_FOLDERPATH = r"C:\\Testing\IVE_UTR_UDL"
INPUTPATH = r"C:\\Testing\\IVE_UTR_UDL\\Input"
OUTPUTPATH = r"C:\\Testing\\IVE_UTR_UDL\\Output"
SOURCEPATH = r"C:\\Testing\\IVE_UTR_UDL\\Source"
INTER_FILE_PATH = r"C:\\Automation\\log.txt"
PARSERLOG = r"C:\\Testing\\IVE_UTR_UDL\\Source\\Parse_log.txt"
SYNTAXLOG = r"C:\\Testing\\Source\\Syntax_Handler_Log.csv"
GENERIC_FRAMEWORK_PATH = r"C:\\Testing\\GenericFramework"
TOOLPATH = r"C:\\Testing\\GenericFramework\\Tools"
MIDDLEWARE_PATH = r"C:\\Testing\\GenericFramework\\MiddleWare"
HAL_PATH = r"C:\\Testing\\GenericFramework\\HardwareAbstractionLayer"
SAL_PATH = r"C:\\Testing\\GenericFramework\\SoftwareAbstractionLayer"
CONFIGPATH = r"C:\\Testing\\IVE_UTR_UDL\\MiddleWare\\Config"

SIKULIPATH = os.path.join(TOOLPATH + "\\" + "sikulix" + "\\" +
                          "Sikuli-IDE.exe")                                     # Path to change dir to execute sikuli executable file
PTTBATPATH = r"C:\\Testing\\GenericFramework\\tools\\PTTBAT\\logs"                 # PTTBAT logs
workingdir = os.getcwd()
SIMICS_LOG_PATH = r"C:\\simics.log"
ACTIVATE_SIMICS_WINDOW = r"C:\\Testing\\GenericFramework\\tools\\app_activa" \
    r"tion_has_presi.exe"
MOUSE_DOUBLE_CLICK = r"C:\\Testing\\GenericFramework\\tools\\Mouse_dou" \
    r"ble_click.exe"
DELETE_DISK_PRESI = r"C:\\Automation\\utils\\removedisk.cmd"
CREATE_DISK_PRESI = r"C:\\Automation\\utils\\create_disk.cmd"
ASSIGN_DRIVE_PRESI = r"C:\\Automation\\utils\\assign_letter.cmd"

CREATE_COMP_NAME_KBD_MOUSE_PRESI = "create-usb3-%s-comp name = %s"
CREATE_CONNECTOR_KBD_MOUSE_PRESI = '\"connect %s.connector_usb_host cnt1 = ' \
    '%s.mb.sb.usb3_port[0]"'
INSTANTIATE_COMPONENTS_PRESI = '"instantiate-components"'
LOAD_MODULE_PRESI = '"load-module usb3-devices-comp"'
CREATE_DISK_PENDRIVE2_PRESI = '"new-usb3-hs-disk-dev file = %s"'
CREATE_DISK_PENDRIVE3_PRESI = '"new-usb3-disk file = %s"'
CONNECT_USB3_COMMAND_PRESI = '\"connect usb3_disk_%s.connector_usb_'\
    'host cnt1 = ''icl.mb.sb.usb3_port[%s]"'
CONNECT_USB3_COMMAND_PRESI_LKF = '\"connect usb3_disk_%s.connector_usb_'\
    'host cnt1 = ''lkf.mb.sb.usb3_port[%s]"'
CONNECT_USB2_COMMAND_PRESI = '\"connect usb3_hs_disk_dev_%s.connector_usb' \
    '_host cnt1 =''icl.mb.sb.usb2_port[%s] "'
CONNECT_USB2_COMMAND_PRESI_LKF = '\"connect usb3_hs_disk_dev_%s.connector_usb' \
    '_host cnt1 =''lkf.mb.sb.usb2_port[%s] "'
DISCONNECT_MOUSE_KEYBOARD_PRESI = '"disconnect %s.connector_usb_host cnt1 = "' \
    '%s.mb.sb.usb3_port[0]"'
DISCONNECT_PENDRIVE2_PRESI = '\"disconnect usb3_hs_disk_dev_%s.' \
    'connector_usb_host cnt1 =''icl.mb.sb.usb2_%s "'
DISCONNECT_PENDRIVE2_PRESI_LKF = '\"disconnect usb3_hs_disk_dev_%s.' \
    'connector_usb_host cnt1 =''lkf.mb.sb.usb2_%s "'
DISCONNECT_PENDRIVE3_PRESI = '\"disconnect usb3_disk_%s.connector_usb_host ' \
    'cnt1 = ''icl.mb.sb.usb3_%s"'
DISCONNECT_PENDRIVE3_PRESI_LKF = '\"disconnect usb3_disk_%s.connector_usb_host'\
    ' cnt1 = ''lkf.mb.sb.usb3_%s"'
MOUSE_DOUBLE_CLICK = r"C:\\Testing\\GenericFramework\\tools\\Mouse_dou" \
    r"ble_click.exe"

BiosDefault = 'BiosDefault.txt'
PIXEL_TOOL = 'pixel.exe'
S5_STATE = 'S5'
CPU_FREQ_DIFFERENCE = 250
MINIMUM_WORKLOAD_GFX = 70
MAXIMUM_WORKLOAD_GFX = 100
WORKLOAD_GFX_SECS = 1000
WORKLOAD_GFX_HALFSECS = 2000
PL1_INDEX=26
PL2_INDEX=27
PL3_INDEX=57
FIVE_MIN = 300
TWO_MIN = 120
SHORT_TIME = 60
LONG_TIME = 132
KEYPRESS_WAIT_SUT = 30
KEYPRESS_WAIT_HOST = 10
SEND_KEY_TIME = 0.5
SX_TIMEOUT = 600
SX_TIME = 30
SX_LOG = r"C:\\Testing\\GenericFramework\\tools\\PwrTest_x64\\pwrtestlog.log"
C_STATE_PERC = [0, 50, 60, 70, 80, 90, 100]
POWER_TEST_MIN_TIME = 30
HIGH_BIT = 63
MEDIUM_BIT = 31
LOW_BIT = 0
SLEEP_TIME = 15
TWO_SECONDS = 2
FIVE_SECONDS = 5
TEN_SECONDS = 10
POINT_FIVE_SECONDS = 0.5
POINT_ONE_SECONDS = 0.1
POINT_ZERO_ONE_SECONDS = 0.01
DEFAULT_RELAY_PRESS_DURATION = 1
DEFAULT_RELAY_PRESS_TIMES = 1
POWER_BUTTON = 'POWER'
CLEAR_CMOS_WAIT_TIME =180
DEFAULT_SX_TIME = 600
THOUSAND = 1000
FIVE_HUNDRED = 500
SIXTY_ONE = 61
PING_TIMES = 35
HEAVY_LOAD = "heavyload.exe /START /CPU 4 /MEMORY 5000 /FILE /TREESIZE"
SHUTDOWN_CMD = "start shutdown /s /f /t 10"
RESTART_CMD = "start shutdown /r /f /t 10"
POSTCODE_TIMES_ONE_MIN = 60
ON = 1
ITERATE1=40
ITERATE2=20
ITERATE3=34
LONG_COUNTER = 2000
TAT_POL = 1000
TAT_EXE = 10
USB2="USB2.0"
USB3="USB3.0"

NON_OS_POST_CODE = ["10ac", "10ad", "10ab", "00ad", "00ac"]
OS_POSTCODE = ["0000", "ab03", "ab04", "abc5"]
S3_POSTCODE = ["0003","0053","b503"]
S4_POSTCODE = ["0004","b504"]
S5_POSTCODE = ["0005","0004","b505", "ffff"]
SUT_POWER_OFF = ["b505","ffff"]
CS_POSTCODE = "00c5"
S0_POSTCODE = ["1414","0000","0234","0235"]
FFFF_POSTCODE = "ffff"
S3_WAKE_POSTCODE = ["ab03","0235","0215","02F1"]
S4_WAKE_POSTCODE = ["ab04","0235","0215","02F1"]
S5_WAKE_POSTCODE = ["0000", "1414", "0235", "0215", "02F1", "9933", "99f1"]
BIOS_PAGE_POSTCODE = ["10ac", "10ab", "9cac"]
EFI_POSTCODE = ["10ad", "9cad","ac10"]
CS_WAKE_POSTCODE = ["00c5","abc5"]
PRE_SI_S5_STATE = "Host Power State Transition is finished: S0->S5"
PRE_SI_S4_STATE = "Host Power State Transition is finished: S0->S4"
PRE_SI_S3_STATE = "Host Power State Transition is finished: S0->S3"
PRE_SI_S3_WAKE_POSTCODE = "ab03"
PRE_SI_S4_WAKE_POSTCODE = "ab04"
PRE_SI_S5_WAKE_POSTCODE = "00ad"

POWER_SETTING_CONSTANT_MAX = 4294967295
PWR_SET_MIN = 0
PWR_SET_MAX = 100
PWR_SET_FIRST_LEVEL = 1
PWR_SET_SECOND_LEVEL = 2
PWR_SET_THIRD_LEVEL = 3
SUBPROCESS_RETURN_TIME = 2
SYSTEM_PATH = "C:\windows\system32"
BAUDRATE = 115200
DEBUG_TOOL = "PUTTY"
DEBUG_COUNTER = 25000
DEBUG_FLASH_DELAY = 900
FLASH_TIMEOUT = 1500
NORMAL_FLASH_DELAY = 120
BT_OFF = 300
BT_ON = 301
SIKULI_EXECUTION_TIME = 10
ONE_KB = 1024
FOUR_KB = 4096
ZERO = 0
ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SEVEN = 7
EIGHT = 8
HUNDRED = 100
TOKEN_LENGTH = 3
ONE_EIGHTY_ONE = 181
RELAY_COUNT = 8
FULL_CHARGE = 100
CRITICAL_CHARGE = 10
TEN = 10
TWENTY = 20
AUDIO_PASS_PERCENTAGE = 97
VIDEO_PASS_PERCENTAGE = 92.2
VIDEO_PASS_SSIM = 265
BRIGHTNESS_MAX_VALUE = 100
BRIGHTNESS_NEG_CHECK = 0
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100
INPUT_BLOCK_TIME = 0.05

AUDIO_FORMAT = ["mp3", "wav", "wmv", "aac", "ogg", "audio"]
VIDEO_FORMAT = ["mp4", "mkv", "avi", "3gp", "mpg", "vob", "flv", "webm",
                "video", "1080p", "720p"]
JUMPER_DEFAULT={'J3B1':'2,3', 'J3B2':'2,3', 'J4A2':'1,2', 'JUMPER':'1,2'}

RECORDED_VIDEO_SIZE = 1048576000
FRAME_DROP = 0
FRAME_DUP = 50
UNIGINE_HEAVEN_DURATION = 310
UNIGINE_VALLEY_DURATION = 250
UNIGINE_VALLEY_CMD = \
    "start launcher_x86.exe -config ../data/launcher/launcher.xml"
UNIGINE_HEAVEN_CMD = \
    "start browser_x86.exe -config ../data/launcher/launcher.xml"
UNIGINE_RUN_KEY = 'F9'
UNIGINE_VALLEY_BENCHMARK_EXE = 'taskkill /f /im Valley.exe'
UNIGINE_VALLEY_BROWSER_EXE = 'taskkill /f /im browser_x86.exe'
UNIGINE_HEAVEN_BENCHMARK_EXE = 'taskkill /f /im Heaven.exe'
UNIGINE_HEAVEN_BROWSER_EXE = 'taskkill /f /im launcher_x86.exe'
FIND_ALL_DEVICE_LIST_CMD = 'devcon.exe Find * > devices.txt'
FIND_HIDDEN_DEVICE_LIST_CMD = 'devcon.exe FindAll * > devices_hidden.txt'
FIND_ALL_HWIDS = 'devcon.exe hwids * > dump.txt'
IP_DETAILS_CMD = 'ipconfig /all > ipdetails.txt'
GRAY_SCALE = 128
GRAY_SCALE_MAX = 255
SKYCAM_IMX = "IMX135"
SKYCAM_OV = "OV2740"
NUMPY_ARRAY =[[0.393, 0.769, 0.189], [0.349, 0.686, 0.168],
              [0.272, 0.534, 0.131]]
HEX_FF = 0xff
BIOS_UPDATE_CMD = "BIOSConf.exe updateq "
COL_TWO = 2
COL_THREE = 3
COL_FOUR = 4
COL_FIVE = 5
COL_SIX = 6
DELAY = 30
BIT_MAX_RANGE = 255
BIT_MIN_RANGE = 0
HWAPI_DATA_ELEMENT_SIZE = 4
HEX_BASE_VALUE = 16
DECIMAL_BASE_VALUE = 10
BINARY_BASE_VALUE = 2
HWAPI_STARTBIT = 0
HWAPI_ENDBIT = 8
HYPER_V_ENABLE_CMD =\
    "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All"
EVENT_VIEWER_LOG_CMD ='''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    Where-Object {$_.entryType -Match "INFO"} '''
EVENT_IGNORE = "luafv service failed"
SPIERASE_STRT_ADDRESS=0x0
SPIERASE_LENGTH=0x1000000
POSTCODE_OS = "1414"
POSTCODE_EDK = "009a"

POSTCODE_ICL_OS_FASTBOOT_LIST = ['ffff', '1096', '10a7', '1092', '109a',
                                 '10a7', '1092', '10a7', '0e25', '10ad', '0000']
POSTCODE_CML_OS_FASTBOOT_LIST = ['ffff', '1096', '10a7', '1092', '109a',
                                 '10a7', '1092', '10a7', '0e25', '10ad', '0000']
POSTCODE_ICL_OS_FULLBOOT_LIST = ['ffff', '1096', '10a7', '1092', '109a',
                                 '10a7', '1092', '10a7', '0e25', '10ad', '0000']
POSTCODE_CML_OS_FULLBOOT_LIST = ['ffff', '1096', '10a7', '1092', '109a',
                                 '10a7', '1092', '10a7', '0e25', '10ad', '0000']

POSTCODE_KBL_OS_LIST = ['ffff', '0b7f', 'dd26', '0b00', '0b0f', '0094', '0096',
                        '0005', '0b7f', 'dd5d', '0055', '0c09','0b0e', '0c40',
                        '0e02', '0e22', '004f', '0b47', '0036', '0e24', '0090',
                        '009c',  '00a7', '00b4', '0e05', '00ad', '0003', '0b03',
                        '0c00', '0c28', '0c7f', '00e3', 'ab03', '0000']

POSTCODE__KBL_EDK_LIST = ['0e22', '004f', '0b47', '0036', '0e24', '0094',
                          '0096', '009c', '00a7', '00b4','0e05', '0e25', '00ad',
                          '009a']

POSTCODE_KBL_OS_FASTBOOT_LIST = ['ffff', '0c20', 'dd26', '0055', '0c09', '0b03',
                                 '0a63', '0e22', '004f', '0b47', '0036', '0e24',
                                 '0096', '009c', '00a7', '0e25', '00ad', '00b4',
                                 '0000']

POSTCODE_APL_OS_FASTBOOT_LIST = ['null']

POSTCODE_APL_OS_LIST = ['0015',	'0c6b',	'0049',	'0035',	'0c6e',	'847f',	'0031',
                        '0020',	'0c84',	'18a0',	'0c3a',	'0c2f',	'0c6a',	'0c6c',
                        '0b01',	'ffff', '009a',	'0c6f',	'ece4',	'00b4',	'0069',
                        '0b10', 'c151',	'0036',	'0000', '009c',	'0c37',	'00ad',
                        '0c38', '0094', '00a7', '0215', '0099', '0096', '0095',
                        '0083', '0050', '0010', '0b08', '0c4f', '0090', '0091',
                        '02e0', '0279']

POSTCODE_APL_EDK_LIST = ['0083', '0a63', '0036', '0b05', '0049', '0035', '0c6e',
                         '0031', '0020', '0c84', '18a0', '004b', '0c3a', '0c2f',
                         '0c6a', '0c6c', '0b01', 'ffff', '009a', '0c6f', 'ece4',
                         '00b4','0069', '0b10', 'c151', '0000', '0c37', '0a0b',
                         '0b0a', '0c38', '00a7', '00a4', '0099', '0076', '0096',
                         '0095', '0094', '0091', '0090', '00ad']

POSTCODE_GLK_OS_LIST = ['0000', '000c', 'db10', 'db13', '0093', '9C0F', '9C6F',
                        'ECE4', 'C151', '0035', '0091', '0099', '0096', '009A',
                        '00b4', '00Ad', '0287', '0235', '0215']

POSTCODE_GLK_OS_FASTBOOT_LIST = ['0000', '000c', 'db10', '0093', '18A0', '9c38',
                                 'c5c6', 'ece4', 'c151', '0035', '0090', '0099',
                                 '0096', '009c', '00a7', '00ad', '0215']

POSTCODE_CFL_OS_LIST = ['ffff', '2507', '0040', '007f', 'db49', 'dd00', 'dd5c',
                        'dd5d', '0055', 'd87f', 'b87f', 'd600', '957f', '0c00',
                        '967f', '9c09', '9b08', '9c18', '9c40', '9c7f', '004f',
                        '757f', '0e24', '767f', '8600', '867f', '1090', '1094',
                        '1096', '10a7', '1092', '109a', '10a7', '1092', '10a7',
                        '0e25', '10ad', '0000']
POSTCODE_OS_BOOT_SEQUENCE_LIST = ['dd06','0040', '007f', 'db49', 'dd00', 'dd05','dd5c',
                        'dd5d', '0055', 'd87f', 'b87f', 'd600', '957f', '0c00',
                        '967f', '9c09', '9b08', '9c18', '9c40', '9c7f', '004f',
                        '757f', '0e24', '767f', '8600', '867f', '1090', '1094',
                        '1096', '10a7', '1092', '109a', '10a7', '1092', '10a7',
                        '0e25', '10ad', '0000']

CURSOR_POS = 550
CURSOR_POS_DEFAULT = 500
LOGICAL_DISK_CMD= "wmic logicaldisk get caption, volumename"
DRIVE_NAME = "wmic logicaldisk get description,name > drive.txt"
HOST_SUT_DRIVE_MAP = 'z:\\'
ENTER_ASCII = 13
SET_BOOT_ORDER_CMD = "bcfg boot mv 1 0"
KEY_PRESS_COMMANDS_IN_EFI = ["RESET -S", "RESET -C", "RESET -W", "CTRL+ALT+DELETE"]
READ_INTEL_SPEED_STEP_ENABLED_BIG = "/BIOS/Intel Advanced Menu/Power & " \
    "Performance/CPU - Power Management Control/Intel(R) SpeedStep(tm) = " \
    "Enabled"
SET_INTEL_SPEED_STEP_DISABLED_BIG = "/BIOS/Intel Advanced Menu/Power & " \
    "Performance/CPU - Power Management Control/Intel(R) SpeedStep(tm) = " \
    "Disabled"
SET_INTEL_SPEED_STEP_DISABLE_SMALL = "/BIOS/Device Manager/System Setup/"\
    "CPU Configuration/CPU Power Management/Intel(R) SpeedStep(tm) = Disable"
READ_INTEL_SPEED_STEP_ENABLE_SMALL = "/BIOS/Device Manager/System Setup/"\
    "CPU Configuration/CPU Power Management/Intel(R) SpeedStep(tm) = Enable"

ENABLE = "01"
DISABLE = "00"
SEND_KEY_SET_BATTERY=["Alt+Ctrl+Shift+1", "Alt+Ctrl+Shift+-",
                      "Alt+Ctrl+Shift+-"]
SMBIOS_FVI_TABLE_NAME = "Firmware Version"
NON_REWORKED_DEVICES = ["3.5mm-Jack-Headset", "BT-Dongle", "BT-Keyboard",
                        "BT-Module", "BT-Mouse", "3G-SIM", "4G-SIM"]
USB_STORAGE_DEVICES = ["NonType-C-USB3.1-Pendrive", "SD-Card2.0", "SD-Card3.0",
                       "TBT-USB3.0-Pendrive", "Type-C-USB3.0-Pendrive",
                       "Type-C-USB3.1-Pendrive", "USB2.0-HDD", "SD-Card4.0",
                       "USB2.0-Pendrive", "USB3.0-Pendrive", "USB-Pendrive",
                       "Type-C-USB2.0-Pendrive", "C-USB-Mouse", "USB3.1-SSD",
                       "Type-C-Pendrive", "TBT-SSD1", "TBT-SSD2", "TBT-SSD3",
                       "TBT-SSD4", "TBT-SSD5", "USB3.0-HDD",
                       "Type-C-USB3.1-Gen2-SSD", "USB3.1-Gen2-SSD"]
MEINFO_DUMP = "MEInfoWin64.exe -FWSTS > MEInfodump.txt"
HIBERNATE_REGISTRY_PATH = r"SYSTEM\\CurrentControlSet\\Control\\Power"
HIBERNATE_REGISTRY_KEY="HibernateEnabledDefault"
HIBERNATE_FAILURE_CODE="0xc000007f"
HIBERNATE_ENABLE_REGISTRY_VALUE=1
HIBERNATE_DISABLE_REGISTRY_VALUE=0
SUBPROCESS_SUCESS_VALUE=0
REGISTRY_UPDATE_CMD = "regedit /s"
AC_MODE=2
DC_MODE=3
EFI_SECURITY_DISABLE =\
    "setvar SecureBootEnable -guid F0A30BC7-AF08-4556-99C4-001009C93A44 =00"
EFI_SECURITY_ENABLE =\
    "setvar SecureBootEnable -guid F0A30BC7-AF08-4556-99C4-001009C93A44 =01"
SATA_DEVICE =\
    'BIOS/Intel Advanced Menu/PCH-IO Configuration/SATA Configuration/' \
    'Software Preserve: SUPPORTED/SATA Device Type'
BIOS_BGUP_IMAGE = ["DEBUG", "RELEASE", "PROD", "PREPROD", "PERFORMANCE",
                   "NR-PERFORMANCE"]
BIOS_TEST_IMAGE = "TEST"
IFWI_IMAGE = ["CONFIG-","RELEASE","DEBUG","PERFORMANCE","CORPORATE",
                 "CONSUMER","RELEASE-FSP","DEBUG-FSP","PERFORMANCE-FSP"]
POWERSHELL_PERMISSION = \
    "powershell.exe Set-ExecutionPolicy Unrestricted -force"

######################## BIOS Setting for CS for KBL ###########################
LOWPOWERS0IDLECAPABILITY = "/Bios/Intel Advanced Menu/ACPI Settings/Low " \
    "Power S0 Idle Capability=Enabled"
CSMCONTROL = "/Bios/Boot Maintenance Manager Menu/Boot Configuration Menu/" \
    "CSM Control=Always OFF"
RTD3SUPPORT = "/Bios/Intel Advanced Menu/RTD3 settings/RTD3 Support=Enabled"
SDCARD3CONTROLLER = "/Bios/Intel advanced menu/PCH-IO Configuration/" \
    "SCS Configuration/SDCard 3.0 Controller=Disabled"
IUERBUTTONENABLE = "/Bios/Intel Advanced Menu/System Agent (SA) Configura" \
    "tion/Graphics Configuration/IUER Button Enable=Enabled"
XDCISUPPORT = "/Bios/Intel Advanced Menu/PCH IO Configuration/USB Configura" \
    "tion/xDCI Support=Disabled"
IUERSLATEENABLE = "/Bios/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/Intel(R) Ultrabook Event Support/" \
    "IUER Slate Enable=Enabled"
IUERDOCKENABLE = "/Bios/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/Intel(R) Ultrabook Event Support/" \
    "IUER Dock Enable=Enabled"
TENSECPOWERBUTTONOVR = "/Bios/Intel Advanced Menu/ACPI Settings/10sec Power " \
    "Button OVR=Enabled"
PEPSATA = "/Bios/Intel Advanced Menu/ACPI Settings/PEP Constraints " \
    "Configuration/PEP SATA Controller=Disabled"

######################## BIOS Setting for CS for APL############################
MANDATORY_CS_SETTINGS_APL = \
    ["/BIOS/Device Manager/System Setup/ACPI Settings/Low Power S0 Idle "
     "Capability = Enable",
     "/BIOS/Device Manager/System Setup/RTD3 settings/RTD3 Support = Enabled"]
SECONDARY_CS_SETTINGS_APL = \
    ["/BIOS/Device Manager/System Setup/Debug Configuration/NPK Debug "
     "Configuration/North Peak enable = Disable",
     "/BIOS/Device Manager/System Setup/South Cluster Configuration/LPSS "
     "Configuration/LPSS IOSF PMCTL S0ix Enable = Enable",
     "/BIOS/Device Manager/System Setup/South Cluster Configuration/PCI "
     "Express Configuration/PCI Express Root Port 5/PCI Express Root Port 5 "
     "= Disable",
     "/BIOS/Device Manager/System Setup/South Cluster Configuration/PCI "
     "Express Configuration/PCI Express Root Port 6/PCI Express Root Port 6 "
     "= Disable",
     "/BIOS/Device Manager/System Setup/South Cluster Configuration/HD-Audio "
     "Configuration/HD-Audio Power Gating = Enable",
     "/BIOS/Device Manager/System Setup/South Cluster Configuration/HD-Audio "
     "Configuration/HD-Audio DSP = Enable"]

######################## BIOS Setting for RTD3##################################
NATIVEASPM = "/Bios/Intel Advanced Menu/ACPI Settings/Native ASPM=Enabled"
GFXLOWPOWERMODE = "/Bios/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/Gfx Low power Mode=Enabled"
PMSUPPORT = "/Bios/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/PM support=Enabled"
I2C0SENSORHUB = "/Bios/Intel Advanced Menu/RTD3 settings/I2C0 Sensor " \
    "Hub=Enabled"
SATAPORT1 = "/Bios/Intel Advanced Menu/RTD3 settings/SATA Port 1=Enabled"
SATAPORT2 = "/Bios/Intel Advanced Menu/RTD3 settings/SATA Port 2=Enabled"
SATAPort1DevSlp = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SATA And RST ConfigurationPort/SATA Port 1 DevSlp=Enabled"
SATAPort2DevSlp = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SATA And RST ConfigurationPort/SATA Port 2 DevSlp=Enabled"

######################## BIOS Setting for DMOS & CMOS ##########################
EXTERNALKIT = "/Bios/Intel AdvancedMenu/PCH-IO Configuration/" \
    "HD Audio Configuration/HDA-Link Codec Select=External Kit"
HDAUDIOLINKFREQUENCY = "/Bios/Intel Advanced Menu/PCH-IO Configuration" \
    "/HD Audio Configuration/HD Audio Advanced Configuration/" \
    "HD Audio Link Frequency=6 MHz"
SDCARDSIDEBANDEVENTS = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SCS Configuration/SDCard Sideband Events=Use GPP_B17"
CONNECTEDDEVICE = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SerialIo Configuration/Serial IO I2C0 Settings/" \
    "Connected device=Synaptics Precision Touchpad"
SPI1CONTROLLER = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SerialIo Configuration/SPI1 Controller=Enabled"
FINGERPRINTSENSOR = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SerialIo Configuration/IO SPI1 Settings/Finger Print Sensor=FPC1020"
DPTFSUPPORT = "/Bios/Intel Advanced Menu/Thermal Configuration/" \
    "DPTF Configuration/DPTF=Enabled"
CONNECTEDDEVICEI2C1 = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "SerialIo Configuration/Serial IO I2C1 Settings/" \
    "Connected device=Atmel3432 TouchPanel"
TENSECPOWERBUTTONOVR = "/Bios/Intel Advanced Menu/ACPI Settings/" \
    "10sec Power Button OVR=Enabled"

########################Setting for perform p - state###########################
INTEL_SPEEDSHIFT_TECHNOLOGY = "/Bios/Intel Advanced Menu/Power & Performance/" \
    "CPU - Power Management Control/Intel(R) Speed Shift Technology=Disabled"

######################## BIOS Setting for GLK###################################
TURBOBOOSTTECHNOLOGY = "/Bios/Device Manager/System Setup/CPU Configuration/" \
    "CPU Power Management/Intel(R) Turbo Boost Technology = Enable"
PCIEXPRESS = "/Bios/Device Manager/System Setup/South Cluster Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 5/" \
    "PCI Express Root Port 5 = Disable"
DPTFSET = "/Bios/Device Manager/System Setup/Thermal/DPTF = Enable"
KERNELDEBUGGER = "/Bios/Device Manager/System Setup/Debug Configuration/" \
    "Kernel Debugger Enable = Disable"
LOWPOWERS0IDLE = "/Bios/Device Manager/System Setup/ACPI Settings/" \
    "Low Power S0 Idle Capability = Enable"

#################### BIOS Setting for KBL/R-WOL ################################
LOW_ON_DC_POWER = "/Bios/Intel Advanced Menu/PCH-IO Configuration/SLP_LAN# " \
    "Low on DC Power = Disabled"
WAKE_ON_WLAN = "/Bios/Intel Advanced Menu/PCH-IO Configuration/Wake on WLAN " \
    "and BT Enable = Enabled"

######################## BIOS Setting for TBT###################################
THUNDERBOLT_SUPPORT = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configura" \
    "tion/Thunderbolt(TM) Support=Enabled"
AIC_SUPPORT = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "AIC Support=Enabled"
AR_AIC_SUPPORT = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "AR AIC Support=Enabled"
SECURITY_LEVEL = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "Security Level=No Security"
ENABLE_CLK_REQ = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "Enable CLK REQ=Enabled"
ENABLE_ASPM = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "Enable ASPM=L1"
GPIO_FILTER = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "GPIO filter=Enabled"
TBT_ROOT_PORT_SELECTOR = "/Bios/Intel Advanced Menu/" \
    "Thunderbolt(TM) Configuration/TBT Root port Selector=" \
    "PCH-PCI Express Root Port 1"
TBT_ROOT_PORT_SELECTOR_PORT_9 = "/Bios/Intel Advanced Menu/" \
    "Thunderbolt(TM) Configuration/TBT Root port Selector=" \
    "PCH-PCI Express Root Port 9"
TBT_HOST_ROUTER = "/Bios/Intel Advanced Menu/Thunderbolt(TM) Configuration/" \
    "TBT Host Router=Two port"
ABOVE_4GB_MMIO_BIOS_ASSIGNMENT= "/Bios/Intel Advanced Menu/" \
    "System Agent (SA) configuration/Above 4GB MMIO BIOS assignment=Enabled"
ASPM = "/Bios/Intel Advanced Menu/PCH-IO Configuration/PCI Express " \
    "Configuration/PCI Express Root Port 1/ASPM=L1"
Ll_SUBSTATES = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 1/L1 Substates=Disabled"
GEN3_EQ_PHASE3_METHOD = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 1/Gen3 Eq Phase3 " \
    "Method=Hardware"
DPTP = "/Bios/Intel Advanced Menu/PCH-IO Configuration/PCI Express Configu" \
    "ration/PCI Express Root Port 1/DPTP=5"
ASPM_PORT_9 = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 9/ASPM=L1"
Ll_SUBSTATES_PORT_9 = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 9/L1 Substates=Disabled"
GEN3_EQ_PHASE3_METHOD_PORT_9 = "/Bios/Intel Advanced Menu/PCH-IO Configu" \
    "ration/PCI Express Configuration/PCI Express Root Port 9/Gen3 Eq Phase3 " \
    "Method=Hardware"
DPTP_PORT_9 = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "PCI Express Configuration/PCI Express Root Port 9/DPTP=5"

######################## BIOS Setting for CPU_frequency_for_all_p-state ########
TURBOMODE_INTELSPEEDSHIFT = ["0006 005C 0078 0030 0030 0032 0044 ONE_OF 00",
                             "0006 005C 0078 0030 0030 0031 0044 ONE_OF 00"]

#####################BIOS SETTINGS FOR FFT FLASHING############################
BIOS_GUARD_CNL= "/Bios/Intel Advanced Menu/CPU Configuration/BIOS Guard" \
    "/BIOS Guard=Disabled"
BIOS_GUARD = "/Bios/Intel Advanced Menu/CPU Configuration/BIOS Guard=Disabled"
FLASH_WEAR_OUT_PROTECTION = "/Bios/Intel Advanced Menu/CPU Configuration/Flash"\
    " Wear Out Protection=Disabled"
RTC_LOCK = "/Bios/Intel Advanced Menu/PCH-IO Configuration/Security "\
    "Configuration/RTC Lock=Disabled"
BIOS_LOCK = "/Bios/Intel Advanced Menu/PCH-IO Configuration/Security "\
    "Configuration/BIOS Lock=Disabled"
ENABLE_TOOLS_INTERFACE_CNL = "/Bios/Intel Advanced Menu/CPU Configuration/" \
    "BIOS Guard/Enable Tools Interface=Enabled"

#####################BIOS SETTINGS FOR BGUP FLASHING############################
ENABLE_BIOS_GUARD = "/Bios/Intel Advanced Menu/CPU Configuration/" \
    "BIOS Guard=Enabled"
ENABLE_BIOS_GUARD_CNL = "/Bios/Intel Advanced Menu/CPU Configuration/" \
    "BIOS Guard/BIOS Guard=Enabled"

#####################BIOS SETTINGS STATE AFTER G3###############################
STATE_AFTER_G3 = "/Bios/Intel Advanced Menu/PCH-IO Configuration/" \
    "State After G3=S5 State"
APL_STATE_AFTER_G3 = "Read Bios /BIOS/Device Manager/System Setup/" \
    "Miscellaneous Configuration/State After G3=S5 State"

##############################Capsule update####################################
GLK_BIOS_LOCK = "Bios/Device Manager/System  Setup/South Cluster Configu" \
    "ration/Miscellaneous Configuration/BIOS Lock = Disabled"
GLK_FlASH_PROTECTION = "Bios/Device Manager/System Setup/South Cluster " \
    "Configuration/Miscellaneous Configuration/Flash Protection Range " \
    "Registers (FPRR) = Disabled"
CAPSULE_UPDATE_TESTSIGNING = "bcdedit /set testsigning on"
CAPSULE_UPDATE_TESTSIGNING_VERIFY = "bcdedit > bcdedit.txt"
GLK_IFWI_VER = "Bios/Device Manager/System Setup/Main/IFWI Version"
GLK_KSC_VER = \
    "Bios/Device Manager/System Setup/Main/Platform Information/KSC FW"
CAPSULE_FILE = "capsule_command_log"
CAPSULE_FOLDER = "SysFwCapsule"
CAPSULE_BIN = "biosupdate.fv"
CAPSULE_FILE_SDRIVE = "S:\\biosupdate.fv"
CAPSULE_SEARCH_PARAM = "capsule driver created successfully"
FTRR = "/Bios/Intel Advanced Menu/PCH-IO Configuration/Flash Protection " \
    "Range Registers (FPRR)=Disabled"

PWR_SHELL_CMD = "$ptt = get-wmiobject -namespace root/cimv2/security/microsofttpm win32_tpm \n"

CPU_GFX=   r"<TatScript><Version>1.0</Version><CMD>" \
           r"<ComponentName>CPU Component</ComponentName>" \
           r"<Command>StartWorkLoad</Command><NodeCount>1" \
           r"</NodeCount><NodeArg>CPU Power</NodeArg>" \
           r"<CommandName>Gfx</CommandName><Value>" \
           r"%s.000000</Value></CMD><CMD><ComponentName/>" \
           r"<Command>StartLog</Command><NodeCount>0" \
           r"</NodeCount><CommandName/><Value>0</Value>" \
           r"</CMD><CMD><ComponentName/><Command>Delay" \
           r"</Command><NodeCount>0</NodeCount>" \
           r"<CommandName/><Value>%s</Value></CMD><CMD>" \
           r"<ComponentName>CPU Component</ComponentName>" \
           r"<Command>StopWorkLoad</Command><NodeCount>1" \
           r"</NodeCount><NodeArg>CPU Power</NodeArg>"\
           r"<CommandName>Gfx</CommandName></CMD><CMD>" \
           r"<ComponentName/><Command>StopLog</Command>" \
           r"<NodeCount>0</NodeCount><CommandName/>" \
           r"<Value>0</Value></CMD></TatScript>"

CPU_CPU=   r"<TatScript><Version>1.0</Version><CMD>" \
           r"<ComponentName/><Command>StartLog" \
           r"</Command><NodeCount>0</NodeCount>" \
           r"<CommandName/><Value>0</Value></CMD>" \
           r"<CMD><ComponentName>CPU Component" \
           r"</ComponentName><Command>StartWorkLoad" \
           r"</Command><NodeCount>1</NodeCount>" \
           r"<NodeArg>CPU-Utilization</NodeArg><CommandName>"\
           r"CPU-All</CommandName><Value>%s</Value>" \
           r"</CMD><CMD><ComponentName/><Command>Delay"\
           r"</Command><NodeCount>0</NodeCount>" \
           r"<CommandName/><Value>%s</Value></CMD>" \
           r"<CMD><ComponentName>CPU Component" \
           r"</ComponentName><Command>StopWorkLoad" \
           r"</Command><NodeCount>1</NodeCount>" \
           r"<NodeArg>CPU-Utilization</NodeArg><CommandName>"\
           r"CPU-All</CommandName></CMD><CMD>" \
           r"<ComponentName/><Command>StopLog</Command>" \
           r"<NodeCount>0</NodeCount><CommandName/>" \
           r"<Value>0</Value></CMD></TatScript>"

####################BIOS SETTING FOR BIOS VERSION ##############################
PLATFORM_MENU = "/Bios/Platform Information menu/"
PLATFORM_NAME = " /Bios/Platform Information menu/Project Version"
################################################################################

try:
    WIN_VER = platform.uname()[2]

    if "64" in platform.uname()[4]:                                             # OS Architecute of the system
        OS_ARCH = "x64"
    else:
        OS_ARCH = "x86"

    NOOFCORES = os.environ.get('NUMBER_OF_PROCESSORS')                          # Number of physical cores EX: 2
    IPADDRESS = socket.gethostbyname(socket.gethostname())                      # Ip Address of the current system EX: 10.223.180.166

    if "64" in platform.uname()[4]: # OS Architecute of the system
        OS_ARCH = "x64"
        PROGRAMFILES = os.environ.get('PROGRAMFILES(X86)')
    else:
        OS_ARCH = "x86"
        PROGRAMFILES = os.environ.get('PROGRAMFILES')                           # gives programfile directory EX: C:\Program Files (x86)

    URRENTDIR = os.getcwd()                                                     # gives current working directory
    SCRIPTDIR = os.path.dirname(os.path.abspath(sys.argv[0]))                   # sys.path[0] # gives script dir EX: C:\Tests\PythonProgram"
    SCRIPTFULLPATH = os.path.realpath(__file__)                                 # gives script path along with py file name.
    UTILPATH = HOMEDRIVE + r"\\Automation\\utility\\utils"
    EPCSTOOLPATH = PROGRAMFILES + \
        r"\Intel Corporation\Intel(R) BIOS Configuration Tool"
    Epcsdir = EPCSTOOLPATH
    APPDESTDIR = HOMEDRIVE + r"\\Tests\\Apps"
    PYTHON = HOMEDRIVE + r"\\Python27\\python.exe"
    SET_GPIO_PORT =0
    SET_GPIO_DIRECTION=[1]
    SET_GPIO_INPUT_DIRECTION=[0]
    SET_GPIO_ON = [0]
    SET_GPIO_OFF=[1]
    WAIT_TIME =30
    PRE_SI_WAIT_TIME =120
    PRE_SI_SX_TIMEOUT = 400
    AC_SOURCES = ["AC", "ATX", "AC BRICK"]
    TYPEC_SOURCES = ["TYPEC-PD-60W", "TYPE-C-PD-CHARGER", "TYPE-C-CHARGER",
                     "TYPEC-PD-CHARGER"]

    ############################################################################
    #LOG LEVELS
    LOG_DEBUG = 0
    LOG_INFO = 1
    LOG_ERROR = 3
    LOG_WARNING = 2
    LOG_PASS = 4
    LOG_FAIL = 5

    ############################################################################
    #SYS_EXIT_VALUES
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1
    ############################################################################
    #INITIALIZE VALUES
    INITIALIZE_ZERO = 0
except Exception as e:
    with open(PARSERLOG, "a") as file_append:
        file_append.write("ERROR: due to %s\n"%e)

####################BIOS MEMORY_CONFIGURATION ##################################
MEMORY_CONFIGURATION_FH = "Bios/Intel Advanced Menu/Memory Configuration/" \
    "Memory Frequency"
MEMORY_CONFIGURATION_SZ = "Bios/Intel Advanced Menu/Memory Configuration/"

###################POWER_SHELL_COMMAND_SYSTEM_LOG###############################
BSOD_SHELL_COMMAND = '''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    ? {$_.eventid -eq '6008' -or $_.eventid -eq '1001'}'''

CS_SHELL_COMMAND = '''Clear-Host
                Get-Eventlog system -Newest 2000 |
                ? {$_.eventid -eq '507'}'''

C3_SHELL_COMMAND = '''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    Where-Object {$_.eventid -eq '1' -and $_.Source -Match
                    "Power-Troubleshooter"}'''

C4_SHELL_COMMAND = '''Clear-Host
                    Get-Eventlog system -Newest 2000 |
                    Where-Object {$_.eventid -eq '1' -and $_.Source -Match
                    "Power-Troubleshooter"}'''

RESTART_SHELL_COMMAND = '''Get-WinEvent -FilterHashtable @{logname='System';
                        id=1074}  | ForEach-Object {
                        $rv = New-Object PSObject | Select-Object Date, User,
                         Action, Process, Reason, ReasonCode, Comment
                        $rv.Date = $_.TimeCreated
                        $rv.User = $_.Properties[6].Value
                        $rv.Process = $_.Properties[0].Value
                        $rv.Action = $_.Properties[4].Value
                        $rv.Reason = $_.Properties[2].Value
                        $rv.ReasonCode = $_.Properties[3].Value
                        $rv.Comment = $_.Properties[5].Value
                        $rv
                        } | Select-Object Date, Action, Reason, User'''

SHUTDOWN_SHELL_COMMAND = '''Get-WinEvent -FilterHashtable @{logname='System';
                        id=1074}  | ForEach-Object {
                        $rv = New-Object PSObject | Select-Object Date, User,
                         Action, Process, Reason, ReasonCode, Comment
                        $rv.Date = $_.TimeCreated
                        $rv.User = $_.Properties[6].Value
                        $rv.Process = $_.Properties[0].Value
                        $rv.Action = $_.Properties[4].Value
                        $rv.Reason = $_.Properties[2].Value
                        $rv.ReasonCode = $_.Properties[3].Value
                        $rv.Comment = $_.Properties[5].Value
                        $rv
                        } | Select-Object Date, Action, Reason, User'''

DRIVER_VERSION_COMMAND = \
   '''powershell.exe Get-WmiObject Win32_PnPSignedDriver| select devicename, 
   driverversion'''

###########################Capsule update check#################################
CAPSULE_PARAMS = ["// Project Version:","// EC FW Version:","// ME FW Version:"]

#################################Write pci bdf##################################
BDF_HIGHBIT = 31
BDF_LOWBIT = 0

####################MSR#########################################################
MSR_LOWBIT = 31
TTK_COUNTER = 20
res = ""

PRIMARY_DISPLAY_CMD = '''Add-Type -AssemblyName System.Windows.Forms
                [System.Windows.Forms.Screen]::AllScreens |
                 Select-Object  BitsPerPixel, Primary |
      ?{($_.Primary -match 'True') -and ($_.BitsPerPixel -eq %s)}'''

SECONDARY_DISPLAY_CMD = '''Add-Type -AssemblyName System.Windows.Forms
                System.Windows.Forms.Screen]::AllScreens |
                Select-Object  BitsPerPixel, Primary |
      ?{($_.Primary -match 'False') -and ($_.BitsPerPixel -eq %s)}'''

BATTERY_PERCENTAGE_CMD = \
    '''(Get-WmiObject win32_battery).estimatedChargeRemaining'''

TPM_ENUMUERATION_CHECK = '''wmic /namespace:\\\\root\cimv2\security\
    \microsofttpm path win32_tpm get /value'''

#####################list_of_device_enumaration_in_device_manager###############
WMI_CHECK = ["SATA-HDD", "SATA", "SATA-SSD", "PS2-KEYBOARD", "PS2-MOUSE",
             "EDP-DISPLAY", "HDMI-DISPLAY", "DP-DISPLAY", "CAMERA-MODULE",
             "EMMC-MODULE","USB-CAMERA","GNSS-MODULE","SD-CARD2.0","SD-CARD3.0",
             "M.2-SSD","WWAN-MODULE","M.2-NVME-SSD","NVME-SSD","WIFI-MODULE",
             "M.2-SATA-SSD", "WIFI_BT_MODULE", "PCIE-NVME-SSD",
             "IR-CAMERA-MODULE", "FLASH-CAMERA-DEVICE", "IPU-CAMERA-MODULE"]

WMI_CHECK_PRESI = ["USB3.0-PENDRIVE","USB2.0-PENDRIVE"]

ONLY_ENUMERATION_CHECK = ["SATA-HDD", "SATA", "SATA-SSD","DTPM2.0",
                          "LPC-DTPM2.0","SPI-DTPM2.0","SPI-DTPM1.2",
                          "LPC-DTPM1.2","DTPM1.2","EMMC-MODULE","GNSS-MODULE",
                          "SD-CARD2.0","SD-CARD3.0","M.2-SSD","WWAN-MODULE",
                          "M.2-NVME-SSD","USB-CAMERA","NVME-SSD","WIFI-MODULE",
                          "M.2-SATA-SSD", "CNVI-CRF-MODULE", "WIFI_BT_MODULE",
                          "PCIE-NVME-SSD", "IR-CAMERA-MODULE","CAMERA-MODULE",
                          "FLASH-CAMERA-DEVICE", "IPU-CAMERA-MODULE"]

ONLY_ENUMERATION_CHECK_HOST = ['USB3.0-TYPE-C-TO-A-MALE-CABLE']

ONLY_PLUG_UNPLUG = ["OTG-CABLE", "TBT-TYPE-C-TO-A-DONGLE",
                    "TYPE-C-TO-A-DONGLE", "TYPE-C-TO-C-CABLE",
                    "TYPE-C-TO-A-HUB", "TYPE-C-TO-A-AUDIO-DONGLE",
                    "TYPE-C-TO-HDMI-DONGLE", "TYPE-C-TO-MDP-DONGLE",
                    "USB-TYPE-C-POWER-ADAPTER", "USB3.0-TYPEC-TO-TYPEC-CABLE"]

PHY_KEYBOARD = ["USB2.0-KEYBOARD", "USB-KEYBOARD", "USB3.0-KEYBOARD",
                "PS2-KEYBOARD","TYPE-C-USB-KEYBOARD"]

PHY_MOUSE = ["USB2.0-MOUSE", "USB-MOUSE", "USB3.0-MOUSE", "PS2-MOUSE"]

COLD_PLUG_SKY_CAM = ["Camera Sensor OV2740", "Camera Sensor IMX135"]

CAMERA_BIOS_SET1 =["0006 005C 0078 0030 0034 0041 0033 ONE_OF 01",
                   "0006 005C 0078 0031 0031 0035 0034 ONE_OF 01",
                   "0006 005C 0078 0031 0031 0035 0035 ONE_OF 01",
                   "0006 005C 0078 0031 0030 0031 0032 ONE_OF 01",
                   "0006 005C 0078 0031 0034 0033 0034 ONE_OF 01",
                   "0006 005C 0078 0031 0034 0033 0035 ONE_OF 01",
                   "0006 005C 0078 0063 0030 0066 0035 ONE_OF 01",
                   "0006 005C 0078 0063 0030 0066 0036 ONE_OF 01"]

CAMERA_BIOS_SET2 = ["0006 005C 0078 0063 0032 0065 0065 ONE_OF 02",
                    "0006 005C 0078 0063 0032 0065 0066 ONE_OF 30",
                    "0006 005C 0078 0063 0032 0066 0030 ONE_OF 21",
                    "0006 005C 0078 0063 0032 0066 0031 ONE_OF 02",
                    "0006 005C 0078 0063 0031 0031 0039 NUMERIC 004D"]

CAMERA_BIOS_SET3 = ["0006 005C 0078 0063 0033 0030 0034 ONE_OF 02",
                    "0006 005C 0078 0063 0033 0030 0035 ONE_OF 50",
                    "0006 005C 0078 0063 0033 0030 0036 ONE_OF 29",
                    "0006 005C 0078 0063 0033 0030 0037 ONE_OF 03",
                    "0006 005C 0078 0063 0033 0030 0038 NUMERIC 0049"]

CAMERA_BIOS_SET4 = ["0006 005C 0078 0063 0032 0035 0065 ONE_OF 04",
                    "0006 005C 0078 0063 0032 0035 0066 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0036 0030 ONE_OF 30",
                    "0006 005C 0078 0063 0032 0036 0031 ONE_OF 00",
                    "0006 005C 0078 0063 0031 0030 0066 ONE_OF 61",
                    "0006 005C 0078 0063 0032 0036 0032 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0036 0033 ONE_OF 00",
                    "0006 005C 0078 0063 0031 0031 0030 ONE_OF 02",
                    "0006 005C 0078 0063 0032 0036 0034 ONE_OF 0124F800",
                    "0006 005C 0078 0063 0032 0036 0035 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0036 0036 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0036 0037 NUMERIC 01",
                    "0006 005C 0078 0063 0032 0036 0038 ONE_OF 02",
                    "0006 005C 0078 0063 0031 0031 0036 NUMERIC 36",
                    "0006 005C 0078 0063 0031 0031 0037 ONE_OF 00"]

CAMERA_BIOS_SET5 = ["0006 005C 0078 0063 0032 0037 0066 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0038 0030 ONE_OF 03",
                    "0006 005C 0078 0063 0032 0038 0031 ONE_OF 50",
                    "0006 005C 0078 0063 0032 0038 0032 ONE_OF 01",
                    "0006 005C 0078 0063 0032 0038 0033 ONE_OF 69",
                    "0006 005C 0078 0063 0032 0038 0034 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0038 0035 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0038 0036 ONE_OF 04",
                    "0006 005C 0078 0063 0032 0038 0037 ONE_OF 0124F800",
                    "0006 005C 0078 0063 0032 0038 0038 ONE_OF 08",
                    "0006 005C 0078 0063 0032 0038 0039 ONE_OF 03",
                    "0006 005C 0078 0063 0032 0038 0061 NUMERIC 06",
                    "0006 005C 0078 0063 0032 0038 0062 ONE_OF 03",
                    "0006 005C 0078 0063 0032 0038 0063 NUMERIC 0010",
                    "0006 005C 0078 0063 0032 0038 0064 ONE_OF 00",
                    "0006 005C 0078 0063 0032 0038 0065 NUMERIC 000E"]

SET_REG_EDIT_WMP = '''
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\WindowsMediaPlayer \
/v GroupPrivacyAcceptance /f
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\WindowsMediaPlayer \
/v GroupPrivacyAcceptance /t REG_DWORD /d 00000001
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\MediaPlayer\Preferences \
/v FirstTime /f
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\MediaPlayer\Preferences \
/v FirstTime /t REG_DWORD /d 00000001
reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\MediaPlayer\Preferences \
/v AcceptedEULA /f
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\MediaPlayer\Preferences \
/v AcceptedEULA /t REG_DWORD /d 00000001
reg add "HKCU\Software\Microsoft\MediaPlayer\Preferences" \
/v "ModeLoop" /t REG_DWORD /d 1 /f
'''

ROTATION_LIST = ["90", "180", "270", "0"]
KB_REPEAT_DELAY= 'mode con: | findstr "keyboard delay"'
KB_REPEAT_RATE = 'mode con: | findstr "keyboard rate"'
KB_PROPERTY_SET = "mode con: rate=%s delay=%s"
KB_PROPERTY_GET = "mode con:"

LAN_CHECK_CMD = "wmic NIC where NetEnabled=true get Name"

FFMPEG_CHECK_DEVICE_CMD = '%s -list_devices true -f dshow -i dummy'

LOWER_RANGE = "0,31"
HIGH_RANGE = "32,63"

############################Sensor HUB######################################
SENSORDICT = {"PROXIMITY SENSOR": "0266000E00010002",
              "GYROMETER SENSOR": "0076000000000001",
              "INCLINOMETER SENSOR": "0086000000000000",
              "PHYSICAL ACCELEROMETER SENSOR": "0073000900070102",
              "COMPASS SENSOR": "0083000000000000",
              "SENSOR-HUB" : "0266000E00010002",
	          "AMBIENT LIGHT SENSOR": "0041001400010002",
              "ALS-SENSOR": "0041001400010002",
              "MAGNETOMETER SENSOR": "020F000000000001",
              "3D ACCELEROMETER SENSOR": "0073000000000000",
              "ACCELEROMETER SENSOR": "0073000000000000",
               "ISH-MODULE": "0266000E00010002",
              "BAROMETER SENSOR": "00310001000C0002", "GRAVITY SENSOR":"007B000000000000",
              "LINEAR ACCELERATION SENSOR": "007C000000000000",
			  "PEDOMETER SENSOR": "00B4000000000000",
              "PHYSICAL ACTIVITY SENSOR": "00B1000000000000",
              "HUMIDITY SENSOR": "00320001000D0002",
	      "LINEAR ACCELERATION GRAVITY SENSOR" : "007B000000000000",
              "GYROMETER SENSOR" : "0076000000000001",
              "SOFT GYROSCOPE SENSOR" : "0076000000000001"}

SENSORUIDDICT = {"ALTIMETER SENSOR" : "207322",
                 "DEVICEORIENTATION" : "207069",
                 "DEVICE ORIENTATION SENSOR" : "207069",
                 "SOFT GYROSCOPE SENSOR" : "206885",
                 "GYRO" : "206885"}

LAN_DEVICE_NAME = ['pcie-lan-x1', 'onboard-lan', 'usb-lan-adaptor',
                   'tbt-lan-dongle', 'pcie-lan-x4']

APL_MRC = '7EE44C61-ADDA-4D27-A4A3-A5615C16C644'

WLAN_PROFILE_XML = '''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
	<name>naresh</name>
	<SSIDConfig>
		<SSID>
			<hex>asdfaf</hex>
			<name>naresh</name>
		</SSID>
	</SSIDConfig>
	<connectionType>ESS</connectionType>
	<connectionMode>manual</connectionMode>
	<MSM>
		<security>
			<authEncryption>
				<authentication>WPA2PSK</authentication>
				<encryption>AES</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
			<sharedKey>
				<keyType>passPhrase</keyType>
				<protected>false</protected>
				<keyMaterial>password*123</keyMaterial>
			</sharedKey>
		</security>
	</MSM>
	<MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">
		<enableRandomization>false</enableRandomization>
		<randomizationSeed>2388630933</randomizationSeed>
	</MacRandomization>
</WLANProfile>'''

WLAN_NETSH_PROFILE_CMD = "netsh wlan add profile "
WLAN_NETSH_CONNECT_CMD = 'netsh wlan connect'
WLAN_DELETE_PROFILE_CMD ='netsh wlan delete profile name='
WLAN_SHOW_PROFILE_CMD = "netsh wlan show profiles"
WLAN_NETSH_AUTO_CHECK_CMD = 'netsh wlan set profileparameter name='

###########################CPU Load#############################################
LOAD_40 = "apply workload for 80 seconds with 50"
LOAD_50 = "apply workload for 200 seconds with 60"
LOAD_60 = "apply workload for 180 seconds with 60"
LOAD_70 = "apply workload for 180 seconds with 70"
LOAD_80 = "apply workload for 300 seconds with 80"
LOAD_90 = "apply workload for 300 seconds with 90"

################################Pre Load OS#####################################
host_share_drive = r'net share work=C:\Automation'
delete_z_drive = r'NET USE z: /DELETE /YES'
host_map_z_drive_sut = r'net use z: \\%s\Automation /user:%s %s /persistent:yes'
network_map_z_drive_sut = r'net use z: %s /user:%s %s /persistent:yes'
initialsetup_copy_to_sut = r'xcopy /I /S /E /Y %sInitialsetup %sInitialsetup'
host_utils_copy = r'xcopy /I /S /E /Y %s %s'

SUT_MAP_Z_DRIVE_HOST = r'net use z: \\%s\Automation /user:%s "" /persistent:yes'
map_z_drive = r'net use z: %s /user:%s %s /persistent:yes'
map_z_drive_without = r'net use z: %s /persistent:yes'
tools_class_method_name = ".tool.tool_all_operation"
BurnIn_key = "Intel Corporation#ANEAAMABEHN5ICZ999WU2UMW6IAKGIT6SNSM6U3JJ4MSG4"\
    "42QY24KFR2JAIVIA52ZDKAZGRNUCQ83A4XHMAQSYCC7IHMUUK36CJX2P9RINDZSKRP6WTCYISD"
GROOVE_PLAYER_CMD = \
    'cmd /c start "explorer.exe shell:C:\Program Files\WindowsApps\Microsoft.' \
    'ZuneMusic_3.6.25021.0_x64__8wekyb3d8bbwe!Microsoft.ZuneMusic"'

FAN_SPEED_PARAM1 = "ACPI MISC"
FAN_SPEED_PARAM2 = "CPU FAN #1 SPEED"
CPU_TEMP_PARAM1 = "DTS(DEGREE C)"
CPU_TEMP_PARAM2 = "CPU"
CPU_TEMP = "temperature"
CPU_SPEED = "fan speed"

BSOD_COMMAND = "NotMyfault.exe /bugcheck 0x2e"
GRAPHICS_REG_PATH = "HKEY_CLASSES_ROOT\Directory\Background\Shellex"
GRAPHICS_REG_VALUE = "{9B5F5829-A529-4B12-814A-E81BCB8D93FC}"
INF_COMMAND = "Pnputil.exe -i -a"
REG_QUERY_COMMAND = "REG QUERY "
WMD_COMMAND = "mdsched.exe"
WMD_ERROR_POWERSHELL = '''get-eventlog system -source Microsoft-Windows-
    MemoryDiagnostics-Results | Select EntryType,InstanceID,Message | 
    format-list'''
WMD_LOG_STRING = "The Windows Memory Diagnostic tested the computer's memory " \
    "and detected no errors"
WMD_TIME = 750
DEFAULT_PASS_COUNT = 2
SELFTEST_VALUE = ["HDDUNLOCK", "SW FEATURE MASK", "LED LOCATE"]

ETHDIS_PARAM1 = 'netsh interface set interface'
ETHDIS_PARAM2 = 'admin=disable'
WIFI_ENABLE = 'netsh interface set interface "Wi-Fi" admin=enable'
ETHEN_PARAM1 = 'netsh interface set interface'
ETHEN_PARAM2 = 'admin=enable'
WIFI_DISABLE = 'netsh interface set interface "Wi-Fi" admin=disable'

GNSS_ENABLE = "devcon.exe /r enable =Sensor"
GNSS_DISABLE = "devcon.exe /r disable =Sensor"

HDMI_PLUG_CMD = 'SHEUtilityTestApp.exe PLUG HDMI_1 15'
HDMI_UNPLUG_CMD = 'SHEUtilityTestApp.exe UNPLUG HDMI_1 15'
DP_PLUG_CMD = 'SHEUtilityTestApp.exe PLUG DP_1 15'
DP_UNPLUG_CMD = 'SHEUtilityTestApp.exe UNPLUG DP_1 15'
EDP_PLUG_CMD = 'SHEUtilityTestApp.exe PLUG EDP 15'
EDP_UNPLUG_CMD = 'SHEUtilityTestApp.exe UNPLUG EDP 15'
VGA_PLUG_CMD = 'SHEUtilityTestApp.exe PLUG HDMI_1 15'
VGA_UNPLUG_CMD = 'SHEUtilityTestApp.exe UNPLUG HDMI_1 15'

#######################BIOS Setting for DPTF w.r.t platform#####################
DPTF_KBL = "/Bios/Intel Advanced Menu/Thermal Configuration/DPTF Configuration"\
    "/DPTF=Enabled"
DPTF_GLK = "/Bios/Device Manager/System Setup/Thermal/DPTF=Enable"

#################################WOL SETTING####################################
WOL_SETTING_CMD = '''$namespace = "root\WMI"

Clear-Host

Write-Host "`nNIC Power Management settings`n"


Write-Host "Enable `"Allow the computer to turn off this device to save power`""
Get-WmiObject Win32_NetworkAdapter -filter "AdapterTypeId=0" | % {
  $strNetworkAdapterID=$_.PNPDeviceID.ToUpper()
  Get-WmiObject -class MSPower_DeviceEnable -Namespace $namespace | % {
    if($_.InstanceName.ToUpper().startsWith($strNetworkAdapterID)){
      $_.Enable = $true
      $_.Put() | Out-Null
    }
  }
}


Write-Host "Enable `"Allow this device to wake the computer`""
Get-WmiObject Win32_NetworkAdapter -filter "AdapterTypeId=0" | % {
  $strNetworkAdapterID=$_.PNPDeviceID.ToUpper()
  Get-WmiObject -class MSPower_DeviceWakeEnable -Namespace $namespace | % {
    if($_.InstanceName.ToUpper().startsWith($strNetworkAdapterID)){
      $_.Enable = $true
      $_.Put() | Out-Null
    }
  }
}

Write-Host "Enable `"Only allow a magic packet to wake the computer`""
Get-WmiObject Win32_NetworkAdapter -filter "AdapterTypeId=0" | % {
  $strNetworkAdapterID=$_.PNPDeviceID.ToUpper()
  Get-WmiObject -class MSNdis_DeviceWakeOnMagicPacketOnly -Namespace $namespace | % {
    if($_.InstanceName.ToUpper().startsWith($strNetworkAdapterID)){
      $_.EnableWakeOnMagicPacketOnly = $true
      $_.Put() | Out-Null
    }
  }
}'''

WOL_SETTING_S3_S4 = 'powercfg /hibernate ON'
WOL_SETTING_S5 = "Set registry HKEY_LOCAL_MACHINE\System\CurrentControl" \
    "Set\Control\Session Manager\Power HiberbootEnabled DWORD 0x0"
WOL_COMMAND_WAKEUP = "wol.exe"

STATE_AFTER_G3_SMALL_CORE = "/BIOS/Device Manager/System Setup/Miscellaneous " \
    "Configuration/State After G3 = S5 State"
CNL_STATE_AFTER_G3_BIG_CORE = "/BIOS/Intel Advanced Menu/PCH-IO Configuration"\
    "/State After G3 = S5 State"
SD_CARD_SIDEBAND_EVENTS_BIG_CORE = "/Bios/Intel Advanced Menu/PCH-IO Confi" \
    "guration/SCS Configuration/SDCard Sideband Events = Disabled"
SD_CARD_SIDEBAND_EVENTS_SMALL_CORE = ""
STATE_AFTER_G3_BIG_CORE = "/Bios/Intel Advanced Menu/PCH-IO Configura" \
    "tion/State After G3=S5 State"

BATTERY_CHARGE_DISCHARGE_WAIT_TIME = 10
BATTERY_CHARGE_DISCHARGE_COUNT = 60
BATTERY_CHARGE_DISCHARGE_DELTA = 3

MEBX_FILE_PATH = os.path.join(TOOLPATH + "\\" + "sikulix" + "\\" +
                              "mebx_latest.sikuli")
SSD_CARD_SIDEBAND_EVENTS_BIG_CORE = "/Bios/Intel Advanced Menu/PCH-IO Confi" \
    "guration/SCS Configuration/SDCard Sideband Events = Disabled"
HEXADECIMAL_CONVERTION = "#04X"
HYPER_V_DISABLE_CMD = "dism.exe /Online /Disable-Feature:Microsoft-Hyper-V /All"
HYPER_V_ENABLE_CMD = "dism.exe /Online /Enable-Feature:Microsoft-Hyper-V /All"
HYPER_V_OUTPUT_STATUS = "[===================100.0%======================]"
HYPER_V_OUTPUT = "The operation completed successfully."
UART_MESSAGE = 'FIRST'
KERNEL_DUMP_MODE = 0x00000002
KERNEL_DUMP_PATH = r"SYSTEM\CurrentControlSet\Control\CrashControl"
BIGCORE = ["KBL", "KBLR", "CNL"]
SMALLCORE = ["GLK", "APL"]

BIGCORE_BIOSVERSION = "/Bios/Platform Information menu/Bios " \
    "Information/Project Version"
SMALLCORE_BIOSVERSION = "/Bios/System Setup/Main/Bios Version"

IMAGE_FORMAT_TYPE = ['.jpg', '.gif', '.bmp', '.tiff','.png']
FILE_FORMAT_TYPE = ['.avi', '.mp3', '.mp4', '.flv', '.wmv','.ivs']

TOOLDIR = r'C:\\Testing\\GenericFramework\\tools\\DISPLAY'
DISPLAY_CMD = 'Execute.exe config get'
DISPLAY_FILE_PATH = r'C:\\Testing\\GenericFramework\\tools\\DISPLAY\\Dis' \
    r'playInfo.txt'

ONBOARD_SWITCHES = ["VIRTUAL BATTERY", "LID", "VIRTUAL-DOCK", "SW2H 1",
                    "SW2H 2"]

VGA_DISPLAY_CMD = 'Get-CimInstance -Namespace root\wmi -ClassName ' \
                  'wmimonitorbasicdisplayparams'

BIOS_CONFIG_COMMAND = "BIOSConf.exe updateq "

UART_USB_QUERY = "Select * From Win32_USBControllerDevice"

UART_CONNECTION = 'serial.Serial()'

UART_WMI_QUERY = 'wmi.WMI()'

BOOT_TO_MEBX = "Mebx"
chromedriverpath = 'C:\Python27\Lib\site-packages\selenium-2.7.0-py2.7.' \
    'egg\selenium\webdriver\chrome\chromedriver.exe'
logonbutton = 'body > form > h2 > input[type="submit"]'
refreshbutton = 'body > table.spread > tbody > tr > td.maincell > table > ' \
    'tbody > tr:nth-child(14) > td:nth-child(1) > form > ' \
    'input[type="submit"]'

SX_STATES = ["S3", "S4", "S5"]
PWRTEST_LOG_PATH = r"C:\\Testing\\GenericFramework\\tools\\Windows " \
    r"Kits\\10\\Tools\\x64\\pwrtestlog.log"
PWRTEST_TOOL_CMD = 'pwrtest.exe'
SX_SLEEP_TIME = 300

MERGE_TXT_FILE = "for %f in (*.txt) do type %f >> "
DELETE_TXT_FILE = "del /s *.txt"
CMD_TO_RUN = "map -r"

GET_INFO = "wmic logicaldisk get deviceid, volumename, description > "
BOOTABLE_FILES = ["bootx64.efi", "bootmgfw.efi", "bootmgr.efi", "memtest.efi"]
WMIC_LOGICAL_DISK_COMMAND = "wmic logicaldisk get caption, volumename"\
    " > logfile.txt"
NONBOOTABLE_DEVICES = ["USB3.0-NONBOOTABLE-PENDRIVE",
                       "USB3.1-NONBOOTABLE-PENDRIVE"]
BOOTABLE_DEVICES = ["TYPE-C-USB3.0-BOOTABLE-PENDRIVE"]

TRACEHUB = "/Bios/Intel Advanced Menu/Debug Settings/Advanced Debug Settings/" \
    "PCH Trace Hub Enable Mode = Target Debugger"

device_info = "devcon_x64.exe drivernodes"

USB_HUB = ["USB-HUB"]
S3_LED = "0111"
S4_LED = "0011"
S5_LED = "0001"
DEEPS3_LED = "0110"
DEEPS4_LED = "0010"
DEEPS5_LED = "0000"
SX_LED_OFF = "1111"
DEEPSX = ["DEEPS3", "DEEPS4", "DEEPS5"]

##################Get package temperature of cpu/read temperature of cpu########
GET_CPU_PKG_TEMPERATURE = "rdpkgconfig index:2 parameter:255 "\
    "log:peci_gettemp.csv unattended"
GET_CPU_TEMPERATURE = "gettemp log:peci_gettemp.csv unattended"
GET_PCH_DTS_TEMPARATURE = "-AU=Y -t=30"
GET_TEMP_VALUE = 6

############################Verify NVME-SSD Functionality #####################
DEVCON_PATH = r"C:\\Testing\\GenericFramework\\tools\\devcon"
COPY_CMD = "xcopy /i /y "

################################Debug cables####################################
DEBUG_CABLES = ["SERIAL-CABLE", "USB2.0-DEBUG-CABLE", "USB-2.0-DEBUG-CABLE",
                "USB3.0-DEBUG-CABLE","SERIAL-TO-USB-CABLE", "SERIAL-DEBUG-CABLE"]

##################INITIAIZE ONLINE VIDEO AND PERFORM SX#########################
OFFLINE_MEDIA_TYPE = ["VIDEO", "AUDIO"]

##############################xml cli###########################################
XML_CLI_ONLINE_LOGPATH = r"C:\\Testing\\GenericFramework\\tools\\pysvtools." \
                         r"xmlcli\\pysvtools\\xmlcli\\out" \
                         r"\\PlatformConfig-online.xml"
XML_CLI_OFFLINE_LOGPATH = r"C:\\Testing\\GenericFramework\\tools\\pysvtools." \
                          r"xmlcli\\pysvtools\\xmlcli\\out" \
                          r"\\PlatformConfig-offline.xml"
XML_CLI_LOG_PATH = r'C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli' \
                   r'\\pysvtools\\xmlcli\\out\\XmlCli.log'
BIOS_INFO = "Bios Information"
FASP_INFO = "Fsp Information"
BOARD_INFO = "Board Information"
PROCESSOR_INFO = "Processor Information"
PCH_INFO = "Pch Information"
LAST_PARAM = "Debug Settings"
POWER_LEVEL = "Config Tdp Configurations"
CUSTOM_PARAM = "Custom Settings Nominal"
CPU_INFO = "Cpu Configuration"
CPU_SSE = "Cpu Smm Enhancement"
CPU_CONF = "Cpu Configuration"
POWER_LIMIT = "Power Limit 1"
MEM_CONF="Memory Configuration"
GRAPHIC_CONF="Graphics Configuration"
PTT_CONF = "Ptt Configuration"
SYS_AGENT = "System Agent (SA) Configuration"

COM_LIST = [BIOS_INFO, FASP_INFO, BOARD_INFO, PROCESSOR_INFO, PCH_INFO,
            SYS_AGENT, LAST_PARAM, POWER_LEVEL, CUSTOM_PARAM, CPU_INFO,
            CPU_SSE, CPU_CONF, MEM_CONF, GRAPHIC_CONF, PTT_CONF]
XML_CLI_LOG_MESG="Verify Passed!"
XML_CLI_LOG_MESG_PWD_ERR = "New password is not strong enough!"
XML_CLI_LOG_MESG_PWD_SET = "New password is updated successfully"
TBD_PLATFORM = ["GLK"]
XML_CLI_TBD_PLATFORM = ["CFL", "CNL", "TGL", "ICL", "KBL", "KBLR", "LKF", "CML"]
BOARD_NAME = "/BIOS/Platform information Menu/Processor Information/Name"
BOARD_PCH_NAME = "/BIOS/Platform information Menu/PCH Information/Name"
LOW_POWER_CAPABILITY = "/BIOS/Intel Advanced Menu/ACPI Settings/Low Power " \
    "S0 Idle Capability = Enabled"
POWER_BUTTON_OVR = "/BIOS/Intel Advanced Menu/ACPI Settings/10sec Power " \
    "Button OVR = Enabled"
KBL_POWER_BUTTON_OVR = "/BIOS/Intel Advanced Menu/ACPI Settings/10sec " \
    "Power Button OVR = Disabled"
PEP_SATA = "/BIOS/Intel Advanced Menu/ACPI Settings/PEP Constraints " \
    "Configuration/PEP SATA = No Constraint"
KBL_PEP_SATA = "/BIOS/Intel Advanced Menu/ACPI Settings/PEP Constraints " \
    "Configuration/PEP SATA Controller = Disabled"
EC_LOW_POWER_MODE = "/BIOS/Intel Advanced Menu/ACPI Settings/EC Low Power " \
    "Mode = Enabled"
AUDIO_LINK = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/HD Audio " \
    "Configuration/Audio Link Mode = SoundWire"
PM_SUPPORT = "/BIOS/Intel Advanced Menu/System Agent (SA) Configura" \
    "tion/Graphics Configuration/PM Support = Enabled"
IPU_DEVICE = "/BIOS/Intel Advanced Menu/System Agent (SA) Configura" \
    "tion/IPU Device (B0:D5:F0) = Disabled"
PCH_LAN = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/PCH LAN " \
    "Controller = Enabled"
SATA_RST = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/SATA And RST " \
    "Configuration/SATA Port 1 DevSlp = Enabled"
TRACE_HUB = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/TraceHub " \
    "Configuration Menu/TraceHub Enable Mode = Host Debugger"
IUER_BUTTON = "/BIOS/Intel Advanced Menu/System Agent (SA) Configuration" \
    "/Graphics Configuration/IUER Button Enable = Enabled"
IUER_SLATE = "/BIOS/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/Intel(R) Ultrabook Event Support/IUER Slate " \
    "Enable = Enabled"
IUER_DOCK = "/BIOS/Intel Advanced Menu/System Agent (SA) Configuration/" \
    "Graphics Configuration/Intel(R) Ultrabook Event Support/IUER Dock " \
    "Enable = Enabled"
DPTF = "/BIOS/Intel Advanced Menu/Thermal Configuration/DPTF Configura" \
    "tion/DPTF = Enabled"
CS_HALO = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/W/A to enable CS " \
    "on HALO = Enabled"
RVP3_SD_CARD = "/BIOS/Intel Advanced Menu/PCH-IO Configuration/SCS " \
    "Configuration/SDCard Sideband Events = Use GPP_B17"
ATTEMPT_SECURE_BOOT = "Set Bios /BIOS/Boot Maintenance Manager Menu/Secure " \
    "Boot Configuration Menu/Attempt Secure Boot = Unchecked"
ATTEMPT_SECURE_BOOT_OPTION = "UNCHECKED"

CFL_U = [LOW_POWER_CAPABILITY, POWER_BUTTON_OVR, EC_LOW_POWER_MODE,
         PEP_SATA,AUDIO_LINK]
CFL_S_CNL_PCH_H = [LOW_POWER_CAPABILITY, POWER_BUTTON_OVR,PEP_SATA, AUDIO_LINK]
CFL_H_CNL_PCH_H = [LOW_POWER_CAPABILITY, POWER_BUTTON_OVR, EC_LOW_POWER_MODE,
                   PEP_SATA, AUDIO_LINK]
CNL_CMOS_DMOS = [LOW_POWER_CAPABILITY, POWER_BUTTON_OVR,EC_LOW_POWER_MODE,
                 PEP_SATA, PM_SUPPORT, IPU_DEVICE]

DICT_UN_CHECK = {'Checked':'0x1', 'Unchecked':'0x0'}
UNIQUE_DICT = {'memory rc version':'Memory RC Version', 'board id':'Board ID',
               'fab id':'Fab ID', 'id':'ID', 'me fw version':'ME FW Version',
               'number of processors':'Number of Processors', 'speed':'Speed',
               'ec fw version':'EC FW Version',
               'lan phy revision':'LAN PHY Revision',
               'igfx gop version':'IGFX GOP Version'}
VERSION_INTELAM = ["Manufacturer", "Channel 0 Slot 0", "Memory Rc Version",
                   "Memory Timings", "Memory Frequency", "L1 Data Cache",
                   "L1 Instruction Cache", "L2 Cache", "L3 Cache", "L4 Cache",
                   "Microcode Revision", "Power Limit 1", "Power Limit 2"]
VERSION_TEMP = ['board id', 'memory rc version', 'fab id', 'me fw version',
                'id', 'number of processors', 'ec fw version', 'speed',
                'lan phy revision', 'igfx gop version']

EFI_LOGPATH = r"S:\\EFI\\xmlcli\\out\\XmlCli.log"
SDRIVE_PATH = r"S:\\"

PYTHON_SCRIPT = '''
import sys
sys.path.append(r"FS0:\\EFI\\xmlcli")
import XmlCli as cli

if "UNCHECKED" == set_option_efi.strip().upper() and \
                "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AttemptSecureBoot=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \
                "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AttemptSecureBoot=0")
elif "CHECKED" == set_option_efi.strip().upper() and \
                "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvProgKnobs("AttemptSecureBoot=1")
elif "CHECKED" == read_option_efi.strip().upper() and \
                "attempt secure boot" == option_in_bios.strip().lower():
    cli.CvReadKnobs("AttemptSecureBoot=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \
                "acpi t-states" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TStatesEnable=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \
                "acpi t-states" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TStatesEnable=0")
elif "CHECKED" == set_option_efi.strip().upper() and \
                "acpi t-states" == option_in_bios.strip().lower():
    cli.CvProgKnobs("TStatesEnable=1")
elif "CHECKED" == read_option_efi.strip().upper() and \
                "acpi t-states" == option_in_bios.strip().lower():
    cli.CvReadKnobs("TStatesEnable=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \
                "pch temp" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \
                "pch temp" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=0")
elif "CHECKED" == set_option_efi.strip().upper() and \
                "pch temp" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PCHTempReadEnable=1")
elif "CHECKED" == read_option_efi.strip().upper() and \
                "pch temp" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PCHTempReadEnable=1")
elif "bios_admin" == option_in_bios.strip().lower():
    cli.SetUserPwd("", set_option_efi)
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DTPM 2.0" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=2")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DTPM 2.0" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=2")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DTPM 1.2" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=1")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DTPM 1.2" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=1")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "PTT (FTPM)" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=3")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "PTT (FTPM)" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=3")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DISABLED" == set_option_efi.strip().upper():
    cli.CvProgKnobs("TpmDevice=0")
elif "current selected tpm device" == option_in_bios.strip().lower() and \
                "DISABLED" == read_option_efi.strip().upper():
    cli.CvReadKnobs("TpmDevice=0")
elif "CHECKED" == set_option_efi.strip().upper() and \
                "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshPdtUnlock=1")
elif "CHECKED" == read_option_efi.strip().upper() and \
                "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshPdtUnlock=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \
                "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshPdtUnlock=0")
elif "UNCHECKED" == read_option_efi.strip().upper() and \
                "pdt unlock message" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshPdtUnlock=0")
elif "CHECKED" == read_option_efi.strip().upper() and \
     "spi" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshSpiGpioAssign=1")
elif "UNCHECKED" == read_option_efi.strip().upper() and \
     "spi" == option_in_bios.strip().lower():
    cli.CvReadKnobs("PchIshSpiGpioAssign=0")
elif "CHECKED" == set_option_efi.strip().upper() and \
     "spi" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshSpiGpioAssign=1")
elif "UNCHECKED" == set_option_efi.strip().upper() and \
     "spi" == option_in_bios.strip().lower():
    cli.CvProgKnobs("PchIshSpiGpioAssign=0")
else:
    pass
'''

PYTHON_FEI_FOLDER = r"S:\\EFI"
SET_VALUES_OPTIONS = ['tCL', 'tRCDtRP', 'tRAS', 'tCWL', 'tFAW', 'tREFI',
                      'tRFC', 'tRRD', 'tRTP', 'tWTR']

KBL_U_Y = [LOW_POWER_CAPABILITY, EC_LOW_POWER_MODE, POWER_BUTTON_OVR,
           KBL_PEP_SATA, PCH_LAN, SATA_RST, TRACE_HUB, IUER_BUTTON, IUER_SLATE,
           IUER_DOCK, DPTF]
KBL_H = [LOW_POWER_CAPABILITY, EC_LOW_POWER_MODE, KBL_POWER_BUTTON_OVR,
         KBL_PEP_SATA, PCH_LAN, SATA_RST, TRACE_HUB, IUER_BUTTON, IUER_SLATE,
         IUER_DOCK, DPTF, CS_HALO]
KBL_R = [LOW_POWER_CAPABILITY, EC_LOW_POWER_MODE, KBL_POWER_BUTTON_OVR,
         KBL_PEP_SATA, RVP3_SD_CARD, PCH_LAN, SATA_RST, TRACE_HUB,
         IUER_BUTTON, IUER_SLATE, IUER_DOCK, DPTF]

FLAG_SINGLE_OPT = ["0x00000000", "0x52EF", "0x30", "0x00"]
OFFLINE_ONLINE_PATH_VARIABLE = ["ME Firmware SKU"] 

#############################Verify Display#####################################
SUT_DISPLAY = ["UEFI", "BIOS SETUP", "EDK SHELL"]
UEFI_DISPLAY = ["UEFI", "v2.50", "(EDK ", "Mapping", " Table", "FS0:",
                " Alias(s)", "Press", "ESC", "in", "seconds", "to", "skip",
                "startup.nsh", "any", "other", "key", "to", "continue",
                "Shell>"]
EDK_display = ["UEFI", "v2.50", "(EDK ", "Mapping", " Table", "FS0:",
               " Alias(s)", "Press", "ESC", "in", "seconds", "to", "skip",
               "startup.nsh", "any", "other", "key", "to", "continue",
               "Shell>"]

BIOS_SETUP = ["<English>", "Select", "Language", "PLatform", "Information",
              "Menu", "Intel", "Advanced", "Menu", "TPV", "EFI", "Device",
              "Manager", "Boot", "Manager", "Menu", "Boot", "Maintenance",
              "Manager", "Menu", "Continue", "Reset", "F2", "Discard",
              "Changes", "F3", "Load", "Defaults", "<Enter>", "=", "Select",
              "Entry", "F4", "Save", "Changes"]

NUMBER_CONVERSION_ALPHABETS = ["a", "b", "c", "d", "e", "f"]

NOT_IN_NUMBER = ["0x", "'b", "mb", "gb", "'d"]

GREYED_OUT_OPTIONS = \
    ["HD AUDIO SUBSYSTEM CONFIGURATION SETTINGS", "GT SLICE DOMAIN",
     "STATICALLY SWITCHABLE BCLK CLOCK FREQUENCY CONFIGURATION",
     "GT UNSLICE DOMAIN", "AUDIO DSP NHLT ENDPOINTS CONFIGURATION",
     "AUDIO DSP FEATURE SUPPORT",
     "AUDIO DSP PRE/POST-PROCESSING MODULE SUPPORT"]

MEMORY_CHANNELS = ["CHANNEL 0 SLOT 0", "CHANNEL 0 SLOT 1", "CHANNEL 1 SLOT 0",
                   "CHANNEL 1 SLOT 1"]
MMEMORY_CHANNEL_FREQUENCY = "/BIOS/Intel Advanced Menu/Memory " \
    "Configuration/Memory Frequency"
CHANNEL_0_SLOT_0 = "/BIOS/Intel Advanced Menu/Memory Configuration/Channel " \
    "0 Slot 0 = Populated & Enabled"
CHANNEL_0_SLOT_1 = "/BIOS/Intel Advanced Menu/Memory Configuration/Channel " \
    "0 Slot 1 = Populated & Enabled"
CHANNEL_1_SLOT_0 = "/BIOS/Intel Advanced Menu/Memory Configuration/Channel " \
    "1 Slot 0 = Populated & Enabled"
CHANNEL_1_SLOT_1 = "/BIOS/Intel Advanced Menu/Memory Configuration/Channel " \
    "1 Slot 1 = Populated & Enabled"
CHANNEL_0_SLOT_0_SIZE = "/BIOS/Intel Advanced Menu/Memory Configuration/" \
    "Channel 0 Slot 0/size"
CHANNEL_0_SLOT_1_SIZE = "/BIOS/Intel Advanced Menu/Memory Configuration/" \
    "Channel 0 Slot 1/size"
CHANNEL_1_SLOT_0_SIZE = "/BIOS/Intel Advanced Menu/Memory Configuration/" \
    "Channel 1 Slot 0/size"
CHANNEL_1_SLOT_1_SIZE = "/BIOS/Intel Advanced Menu/Memory Configuration/" \
    "Channel 1 Slot 1/size"
GB_SIZE = 1024

FFT_LOG = r"C:\\Program Files (x86)\\Intel Corporation\Intel(R) Firmware " \
    r"Flash Tool\\fft_flash_log.txt"

HWID_PROPERTY_NAME = ["HARDWAREID", "HARDWARE ID", "HARDWARE IDS"]

NODE_ATTRIBUTE_OPTIONS = ["PowerLimit4", "Custom1TurboActivationRatio",
                          "CpuRatio"]

ONLINE_XML_LOG_OPTIONS = ["0x00000000", "0x00", "0x1D", "0x1A"]

#############################TAT Tool###########################################
TAT_TOOL_PATH = r"C:\Program Files\Intel Corporation\Intel(R)TAT6\Host"
TAT_TOOL_RESULT_PATH = r"C:\\Users\\Administrator\\Documents\\iTAT\\log"
DELETE_CSV_FILE = "del /s *.csv"
PSTATE_WORKSPACE = r'C:\AUTOMATION\TOOLS\PSTATE_WS.XML'
INSTALLEDPATH_TARGET = r'C:\Program Files\Intel Corporation\Intel(R)TAT6\Target'
PSTATE_CYCLING_SCRIPT = r'C:\AUTOMATION\TOOLS\PSTATE_CYCLING.XML'
PSTATE_WORKSPACE_APPLY_WORKLOAD = \
    r"C:\Automation\tools\pstate_ws_apply_workload.xml"
TAT_CLI = "THERMALANALYSISTOOLCMD.EXE"

###########################Fpt##################################################
FPT_EFI = ["Fpt.efi","fparts.txt"]

##########################PECI##################################################
PECI_LOG = r"C:\\Program Files\\Intel Corporation\\Intel(R)PECI\\log.csv"
PECI_INSTALLED_PATH = r"C:\\Program Files\\Intel Corporation\\Intel(R)PECI"
PECI_APP = "PECIApp.exe"

# TTK2 Constant Values
TTK2_INSTALL_FOLDER = r"C:\SVShare\user_apps\TTK2"
TTK2_PYTHON_FILES_PATH = r"C:\SVShare\user_apps\TTK2\API\Python"
TOOL_TTK2 = "TTK2"
STR_NONE = "None"
GPIO_XML = r'C:\\SVSHARE\\User_Apps\\TTK2\\Xml Configurations\\Karkom.xml'
PLATFORM_XML = r'C:\\SVSHARE\\User_Apps\\TTK2\\Xml Configurations\\BxtVv.xml'
POSTCODE_XML = r'C:\\SVSHARE\\User_Apps\\TTK2\\Xml Configurations\\Mini' \
    r'Port80_smbus.xml'
AC_POWER = "ac_power"
CHIP_MODEL_ERROR = "Unknown"
G3_TYPE_AC = "ac"
TTK2_SWITCH_NO_AC = 0
TTK2_APP_NAME = "TTK2_Server.exe"
TTK_FOLDER_PATH = r"C:\SVShare\user_apps\TTK2"
TTK_PYTHON_PATH = r"C:\SVShare\user_apps\TTK2\API\Python"
CONFIG_TAG = "Ambience"
TTK_ACTION_ON = "ON"
TTK_ACTION_OFF = "OFF"
NOT_CONNECTED = "NC"

# XmlCli Tool Constant Values
XMLCLI_TOOLPATH = r"C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli"
RETURN_SUCCESS = 0
TOOL_XMLCLI = "XmlCli"
EFI_OPTION_LIST = ['attempt secure boot', 'acpi t-states', 
                   'current selected tpm device', 'pdt unlock message',
                   'me state', 'pcr bank: sha256', 'pcr bank: sha1',
                   'tpm2 operation', 'tpm2 operation parameter',
                   'wake from thunderbolt(tm) devices', "enable hibernation",
                   "bluetooth sideband", "spi", "uart0", "uart1", "i2c0",
                   "i2c1", "i2c2", "gp_0", "gp_1", "gp_2", "gp_3", "gp_4",
                   "gp_5", "gp_6", "gp_7", "unconfigure me",
                   "mebx oem debug menu enable", "pch temp read",
                   "hide unconfigure me confirmation prompt",
                   "mebx selection screen", "mebx hotkey pressed",
                   "activate remote assistance process", "s0i2",
                   "enable rail in s0i3", "enable rail in s3",
                   "enable rail in s4", "enable rail in s5"]
GP_X_EFI_OPTION_LIST = ["gp_0", "gp_1", "gp_2", "gp_3", "gp_4", "gp_5", "gp_6",
                        "gp_7"]
STR_PASS = "PASS"
STR_FAIL = "FAIL"
STR_MOUNT_DRIVE = "mount drive"
PATH_SEP = os.sep
TOOL_PATH_EFI_PYTHON = "C:\\Testing\\GenericFramework\\tools\\"
STR_EDK = "EDK"
TOOL_PATH_XML = ""
XMLCLI_PATH = r"C:\\Testing\\GenericFramework\\tools\\pysvtools.xmlcli" \
              r"\\pysvtools\\xmlcli\\out\\PlatformConfig.xml"

################################PAVP_APP########################################
PAVP_PATH = r"C:\\Testing\\GenericFramework\\tools\\PAVP_APP"
PAVP_HEAVY_BAT = "pavp_heavy.bat"
PAVP_LITE_BAT = "pavp_lite.bat"

################################ SYSCOPE #####################################
SYSCOPE_TOOLDIR = "C:\\Program Files\\Intel Corporation\\Intel(R) System Scope Tool"
SYSCOPE_EXE = "SystemScopeCmdLine.exe"
SYSCOPE_PATH = "C:\\Program Files\\Intel Corporation\\Intel(R) System Scope Tool"
SYSCOPE_TOOL_NAME = "Intel(R) System Scope Tool"
SYSCOPE_SETUP_PATH = "C:\\OWR\\SystemScope"
SYSCOPE_SETUP = "Intel(R)SystemScopeInstallerWinInternal.exe"
SYSCOPE_LICENSE = "C:\\OWR\\SystemScope\\license.txt"
SYSCOPE_TELEMETRY = "C:\\Testing\\GenericFramework\\Tools\\TelemetryLicenseAgreement.txt"
SYSCOPE_LICENSEAGREEMENT = "C:\\Testing\\GenericFramework\\Tools\\LicenseAgreement.txt"
SYSCOPE_BINARIES_TELE = "C:\\Program Files\\Intel Corporation\\" \
                        "Intel(R) System Scope Tool\\SupportedBinaries\\TelemetryLicenseAgreement.txt"
SYSCOPE_BINARIES_LICE = "C:\\Program Files\\Intel Corporation\\" \
                        "Intel(R) System Scope Tool\\SupportedBinaries\\LicenseAgreement.txt"

################################################################################
UNINSTALL_DRIVER = ['ISH','IRMT']
DEFAULT_DRIVERS = ["AVSTREAM", "SKYCAM", "SKY CAM"]

########################### PWRSHELL ###########################################
PWRSHELL_PATH = "C:\\Users\\Administrator\\AppData\\Roaming\\Microsoft" \
                 "\\Windows\\Start Menu\\Programs\\Windows PowerShell"

############################ USBVIEW ###########################################
USBVIEW_PATH = "C:\\Testing\\GenericFramework\\Tools\\UsbView"
USBVIEW_SETUP = "usbview.exe"
USBVIEW_CMD = "/q /f /saveall:USBViewAll.txt"

################################################################################
PLINK_SERVICE = "plink.exe"
PLINK_EXE = r"C:\Testing\plink.exe"
TERATERM_SERVICE = "ttermpro.exe"
TERATERM_PATH = r"C:\Program Files (x86)\teraterm"
WINDBG_SERVICE = "windbg.exe"

######################### USBTREEVIEW ##########################################
USBTREEVIEW_PATH = "C:\\Testing\\GenericFramework\\Tools\\usbtreeview\\x64"
USBTREEVIEW_EXE = "UsbTreeView.exe"

########################## CSWITCH #############################################
CSWITCH_INSTALLED_PATH = "C:\\SVShare\\user_apps\\FTDI_Wrapper"

# SUT Interface folder path for to get LED Status using LSD Device
SUT_INTERFACE_FOLDER_PATH = r"C:\Testing\GenericFramework\Tools\sutinterface"

# Flash using XmlCli Test Cases List
FLASH_USING_XMLCLI_TEST_CASE_LIST = \
    ["CSS-IVE-51090", "CSS-IVE-51099", "CSS-IVE-92255", "CSS-IVE-117319",
     "CSS-IVE-51069", "CSS-IVE-51081", "CSS-IVE-77379", "CSS-IVE-116772",
     "CSS-IVE-51037", "CSS-IVE-51044", "CSS-IVE-51045", "CSS-IVE-67259",
     "CSS-IVE-65694", "CSS-IVE-50439", "CSS-IVE-50440", "CSS-IVE-97346",
     "CSS-IVE-78671", "CSS-IVE-62141", "CSS-IVE-114614" "CSS-IVE-95350",
     "CSS-IVE-118157", "CSS-IVE-118158", "CSS-IVE-118518", "CSS-IVE-101521",
     "CSS-IVE-129921", "CSS-IVE-102439", "CSS-IVE-75916", "CSS-IVE-93277",
     "CSS-IVE-117884", "CSS-IVE-118266", "CSS-IVE-118362", "CSS-IVE-105698",
     "CSS-IVE-117060", "CSS-IVE-117063", "CSS-IVE-117064", "CSS-IVE-108297",
     "CSS-IVE-105851", "CSS-IVE-51282", "CSS-IVE-51283", "CSS-IVE-51284",
     "CSS-IVE-51285", "CSS-IVE-51301", "CSS-IVE-51302", "CSS-IVE-67206",
     "CSS-IVE-72613", "CSS-IVE-77495", "CSS-IVE-114265", "CSS-IVE-117954",
     "CSS-IVE-119239", "CSS-IVE-51158", "CSS-IVE-113642", "CSS-IVE-119086",
     "CSS-IVE-119087", "CSS-IVE-119091", "CSS-IVE-119092", "CSS-IVE-119094",
     "CSS-IVE-119095", "CSS-IVE-119097", "CSS-IVE-119098", "CSS-IVE-119103",
     "CSS-IVE-119104", "CSS-IVE-119106", "CSS-IVE-119107", "CSS-IVE-119118",
     "CSS-IVE-119119", "CSS-IVE-119121", "CSS-IVE-119122", "CSS-IVE-114894",
     "CSS-IVE-114895", "CSS-IVE-117737", "CSS-IVE-122417", "CSS-IVE-122432",
     "CSS-IVE-122441", "CSS-IVE-122447", "CSS-IVE-122147", "CSS-IVE-122148",
     "CSS-IVE-122156", "CSS-IVE-122158", "CSS-IVE-122224", "CSS-IVE-122149",
     "CSS-IVE-122238", "CSS-IVE-122322", "CSS-IVE-122371", "CSS-IVE-122372",
     "CSS-IVE-122378", "CSS-IVE-122388", "CSS-IVE-122138", "CSS-IVE-122160",
     "CSS-IVE-119084", "CSS-IVE-129857", "CSS-IVE-118611", "CSS-IVE-118680",
     "CSS-IVE-80441", "CSS-IVE-51026", "CSS-IVE-51028", "CSS-IVE-51033",
     "CSS-IVE-51035", "CSS-IVE-51036", "CSS-IVE-67212"]

SET_READ_USING_BIOS_CONFIG_TOOL = \
    ["CSS-IVE-75985"]