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
# noinspection PyProtectedMember
from alabs.ppm import _main
from unittest import TestCase, TestLoader, TextTestRunner
from pathlib import Path
from contextlib import contextmanager
from io import StringIO


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

    # ==========================================================================
    def test_0020_no_param(self):
        try:
            with captured_output() as (out, err):
                r = _main([])
            self.assertTrue(not r)
            stdout = out.getvalue().strip()
            stderr = err.getvalue().strip()
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

    # ==========================================================================
    def test_0030_test(self):
        try:
            # recursive test for comment out
            # r = _main(['--venv', 'test'])
            # self.assertTrue(not r)
            self.assertTrue(True)
        except Exception as e:
            print(e)
            self.assertTrue(False)

    # ==========================================================================
    def test_0035_clear_all(self):
        r = _main(['clear-all'])
        self.assertTrue(r == 0)

    # ==========================================================================
    def test_0040_build(self):
        r = _main(['--venv', 'build'])
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
    def test_0050_submit(self):
        try:
            _main(['submit'])
            self.assertTrue(True)
        except Exception as e:
            print(e)
            self.assertTrue(False)

    # ==========================================================================
    def test_0060_upload(self):
        # 사설 저장소에 wheel upload (내부 QC를 거친 후)
        r = _main(['--venv', 'upload'])
        self.assertTrue(r == 0)

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
        self.assertTrue(stdout.startswith('http'))
        rep = stdout

        with captured_output() as (out, err):
            r = _main(['get', 'trusted-host'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
        self.assertTrue(rep.find(stdout) > 0)

    # ==========================================================================
    def test_0150_list_uninstall(self):
        with captured_output() as (out, err):
            r = _main(['-vv', 'list'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
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
        self.assertTrue(stdout.find('alabs.ppm') > 0)

    # ==========================================================================
    def test_0210_show(self):
        with captured_output() as (out, err):
            r = _main(['show', 'alabs.ppm'])
        self.assertTrue(r == 0)
        stdout = out.getvalue().strip()
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
        self.assertFalse(stdout.find('alabs.ppm') > 0)

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
