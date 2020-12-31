import subprocess
import os
import re


class QuartusError(Exception):
    """Used when Quartus raise error """

    def __init__(self, error_msg):
        self.error_msg = error_msg

    def __str__(self):
        return 'Error={}'.format(self.error_msg)


class Quartus(object):
    """
        Use to program CPLD(.pof)
    """

    def __init__(self, path, binary=None, jtag_binary=None):
        self.path = path
        self.devices = {}
        if os.name != 'nt':
            error_msg = 'Only support win OS'
            raise QuartusError(error_msg)
        if binary is not None:
            self._binary = binary
        else:
            self._binary = r'C:\intelFPGA_pro\19.1\qprogrammer\quartus\bin64\quartus_pgm'
        if jtag_binary is not None:
            self._jtag_binary = jtag_binary
        else:
            self._jtag_binary = r'C:\intelFPGA_pro\19.1\qprogrammer\quartus\bin64\jtagconfig'

    @staticmethod
    def send_cmd(cmd):
        print(cmd)
        result = ''
        try:
            result = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
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
            for line in lines:
                print(line.decode())
        return lines

    def detect_devices(self, expect_cables=None, regex_device=None):
        if regex_device is not None:
            regex_device = regex_device
        else:
            regex_device = '10M'
        print("Quartus: checking JTAG cables detected")
        try:
            result = self.send_cmd(self._binary + ' --list')
        except subprocess.CalledProcessError:
            result = []
            pass
        regex = re.compile(r'.*\d+\)')
        count_cables = 0
        cable_list = []
        for rlt in result:
            if re.match(regex, rlt.decode()):
                count_cables += 1
                cable_list.append(rlt.decode().split(')')[-1].strip())
        if expect_cables is not None and count_cables != expect_cables:
            error_msg = 'Expected {} cables. detected {}'.format(expect_cables, count_cables)
            raise QuartusError(error_msg)
        for cable in cable_list:
            print("Quartus: checking cable {} devices detected".format(cable))
            try:
                result = self.send_cmd(self._binary + ' -a --cable "{}"'.format(cable))
            except subprocess.CalledProcessError:
                result = []
                pass
            regex = re.compile(regex_device)
            count_devices = sum(1 for rlt in result if re.search(regex, rlt.decode()))
            if count_devices == 0:
                error_msg = 'No devices under chain {}'.format(cable)
                raise QuartusError(error_msg)
            self.devices[cable] = count_devices
        return self.devices

    def verify_cable_hardware_frequency(self, cable):
        print("Quartus: get cable {} Hardware frequency".format(cable))
        cmd = '{} --getparam "{}" JtagClock'.format(self._jtag_binary, cable)
        try:
            result = self.send_cmd(cmd)
        except subprocess.CalledProcessError:
            print("Quartus: unable to read cable {} Hardware frequency".format(cable))
            return False
        correct_frequency = False
        for r in result:
            if '6M' in r.decode():
                correct_frequency = True
        return correct_frequency

    def set_hardware_frequency(self, cable):
        print("Quartus: set cable {} Hardware frequency to 6000000".format(cable))
        if not self.verify_cable_hardware_frequency(cable):
            cmd = '{} --setparam "{}" JtagClock 6000000'.format(self._jtag_binary, cable)
            try:
                self.send_cmd(cmd)
            except subprocess.CalledProcessError:
                print("Quartus: unable to set cable {} ".format(cable))
                return False
            return self.verify_cable_hardware_frequency(cable)
        else:
            return True

    def _find_pof_file(self, pof):
        files = os.listdir(self.path)
        filtered = [f for f in files if pof in f.lower() and f.endswith('.pof')]
        if len(filtered) == 1:
            return os.path.join(self.path, filtered[0])
        else:
            error_msg = 'failed to get pof file, should be only 1 {} pof file, find {} files'. \
                format(pof, len(filtered))
            raise QuartusError(error_msg)

    def program_cpld(self, abort_on_failure=True):
        program_result = True
        if len(self.devices) == 0:
            print('No devices to program')
            return False
        for cable, count_devices in self.devices.items():
            if not self.verify_cable_hardware_frequency(cable):
                if not self.set_hardware_frequency(cable):
                    print('unable to set cable {} hardware frequency'.format(cable))
                    return False
            cable_str = '--cable="{}"'.format(cable)
            if count_devices == 2:
                pof_file_main = self._find_pof_file('pfr')
                pof_file_debug = self._find_pof_file('debug')
                cmd = '{} {} -z -verify -m jtag -o "pv;{}@1" -o "pv;{}@2"'. \
                    format(self._binary, cable_str, pof_file_main, pof_file_debug)
            elif count_devices == 1:
                pof_file_globle = self._find_pof_file('global')
                cmd = '{} {} -z -verify -m jtag -o "pv;{}@1"'. \
                    format(self._binary, cable_str, pof_file_globle)
            else:
                error_msg = 'Can not handle one cable {} with {} devices'.format(cable, count_devices)
                raise QuartusError(error_msg)
            result = []
            try:
                result = self.send_cmd(cmd)
            except subprocess.CalledProcessError:
                print('Unable to program cpld')
                if abort_on_failure:
                    error_msg = 'Unable to program cpld'
                    raise QuartusError(error_msg)
                return False
            success_tag = 'Quartus Prime Programmer was successful. 0 errors'
            program_result_cable = False
            for slt in result:
                if success_tag in slt.decode():
                    print('successful programmer cable {} '.format(cable))
                    program_result_cable = True
                    break
            if not program_result_cable:
                program_result = False
        return program_result


class altera_system_console(object):
    def __init__(self, system_console_bin=None):
        if system_console_bin is None:
            sc_path = r'C:\intelFPGA_pro\19.1\qprogrammer\syscon\bin\system-console.exe --cli --disable_readline'
        else:
            sc_path = '{} --cli --disable_readline'.format(system_console_bin)
        self.console = subprocess.Popen(sc_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read_output(self):
        rtn = ""
        loop = True
        match = '%'
        while loop:
            out = self.console.stdout.read(1)
            if bytes(match, 'utf-8') == out:
                loop = False
            else:
                rtn = rtn + out.decode('utf-8')
        return rtn

    def cmd(self, cmd_string):
        self.console.stdin.write(bytes(cmd_string + '\n', 'utf-8'))
        self.console.stdin.flush()
        return self.read_output()

    def __del__(self):
        if hasattr(self, 'console'):
            self.console.terminate()


if __name__ == '__main__':
    q = Quartus(r'C:\Users\sys_eval\Documents\Liang')
    print(q.detect_devices())
    print(q.program_cpld())
