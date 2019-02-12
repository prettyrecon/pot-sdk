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
import glob
from alabs.common.util.vvargs import ArgsError
from alabs.rpa.autogui.click import main as _main
from alabs.rpa.autogui.click import ClickType, ClickMotionType
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

        # 값 입력 유무 검사
        args = ''
        with self.assertRaises(ArgsError):
            _main(args.split())

        # 유효 값 오류 검사
        with self.assertRaises(ArgsError):
            _main(*G_PARAMS, '--clickmotiontype', _WRONG_VALUE)

        # 유효 값 검사
        ret = _main(*G_PARAMS)
        self.assertEqual((0,0), ret)

    # ==========================================================================
    def test_argument_click_point(self):
        """
        --clickpoint 옵션 검사
        :return:
        """
        _VALUE_2 = "123, 45"

        # 값 입력 유무 검사
        with self.assertRaises(ArgsError):
            _main([])

        # 잘못된 값 검사
        with self.assertRaises(ArgsError):
            _main('ABC',)

        # 값 띄워쓰기 검사
        ret = _main('0, 0',)
        self.assertEqual((0, 0), ret)

        # 값 범위 검사
        # with self.assertRaises(ArgsError):
        _main('-10, 1')



    # ==========================================================================
    def test_argument_click_type(self):
        """
        --clicktype 옵션 검사
        :return:
        """
        _VALUE = "Left"
        _WRONG_VALUE = "ABC"

        # 값 입력 유무 검사
        args = '--clicktype'
        with self.assertRaises(ArgsError):
            _main(*G_PARAMS, args)

        # 유효 값 오류 검사
        args = '--clicktype', _WRONG_VALUE
        with self.assertRaises(ArgsError):
            _main(*G_PARAMS, args)

        # 유효 값 검사
        args = '--clicktype', _VALUE
        _main(*G_PARAMS, args)

