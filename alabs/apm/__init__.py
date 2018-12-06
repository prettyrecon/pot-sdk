#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:alabs.apm ARGOS-LABS Plugin Module Manager
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
import shutil
import argparse
import datetime
import traceback
import subprocess
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
        else:
            raise RuntimeWarning('ArgumentParser Exit')


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
        return True

    # ==========================================================================
    def check_environments(self):
        self.check_python()

    # ==========================================================================
    def clear(self):
        if os.path.isdir(self.root):
            shutil.rmtree(self.root)
        return True

    # ==========================================================================
    def make_venv(self, isdelete=True):
        if not self.use:
            return 0
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
class APM(object):
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
        'Build :: Method :: alabs.apm',
        'Build :: Date :: %s' %
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    ]

    # ==========================================================================
    def __init__(self, venv, args):
        self.venv = venv
        self.args = args
        # for internal
        self.pkgname = None
        self.pkgpath = None
        self.basepath = None
        self.rep_param = []

    # ==========================================================================
    def _get_pkgname(self):
        # alabs.demo.helloworld 패키지를 설치하려고 하면, 해당 helloworld 폴더에
        # 들어가서 apm 을 돌림
        if not os.path.exists('__init__.py'):
            # --venv 가 없는 경우도 있으므로 그냥 '.' 을 리턴
            # raise RuntimeError('Cannot find __init__.py file. Please run '
            #                    'apm in python package folder')
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
        return c_cnt > 0

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def _clear_py(self):
        return self.venv.clear()

    # ==========================================================================
    def do(self):
        try:
            if hasattr(self.args, 'subargs'):
                subargs = self._check_subargs(self.args.subargs)
            else:
                subargs = []

            rep_host = urlparse(self.args.repository).netloc.split(':')[0]
            self.rep_param = ['--index', self.args.repository,
                              '--trusted-host', rep_host]
            # first do actions which do not need virtualenv
            # get commond
            if self.args.command == 'get':
                if self.args.get_config == 'repository':
                    print(self.args.repository)
                elif self.args.get_config == 'trusted-host':
                    print(rep_host)
                return True

            print('start %s ...' % self.args.command)
            # pip commond
            if self.args.command == 'install':
                subargs.insert(0, 'install')
                subargs.extend(self.rep_param)
                return self.venv.venv_pip(*subargs) == 0
            elif self.args.command == 'show':
                subargs.insert(0, 'show')
                subargs.append('--verbose')
                return self.venv.venv_pip(*subargs, getstdout=True) == 0
            elif self.args.command == 'uninstall':
                subargs.insert(0, '-y')
                subargs.insert(0, 'uninstall')
                return self.venv.venv_pip(*subargs) == 0
            elif self.args.command == 'search':
                subargs.insert(0, 'search')
                subargs.extend(self.rep_param)
                return self.venv.venv_pip(*subargs, getstdout=True) == 0
            elif self.args.command == 'list':
                return self.venv.venv_pip('list', getstdout=True) == 0

            # 만약 clear* 명령이면 venv를 강제로 true 시킴
            if self.args.command.startswith('clear') and not self.args.venv:
                self.args.venv = True  # 그래야 아래  _check_pkg에서 폴더 옮김
            self._check_pkg()
            # apm functions
            if self.args.command == 'clear':
                return self._clear()
            elif self.args.command == 'clear-py':
                return self._clear_py()
            elif self.args.command == 'clear-all':
                self._clear()
                return self._clear_py()
            elif self.args.command == 'test':
                return self.setup('test') == 0
            elif self.args.command == 'build':
                for pkg in self.BUILD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.rep_param)
                return self.setup('bdist_wheel') == 0
            elif self.args.command == 'register':
                raise NotImplementedError('TODO:register into '
                                          'module upload server '
                                          '(Not yet implemented)')
            elif self.args.command == 'upload':
                for pkg in self.UPLOAD_PKGS:
                    self.venv.venv_pip('install', pkg, *self.rep_param)
                gl = glob.glob('dist/%s*.whl' % self.pkgname)
                if not gl:
                    raise RuntimeError('Cannot find wheel package file at "%s",'
                                       ' please build first' %
                                       os.path.join(self.basepath, 'dist'))
                if not self.args.repository:
                    raise RuntimeError('Private repository is not set, please '
                                       'set --repository option first')
                if not self.args.username:
                    raise RuntimeError('username is not set for Private '
                                       'repository, please set --username '
                                       'option first')
                if not self.args.password:
                    raise RuntimeError('password is not set for Private '
                                       'repository, please set --password '
                                       'option first')
                return self.venv.venv_py('-m', 'twine', 'upload', 'dist/*',
                                         '--repository-url',
                                         self.args.repository,
                                         '--username', self.args.username,
                                         '--password', self.args.password,
                                         stdout=True) == 0

            # direct command for (pip, python, python setup.py)
            if self.args.command == 'pip':
                return self.venv.venv_pip(*subargs) == 0
            elif self.args.command == 'py':
                return self.venv.venv_py(*subargs) == 0
            elif self.args.command == 'setup':
                return self.setup(*subargs) == 0
            elif self.args.command == 'list-repository':
                for pkg in self.LIST_PKGS:
                    self.venv.venv_pip('install', pkg, *self.rep_param)
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
                return True
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
        yamlpath = os.path.join(self.pkgpath, 'setup.yaml')
        if not os.path.exists(yamlpath):
            raise IOError('Cannot find "%s" for setup' % yamlpath)
        with open(yamlpath) as ifp:
            yaml_config = yaml.load(ifp)
            if 'setup' not in yaml_config:
                raise RuntimeError('"setup" attribute must be '
                                   'exists in setup.yaml')
            setup_config = yaml_config['setup']
        supath = 'setup.py'
        keywords = setup_config.get('keywords', [])
        for kw in self.pkgname.split('.'):
            if kw not in keywords:
                keywords.append(kw)
        requirements_txt = os.path.join(self.pkgpath, 'requirements.txt')
        if not os.path.exists(requirements_txt):
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
        r = self.venv.venv_pip('install', '-r', requirements_txt,
                               *self.rep_param)
        if r != 0:
            raise RuntimeError('Error in installing "%s"' % requirements_txt)
        pkghistory = []
        eles = self.pkgname.split('.')
        for i in range(len(eles)):
            pkghistory.append("'%s'" % '.'.join(eles[0:i+1]))
        # pkghistory.append(self.pkgname)
        classifiers = setup_config.get('classifiers', [])
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
    package_data={{}},
    zip_safe=False,
    classifiers=[
{classifiers}
    ],
    entry_points={{
        'console_scripts': [
            '{pkgname}={pkgname}:main',
        ],
    }},
)
'''.format(
                pkghistory=','.join(pkghistory),
                requirements_txt=requirements_txt,
                pkgname=self.pkgname,
                version=setup_config.get('version', '0.1.0'),
                description=setup_config.get('description', 'description'),
                author=setup_config.get('author', 'author'),
                author_email=setup_config.get('author_email', 'author_email'),
                url=setup_config.get('url', 'url'),
                license=setup_config.get('license', 'Proprietary License'),
                keywords=keywords,
                platforms=str(setup_config.get('platforms', [])),
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

        return self.venv.venv_py(supath, *args)


################################################################################
def get_repository_env():
    cf = os.path.join(str(Path.home()), '.apm.conf')
    dcf = {
        'repository': 'http://pypi.argos-labs.com:8080',
        'username': None,
        'password': None,
    }
    if os.path.exists(cf):
        with open(cf) as ifp:
            dcf = yaml.load(ifp)
    v = os.environ.get('APM_REPOSITORY')
    if v:
        dcf['repository'] = v
    v = os.environ.get('APM_USERNAME')
    if v:
        dcf['username'] = v
    v = os.environ.get('APM_PASSWORD')
    if v:
        dcf['password'] = v
    return dcf


################################################################################
def _main(argv=None):
    cwd = os.getcwd()
    try:
        dcf = get_repository_env()
        parser = ArgumentParser(
            description='''ARGOS-LABS Plugin Module Manager

