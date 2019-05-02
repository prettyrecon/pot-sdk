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
#  * [2018/11/28]
#     - 본 모듈 작업 시작
################################################################################
import os
import sys
import json
import shutil
import tempfile
from tempfile import gettempdir
# noinspection PyProtectedMember
from alabs.ppm import _main
from unittest import TestCase, TestLoader, TextTestRunner
from pathlib import Path
from contextlib import contextmanager
from io import StringIO
from pprint import pprint


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
class TU(TestCase):
    # ==========================================================================
    def test_0000_check_python(self):
        self.assertTrue('%s.%s' % (sys.version_info.major,
                                   sys.version_info.minor) > '3.3')

    # ==========================================================================
    def test_0005_check_apm_conf(self):
        cf = os.path.join(str(Path.home()), '.argos-rpa.conf')
        if not os.path.exists(cf):
            sys.stderr.write('First MUST edit "%s"' % cf)
        self.assertTrue(os.path.exists(cf))

    # ==========================================================================
    def test_0010_help(self):
        try:
            _main(['-h'])
            # -h 에 오류 발생하지 않도록 억제
            self.assertTrue(True)
        except RuntimeWarning as e:
            print(e)
            self.assertTrue(True)

    # # ==========================================================================
    # def test_0020_no_param(self):
    #     try:
    #         with captured_output() as (out, err):
    #             r = _main([])
    #         self.assertTrue(not r)
    #         stdout = out.getvalue().strip()
    #         if stdout:
    #             print(stdout)
    #         stderr = err.getvalue().strip()
    #         if stderr:
    #             sys.stderr.write(stderr)
    #         self.assertTrue(stdout.find('ARGOS-LABS Plugin Package Manager') > 0)
    #         self.assertTrue(stderr == 'Need command for ppm.')
    #     except Exception as e:
    #         print(e)
    #         self.assertTrue(False)
    #
    # # ==========================================================================
    # def test_0025_invalid_cmd(self):
    #     try:
    #         _ = _main(['alskdfjasklfj'])
    #         self.assertTrue(False)
    #     except RuntimeWarning as e:
    #         print(e)
    #         self.assertTrue(True)
    #
    # # recursive test for comment out
    # # # ==========================================================================
    # # def test_0030_test(self):
    # #     try:
    # #         # r = _main(['--venv', 'test'])
    # #         # self.assertTrue(not r)
    # #         self.assertTrue(True)
    # #     except Exception as e:
    # #         print(e)
    # #         self.assertTrue(False)
    #
    # # ==========================================================================
    # def test_0035_clear_all(self):
    #     r = _main(['clear-all'])
    #     self.assertTrue(r == 0)
    #
    # # ==========================================================================
    # def test_0040_build(self):
    #     r = _main(['--venv', '-v', 'build'])
    #     self.assertTrue(r == 0)
    #     mdir = os.path.dirname(__file__)
    #     ppdir = os.path.abspath(os.path.join(mdir, '..', '..'))
    #     self.assertTrue(os.path.exists(os.path.join(ppdir, 'alabs.ppm.egg-info',
    #                                                 'PKG-INFO')))
    #     if sys.platform == 'win32':
    #         self.assertTrue(os.path.exists(os.path.join(str(Path.home()),
    #                                                     'py.%s' % sys.platform,
    #                                                     'Scripts',
    #                                                     'python.exe')))
    #     else:
    #         self.assertTrue(os.path.exists(os.path.join(str(Path.home()),
    #                                                     'py.%s' % sys.platform,
    #                                                     'bin',
    #                                                     'python')))
    #
    # # ==========================================================================
    # def test_0050_submit(self):
    #     try:
    #         _main(['submit'])
    #         self.assertTrue(True)
    #     except Exception as e:
    #         print(e)
    #         self.assertTrue(False)
    #
    # # ==========================================================================
    # def test_0060_upload(self):
    #     # 사설 저장소에 wheel upload (내부 QC를 거친 후)
    #     r = _main(['--venv', 'upload'])
    #     self.assertTrue(r == 0)
    #
    # # ==========================================================================
    # def test_0070_clear_all_after_upload(self):
    #     r = _main(['clear-all'])
    #     self.assertTrue(r == 0)
    #
    # # ==========================================================================
    # def test_0110_invalid_get(self):
    #     try:
    #         _ = _main(['get', 'alskdfjasklfj'])
    #         self.assertTrue(False)
    #     except Exception as e:
    #         print(e)
    #         self.assertTrue(True)
    #
    # # ==========================================================================
    # def test_0120_get(self):
    #     with captured_output() as (out, err):
    #         r = _main(['get', 'repository'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertTrue(stdout.startswith('http'))
    #     rep = stdout
    #
    #     with captured_output() as (out, err):
    #         r = _main(['get', 'trusted-host'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertTrue(rep.find(stdout) > 0)
    #
    # # ==========================================================================
    # def test_0150_list(self):
    #     with captured_output() as (out, err):
    #         r = _main(['-vv', 'list'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     # self.assertTrue(stdout.find('alabs.ppm') > 0)
    #     if stdout.find('alabs.ppm') > 0:
    #         r = _main(['-vv', 'uninstall', 'alabs.ppm'])
    #         self.assertTrue(r == 0)
    #
    # # ==========================================================================
    # def test_0200_install(self):
    #     r = _main(['-vv', 'install', 'alabs.ppm'])
    #     self.assertTrue(r == 0)
    #     # check install
    #     with captured_output() as (out, err):
    #         r = _main(['-vv', 'list'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertTrue(stdout.find('alabs.ppm') > 0)
    #
    # # ==========================================================================
    # def test_0210_show(self):
    #     with captured_output() as (out, err):
    #         r = _main(['show', 'alabs.ppm'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertTrue(stdout.find('alabs.ppm') > 0)
    #
    # # ==========================================================================
    # def test_0220_uninstall(self):
    #     r = _main(['-vv', 'uninstall', 'alabs.ppm'])
    #     self.assertTrue(r == 0)
    #     # check uninstall
    #     with captured_output() as (out, err):
    #         r = _main(['-vv', 'list'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertFalse(stdout.find('alabs.ppm') > 0)
    #
    # # ==========================================================================
    # def test_0300_search(self):
    #     with captured_output() as (out, err):
    #         r = _main(['-vv', 'search', 'argoslabs'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertFalse(stdout.find('alabs.ppm') > 0)
    #
    # # ==========================================================================
    # def test_0310_list_repository(self):
    #     with captured_output() as (out, err):
    #         r = _main(['list-repository'])
    #     self.assertTrue(r == 0)
    #     stdout = out.getvalue().strip()
    #     print(stdout)
    #     self.assertTrue(stdout.find('argoslabs.data.excel') > 0)
    #     r = _main(['list-repository'])
    #     self.assertTrue(r == 0)

    # ==========================================================================
    def test_0400_plugin_get_all_short_output(self):
        cmd = ['plugin', 'get', '--short-output', '--flush-cache']
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
    def test_0420_plugin_get_module(self):
        cmd = ['plugin', 'get', 'argoslabs.demo.helloworld']
        with captured_output() as (out, err):
            r = _main(cmd)
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        print(stdout)
        self.assertTrue(stdout.find('argoslabs.demo.helloworld') > 0)
        rd = json.loads(stdout)
        self.assertTrue(len(rd['argoslabs.demo.helloworld']) >= 1 and
                        rd['argoslabs.demo.helloworld'][0]['owner'] == 'ARGOS-LABS-DEMO')

    # ==========================================================================
    def test_0430_plugin_get_all_only_official(self):
        jsf = '%s%sget-official-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'get', '--official-only', '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            # noinspection PyChainedComparisons
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' not in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0440_plugin_dumpspec_all_only_official(self):
        jsf = '%s%sdumpspec-official-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'dumpspec', '--official-only', '--outfile', jsf]
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
    def test_0450_plugin_dumpspec_all_only_private(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'dumpspec', '--private-only', '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            for k, vd in rd.items():
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'].startswith('ARGOS-LABS'))
                self.assertTrue(vd['name'] == k)
                if 'last_modify_datetime' not in vd:
                    print('%s does not have "last_modify_datetime"' % k)
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # ==========================================================================
    def test_0460_plugin_dumpspec_user_official(self):
        jsf = '%s%sdumpspec-private-all.json' % (gettempdir(), os.path.sep)
        try:
            cmd = ['plugin', 'dumpspec', '--official-only',
                   '--user', 'seonme@vivans.net',
                   '--outfile', jsf]
            r = _main(cmd)
            self.assertTrue(r == 0)
            self.assertTrue(os.path.exists(jsf))
            with open(jsf) as ifp:
                rd = json.load(ifp)
            pprint(rd)
            for k, vd in rd.items():
                self.assertTrue(k.startswith('argoslabs.'))
                self.assertTrue(vd['owner'].startswith('ARGOS-LABS'))
                self.assertTrue(vd['name'] == k)
                if 'last_modify_datetime' not in vd:
                    print('%s does not have "last_modify_datetime"' % k)
                self.assertTrue('last_modify_datetime' in vd)
            self.assertTrue('argoslabs.data.json' in rd and
                            'argoslabs.demo.helloworld' in rd)
        finally:
            if os.path.exists(jsf):
                os.remove(jsf)

    # # ==========================================================================
    # def test_0500_plugin_venv_clear(self):
    #     venv_d = os.path.join(str(Path.home()), '.argos-rpa.venv')
    #     if os.path.exists(venv_d):
    #         shutil.rmtree(venv_d)
    #     self.assertTrue(not os.path.exists(venv_d))
    #
    # # ==========================================================================
    # def test_0510_plugin_venv_success(self):
    #     try:
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', 'argoslabs.data.json']
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         TU.venv_01 = stdout
    #         freeze_f = os.path.join(TU.venv_01, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue('argoslabs.data.json' in rd)
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         pass
    #
    # # ==========================================================================
    # def test_0520_plugin_venv_success_helloworld(self):
    #     try:
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', 'argoslabs.demo.helloworld==1.424.2255']
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         self.assertTrue(TU.venv_01 == stdout)
    #         freeze_f = os.path.join(TU.venv_01, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue(rd['argoslabs.demo.helloworld'] == '1.424.2255')
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         pass
    #
    # # ==========================================================================
    # def test_0530_plugin_venv_success_helloworld_again(self):
    #     try:
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', 'argoslabs.demo.helloworld==1.424.2255']
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         self.assertTrue(TU.venv_01 == stdout)
    #         freeze_f = os.path.join(TU.venv_01, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue(rd['argoslabs.demo.helloworld'] == '1.424.2255')
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         pass
    #
    # # ==========================================================================
    # def test_0540_plugin_venv_new_helloworld(self):
    #     try:
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', 'argoslabs.demo.helloworld==1.427.2277']
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         self.assertTrue(TU.venv_01 != stdout)
    #         TU.venv_02 = stdout
    #         freeze_f = os.path.join(TU.venv_02, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue(rd['argoslabs.demo.helloworld'] == '1.427.2277')
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         pass
    #
    # # ==========================================================================
    # def test_0550_plugin_venv_requirements_txt(self):
    #     tmpdir = None
    #     try:
    #         modlist = [
    #             'argoslabs.demo.helloworld==1.427.2277',
    #             'argoslabs.ai.tts ==  1.330.1500',
    #         ]
    #         tmpdir = tempfile.mkdtemp(prefix='requirements_')
    #         requirements_txt = os.path.join(tmpdir, 'requirements.txt')
    #         with open(requirements_txt, 'w') as ofp:
    #             ofp.write('# pip dependent packages\n')
    #             ofp.write('\n'.join(modlist))
    #
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', '--requirements-txt', requirements_txt]
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         self.assertTrue(TU.venv_02 == stdout)
    #         TU.venv_02 = stdout
    #         freeze_f = os.path.join(TU.venv_02, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue(
    #             rd['argoslabs.demo.helloworld'] == '1.427.2277' and
    #             rd['argoslabs.ai.tts'] == '1.330.1500'
    #         )
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         if tmpdir and os.path.exists(tmpdir):
    #             shutil.rmtree(tmpdir)
    #
    # # ==========================================================================
    # def test_0560_plugin_venv_requirements_txt_best(self):
    #     tmpdir = None
    #     try:
    #         modlist = [
    #             'alabs.common',
    #             'argoslabs.ai.tts ==  1.330.1500',
    #         ]
    #         tmpdir = tempfile.mkdtemp(prefix='requirements_')
    #         requirements_txt = os.path.join(tmpdir, 'requirements.txt')
    #         with open(requirements_txt, 'w') as ofp:
    #             ofp.write('# pip dependent packages\n')
    #             ofp.write('\n'.join(modlist))
    #
    #         with captured_output() as (out, err):
    #             cmd = ['plugin', 'venv', '--requirements-txt', requirements_txt]
    #             r = _main(cmd)
    #         self.assertTrue(r == 0)
    #         stdout = out.getvalue().strip()
    #         print(stdout)
    #         self.assertTrue(TU.venv_02 == stdout)
    #         TU.venv_02 = stdout
    #         freeze_f = os.path.join(TU.venv_02, 'freeze.json')
    #         self.assertTrue(os.path.exists(freeze_f))
    #         with open(freeze_f) as ifp:
    #             rd = json.load(ifp)
    #         self.assertTrue(
    #             rd['argoslabs.demo.helloworld'] == '1.427.2277' and
    #             rd['argoslabs.ai.tts'] == '1.330.1500'
    #         )
    #         for k, v in rd.items():
    #             print('%s==%s' % (k, v))
    #     finally:
    #         if tmpdir and os.path.exists(tmpdir):
    #             shutil.rmtree(tmpdir)

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

    # ==========================================================================
    def test_9999_quit(self):
        self.assertTrue(True)


################################################################################
if __name__ == "__main__":
    suite = TestLoader().loadTestsFromTestCase(TU)
    result = TextTestRunner(verbosity=2).run(suite)
    ret = not result.wasSuccessful()
    sys.exit(ret)
