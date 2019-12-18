"""
====================================
 :mod:alabs.ppm ARGOS-LABS Plugin Module Manager
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
#  * [2019/12/12]
#   - --on-premise 별도 옵션 추가
#  * [2019/12/11]
#   - on-premise에서 인터넷 연결 시 문제 수정
#  * [2019/12/06]
#   - on-premise에 적응하도록 수정 (도메인의 호스트 명에 -hcl 붙인 것들 확인)
#   - 정확히 일치하는 버전의 플러그인 없으면 최신 버전을 설치하도록 수정
#  * [2019/12/04]
#   - offline 저장소를 만들려다 보니 argoslabs.* 만 플러그인으로 가져오도록 함 _list_modules
#  * [2019/09/03]
#   - argos-pbtail.exe 상태 표시창 추가 (win32)
#  * [2019/08/28]
#   - STU & PAM에서 사용할 기본 상태파일 마련 : HOME/.argos-rpa.sta
#  * [2019/08/26]
#   - ppm exe로 만들어 테스트 하기: for STU & PAM
#  * [2019/08/08]
#   - argoslabs.time.workanlendar 같은 경우 ephem 모듈은 C컴파일러가 필요하므로
#     prebuilt 버전이 필요함. 이에 따라 로컬에 가져온 다음 필요에 따라
#     requirements.txt를 미리 설치하도록 함
#  * [2019/08/06]
#   - PAM 이 맥주소를 넘길 수 있도록 --pam-id 추가
#  * [2019/07/29]
#   - upload 시 user 및 암호 받아오기
#  * [2019/07/27]
#   - --self-upgrade 체크 속도 개선
#  * [2019/07/25]
#   - POT 속도개선 작업
#  * [2019/06/25]
#   - venv의 Popen 결과를 Thread, Queue로 해결
#  * [2019/06/20]
#   - venv의 Popen 결과를 line by line 으로 가져와서 처리
#  * [2019/05/28]
#   - ppm self upgrade on startup (--self-upgrade option)
#   - TODO : pip2pi 모듈로 로컬용 pi를 만들고 로컬에서 설치하는 것 테스트
#   - dumppi 명령 추가 (--dumppi-folder 옵션)
#  * [2019/05/27]
#   - submit 별도 구축 및 테스트
#   - 설정에 버전 넣고 지정
#   - plugin versions 명령은 해당 플러그인 들만 가져오도록 수정해야함
#   - pypiuploader를 이용하여 https용 pypiserver에 업로드
#  * [2019/05/17]
#   - python 3.6.3 에서 setuptools 를 최신 것으로 update 해야하는 상황 발생
#  * [2019/05/2?]
#   - python 3.6.3 에서 setuptools 를 최신 것으로 update 해야하는 상황 발생
#  * [2019/05/04]
#   - 특정 plugin의 버전목록 구하기 기능 추가
#  * [2019/05/01]
#   - 사용자 별 dumpspec 기능 추가
#  * [2019/04/29]
#   - plugin venv command 추가
#   - plugin command 에서 버전 목록을 가장 최신 버전부터 소팅
#  * [2019/04/24]
#   - plugin commands 추가
#  * [2019/04/22]
#   - dumpspec.json 을 alabs.ppm build 에서 wheel을 만들기 전에 포함되도록
#   - 이후 해당 dumpspec을 가져오는 것은
#     pip download argoslabs.terminal.sshexp --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com --dest=C:\tmp\pkg --no-deps
#     pip download argoslabs.demo.helloworld==1.327.1731 --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com --dest=C:\tmp\pkg --no-deps
#     위의 명령어로 해당 패키지만 다운받아 unzip 하여 dumpspec.json 을 추출하여 특정 dumpspec.json 뽑도록
#  * [2019/04/03]
#   - check empty 'private-repositories'
#  * [2019/03/27]
#   - search 에서는 --extra-index-url 등이 지원 안되는 문제
#  * [2019/03/22~2019/03/26]
#   - PPM.do 에서 return 값을 실제 프로세스 returncode를 리턴 0-정상
#   - submit 에서 upload 서버로 올림
#  * [2019/03/20]
#   - .argos-rpa.conf 애 private-repositories 목록 추가
#   - 기존 register => submit 변경
#  * [2019/03/06]
#   - dumpspec 추가
#  * [2019/03/05]
#   - add package_data
#  * [2018/11/28]
#   - Linux 테스트 OK
#  * [2018/11/27]
#   - 윈도우 테스트 OK
#  * [2018/10/31]
#   - 본 모듈 작업 시작
################################################################################
import os
import sys
import ssl
# noinspection PyPackageRequirements
import yaml
import glob
import copy
import json
import time
# noinspection PyUnresolvedReferences
import venv       # for making venv in pyinstaller
import shutil
# noinspection PyPackageRequirements
import chardet
import logging
import zipfile
# noinspection PyPackageRequirements
import requests
import argparse
import datetime
import tempfile
import traceback
import subprocess
import requirements
import pkg_resources
# noinspection PyPackageRequirements
import urllib3
import urllib.request
import urllib.parse
# noinspection PyUnresolvedReferences
import setuptools
# noinspection PyUnresolvedReferences,PyPackageRequirements,PyProtectedMember
# from pip._internal import main as pipmain
# from random import randint
from threading import Thread
from queue import Queue, Empty
# noinspection PyPackageRequirements
from bs4 import BeautifulSoup
from alabs.common.util.vvjson import get_xpath
from alabs.common.util.vvlogger import get_logger
from alabs.common.util.vvupdown import SimpleDownUpload
from alabs.common.util.vvnet import is_svc_opeded
from alabs.ppm.pypiuploader.commands import main as pu_main
from functools import cmp_to_key
from getpass import getpass
from pathlib import Path
from contextlib import closing
# from tempfile import gettempdir
if '%s.%s' % (sys.version_info.major, sys.version_info.minor) < '3.3':
    raise EnvironmentError('Python Version must greater then "3.3" '
                           'which support venv')
else:
    from urllib.parse import urlparse, quote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


################################################################################
CONF_NAME = '.argos-rpa.conf'
CONF_PATH = os.path.join(str(Path.home()), CONF_NAME)
LOG_NAME = '.argos-rpa.log'
LOG_PATH = os.path.join(str(Path.home()), LOG_NAME)
OUT_NAME = '.argos-rpa.out'
OUT_PATH = os.path.join(str(Path.home()), OUT_NAME)
ERR_NAME = '.argos-rpa.err'
ERR_PATH = os.path.join(str(Path.home()), ERR_NAME)
pbtail_po = None


################################################################################
__all__ = ['main']

_conf_version_list = [
    '1.1'
]
_conf_last_version = _conf_version_list[-1]
_conf_contents_dict = {
    _conf_last_version: """
---
version: "{last_version}"

repository:
  url: https://pypi-official.argos-labs.com/pypi
  req: https://pypi-req.argos-labs.com
