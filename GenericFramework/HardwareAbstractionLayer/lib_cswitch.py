## Revision Control
## cswitch_rev00 - CSwitch release
## cswitch_rev01 - Added time.sleep(0.5) between port connections
## cswitch_rev02 - Added IO Expander MAX7311. Supports "TCSM_HW_ECN_02.pdf" and "CSwitchControlBoard_HW_ECN_02.pdf"
## cswitch_rev03 - Added IO DFF. Supports Fab B and CSwitch2.0
## cswitch_rev04 - Added loop function, added OutputPortRegisterRead function. Supports CSwitch Fab B and CSwitch2.0.
## cswitch_rev05 - Added Python3 support

__author__ = 'jpuklatx'

import os, sys
import datetime
import time
import threading
# Local python imports
import library
import lib_constants
sys.path.append(lib_constants.CSWITCH_INSTALLED_PATH)
if os.path.exists(lib_constants.CSWITCH_INSTALLED_PATH):
    from Ftdi_Wrapper import *

def gpioModify(ftdiInt, portNum, pinNumber, value):
    """
    PortNum - 0 for port A , 1 for B , 2 for C , 3 for D
    pinNumber - 0 for pin 0, 7 for pin 7
    value - 0 to drive "0" , 1 to drive "1"
    """
    if (value == 1 ):
        ftdiInt.SetPin(portNum, pinNumber)
    if (value == 0 ):
        ftdiInt.ClearPin(portNum, pinNumber)

def DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd):
    # Disable all CSwitch device ports in order to prevent "all on" initial condition

    try:
        ExtenderAddress = 0xB6                                        #Nevo IO extender address


        data = ftdiInterface.Read(ExtenderAddress,4)
        fromPort1 = 0x02

        arr = bytearray()
        arr.append(0x2)
        arr.append(0x0)

        ftdiInterface.Write(b'\xb6', arr)


        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x00])
               #Setting extender output buffer to "0" in order to prevent "all on" initial condition

##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1
##        buffPort1 = []
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        fromPort2 = 0x03
        arr = bytearray()
        arr.append(0x3)
        arr.append(0x0)

        ftdiInterface.Write(b'\xb6', arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x00])       #Setting extender output buffer to "0". All the Cx are disabled because "C_HDR_CTL_SEL_EN" is low
##        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port2
##        buffPort2 = []
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        # print (".")
##        # time.sleep(1)
##        # print ("..")
##        # time.sleep(1)

        OutputPort2 = 0x07
        arr = bytearray()
        arr.append(0x7)
        arr.append(0x0)

        ftdiInterface.Write(b'\xb6', arr)                                         #Configuration register address
        #ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #Setting configuration register at output state
        OutputPort1 = 0x06
        arr = bytearray()
        arr.append(0x6)
        arr.append(0x0)

        ftdiInterface.Write(b'\xb6', arr)                                            #Configuration register address
        #ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #Setting configuration register at output state

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: All CSwitch ports output ready but disabled",
                          test_case_id, script_id, "None", "None",
                          log_level, tbd)
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: In DisableAll(),due to: %s" % e_obj,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
    return False

def OpenAll_before_or_after_DelayEvent(ftdiInterface):
    # Disable all CSwitch device ports in order to prevent "all on" initial condition
        ExtenderAddress = 0xB6                                      #Nevo IO extender address

        fromPort1 = 0x02
        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x04])       #Setting extender output buffer to "0" in order to prevent "all on" initial condition
##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1
##        buffPort1 = []
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        fromPort2 = 0x03
        ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x00])       #Setting extender output buffer to "0". All the Cx are disabled because "C_HDR_CTL_SEL_EN" is low
##        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port2
##        buffPort2 = []
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]


        print (".")
        time.sleep(1)
        print ("..")
        time.sleep(1)

        OutputPort2 = 0x07                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #Setting configuration register at output state
        OutputPort1 = 0x06                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #Setting configuration register at output state

        print ("All CSwitch ports are open, waiting for wake up event start or end")

