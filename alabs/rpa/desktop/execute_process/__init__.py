#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.la.bot2py
====================================
.. moduleauthor:: Duk Kyu Lim <deokyu@argos-labs.com>
.. note:: ARGOS-LABS License

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

from subprocess import Popen, PIPE

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

import os

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
    proc = Popen('{}'.format(argspec.command), shell=True, stdout=PIPE)
    # ret = proc.stdout.read()
    # mcxt.logger.info(ret)
    ret = {'PID': proc.pid, 'PROC': proc, 'NAME': argspec.command.split()[0]}
    mcxt.logger.info('>>>end...')
    return ret[argspec.ret]


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

(참조: https://docs.python.org/ko/3.7/library/argparse.html)
사용자 입력에 필요한 spec은 다음과 같이 add_argument 함수 호출로 가능
    mcxt.add_argument(name or flags...[, action][, nargs][, const][, default]
        [, type][, choices][, required][, help][, metavar][, dest])
    단일 명령행 인자를 구문 분석하는 방법을 정의합니다.
    매개 변수마다 아래에서 더 자세히 설명되지만, 요약하면 다음과 같습니다:

    name or flags - 옵션 문자열의 이름이나 리스트, 예를 들어 foo 또는 -f, --foo.
        '-m', '--myarg' 와 같이 '-'로 시작하면 옵션 아니면 패러미터

    action - 명령행에서 이 인자가 발견될 때 수행 할 액션의 기본형
        'store' - 인자 값을 저장합니다. 이것이 기본 액션
        'append' - 리스트를 저장하고 각 인자 값을 리스트에 추가합니다
            옵션을 여러 번 지정할 수 있도록 하는 데 유용합니다
        'count' - 키워드 인자가 등장한 횟수를 계산합니다. 예를 들어,
            상세도를 높이는 데 유용합니다
        'store_true' 와 'store_false' - 각각 True 와 False 값을 저장하는
            'store_const' 의 특별한 경우입니다. 또한, 각각 기본값 False 와
            True 를 생성합니다

    nargs - 소비되어야 하는 명령행 인자의 수. 또는 다음과 같은 의미의 문자,
        N (정수). 명령행에서 N 개의 인자를 함께 모아서 리스트에 넣습니다.
        '?'. 가능하다면 한 인자가 명령행에서 소비되고 단일 항목으로 생성됩니다.
            명령행 인자가 없으면 default 의 값이 생성됩니다. 선택 인자의 경우
            추가적인 경우가 있습니다 - 옵션 문자열은 있지만, 명령행 인자가
            따라붙지 않는 경우입니다. 이 경우 const 의 값이 생성됩니다.
        '*'. 모든 명령행 인자를 리스트로 수집합니다. 일반적으로 두 개 이상의
            위치 인자에 대해 nargs='*' 를 사용하는 것은 별로 의미가 없지만,
            nargs='*' 를 갖는 여러 개의 선택 인자는 가능합니다
        '+'. '*' 와 같이, 존재하는 모든 명령행 인자를 리스트로 모읍니다.
            또한, 적어도 하나의 명령행 인자가 제공되지 않으면 에러 메시지가
            만들어집니다

    const - nargs='?' 를 주고 해당 값이 생략될 때 필요한 상숫값.

    default - 인자가 명령행에 없는 경우 생성되는 값.

    type - 명령행 인자가 변환되어야 할 형. (또는 str2bool 와 같은 함수)
        str - 문자열 (디폴트)
        int - 정수형
        float - 실수형
        str2bool - True/False, Yes/No 등의 문자열에서 판별
            'yes', 'true', 't', 'y', '1' 이면 True
            'no', 'false', 'f', 'n', '0' 이면 False
            둘다 아니면 예외 발생

    choices - 인자로 허용되는 값의 컨테이너.

    required - 명령행 옵션을 생략 할 수 있는지 아닌지 (선택적일 때만).

    help - 인자가 하는 일에 대한 간단한 설명.

    metavar - 사용 메시지에 사용되는 인자의 이름.

    dest - parse_args() 가 반환하는 argspec 객체에 추가될 어트리뷰트의 이름.

    min_value | greater_eq - 사용자가 입력한 값이 설정 값보다 같거나 크면 정상

    max_value | less_eq - 사용자가 입력한 값이 설정 값보다 같거나 작으면 정상

    min_value_ni | greater - 사용자가 입력한 값이 설정 값보다 크면 정상

    max_value_ni | less - 사용자가 입력한 값이 설정 값보다 작으면 정상

    equal - 사용자가 입력한 값이 설정 값과 같으면 정상

    not_equal - 사용자가 입력한 값이 설정 값과 같지 않으면 정상

    re_match - 사용자가 입력한 값이 설정 정규식을 만족하면 정상
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
        mcxt.add_argument('command', help='Command to execute')
        mcxt.add_argument('--ret', choices=['PROC', 'PID', 'NAME'], type=str,
                          default='PID',
                          help='Command to execute')

        argspec = mcxt.parse_args(args)
        return execute_process(mcxt, argspec)

################################################################################
def main(*args):
    return _main(*args)

