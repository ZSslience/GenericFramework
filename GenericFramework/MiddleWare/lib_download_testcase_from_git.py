"""
Performs to download the test cases scripts by git clone cmd.
Title      	: lib_dowload_testcase_from_git.py
Author(s)  	: Liang Yan
Description	: Things to perform:
            1. Get the parameter(username, password, git_url, local_dir) from config file.
            2. Execute the git cmd and check if success download test script.
"""
from __future__ import unicode_literals, print_function
from subprocess import Popen, PIPE
import os
from SoftwareAbstractionLayer import lib_parse_config



def download_testcase():
    """
    Function Name       : download_testcase
    Parameters          : None
    Functionality       : Get git cmd parameter and execute git clone cmd to download the test case scripts.
    Function Invoked    : get_value
    Return Value        : 'success' if success download the test cases scripts, else the error msg for debugging.
    parameter in config file:
        username: username for git account
        password: The password of the username.
        git_url: The test case git clone url,it's better to use https url for win os.
        local_dir: The destination folder which would save the test case.
    """
    SUT_CONFIG_CLIENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
                                      r"SoftwareAbstractionLayer\system_configuration.ini")
    config = lib_parse_config.ParseConfig()
    username = config.get_value(SUT_CONFIG_CLIENTS, 'Getting Test Scripts', 'username')
    password = config.get_value(SUT_CONFIG_CLIENTS, 'Getting Test Scripts', 'password')
    git_url = config.get_value(SUT_CONFIG_CLIENTS, 'Getting Test Scripts', 'git_url')
    local_dir = config.get_value(SUT_CONFIG_CLIENTS, 'Getting Test Scripts', 'local_dir')
    if '@' in password:
        password = password.replace('@','%40')
    if ':' in password:
        password = password.replace(':', '%3A')
    git_cmd = '{}//{}:{}@{}'.format(git_url.split('//')[0], username, password, git_url.split('//')[1])
    cmd = ['git', 'clone', '--progress', git_cmd, local_dir]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    outs, errs = proc.communicate()
    if r'Receiving objects: 100%' in errs.decode('ascii'):
        return 'success'
    else:
        return errs.decode('ascii')


def test():
    """function for test this lib api"""
    status = download_testcase()
    if status == 'success':
        print('Download testcase sucessfully.')
    else:
        print('Failed to Download test case.\n%s' % status)


if __name__ == '__main__':
    test()
