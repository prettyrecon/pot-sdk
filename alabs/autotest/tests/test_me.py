################################################################################
import os
import sys
import datetime
from alabs.common.util.vvargs import ArgsError
from alabs.autotest import main
from unittest import TestCase


################################################################################
class TU(TestCase):
    # ==========================================================================
    def setUp(self) -> None:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    def test0100_autotest(self):
        of = 'foo.txt'
        try:
            r = main('--start', '--tee',
                     '--outfile', of)
            self.assertTrue(r == 0)
            with open(of, encoding='utf-8') as ifp:
                rstr = ifp.read()
                print(rstr)
            self.assertTrue(rstr.find('Start testing Google Vision API') > 0)
        except Exception as e:
            sys.stderr.write('\n%s\n' % str(e))
            self.assertTrue(False)
        finally:
            if os.path.exists(of):
                os.remove(of)

    # ==========================================================================
    def test0110_stat(self):
        of = 'foo.txt'
        try:
            r = main('--stat',
                     '--outfile', of)
            self.assertTrue(r == 0)
            with open(of, encoding='utf-8') as ifp:
                rstr = ifp.read()
                print(rstr)
                self.assertTrue(rstr)
        except Exception as e:
            sys.stderr.write('\n%s\n' % str(e))
            self.assertTrue(False)
        finally:
            if os.path.exists(of):
                os.remove(of)

    # ==========================================================================
    def test9999_quit(self):
        self.assertTrue(True)
