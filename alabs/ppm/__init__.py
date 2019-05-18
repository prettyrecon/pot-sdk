#!/usr/bin/env python
# coding=utf8
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
#  * [2019/05/17]
#     - python 3.6.3 에서 setuptools 를 최신 것으로 update 해야하는 상황 발생
#  * [2019/05/04]
#     - 특정 plugin의 버전목록 구하기 기능 추가
#  * [2019/05/01]
#     - 사용자 별 dumpspec 기능 추가
#  * [2019/04/29]
#     - plugin venv command 추가
#     - plugin command 에서 버전 목록을 가장 최신 버전부터 소팅
#  * [2019/04/24]
#     - plugin commands 추가
#  * [2019/04/22]
#     - dumpspec.json 을 alabs.ppm build 에서 wheel을 만들기 전에 포함되도록
#     - 이후 해당 dumpspec을 가져오는 것은
#     pip download argoslabs.terminal.sshexp --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com --dest=C:\tmp\pkg --no-deps
#     pip download argoslabs.demo.helloworld==1.327.1731 --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com --dest=C:\tmp\pkg --no-deps
#     위의 명령어로 해당 패키지만 다운받아 unzip 하여 dumpspec.json 을 추출하여 특정 dumpspec.json 뽑도록
#  * [2019/04/03]
#     - check empty 'private-repositories'
#  * [2019/03/27]
#     - search 에서는 --extra-index-url 등이 지원 안되는 문제
#  * [2019/03/22~2019/03/26]
#     - PPM.do 에서 return 값을 실제 프로세스 returncode를 리턴 0-정상
#     - submit 에서 upload 서버로 올림
#  * [2019/03/20]
#     - .argos-rpa.conf 애 private-repositories 목록 추가
#     - 기존 register => submit 변경
#  * [2019/03/06]
#     - dumpspec 추가
#  * [2019/03/05]
#     - add package_data
#  * [2018/11/28]
#     - Linux 테스트 OK
#  * [2018/11/27]
#     - 윈도우 테스트 OK
#  * [2018/10/31]
#     - 본 모듈 작업 시작
################################################################################
import os
import sys
# noinspection PyPackageRequirements
import yaml
import glob
import copy
import json
import shutil
import logging
import zipfile
import requests
import argparse
import datetime
import tempfile
import traceback
import subprocess
import requirements
import urllib3
from urllib.parse import quote
from alabs.common.util.vvjson import get_xpath
from alabs.common.util.vvlogger import get_logger
from alabs.common.util.vvupdown import SimpleDownUpload
from functools import cmp_to_key
# from tempfile import gettempdir
if '%s.%s' % (sys.version_info.major, sys.version_info.minor) < '3.3':
    raise EnvironmentError('Python Version must greater then "3.3" '
                           'which support venv')
else:
    from urllib.parse import urlparse
    from pathlib import Path
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

################################################################################
__all__ = ['main']


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
    def make_venv(self, isdelete=True):
        if not self.use:
            return 9
        if os.path.isdir(self.root) and isdelete:
            shutil.rmtree(self.root)

        self.logger.info("Now making venv %s ..." % self.root)
        cmd = [
            '"%s"' % os.path.abspath(sys.executable),
            '-m',
            'venv',
            self.root
        ]
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
        r = self.venv_pip('install', '--upgrade', 'pip')
        if r == 0:
            r = self.venv_pip('install', '--upgrade', 'setuptools')
        return r

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
            cmd += args
            self.logger.debug('VEnv.venv_py: cmd="%s"' % ' '.join(cmd))
            # Windows의 python.exe -m 등의 명령어가 shell 모드에서 정상 동작함

            tmpdir = tempfile.mkdtemp(prefix='venv_py_')
            out_path = os.path.join(tmpdir, 'stdout.txt')
            err_path = os.path.join(tmpdir, 'stderr.txt')

            with open(out_path, 'w', encoding='utf-8') as out_fp, \
                    open(err_path, 'w', encoding='utf-8') as err_fp:

                po = subprocess.Popen(' '.join(cmd), shell=True,
                                      stdout=out_fp, stderr=err_fp)
                po.wait()

            if kwargs['outfile']:
                shutil.copy2(out_path, kwargs['outfile'])
            if kwargs['getstdout']:
                with open(out_path) as ifp:
                    print(ifp.read())

            with open(out_path) as ifp:
                try:
                    out = ifp.read().encode('utf-8')
                except UnicodeDecodeError as e:
                    out = ifp.read().encode(e.encoding)
                if out:
                    self.logger.debug('VEnv.venv_py: stdout=<%s>' % out.decode('utf-8'))
            with open(err_path) as ifp:
                try:
                    err = ifp.read().encode('utf-8')
                except UnicodeDecodeError as e:
                    err = ifp.read().encode(e.encoding)
                if err:
                    self.logger.debug('VEnv.venv_py: stderr=<%s>' % err.decode('utf-8'))
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
        return self.venv_py('-m', 'pip', *args, **kwargs)


