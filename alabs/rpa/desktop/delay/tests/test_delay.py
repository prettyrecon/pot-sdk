#!/usr/bin/env python
"""
====================================
 :mod: Test case for Config Module
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""

################################################################################
import os
import time
from alabs.common.util.vvargs import ArgsError, ArgsExit
from alabs.rpa.ha.desktop.delay import main as _main
from unittest import TestCase


################################################################################
G_PARAMS = ['0,0',]


################################################################################
class TU(TestCase):
    # ==========================================================================
    isFirst = True

    # ==========================================================================
    @staticmethod
    def clear():
        pass

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
    def test_100_delay_option_check(self):
        # 값을 입력 안했을 때
        with self.assertRaises(ArgsError):
            _main()

        # 허용하지 않는 값 입력을 받았을 때
        with self.assertRaises(ArgsError):
            _main('1234A')


    # ==========================================================================
    def test_200_delay_check(self):
        start_t = time.time()
        _main(1000)
        end_t = time.time()
        self.assertTrue((end_t - start_t) < 1.3)


