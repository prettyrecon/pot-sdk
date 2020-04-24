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
from alabs.common.util.vvargs import ModuleContext, func_log, str2bool, \
    ArgsError, ArgsExit
from alabs.common.util.vvlogger import StructureLogFormat
from alabs.pam.rpa.autogui.find_image_location import find_all

from pam.utils.process import run_operation
from alabs.pam.rpa.desktop.screenshot import main as screenshot


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
def find_image_location(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info('FindImage start ...')

    # 현재화면 스크린 샷
    op = screenshot
    args = ('--path', 'temp.png')
    rst = run_operation(op, args)
    if not rst['RETURN_CODE']:
        sys.stderr.write(str(rst))
        return rst
    source_image = rst['RETURN_VALUE']

    # 같은 이미지 리스트
    order_number = argspec.order_number
    limit = 1000
    if order_number == 0:
        limit = 1
    locations = find_all(argspec.filename, source_image,
                         argspec.save_file,
                         argspec.region,
                         argspec.similarity * 0.01,
                         limit=limit)

    value = False
    location = None
    message = 'Failed to find location.'
    if locations:
        if order_number == 0:
            location = locations[0]
        else:
            location = locations[order_number - 1]
        value = True
        location = ', '.join(map(str, list(location)))
        message = ''

    result = StructureLogFormat(RETURN_CODE=True,
                                RETURN_VALUE={
                                    'RESULT': value,
                                    'VALUE': location},
                                MESSAGE=message)

    sys.stdout.write(str(result))
    mcxt.logger.info('FindImage end ...')
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
        mcxt.add_argument('--region', nargs=4, type=int, default=None,
                          metavar='0', help='')
        mcxt.add_argument('--similarity', type=int, metavar='50',
                          default=50, min_value=0, max_value=100, help='')
        mcxt.add_argument('--timeout', type=int, default=5)
        mcxt.add_argument('--order_number', type=int, default=0,
                          help="chosen_number")
        mcxt.add_argument('--save_file', type=str, default=None,
                          help="Path that result will be stored.")
        argspec = mcxt.parse_args(args)
        return find_image_location(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)