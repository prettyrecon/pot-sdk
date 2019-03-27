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
from alabs.common.util.vvargs import ArgsError
from alabs.rpa.ha.autogui.scroll import main as _main
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
    def test_110_option_scroll(self):
        X = 10
        Y = 25

        # 값을 입력 안했을 경우
        with self.assertRaises(ArgsError):
            x, y = _main()

        # 지원하지 않는 타입을 입력했을 경우
        with self.assertRaises(ArgsError):
            x, y = _main('-y', 'ABC')

        x, y = _main('-y', 25, '-x', '10')
        self.assertEqual((X, Y), (x, y))


