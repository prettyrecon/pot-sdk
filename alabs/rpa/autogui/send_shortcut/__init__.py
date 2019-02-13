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
import pyautogui
from pyautogui import KEY_NAMES
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit


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

FILTER_CHAR = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", ]
KEYS = list(filter(lambda x: x not in FILTER_CHAR, KEY_NAMES))

################################################################################
@func_log
def send_shortcut(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    # --txt는 LA Stu에서 생성한 키시퀀스 하위호환
    mcxt.logger.info('>>>starting...')
    if not argspec.keys:
        raise ArgsError
    for key in argspec.keys:
        if key not in KEYS:
            raise ArgsError("{} is not valid. Please check the help message.")
    pyautogui.hotkey(*argspec.keys, interval=argspec.interval)
    mcxt.logger.info('>>>end...')

    return argspec.keys

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
        k = ' '.join([str(v) for v in KEYS])
        mcxt.add_argument('keys', nargs='+', help=k)
        mcxt.add_argument('--interval', type=float, default=0.05, help='')
        argspec = mcxt.parse_args(args)

        return send_shortcut(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

