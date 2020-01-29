#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Duk Kyu Lim <deokyu@argos-labs.com>
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
import platform

from subprocess import Popen, PIPE

from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from alabs.common.util.vvlogger import StructureLogFormat


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

CURRENT_PLATFORM = platform.system()

################################################################################
def for_window(mcxt, argspec):
    method = 'process_name' if argspec.process_name else 'pid_number'
    cmd = "taskkill {} {} {}"
    option_1 = {'process_name': '/im', 'pid_number': '/pid'}
    target = str(argspec.process_name if method == 'process_name'
                 else argspec.pid)
    option_2 = '/f' if argspec.force else ''
    return cmd.format(option_1[method], target, option_2)

def for_darwin(mcxt, argspec):
    target = argspec.process_name
    cmd = '{} {}'.format('killall', target)
    return cmd


def for_linux(mcxt, argspec):
    # method = 'killall' if argspec.process_name in vars(
    #     argspec) else 'kill'
    target = argspec.process_name
    cmd = '{} {}'.format('killall', target)
    return cmd


CALLER = {'Windows': for_window, 'Linux': for_linux, 'Darwin': for_darwin}

################################################################################
@func_log
def stop_process(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('>>>starting...')
    cmd = CALLER[CURRENT_PLATFORM](mcxt, argspec)
    mcxt.logger.debug(StructureLogFormat(CMD=cmd))
    with Popen(
        '{}'.format(cmd), shell=True, stdout=PIPE) as proc:
        pass
        # ret = proc.stdout.read()
        # mcxt.logger.info(ret)

    mcxt.logger.info('>>>end...')
    return proc.returncode


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
        ###################################### for app dependent parameters
        group = mcxt.add_mutually_exclusive_group(required=True)
        group.add_argument('--process_name', '-n', metavar='PROCESS NAME',
                           type=str, help='')
        group.add_argument('--pid', '-p', metavar='PROCESS PID',
                          type=int, help='' )

        mcxt.add_argument('--force', '-f', action='store_true', default=False,
                          help='')
        argspec = mcxt.parse_args(args)
        return stop_process(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