################################################################################
class PPM(object):
    # ==========================================================================
    BUILD_PKGS = [
        'wheel',
    ]
    UPLOAD_PKGS = [
        'twine',
    ]
    LIST_PKGS = [
        'beautifulsoup4',
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
    EXCLUDE_PKGS = ('alabs.ppm', 'alabs.common')

    # ==========================================================================
    def __init__(self, venv, args, config, logger=None):
        self.venv = venv
        self.args = args
        self.config = config    # .argos-rpa.conf (yaml)
        if logger is None:
            logger = get_logger(LOG_PATH)
        self.logger = logger
        # for internal
        self.pkgname = None
        self.pkgpath = None
        self.basepath = None
        self.setup_config = None
        self.indices = []
        self.ndx_param = []

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
                yaml_config = yaml.load(ifp, Loader=yaml.FullLoader)
            else:
                yaml_config = yaml.load(ifp)
            if 'setup' not in yaml_config:
                raise RuntimeError('PPM._get_setup_config: "setup" attribute must be exists in setup.yaml')
            self.setup_config = yaml_config['setup']

    # ==========================================================================
    def _get_indices(self):
        self.indices = []
        self.ndx_param = []
        url = get_xpath(self.config, '/repository/url')
        if not url:
            raise RuntimeError('PPM._get_indices: Invalid repository.url from %s' % CONF_NAME)
        self.indices.append(url)
        self.ndx_param.append('--index')
        self.ndx_param.append(url)
        self.ndx_param.append('--trusted-host')
        self.ndx_param.append(self._get_host_from_index(url))
        pr = None
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
        for pkg in self.LIST_PKGS:
            # self.venv.venv_pip('install', pkg, *self.ndx_param)
            self.venv.venv_pip('install', pkg)
        import urllib.request
        import urllib.parse
        # noinspection PyUnresolvedReferences,PyPackageRequirements
        from bs4 import BeautifulSoup
        for i, url in enumerate(self.indices):
            if i == 0 and private_only:
                continue
            if i > 0 and official_only:
                break
            web_url = url + '/packages/'
            with urllib.request.urlopen(web_url) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
            for x in soup.find_all('a'):
                # pprint(x.text)
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
    def _dumpspec_json(self, modname, version=None):
        # pip download argoslabs.demo.helloworld==1.327.1731
        # --index http://pypi.argos-labs.com:8080 --trusted-host=pypi.argos-labs.com
        # --dest=C:\tmp\pkg --no-deps
        mname = modname
        if version:
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
            raise RuntimeError('PPM._dumpspec_json: Cannot get plugin wheel file "%s"' % mfilename)
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
        # curl -X GET --header 'Accept: application/json' 'https://api-chief.argos-labs.com/plugin/api/v1.0/users/seonme%40vivans.net/plugins'
        url = 'https://api-chief.argos-labs.com/plugin/api/v1.0/users/%s/plugins' \
              % quote(self.args.user)
        headers = {
            # 'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'
        }
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code // 10 != 20:
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
        # print(md)
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
        self.args.user = None
        return True

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
            r = new_venv.venv_pip('install', '-r', requirements_txt,
                                  *self.ndx_param)
            if r == 0:
                outfile = os.path.join(new_d, 'freeze.txt')
                new_venv.venv_pip('freeze', outfile=outfile)
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
            return True
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
    def do_plugin(self):
        ofp = sys.stdout
        modd = {}
        modds = {}
        tmpdir = tempfile.mkdtemp(prefix='do_plugin_')
        try:
            self.logger.info('PPM.do_plugin: starting... %s' % self.args.plugin_cmd)
            ####################################################################
            # PAM용 환경설정 만들기
            ####################################################################
            if self.args.plugin_cmd == 'venv':
                if not (self.args.plugin_module or self.args.requirements_txt):
                    raise RuntimeError('PPM.do_plugin: plugin-modules parameters or --requirements-txt option must be specifiyed.')
                if self.args.requirements_txt and not os.path.exists(self.args.requirements_txt):
                    raise RuntimeError('PPM.do_plugin: --requirements-txt "%s" file does not exists.' % self.args.requirements_txt)
                # ~/.argos-rpa.venv/ 폴더 안에 YYYMMDD-HHMMSS 로 가상환경을 만듦
                venv_d = os.path.join(str(Path.home()), '.argos-rpa.venv')
                if not os.path.exists(venv_d):
                    os.makedirs(venv_d)
                modspec = self._get_modspec(tmpdir)
                glob_f = os.path.join(venv_d, '**', 'freeze.json')
                match_list = list()
                for f in glob.glob(glob_f):
                    with open(f) as ifp:
                        freeze_d = json.load(ifp)
                    if self._is_conflict(freeze_d, modspec):
                        continue
                    match_cnt = self._count_satisfy(freeze_d, modspec)
                    get_venv = os.path.dirname(os.path.abspath(f))
                    match_list.append((match_cnt, get_venv))
                # 설치가능한 venv가 발견되지 않았다면, 새로 만듦
                if not match_list:
                    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    get_venv = os.path.join(venv_d, now)
                else:  # 아니면 가장 많이 매칭된 것을 찾아 이용
                    match_list.sort(key=lambda x: x[0])
                    get_venv = match_list[-1][1]
                self._get_venv(get_venv)
                print(get_venv)
                return 0

            # 만약 CHIEF에 특정 사용자별 dumpspec 결과를 가져오려면 우선
            # 해당 모듈 리스트를 구함
            if self.args.plugin_cmd == 'dumpspec' and self.args.user:
                self._dumpspec_user(tmpdir)

            # 나머지는 CHIEF, STU용
            # 우선은 pypi 서버에서 해당 모듈 목록을 구해와서
            # 해당 모듈(wheel)만 다운로드하여 포함되어 있는 dumpspec.json을
            # 가져오는데 tempdir에 dumpspec-modulename-version.json 식으로 캐슁
            if self.args.outfile:
                ofp = open(self.args.outfile, 'w', encoding='utf-8')
            if self.args.flush_cache:
                self._dumpspec_json_clear_cache()
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
                rd = self._cmd_modspec(modd, modspec)
                if not self.args.short_output:
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
                rd = self._cmd_modspec(modds, modspec, version_attr='plugin_version')
                json.dump(rd, ofp)
            return 0
        finally:
            if self.args.outfile:
                ofp.close()
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            self.logger.info('PPM.do_plugin: end. %s' % self.args.plugin_cmd)

    # ==========================================================================
    def do(self):
        try:
            self.logger.info('PPM.do: starting... %s' % self.args.command)
            if hasattr(self.args, 'subargs'):
                subargs = self._check_subargs(self.args.subargs)
            else:
                subargs = []
            self._get_indices()
            # first do actions which do not need virtualenv
            ####################################################################
            # get commond
            ####################################################################
            if self.args.command == 'get':
                if self.args.get_cmd == 'repository':
                    print(self.indices[0])
                elif self.args.get_cmd == 'trusted-host':
                    print(self._get_host_from_index(self.indices[0]))
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
                subargs.insert(0, 'install')
                subargs.extend(self.ndx_param)
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'show':
                subargs.insert(0, 'show')
                subargs.append('--verbose')
                return self.venv.venv_pip(*subargs, getstdout=True)
            elif self.args.command == 'uninstall':
                subargs.insert(0, '-y')
                subargs.insert(0, 'uninstall')
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'search':
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
                return r
            elif self.args.command == 'list':
                return self.venv.venv_pip('list', getstdout=True)

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
                return self._clear()
            elif self.args.command == 'clear-py':
                return self._clear_py()
            elif self.args.command == 'clear-all':
                self._clear()
                return self._clear_py()
            elif self.args.command == 'dumpspec':
                pass
            elif self.args.command == 'test':
                r = self.setup('test')
                print('test is done. success is %s' % (r == 0,))
                return r
            elif self.args.command == 'build':
                for pkg in self.BUILD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param, getstdout=True)
                self._dumpspec()
                r = self.setup('bdist_wheel')
                print('build is done. success is %s' % (r == 0,))
                return r
            elif self.args.command == 'submit':
                zf = None
                try:
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
                    sdu = SimpleDownUpload(host=self.ndx_param[3], token=SimpleDownUpload.static_token)
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
                r = self.venv.venv_py('-m', 'twine', 'upload', 'dist/*',
                                      '--repository-url', pr_url,
                                      '--username', pr_user,
                                      '--password', pr_pass,
                                      stdout=True)
                print('upload is done. success is %s' % (r == 0,))
                return r

            # direct command for (pip, python, python setup.py)
            if self.args.command == 'pip':
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'py':
                return self.venv.venv_py(*subargs)
            elif self.args.command == 'setup':
                return self.setup(*subargs)
            elif self.args.command == 'list-repository':
                # noinspection PyTypeChecker
                modlist = self._list_modules(startswith=None,
                                             official_only=False,
                                             private_only=False)
                for mod in modlist:
                    print(mod)
                return 0 if bool(modlist) else 1
            else:
                raise RuntimeError('PPM.do: Cannot support command "%s"'
                                   % self.args.command)
        except Exception as err:
            _exc_info = sys.exc_info()
            _out = traceback.format_exception(*_exc_info)
            del _exc_info
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
    def _install_requirements(self):
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
            ofp.write('''---
repository:
  url: http://pypi.argos-labs.com:8080
''')
    with open(cf) as ifp:
        if yaml.__version__ >= '5.1':
            dcf = yaml.load(ifp, Loader=yaml.FullLoader)
        else:
            dcf = yaml.load(ifp)
    return dcf


