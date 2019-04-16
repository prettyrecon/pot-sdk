#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.rpa.desktop.execute_process
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

 * [2019/04/16]
    - starting
"""

################################################################################
import wda
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
@func_log
def execute_process(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """
    mcxt.logger.info('>>>starting...')
    client = wda.Client(url='{url}:{port}'.format(url=argspec.wda_url,
                                                  port=argspec.wda_port))
    session = client.session(bundle_id=argspec.bundleid,
                             arguments=argspec.args)
    mcxt.logger.info(session.bundle_id)
    mcxt.logger.info('>>>end...')
    return session.bundle_id


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
        ###################################### for app dependent parameters
        mcxt.add_argument('bundleid', help='Application bundle id')
        mcxt.add_argument('--args', type=str, nargs='+',
                          help='-u https://www.google.com/ncr', default=None)
        mcxt.add_argument('--wda_url', type=str,
                          default='http://localhost', help='')
        mcxt.add_argument('--wda_port', type=str, default='8100', help='')

        argspec = mcxt.parse_args(args)
        return execute_process(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