private-repositories:
""".format(last_version=_conf_last_version)
    # - name: pypi-test
    #  url: https://pypi-test.argos-labs.com/simple
    #  username: user
    #  password: pass
}
_conf_last_contents = _conf_contents_dict[_conf_last_version]

g_path = os.environ['PATH']


################################################################################
class StatLogger(object):
    # ==========================================================================
    STA_NAME = '.argos-rpa.sta'
    STA_PATH = os.path.join(str(Path.home()), STA_NAME)
    ERR_NAME = '.argos-rpa.err'
    ERR_PATH = os.path.join(str(Path.home()), ERR_NAME)
    # ==========================================================================
    LT_1 = 1
    LT_2 = 2
    LT_3 = 3

    # ==========================================================================
    def clear(self):
        for f in glob.glob(self.STA_PATH):
            os.remove(f)
        for f in glob.glob('%s.*' % self.STA_PATH):
            os.remove(f)
        if os.path.exists(self.ERR_PATH):
            os.remove(self.ERR_PATH)

    # ==========================================================================
    def __init__(self, is_clear=False):
        if is_clear:
            self.clear()

    # ==========================================================================
    def __add__(self, other):
        self.log(*other)

    # ==========================================================================
    def log(self, level, msg, is_append=True):
        with open(self.STA_PATH, 'a', encoding='utf-8') as ofp:
            ofp.write('[%s:%s] %s\n' %
                      (datetime.datetime.now().strftime('%Y%m%d %H%M%S'), level, msg))
            ofp.flush()
        om = 'a' if is_append else 'w'
        if level <= 0:
            level = 1
        elif level > 3:
            level = 3
        with open('%s.%s' % (self.STA_PATH, level), om, encoding='utf-8') as ofp:
            ofp.write('%s\n' % msg)
            ofp.flush()

    # ==========================================================================
    def error(self, msg):
        with open(self.STA_PATH, 'a', encoding='utf-8') as ofp:
            ofp.write('[%s:E] %s\n' %
                      (datetime.datetime.now().strftime('%Y%m%d %H%M%S'), msg))
            ofp.flush()
        with open(self.ERR_PATH, 'a', encoding='utf-8') as ofp:
            ofp.write('[%s] %s\n' %
                      (datetime.datetime.now().strftime('%Y%m%d %H%M%S'), msg))
            ofp.flush()


################################################################################
def ver_compare(a, b):
    a_eles = a.split('.')
    b_eles = b.split('.')
    max_len = max(len(a_eles), len(b_eles))
    for i in range(max_len):
        if i >= len(a_eles):    # a='1.2', b='1.2.3' 인 경우 a < b
            return -1
        elif i >= len(b_eles):  # a='1.2.3', b='1.2' 인 경우 a > b
            return 1
        if int(a_eles[i]) > int(b_eles[i]):
            return 1
        elif int(a_eles[i]) < int(b_eles[i]):
            return -1
    return 0


################################################################################
def version_compare(a, b):
    return ver_compare(a['version'], b['version'])


################################################################################
def plugin_version_compare(a, b):
    return ver_compare(a['plugin_version'], b['plugin_version'])


################################################################################
class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
            raise RuntimeWarning('ArgumentParser Exit: %s', message)
        # else:
        #     raise RuntimeWarning('ArgumentParser Exit')


################################################################################
def set_venv(g_dir):
    os.environ['VIRTUAL_ENV'] = g_dir
    os.environ['PATH'] = os.path.join(g_dir, r'Scripts') + ';' + g_path
    # sys.stderr.write('setuptools.__file__=%s\n' % setuptools.__file__)
    # sys.stderr.write('sys.path=%s\n' % sys.path)
    # sys.stderr.write('os.environ["PATH"]=%s\n' % os.environ['PATH'])
    os.environ['PYTHONPATH'] = g_dir + r'\Lib\site-packages'
    pw = os.path.join(g_dir, r'Scripts\python.exe')
    sys.executable = pw
    sys.path = [
        g_dir,
        g_dir + '\\lib\\site-packages',
        g_dir + '\\lib\\site-packages\\win32',
        g_dir + '\\lib\\site-packages\\win32\\lib',
        g_dir + '\\lib\\site-packages\\Pythonwin',
    ]
    return True


################################################################################
# noinspection PyProtectedMember
class VEnv(object):
    # ==========================================================================
    def __init__(self, args, root='py.%s' % sys.platform, logger=None):
        self.args = args
        # home 폴더 아래에 py.win32, py.darwin, py.linux 처럼 만듦
        if os.path.basename(root) == root:  # basename만 왔을 경우 ~/ HOME 아래에
            self.root = os.path.join(str(Path.home()), root)
        else:
            self.root = root
        self.use = args.venv
        if logger is None:
            logger = get_logger(LOG_PATH)
        self.logger = logger
        # for internal
        self.py = None
        self.check_environments()
        self.sta = StatLogger()

    # ==========================================================================
    def check_python(self):
        pyver = '%s.%s' % (sys.version_info.major, sys.version_info.minor)
        if pyver < '3.3':
            msg = 'Python Version must greater then "3.3" but "%s"' % pyver
            self.logger.error(msg)
            raise EnvironmentError(msg)
        self.logger.debug('VEnv.check_python: python version is "%s"' % pyver)
        return 0

    # ==========================================================================
    def check_environments(self):
        self.check_python()

    # ==========================================================================
    def clear(self):
        if os.path.isdir(self.root):
            shutil.rmtree(self.root)
        self.logger.debug('VEnv.clear: "%s" is removed' % self.root)
        return 0

    # ==========================================================================
    def _upgrade(self, ndx_param=None, is_common=True, is_ppm=True):
        if not any((is_common, is_ppm)):
            return 9
        rl = list()
        rl.append(self.venv_pip('install', '--upgrade', 'pip'))
        rl.append(self.venv_pip('install', '--upgrade', 'setuptools'))
        if not ndx_param:
            ndx_param = list()
        if is_common:
            rl.append(self.venv_pip('install', '--upgrade', 'alabs.common', *ndx_param))
        if is_ppm:
            rl.append(self.venv_pip('install', '--upgrade', 'alabs.ppm', *ndx_param))
        return 1 if any(rl) else 0

    # ==========================================================================
    # noinspection PyUnresolvedReferences
    def make_venv(self, isdelete=True):
        if not self.use:
            return 9
        if os.path.isdir(self.root) and isdelete:
            shutil.rmtree(self.root)

        self.logger.info("Now making venv %s ..." % self.root)
        if getattr(sys, 'frozen', False):
            shutil.copytree(os.path.join(os.path.abspath(sys._MEIPASS), 'venv'), self.root)
            set_venv(self.root)
            return 0
        cmd = [
            '"%s"' % os.path.abspath(sys.executable),
            '-m',
            'venv',
            '"%s"' % self.root  # 아래의 shell=True 때문에 ""를 주었음
        ]
        self.logger.info("venv: cmd='%s'" % ' '.join(cmd))
        # python -m venv ... 명령은 shell 에서 해야 정상 동작함
        with open(OUT_PATH, 'w', encoding='utf-8') as out_fp, \
                open(ERR_PATH, 'w', encoding='utf-8') as err_fp:
            po = subprocess.Popen(' '.join(cmd), shell=True,
                                  stdout=out_fp, stderr=err_fp)
            po.wait()

        if po.returncode != 0:
            msg = 'VEnv.make_venv: making venv %s: error %s' % \
                  (' '.join(cmd), po.returncode)
            self.logger.error(msg)
            raise RuntimeError(msg)
        self.logger.info("making venv %s success!" % self.root)
        return 0

    # ==========================================================================
    def check_venv(self):
        if not self.use:
            py = os.path.abspath(sys.executable)
            self.py = py
            self.logger.debug('VEnv.check_venv: use=%s, py=%s' % (self.use, self.py))
            return py

        if not os.path.isdir(self.root):
            self.make_venv()
        if sys.platform == 'win32':
            py = os.path.abspath(os.path.join(self.root, 'Scripts', 'python.exe'))
        else:
            py = os.path.abspath(os.path.join(self.root, 'bin', 'python'))
        if not os.path.exists(py):
            msg = 'VEnv.check_venv: Cannot find python "%s"' % py
            self.logger.error(msg)
            raise RuntimeError(msg)
        self.py = py
        self.logger.debug(
            'VEnv.check_venv: use=%s, py=%s' % (self.use, self.py))
        return py

    # ==========================================================================
    def get_venv(self):
        return self.check_venv()

    # ==========================================================================
    @staticmethod
    def enqueue_stdout(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    # ==========================================================================
    @staticmethod
    def enqueue_stderr(err, queue):
        for line in iter(err.readline, b''):
            queue.put(line)
        err.close()

    # ==========================================================================
    def get_line_str(self, line):
        try:
            line = line.decode("utf-8").rstrip()
        except UnicodeDecodeError:
            cd = chardet.detect(line)
            line = line.decode(cd['encoding']).rstrip()
        except Exception as err:
            self.logger.error('get_line_str: Error: %s' % str(err))
            raise
        return line

    # ==========================================================================
    def do_stdout(self, line, kwargs, out_fp):
        if not line:
            return
        line = self.get_line_str(line)
        if kwargs['getstdout']:
            print(line)
        out_fp.write('%s\n' % line)
        self.logger.debug('VEnv.venv_py: %s' % line)
        if self.sta is None:
            self.sta = StatLogger()
        self.sta.log(StatLogger.LT_3, line)

    # ==========================================================================
    def do_stderr(self, line, kwargs, err_fp):
        if not line:
            return
        line = self.get_line_str(line)
        if kwargs['getstdout']:
            sys.stderr.write('%s\n' % line)
        err_fp.write('%s\n' % line)
        if line.startswith('You are using pip version') or line.startswith('You should consider upgrading via the'):
            self.logger.debug('VEnv.venv_py: %s' % line)
        else:
            self.logger.error('VEnv.venv_py: %s' % line)

    # ==========================================================================
    def venv_py(self, *args, **kwargs):
        tmpdir = None
        try:
            if 'raise_error' not in kwargs:
                kwargs['raise_error'] = False
            if 'getstdout' not in kwargs:
                kwargs['getstdout'] = False
            if 'outfile' not in kwargs:
                kwargs['outfile'] = None
            cmd = [
                self.get_venv(),
            ]
            # cmd += args
            for arg in args:
                if arg.lower().startswith('c:\\'):
                    arg = '"%s"' % arg
                cmd.append(arg)
            self.logger.debug('VEnv.venv_py: cmd="%s"' % ' '.join(cmd))
            # Windows의 python.exe -m 등의 명령어가 shell 모드에서 정상 동작함

            tmpdir = tempfile.mkdtemp(prefix='venv_py_')
            out_path = os.path.join(tmpdir, 'stdout.txt')
            err_path = os.path.join(tmpdir, 'stderr.txt')
            self.logger.debug('VEnv.venv_py: cmd="%s"' % ' '.join(cmd))
            with open(out_path, 'w', encoding='utf-8') as out_fp, \
                    open(err_path, 'w', encoding='utf-8') as err_fp:
                # po = subprocess.Popen(' '.join(cmd), shell=True,
                #                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                po = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                q_out, q_err = Queue(), Queue()
                t_out = Thread(target=self.enqueue_stdout, args=(po.stdout, q_out))
                t_out.daemon = True  # thread dies with the program
                t_out.start()
                t_err = Thread(target=self.enqueue_stderr, args=(po.stderr, q_err))
                t_err.daemon = True  # thread dies with the program
                t_err.start()

                # while po.poll() is None:
                while po.poll() is None:
                    try:
                        line = q_out.get_nowait()
                        self.do_stdout(line, kwargs, out_fp)
                    except Empty:
                        pass
                    try:
                        line = q_err.get_nowait()  # or q.get(timeout=.1)
                        self.do_stderr(line, kwargs, err_fp)
                    except Empty:
                        pass
                    time.sleep(0.1)

                while not q_out.empty():
                    line = q_out.get()
                    self.do_stdout(line, kwargs, out_fp)
                while not q_err.empty():
                    line = q_err.get()  # or q.get(timeout=.1)
                    self.do_stderr(line, kwargs, err_fp)

                t_out.join()
                t_err.join()

            if kwargs['outfile']:
                shutil.copy2(out_path, kwargs['outfile'])
            if po.returncode != 0 and kwargs['raise_error']:
                msg = 'VEnv.venv_py: venv command "%s": error %s' % (' '.join(cmd), po.returncode)
                self.logger.error(msg)
                raise RuntimeError(msg)
            self.logger.debug('VEnv.venv_py: returncode="%s"' % po.returncode)
            return po.returncode
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)

    # ==========================================================================
    def venv_pip(self, *args, **kwargs):
        # self.logger.debug('venv_pip: self.py="%s"' % self.py)
        # self.logger.debug('venv_pip: sys.executable="%s"' % sys.executable)
        # self.logger.debug('venv_pip: sys.path=%s' % sys.path)
        # self.logger.debug('venv_pip: environ[PATH]="%s"' % os.environ['PATH'])
        # self.logger.debug('venv_pip: environ[PYTHONPATH]="%s"' % os.environ['PYTHONPATH'])

        # r = pipmain(list(args))
        msg_l = list(args[:2])
        if msg_l[-1].startswith('-') and len(args) > 2:
            msg_l.append(args[2])
        if len(msg_l) >= 2 and msg_l[-1].startswith(str(Path.home())):
            # noinspection PyBroadException
            try:
                msg_l[-1] = os.path.basename(msg_l[-1])
            except Exception:
                pass
        if msg_l[0] == 'freeze':
            msg_l[0] = 'finishing...'
        if self.sta is None:
            self.sta = StatLogger()
        self.sta.log(StatLogger.LT_2, ' '.join(msg_l))
        r = self.venv_py('-m', 'pip', *args, **kwargs)
        self.logger.debug('venv_pip: "%s" returns %s' % (' '.join(args), r))
        return r


################################################################################
# noinspection PyShadowingBuiltins,PyUnresolvedReferences,PyBroadException,PyPep8Naming
class PPM(object):
    # ==========================================================================
    BUILD_PKGS = [
        'wheel',
    ]
    UPLOAD_PKGS = [
        'twine',
    ]
    # PLUGIN_PKGS = [
    #     # 'pip2pi',
    #     # 'twine',    # for gTTS
    #     # 'zip',  # for dumppi
    #     # 'pbr',  # for dumppi
    # ]
    DUMPPI_PKGS = [
        'alabs.ppm',
        'twine',
        # 'zip',
        'pbr',
    ]
    CLASSIFIERS = [
        'Topic :: RPA',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        # for build date
        'Build :: Method :: alabs.ppm',
        'Build :: Date :: %s' %
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ]
    DUMPSPEC_JSON = 'dumpspec.json'
    EXCLUDE_PKGS = ('alabs.ppm', 'alabs.common', 'alabs.icon')
    # ==========================================================================
    URL_OAUTH = [
        'https://oauth-rpa.argos-labs.com',     # 첫번째는 무조건 공식 도메인
        'https://oauth-rpa-hcl.argos-labs.com',
    ]
    URL_API_CHIEF = [
        'https://api-chief.argos-labs.com',     # 첫번째는 무조건 공식 도메인
        'https://api-chief-hcl.argos-labs.com',
    ]
    URL_S3 = 'https://s3-us-west-2.amazonaws.com'
    URL_MOD_VER = '%s/rpa-file.argos-labs.com/plugins/mod-ver-list.json' % URL_S3
    URL_DEF_DUMPSPEC = '%s/rpa-file.argos-labs.com/plugins/dumpspec-def-all.json' % URL_S3
    URL_DUMPSPEC = '%s/rpa-file.argos-labs.com/plugins/{plugin_name}-{version}-dumpspec.json' % URL_S3

    # ==========================================================================
    @staticmethod
    def _is_url_valid(url):
        up = urlparse(url)
        nl = up.netloc
        if nl.find(':') > 0:
            host = urlparse(url).netloc.split(':')[0]
            port = urlparse(url).netloc.split(':')[1]
        else:
            host = nl
            port = 443 if up.scheme == 'https' else 80
        return is_svc_opeded(host, int(port))

    # ==========================================================================
    @staticmethod
    def _get_valid_url(urls):
        for url in urls:
            if PPM._is_url_valid(url):
                return url
        return None

    # ==========================================================================
    def _get_URL_OAUTH(self, is_on_premise=False):
        if is_on_premise:
            r = self._get_valid_url(reversed(self.URL_OAUTH))
        else:
            r = self._get_valid_url(self.URL_OAUTH)
        if not r:
            raise RuntimeError('Cannot valid URL for OAUTH')
        return r

    # ==========================================================================
    def _get_URL_API_CHIEF(self, is_on_premise=False):
        if is_on_premise:
            r = self._get_valid_url(reversed(self.URL_API_CHIEF))
        else:
            r = self._get_valid_url(self.URL_API_CHIEF)
        if not r:
            raise RuntimeError("Cannot valid URL for Supersivor's API")
        return r

    # ==========================================================================
    def _is_on_premise(self):
        return self.args.on_premise
        # # 인터넷 연결과 상관없이 on-premise 인가 조사
        # r1 = self._get_valid_url(self.URL_OAUTH[1:])
        # r2 = self._get_valid_url(self.URL_API_CHIEF[1:])
        # return r1 and r2

    # ==========================================================================
    def __init__(self, _venv, args, config, logger=None, sta=None):
        self.venv = _venv
        self.args = args
        self.config = config    # .argos-rpa.conf (yaml)
        if logger is None:
            logger = get_logger(LOG_PATH)
        self.logger = logger
        if sta is None:
            sta = StatLogger()
        self.sta = sta
        # for internal
        self.pkgname = None
        self.pkgpath = None
        self.basepath = None
        self.setup_config = None
        self.indices = []
        self.ndx_param = []
        # Next are for POT speed-up
        self.mod_ver_list = None
        self.def_dumpspec = None

    # ==========================================================================
    def _get_pkgname(self):
        # alabs.demo.helloworld 패키지를 설치하려고 하면, 해당 helloworld 폴더에
        # 들어가서 ppm 을 돌림
        if not os.path.exists('__init__.py'):
            # --venv 가 없는 경우도 있으므로 그냥 '.' 을 리턴
            # raise RuntimeError('Cannot find __init__.py file. Please run '
            #                    'ppm in python package folder')
            return '.'
        pkglist = []
        abspath = os.path.abspath('.')
        abs_list = abspath.split(os.path.sep)
        while True:
            if len(abs_list) <= 1:
                raise RuntimeError('PPM._get_pkgname: Cannot find package (__init__.py)')
            pkglist.append(abs_list[-1])
            abs_list = abs_list[0:-1]
            ppath = os.path.sep.join(abs_list)
            if not os.path.exists(os.path.join(ppath, '__init__.py')):
                self.basepath = ppath
                if self.args.venv:
                    os.chdir(ppath)
                break
        pkglist.reverse()
        return '.'.join(pkglist)

    # ==========================================================================
    def _check_pkg(self):
        self.pkgname = self._get_pkgname()
        self.pkgpath = self.pkgname.replace('.', os.path.sep)

        if self.args.venv and not os.path.exists(self.pkgpath):
            raise RuntimeError('PPM._check_pkg: Cannot find package path for "%s"' % self.pkgpath)
        if self.args.new_py:
            self.venv.make_venv()
        else:
            self.venv.check_venv()

    # ==========================================================================
    @staticmethod
    def _check_subargs(subargs):
        sa = subargs
        # subparser에서 REMAINER를 이용하면 첫번째 "-V" 과 같은 옵션이
        # 상위 옵션으로 먹히기 때문에 옵션부터 이용할 경우 pass 라고 줌
        if sa and sa[0] == 'pass':
            return sa[1:]
        return sa

    # ==========================================================================
    def _clear(self):
        c_cnt = 0
        f = '%s.%s' % (self.pkgname, 'egg-info')
        if os.path.exists(f):
            shutil.rmtree(f)
            c_cnt += 1
        f = 'build'
        if os.path.exists(f):
            shutil.rmtree(f)
            c_cnt += 1
        f = 'dist'
        if os.path.exists(f):
            shutil.rmtree(f)
            c_cnt += 1
        dl = [d for d in glob.glob('**/__pycache__', recursive=True) if
              not d.startswith('py.')]
        for d in dl:
            shutil.rmtree(d)
            c_cnt += 1
        gfl = ('setup.py', 'setup.py.log', 'setup.cfg')
        for gf in gfl:
            if os.path.exists(gf):
                os.unlink(gf)
                c_cnt += 1
        return 0 if c_cnt > 0 else 1

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _clear_py(self):
        return self.venv.clear()

    # ==========================================================================
    def _get_setup_config(self):
        yamlpath = os.path.join(self.pkgpath, 'setup.yaml')
        if not os.path.exists(yamlpath):
            raise IOError('PPM._get_setup_config: Cannot find "%s" for setup' % yamlpath)
        with open(yamlpath) as ifp:
            if yaml.__version__ >= '5.1':
                # noinspection PyUnresolvedReferences
                yaml_config = yaml.load(ifp, Loader=yaml.FullLoader)
            else:
                yaml_config = yaml.load(ifp)
            if 'setup' not in yaml_config:
                raise RuntimeError('PPM._get_setup_config: "setup" attribute must be exists in setup.yaml')
            self.setup_config = yaml_config['setup']

    # ==========================================================================
    def _set_private_repositories(self, _prlist):
        prconfig = list()
        prlist = sorted(_prlist, key=lambda d: d['view_priority'])
        for prd in prlist:
            if not prd['is_activate']:
                continue
            prconfig.append({
                'name': prd['repo_name'],
                'url': prd['repo_url'],
                'username': prd['repo_user'],
                'password': prd['repo_pw'],
            })
        self.config['private-repositories'] = prconfig

    # ==========================================================================
    def _get_private_repositories(self):
        url = '%s/chief/repositories' \
              % self._get_URL_API_CHIEF(is_on_premise=self._is_on_premise())
        try:
            headers = {
                'Accept': 'application/json',
            }
            if not self.args.pam_id:
                headers['authorization'] = self.args.user_auth
                r = requests.get(url, headers=headers)
            else:
                params = (
                    ('user_id', self.args.user),
                    ('pam_auth_key', self.args.user_auth),
                    ('pam_mac_address', self.args.pam_id),
                )
                r = requests.get(url, headers=headers, params=params)
            if r.status_code // 10 != 20:
                msg = 'Get private plugin for user "%s" Error: API result is %s' \
                      % (self.args.user, r.status_code)
                sys.stderr.write('%s\n' % msg)
                self.logger.error(msg)
                return False
            else:
                self._set_private_repositories(json.loads(r.text))
                return True
        except Exception as err:
            self.sta.log(StatLogger.LT_2, 'Error: to connect "%s"' % url)
            msg = '_get_private_repositories Error to connect "%s": \n%s\n' % (url, str(err))
            sys.stderr.write(msg)
            self.logger.error(msg)
            return False

    # ==========================================================================
    def _get_indices(self):
        self.indices = []
        self.ndx_param = []

        if not self._is_on_premise():
            url = get_xpath(self.config, '/repository/url')
            if not url:
                raise RuntimeError('PPM._get_indices: Invalid repository.url from %s'
                                   % CONF_NAME)
            if self._is_url_valid(url):
                self.indices.append(url)
                self.ndx_param.append('--index')
                self.ndx_param.append(url)
                self.ndx_param.append('--trusted-host')
                self.ndx_param.append(self._get_host_from_index(url))
        pr = None

        # 2019.7.27 POT private plugin 정보를 API로 가져오도록 함
        is_pr = False
        if self.args.user and self.args.user_auth:
            is_pr = self._get_private_repositories()
        if not is_pr:
            return self.indices
        # 2019.12.06 : 만약 on-premise 처럼 API에서 못 가져오면 config에서
        # 가져오도록 아래를 타도록 위에 두 줄을 막음

        if 'private-repositories' in self.config:
            pr = self.config.get('private-repositories', [])
        if not pr:
            pr = []
        for rep in pr:
            url = rep.get('url')
            if not url:
                continue
            self.indices.append(url)
            self.ndx_param.append('--extra-index-url')
            self.ndx_param.append(url)
            self.ndx_param.append('--trusted-host')
            self.ndx_param.append(self._get_host_from_index(url))
        self.logger.debug('PPM._get_indices: indices=%s, ndx_param=%s' %
                          (self.indices, self.ndx_param))
        return self.indices

    # ==========================================================================
    @staticmethod
    def _get_host_from_index(url):
        return urlparse(url).netloc.split(':')[0]

    # ==========================================================================
    def _dumpspec(self):
        _ = self._install_requirements()
        dumpspec_file = os.path.join(self.pkgpath, self.DUMPSPEC_JSON)
        self.venv.venv_py('-m',
                          self.pkgname, '--dumpspec',
                          '--outfile', dumpspec_file,
                          getstdout=True)

    # ==========================================================================
    def _list_modules(self, startswith='argoslabs.',
                      official_only=False, private_only=False):
        modlist = list()
        if official_only and self._is_on_premise():
            # 2019.12.11 on-premise 인 경우에는 official 무시
            return modlist
        for i, url in enumerate(self.indices):
            if i == 0 and private_only:
                if self._get_host_from_index(url) == 'pypi-official.argos-labs.com':
                    continue
            if official_only:
                if self._get_host_from_index(url) != 'pypi-official.argos-labs.com':
                    continue
            o = urlparse(url)
            web_url = '{scheme}://{netloc}/packages/'.format(scheme=o.scheme,
                                                             netloc=o.netloc)
            # noinspection PyProtectedMember
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(web_url, context=context) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
            for x in soup.find_all('a'):
                # pprint(x.text)
                # offline 저장소를 만들려다 보니 argoslabs.* 만 플러그인으로 가져오도록 함
                if not x.text.startswith('argoslabs.'):
                    continue
                if startswith and not x.text.startswith(startswith):
                    continue
                is_exclude = False
                for exc_pkg in self.EXCLUDE_PKGS:
                    if x.text.startswith(exc_pkg):
                        is_exclude = True
                        break
                if is_exclude:
                    continue
                if x.text not in modlist:
                    modlist.append(x.text)
        modlist.sort()
        return modlist

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _dumpspec_json_clear_cache(self):
        glob_filter = '%s%sdumpspec-*.json' % (tempfile.gettempdir(), os.path.sep)
        for f in glob.glob(glob_filter):
            os.remove(f)

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _dumpspec_json_save(self, modname, version, jd):
        jsfile = '%s%sdumpspec-%s-%s.json' % (tempfile.gettempdir(), os.path.sep, modname, version)
        if os.path.exists(jsfile):
            return False
        with open(jsfile, 'w') as ofp:
            json.dump(jd, ofp)
        self.logger.debug('PPM._dumpspec_json_save: save dumpspec cache "%s"' % jsfile)
        return True

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _dumpspec_json_load(self, modname, version):
        jsfile = '%s%sdumpspec-%s-%s.json' % (tempfile.gettempdir(), os.path.sep, modname, version)
        if not os.path.exists(jsfile):
            return None
        with open(jsfile) as ifp:
            r = json.load(ifp)
        self.logger.debug('PPM._dumpspec_json_load: load dumpspec from "%s"' % jsfile)
        return r

    # ==========================================================================
    def _def_dumpspec_from_s3(self):
        if not self._is_url_valid(self.URL_S3):
            return {}
        r = requests.get(self.URL_DEF_DUMPSPEC)
        if r.status_code // 10 != 20:
            self.sta.error("download %s error!" % self.URL_DEF_DUMPSPEC)
            raise RuntimeError('Cannot get "%s"' % self.URL_DEF_DUMPSPEC)
        self.sta.log(StatLogger.LT_3, "download %s" % self.URL_DEF_DUMPSPEC.split('/')[-1])
        return json.loads(r.content)

    # ==========================================================================
    def _dumpspec_from_s3(self, modname, version):
        if modname in self.def_dumpspec:
            for ds in self.def_dumpspec[modname]:
                if ds['plugin_version'] == version:
                    return ds
            self.logger.error('Found "%s" module but not version "%s" in self.def_dumpspec' % (modname, version))
        if not self._is_url_valid(self.URL_S3):
            raise IOError('Cannot find valid url for S3 store')
        url = self.URL_DUMPSPEC.format(plugin_name=modname, version=version)
        r = requests.get(url)
        if r.status_code // 10 != 20:
            self.sta.error("download %s error!" % url)
            raise RuntimeError('Cannot get "%s"' % url)
        self.sta.log(StatLogger.LT_3, "download %s" % url.split('/')[-1])
        return json.loads(r.content)

    # ==========================================================================
    def _mod_ver_list_from_s3(self):
        try:
            if not self._is_url_valid(self.URL_S3):
                raise RuntimeError('Cannot find valid url for S3 store')
            r = requests.get(self.URL_MOD_VER)
            if r.status_code // 10 != 20:
                self.sta.error("download %s error!" % self.URL_MOD_VER)
                raise RuntimeError('Cannot get "%s"' % self.URL_MOD_VER)
            self.sta.log(StatLogger.LT_3, "download %s" % self.URL_MOD_VER.split('/')[-1])
            rj = json.loads(r.content)
            mvl = {}
            for md in rj['mod-ver-list']:
                mvl[md['name']] = md['versions']
            return mvl
        except Exception:
            return {}

    # ==========================================================================
    def _find_last_version_from_mod_ver_list(self, modname):
        if not self.mod_ver_list:
            return None
        if modname not in self.mod_ver_list:
            return None
        return self.mod_ver_list[modname][0]   # descending order

    # ==========================================================================
    def _dumpspec_json(self, modname, version=None):
        # pip download argoslabs.demo.helloworld==1.327.1731
        # --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com
        # --dest=C:\tmp\pkg --no-deps
        if not version:
            log_msg = "Getting specifications for plugin %s" % modname
        else:
            log_msg = "Getting specifications for plugin %s with version %s" % (modname, version)
        self.sta.log(StatLogger.LT_3, log_msg)
        mname = modname
        if not version:
            version = self._find_last_version_from_mod_ver_list(modname)
        if version:
            # noinspection PyBroadException
            try:
                return self._dumpspec_from_s3(modname, version)
            except Exception:
                err_msg = 'Cannot get S3 dumpspec for ("%s", "%s")' % (modname, version)
                self.sta.error(err_msg)
                self.logger.debug(err_msg)
            mname = '%s==%s' % (modname, version)
            jd = self._dumpspec_json_load(modname, version)
            if jd:
                return jd

        glob_filter = '%s%s%s-*.whl' % (tempfile.gettempdir(), os.path.sep, modname)
        for f in glob.glob(glob_filter):
            os.remove(f)
        self.venv.venv_pip('download', mname,
                           '--dest', tempfile.gettempdir(),
                           '--no-deps',
                           *self.ndx_param)
        mfilename = None
        for f in glob.glob(glob_filter):
            mfilename = f
            break
        if not mfilename:
            err_msg = 'PPM._dumpspec_json: Cannot get plugin wheel file "%s"' % mfilename
            self.sta.error(err_msg)
            raise RuntimeError(err_msg)
        eles = os.path.basename(mfilename).split('-')
        jd = self._dumpspec_json_load(eles[0], eles[1])
        if jd:
            return jd
        with zipfile.ZipFile(mfilename) as zf:
            dsj = modname.replace('.', '/') + '%s%s' % ('/', self.DUMPSPEC_JSON)
            with zf.open(dsj) as jfp:
                jd = json.load(jfp)
                self.logger.debug('PPM._dumpspec_json: get dumpspec.json from "%s"' % mfilename)
                self._dumpspec_json_save(eles[0], eles[1], jd)
                return jd

    # ==========================================================================
    def _dumpspec_user(self, tmpdir):
        # curl -X GET --header 'Accept: application/json'
        #   --header 'authorization: Bearer 312df8e2-b143-4d5e-8d77-f4c15fe2b911'
        #   'https://api-chief.argos-labs.com/plugin/api/v1.0/users/fjoker%40naver.com/plugins'
        # GET /plugin/api/v1.0/users/{user_id}/plugins
        # curl -X GET --header 'Accept: application/json' 'https://api-chief.argos-labs.com/plugin/api/v1.0/users/seonme%40vivans.net/plugins'
        msg = 'Try to dump plugin spec for user "%s"' % self.args.user
        sys.stdout.write('%s\n' % msg)
        self.logger.info(msg)
        url = '%s/plugin/api/v1.0/users/%s/plugins' \
              % (self._get_URL_API_CHIEF(is_on_premise=self._is_on_premise()),
                 quote(self.args.user))
        if not self.args.user_auth:
            raise RuntimeError('_dumpspec_user: --user-auth option must have a valid key')
        headers = {
            # 'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'authorization': self.args.user_auth,
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3',
        }
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code // 10 != 20:
            msg = 'Dump plugin spec for user "%s" Error: API result is %s' % (self.args.user, r.status_code)
            sys.stderr.write('%s\n' % msg)
            self.logger.error(msg)
            self.sta.error('Error to get user dependent information. Please logout STU and login again.')
            raise RuntimeError('PPM._dumpspec_user: API Error!')
            # mdlist = [
            #     {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.ai.tts', 'plugin_version': '1.330.1500'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.api.rest', 'plugin_version': '1.315.1054'},
            #     {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.api.rossum', 'plugin_version': '1.327.1355'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.data.excel', 'plugin_version': '1.425.1322'},
            #     {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.data.json', 'plugin_version': '1.418.1631'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.data.rdb', 'plugin_version': '1.313.1857'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.filesystem.monitor', 'plugin_version': '1.424.1142'},
            #     {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.filesystem.op', 'plugin_version': '1.418.1812'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.filesystem.op', 'plugin_version': '1.430.1418'},
            #     # {'user_id': 'seonme@vivans.net', 'plugin_id': 'argoslabs.terminal.sshexp', 'plugin_version': '1.415.1930'},
            # ]
        else:
            mdlist = json.loads(r.text)
            self.sta.log(StatLogger.LT_3, 'Getting %d plugins for the user' % len(mdlist))
        # print(md)
        if not self.args.private_only:
            req_txt = os.path.join(tmpdir, 'requirements.txt')
            with open(req_txt, 'w') as ofp:
                for md in mdlist:
                    if 'plugin_name' in md:
                        if 'plugin_version' in md:
                            ofp.write('%s==%s\n' % (md['plugin_name'], md['plugin_version']))
                        else:
                            ofp.write('%s\n' % md['plugin_name'])
                    else:
                        self.logger.error('Chief API result for user plugin "%s" must have "plugin_name" key')
            self.args.requirements_txt = req_txt
            # self.args.user = None
        return True

    # ==========================================================================
    def _pre_requirements_install(self, new_venv, _tmpdir, whlfile, modname,
                                  prefix='argoslabs.'):
        self.logger.debug('_pre_requirements_install: new_venv="%s", _tmpdir="%s", whlfile="%s", modname="%s", prefix="%s"'
                          % (new_venv.root,  _tmpdir, whlfile, modname, prefix))
        with closing(zipfile.ZipFile(whlfile)) as zf:
            rqt = modname.replace('.', os.path.sep) + '%s%s' % (os.path.sep, 'requirements.txt')
            rqt_f = '%s%srequirements.txt' % (_tmpdir, os.path.sep)
            # 만약 whl 안에 requirements.txt 가 있다면 이를 먼저 설치
            # noinspection PyBroadException
            try:
                with zf.open(rqt) as ifp:
                    with open(rqt_f, 'w', encoding='utf-8') as ofp:
                        ofp.write(ifp.read().decode('utf-8'))
                r = new_venv.venv_pip('install', '-r', rqt_f, *self.ndx_param)
                if r != 0:
                    self.logger.error('_pre_requirements_install: '
                                      'install "%s" error!' % rqt_f)
            except Exception as err:
                # _exc_info = sys.exc_info()
                # _out = traceback.format_exception(*_exc_info)
                # del _exc_info
                # sys.stderr.write('_pre_requirements_install: %s\n' % ''.join(_out))
                self.logger.debug('_pre_requirements_install: '
                                  'install "%s" error: %s' % (rqt_f, str(err)))
            # 만약 whl 안에 whl 이 있다면 이를 직접 설치
            for info in zf.infolist():
                if info.filename.lower().endswith('.whl'):
                    zf.extract(info, _tmpdir)
                    wh_t = os.path.join(_tmpdir, info.filename)
                    if not os.path.exists(wh_t):
                        wh_t = os.path.join(_tmpdir, os.path.basename(info.filename))
                    if not os.path.exists(wh_t):
                        self.logger.error('_pre_requirements_install: '
                                          'extract "%s" from whl but fail to access' % info.filename)
                        r = 1
                    else:
                        r = new_venv.venv_pip('install', wh_t)
                    if r != 0:
                        self.logger.error('_pre_requirements_install: '
                                          'install "%s" error!' % wh_t)

        r = new_venv.venv_pip('install', whlfile, *self.ndx_param)
        return r

    # ==========================================================================
    def _check_cache_download_and_install(self, new_venv, modname, op, version):
        self.logger.debug('_check_cache_download_and_install: new_venv="%s", modname="%s", op="%s", version="%s"'
                          % (new_venv.root, modname, op, version))
        _cachedir = tempfile.gettempdir()
        _tmpdir = tempfile.mkdtemp(prefix='down_install_')
        try:
            if op == '==' and version:
                gl = glob.glob('%s/%s-%s-*.whl' % (_cachedir, modname, version))
                for f in gl:
                    return self._pre_requirements_install(new_venv, _tmpdir, f, modname)
            modspec = modname
            if op and version:
                modspec += '%s%s' % (op, version)
            _args = [
                'download', modspec,
                '--dest', _tmpdir,
                '--no-deps',
                *self.ndx_param
            ]
            r = new_venv.venv_pip(*_args)
            if r != 0:
                _msg = '_check_cache_download_and_install: Cannot pip download: cmd=%s' % ' '.join(_args)
                self.logger.error(_msg)
                raise RuntimeError(_msg)
            gl = glob.glob('%s/%s-*.whl' % (_tmpdir, modname))
            gls = [f for f in gl]
            if gls:
                for f in gls:
                    r = self._pre_requirements_install(new_venv, _tmpdir, f, modname)
                    if r != 0:
                        self.logger.error('_check_cache_download_and_install: '
                                          'install "%s" error!' % f)
                    # noinspection PyBroadException
                    try:
                        shutil.move(f, _cachedir)
                    except Exception:
                        self.logger.error('"%s" is exists in "%s"'
                                          % (os.path.basename(f), _cachedir))
                    return r
            # whl이 아닌 경우 그대로 설치하려고 노력 : 2019.12.12
            _args = [
                'install', modspec,
                *self.ndx_param
            ]
            r = new_venv.venv_pip(*_args)
            return r
        finally:
            if os.path.exists(_tmpdir):
                shutil.rmtree(_tmpdir)

    # ==========================================================================
    def _download_and_install(self, new_venv, requirements_txt):
        self.logger.debug('_download_and_install: new_venv="%s", requirements_txt="%s"'
                          % (new_venv.root, requirements_txt))
        r = -1
        _modspec = {}
        with open(requirements_txt) as ifp:
            for req in requirements.parse(ifp):
                _modspec[req.name] = req.specs
        for modname, speclist in _modspec.items():
            if speclist:
                for op, ver in speclist:
                    r = self._check_cache_download_and_install(new_venv, modname, op, ver)
                    break
            else:
                # noinspection PyTypeChecker
                r = self._check_cache_download_and_install(new_venv, modname, None, None)
        return r

    # ==========================================================================
    def _get_venv(self, new_d):
        _tmpdir = None
        try:
            self.args.venv = True
            new_venv = VEnv(self.args, root=new_d, logger=self.logger)
            new_venv.check_venv()
            if self.args.requirements_txt:
                requirements_txt = self.args.requirements_txt
            else:
                _tmpdir = tempfile.mkdtemp(prefix='get_venv_')
                requirements_txt = os.path.join(_tmpdir, 'requirements.txt')
                with open(requirements_txt, 'w') as ofp:
                    ofp.write('# pip dependent packages\n')
                    for pm in self.args.plugin_module:
                        ofp.write('%s\n' % pm)
            # r = new_venv.venv_pip('install', '-r', requirements_txt,
            #                       *self.ndx_param, getstdout=True)
            r = self._download_and_install(new_venv, requirements_txt)
            if r == 0:
                outfile = os.path.join(new_d, 'freeze.txt')
                new_venv.venv_pip('freeze', outfile=outfile, getstdout=True)
                freeze_d = {}
                with open(outfile) as ifp:
                    for line in ifp:
                        eles = line.rstrip().split('==')
                        if len(eles) != 2:
                            raise RuntimeError('PPM._get_venv: freeze must module==version but "%s"' % line.rstrip())
                        freeze_d[eles[0].strip().lower()] = eles[1].strip()
                if os.path.exists(outfile):
                    os.remove(outfile)
                freeze_f = os.path.join(new_d, 'freeze.json')
                with open(freeze_f, 'w') as ofp:
                    json.dump(freeze_d, ofp)
            else:
                raise RuntimeError('PPM._get_venv: r=%s, new_venv="%s", requirements_txt="%s" error' %
                                   (r, new_venv.root, requirements_txt))
            return r
        finally:
            if _tmpdir and os.path.exists(_tmpdir):
                shutil.rmtree(_tmpdir)

    # ==========================================================================
    def _get_modspec(self, tmpdir):
        """
