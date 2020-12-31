import os
import subprocess
import re


class SF600(object):
    def __init__(self, binary=None):
        self.bmc = None
        self.chip = None
        if binary is not None:
            self.sf600 = binary
        else:
            self.sf600 = r"C:\Program Files (x86)\DediProg\SF100\dpcmd.exe"

    @staticmethod
    def send_cmd(cmd):
        print(cmd)
        result = []
        try:
            result = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                shell=True
                )
        except subprocess.CalledProcessError as e:
            # get the result string from the process output
            # then re-raise (finally will be called first)
            result = e.output
            # raise
        finally:
            # always log the output
            lines = result.splitlines()
            for line in lines:
                print(line.decode())
        return lines

    def parse_output(self, output):
        exp_chipID = r"(?P<chip>[A-Za-z0-9]+) parameters [A-Za-z]+"
        exp_erase_ok = r"Erase (?P<erase>[A-Za-z0-9]+)"
        exp_program_ok = r"Automatic program (?P<program>[A-Za-z0-9]+)"
        exp_verify_ok = r"Verify (?P<verify>[A-Za-z0-9]+)"
        exp_checksum1 = r"Checksum.file.: (?P<checksum1>[A-Za-z0-9]+)"
        exp_checksum2 = r"Checksum.Written part of file.: (?P<checksum2>[A-Za-z0-9]+)"
        exp_error = r"Error: (?P<error>[A-Za-z0-9]+)"
        exp_finish = r"Operation completed."
        chipID = re.compile(exp_chipID)
        erase_ok = re.compile(exp_erase_ok)
        program_ok = re.compile(exp_program_ok)
        verify_ok = re.compile(exp_verify_ok)
        checksum1 = re.compile(exp_checksum1)
        checksum2 = re.compile(exp_checksum2)
        finish = re.compile(exp_finish)
        error1 = re.compile(exp_error)
        error2 = re.compile('One instance of DediProg GUI or Console application is already running')
        errors = [error1, error2]
        end = False
        for line in output:
            line = line.decode()
            if 'elapsed' in line:
                # last = line
                del line
            else:
                m1 = chipID.search(line)
                m2 = erase_ok.search(line)
                m3 = program_ok.search(line)
                m4 = verify_ok.search(line)
                m5 = checksum1.search(line)
                m6 = checksum2.search(line)
                m7 = finish.search(line)
                if m7 and end is False:
                    end = True
                if m1 is not None:
                    print("chip ID", m1.group("chip"))
                if m2 is not None:
                    print("Erase Status", m2.group("erase"))
                    end = True
                if m3 is not None:
                    print("Programming Status", m3.group("program"))
                if m4 is not None:
                    print("Verify Status", m4.group("verify"))
                if m5 is not None:
                    print("Checksum File", m5.group("checksum1"))
                if m6 is not None:
                    print("Checksum Chip", m6.group("checksum2"))
                for error in errors:
                    if error.search(line) is not None:
                        tmp = "Error in dpcmd.exe: " + line
                        print(tmp)
                        # fail = True
                        return False
        if not end:
            print('Operation not completed, please verify Dediprog software')
            return False
        return True

    def burn(self, bmc):
        self.bmc = bmc
        # start to burn the bmc, to start you need to set correct the variable of the class
        print("start")
        if self.bmc is None:
            print("bmc file is not set")
            return False

        if not os.path.exists(self.sf600):
            print('Configuration', "Cannot find sf600 executable")
            return False

        # Select sf600 operation mode:
        cmd = self.sf600

        # kills dediprog if is opened.
        ps = os.popen("C:/WINDOWS/system32/tasklist.exe", "r")
        pp = ps.readlines()
        ps.close()
        process = 'dedipro.exe'
        for x in pp:
            if x.lower().startswith(process):
                print(x)
                os.system("taskkill /im %s" % process)
                print("Killing dediprog process before starting.")

        for x in range(3):
            if not self.chip:
                print("Command %d: '%s' %s %s %s %s %s" % (x, cmd, '-d', '-u', self.bmc, '-v ', '-i'))
                result = self.send_cmd([cmd, '-d', '-u', self.bmc, '-v', '-i'])
            else:
                print("Command %d: '%s' %s %s %s %s %s %s"
                      % (x, cmd, '-u', self.bmc, '-v ', '-i', '--type', self.chip))
                result = self.send_cmd([cmd, '-u', self.bmc, '-v', '-i', '--type', self.chip])
            if self.parse_output(result):
                return True
            else:
                continue
        print("Failed to flash BMC.")
        return False


def main():
    sf = SF600()
    print(sf.burn(r'C:\Users\sys_eval\Documents\Liang\WhitleyOBMC-wht-0.54-0-g017dda-a6da583-pfr-full.ROM'))


if __name__ == '__main__':
    main()