This manager use private PyPI repository.
set {home}{sep}.apm.conf

repository: http://pypi.argos-labs.com:8080
username: user
password: pass

Or 
set environmental variables
APM_REPOSITORY=http://pypi.argos-labs.com:8080
APM_USERNAME=user
APM_PASSWORD=pass

Or use argument options
--repository http://pypi.argos-labs.com:8080
--username user
--password pass
'''.format(home=str(Path.home()), sep=os.path.sep),
            formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--new-py', action='store_true',
                            help='making new python venv environment at py.%s' %
                            sys.platform)
        parser.add_argument('--venv', action='store_true',
                            help='if set use package top py.%s for virtual env.'
                                 ' If not set. Use system python instead.'
                                 % sys.platform)
        parser.add_argument('--repository', '-r', nargs='?',
                            help='set module repository')
        parser.add_argument('--username', nargs='?',
                            help='user name for private repository')
        parser.add_argument('--password', nargs='?',
                            help='password for private repository')
        parser.add_argument('--clean', '-c', action='store_true',
                            help='clean all temporary folders, etc.')
        parser.add_argument('--verbose', '-v', action='count', default=0,
                            help='verbose output eg) -v, -vv, -vvv, ...')

        subps = parser.add_subparsers(help='apm command help', dest='command')
        # apm functions
        _ = subps.add_parser('test', help='test this module')
        _ = subps.add_parser('build', help='build this module')
        _ = subps.add_parser('register', help='register to upload server')
        _ = subps.add_parser('upload', help='upload this module to server')
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
        if args.verbose > 0:
            print(str(args).replace('Namespace', 'Arguments'))
        if not args.command:
            sys.stderr.write('Need command for apm.\n')
            parser.print_help()
            return False
        else:
            if not args.repository:
                args.repository = dcf['repository']
            if not args.username:
                args.username = dcf['username']
            if not args.password:
                args.password = dcf['password']
            venv = VEnv(args)
            apm = APM(venv, args)
            return apm.do()
    finally:
        os.chdir(cwd)


################################################################################
def main(argv=None):
    try:
        _main(argv)
    except Exception as err:
        _exc_info = sys.exc_info()
        _out = traceback.format_exception(*_exc_info)
        del _exc_info
        sys.stderr.write('%s\n' % ''.join(_out))
        sys.stderr.write('%s\n' % str(err))
        sys.stderr.write('  use -h option for more help\n')
        sys.exit(9)