docopt == 0.6.1             # Version Matching. Must be version 0.6.1
keyring >= 4.1.1            # Minimum version 4.1.1
coverage != 3.5             # Version Exclusion. Anything except version 3.5
Mopidy-Dirble ~= 1.1        # Compatible release. Same as >= 1.1, == 1.*
SomeProject
SomeProject == 1.3
SomeProject >=1.2,<2.0
SomeProject[foo, bar]
SomeProject~=1.4.2

Django [('>=', '1.11'), ('<', '1.12')]
six [('==', '1.10.0')]
        """
        requirements_txt = None
        try:
            modspec = {}
            requirements_txt = os.path.join(tmpdir, 'modspec.txt')
            if self.args.requirements_txt and os.path.exists(self.args.requirements_txt):
                shutil.copy(self.args.requirements_txt, requirements_txt)
            if self.args.plugin_module:
                with open(requirements_txt, 'a') as ofp:
                    ofp.write('# plugin_module parameters\n')
                    for pm in self.args.plugin_module:
                        ofp.write('%s\n' % pm)
            if not os.path.exists(requirements_txt):
                return modspec
            with open(requirements_txt) as ifp:
                for req in requirements.parse(ifp):
                    modspec[req.name.lower()] = req.specs
            return modspec
        finally:
            if requirements_txt and os.path.exists(requirements_txt):
                os.remove(requirements_txt)

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _is_conflict(self, freeze_d, modspec):
        for modname, speclist in modspec.items():
            if modname not in freeze_d:
                continue
            for op, ver in speclist:
                cmp = ver_compare(freeze_d[modname], ver)
                if op == '==':
                    if cmp != 0:
                        return True
                elif op == '>':
                    if cmp <= 0:
                        return True
                elif op == '>=':
                    if cmp < 0:
                        return True
                elif op == '<':
                    if cmp >= 0:
                        return True
                elif op == '<=':
                    if cmp > 0:
                        return True
                elif op == '~=':  # '>=' and '=='
                    f_v = '.'.join(freeze_d[modname].split('.')[:-1])
                    s_v = '.'.join(ver.split('.')[:-1])
                    cmp = ver_compare(f_v, s_v)
                    if cmp < 0:
                        return True
        return False

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _count_satisfy(self, freeze_d, modspec):
        match_cnt = 0
        for modname, speclist in modspec.items():
            if modname not in freeze_d:
                continue
            if not speclist:
                # 만약 모듈이름만 나왔다면 무조건 하나 매칭된다고 가정하자
                match_cnt += 1
            for op, ver in speclist:
                cmp = ver_compare(freeze_d[modname], ver)
                if op == '==':
                    if cmp == 0:
                        match_cnt += 1
                elif op == '>':
                    if cmp > 0:
                        match_cnt += 1
                elif op == '>=':
                    if cmp >= 0:
                        match_cnt += 1
                elif op == '<':
                    if cmp < 0:
                        match_cnt += 1
                elif op == '<=':
                    if cmp <= 0:
                        match_cnt += 1
                elif op == '~=':  # '>=' and '=='
                    f_v = '.'.join(freeze_d[modname].split('.')[:-1])
                    s_v = '.'.join(ver.split('.')[:-1])
                    cmp = ver_compare(f_v, s_v)
                    if cmp >= 0:
                        match_cnt += 1
        return match_cnt

    # ==========================================================================
    def _cmd_modspec(self, moddict, modspec, version_attr='version'):
        rd = {}
        if not modspec:  # all
            if self.args.last_only:
                for modname in moddict.keys():
                    rd[modname] = moddict[modname][0]  # 마지막 버전
                return rd
            return moddict
        for modname, speclist in modspec.items():
            if modname not in moddict:
                self.logger.error('plugin get command module "%s" does not exists in plugin list' % modname)
                continue
            if not speclist:
                # 만약 모듈이름만 나왔다면 무조건 최신 모듈
                rd[modname] = moddict[modname][0]  # 마지막 버전
                continue
            b_found = False
            for vdict in moddict[modname]:
                for op, ver in speclist:
                    cmp = ver_compare(vdict[version_attr], ver)
                    if op == '==':
                        if cmp == 0:
                            b_found = True
                    elif op == '>':
                        if cmp > 0:
                            b_found = True
                    elif op == '>=':
                        if cmp >= 0:
                            b_found = True
                    elif op == '<':
                        if cmp < 0:
                            b_found = True
                    elif op == '<=':
                        if cmp <= 0:
                            b_found = True
                    elif op == '~=':  # '>=' and '=='
                        f_v = '.'.join(vdict[version_attr].split('.')[:-1])
                        s_v = '.'.join(ver.split('.')[:-1])
                        cmp = ver_compare(f_v, s_v)
                        if cmp >= 0:
                            b_found = True
                    if b_found:
                        rd[modname] = vdict
                        break
                if b_found:
                    break
            if not b_found:
                self.logger.error('plugin get command module "%s" failed to find '
                                  'version spec %s' % (modname, str(speclist)))
        return rd

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _get_with_dumpspec(self, mod, d, modds):
        if mod not in modds:
            raise RuntimeError('Cannot get "%s" dumpspec from modds in _get_with_dumpspec' % mod)
        for ds in modds[mod]:
            if d['version'] == ds['plugin_version']:
                d['dumpspec'] = ds
                return True
        raise RuntimeError('Cannot find "%s" dumpspec from modds in _get_with_dumpspec' % mod)

    # ==========================================================================
    def do_plugin(self):
        ofp = sys.stdout
        modd = {}
        modds = {}
        tmpdir = tempfile.mkdtemp(prefix='do_plugin_')
        try:
            self.sta.log(StatLogger.LT_2, "Starting plugin %s command" % self.args.plugin_cmd)
            self.logger.info('PPM.do_plugin: starting... %s' % self.args.plugin_cmd)
            self.def_dumpspec = self._def_dumpspec_from_s3()

            # for pkg in self.PLUGIN_PKGS:
            #     # self.venv.venv_pip('install', pkg, *self.ndx_param)
            #     self.venv.venv_pip('install', pkg)

            if self.args.outfile:
                ofp = open(self.args.outfile, 'w', encoding='utf-8')

            ####################################################################
            # PAM용 환경설정 만들기
            ####################################################################
            if self.args.plugin_cmd == 'venv':
                self.sta.log(StatLogger.LT_2, "Preparing execution environment")
                if not (self.args.plugin_module or self.args.requirements_txt):
                    raise RuntimeError('PPM.do_plugin: plugin-modules parameters or --requirements-txt option must be specifiyed.')
                if self.args.requirements_txt and not os.path.exists(self.args.requirements_txt):
                    raise RuntimeError('PPM.do_plugin: --requirements-txt "%s" file does not exists.' % self.args.requirements_txt)
                # ~/.argos-rpa.venv/ 폴더 안에 YYYMMDD-HHMMSS 로 가상환경을 만듦
                venv_d = os.path.join(str(Path.home()), '.argos-rpa.venv')
                if not os.path.exists(venv_d):
                    os.makedirs(venv_d)
                modspec = self._get_modspec(tmpdir)
                # glob_f = os.path.join(venv_d, '**', 'freeze.json')
                glob_f = os.path.join(venv_d, '*')
                match_list = list()
                for f in glob.glob(glob_f):
                    if not os.path.isdir(f):
                        continue
                    if os.path.basename(f) == 'Python37-32':
                        continue
                    fzj = os.path.join(f, 'freeze.json')
                    if not os.path.exists(fzj):
                        shutil.rmtree(f)
                        continue
                    with open(fzj) as ifp:
                        freeze_d = json.load(ifp)
                    if self._is_conflict(freeze_d, modspec):
                        continue
                    match_cnt = self._count_satisfy(freeze_d, modspec)
                    get_venv = os.path.abspath(f)
                    match_list.append((match_cnt, get_venv))
                # 설치가능한 venv가 발견되지 않았다면, 새로 만듦
                if not match_list:
                    self.sta.log(StatLogger.LT_1, 'Preparing ARGOS RPA+ environment. This process may take a few minutes.')
                    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    get_venv = os.path.join(venv_d, now)
                    self._get_venv(get_venv)
                else:  # 아니면 가장 많이 매칭된 것을 찾아 이용
                    self.sta.log(StatLogger.LT_1, 'An ARGOS RPA+ environment was found.')
                    match_list.sort(key=lambda x: x[0])
                    get_venv = match_list[-1][1]
                    if match_list[-1][0] < len(modspec):
                        self._get_venv(get_venv)
                ofp.write(get_venv)
                return 0

            # 만약 CHIEF에 특정 사용자별 dumpspec 결과를 가져오려면 우선
            # 해당 모듈 리스트를 구함
            if self.args.plugin_cmd == 'dumpspec' and self.args.user:
                self._dumpspec_user(tmpdir)

            # 나머지는 CHIEF, STU용
            # 우선은 pypi 서버에서 해당 모듈 목록을 구해와서
            # 해당 모듈(wheel)만 다운로드하여 포함되어 있는 dumpspec.json을
            # 가져오는데 tempdir에 dumpspec-modulename-version.json 식으로 캐슁
            self.sta.log(StatLogger.LT_1, 'Downloading plugins. It may take a few minutes. Private plugins could take more.')

            if self.args.flush_cache:
                self._dumpspec_json_clear_cache()
            if self.args.plugin_cmd == 'versions' and not self.args.startswith:
                # versions 명령에서는 해당 모듈만 가져오도록 필터링
                self.args.startswith = self.args.plugin_module[0]
            modlist = self._list_modules(startswith=self.args.startswith,
                                         official_only=self.args.official_only,
                                         private_only=self.args.private_only)
            for mod in modlist:
                eles = mod.rstrip('.whl').split('-')
                if len(eles) not in (5,):
                    raise RuntimeError('PPM.do_plugin: Invalid format for wheel file "%s"' % mod)
                ved = {
                    'version': eles[1],
                    'python-tag': eles[2],
                    'abi-tag': eles[3],
                    'flatform-tag': eles[4],
                }
                dsj = self._dumpspec_json(eles[0], eles[1])
                ved['display_name'] = dsj.get('display_name')
                ved['description'] = dsj.get('description')
                ved['owner'] = dsj.get('owner')
                ved['group'] = dsj.get('group')
                ved['platform'] = dsj.get('platform')
                ved['last_modify_datetime'] = dsj.get('last_modify_datetime')
                ved['icon'] = dsj.get('icon')
                ved['sha256'] = dsj.get('sha256')
                if eles[0] not in modd:
                    modd[eles[0]] = [ved]
                    modds[eles[0]] = [dsj]
                else:
                    b_found = False
                    for ve in modd[eles[0]]:
                        if ve['version'] == eles[1]:
                            b_found = True
                            break
                    if not b_found:
                        modd[eles[0]].append(ved)
                        modds[eles[0]].append(dsj)
            # modd 에 있는 ved 목록에 대하여 내림차순 정렬
            # cmp_items_py3 = cmp_to_key(version_compare)
            for k, v in modd.items():
                if len(v) <= 1:
                    continue
                modd[k] = sorted(v, key=cmp_to_key(version_compare), reverse=True)
            for k, v in modds.items():
                if len(v) <= 1:
                    continue
                modds[k] = sorted(v, key=cmp_to_key(plugin_version_compare), reverse=True)

            ####################################################################
            # 사용자 plugin_modules를 포함한 --requirements-txt 의 모듈 스펙을 파싱
            ####################################################################
            modspec = self._get_modspec(tmpdir)

            ####################################################################
            # --user 옵션을 안주면 CHIEF에서 모든 플러그인 가져오기
            # 예) alabs.ppm plugin get --official-only --outfile get-all.json
            # --user 옵션을 주면 STU에서 해당 로그인 사용자의 플러그인 가져오기
            # 예) alabs.ppm plugin get --user a@b.c.d --official-only --outfile get-user.json
            # --official-only 는 공식사이트, --private-only는 자신의 private 만 (~/.argos-rpa.conf 에서)
            # 예) alabs.ppm plugin get --user a@b.c.d --private-only --outfile get-user-private.json
            # --last-only
            ####################################################################
            if self.args.plugin_cmd == 'get':
                self.sta.log(StatLogger.LT_2, "Getting the information of plugins")
                rd = self._cmd_modspec(modd, modspec)
                if not self.args.short_output:
                    if self.args.with_dumpspec:
                        for mod, dl in rd.items():
                            if isinstance(dl, dict):
                                self._get_with_dumpspec(mod, dl, modds)
                            elif isinstance(dl, list):
                                for d in dl:
                                    self._get_with_dumpspec(mod, d, modds)
                            else:
                                raise RuntimeError('Invalid type of get result, needed {dict, list}')
                    json.dump(rd, ofp)
                else:
                    for mod in sorted([x for x in rd.keys()]):
                        for ved in rd[mod]:
                            if isinstance(ved, list):
                                for v in ved:
                                    ofp.write('%s,%s%s' % (mod, v['version'], os.linesep))
                            else:
                                ofp.write('%s,%s%s' % (mod, ved['version'], os.linesep))

            elif self.args.plugin_cmd == 'versions':
                self.sta.log(StatLogger.LT_2, "Checking version numbers of plugin")
                if not self.args.plugin_module or len(self.args.plugin_module) != 1:
                    raise RuntimeError('plugin versions need only one plugin_module parameter')
                modname = self.args.plugin_module[0]
                if modname not in modd:
                    raise RuntimeError('module "%s" not in plugin module list' % modname)
                for ved in modd[modname]:
                    print(ved['version'])

            ####################################################################
            # --user 옵션을 안주면 CHIEF/STU에서 모든 플러그인 dumpspec 가져오기
            # 예) alabs.ppm plugin dumpspec --official-only --outfile dumpspec.json
            # --user 옵션을 주면 STU에서 해당 로그인 사용자의 플러그인 가져오기
            # 예) alabs.ppm plugin dumpspec --user a@b.c.d --official-only --outfile dumpspec.json
            # --official-only 는 공식사이트, --private-only는 자신의 private 만 (~/.argos-rpa.conf 에서)
            # 예) alabs.ppm plugin dumpspec --private-only --outfile dumpspec.json
            ####################################################################
            elif self.args.plugin_cmd == 'dumpspec':
                self.sta.log(StatLogger.LT_2, "Getting the specifications of plugins")
                rd = self._cmd_modspec(modds, modspec, version_attr='plugin_version')
                json.dump(rd, ofp)
            ####################################################################
            # plugin 오프라인 용 저장소 만들기 (나중에 http.server 로 동작가능)
            ####################################################################
            # elif self.args.plugin_cmd == 'dumppi':
            #     self.sta.log(StatLogger.LT_2, "Preparing offline plugin reposotory")
            #     if not self.args.dumppi_folder:
            #         raise RuntimeError(
            #             'plugin dumppi command need --dumppi-folder option')
            #     # pip2pi \work\p2p -r \work\reqtest.txt --index https://pypi-official.argos-labs.com/pypi -S
            #     rd = self._cmd_modspec(modd, modspec)
            #     # dp_req_file = '%s%s.dumppi.%d.txt' % (tmpdir, os.path.sep, randint(100000, 999999))
            #     # with open(dp_req_file, 'w') as dp_ofp:
            #     modl = list()
            #     for mod in sorted([x for x in rd.keys()]):
            #         if isinstance(rd[mod], list):
            #             for ved in rd[mod]:
            #                 line = '%s==%s' % (mod, ved['version'])
            #                 # dp_ofp.write('%s\n' % line)
            #                 modl.append(line)
            #         elif isinstance(rd[mod], dict):
            #             line = '%s==%s' % (mod, rd[mod]['version'])
            #             # dp_ofp.write('%s\n' % line)
            #             modl.append(line)
            #         # else raise runtime
            #     from libpip2pi.commands import pip2pi
            #     if not os.path.exists(self.args.dumppi_folder):
            #         os.makedirs(self.args.dumppi_folder)
            #     args = [
            #         'pip2pi',
            #         self.args.dumppi_folder,
            #     ]
            #     args.extend(self.ndx_param)
            #     # if sys.platform == 'win32':
            #     args.append('--no-symlink')  # win32 고려
            #     args.extend(modl)
            #     args.extend(self.DUMPPI_PKGS)
            #     self.logger.debug('pip2pi(%s)' % ' '.join(args))
            #     # pip2pi p2p --index https://pypi-official.argos-labs.com/pypi
            #     # --trusted-host pypi-official.argos-labs.com
            #     # --extra-index-url https://pypi-test.argos-labs.com/simple
            #     # --trusted-host pypi-test.argos-labs.com --no-symlink
            #     # argoslabs.ai.translate==1.410.1357 argoslabs.ai.tts==1.330.1500
            #
            #     # _ = pip2pi(args)
            #     po = subprocess.Popen(args)
            #     po.wait()
            return 0
        finally:
            if self.args.outfile and ofp != sys.stdout:
                ofp.close()
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            self.logger.info('PPM.do_plugin: end. %s' % self.args.plugin_cmd)

    # ==========================================================================
    @staticmethod
    def _parse_req(req):
        o = urlparse(req)
        nls = o.netloc.split(':')
        port = None
        if len(nls) == 2:
            port = int(nls[1])
        else:
            if o.scheme == 'http':
                port = 80
            elif o.scheme == 'https':
                port = 443
        return nls[0], port

    # ==========================================================================
    def _do_upload(self, url, user, passwd, wheels):
        o = urlparse(url)
        raw_url = '{scheme}://{netloc}/'.format(scheme=o.scheme,
                                                netloc=o.netloc)
        # 기존의 twine으로 사설 pypiserver로 올리는데 https 문제 때문에
        # pypiuploader 를 가져와 처리
        # r = self.venv.venv_py('-m', 'twine', 'upload', wheel,
        #                       '--repository-url', raw_url,
        #                       '--username', user,
        #                       '--password', passwd,
        #                       stdout=True)
        cmd = [
            'files',
            '--index-url',
            raw_url,
            '--username', user,
            '--password', passwd,
        ]
        cmd.extend(wheels)
        self.logger.debug('_do_upload: cmd="%s"' % ' '.join(cmd))
        return pu_main(argv=cmd)

    # ==========================================================================
    def _can_self_upgrade(self):
        is_common, is_ppm = False, False
        # for alabs.common
        try:
            cur_common = pkg_resources.get_distribution("alabs.common").version
            last_common = self.mod_ver_list['alabs.common'][0]
            if ver_compare(last_common, cur_common) > 0:
                is_common = True
        except Exception as e:
            self.logger.error('Cannot get version of "alabs.common": %s' % str(e))
        # for alabs.ppm
        try:
            cur_ppm = pkg_resources.get_distribution("alabs.ppm").version
            last_ppm = self.mod_ver_list['alabs.ppm'][0]
            if ver_compare(last_ppm, cur_ppm) > 0:
                is_ppm = True
        except Exception as e:
            self.logger.error('Cannot get version of "alabs.common": %s' % str(e))
        return is_common, is_ppm

    # ==========================================================================
    def _get____tk____(self, u___i, p___w):
        try:
            root_url = self._get_URL_OAUTH(is_on_premise=self._is_on_premise())
            cookies = {
                'JSESSIONID': '04EFBA89842288248F32F9EC19B7423E',
            }

            headers = {
                'Accept': '*/*',
                'Authorization': 'Basic YXJnb3MtcnBhOjA0MGM1YTA1MTkzZWRjYWViZjk4NTY1MmMxOGE1MThj',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Host': '%s' % self._get_host_from_index(root_url),
                'Postman-Token': 'd010ec3c-d0b5-40cf-a3a5-4522fe73b2ad,0af02f20-2044-4983-9db4-ab7aa8453e06',
                'User-Agent': 'PostmanRuntime/7.13.0',
                'accept-encoding': 'gzip, deflate',
                'cache-control': 'no-cache',
                'content-length': '92',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': 'JSESSIONID=04EFBA89842288248F32F9EC19B7423E',
            }

            data = {
                'grant_type': 'password',
                'client_id': 'argos-rpa',
                'scope': 'read write',
                'username': u___i,
                'password': p___w,
            }
            r = requests.post('%s/oauth/token' % root_url,
                              headers=headers, cookies=cookies, data=data)
            if r.status_code // 10 != 20:
                raise RuntimeError('PPM._dumpspec_user: API Error!')
            jd = json.loads(r.text)
            return 'Bearer %s' % jd['access_token']
        except Exception as e:
            msg = '_get____tk____ Error: %s' % str(e)
            self.logger.error(msg)
            return None

    # ==========================================================================
    def do(self):
        try:
            self.logger.info('PPM.do: starting... %s' % self.args.command)

            if self.args.pr_user:
                setattr(self.args, 'user', self.args.pr_user)
            elif not hasattr(self.args, 'user'):
                setattr(self.args, 'user', None)
            if self.args.pr_user_auth:
                setattr(self.args, 'user_auth', self.args.pr_user_auth)
            elif not hasattr(self.args, 'user_auth'):
                setattr(self.args, 'user_auth', None)
            # 만약 --pr-user, --pr-user-pass 를 입력한 경우
            if self.args.user and self.args.pr_user_pass and not self.args.pr_user_auth:
                setattr(self.args, 'user_auth',
                        self._get____tk____(self.args.user, self.args.pr_user_pass))
            # pam_id 처리
            if not hasattr(self.args, 'pam_id'):
                setattr(self.args, 'pam_id', None)

            if self.args.command in ('upload',):
                # 만약 upload 에서 --pr-user 옵션을 안 준 경우, 사용자를 물어서 가져옴
                if not self.args.user:
                    user = input('%s command need user id for ARGOS RPA, User ID? '
                                 % self.args.command)
                    setattr(self.args, 'user', user)
                # 만약 upload 에서 --pr-user 옵션만 주고 실행했을 때는 암호를 물어서 가져옴
                if not self.args.user_auth:
                    u___p = getpass('%s command need user password for ARGOS RPA, User Password? '
                                    % self.args.command)
                    setattr(self.args, 'user_auth', self._get____tk____(self.args.user, u___p))

            if hasattr(self.args, 'subargs'):
                subargs = self._check_subargs(self.args.subargs)
            else:
                subargs = []
            # officail 및 private의 --index 내용 가져오기
            self._get_indices()
            # s3에서 pypi-official의 module 및 버전 목록을 구해옴
            self.mod_ver_list = self._mod_ver_list_from_s3()
            if not getattr(sys, 'frozen', False) and self.args.self_upgrade:
                is_common, is_ppm = self._can_self_upgrade()
                # noinspection PyProtectedMember
                self.venv._upgrade(self.ndx_param, is_common=is_common, is_ppm=is_ppm)

            # first do actions which do not need virtualenv
            ####################################################################
            # get commond
            ####################################################################
            if self.args.command == 'get':
                if self.args.get_cmd == 'repository':
                    self.sta.log(StatLogger.LT_2, 'Connecting offcial repository')
                    print(self.indices[0])
                elif self.args.get_cmd == 'trusted-host':
                    self.sta.log(StatLogger.LT_2, 'Connecting trusted host')
                    print(self._get_host_from_index(self.indices[0]))
                elif self.args.get_cmd == 'private':
                    self.sta.log(StatLogger.LT_2, 'Connecting private repository')
                    prl = self.indices[1:]
                    if not prl:
                        print('No private repository')
                    else:
                        print('There are %s private repository(ies)' % len(prl))
                        print('\n'.join(prl))
                return 0
            # print('start %s ...' % self.args.command)

            ####################################################################
            # plugin commond
            ####################################################################
            if self.args.command == 'plugin':
                return self.do_plugin()

            ####################################################################
            # pip commond
            ####################################################################
            if self.args.command == 'install':
                self.sta.log(StatLogger.LT_2, 'install %s' % ' '.join(subargs))
                subargs.insert(0, 'install')
                subargs.extend(self.ndx_param)
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'show':
                self.sta.log(StatLogger.LT_2, 'show %s' % ' '.join(subargs))
                subargs.insert(0, 'show')
                subargs.append('--verbose')
                return self.venv.venv_pip(*subargs, getstdout=True)
            elif self.args.command == 'uninstall':
                self.sta.log(StatLogger.LT_2, 'uninstall %s' % ' '.join(subargs))
                subargs.insert(0, '-y')
                subargs.insert(0, 'uninstall')
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'search':
                self.sta.log(StatLogger.LT_2, 'search %s' % ' '.join(subargs))
                r = 1
                for ndx in self.indices:
                    sargs = copy.copy(subargs)
                    sargs.insert(0, 'search')
                    # subargs.extend(self.ndx_param)
                    sargs.append('--index')
                    sargs.append(ndx)
                    sargs.append('--trusted-host')
                    sargs.append(self._get_host_from_index(ndx))
                    r = self.venv.venv_pip(*sargs, getstdout=True)
                    # official repository 애서만 가져오도록 수정
                    break
                return r
            elif self.args.command == 'list':
                self.sta.log(StatLogger.LT_2, 'list modules')
                return self.venv.venv_pip('list', getstdout=True)

            # direct command for (pip, python, python setup.py)
            if self.args.command == 'pip':
                self.sta.log(StatLogger.LT_2, 'pip %s' % ' '.join(subargs))
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'py':
                self.sta.log(StatLogger.LT_2, 'py %s' % ' '.join(subargs))
                return self.venv.venv_py(*subargs)
            elif self.args.command == 'setup':
                self.sta.log(StatLogger.LT_2, 'setup %s' % ' '.join(subargs))
                return self.setup(*subargs)
            elif self.args.command == 'list-repository':
                self.sta.log(StatLogger.LT_2, 'list repositories')
                # noinspection PyTypeChecker
                modlist = self._list_modules(startswith=None,
                                             official_only=False,
                                             private_only=False)
                for mod in modlist:
                    print(mod)
                return 0 if bool(modlist) else 1

            ####################################################################
            # 만약 clear* 명령이면 venv를 강제로 true 시킴
            ####################################################################
            if self.args.command in ('clear', 'clear-py',
                                     'clear-all', 'dumpspec', 'submit',
                                     'list-repository') \
                    and not self.args.venv:
                self.args.venv = True  # 그래야 아래  _check_pkg에서 폴더 옮김
            self._check_pkg()
            self._get_setup_config()

            ####################################################################
            # ppm functions
            ####################################################################
            if self.args.command == 'clear':
                self.sta.log(StatLogger.LT_2, 'clear')
                return self._clear()
            elif self.args.command == 'clear-py':
                self.sta.log(StatLogger.LT_2, 'clear python environment')
                return self._clear_py()
            elif self.args.command == 'clear-all':
                self.sta.log(StatLogger.LT_2, 'clear all')
                self._clear()
                return self._clear_py()
            elif self.args.command == 'dumpspec':
                pass
            elif self.args.command == 'test':
                self.sta.log(StatLogger.LT_2, 'setup test')
                r = self.setup('test')
                print('test is done. success is %s' % (r == 0,))
                return r
            elif self.args.command == 'build':
                self.sta.log(StatLogger.LT_2, 'setup build')
                for pkg in self.BUILD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param, getstdout=True)
                self._dumpspec()
                r = self.setup('bdist_wheel')
                print('build is done. success is %s' % (r == 0,))
                return r
            elif self.args.command == 'submit':
                zf = None
                self.sta.log(StatLogger.LT_2, "submitting plugin candidate file")
                try:
                    if not self.args.submit_key:
                        raise RuntimeError('submit: Invalid submit key')
                    current_wd = os.path.abspath(getattr(self.args, '_cwd_'))
                    parent_wd = os.path.abspath(os.path.join(getattr(self.args, '_cwd_'), '..'))
                    if not os.path.exists(parent_wd):
                        raise RuntimeError('PPM.do: Cannot access parent monitor')
                    zf = os.path.join(parent_wd, '%s.zip' % self.pkgname)
                    shutil.make_archive(zf[:-4], 'zip',
                                        root_dir=os.path.dirname(current_wd),
                                        base_dir=os.path.basename(current_wd))
                    if not os.path.exists(zf):
                        raise RuntimeError('PPM.do: Cannot build zip file "%s" to submit' % zf)
                    req = get_xpath(self.config, '/repository/req')
                    if not req:
                        raise RuntimeError('PPM.do: Cannot submit to "%s"' % req)
                    sdu = SimpleDownUpload(url=req, token=self.args.submit_key)
                    sfl = list()
                    sfl.append(self.pkgname)
                    emstr = self.setup_config.get('author_email', 'unknown email')
                    sfl.append(emstr.replace('@', '-'))
                    sfl.append(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
                    r = sdu.upload(zf, saved_filename='%s.zip' % ' '.join(sfl))
                    if not r:
                        raise RuntimeError('PPM.do: Cannot upload "%s"' % zf)
                    print('Succesfully submitted "%s"' % zf)
                    print('submit is done. success is True')
                    return 0
                finally:
                    if zf and os.path.exists(zf):
                        os.remove(zf)
            elif self.args.command == 'upload':
                self.sta.log(StatLogger.LT_2, "upload plugin file to the private repository")
                for pkg in self.UPLOAD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param)

                pri_reps = get_xpath(self.config, '/private-repositories')
                if not pri_reps:
                    raise RuntimeError('PPM.do: Private repository (private-repositories) '
                                       'is not set at %s' % CONF_NAME)
                pri_rep = None
                if not self.args.repository_name:
                    pri_rep = pri_reps[0]
                else:
                    for pr in pri_reps:
                        if pr.get('name') == self.args.repository_name:
                            pri_rep = pr
                            break
                if not pri_reps:
                    raise RuntimeError('PPM.do: Private repository "%s" is not exists at %s'
                                       % (self.args.repository_name, CONF_NAME))

                pr_url = pri_rep.get('url')
                pr_user = pri_rep.get('username')
                pr_pass = pri_rep.get('password')
                if not pr_url:
                    raise RuntimeError('PPM.do: url of private repository is not set, please '
                                       'check private-repositories at %s' % CONF_NAME)
                if not pr_user:
                    raise RuntimeError('PPM.do: username of private repository is not set, please '
                                       'check private-repositories at %s' % CONF_NAME)
                if not pr_pass:
                    raise RuntimeError('PPM.do: password of private repository is not set, please '
                                       'check private-repositories at %s' % CONF_NAME)
                gl = glob.glob('dist/%s*.whl' % self.pkgname)
                if not gl:
                    raise RuntimeError('PPM.do: Cannot find wheel package file at "%s",'
                                       ' please build first' %
                                       os.path.join(self.basepath, 'dist'))
                pr_wheels = [f for f in gl]
                kwargs = {
                    'url': pr_url,
                    'user': pr_user,
                    'passwd': pr_pass,
                    'wheels': pr_wheels,
                }
                r = self._do_upload(**kwargs)
                print('upload is done. success is %s' % (r == 0,))
                return r

            # else:
            #     raise RuntimeError('PPM.do: Cannot support command "%s"'
            #                        % self.args.command)
        except Exception as err:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
            self.sta.error(''.join(_out))
            self.logger.error(''.join(_out))
            self.logger.error(str(err))
            raise
        finally:
            if self.args.clean:
                self._clear()
            # if self.args.command != 'get':
            #     print('done.')
            self.logger.info('PPM.do: end. %s' % self.args.command)

    # ==========================================================================
    def append_pkg_history(self, pkghistory):
        fl = [f for f in
              glob.glob(os.path.join(self.pkgpath, '**', '__init__.py'),
                        recursive=True)]
        for d in map(os.path.dirname, fl):
            d = "'%s'" % d.replace(os.path.sep, '.')
            if d not in pkghistory:
                pkghistory.append(d)

    # ==========================================================================
    def _install_precompiled_wheel(self):
        for whl in glob.glob('%s%s*.whl' % (self.pkgpath, os.path.sep)):
            r = self.venv.venv_pip('install', whl,
                                   *self.ndx_param, getstdout=True)
            if r != 0:
                raise RuntimeError('PPM._install_precompiled_wheel: Error in installing "%s"' % whl)

    # ==========================================================================
    def _install_requirements(self):
        self._install_precompiled_wheel()
        requirements_txt = os.path.join(self.pkgpath, 'requirements.txt')
        if not os.path.exists(requirements_txt):
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
        r = self.venv.venv_pip('install', '-r', requirements_txt,
                               *self.ndx_param, getstdout=True)
        if r != 0:
            raise RuntimeError('PPM._install_requirements: Error in installing "%s"' % requirements_txt)
        return requirements_txt

    # ==========================================================================
    def setup(self, *args):
        self.logger.info('PPM.setup: starting...')
        supath = 'setup.py'
        keywords = self.setup_config.get('keywords', [])
        for kw in self.pkgname.split('.'):
            if kw not in keywords:
                keywords.append(kw)
        requirements_txt = self._install_requirements()

        pkghistory = []
        eles = self.pkgname.split('.')
        for i in range(len(eles)):
            pkghistory.append("'%s'" % '.'.join(eles[0:i+1]))
        # pkghistory.append(self.pkgname)
        classifiers = self.setup_config.get('classifiers', [])
        for c in self.CLASSIFIERS:
            if c not in classifiers:
                classifiers.append(c)
        classifiers_str = '\n'.join(
            ["        '%s'," % c for c in sorted(classifiers)])
        self.append_pkg_history(pkghistory)
        if sys.platform == 'win32':
            requirements_txt = requirements_txt.replace('\\', '\\\\')
        # for package_data
        package_data = self.setup_config.get('package_data',
                                             "{%s: ['icon.*']}" % self.pkgname)
        if self.DUMPSPEC_JSON not in package_data[self.pkgname]:
            package_data[self.pkgname].append(self.DUMPSPEC_JSON)
        with open(supath, 'w') as ofp:
            setup_str = '''
import unittest
from setuptools import setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession


################################################################################
def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('{pkgname}',
                                      pattern='test*.py')
    return test_suite


################################################################################
# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("{requirements_txt}", session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='{pkgname}',
    test_suite='setup.my_test_suite',
    packages=[
        {pkghistory}
    ],
    version='{version}',
    description='{description}',
    author='{author}',
    author_email='{author_email}',
    url='{url}',
    license='{license}',
    keywords={keywords},
    platforms={platforms},
    install_requires=reqs,
    python_requires='>=3.6',
    package_data={package_data},
    zip_safe=False,
    classifiers=[
{classifiers}
    ],
    entry_points={{
        'console_scripts': [
            '{pkgname}={pkgname}:main',
        ],
    }},
    include_package_data=True,
)
'''.format(
                pkghistory=','.join(pkghistory),
                requirements_txt=requirements_txt,
                pkgname=self.pkgname,
                version=self.setup_config.get('version', '0.1.0'),
                description=self.setup_config.get('description', 'description'),
                author=self.setup_config.get('author', 'author'),
                author_email=self.setup_config.get('author_email', 'author_email'),
                url=self.setup_config.get('url', 'url'),
                license=self.setup_config.get('license', 'Proprietary License'),
                keywords=keywords,
                platforms=str(self.setup_config.get('platforms', [])),
                package_data=package_data,
                classifiers=classifiers_str,
            )
            ofp.write(setup_str)
            self.logger.debug('PPM.setup: %s=<%s>' % (supath, setup_str))
        # for setup.cfg
        sucpath = 'setup.cfg'
        _license = ''
        if os.path.exists(os.path.join(self.pkgpath, 'LICENSE.txt')):
            _license = "license_files = %s%sLICENSE.txt" \
                      % (self.pkgpath, os.path.sep)
        readme = ''
        if os.path.exists(os.path.join(self.pkgpath, 'README.md')):
            readme = "description-file = %s%sREADME.md" \
                      % (self.pkgpath, os.path.sep)
        with open(sucpath, 'w') as ofp:
            sucstr = '''
[metadata]
# license_files = LICENSE.txt
{license}
# description-file = README.md
{readme}
'''.format(license=_license, readme=readme)
            ofp.write(sucstr)
            self.logger.debug('PPM.setup: %s=<%s>' % (sucpath, sucstr))
        # instead use package_data
        # if os.path.exists(os.path.join(self.pkgpath, 'MANIFEST.in')):
        #     shutil.copy(os.path.join(self.pkgpath, 'MANIFEST.in'), supath)

        r = self.venv.venv_py(supath, *args, getstdout=True)
        self.logger.info('PPM.setup: end.')
        return r


################################################################################
def get_repository_env():
    cf = CONF_PATH
    if not os.path.exists(cf):
        with open(cf, 'w') as ofp:
            ofp.write(_conf_last_contents)
    with open(cf) as ifp:
        if yaml.__version__ >= '5.1':
            # noinspection PyUnresolvedReferences
            dcf = yaml.load(ifp, Loader=yaml.FullLoader)
        else:
            dcf = yaml.load(ifp)
    need_conf_upgrade = False
    if 'version' not in dcf:
        need_conf_upgrade = True
    elif ver_compare(dcf['version'], _conf_last_version) < 0:
        need_conf_upgrade = True
    if need_conf_upgrade:
        with open(cf, 'w') as ofp:
            ofp.write(_conf_last_contents)
        with open(cf) as ifp:
            if yaml.__version__ >= '5.1':
                # noinspection PyUnresolvedReferences
                dcf = yaml.load(ifp, Loader=yaml.FullLoader)
            else:
                dcf = yaml.load(ifp)
    return dcf


################################################################################
def start_pbtail(g_dir):
    if sys.platform != 'win32':
        return False
    exe_f = g_dir + r'\Release\argos-pbtail.exe'
    if not os.path.exists(exe_f):
        return False
    global pbtail_po
    pbtail_po = subprocess.Popen([exe_f])
    return True


################################################################################
# noinspection PyUnresolvedReferences,PyProtectedMember
def ppm_exe_init(sta):
    tmpdir = None
    try:
        g_dir = os.path.abspath(sys._MEIPASS)
        # c_dir = os.path.abspath(os.path.dirname(sys.executable))
        # argos-pbtail.exe 실행
        start_pbtail(g_dir)
        # 일단은 윈도우만 실행된다고 가정
        set_venv(g_dir + r'\venv')
        # %HOME%argos-rpa.venv 에 Python37-32 에 원본 확인 및 복사
        py_root = os.path.join(str(Path.home()), '.argos-rpa.venv')
        if not os.path.exists(py_root):
            os.makedirs(py_root)
        if not os.path.exists(os.path.join(py_root, 'Python37-32', 'python.exe')):
            sta.log(StatLogger.LT_1, 'Installing Python 3. It may take some time.')
            zip_file = os.path.join(os.path.abspath(sys._MEIPASS), 'Python37-32.zip')
            if not os.path.exists(zip_file):
                raise RuntimeError('Cannot find "%s"' % zip_file)
            tmpdir = tempfile.mkdtemp(prefix='py37-32_')
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            if os.path.exists(os.path.join(py_root, 'Python37-32')):
                shutil.rmtree(os.path.join(py_root, 'Python37-32'))
            shutil.move(os.path.join(tmpdir, 'Python37-32'), py_root)
        # g_dir\venv\pyvenv.cfg 덮어씀
        with open(os.path.join(g_dir, 'venv', 'pyvenv.cfg'), 'w') as ofp:
            ofp.write('''home = %s
include-system-site-packages = false
version = 3.7.3
''' % os.path.join(py_root, 'Python37-32'))
        return 0
    finally:
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)


################################################################################
def _main(argv=None):
    sta = StatLogger(is_clear=True)
    sta.log(StatLogger.LT_1, 'Preparing STU and PAM.')
    if getattr(sys, 'frozen', False):
        ppm_exe_init(sta)
    cwd = os.getcwd()
    try:
        dcf = get_repository_env()
        parser = ArgumentParser(
            description='''ARGOS-LABS Plugin Package Manager

This manager use private PyPI repository.
set {conf_path} as follows:

{conf_contents}

* repository is the main plugin modules's store
  * url is the url of ARGOS RPA+ main pypi module
  NB) ARGOS RPA+ main module is not allowed to upload directly
      but submit first and then ARGOS team to decide 
* private-repositories are the list of user's private plugin modules's store
  * name is the name of private repository (for example "internal", "external") 
  * url is the url of pypi module
  * username is the user name at pypi repository
  * password is the user password at pypi repository
  NB) username and password is only needed for upload
      upload is only valid for private repositories
'''.format(conf_path=CONF_PATH, conf_contents=_conf_contents_dict[_conf_last_version]), formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--new-py', action='store_true',
                            help='making new python venv environment at py.%s' %
                            sys.platform)
        parser.add_argument('--venv', action='store_true',
                            help='if set use package top py.%s for virtual env.'
                                 ' If not set. Use system python instead.'
                                 % sys.platform)
        parser.add_argument('--self-upgrade', '-U', action='store_true',
                            help='If set this flag self upgrade this ppm.')
        parser.add_argument('--clean', '-c', action='store_true',
                            help='clean all temporary folders, etc.')
        parser.add_argument('--verbose', '-v', action='count', default=0,
                            help='verbose output eg) -v, -vv, -vvv, ...')
        parser.add_argument('--pr-user',
                            help="user id for private plugin repository command")
        parser.add_argument('--pr-user-pass',
                            help="user passwd for private plugin repository command")
        parser.add_argument('--pr-user-auth',
                            help="user authentication for private plugin repository command, usually this is for program")
        parser.add_argument('--on-premise', action='store_true',
                            help="If this flag is set applied to on-premise environment")

        subps = parser.add_subparsers(help='ppm command help', dest='command')
        ########################################################################
        # ppm functions
        ########################################################################
        _ = subps.add_parser('test', help='test this module')
        _ = subps.add_parser('build', help='build this module')
        ss = subps.add_parser('submit', help='submit to upload server')
        _ = ss.add_argument('--submit-key',
                            help="token key to submit")
        sp = subps.add_parser('upload', help='upload this module to pypi server')
        sp.add_argument('repository_name', nargs='?',
                        help="repository name from the list of private repositories. "
                             "If not specified then first item from private-repositories list.")
        _ = subps.add_parser('clear', help='clear all temporary folders')
        _ = subps.add_parser('clear-py',
                             help='clear py.%s virtual environment'
                                  % sys.platform)
        _ = subps.add_parser('clear-all',
                             help='clear all temporary folders and '
                                  'virtual environment')

        ########################################################################
        # get command
        ########################################################################
        sp = subps.add_parser('get', help='get command')
        sp.add_argument('get_cmd', metavar='get_sub_cmd',
                        choices=['repository', 'trusted-host', 'private'],
                        help="get command {'repository', 'trusted-host', 'private'}")

        ########################################################################
        # plugin command
        ########################################################################
        sp = subps.add_parser('plugin', help='plugin command')
        sp.add_argument('plugin_cmd',
                        choices=['get', 'dumpspec', 'venv', 'versions', 'dumppi'],
                        help="""plugin command, one of {'get', 'dumpspec', 'venv', 'versions', 'dumppi']}.
   - get : get plugin info for STU
   - dumpspec : get plugin spec for STU
   - venv : making virtual environment for PAM
   - versions : get versions for a plugin
   - dumppi : dump all pypi index for mirroring to a folder
