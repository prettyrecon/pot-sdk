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
import enum
import pyautogui
from argparse import Namespace
from alabs.pam.rpa.autogui.click import ClickMotionType, ClickType, to_int
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
class BaseAreaType(enum.Enum):
    BROWSER = 'Browser'
    FULLSCREEN = 'FullScreen'
    ELEMENT = 'Element'
    CURSOR = 'Cursor'


################################################################################
@func_log
def click(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    mcxt.logger.info('>>>starting...')
    pyautogui.FAILSAFE = False

    # 캡쳐파일 불러오기
    # 캡쳐파일과 화면 비교
    # 마우스 포인터를 해당 좌표에 위치시키기
    x, y = argspec.coordinates
    # 버튼
    motion = ClickMotionType[argspec.motion].value
    button = ClickType[argspec.button].value

    if argspec.relativepos:
        pyautogui.move(x, y)
    else:
        pyautogui.moveTo(x, y)
    if button != 'None':
        action = getattr(pyautogui, motion)
        action(button=button)

    mcxt.logger.info('>>>end...')

    return pyautogui.position()


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
        mcxt.add_argument('--motion',
                            default=ClickMotionType.CLICK.name,
                            choices=[
                                ClickMotionType.CLICK.name,
                                ClickMotionType.DOUBLE.name,
                                ClickMotionType.TRIPLE.name,
                                ClickMotionType.PRESS.name,
                                ClickMotionType.RELEASE.name, ],
                            help='')
        mcxt.add_argument('--button',
                            default=ClickType.LEFT.name,
                            choices=[
                                ClickType.RIGHT.name,
                                ClickType.LEFT.name,
                                ClickType.NONE.name, ],
                            help='')
        mcxt.add_argument('--relativepos', action='store_true',
                          help='Move the mouse cursor over a few pixels '
                               'relative to its current postion')
        ########################################################################
        mcxt.add_argument('coordinates', nargs=2, type=int, default=None,
                          metavar='COORDINATE', help='X Y')

        argspec = mcxt.parse_args(args)
        return click(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)