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
import shutil
import argparse
import datetime
import traceback
import subprocess
from alabs.common.util.vvjson import get_xpath
from alabs.common.util.vvupdown import SimpleDownUpload
if '%s.%s' % (sys.version_info.major, sys.version_info.minor) < '3.3':
    raise EnvironmentError('Python Version must greater then "3.3" '
                           'which support venv')
else:
    from urllib.parse import urlparse
    from pathlib import Path


################################################################################
__all__ = ['main']


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
    def __init__(self, args, root='py.%s' % sys.platform):
        self.args = args
        # home 폴더 아래에 py.win32, py.darwin, py.linux 처럼 만듦
        self.root = os.path.join(str(Path.home()), root)
        self.use = args.venv
        # for internal
        self.py = None
        self.check_environments()

    # ==========================================================================
    @staticmethod
    def check_python():
        if '%s.%s' % (sys.version_info.major, sys.version_info.minor) < '3.3':
            raise EnvironmentError('Python Version must greater then "3.3" '
                                   'which support venv')
        return 0

    # ==========================================================================
    def check_environments(self):
        self.check_python()

    # ==========================================================================
    def clear(self):
        if os.path.isdir(self.root):
            shutil.rmtree(self.root)
        return 0

    # ==========================================================================
    def make_venv(self, isdelete=True):
        if not self.use:
            return 9
        if os.path.isdir(self.root) and isdelete:
            shutil.rmtree(self.root)

        print("Now making venv %s ..." % self.root)
        cmd = [
            '"%s"' % os.path.abspath(sys.executable),
            '-m',
            'venv',
            self.root
        ]
        # python -m venv ... 명령은 shell 에서 해야 정상 동작함
        po = subprocess.Popen(' '.join(cmd), shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sys.stdout.write('%s\n' % po.stdout.read().decode('utf8'))
        sys.stderr.write('%s\n' % po.stderr.read().decode('utf8'))
        po.wait()
        if po.returncode != 0:
            raise RuntimeError('making venv %s: error %s'
                               % (' '.join(cmd), po.returncode))
        print("making venv %s success!" % self.root)
        return self.venv_pip('install', '--upgrade', 'pip')

    # ==========================================================================
    def check_venv(self):
        if not self.use:
            py = os.path.abspath(sys.executable)
            self.py = py
            return py

        if not os.path.isdir(self.root):
            self.make_venv()
        if sys.platform == 'win32':
            py = os.path.abspath(os.path.join(self.root,
                                              'Scripts', 'python.exe'))
        else:
            py = os.path.abspath(os.path.join(self.root, 'bin', 'python'))
        if not os.path.exists(py):
            raise RuntimeError('Cannot find python "%s"' % py)
        self.py = py
        return py

    # ==========================================================================
    def get_venv(self):
        return self.check_venv()

    # ==========================================================================
    def venv_py(self, *args, **kwargs):
        raise_error = False
        if 'raise_error' in kwargs:
            raise_error = bool(kwargs['raise_error'])
        getstdout = False
        if 'getstdout' in kwargs:
            getstdout = bool(kwargs['getstdout'])
        cmd = [
            self.get_venv(),
        ]
        cmd += args
        if self.args.verbose >= 2:
            print('%s venv_py cmd="%s"' % ('*'*50, ' '.join(cmd)))
        # Windows의 python.exe -m 등의 명령어가 shell 모드에서 정상 동작함
        if not getstdout:
            po = subprocess.Popen(' '.join(cmd), shell=True)
            po.wait()
        else:
            po = subprocess.Popen(' '.join(cmd), shell=True,
                                  stdout=subprocess.PIPE)
            if sys.platform == 'win32':
                print(po.stdout.read().decode('cp949'))
            else:
                print(po.stdout.read().decode('utf-8'))
            po.wait()
        if po.returncode != 0 and raise_error:
            raise RuntimeError('venv command "%s": error %s'
                               % (' '.join(cmd), po.returncode))
        if self.args.verbose >= 1:
            print('%s venv_py return %s' % ('*'*50, po.returncode))
        return po.returncode

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

    # ==========================================================================
    def __init__(self, venv, args, config):
        self.venv = venv
        self.args = args
        self.config = config    # .argos-rpa.conf (yaml)
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
                raise RuntimeError('Cannot find package (__init__.py)')
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
            raise RuntimeError('Cannot find package path for "%s"'
                               % self.pkgpath)
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
            raise IOError('Cannot find "%s" for setup' % yamlpath)
        with open(yamlpath) as ifp:
            yaml_config = yaml.load(ifp)
            if 'setup' not in yaml_config:
                raise RuntimeError('"setup" attribute must be '
                                   'exists in setup.yaml')
            self.setup_config = yaml_config['setup']

    # ==========================================================================
    def _get_indices(self):
        self.indices = []
        self.ndx_param = []
        url = get_xpath(self.config, '/repository/url')
        if not url:
            raise RuntimeError('Invalid repository.url from .argos-rpa.conf')
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
        return self.indices

    # ==========================================================================
    @staticmethod
    def _get_host_from_index(url):
        return urlparse(url).netloc.split(':')[0]

    # ==========================================================================
    def do(self):
        try:
            if hasattr(self.args, 'subargs'):
                subargs = self._check_subargs(self.args.subargs)
            else:
                subargs = []
            self._get_indices()
            # first do actions which do not need virtualenv
            # get commond
            if self.args.command == 'get':
                if self.args.get_config == 'repository':
                    print(self.indices[0])
                elif self.args.get_config == 'trusted-host':
                    print(self._get_host_from_index(self.indices[0]))
                return 0
            print('start %s ...' % self.args.command)
            # pip commond
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

            # 만약 clear* 명령이면 venv를 강제로 true 시킴
            if self.args.command in ('clear', 'clear-py',
                                     'clear-all', 'dumpspec', 'submit') \
                    and not self.args.venv:
                self.args.venv = True  # 그래야 아래  _check_pkg에서 폴더 옮김
            self._check_pkg()
            self._get_setup_config()
            # ppm functions
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
                return self.setup('test')
            elif self.args.command == 'build':
                for pkg in self.BUILD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param)
                return self.setup('bdist_wheel')
            elif self.args.command == 'submit':
                zf = None
                try:
                    current_wd = os.path.abspath(getattr(self.args, '_cwd_'))
                    parent_wd = os.path.abspath(os.path.join(getattr(self.args, '_cwd_'), '..'))
                    if not os.path.exists(parent_wd):
                        raise RuntimeError('Cannot access parent monitor')
                    zf = os.path.join(parent_wd, '%s.zip' % self.pkgname)
                    shutil.make_archive(zf[:-4], 'zip',
                                        root_dir=os.path.dirname(current_wd),
                                        base_dir=os.path.basename(current_wd))
                    if not os.path.exists(zf):
                        raise RuntimeError('Cannot build zip file "%s" to submit' % zf)
                    sdu = SimpleDownUpload(host=self.ndx_param[3], token=SimpleDownUpload.static_token)
                    sfl = list()
                    sfl.append(self.pkgname)
                    emstr = self.setup_config.get('author_email', 'unknown email')
                    sfl.append(emstr.replace('@', '-'))
                    sfl.append(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
                    r = sdu.upload(zf, saved_filename='%s.zip' % ' '.join(sfl))
                    if not r:
                        raise RuntimeError('Cannot upload "%s"' % zf)
                    print('Succesfully submitted "%s"' % zf)
                    return 0
                finally:
                    if zf and os.path.exists(zf):
                        os.remove(zf)
            elif self.args.command == 'upload':
                for pkg in self.UPLOAD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param)

                pri_reps = get_xpath(self.config, '/private-repositories')
                if not pri_reps:
                    raise RuntimeError('Private repository (private-repositories) '
                                       'is not set at .argos-rpa.conf,')
                pri_rep = None
                if not self.args.repository_name:
                    pri_rep = pri_reps[0]
                else:
                    for pr in pri_reps:
                        if pr.get('name') == self.args.repository_name:
                            pri_rep = pr
                            break
                if not pri_reps:
                    raise RuntimeError('Private repository "%s" is not exists '
                                       'at .argos-rpa.conf,' % self.args.repository_name)

                pr_url = pri_rep.get('url')
                pr_user = pri_rep.get('username')
                pr_pass = pri_rep.get('password')
                if not pr_url:
                    raise RuntimeError('url of private repository is not set, please '
                                       'check private-repositories at .argos-rpa.conf')
                if not pr_user:
                    raise RuntimeError('username of private repository is not set, please '
                                       'check private-repositories at .argos-rpa.conf')
                if not pr_pass:
                    raise RuntimeError('password of private repository is not set, please '
                                       'check private-repositories at .argos-rpa.conf')
                gl = glob.glob('dist/%s*.whl' % self.pkgname)
                if not gl:
                    raise RuntimeError('Cannot find wheel package file at "%s",'
                                       ' please build first' %
                                       os.path.join(self.basepath, 'dist'))
                return self.venv.venv_py('-m', 'twine', 'upload', 'dist/*',
                                         '--repository-url', pr_url,
                                         '--username', pr_user,
                                         '--password', pr_pass,
                                         stdout=True)

            # direct command for (pip, python, python setup.py)
            if self.args.command == 'pip':
                return self.venv.venv_pip(*subargs)
            elif self.args.command == 'py':
                return self.venv.venv_py(*subargs)
            elif self.args.command == 'setup':
                return self.setup(*subargs)
            elif self.args.command == 'list-repository':
                for pkg in self.LIST_PKGS:
                    self.venv.venv_pip('install', pkg, *self.ndx_param)
                import urllib.request
                import urllib.parse
                # noinspection PyUnresolvedReferences,PyPackageRequirements
                from bs4 import BeautifulSoup
                from pprint import pprint

                web_url = self.args.repository + '/packages/'
                with urllib.request.urlopen(web_url) as response:
                    html = response.read()
                    soup = BeautifulSoup(html, 'html.parser')
                for x in soup.find_all('a'):
                    pprint(x.text)
                return 0
            else:
                raise RuntimeError('Cannot support command "%s"'
                                   % self.args.command)
        finally:
            if self.args.clean:
                self._clear()
            if self.args.command != 'get':
                print('done.')

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
    def setup(self, *args):
        supath = 'setup.py'
        keywords = self.setup_config.get('keywords', [])
        for kw in self.pkgname.split('.'):
            if kw not in keywords:
                keywords.append(kw)
        requirements_txt = os.path.join(self.pkgpath, 'requirements.txt')
        if not os.path.exists(requirements_txt):
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
        r = self.venv.venv_pip('install', '-r', requirements_txt,
                               *self.ndx_param)
        if r != 0:
            raise RuntimeError('Error in installing "%s"' % requirements_txt)
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
        with open(supath, 'w') as ofp:
            ofp.write('''
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
                package_data=self.setup_config.get('package_data', '{}'),
                classifiers=classifiers_str,
            ))
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
            ofp.write('''
[metadata]
# license_files = LICENSE.txt
{license}
# description-file = README.md
{readme}
'''.format(license=_license, readme=readme))
        # instead use package_data
        # if os.path.exists(os.path.join(self.pkgpath, 'MANIFEST.in')):
        #     shutil.copy(os.path.join(self.pkgpath, 'MANIFEST.in'), supath)

        return self.venv.venv_py(supath, *args)


################################################################################
def get_repository_env():
    cf = os.path.join(str(Path.home()), '.argos-rpa.conf')
    with open(cf) as ifp:
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
set {home}{sep}.argos-rpa.conf as follows:

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
'''.format(home=str(Path.home()), sep=os.path.sep),
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--new-py', action='store_true',
                            help='making new python venv environment at py.%s' %
                            sys.platform)
        parser.add_argument('--venv', action='store_true',
                            help='if set use package top py.%s for virtual env.'
                                 ' If not set. Use system python instead.'
                                 % sys.platform)
        # .argos-rpa.conf 로면 설정하도록 수정
        # parser.add_argument('--repository', '-r', nargs='?',
        #                     help='set url for private repository')
        # parser.add_argument('--username', nargs='?',
        #                     help='user name for private repository')
        # parser.add_argument('--password', nargs='?',
        #                     help='password for private repository')
        parser.add_argument('--clean', '-c', action='store_true',
                            help='clean all temporary folders, etc.')
        parser.add_argument('--verbose', '-v', action='count', default=0,
                            help='verbose output eg) -v, -vv, -vvv, ...')

        subps = parser.add_subparsers(help='ppm command help', dest='command')
        # ppm functions
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

        # get command
        sp = subps.add_parser('get', help='get configuration')
        sp.add_argument('get_config', metavar='config',
                        choices=['repository', 'trusted-host'],
                        help="get configuration {'repository', 'trusted-host'}")

        # pip command
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
        sp = subps.add_parser('dumpspec', help='dumpspec keywords')
        sp.add_argument('modulename',
                        help='dumpspec module which have modulename')
        _ = subps.add_parser('list', help='list installed module')
        _ = subps.add_parser('list-repository',
                             help='list all modules at remote')

        # direct command
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
            venv = VEnv(args)
            ppm = PPM(venv, args, dcf)
            return ppm.do()
    finally:
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