""")
        sp.add_argument('plugin_module',
                        nargs="*",
                        help="plugin module name eg) argoslabs.demo.helloworld or argoslabs.demo.helloworld==1.327.1731")
        # 2019.07.27 : 다음의 plugin 의존적인 --user, --user-auth 옵션은 놔두고
        # --pr-puser, --pr-user-auth 전체 옵션 추가
        sp.add_argument('--user',
                        help="user id for plugin command")
        sp.add_argument('--user-auth',
                        help="user authentication for plugin command")
        sp.add_argument('--pam-id',
                        help="PAM ID(mac addr or uuid) for plugin command")
        sp.add_argument('--startswith',
                        help="module filter to start with")
        sp.add_argument('--official-only', action="store_true",
                        help="do plugin command with official repository only")
        sp.add_argument('--private-only', action="store_true",
                        help="do plugin command with private repository only")
        sp.add_argument('--short-output', action="store_true",
                        help="just print module name and version only")
        sp.add_argument('--flush-cache', action="store_true",
                        help="dumpspec.json will be cached. If this flag is set, clear all cache first.")
        sp.add_argument('--last-only', action="store_true",
                        help="get or dumpspec last version only.")
        sp.add_argument('--with-dumpspec', action="store_true",
                        help="dumpspec.json will be added in result of get result. If --short-output is set, this option is not applied.")
        sp.add_argument('--dumppi-folder',
                        help="module filter to start with")
        sp.add_argument('--outfile',
                        help="filename to save the stdout into a file")
        sp.add_argument('--requirements-txt',
                        help="filename to read modules from requirements.txt instead plugin_module parameters")

        ########################################################################
        # pip command
        ########################################################################
        sp = subps.add_parser('install', help='install module')
        sp.add_argument('subargs', metavar='module', nargs=argparse.REMAINDER,
                        help='module[s] to install')
        sp = subps.add_parser('show', help='show module info')
        sp.add_argument('subargs', metavar='module', nargs=argparse.REMAINDER,
                        help='module[s] to show information')
        sp = subps.add_parser('uninstall', help='uninstall module')
        sp.add_argument('subargs', metavar='module', nargs=argparse.REMAINDER,
                        help='module[s] to uninstall')
        sp = subps.add_parser('search', help='search keywords')
        sp.add_argument('subargs', metavar='keyword', nargs=argparse.REMAINDER,
                        help='search module which have keywords')
        # sp = subps.add_parser('dumpspec', help='dumpspec keywords')
        # sp.add_argument('modulename',
        #                 help='dumpspec module which have modulename')
        _ = subps.add_parser('list', help='list installed module')
        _ = subps.add_parser('list-repository',
                             help='list all modules at remote')

        ########################################################################
        # direct command
        ########################################################################
        sp = subps.add_parser('pip', help='pip command')
        sp.add_argument('subargs', metavar='pip-arguments',
                        nargs=argparse.REMAINDER,
                        help='pip arguments (if option is first needed then '
                             'use pass first)')
        sp = subps.add_parser('py', help='python command')
        sp.add_argument('subargs', metavar='python-arguments',
                        nargs=argparse.REMAINDER,
                        help='python arguments (if option is first needed then '
                             'use pass first)')
        sp = subps.add_parser('setup', help='setup command with setup.yaml')
        sp.add_argument('subargs', metavar='setup-arguments',
                        nargs=argparse.REMAINDER,
                        help='setup arguments (if option is first needed then '
                             'use pass first)')
        # sys.stderr.write('<<SYS.argv="%s">>' % sys.argv)

        args = parser.parse_args(args=argv)
        setattr(args, '_cwd_', cwd)
        if args.verbose > 0:
            print(str(args).replace('Namespace', 'Arguments'))
        if not args.command:
            sys.stderr.write('Need command for ppm.\n')
            parser.print_help()
            return False
        else:
            if os.path.exists(OUT_PATH):
                os.remove(OUT_PATH)
            if os.path.exists(ERR_PATH):
                os.remove(ERR_PATH)
            # loglevel = logging.INFO if args.verbose <= 0 else logging.DEBUG
            loglevel = logging.DEBUG
            try:
                logger = get_logger(LOG_PATH, loglevel=loglevel)
                _venv = VEnv(args, logger=logger)
                ppm = PPM(_venv, args, dcf, logger=logger, sta=sta)
                return ppm.do()
            finally:
                logging.shutdown()
    finally:
        sta.log(StatLogger.LT_1, 'Preparing STU and PAM is done.')
        global pbtail_po
        if pbtail_po is not None:
            pbtail_po.wait()
            # pbtail_po.terminate()
            StatLogger().clear()
        os.chdir(cwd)


################################################################################
def main(argv=None):
    try:
        r = _main(argv)
        sys.exit(r)
    except Exception as err:
        _exc_info = sys.exc_info()
        _out = traceback.format_exception(*_exc_info)
        del _exc_info
        sys.stderr.write('%s\n' % ''.join(_out))
        sys.stderr.write('%s\n' % str(err))
        sys.stderr.write('  use -h option for more help\n')
        sys.exit(9)
