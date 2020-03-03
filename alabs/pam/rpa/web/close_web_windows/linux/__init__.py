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

from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import NoSuchElementException, \
    NoSuchFrameException, TimeoutException

from alabs.common.util.vvargs import ModuleContext, func_log
from alabs.common.util.vvlogger import StructureLogFormat
from alabs.pam.rpa.web import create_driver_session


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
def close_popup(mcxt, argspec):
    """
    LocateImage
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info("Close Popup start ...")

    status = True
    message = ''
    try:
        # Selenium 접속
        driver = create_driver_session(argspec.session_id, argspec.url)
        target = argspec.handle_ids
        all_handles = driver.window_handles
        for hdr in all_handles:
            if hdr not in target:
                continue
            driver.switch_to.window(hdr)
            driver.close()

    except MaxRetryError as e:
        # 잘못된 URL. 셀레니움에 접속 할 수 없음
        status = False
        message = f'Failed to connect to the remote browser with {argspec.url}'
    except TimeoutException as e:
        status = False
        message = f'Time is up. Failed to find the element.'

    except Exception as e:
        status = False
        mcxt.logger.exception(str(e))
        message = str(e)

    result = StructureLogFormat(RETURN_CODE=status,
                                RETURN_VALUE={'RESULT': status},
                                MESSAGE=message)
    std = {True: sys.stdout, False: sys.stderr}[status]
    std.write(str(result))

    mcxt.logger.info("Close popup end ...")
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
        mcxt.add_argument('url', type=str, help='Remote selenium address')
        mcxt.add_argument('session_id', type=str, help='Selenium session_id')
        mcxt.add_argument('handle_ids', type=str, nargs='+',
                          help='Window title name')

        argspec = mcxt.parse_args(args)
        return close_popup(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

