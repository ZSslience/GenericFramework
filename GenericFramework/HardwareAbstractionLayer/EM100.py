#
# EM100 Module
# This module Use the Command line provided for Dediprog
# It provides basic control functions for EM100 emulator:
# - SetChip set the name of the SPI to emulate
# - SetBios set the BIOS file to emulate
# - kill_EM100 this function kill the task of EM100
# - burn   this function load the BIOS file and start the emulation
#
# author (miguel.a.cervantes.servin@intel.com)
# author (carlos.a.delgado.cardona@intel.com)
# author (arturo.medina.mendoza@intel.com)
# author (daniel.flores.alvarado@intel.com)+
# author  (sfp.fia.auto@intel.com)
# Exceptions raise or capture in this model: EM100Error
#
# This class need EM100 installed on the system under the program files \ dediprog\ EM100 folder
#
#
import os
import subprocess
import time
import platform


class EM100Error(Exception):
    pass


class EM100(object):

    def __init__(self,  binary=None):
        """
        EM100 construct function, set some defaults values to be used on the BIOS Flashing.
        :param None
        :return None
        :exception raise EM100Error exception if the the EM100 application doesn't exist
        :estimated LOC: 12
        """
        try:
            self._bios = None
            self._chip = "W25Q256FV"
            if self.is_windows_host():
                if binary is not None:
                    self._em100 = binary
                else:
                    self._em100 = r"C:\Program Files (x86)\DediProg\EM100\smucmd.exe"
            else:
                self._em100 = ''
                raise Exception('em100 not config for {0} host'.format(self.host_platform()))
            self._retries = 3

            if not os.path.exists(self._em100):
                print('Cannot find EM100 executable')
                raise EM100Error
        except Exception:
            print('Em100 application not found ')
            raise

    @staticmethod
    def send_cmd(cmd):
        print(cmd)
        result = ''
        try:
            result = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            # get the result string from the process output
            # then reraise (finally will be called first)
            result = e.output
            raise
        finally:
            # always log the output
            lines = result.splitlines()
        return lines

    def setChip(self, chipName):
        """
        setChip function, set the name for the chip that will be emulated
        :param chipName name of the Chip, must be part of the dediprog BIOS configuration
        :return True if the name is assigned
        :exception raise EM100Error if the name can't be assigned or the Chip name is none
        :black box equivalent class
            valid equivalent Class:    chipName="W25Q256FV"
            invalid equivalent Class:  chipName=None
        :estimated LOC: 6
        """
        try:
            if chipName is None:
                print('Error chip name is none')
                raise EM100Error

            self._chip = chipName
            return True
        except Exception:
            print(r'Chip name error')
            raise EM100Error

    def setBios(self, biosName):
        """
        setBios function, set the name for the BIOS that will be emulated
        :param biosName path to the BIOS that will be emulated
        :return True if the name is assigned
        :exception raise EM100Error if the name can't be assigned or if the Bios name is none
        :black box equivalent class
            valid equivalent Class:    biosName="bios.0014.d015.bin"
            invalid equivalent Class:  biosName=None

        :estimated LOC: 6
        """
        try:
            if biosName is None:
                print(r'Error Bios name is none')
                raise EM100Error
            self._bios = biosName
            return True
        except Exception:
            print(r'Bios name error')
            raise EM100Error

    def kill_EM100(self):
        """
        kill_EM100 function, task kill the dediprog EM100
        this function looks for the EM100 process and try to kill it using the taskkill command
        :param None
        :return True if the Process was removed
        :exception raise EM100Error if the name can't be assigned
        :estimated LOC: 13
        """
        process = 'EM100.exe'
        try:
            if self.is_windows_host():
                pass
            elif self.is_linux_host():
                raise Exception('em100 not config for linux host')
            else:
                raise Exception('em100 not config for {0} host'.format(self.host_platform()))
            pp = self.send_cmd('C:/WINDOWS/system32/tasklist.exe')
            # kills dediprog if is opened.
            for x in pp:
                if x.decode().startswith(process):
                    self.send_cmd(r"C:/WINDOWS/system32/taskkill.exe /im %s" % process)
                    print("Killing dediprog process before starting.")
                    time.sleep(5)
            pp = self.send_cmd('C:/WINDOWS/system32/tasklist.exe')
            for x in pp:
                if x.decode().startswith(process):
                    print(" The EM100 can't be stopped")
                    return False
            return True
        except Exception as e:
            print(r'Error trying to kill EM100:{}'.format(e))
            raise EM100Error

    def stop(self):
        lookfor = "Ready to boot your system now."
        lookforErr = "Error: EM100/EM100Pro can not be detected"

        try:
            if self.is_windows_host():
                pass
            elif self.is_linux_host():
                raise Exception('em100 not config for linux host')
            else:
                raise Exception('em100 not config for {0} host'.format(self.host_platform()))

            if self._bios is None:
                print(" BIOS file is not set")
                return False

            if not os.path.exists(self._em100):
                print(" Cannot find EM100 executable")
                return False

            # command line generation
            cmd = [self._em100] + ['--stop']
            # log command
            print(" Command: %s" % str(cmd))

            for t in range(self._retries):
                print(" ### Try %s" % str(t))

                if self.kill_EM100():
                    # sending command
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None)
                    r = p.communicate()

                    if r is None:
                        print(" There was a problem communicating with the em100 process")
                        continue

                    if lookforErr in r[0].decode():
                        print(" There was a problem, EM100/EM100Pro can not be detected")
                        continue

                    if lookfor in r[0].decode():
                        print(" BIOS OK")
                        return True
                    else:
                        print(" Couldn't find string: %s" % lookfor)
            else:
                print(" retries reached")

        except Exception as error:
            print('Error when try flash bios ' + str(error))

        return False

    def burn(self):
        """
        burn function, start the BIOS emulation
        this function launch the EM100 and pass as parameter the self._chip and self._bios.
        this functions looks for the label Ready or Error to report if pass or fail
        :param None
        :return Pass  if the EM100 works fine, False if we have issues to launch the BIOS
        :estimated LOC: 31
        """
        lookfor = "Ready to boot your system now."
        lookforErr = r"Error: EM100/EM100Pro can not be detected"

        # start to burn the BIOS, to start you need to set correct the variable of the class
        try:
            if not self.is_windows_host():
                raise Exception('em100 not config for {} host'.format(self.host_platform()))

            if self._bios is None:
                print(" BIOS file is not set")
                return False

            if not os.path.exists(self._em100):
                print(" Cannot find EM100 executable")
                return False

            # command line generation
            cmd = [self._em100] + ['--stop', '--set', self._chip, "-b", "-d", self._bios, "--start"]
            # log command
            print(" Command: %s" % str(cmd))

            for t in range(self._retries):
                print(" ### Try %s" % str(t))

                if self.kill_EM100():
                    # sending command
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None)
                    r = p.communicate()

                    if r is None:
                        print(" There was a problem communicating with the em100 process")
                        continue

                    if lookforErr in r[0].decode():
                        print(" There was a problem, EM100/EM100Pro can not be detected")
                        continue

                    if lookfor in r[0].decode():
                        print(" BIOS OK")
                        return True
                    else:
                        print(r[0],r[1])
                        print(" Couldn't find string: %s" % lookfor)
            else:
                print(" retries reached")

        except Exception as error:
            print('Error when try flash bios ' + str(error))

        return False

    @staticmethod
    def is_linux_host():
        return platform.system().lower() == 'linux'

    @staticmethod
    def is_windows_host():
        return platform.system().lower() == 'windows'

    @staticmethod
    def host_platform():
        return platform.system()


