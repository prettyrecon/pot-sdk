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
import sys
import pyautogui
import keyboard
import pyperclip
import pickle
from alabs.common.util.vvargs import ModuleContext
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


################################################################################
def type_text(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('TypeText is Running...')
    mcxt.logger.debug(StructureLogFormat(ARGS_SPEC=argspec.__dict__))
    if argspec.pickle:
        with open(argspec.pickle, 'rb') as f:
            text = pickle.load(f)
    else:
        text = argspec.text
    if not argspec.interval:
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
    else:
        # pyautogui.typewrite(text.encode('cp949'), interval=argspec.interval)
        # pyautogui.typewrite(text.encode('cp949'), interval=argspec.interval)
        keyboard.write(text)
    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=None, MESSAGE="")
    sys.stdout.write(str(result))
    mcxt.logger.info('TypeText is Done.')
    return result


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
        ########################################################################
        mcxt.add_argument('text', type=str,
                          help='Text to type on an application')
        mcxt.add_argument('--pickle', type=str, help='')
        mcxt.add_argument('--interval', type=float, default=0.15,
                          help='Interval')

        argspec = mcxt.parse_args(args)
        return type_text(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

