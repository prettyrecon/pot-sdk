"""
====================================
 :mod:mon_dir
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: VIVANS
"""

# 관련 작업자
# ===========
#
# 본 모듈은 다음과 같은 사람들이 관여했습니다:
#  * 채문창
#
# 작업일지
# --------
#
# 다음과 같은 작업 사항이 있었습니다:
#
#  * [2019/03/18]
#     - --outfile, --errfile을 모두 utf-8 인코딩 방식으로 열기
#  * [2019/03/13]
#     - get_pip_version 추가 및 plugin_version 추가
#  * [2019/03/07]
#     - 모듈 스펙에 icon 추가 방법
#     - dumpspec 시 icon.* 파일이 존재하면 첫번째 파일에 대하여 base64 형식 포함
#  * [2019/03/06]
#     - display_name 추가
#     - mod_spec에 action 추가 (클래스 이름에서 유추, _get_action_name)
#  * [2019/02/25]
#     - 입력 아규먼트에 input_group 속성 추가
#     - 입력 아규먼트에 input_method 속성 추가
#  * [2018/09/30]
#     - 본 모듈 작업 시작
################################################################################
import os
import re
import sys
import glob
import base64
import datetime
import traceback
import logging
import hashlib
from copy import copy
from json import dumps as json_dumps
from yaml import dump as yaml_dump
# noinspection PyProtectedMember
from functools import wraps
# noinspection PyProtectedMember
from argparse import ArgumentParser, _HelpAction
from io import StringIO
from alabs.common.util.vvlogger import get_logger
from pprint import pformat


################################################################################
class ArgsExit(Exception):
    pass


################################################################################
class ArgsError(Exception):
    pass


