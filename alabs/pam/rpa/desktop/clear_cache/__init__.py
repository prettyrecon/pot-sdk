#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Raven Lim <deokyu@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Raven Lim

Change Log
--------

 * [2019/01/30]
    - starting
"""

################################################################################
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
import subprocess


################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['windows', 'darwin', 'linux']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'


################################################################################
@func_log
def clear_cache(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('>>>starting...')
    cmd = list()

    if argspec.ie:
        cmd.append('RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8')
        cmd.append('erase "%LOCALAPPDATA%\\Microsoft\\Windows\\Tempor~1\\*.*" /f /s /q')
        cmd.append('for /D %%i in ("%LOCALAPPDATA%\\Microsoft\\Windows\\Tempor~1\\*") do RD /S /Q "%%i"')

    if argspec.chrome:
        cmd.append('Set uname=%username%')
        cmd.append('set ChromeDataDir="C:\\Users\\%uname%\\AppData\\Local\\Google\\Chrome\\User Data\\Default"')
        cmd.append('set ChromeCache=%ChromeDataDir%\\Cache')
        cmd.append('del /q /s /f %ChromeCache%\\*.*')

    if argspec.chrome_cookie:
        cmd.append('Set uname=%username%')
        cmd.append('set ChromeDataDir="C:\\Users\\%uname%\\AppData\\Local\\Google\\Chrome\\User Data\\Default"')
        cmd.append('set ChromeCache=%ChromeDataDir%\\Cache')
        cmd.append('del /q /f %ChromeDataDir%\\*Cookies*.*')

    if argspec.chrome_all:
        cmd.append('Set uname=%username%')
        cmd.append('set ChromeDataDir="C:\\Users\\%uname%\\AppData\\Local\\Google\\Chrome\\User Data\\Default"')
        cmd.append('del /q /f %ChromeDataDir%\\*.*')

    if cmd:

        cmd = ';'.join(cmd)
        cmd = 'cmd /c ' + cmd
        print(cmd)
        subprocess.Popen(cmd, shell=True)

    mcxt.logger.info('>>>end...')

    return

################################################################################
def _main(*args):
    """
    Build user argument and options and call plugin job function
    :param args: user arguments
    :return: return value from plugin job function

    ..note:: _main 함수에서 사용되는 패러미터(옵션) 정의 방법
플러그인 모듈은 ModuleContext 을 생성하여 mcxt를 with 문과 함께 사용
    owner='ARGOS-LABS',
    group='pam',
    version='1.0',
    platform=['windows', 'darwin', 'linux'],
    output_type='text',
    description='HA Bot for LA',
    test_class=TU,
    """
    with ModuleContext(
        owner=OWNER,
        group=GROUP,
        version=VERSION,
        platform=PLATFORM,
        output_type=OUTPUT_TYPE,
        description=DESCRIPTION,
    ) as mcxt:
        # --ie --chrome --chrome_cookie
        mcxt.add_argument('--ie', action='store_true',
                          help='Delete the caches of IE.')
        mcxt.add_argument('--chrome', action='store_true',
                          help='Delete the caches of Chrome.')
        mcxt.add_argument('--chrome_cookie', action='store_true',
                          help='Delete Chrome cookie')
        mcxt.add_argument('--chrome_all', action='store_true',
                          help='Delete all of the chrome cache directory')
        argspec = mcxt.parse_args(args)

        return clear_cache(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

