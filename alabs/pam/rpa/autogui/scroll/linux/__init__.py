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
import win32con, win32api
from alabs.pam.utils.windows import get_registry_key_value
from alabs.common.util.vvlogger import StructureLogFormat
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

################################################################################
@func_log
def scroll(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info('>>> MouseScroll Start ...')
    x = argspec.horizon
    y = argspec.vertical
    if not any([x, y]):
        raise ArgsError
    if y:
        scroll_per_lines = get_registry_key_value('HKEY_CURRENT_USER',
                                                  'Control Panel\\Desktop',
                                                  'WheelScrollLines')[0]
        wheel_delta = win32con.WHEEL_DELTA

        y = int((y * -1 * wheel_delta) / int(scroll_per_lines))
        mx, my = pyautogui.position()
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, mx, my, y, 0)
        log = StructureLogFormat(SCROLL_PER_LINES=scroll_per_lines,
                                 WHEEL_DELTA=wheel_delta,
                                 LINES=y,
                                 USER_VALUE_Y=argspec.vertical)
        mcxt.logger.debug(log)
    if x:
        pyautogui.hscroll(x)
    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=(x, y),
                                MESSAGE="")
    sys.stdout.write(str(result))
    mcxt.logger.info('>>> MouseScroll End')

    return x, y

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
        mcxt.add_argument('--horizon', '-x',  type=int, default=0,  help='')
        mcxt.add_argument('--vertical', '-y', type=int, default=0, help='')
        argspec = mcxt.parse_args(args)
        return scroll(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)