################################################################################
def get_file_hash(f):
    buf_size = 65536  # lets read stuff in 64kb chunks!
    sha256 = hashlib.sha256()
    if not os.path.exists(f):
        return 'unknown'
    with open(f, 'rb') as ifp:
        while True:
            data = ifp.read(buf_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


################################################################################
def get_icon_path(f):
    md = os.path.abspath(os.path.dirname(f))
    icon_f = None
    for f in glob.glob(os.path.join(md, 'icon.*')):
        icon_f = f
        break  # 첫번째 아이콘만 처리
    return icon_f


################################################################################
def func_log(original_function):
    @wraps(original_function)
    # ==========================================================================
    def new_function(mcxt, argspec, *args, **kwargs):
        """ new_function for decorator """
        _s_ts_ = datetime.datetime.now()
        try:
            mcxt.logger.debug('%s\n(%s,%s,%s)\nStarting...' %
                              (original_function.__name__, argspec,
                               args, kwargs))
            r = original_function(mcxt, argspec, *args, **kwargs)
            mcxt.logger.debug('%s\n(%s,%s,%s)\nReturn:%s' %
                              (original_function.__name__, argspec,
                               args, kwargs, r))
            return r
        except Exception as exp:
            # mcxt.logger.error('%s\n(%s,%s,%s)\nError:%s' %
            #                   (original_function.__name__, argspec,
            #                    args, kwargs, str(exp)))
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            mcxt.logger.error("'%s\n(%s,%s,%s)\nError %s\nError Stack: %s" %
                              (original_function.__name__, argspec,
                               args, kwargs, str(exp), ''.join(_out)))
            raise  # current exception
        finally:
            _e_ts_ = datetime.datetime.now()
            mcxt.logger.debug('%s\n(%s,%s,%s)\nTakes:%s' %
                              (original_function.__name__, argspec,
                               args, kwargs, (_e_ts_ - _s_ts_)))
    # ==========================================================================
    # enherit from original_function
    return new_function


################################################################################
def re_match(s, p):
    m = re.match(p, s)
    return m is not None


################################################################################
class ModuleContext(ArgumentParser):
    # ==========================================================================
    PLATFORMS = ("windows", "darwin", "linux")
    OUTPUT_TYPES = ("text", "json", "csv")
    VALID_RE1 = re.compile(r"^[a-zA-Z0-9_\-.]+")

    # 각 패러미터에 대한 부가 속성 : 주로 사용자 입력 UI 관련
    ETC_ATTRS = {
        # 1) 해당 패러미터의 입력 그룹 (디폴트는 None)
        'input_group': None,
        # 2) 해당 패러미터의 특정 UI 입력 방법 (디폴트는 None)
        # 2.1) "password" : Stu에서 암호표시
        # 2.2) "fileread" : Stu에서 읽을 파일을 지정
        # 2.3) "filewrite" : Stu에서 쓸 파일을 지정
        'input_method': None,
    }
    # argparse 에 더붙이는 자체 검증 모듈
    EXTENDED_ATTRS = {
        # 사용자 입력 검증
        # 패러미터속성이름 : 람다함수
        #   람다 함수 : av(사용자 입력값), cv(설정값)
        # 1) 사용자가 입력한 값이 설정 값보다 같거나 크면 정상
        'min_value': lambda av, cv: av >= cv,
        # 2) 사용자가 입력한 값이 설정 값보다 같거나 작으면 정상
        'max_value': lambda av, cv: av <= cv,
        # 3) 사용자가 입력한 값이 설정 값보다 크면 정상
        'min_value_ni': lambda av, cv: av > cv,
        # 4) 사용자가 입력한 값이 설정 값보다 작으면 정상
        'max_value_ni': lambda av, cv: av < cv,
        # 5) 사용자가 입력한 값이 설정 값보다 크면 정상: min_value_ni 와 동일
        'greater': lambda av, cv: av > cv,
        # 6) 사용자가 입력한 값이 설정 값보다 같거나 크면 정상: min_value 와 동일
        'greater_eq': lambda av, cv: av >= cv,
        # 7) 사용자가 입력한 값이 설정 값보다 작으면 정상: max_value_ni 와 동일
        'less': lambda av, cv: av < cv,
        # 8) 사용자가 입력한 값이 설정 값보다 같거나 작으면 정상: max_value 와 동일
        'less_eq': lambda av, cv: av <= cv,
        # 9) 사용자가 입력한 값이 설정 값과 같으면 정상
        'equal': lambda av, cv: av == cv,
        # 10) 사용자가 입력한 값이 설정 값과 같지 않으면 정상
        'not_equal': lambda av, cv: av != cv,
        # 11) 사용자가 입력한 값이 설정 정규식을 만족하면 정상
        're_match': re_match,
    }

    # ==========================================================================
    def _valid_literal(self, s, raise_empty_exception=True):
        if raise_empty_exception and not s:
            raise ValueError('Invalid literal "%s"' % s)
        return self.VALID_RE1.sub('_', s)

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _valid_choice(self, s, choices, raise_exception=True):
        if not isinstance(s, (tuple, list)):
            s = [s]
        for _s in s:
            if raise_exception and _s.lower() not in choices:
                raise ValueError('Invalid choice "%s" not in %s'
                                 % (_s, choices))
            if _s.lower() not in choices:
                return False
        return list(s)

    # ==========================================================================
    def __init__(self,
                 owner=None,
                 group=None,
                 version=None,
                 platform=None,
                 output_type=None,
                 display_name=None,
                 icon_path=None,
                 *args, **kwargs):
        """
        ModuleContext consturctor
        :param owner: owner name (only allowed "[a-zA-Z0-9_-.]+")
        :param group: group name (only allowed "[a-zA-Z0-9_-.]+")
        :param version: version name (only allowed "[a-zA-Z0-9_-.]+")
        :param platform: list of words ["windows", "darwin", "linux"]
            which will be supported
        :param output_type: one of these ["text", "json", "csv"]
        :param display_name: display name for Stu
        :param args:
        :param kwargs:
        """
        self.owner = self._valid_literal(owner)
        self.group = self._valid_literal(group)
        self.version = self._valid_literal(version)
        self.platform = self._valid_choice(platform, self.PLATFORMS)
        self.output_type = self._valid_choice(output_type, self.OUTPUT_TYPES)
        self.display_name = display_name
        self.icon_path = icon_path
        kwargs['add_help'] = False
        ArgumentParser.__init__(self, *args, **kwargs)
        self._add_common_args()
        self._args = None
        self._isopened = False
        self._org_stdout = sys.stdout
        self._org_stdin = sys.stdin
        self._org_stderr = sys.stderr
        self._stdout = None
        self._stdin = None
        self._stdout = None
        self._loglevel = logging.INFO
        self.logger = None
        self._verbose = 0
        self._raise_args_error = False
        self._args_error = None
        self._ext_argspec = {}
        self._etc_argspec = {}

    # ==========================================================================
    def __repr__(self):
        _d = {
            'owner': self.owner,
            'group': self.group,
            'prog': self.prog,
            'version': self.version,
            'description': self.description,
            'platform': self.platform,
            'output_type': self.output_type,
            'display_name': self.display_name,
            'icon_path': self.icon_path,
            'args': self._args,
            'isopened': self._isopened,
        }
        return 'ModuleContext=%s' % pformat(_d)

    # ==========================================================================
    def add_argument(self, *args, **kwargs):
        ext_kwargs = {}
        for ea in self.EXTENDED_ATTRS.keys():
            if ea in kwargs:
                ext_kwargs[ea] = kwargs[ea]
                del kwargs[ea]
        etc_kwargs = copy(self.ETC_ATTRS)
        for ea in self.ETC_ATTRS.keys():
            if ea in kwargs:
                etc_kwargs[ea] = kwargs[ea]
                del kwargs[ea]
        action = ArgumentParser.add_argument(self, *args, **kwargs)
        self._ext_argspec[action.dest] = ext_kwargs
        self._etc_argspec[action.dest] = etc_kwargs
        return action

    # ==========================================================================
    def _add_common_args(self):
        argc = self.add_argument_group('common options for all modules')
        argc.add_argument('--help', '-h', nargs='?', type=bool,
                          const=True, default=False,
                          help='Print usage')
        argc.add_argument('--infile', nargs='?', const='-',
                          help='for input stream file '
                               '(default is nothing, "-" means stdin)')
        argc.add_argument('--outfile', nargs='?',
                          help='for output stream file (default is stdout)')
        argc.add_argument('--errfile', nargs='?',
                          help='for error stream file (default is stderr)')
        argc.add_argument('--statfile', nargs='?',
                          help='for status (default is stdout)')
        argc.add_argument('--logfile', nargs='?',
                          help='for log file to logging, default is %s.log '
                               '(500K size, rotate 4)' % self.prog)
        argc.add_argument('--loglevel', nargs='?',
                          choices=['debug', 'info', 'warning',
                                   'error', 'critical'],
                          help='loglevel for logfile (default is "info")')
        argc.add_argument('--verbose', '-v', default=0, action='count',
                          help='verbose logging (-v, -vv, -vvv ... '
                               'more detail log)')
        argc.add_argument('--dumpspec', nargs='?', choices=['json', 'yaml'],
                          const='json', default=None,
                          help='dump arguments spec as json or yaml format')
        # argc.add_argument('--unittest', nargs='?', type=bool,
        #                   const=True, default=False,
        #                   help='unittest for this module')

    # ==========================================================================
    @staticmethod
    def _get_action_name(a):
        r = type(a).__name__.lower()
        if r.startswith('argparse.'):
            r = r[9:]
        if r.startswith('_'):
            r = r[1:]
        if r.endswith('action'):
            r = r[:-6]
        return r

    # ==========================================================================
    @staticmethod
    def _get_icon(icon_path):
        if not (icon_path
                and os.path.exists(icon_path)):
            return None
        with open(icon_path, 'rb') as ifp:
            rb = ifp.read()
        icon = base64.b64encode(rb)
        return icon.decode('ascii')

    # ==========================================================================
    def _module_spec(self):
        common_names = (
            'help', 'infile', 'outfile', 'errfile', 'statfile', 'logfile',
            'loglevel', 'verbose', 'dumpspec'
        )
        mod_spec = {
            # module accessed owner/name/
            'owner': self.owner,  # module owner
            'group': self.group,  # group name
            'name': self.prog,
            'plugin_version': get_pip_version(self.prog),
            'version': self.version,  # module version
            'sha256': get_file_hash(self.prog),
            'type': 'embeded-exe',
            'platform': self.platform,
            'description': self.description,
            'options': [],
            'parameters': [],
            'mutually_exclusive_group': [],
            'output_type': self.output_type,
            'display_name': self.display_name if self.display_name else self.prog,
            'icon_path': self.icon_path,
            'icon': self._get_icon(self.icon_path)
        }
        for a in self._actions:
            if isinstance(a, _HelpAction):
                continue
            # print('%s:required=%s' % (a, a.required))
            action_spec = {
                'name': a.dest,
                'nargs': a.nargs,
                'const': a.const,
                'default': a.default,
                'type': 'str' if a.type is None else str(a.type.__name__),
                'choices': a.choices,
                'title': a.dest,  # title for label
                'help': a.help,
                'required': a.required,
                'value': a.default,
                'option_strings': a.option_strings,
                'placeholder': None,  # background placeholder for text input
                'is_visible': False if a.dest in common_names else True,
                'action': self._get_action_name(a)
            }
            if a.dest in self._ext_argspec:
                for ea, ev in self._ext_argspec[a.dest].items():
                    action_spec[ea] = ev
            if a.dest in self._etc_argspec:
                for ea, ev in self._etc_argspec[a.dest].items():
                    action_spec[ea] = ev
            if a.option_strings:
                mod_spec['options'].append(action_spec)
            else:
                mod_spec['parameters'].append(action_spec)
        # print("_mutually_exclusive_groups")
        for mg in self._mutually_exclusive_groups:
            # print('mutually_exclusive_group=%s' % mg)
            meg_spec = {
                'required': mg.required,
                'options': [],
                'parameters': [],
            }
            # noinspection PyProtectedMember
            for ma in mg._group_actions:
                # print(ma)
                if ma.option_strings:
                    meg_spec['options'].append(ma.dest)
                else:
                    meg_spec['parameters'].append(ma.dest)
            mod_spec['mutually_exclusive_group'].append(meg_spec)

        return mod_spec

    # ==========================================================================
    def get_json_spec(self):
        sd = self._module_spec()
        return json_dumps(sd)

    # ==========================================================================
    def get_yaml_spec(self):
        sd = self._module_spec()
        sop = StringIO()
        yaml_dump(sd, sop)
        return sop.getvalue()

    # ==========================================================================
    @staticmethod
    def pformat_args(args):
        pfd = {}
        for att in dir(args):
            if att.startswith('_'):
                continue
            pfd[att] = getattr(args, att)
        return pformat(pfd)

    # ==========================================================================
    def parse_args(self, args=None, namespace=None):
        if args is not None and not args:
            args = None
        elif isinstance(args, (list, tuple)):
            args = list(map(str, args))
        # 에러 없이 돌리고
        self._raise_args_error = False
        self._args_error = None
        try:
            self._args = ArgumentParser.parse_args(self, args, namespace)
        except Exception as _:
            raise ArgsError('%s' % self._args_error)
        self._open()
        self._raise_args_error = True
        # 에러 활성화하여 돌리고
        self._args = ArgumentParser.parse_args(self, args, namespace)
        # EXTENDED_ATTRS 에 대한 검증
        for dest, ext_args in self._ext_argspec.items():
            av = getattr(self._args, dest, None)
            if av is None:
                continue
            for ext_att, cv in ext_args.items():
                # None은 비교대상이 아님
                if cv is None:
                    continue
                if not isinstance(av, list):
                    av = [av]
                for iav in av:
                    if not isinstance(iav, type(cv)):
                        raise ValueError('%s must be type(%s) for %s'
                                         % (cv, type(iav).__name__, dest))
                    if not self.EXTENDED_ATTRS[ext_att](iav, cv):
                        raise ArgsError('For Argument "%s", "%s" validatation '
                                        'error: user input is "%s" but rule is '
                                        '"%s"' % (dest, ext_att, iav, cv))
        self.logger.info("args=%s: opened" % self.pformat_args(self._args))
        return self._args

    # ==========================================================================
    def error(self, message):
        # exc = sys.exc_info()[1]
        # if exc:
        #     exc.argument = self._get_action_from_name(exc.argument_name)
        #     raise exc
        self._args_error = message
        if self._raise_args_error:
            raise ArgsError(message)

    # ==========================================================================
    def exit(self, status=0, message=None):
        if message:
            # self._print_message(message, sys.stderr)
            sys.stderr.write(message)

    # ==========================================================================
    def _get_loglevel(self):
        # 만약 verbose 가 하나 이상 설정 되었다면 DEBUG 로그레벨로
        if self._args.loglevel == 'debug' or self._args.verbose > 0:
            self._loglevel = logging.DEBUG
        elif self._args.loglevel == 'info':
            self._loglevel = logging.INFO
        elif self._args.loglevel == 'warning':
            self._loglevel = logging.WARNING
        elif self._args.loglevel == 'error':
            self._loglevel = logging.ERROR
        elif self._args.loglevel == 'critical':
            self._loglevel = logging.CRITICAL

    # ==========================================================================
    def _open(self):
        if self._args.infile:
            if self._args.infile == '-':
                self._stdin = sys.stdin
            else:
                if not os.path.exists(self._args.infile):
                    raise IOError('Cannot find infile "%s" for input stream' 
                                  % self._args.infile)
                self._stdin = open(self._args.infile, 'r')
                sys.stdin = self._stdin
        if self._args.outfile:
            self._stdout = open(self._args.outfile, 'w', encoding='utf-8')
            sys.stdout = self._stdout
        else:
            self._stdout = sys.stdout
        if self._args.errfile:
            self._stderr = open(self._args.errfile, 'w', encoding='utf-8')
            sys.stderr = self._stderr
        else:
            self._stderr = sys.stderr
        self._get_loglevel()
        if not self._args.logfile:
            self._args.logfile = '%s.log' % self.prog
        self.logger = get_logger(self._args.logfile, loglevel=self._loglevel)
        if self._args.verbose > 0:
            self._verbose = self._args.verbose

        # 아래의 옵션은 특정 명령을 수행하고 ArgsExit 예외 발생
        self._isopened = True  # 이미 open되었음
        if self._args.help:
            self.print_help()
            raise ArgsExit('print help message')
        if self._args.dumpspec == 'json':
            ss = self.get_json_spec()
            self._stdout.write('%s' % ss)
            raise ArgsExit('generate json module spec')
        elif self._args.dumpspec == 'yaml':
            ss = self.get_yaml_spec()
            # noinspection PyTypeChecker
            self._stdout.write('%s' % ss)
            raise ArgsExit('generate yaml module spec')
        # if self._args.unittest:
        #     suite = unittest.TestLoader().
        # loadTestsFromTestCase(self.test_class)
        #     result = unittest.TextTestRunner(verbosity=2).run(suite)
        #     ret = not result.wasSuccessful()
        #     raise ArgsExit('unittest running: result is %s' % ret)

        self._isopened = True
        return self._isopened

    # ==========================================================================
    def _close(self):
        if self._isopened:
            if self._stdin is not None and self._stdin != self._org_stdin \
                    and self._stdin.fileno() > 2:
                self._stdin.close()
            if self._stdout is not None and self._stdout != self._org_stdout \
                    and self._stdout.fileno() > 2:
                self._stdout.close()
            if self._stderr is not None and self._stderr != self._org_stderr \
                    and self._stderr.fileno() > 2:
                self._stderr.close()
            sys.stdin = self._org_stdin
            sys.stdout = self._org_stdout
            sys.stderr = self._org_stderr
            self._ext_argspec = {}
            self._isopened = False
            # close logger's handlers
            if self.logger is not None and self.logger.handlers is not None \
                    and len(self.logger.handlers) >= 0:
                for handler in self.logger.handlers:
                    handler.close()
                    self.logger.removeHandler(handler)
                self.logger.handlers = []

        return not self._isopened

    # ==========================================================================
    def __del__(self):
        self._close()

    # ==========================================================================
    def __enter__(self):
        return self

    # ==========================================================================
    # noinspection PyShadowingBuiltins,PyShadowingNames
    def __exit__(self, type, value, traceback):
        self._close()
        return False

    # ==========================================================================
    def add_status(self, step, total_step, percent, message, separator=':'):
        """
        현재 step의 상태 출력
        :param step: 1-based step 정수 값
        :param total_step: 전체 step 개수
        :param percent: 현재 step의 퍼센트 진행률
        :param message: 출력할 메시지 (한줄로 처리)
        :param separator: 구분자, 디폴트는 ':'
        :return: True/False, 옵션에 --statfile 을 지정했으면 해당 파일에 append
            하고 True 아니면 False
            ':' 콜론 구분자로 출력
        """
        if not self._args.statfile:
            return False
        with open(self._args.statfile, 'a') as ofp:
            message = message.replace('\n', ' ').replace(separator, ' ')
            ofp.write('%s\n' %
                      separator.join(map(str,
                                         (step, total_step, percent, message))))
        return True


################################################################################
def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgsError('Boolean value expected but "%s"' % v)


################################################################################
# noinspection PyProtectedMember,PyUnresolvedReferences,PyUnresolvedReferences
def get_all_pip_version():
    try:
        from pip._internal.operations import freeze
    except ImportError:  # pip < 10.0
        from pip.operations import freeze

    x = freeze.freeze()
    rd = {}
    for p in x:
        # print(p)
        eles = p.split('==')
        rd[eles[0]] = eles[1]
    return rd


################################################################################
def get_pip_version(modname):
    _d = get_all_pip_version()
    if modname not in _d:
        return None
    return _d[modname]


################################################################################
if __name__ == '__main__':
    d = get_all_pip_version()
    print(d)
    print(get_pip_version('alabs.common'))