def plugC1(ftdiInterface, test_case_id, script_id, log_level="ALL", tbd=None):
    # plug to conn1
    try:
        ExtenderAddress = b'\xB6'                                        #Nevo IO extender address

        fromPort1 = 0x02
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0xC1)

        ftdiInterface.Write(ExtenderAddress, arr)                                             #
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0xC1])       #C1 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1

##        buffPort2 = []
        fromPort2 = 0x03
        arr = bytearray()
        arr.append(fromPort2)
        arr.append(0x05)

        ftdiInterface.Write(ExtenderAddress, arr)                                 #
        #ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x05])       #C1
        #ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port1
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []

        ftdiInterface.Write(ExtenderAddress, [fromPort1, b'\xC5'])
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0xC5])       #C1 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                        #Configuration register addres
        arr = bytearray()
        arr.append(fromPort2)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort1)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: Device successfully plugged to C1",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: In plugC1(),due to: %s" % e_obj,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False


def plugC2(ftdiInterface, test_case_id, script_id, log_level="ALL", tbd=None):
    # plug to conn2
    try:

        #ExtenderAddress = 0xB6
        ExtenderAddress = b'\xB6'                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x82)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x82])       #C2 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port2

##        buffPort2 = []
        fromPort2 = 0x03
        arr = bytearray()
        arr.append(fromPort2)
        arr.append(0x04)

        ftdiInterface.Write(ExtenderAddress, arr)                                              #
        #ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x04])       #C2
        #ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port2
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x86)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x86])       #C2 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port2
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                          #Configuration register address
        arr = bytearray()
        arr.append(OutputPort2)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort1)
        arr.append(0x00)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: Device successfully plugged to C2",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: In plugC2(),due to: %s" % e_obj,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
        return False

def plugC3(ftdiInterface, test_case_id, script_id, log_level="ALL", tbd=None):
    # plug to conn3
    try:
        #ExtenderAddress = 0xB6                                        #Nevo IO extender address
        ExtenderAddress = b'\xB6'

        fromPort1 = 0x02
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x48)

        ftdiInterface.Write(ExtenderAddress, arr)                                             #
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x48])       #C3 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port3

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        arr = bytearray()
        arr.append(fromPort2)
        arr.append(0x02)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x02])       #C3
        #ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port3
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x4C)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x4C])       #C3 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port3
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort2)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort1)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: Device successfully plugged to C3",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: In plugC3(),due to: %s" % e_obj,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
    return False


def plugC4(ftdiInterface, test_case_id, script_id, log_level="ALL", tbd=None):
    # plug to conn3
    try:
        #ExtenderAddress = 0xB6                                        #Nevo IO extender address
        ExtenderAddress = b'\xB6'

        fromPort1 = 0x02
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x10)

        ftdiInterface.Write(ExtenderAddress, arr)                                             #
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x10])       #C4 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port4

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        arr = bytearray()
        arr.append(fromPort2)
        arr.append(0x03)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x03])       #C4
        #ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port4
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
        arr = bytearray()
        arr.append(fromPort1)
        arr.append(0x14)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x14])       #C4 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
        #ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port4
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort2)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        arr = bytearray()
        arr.append(OutputPort1)
        arr.append(0x00)

        ftdiInterface.Write(ExtenderAddress, arr)
        #ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        library.write_log(lib_constants.LOG_INFO,
                          "INFO: Device successfully plugged to C4",
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return True
    except Exception as e_obj:
        library.write_log(lib_constants.LOG_ERROR,
                          "EXCEPTION: In plugC4(),due to: %s" % e_obj,
                          test_case_id, script_id,
                          "None", "None", log_level, tbd)
    return False


def afterDelayplugC1(ftdiInterface):
    # plug to conn1

        ExtenderAddress = 0xB6                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0xC5])       #C1 ready  "C_FT_CTL_SEL_EN_R" = 1
        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x05])       #C1
        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port1
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
##        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0xC5])       #C1 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port1
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        print ("Plugged to C1")

