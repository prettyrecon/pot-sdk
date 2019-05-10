#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.rpa.autogui.find_image_location.ios
====================================
.. moduleauthor:: Injoong Kim <nebori92@argos-labs.com>
.. note:: VIVANS License

Description
===========
ARGOS LABS PAM For LA

Authors
===========

* Injoong Kim

Change Log
--------

 * [2019/04/12]
    - starting
"""

################################################################################
import wda
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from alabs.rpa.autogui.click import ClickMotionType, ClickType, to_int

from alabs.rpa.autogui.find_image_location.ios \
    import find_image_location

from alabs.rpa.autogui.click.ios import touch


################################################################################
# Version
NUM_VERSION = (0, 9, 0)
VERSION = ".".join(str(nv) for nv in NUM_VERSION)
__version__ = VERSION

OWNER = 'ARGOS-LABS'
GROUP = 'Pam'
PLATFORM = ['darwin']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

################################################################################
@func_log
def locate_image(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info('>>>starting...')
    # 이미지 좌표 구하기
    location = find_image_location(mcxt, argspec)
    if not location:
        return None
    x, y, *_ = location
    cx, cy = argspec.coordinates
    x += cx
    y += cy
    argspec.coordinates = [x, y]
    touch(mcxt, argspec)
    # client = wda.Client(url='{url}:{port}'.format(url=argspec.wda_url,
    #                                               port=argspec.wda_port))
    # session = client.session()
    # session.tap(x=x, y=y)
    mcxt.logger.info('>>>end...')
    if argspec.verbose:
        print(x, y)
    return location

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
        mcxt.add_argument('--region', nargs=4, type=int, default=None,
                          metavar='0', help='')
        mcxt.add_argument('--similarity', type=int, metavar='50',
                          default=50, min_value=0, max_value=100, help='')
        mcxt.add_argument('--coordinates', type=int, nargs=2, default=[0, 0],
                          metavar='0', help='')
        mcxt.add_argument('--wda_url', type=str, default='http://localhost', help='')
        mcxt.add_argument('--wda_port', type=str, default='8100', help='')
        mcxt.add_argument('--motion',
                          default=ClickMotionType.CLICK.name,
                          choices=[
                              ClickMotionType.CLICK.name,
                              ClickMotionType.DOUBLE.name,
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

