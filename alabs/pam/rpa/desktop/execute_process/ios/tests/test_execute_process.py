#!/usr/bin/env python
# coding=utf8


################################################################################
import os
import glob
from alabs.common.util.vvargs import ArgsError, ArgsExit, ModuleContext,\
    func_log, str2bool
from alabs.pam.rpa.desktop.execute_process.ios import main as _main
from unittest import TestCase


################################################################################
G_PARAMS = ['y', '50', '0.5', '1.2.3.4', 'tom', 'jerry', 'foo', 'foo']


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
    def test0010_execute(self):
        ret = _main("echo ARGOS_RPA")
        self.assertEqual(b'ARGOS_RPA\n', ret)

    # ==========================================================================
    def test0011_execute_error(self):
        with self.assertRaises(ArgsError):
            _main("echo ARGOS_RPA", "ABC")