def afterDelayplugC2(ftdiInterface):
    # plug to conn2

        ExtenderAddress = 0xB6                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x86])       #C2 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port2

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x04])       #C2
        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port2
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
##        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x86])       #C2 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port2
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        print ("Plugged to C2")

def afterDelayplugC3(ftdiInterface):
    # plug to conn3

        ExtenderAddress = 0xB6                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x4C])       #C3 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port3

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x02])       #C3
        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port3
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
##        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x4C])       #C3 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port3
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        print ("Plugged to C3")

def afterDelayplugC4(ftdiInterface):
    # plug to conn3

        ExtenderAddress = 0xB6                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x14])       #C4 ready but diabled "C_FT_CTL_SEL_EN_R" = 0
        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port3

##        buffPort2 = []
        fromPort2 = 0x03                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort2, 0x03])       #C4
        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender Port4
##        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort2[0]

##        buffPort1 = []
##        ftdiInterface.Write(ExtenderAddress, [fromPort1, 0x14])       #C4 ready and enabled "C_FT_CTL_SEL_EN_R" = 1
##        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender Port4
##        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 1))
##        print buffPort1[0]

        OutputPort2 = 0x07                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort2, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to set high in the latest transaction
        OutputPort1 = 0x06                                            #Configuration register address
        ftdiInterface.Write(ExtenderAddress, [OutputPort1, 0x00])     #setting configuration register at output state. "CTL_SEL_EN" has to stay low till the latest transaction

        print ("Plugged to C4")

def pulseDelay(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0x00
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 1) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 0) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" - RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def pulseDelay_133msec(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0x00                   # "0x00" - 08[sec] or "0xFF" - 16[sec] for DIVCODE=7 and RSET=201Kohm
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 1) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 1) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" -RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def pulseDelay_8p5sec(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0x00                   # "0x00" - 08[sec] or "0xFF" - 16[sec] for DIVCODE=7 and RSET=201Kohm
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 0) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 1) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" -RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def pulseDelay_18sec(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0xFF                   # "0x00" - 08[sec] or "0xFF" - 16[sec] for DIVCODE=7 and RSET=201Kohm
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 0) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 1) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" -RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def pulseDelay_17p5sec(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0x00                   # "0x00" - 16[sec] or "0xFF" - 23[sec] for DIVCODE=7 and RSET=402Kohm
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 0) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 0) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" -RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def pulseDelay_26p5sec(ftdiInterface):

        digpotAddressW = 0x50
        digpotControl = 0x11
        digpotData = 0xFF                   # "0x00" - 16[sec] or "0xFF" - 23[sec] for DIVCODE=7 and RSET=402Kohm
        ftdiInterface.Write(digpotAddressW, [digpotControl,digpotData])
        print ("digpotAddressW --> Done")

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        gpioModify(ftdiInterface, 0, 7 , 0) #C_FT_R2_VAL_CTRL               "1" - DIVCODE=5 [133-410 msec]      "0" - DIVCODE=7 [8500-25000 msec]
        gpioModify(ftdiInterface, 0, 5 , 0) #C_FT_RSET_VAL_CTRL             "1" - RSET=201Kohm                  "0" -RSET=402Kohm
        gpioModify(ftdiInterface, 0, 3 , 0) #C_CTL_SEL_EN

        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 0) #C_DELAY_CTRL
        time.sleep(0.5)
        gpioModify(ftdiInterface, 0, 1 , 1) #C_DELAY_CTRL
        print ("Dellay initialized")

def loop(ftdiInterface, test_case_id, script_id, log_level="ALL", tbd=None):
    i=0; size=10
    for i in range(0,size):
        DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd)
        plugC1(ftdiInterface, test_case_id, script_id, log_level, tbd)
        time.sleep(20)
        DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd)
        plugC2(ftdiInterface, test_case_id, script_id, log_level, tbd)
        time.sleep(20)
        DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd)
        plugC3(ftdiInterface, test_case_id, script_id, log_level, tbd)
        time.sleep(20)
        DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd)
        plugC4(ftdiInterface, test_case_id, script_id, log_level, tbd)
        time.sleep(20)
        i=i+1
    print(("loop with size =" ,size," --> Done"))

