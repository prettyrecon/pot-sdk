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

 * [2019/04/24]
    - starting
"""

################################################################################
import io
import sys
import pathlib
import tempfile
import pyscreenshot as ImageGrab
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
PLATFORM = ['Linux',]
OUTPUT_TYPE = 'json'
DESCRIPTION = 'Pam for HA. It reads json scenario files by LA Stu and runs'

################################################################################
@func_log
def screenshot(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    mcxt.logger.info('>>>starting...')

    img = ImageGrab.grab(argspec.coord)
    buffer = io.BytesIO()

    img.save(buffer, 'PNG')
    if not argspec.path:
        tempdir = pathlib.Path(tempfile.gettempdir())
        temppng = tempdir / pathlib.Path('temp.png')
        file_path = str(temppng)
    else:
        file_path = argspec.path
    img.save(file_path, 'PNG')

    buffer.seek(0)
    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=file_path,
                                MESSAGE="")
    sys.stdout.write(str(result))
    mcxt.logger.info('>>>end...')
    return buffer

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
        mcxt.add_argument('--path', re_match='.*[.](png|PNG).*$',
                          type=str, default=None, metavar='screenshot_path',
                          help='screenshot path')
        mcxt.add_argument('--coord', nargs=4, type=int, default=None,
                          help='x1 y1 x2 y2')

        argspec = mcxt.parse_args(args)
        return screenshot(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)