################################################################################
def _main(argv=None):
    cwd = os.getcwd()
    try:
        dcf = get_repository_env()
        parser = ArgumentParser(
            description='''ARGOS-LABS Plugin Package Manager

This manager use private PyPI repository.
set {conf_path} as follows:

---
repository:
  url: http://pypi.argos-labs.com:8080
private-repositories:
  - name: internal
    url: http://10.211.55.2:48080
    username: user
    password: pass
  - name: external
    url: http://pypi.argos-labs.com:8080
    username: user
    password: pass


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
'''.format(conf_path=CONF_PATH),
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--new-py', action='store_true',
                            help='making new python venv environment at py.%s' %
                            sys.platform)
        parser.add_argument('--venv', action='store_true',
                            help='if set use package top py.%s for virtual env.'
                                 ' If not set. Use system python instead.'
                                 % sys.platform)
        parser.add_argument('--clean', '-c', action='store_true',
                            help='clean all temporary folders, etc.')
        parser.add_argument('--verbose', '-v', action='count', default=0,
                            help='verbose output eg) -v, -vv, -vvv, ...')

        subps = parser.add_subparsers(help='ppm command help', dest='command')
        ########################################################################
        # ppm functions
        ########################################################################
        _ = subps.add_parser('test', help='test this module')
        _ = subps.add_parser('build', help='build this module')
        _ = subps.add_parser('submit', help='submit to upload server')
        # TODO : 현재는 붙박이로 키를 넣어서 가져오지만 나중에는 vault 서비스에서 가져오도록 수정
        #  sp.add_argument('submit_key',
        #                 help="token key to submit")
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
                        choices=['repository', 'trusted-host'],
                        help="get command {'repository', 'trusted-host'}")

        ########################################################################
        # plugin command
        ########################################################################
        sp = subps.add_parser('plugin', help='plugin command')
        sp.add_argument('plugin_cmd',
                        choices=['get', 'dumpspec', 'venv', 'versions'],
                        help="plugin command, one of {'get', 'dumpspec', 'venv', 'versions']}")
        sp.add_argument('plugin_module',
                        nargs="*",
                        help="plugin module name eg) argoslabs.demo.helloworld or argoslabs.demo.helloworld==1.327.1731")
        sp.add_argument('--user',
                        help="user id for plugin command")
        sp.add_argument('--user-auth',
                        help="user authentication for plugin command")
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
                venv = VEnv(args, logger=logger)
                ppm = PPM(venv, args, dcf, logger=logger)
                return ppm.do()
            finally:
                logging.shutdown()
    finally:
        os.chdir(cwd)


################################################################################
def main(argv=None):
    try:
        r = _main(argv)
        sys.exit(r)
    except Exception as err:
        # _exc_info = sys.exc_info()
        # _out = traceback.format_exception(*_exc_info)
        # del _exc_info
        # sys.stderr.write('%s\n' % ''.join(_out))
        sys.stderr.write('%s\n' % str(err))
        sys.stderr.write('  use -h option for more help\n')
        sys.exit(9)
