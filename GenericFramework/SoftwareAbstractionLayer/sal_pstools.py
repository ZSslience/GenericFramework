import os
from SoftwareAbstractionLayer import lib_constants as lc
from SoftwareAbstractionLayer import lib_parse_config



def ps_tools_run(cmd_input, clear=True, remo_file=False):
    """
    Function Name       : ps_tools_run()
    Parameters          : cmd_input(str): Command input to remote script run
                          stdout will be redirected to log file defined in
                          system_configuration.ini
                          i.e: "ipconfig", "python P:ATH\\TO\\SCRIPT"
                          remo_file(bool) : To use the remote file or not
                          clear(bool)     : Clean log file before run.
    Functionality       : Send remote command to run on SUT
    Function Invoked    : PSTools Binaries
    Return Value        : (bool) True  - Run Succeed
                                 False - Run Failed
    """
    SUT_CONFIG = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), os.path.pardir,
            r"SoftwareAbstractionLayer\system_configuration.ini")
    config = lib_parse_config.ParseConfig()
    pst_dir = str(config.get_value(
        SUT_CONFIG, 'PS_Tools', 'PST_DIR'))
    ps_exec_rp = str(config.get_value(
        SUT_CONFIG, 'PS_Tools', 'PS_EXEC'))
    cmd_log = str(config.get_value(
        SUT_CONFIG, 'PS_Tools', 'PS_LOG'))
    sut_host = r"\\" + str(config.get_value(
        SUT_CONFIG, 'SSH Configuration', 'HOST'))
    sut_user = str(config.get_value(
        SUT_CONFIG, 'SSH Configuration', 'USER'))
    sut_pswd = str(config.get_value(
        SUT_CONFIG, 'SSH Configuration', 'PASS'))
    run_wrapper = 'remote.cmd'

    cmd_head = os.path.join(lc.TOOLPATH + "\\" + pst_dir
                            + "\\" + ps_exec_rp + " -accepteula" +" ")
    if remo_file:
        cmd_info = str(sut_host + " -u " + sut_user + " -p "
                       + sut_pswd + " -i 1 ")
        if cmd_input == "":
            print("WARNING: Pls. provide [commands(str)] run on remote SUT.")
            run_start = False
        else:
            cmd_tail = cmd_input

    else:
        cmd_info = str(sut_host + " -u " + sut_user + " -p "
                       + sut_pswd + " -i 1 -c -f ")
        cmd_tail = os.path.join(lc.TOOLPATH + "\\" + pst_dir
                                + "\\" + run_wrapper)

        if clear is True:
            sut_cmd = open(cmd_tail, 'w')
            sut_cmd.write("del " + cmd_log)
            sut_cmd.close()
            run_cmd = (cmd_head + cmd_info + cmd_tail)
            os.system(run_cmd)
        run_cmd = None

        if cmd_input == "":
            print("WARNING: Pls. provide [commands(str)] run on remote SUT.")
            run_start = False
        else:
            sut_cmd = open(cmd_tail, 'w')
            sut_cmd.write(cmd_input + " >> " + cmd_log + "\r")
            sut_cmd.close()
    run_cmd = (cmd_head + cmd_info + cmd_tail)
    print(run_cmd)
    remote_run = os.system(run_cmd)
    if remote_run == 0:
        run_start = True
    else:
        run_start = False
    return(run_start)


if __name__ == "__main__":
    ps_tools_run("ipconfig", clear=False)
    ps_tools_run("dir", clear=True)
    # Need to prepare or push a file to be executed
    ps_tools_run(r"c:\remote.cmd", remo_file=True)
