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
import enum
import json
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

SELECTED_BUTTON_VALUE = None

class ComparisonSign(enum.Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="


def safe_eval(value):
    env = dict()
    env["locals"] = None
    env["globals"] = None
    env["__name__"] = None
    env["__file__"] = None
    env["__builtins__"] = None
    return eval(value, env)


def compare_values(a:str, op, b:str):
    """
    비교함수 문자열은 반드시 json.dump를 사용할것
    :param a:
    :param op:
    :param b:
    :return:
    """
    a = int(a) if a.isdigit() else json.dumps(a)
    b = int(b) if b.isdigit() else json.dumps(b)
    if type(a) is not type(b):
        raise TypeError(
            'values must be same type each. {} is "{}" but {} is "{}".'.format(
                a, type(a).__name__, b, type(b).__name__))

    # 문자열 비교는 ==, != 지원
    string_allow_op = {ComparisonSign.EQUAL.value,
                       ComparisonSign.NOT_EQUAL.value}
    if type(a) is str and not {op} & string_allow_op:
        raise ValueError(
            "Operators '==' and '!=' are supported for string comparing")

    env = dict()
    env["locals"] = None
    env["globals"] = None
    env["__name__"] = None
    env["__file__"] = None
    env["__builtins__"] = None
    op = op.replace('"', '')
    try:
        result = safe_eval('{} {} {}'.format(a, op, b))
    except Exception as e:
        raise ValueError(
            'Something wrong with the statement, {} {} {} '.format(a, op, b))
    return result



################################################################################
def compare(mcxt, argspec):
    """
    plugin job function
    :param mcxt: module context
    :param argspec: argument spec
    :return: True
    """

    # 버튼 생성
    # mcxt.logger.info(str(argspec.compare))
    values = list()
    # from alabs.pam import ForkedPdb
    # ForkedPdb().set_trace()
    a, op, b =  argspec.compare_value
    try:
        values.append(str(compare_values(a, op, b)))
    except Exception as e:
        result = StructureLogFormat(RETURN_CODE=False, RETURN_VALUE=None,
                                    MESSAGE=str(e))
        mcxt.logger.error(result)
        sys.stderr.write(str(result))
        exit(-1)

    options = argspec.compare
    if options:
        for value in options:
            logical_op, a, op, b = value
            values.append(logical_op.lower())
            values.append(str(compare_values(a, op, b)))

    values = ' '.join(values)
    data = safe_eval(values)
    result = StructureLogFormat(RETURN_CODE=True, RETURN_VALUE=data, MESSAGE="")
    sys.stdout.write(str(result))
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
        help_msg = """
        'ABC' '==' 'DEF' 
        --compare 'AND' '1' '>' '0'
        --compare 'OR' '2' == '2'
        """
        mcxt.add_argument('-c', '--compare', action='append', nargs='+',
                          help=help_msg)

        ########################################################################
        mcxt.add_argument('compare_value',  nargs='+')
        argspec = mcxt.parse_args(args)
        return compare(mcxt, argspec)


################################################################################
def main(*args):
    return _main(*args)

