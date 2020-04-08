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
import windsound as ws
import pathlib
from playsound import playsound
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
def beep(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('Start...')
    if argspec.beep:
        freq = 2000
        duration = argspec.duration * 1000
        ws.Beep(freq, duration)
    elif argspec.sound:
        current_path = pathlib.Path(pathlib.Path(__file__).resolve()).parent
        siren = str(current_path / pathlib.Path('siren.wav'))
        ws.PlaySound(siren)

    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=None, MESSAGE="")
    sys.stdout.write(str(result))
    mcxt.logger.info('End...')
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
        mcxt.add_argument('--beep', type=str)
        mcxt.add_argument('--sound', type=str)
        mcxt.add_argument('--duration', type=int, default=2)

        argspec = mcxt.parse_args(args)
        return beep(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

