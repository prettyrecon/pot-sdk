#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
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

 * [2019/03/29]
    - starting
"""

################################################################################
import sys
import enum
import wda
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
PLATFORM = ['darwin']
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

################################################################################
class TapMotionType(enum.Enum):
    TAP = 'touch'
    DRAG = 'drag'


################################################################################
class TapType(enum.Enum):
    ONEFINGER = 'one'
    TWOFINGER = 'two'
    THREEFINGER = 'three'

################################################################################
@func_log
def touch(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    mcxt.logger.info('>>>starting...')

    points: [] = argspec.coordinates
    motion = TapMotionType[argspec.motion]
    finger = TapType[argspec.finger]

    wda_url = "http://localhost"
    # 얻어와야 함 (포트매니저 필요)
    wda_port = 8100

    client = wda.Client(url='{url}:{port}'.format(url=wda_url, port=wda_port))
    session = client.session()

    if motion == TapMotionType.TAP:
        if len(points) >= 2:
            x, y = points[0], points[1]
        else:
            raise ArgsError('Need more args')
        session.tap(x=x, y=y)
    elif motion == TapMotionType.DRAG:
        if len(points) >= 4:
            x, y, x2, y2 = points[0], points[1], points[2], points[3]
        else:
            raise ArgsError('Need more args')
        session.swipe(x1=x, y1=y, x2=x2, y2=y2)

    mcxt.logger.info('>>>end...')

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
    platform=['darwin'],
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
                            default=TapMotionType.TAP.name,
                            choices=[
                                TapMotionType.TAP.name,
                                TapMotionType.DRAG.name, ],
                            help='')
        mcxt.add_argument('--finger',
                            default=TapType.ONEFINGER.name,
                            choices=[
                                TapType.ONEFINGER.name, ],
                            help='')
        ########################################################################
        mcxt.add_argument('coordinates', nargs='+', type=int, default=None,
                          metavar='COORDINATE', help='X Y [X2] [Y2]')

        argspec = mcxt.parse_args(args)
        return touch(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)