def flashifwi_em100(binfile, chip_name="MX25L51245G", finish_stop=False):
    """
    This API will set the Binfile to the EM100 class and call the funtion burn from the EM100 class.
    :param:   binfile            :IFWI bin file name with full path.
    :return:  RET_SUCCESS        :Successfully flashed IFWI bin file was emulated.
              RET_TEST_FAIL      :After flashing, chip content checksum is not correct or depended APIs return RET_TEST_FAIL;
              RET_INVALID_INPUT  :If the binfile is not correct or not exist.
    :external dependence:   private/EM100(); private/EM100().setBios; private/EM100().burn()
    :black box equivalent class
        valid equivalent Class:   binfile=PLYDCRB.86B.OR.64.2016.33.4.07.0636_LBG_SPS.bin
        invalid equivalent Class: binfile=None
    :estimated LOC:  9
    """
    print('Current bin file: %s' % binfile)
    em100 = EM100()
    em100.setChip(chip_name)
    if em100.setBios(binfile):
        print('Flashing IFWI Start')
        if em100.burn():
            print('Flashing IFWI Done')

            if finish_stop:
                em100.stop()
            return True
        else:
            print('Unable to flash the BIOS bin file')
            return False
    else:
        print('Unable to set the BIOS name')
        return False


if __name__ == '__main__':
    flashifwi_em100(r'C:\Users\sys_eval\Documents\Liang\WLYDCRB.PB1.SYS.WR.64.2020.21.1.01.0613_0016'
                    r'.P11_P0001c_LBG_SPS_CPX_DBG_Pfr_Container_BtgP3.bin')