def OutputPortRegisterRead(ftdiInterface):
        ExtenderAddress = 0xB6                                        #Nevo IO extender address

        fromPort1 = 0x02                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort1])             #Reading IO extender OutputPortRegister
        buffPort1 = (ftdiInterface.Read(ExtenderAddress, 2))
        print(('0x02 output port register value is '), hex(buffPort1[1]))

        fromPort2 = 0x03                                              #
        ftdiInterface.Write(ExtenderAddress, [fromPort2])             #Reading IO extender OutputPortRegister
        buffPort2 = (ftdiInterface.Read(ExtenderAddress, 2))
        print(('0x03 output port register value is ', hex(buffPort2[1])))

def cswitch_plug(serialNumber, cswitch_port, test_case_id, script_id,
                 log_level="ALL", tbd=None):

    try:
        ftdiInterface = Ftdi_GPIO_I2C_Wrapper()
        devices = ftdiInterface.GetCardSerialNumbers()

        if not devices:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Could not "
                              "find FTDI devices", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if serialNumber in devices:
            ftdiInterface = Ftdi_GPIO_I2C_Wrapper()
            ftdiInterface.OpenInterface(serialNumber)
            library.write_log(lib_constants.LOG_INFO, "INFO: Connected to FTDI"
                              " SN - %s and DIPSW value: %s"
                              % (serialNumber, ftdiInterface.GetPins(3)),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

            gpioModify(ftdiInterface, 2, 0, 0)                                  # C_FT_BUFF_EN. Open buff after FTDI
            DisableAll(ftdiInterface, test_case_id, script_id, log_level, tbd)

            port_action = {"C1": "plugC1(ftdiInterface, test_case_id,"
                                 "script_id, log_level, tbd)",
                           "C2": "plugC2(ftdiInterface, test_case_id,"
                                 "script_id, log_level, tbd)",
                           "C3": "plugC3(ftdiInterface, test_case_id,"
                                 "script_id, log_level, tbd)",
                           "C4": "plugC4(ftdiInterface, test_case_id,"
                                 "script_id, log_level, tbd)"}

            result = eval(port_action.get(cswitch_port.upper()))
            ftdiInterface.Close()
            return result
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: The given "
                              "CSwitch - %s device is not connected to the "
                              "system" % serialNumber, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False


def cswitch_unplug(serialNumber, test_case_id, script_id, log_level="ALL",
                   tbd=None):

    try:
        ftdiInterface = Ftdi_GPIO_I2C_Wrapper()
        devices = ftdiInterface.GetCardSerialNumbers()

        if not devices:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: Could not "
                              "find FTDI devices", test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False

        if serialNumber in devices:
            ftdiInterface = Ftdi_GPIO_I2C_Wrapper()
            ftdiInterface.OpenInterface(serialNumber)
            library.write_log(lib_constants.LOG_INFO, "INFO: Connected to FTDI"
                              " SN - %s and DIPSW value: %s"
                              % (serialNumber, ftdiInterface.GetPins(3)),
                              test_case_id, script_id, "None", "None",
                              log_level, tbd)

            gpioModify(ftdiInterface, 2, 0, 0)                                  # C_FT_BUFF_EN. Open buff after FTDI
            result = DisableAll(ftdiInterface, test_case_id, script_id,
                                log_level, tbd)
            ftdiInterface.Close()
            return result
        else:
            library.write_log(lib_constants.LOG_WARNING, "WARNING: The given "
                              "CSwitch - %s device is not connected to the "
                              "system" % serialNumber, test_case_id, script_id,
                              "None", "None", log_level, tbd)
            return False
    except Exception as e:
        library.write_log(lib_constants.LOG_ERROR, "EXCEPTION: Due to %s" % e,
                          test_case_id, script_id, "None", "None", log_level,
                          tbd)
        return False
