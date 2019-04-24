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
from alabs.rpa.autogui.send_shortcut import main as _main
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
    def test0100_argument_click_motion_type(self):
        """
        --clickmotiontype 옵션 검사
        :return:
        """
        _WRONG_VALUE = "ABC"
        _VALUE = ['ctrlleft', 'a']
        # 값 입력 유무 검사
        with self.assertRaises(ArgsError):
            _main()

        # 유효 값 오류 검사
        with self.assertRaises(ArgsError):
            _main(_WRONG_VALUE)

        # 유효 값 검사
        ret = _main(*_VALUE)
        self.assertEqual(_VALUE, ret)

