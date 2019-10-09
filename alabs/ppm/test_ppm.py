"""
====================================
 :mod:test_ppm
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS
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
#  * [2019/08/26]
#   - ppm exe로 만들어 테스트 하기: for STU & PAM
#  * [2019/08/09]
#     - 680 argoslabs.time.workalendar prebuilt requirements.txt and then install whl
#  * [2019/05/29]
#     - dumppi 테스트
#  * [2019/05/27]
#     - POT 환경 구축 후 테스트
#     - 마지막 테스트 후 24시간이 지나지 않으면 dumpspec 캐시를 지우는 테스트 않함
#  * [2018/11/28]
#     - 본 모듈 작업 시작
################################################################################
import os
import sys
import glob
import json
# import time
import shutil
import tempfile
import requests
import datetime
# import subprocess
import urllib3
from tempfile import gettempdir
# from urllib.parse import quote
# noinspection PyProtectedMember,PyUnresolvedReferences
from alabs.ppm import _main, CONF_PATH, _conf_last_version
from unittest import TestCase, TestLoader, TextTestRunner
from pathlib import Path
from contextlib import contextmanager
from io import StringIO
from pprint import pprint
from pickle import dump, load
if '%s.%s' % (sys.version_info.major, sys.version_info.minor) < '3.3':
    raise EnvironmentError('Python Version must greater then "3.3" '
                           'which support venv')
else:
    from urllib.parse import urlparse, quote
    from pathlib import Path
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


################################################################################
@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


################################################################################
# noinspection PyUnresolvedReferences
class TU(TestCase):
    # ==========================================================================
    vers = list()
    TS_FILE = '%s/.test_ppm.pkl' % gettempdir()
    TS_LAST = datetime.datetime(2000, 1, 1, 0, 0, 0)
    TS_CLEAR = True
    DUMPPI_FOLDER = '%s%sdumppi_folder' % (gettempdir(), os.path.sep)
    HTTP_SERVER_PO = None

    # ==========================================================================
    def test_0000_check_python(self):
        self.assertTrue('%s.%s' % (sys.version_info.major,
                                   sys.version_info.minor) > '3.3')
        if os.path.exists(TU.TS_FILE):
            with open(TU.TS_FILE, 'rb') as ifp:
                TU.TS_LAST = load(ifp)
        ts_diff = datetime.datetime.now() - TU.TS_LAST
        TU.TS_CLEAR = True if ts_diff.total_seconds() > 86400 else False
        sta_f = os.path.join(str(Path.home()), '.argos-rpa.sta')
        if os.path.exists(sta_f):
            os.remove(sta_f)

    # ==========================================================================
    def test_0005_check_apm_conf(self):
        if os.path.exists(CONF_PATH):
            os.remove(CONF_PATH)
        self.assertTrue(not os.path.exists(CONF_PATH))

    # ==========================================================================
    def test_0010_help(self):
        try:
            _main(['-h'])
            # -h 에 오류 발생하지 않도록 억제
            self.assertTrue(True)
        except RuntimeWarning as e:
            print(e)
            self.assertTrue(True)

    # ==========================================================================
    def test_0020_no_param(self):
        try:
            with captured_output() as (out, err):
                r = _main([])
            self.assertTrue(not r)
            stdout = out.getvalue().strip()
            if stdout:
                print(stdout)
            stderr = err.getvalue().strip()
            if stderr:
                sys.stderr.write(stderr)
            self.assertTrue(stdout.find('ARGOS-LABS Plugin Package Manager') > 0)
            self.assertTrue(stderr == 'Need command for ppm.')
        except Exception as e:
            print(e)
            self.assertTrue(False)

    # ==========================================================================
    def test_0025_invalid_cmd(self):
        try:
            _ = _main(['alskdfjasklfj'])
            self.assertTrue(False)
        except RuntimeWarning as e:
            print(e)
            self.assertTrue(True)

    # recursive test for comment out
    # # ==========================================================================
    # def test_0030_test(self):
    #     try:
    #         # r = _main(['--venv', 'test'])
    #         # self.assertTrue(not r)
    #         self.assertTrue(True)
    #     except Exception as e:
    #         print(e)
    #         self.assertTrue(False)

    # ==========================================================================
    def test_0035_clear_all(self):
        r = _main(['clear-all'])
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0040_build(self):
        r = _main(['--venv', '-v', 'build'])
        self.assertTrue(r == 0)
        mdir = os.path.dirname(__file__)
        ppdir = os.path.abspath(os.path.join(mdir, '..', '..'))
        self.assertTrue(os.path.exists(os.path.join(ppdir, 'alabs.ppm.egg-info',
                                                    'PKG-INFO')))
        if sys.platform == 'win32':
            self.assertTrue(os.path.exists(os.path.join(str(Path.home()),
                                                        'py.%s' % sys.platform,
                                                        'Scripts',
                                                        'python.exe')))
        else:
            self.assertTrue(os.path.exists(os.path.join(str(Path.home()),
                                                        'py.%s' % sys.platform,
                                                        'bin',
                                                        'python')))

    # ==========================================================================
    def test_0045_change_apm_conf(self):
        with open(CONF_PATH, 'w') as ofp:
            ofp.write('''
---
version: "1.1"

repository:
  url: https://pypi-official.argos-labs.com/pypi
  req: https://pypi-req.argos-labs.com
private-repositories:
- name: pypi-test
  url: https://pypi-test.argos-labs.com/simple
  username: argos
  password: argos_01
''')
        self.assertTrue(os.path.exists(CONF_PATH))

    # ==========================================================================
    def test_0050_submit_without_key(self):
        try:
            _main(['submit'])
            self.assertTrue(False)
        except Exception as e:
            print(e)
            self.assertTrue(True)

    # TODO
    # # ==========================================================================
    # def test_0055_submit_with_key(self):
    #     try:
    #         _main(['submit', '--submit-key', 'aL0PK2Rhs6ed0mgqLC42'])
    #         self.assertTrue(True)
    #     except Exception as e:
    #         print(e)
    #         self.assertTrue(False)

    # TODO
    # # ==========================================================================
    # def test_0060_upload(self):
    #     # 사설 저장소에 wheel upload (내부 QC를 거친 후)
    #     r = _main(['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
    #                '--venv', 'upload'])
    #     self.assertTrue(r == 0)

    # ==========================================================================
    def test_0070_clear_all_after_upload(self):
        r = _main(['clear-all'])
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0110_invalid_get(self):
        try:
            _ = _main(['get', 'alskdfjasklfj'])
            self.assertTrue(False)
        except Exception as e:
            print(e)
            self.assertTrue(True)

    # ==========================================================================
    def test_0120_get(self):
        with captured_output() as (out, err):
            r = _main(['get', 'repository'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.startswith('http'))
        rep = stdout

        with captured_output() as (out, err):
            r = _main(['get', 'trusted-host'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(rep.find(stdout) > 0)

    # ==========================================================================
    def test_0150_list(self):
        with captured_output() as (out, err):
            r = _main(['-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        # self.assertTrue(stdout.find('alabs.ppm') > 0)
        if stdout.find('alabs.ppm') > 0:
            r = _main(['-vv', 'uninstall', 'alabs.ppm'])
            self.assertTrue(r == 0)

    # ==========================================================================
    def test_0160_list_self_upgrade(self):
        with captured_output() as (out, err):
            r = _main(['--self-upgrade', '-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        # self.assertTrue(stdout.find('alabs.ppm') > 0)
        if stdout.find('alabs.ppm') > 0:
            r = _main(['-vv', 'uninstall', 'alabs.ppm'])
            self.assertTrue(r == 0)

    # ==========================================================================
    def test_0200_install(self):
        r = _main(['-vv', 'install', 'alabs.ppm'])
        self.assertTrue(r == 0)
        # check install
        with captured_output() as (out, err):
            r = _main(['-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_0210_show(self):
        with captured_output() as (out, err):
            r = _main(['show', 'alabs.ppm'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_0220_uninstall(self):
        r = _main(['-vv', 'uninstall', 'alabs.ppm'])
        self.assertTrue(r == 0)
        # check uninstall
        with captured_output() as (out, err):
            r = _main(['-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertFalse(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_0300_search(self):
        with captured_output() as (out, err):
            r = _main(['-vv', 'search', 'argoslabs'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertFalse(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_0310_list_repository(self):
        with captured_output() as (out, err):
            r = _main(['list-repository'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.data.excel') > 0)
        r = _main(['list-repository'])
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0390_plugin_versions(self):
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'versions', 'argoslabs.demo.helloworld']
        if TU.TS_CLEAR:
            cmd.append('--flush-cache')
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        TU.vers1 = stdout.split('\n')
        self.assertTrue(len(TU.vers1) >= 2)

    # ==========================================================================
    def test_0400_plugin_get_all_short_output(self):
        # --flush-cache 캐쉬를 지우면 오래 걸림 (특히 플러그인이 많을 경우)
        cmd = ['plugin', 'get', '--short-output', '--official-only']
        if TU.TS_CLEAR:
            cmd.append('--flush-cache')
        # cmd = ['plugin', 'get', '--short-output']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.data.json,') > 0)
        r = _main(cmd)
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0405_plugin_get_all_short_output(self):
        # --flush-cache 캐쉬를 지우면 오래 걸림 (특히 플러그인이 많을 경우)
        cmd = ['plugin', 'get', '--short-output']
        if TU.TS_CLEAR:
            cmd.append('--flush-cache')
        # cmd = ['plugin', 'get', '--short-output']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.data.json,') > 0)
        r = _main(cmd)
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0410_plugin_get_all(self):
        cmd = ['plugin', 'get']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.data.json') > 0 and
                        stdout.find('display_name') > 0)
        # r = _main(cmd)
        # self.assertTrue(r == 0)

    # ==========================================================================
    def test_0420_plugin_versions(self):
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'versions', 'argoslabs.demo.helloworld']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        TU.vers1 = stdout.split('\n')
        self.assertTrue(len(TU.vers1) >= 2)

    # ==========================================================================
    def test_0430_plugin_get_module(self):
        # 특정 버전을 지정하지 않으면 가장 최신 버전
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'get', 'argoslabs.demo.helloworld']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.demo.helloworld') > 0)
        rd = json.loads(stdout)
        self.assertTrue(rd['argoslabs.demo.helloworld']['version'] == TU.vers1[0])

    # ==========================================================================
    def test_0440_plugin_get_module_with_version(self):
        # 특정 버전을 지정
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'get', 'argoslabs.demo.helloworld==%s' % TU.vers1[1]]
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.demo.helloworld') > 0)
        rd = json.loads(stdout)
        self.assertTrue(rd['argoslabs.demo.helloworld']['version'] == TU.vers1[1])

    # ==========================================================================
    def test_0450_plugin_get_module_with_version(self):
        # 특정 버전 보다 큰 버전
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'get', 'argoslabs.demo.helloworld>%s' % TU.vers1[1]]
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.demo.helloworld') > 0)
        rd = json.loads(stdout)
        self.assertTrue(rd['argoslabs.demo.helloworld']['version'] == TU.vers1[0])

    # ==========================================================================
    def test_0460_plugin_get_module_with_version(self):
        # 특정 버전 보다 작은 버전
        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'get', 'argoslabs.demo.helloworld<%s' % TU.vers1[0]]
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.demo.helloworld') > 0)
        rd = json.loads(stdout)
        self.assertTrue(rd['argoslabs.demo.helloworld']['version'] == TU.vers1[1])

    # ==========================================================================
    def test_0470_plugin_get_all_only_official(self):
        jsf = '%s%sget-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 안주면 목록으로 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'get', '--official-only', '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            # noinspection PyChainedComparisons
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd[0]['owner'] == 'ARGOS-LABS')
                self.assertTrue('last_modify_datetime' in vd[0])
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0475_plugin_get_all_only_official_with_dumpspec(self):
        jsf = '%s%sget-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 안주면 목록으로 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'get', '--official-only', '--with-dumpspec',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(jsf) as ifp:
                rd = json.load(ifp)
            # pprint(rd)
            # noinspection PyChainedComparisons
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd[0]['owner'] == 'ARGOS-LABS')
                self.assertTrue('last_modify_datetime' in vd[0])
                if isinstance(vd, list):
                    for vdi in vd:
                        self.assertTrue('dumpspec' in vdi and isinstance(vdi['dumpspec'], dict))
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0480_plugin_get_all_only_official_last_only(self):
        jsf = '%s%sget-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 주면 최신버전을 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'get', '--official-only', '--last-only',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            # noinspection PyChainedComparisons
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'] == 'ARGOS-LABS')
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0485_plugin_get_all_only_official_last_only_with_dumpspec(self):
        jsf = '%s%sget-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 주면 최신버전을 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'get', '--official-only', '--last-only',
                   '--with-dumpspec',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            # noinspection PyChainedComparisons
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'] == 'ARGOS-LABS')
                self.assertTrue('last_modify_datetime' in vd)
                self.assertTrue('dumpspec' in vd and isinstance(vd['dumpspec'], dict))
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0490_plugin_dumpspec_all_only_official(self):
        jsf = '%s%sdumpspec-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 안주면 목록으로 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'dumpspec', '--official-only', '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            # pprint(rd)
            for k, vd in rd.items():
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'] == 'ARGOS-LABS')
                self.assertTrue(vd['name'] == k)
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0500_plugin_dumpspec_all_only_official_with_last_only(self):
        jsf = '%s%sdumpspec-official-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 주면 최신버전을 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'dumpspec', '--official-only', '--last-only',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            for k, vd in rd.items():
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'] == 'ARGOS-LABS')
                self.assertTrue(vd['name'] == k)
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0510_plugin_dumpspec_all_only_private(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            # --last-only 옵션을 주면 최신버전을 가져옴
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'dumpspec', '--private-only', '--last-only',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            # pprint(rd)
            ag_cnt = 0
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                ag_cnt += 1
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'].startswith('ARGOS-LABS'))
                self.assertTrue(vd['name'] == k)
                if 'last_modify_datetime' not in vd:
                    print('%s does not have "last_modify_datetime"' % k)
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue(ag_cnt > 0 and 'argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0520_get_oauth_token(self):
        # 현재 STU에서 호출할 경우에는 token을 받아 처리하지만 이 유닛 테스트는
        # 그럴 수 없으므로 황이사가 알려준 admin 토큰 받아오는 것을 불러
        # 테스트를 하지만, 이런 경우 보안 구멍이 있을 수 있으므로 테스트 시에만
        TU.token = None
        try:
            cookies = {
                'JSESSIONID': '04EFBA89842288248F32F9EC19B7423E',
            }

            headers = {
                'Accept': '*/*',
                'Authorization': 'Basic YXJnb3MtcnBhOjA0MGM1YTA1MTkzZWRjYWViZjk4NTY1MmMxOGE1MThj',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Host': 'oauth-rpa.argos-labs.com',
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
                # 'username': 'admin',
                # 'password': '78argos90',
                'username': 'mcchae@gmail.com',
                'password': 'ghkd67vv'
            }

            r = requests.post('https://oauth-rpa.argos-labs.com/oauth/token',
                              headers=headers, cookies=cookies, data=data)
            if r.status_code // 10 != 20:
                raise RuntimeError('PPM._dumpspec_user: API Error!')
            jd = json.loads(r.text)
            TU.token = 'Bearer %s' % jd['access_token']
            TU.access_token = jd['access_token']
            self.assertTrue(TU.token.startswith('Bearer '))
        except Exception as e:
            sys.stderr('%s%s' % (str(e), os.linesep))
            self.assertTrue(False)

    # ==========================================================================
    def test_0530_plugin_dumpspec_user_official_without_auth(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'dumpspec', '--official-only',
                   # '--user', 'fjoker@naver.com',
                   '--user', 'mcchae@gmail.com',
                   '--outfile', jsf]
            _ = _main(cmd)
            self.assertTrue(False)
        except Exception as err:
            sys.stderr.write('%s%s' % (str(err), os.linesep))
            self.assertTrue(True)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0540_plugin_dumpspec_user_official_invalid_auth(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'dumpspec', '--official-only',
                   # '--user', 'fjoker@naver.com',
                   '--user', 'mcchae@gmail.com',
                   '--user-auth', 'invalid--key',
                   '--outfile', jsf]
            _ = _main(cmd)
            self.assertTrue(False)
        except Exception as err:
            sys.stderr.write('%s%s' % (str(err), os.linesep))
            self.assertTrue(True)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0550_plugin_dumpspec_user_official(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        # 2019.07.27 : 다음의 plugin 의존적인 --user, --user-auth 옵션을 메인 옵션으로 옮김
        #   STU와 협의 요
        try:
            cmd = ['plugin', 'dumpspec', '--official-only', '--last-only',
                   # '--user', 'fjoker@naver.com',
                   '--user', 'mcchae@gmail.com',
                   '--user-auth', TU.token,
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            # pprint(rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'].startswith('ARGOS-LABS'))
                self.assertTrue(vd['name'] == k)
        except Exception as err:
            sys.stderr.write('%s%s' % (str(err), os.linesep))
            self.assertTrue(False)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0560_plugin_dumpspec_user_official(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['--pr-user', 'mcchae@gmail.com',  # 'fjoker@naver.com',
                   '--pr-user-auth', TU.token,
                   'plugin', 'dumpspec', '--official-only',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            # pprint(rd)
            for k, vd in rd.items():
                if not k.startswith('argoslabs.'):
                    continue
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'].startswith('ARGOS-LABS'))
                self.assertTrue(vd['name'] == k)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0570_get_with_private_repository(self):
        with captured_output() as (out, err):
            r = _main(['--pr-user', 'mcchae@gmail.com',  # 'fjoker@naver.com',
                       '--pr-user-auth', TU.token,
                       'get', 'private'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.startswith('There are ')
                        or stdout == 'No private repository')

    # ==========================================================================
    def test_0600_plugin_venv_clear(self):
        venv_d = os.path.join(str(Path.home()), '.argos-rpa.venv')
        if os.path.exists(venv_d):
            shutil.rmtree(venv_d)
        self.assertTrue(not os.path.exists(venv_d))

        cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
               'plugin', 'versions', 'argoslabs.data.fileconv']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        TU.vers2 = stdout.split('\n')
        self.assertTrue(len(TU.vers2) >= 2)

        cmd = ['plugin', 'versions', 'argoslabs.web.bsoup']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        TU.vers3 = stdout.split('\n')
        self.assertTrue(len(TU.vers3) >= 2)

    # ==========================================================================
    def test_0605_plugin_venv_success(self):
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', 'argoslabs.ai.tts',
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                TU.venv_01 = ifp.read()
            self.assertTrue(True)
        except Exception as err:
            sys.stderr.write('%s%s' % (str(err), os.linesep))
            self.assertTrue(False)
        finally:
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0610_plugin_venv_success(self):
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 최신버전 설치 in venv_01
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', 'argoslabs.data.fileconv',
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 == stdout)
            freeze_f = os.path.join(TU.venv_01, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(rd['argoslabs.data.fileconv'] == TU.vers2[0])
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0620_plugin_venv_success(self):
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 최신버전 설치 in venv_01
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', 'argoslabs.data.fileconv==%s' % TU.vers2[0],
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 == stdout)
            freeze_f = os.path.join(TU.venv_01, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(rd['argoslabs.data.fileconv'] == TU.vers2[0])
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0630_plugin_venv_success(self):
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.web.bsoup 최신버전 설치 in venv_01
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', 'argoslabs.web.bsoup==%s' % TU.vers3[0],
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 == stdout)
            freeze_f = os.path.join(TU.venv_01, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(rd['argoslabs.web.bsoup'] == TU.vers3[0])
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0640_plugin_venv(self):
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 이전버전 설치 in venv_02
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', 'argoslabs.data.fileconv==%s' % TU.vers2[1],
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 != stdout)
            TU.venv_02 = stdout
            freeze_f = os.path.join(TU.venv_02, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(rd['argoslabs.data.fileconv'] == TU.vers2[1])
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0650_plugin_venv_requirements_txt(self):
        tmpdir = None
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 이전버전 설치
            # argoslabs.web.bsoup 이전버전 설치
            # in venv_02
            modlist = [
                'argoslabs.data.fileconv==%s' % TU.vers2[1],
                'argoslabs.web.bsoup==%s' % TU.vers3[1],
            ]
            tmpdir = tempfile.mkdtemp(prefix='requirements_')
            requirements_txt = os.path.join(tmpdir, 'requirements.txt')
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
                ofp.write('\n'.join(modlist))

            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', '--requirements-txt', requirements_txt,
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_02 == stdout)
            TU.venv_02 = stdout
            freeze_f = os.path.join(TU.venv_02, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(
                rd['argoslabs.data.fileconv'] == TU.vers2[1] and
                rd['argoslabs.web.bsoup'] == TU.vers3[1]
            )
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0660_plugin_venv_requirements_txt_best(self):
        tmpdir = None
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 이전버전 설치
            # argoslabs.web.bsoup 최신버전 설치
            # in venv_03
            modlist = [
                'argoslabs.data.fileconv==%s' % TU.vers2[1],
                'argoslabs.web.bsoup==%s' % TU.vers3[0],
            ]
            tmpdir = tempfile.mkdtemp(prefix='requirements_')
            requirements_txt = os.path.join(tmpdir, 'requirements.txt')
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
                ofp.write('\n'.join(modlist))
            cmd = ['--pr-user', 'mcchae@gmail.com', '--pr-user-pass', 'ghkd67vv',
                   'plugin', 'venv', '--requirements-txt', requirements_txt,
                   '--outfile', venvout]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 != stdout and TU.venv_02 != stdout)
            TU.venv_02 = stdout
            freeze_f = os.path.join(TU.venv_02, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(
                rd['argoslabs.data.fileconv'] == TU.vers2[1] and
                rd['argoslabs.web.bsoup'] == TU.vers3[0]
            )
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0670_plugin_venv_requirements_txt_for_pam(self):
        tmpdir = None
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 이전버전 설치
            # argoslabs.web.bsoup 최신버전 설치
            # in venv_03
            modlist = [
                'argoslabs.data.fileconv==%s' % TU.vers2[1],
                'argoslabs.web.bsoup==%s' % TU.vers3[0],
                'yourfolder.demo.helloworld==1.100.1000',
            ]
            tmpdir = tempfile.mkdtemp(prefix='requirements_')
            requirements_txt = os.path.join(tmpdir, 'requirements.txt')
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
                ofp.write('\n'.join(modlist))
            cmd = [
                'plugin', 'venv', '--requirements-txt', requirements_txt,
                '--user', 'mcchae@gmail.com',
                '--user-auth', '82abacb7-b8b1-11e9-bdba-064c24692e8b',
                '--pam-id', '001C4231BA4F',
                '--outfile', venvout
            ]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            self.assertTrue(TU.venv_01 != stdout and TU.venv_02 == stdout)
            freeze_f = os.path.join(TU.venv_02, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(
                rd['argoslabs.data.fileconv'] == TU.vers2[1] and
                rd['argoslabs.web.bsoup'] == TU.vers3[0] and
                rd['yourfolder.demo.helloworld'] == '1.100.1000'
            )
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0680_plugin_venv_requirements_txt_for_pam_prebuilt(self):
        tmpdir = None
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            # argoslabs.data.fileconv 이전버전 설치
            # argoslabs.web.bsoup 최신버전 설치
            # in venv_03
            modlist = [
                'yourfolder.demo.helloworld==1.100.1000',
                'argoslabs.time.workalendar==1.830.2039',
            ]
            tmpdir = tempfile.mkdtemp(prefix='requirements_')
            requirements_txt = os.path.join(tmpdir, 'requirements.txt')
            with open(requirements_txt, 'w') as ofp:
                ofp.write('# pip dependent packages\n')
                ofp.write('\n'.join(modlist))
            cmd = [
                'plugin', 'venv', '--requirements-txt', requirements_txt,
                '--user', 'mcchae@gmail.com',
                '--user-auth', '82abacb7-b8b1-11e9-bdba-064c24692e8b',
                '--pam-id', '001C4231BA4F',
                '--outfile', venvout
            ]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(venvout) as ifp:
                stdout = ifp.read()
            freeze_f = os.path.join(stdout, 'freeze.json')
            self.assertTrue(os.path.exists(freeze_f))
            with open(freeze_f) as ifp:
                rd = json.load(ifp)
            self.assertTrue(
                rd['yourfolder.demo.helloworld'] == '1.100.1000' and
                rd['argoslabs.time.workalendar'] == '1.830.2039'
            )
            for k, v in rd.items():
                print('%s==%s' % (k, v))
        finally:
            if tmpdir and os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0690_pip_download(self):
        # tmpdir = tempfile.mkdtemp(prefix='down_install_')
        tmpdir = r'C:\Users\Administrator\AppData\Local\Temp\foobar'
        venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
        try:
            cmd = [
                'pip', 'download',
                'argoslabs.ai.tts',
                '--dest', tmpdir,
                '--no-deps',
                '--index', 'https://pypi-official.argos-labs.com/pypi',
                '--trusted-host', 'pypi-official.argos-labs.com',
                '--extra-index-url', 'https://pypi-test.argos-labs.com/simple',
                '--trusted-host', 'pypi-test.argos-labs.com',
                '--extra-index-url', 'https://pypi-demo.argos-labs.com/simple',
                '--trusted-host', 'pypi-demo.argos-labs.com',
                # '--outfile', venvout,
            ]
            r = _main(cmd)
            self.assertTrue(r == 0)
            fl = glob.glob(os.path.join(tmpdir, 'argoslabs.ai.tts-*.whl'))
            self.assertTrue(len(fl) == 1)
        finally:
            # if tmpdir and os.path.exists(tmpdir):
            #     shutil.rmtree(tmpdir)
            if os.path.exists(venvout):
                os.remove(venvout)

    # ==========================================================================
    def test_0700_pip_install(self):
        try:
            cmd = [
                'pip', 'install',
                'argoslabs.time.workalendar==1.830.2039',
                # 'argoslabs.ai.tts',
                # '--index', 'https://pypi-official.argos-labs.com/pypi',
                # '--trusted-host', 'pypi-official.argos-labs.com',
                # '--extra-index-url', 'https://pypi-test.argos-labs.com/simple',
                # '--trusted-host', 'pypi-test.argos-labs.com',
                # '--extra-index-url', 'https://pypi-demo.argos-labs.com/simple',
                # '--trusted-host', 'pypi-demo.argos-labs.com',
            ]
            r = _main(cmd)
            self.assertTrue(r == 0)
        finally:
            pass

    # ==========================================================================
    def test_0710_plugin_venv(self):
        try:
            cmd = [
                'plugin', 'venv',
                'alabs.common',
                'pyautogui',
                'bs4',
                'opencv-python',
            ]
            r = _main(cmd)
            self.assertTrue(r == 0)
        finally:
            pass

    # # ==========================================================================
    # def test_0710_stu_issue(self):
    #     try:
    #         cmd = [
    #             '--self-upgrade',
    #             'plugin', 'dumpspec',
    #             '--official-only',
    #             '--last-only',
    #             '--user', 'taejin.kim@vivans.net',
    #             '--user-auth', "Bearer fed39c5c-3b1e-402d-ab0c-035ea30bcc6c",
    #         ]
    #         r = _main(cmd)
    #         self.assertTrue(r == 0)
    #     finally:
    #         pass

    # TODO : local repository
    # # ==========================================================================
    # def test_0700_plugin_dumppi_empty_folder(self):
    #     try:
    #         cmd = ['plugin', 'dumppi', '--official-only', '--last-only']
    #         _ = _main(cmd)
    #         self.assertTrue(False)
    #     except Exception as err:
    #         sys.stderr.write('%s%s' % (str(err), os.linesep))
    #         self.assertTrue(True)
    #
    # # ==========================================================================
    # def test_0710_plugin_dumppi(self):
    #     try:
    #         if os.path.exists(TU.DUMPPI_FOLDER):
    #             shutil.rmtree(TU.DUMPPI_FOLDER)
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'dumppi', '--official-only', '--last-only',
    #                    '--dumppi-folder', TU.DUMPPI_FOLDER]
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         stderr = err.getvalue().strip()
    #         sys.stderr.write('%s\n' % stderr)
    #     except Exception as err:
    #         sys.stderr.write('%s%s' % (str(err), os.linesep))
    #         self.assertTrue(False)
    #
#     # ==========================================================================
#     def test_0720_remove_all_venv(self):
#         venv_d = os.path.join(str(Path.home()), '.argos-rpa.venv')
#         if os.path.exists(venv_d):
#             shutil.rmtree(venv_d)
#         self.assertTrue(not os.path.exists(venv_d))
#
#     # ==========================================================================
#     def test_0730_http_server(self):
#         cmd = [
#             'python',
#             '-m',
#             'http.server',
#             '--directory', TU.DUMPPI_FOLDER,
#             '38038'
#         ]
#         TU.HTTP_SERVER_PO = subprocess.Popen(cmd)
#         time.sleep(1)
#         self.assertTrue(TU.HTTP_SERVER_PO is not None)
#
#     # ==========================================================================
#     def test_0740_rename_conf(self):
#         os.rename(CONF_PATH, '%s.org' % CONF_PATH)
#         with open(CONF_PATH, 'w') as ofp:
#             ofp.write('''
# version: "%s"
# repository:
#   url: http://localhost:38038/simple
# '''% _conf_last_version)
#         self.assertTrue(os.path.exists('%s.org' % CONF_PATH))
#
#     # 2019.08.09 : POT 이후 문제 발생
#     # ==========================================================================
#     def test_0750_plugin_venv_success(self):
#         venvout = '%s%svenv.out' % (gettempdir(), os.path.sep)
#         try:
#             cmd = ['plugin', 'venv', 'argoslabs.ai.tts', '--outfile', venvout]
#             r = _main(cmd)
#             self.assertTrue(r == 0)
#             with open(venvout) as ifp:
#                 stdout = ifp.read()
#             TU.venv_01 = stdout
#             self.assertTrue(True)
#         except Exception as err:
#             sys.stderr.write('%s%s' % (str(err), os.linesep))
#             self.assertTrue(False)
#         finally:
#             if os.path.exists(venvout):
#                 os.remove(venvout)
#
#     # ==========================================================================
#     def test_0760_restore_conf(self):
#         os.remove(CONF_PATH)
#         os.rename('%s.org' % CONF_PATH, CONF_PATH)
#         self.assertTrue(not os.path.exists('%s.org' % CONF_PATH))
#
#     # ==========================================================================
#     def test_0770_stop_http_server(self):
#         self.assertTrue(TU.HTTP_SERVER_PO is not None)
#         TU.HTTP_SERVER_PO.terminate()
#         TU.HTTP_SERVER_PO.wait()

    # ==========================================================================
    def test_9980_install_last(self):
        r = _main(['-vv', 'install', 'alabs.ppm'])
        self.assertTrue(r == 0)
        # check install
        with captured_output() as (out, err):
            r = _main(['-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        self.assertTrue(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_9990_clear_all(self):
        r = _main(['clear-all'])
        self.assertTrue(r == 0)
        if os.path.exists(TU.DUMPPI_FOLDER):
            shutil.rmtree(TU.DUMPPI_FOLDER)
        self.assertTrue(not os.path.exists(TU.DUMPPI_FOLDER))

    # ==========================================================================
    def test_9999_quit(self):
        with open(TU.TS_FILE, 'wb') as ofp:
            dump(datetime.datetime.now(), ofp)
        self.assertTrue(os.path.exists(TU.TS_FILE))


################################################################################
if __name__ == "__main__":
    suite = TestLoader().loadTestsFromTestCase(TU)
    result = TextTestRunner(verbosity=2).run(suite)
    ret = not result.wasSuccessful()
    sys.exit(ret)
