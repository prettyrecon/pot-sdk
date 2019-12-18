#!/usr/bin/env python

################################################################################
import os
import glob
import platform
import unittest
from alabs.common.util.vvargs import ArgsError, ArgsExit, ModuleContext,\
    func_log, str2bool
from alabs.pam.rpa.desktop.stop_process.ios import main as _main
from alabs.pam.rpa.desktop.execute_process.ios import main as execute_process
from unittest import TestCase



################################################################################
G_PARAMS = ['y', '50', '0.5', '1.2.3.4', 'tom', 'jerry', 'foo', 'bar']


################################################################################
class TU(TestCase):
    # ==========================================================================
    isFirst = True

    # ==========================================================================
    @staticmethod
    def clear():
        flist = (
            'debug.log', 'error.log', 'helloworld.err', 'helloworld.help',
            'helloworld.py.log', 'helloworld.yaml', 'helloworld.yaml2',
            'mylog.log', 'status.log', '__main__.py.log'
        )
        for f in flist:
            if os.path.exists(f):
                os.unlink(f)
        for f in glob.glob('*.log'):
            os.unlink(f)

    # ==========================================================================
    @staticmethod
    def init_wd():
        mdir = os.path.dirname(__file__)
        os.chdir(mdir)

    # ==========================================================================
    # noinspection PyMethodMayBeStatic
    def myInit(self):
        if TU.isFirst:
            TU.isFirst = False
            self.init_wd()
            self.clear()

    # ==========================================================================
    def setUp(self):
        self.myInit()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    # def test0010_argument_check(self):
    #     self.assertTrue(False)

    # ==========================================================================
    def test0020_stop_process_by_name(self):
        import time

        cmd = 'python -m alabs.rpa.ha.desktop.execute_process python -c "import time;time.sleep(5)"'
        pid = execute_process(cmd)
        time.sleep(1)
        print(_main('-p', pid))



    def test0030_stop_proceess_by_pid(self):
        pass

    def test0040_stop_process_forced(self):
        pass


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TU)
    unittest.TextTestRunner(verbosity=2).run(suite)