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
import subprocess
import selenium
from appium import webdriver

from alabs.common.util.vvargs import ModuleContext, func_log
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
def assemble_address(address:str, host:int):
    if not address.startswith(('http://', 'https://')):
        address = 'http://' + address
    return f'{address}:{host}'

################################################################################
@func_log
def window_object(mcxt, argspec):
    """
    LocateImage
    :param mcxt: module context
    :param argspec: argument spec
    :return: x, y
    """
    mcxt.logger.info("Window Object start ...")

    status = True
    message = ''
    location = None

    try:
        on_posix = 'posix' in sys.builtin_module_names
        proc = subprocess.Popen([argspec.web_app_driver],
                                stdout=subprocess.PIPE,
                                bufsize=1, close_fds=on_posix)

        desired_caps = dict()
        desired_caps["app"] = "Root"
        desired_caps["deviceName"] = "WindowsPC"

        driver = webdriver.Remote(
            command_executor=assemble_address(argspec.ip, argspec.port),
            desired_capabilities=desired_caps)

        el = driver.find_element_by_xpath(argspec.xpath)
        location = el.location
        proc.kill()
    except FileNotFoundError as e:
        status = False
        mcxt.logger.exception(str(e))
        message = 'Please check the app driver is installed or ' \
                  'it exist at the path.'
    except selenium.common.exceptions.WebDriverException as e:
        status = False
        mcxt.logger.exception(str(e))
        message = 'Wrong xpath you tried to use. please check the xpath.'
    except Exception as e:
        status = False
        mcxt.logger.exception(str(e))
        message = str(e)

    result = StructureLogFormat(RETURN_CODE=status,
                                RETURN_VALUE={'RESULT': location},
                                MESSAGE=message)
    std = {True: sys.stdout, False: sys.stderr}[status]
    std.write(str(result))

    mcxt.logger.info("Window Object end ...")
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
        # 'python -m alabs.pam.rpa.desktop.window_object ' \
        # web_app_driver 실행파일경로
        # xpath
        # return location of center

        # 필수 입력 항목
        mcxt.add_argument('web_app_driver', type=str, help='')
        mcxt.add_argument('xpath', type=str,  help='')
        mcxt.add_argument('--ip', type=str,
                          default='http://127.0.0.1', help='')
        mcxt.add_argument('--port', type=int, default=4723, help='')

        argspec = mcxt.parse_args(args)
        return window_object(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

