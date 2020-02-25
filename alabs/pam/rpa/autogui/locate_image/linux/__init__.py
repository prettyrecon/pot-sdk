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
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from alabs.pam.rpa.autogui.click import ClickMotionType, ClickType, to_int
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
@func_log
def locate_image(mcxt, argspec):
    """
    LocateImage
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info("LocateImage start ...")

    # 이미지 좌표 구하기
    # Confidence 기본 값은 0.999
    try:
        location = pyautogui.locateOnScreen(
            argspec.filename,
            confidence=argspec.similarity * 0.01)
    except Exception as e:
        result = StructureLogFormat(RETURN_CODE=False, RETURN_VALUE=None,
                                    MESSAGE=str(e))
        mcxt.logger.error(result)
        sys.stderr.write(str(result))
        return

    if not location:
        result = StructureLogFormat(RETURN_CODE=False, RETURN_VALUE=None,
                                    MESSAGE='Failed to find location.')
        mcxt.logger.error(result)
        sys.stderr.write(str(result))
        exit(-1)
    x, y, *_ = location
    mcxt.logger.debug(StructureLogFormat(LOCATION_X=str(x), LOCATION_Y=str(y)))

    # 버튼
    motion = ClickMotionType[argspec.motion].value
    button = ClickType[argspec.button].value

    cx, cy = argspec.coordinates
    x += cx
    y += cy
    mcxt.logger.debug(StructureLogFormat(LOCATION_X=str(x), LOCATION_Y=str(y),
                                         COODINATE_X=str(cx),
                                         COODINATE_Y=str(cy)))

    action = getattr(pyautogui, motion)
    action(button=button, x=x, y=y)

    # TODO: 실행결과 값 JSON 형태로 반환 필요.

    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=None, MESSAGE="")
    sys.stdout.write(str(result))
    mcxt.logger.info("LocateImage end ...")
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
        # 필수 입력 항목
        mcxt.add_argument('filename', re_match='.*[.](png|PNG).*$',
                          metavar='image_filename.png',  help='')
        mcxt.add_argument('--searchon',
                          choices=['app', 'fullscreen', 'web'],
                          default='fullscreen')
        mcxt.add_argument('--name', type=str)
        mcxt.add_argument('--title', type=str)

        mcxt.add_argument('--region', nargs=4, type=int, default=None,
                          metavar='0', help='')
        mcxt.add_argument('--similarity', type=int, metavar='50',
                          default=50, min_value=0, max_value=100, help='')
        mcxt.add_argument('--coordinates', type=int, nargs=2, default=[0, 0],
                          metavar='0', help='')
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
        argspec = mcxt.parse_args(args)

        return locate_image(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

