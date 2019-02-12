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
class ClickMotionType(enum.Enum):
    CLICK = 'click'
    PRESS = 'mouseDown'
    RELEASE = 'mouseUp'


################################################################################
class ClickType(enum.Enum):
    RIGHT = 'Right'
    LEFT = 'Left'
    DOUBLE = 'Double'
    NONE = 'None'


################################################################################
class BaseAreaType(enum.Enum):
    BROWSER = 'Browser'
    FULLSCREEN = 'FullScreen'
    ELEMENT = 'Element'
    CURSOR = 'Cursor'

################################################################################
def to_int(value:str):
    return tuple((int(v) for v in value.split(',')))

################################################################################
def motion_type_for_la(click_motion_type, click_type):
    motion = None
    button = None
    if ClickMotionType.RELEASE.value == click_motion_type:
        motion = 'mouseUp'
    elif ClickMotionType.PRESS.value == click_motion_type:
        motion = 'mouseDown'
    elif ClickMotionType.CLICK.value == click_motion_type:
        motion = 'click'

    if ClickType.LEFT.value == click_type:
        button = 'left'
    elif ClickType.RIGHT.value == click_type:
        button = 'right'
    elif ClickType.DOUBLE.value == click_type:
        motion = 'doubleClick'
        button = 'left'

    if any([motion, button]):
        raise ValueError("MOTION or CLICK TYPE VALUE ERROR")
    return motion, button

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
    button = ''
    motion = ''
    x, y = to_int(argspec.clickpoint)
    click_motion_type = argspec.clickmotiontype
    click_type = argspec.clicktype
    motion, button = motion_type_for_la(click_motion_type, click_type)

    action = getattr(pyautogui, motion)
    action(button=button, x=x, y=y)

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
        mcxt.add_argument('--attname', help='NOT SUPPORTED YET')
        mcxt.add_argument('--attvalue', help='NOT SUPPORTED YET')
        mcxt.add_argument('--baseareatype',
                            default=BaseAreaType.FULLSCREEN.value,
                            choices=[
                                BaseAreaType.BROWSER.value,
                                BaseAreaType.FULLSCREEN.value,
                                BaseAreaType.ELEMENT.value,
                                BaseAreaType.CURSOR.value],
                            help='')
        mcxt.add_argument('--classpath', help='NOT SUPPORTED YET.')
        mcxt.add_argument('--framename', help='NOT SUPPORTED YET.')
        mcxt.add_argument('--tagname', help='NOT SUPPORTED YET.')
        mcxt.add_argument('--clickmotiontype',
                            default=ClickMotionType.CLICK.value,
                            choices=[
                                ClickMotionType.CLICK.value,
                                ClickMotionType.PRESS.value,
                                ClickMotionType.RELEASE.value, ],
                            help='')
        mcxt.add_argument('--clicktype',
                            default=ClickType.LEFT.value,
                            choices=[
                                ClickType.RIGHT.value,
                                ClickType.LEFT.value,
                                ClickType.DOUBLE.value,
                                ClickType.NONE.value, ],
                            help='')
        ########################################################################
        mcxt.add_argument('clickpoint',
                            type=str,
                            re_match='^\d+\s*,\s*\d+',
                            help='0, 0')

        argspec = mcxt.parse_args(args)
        return click(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

