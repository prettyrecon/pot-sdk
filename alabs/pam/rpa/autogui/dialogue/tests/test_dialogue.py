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
from alabs.pam.rpa.autogui.dialogue.linux import _main
from alabs.pam.rpa.autogui.dialogue import ACTION, check_args
from unittest import TestCase

EXAMPLE000 = '--button Resume'.split()
EXAMPLE001 = '--button MoveOn "title"'.split()
EXAMPLE002 = '--button TreatAsError "title"'.split()
EXAMPLE003 = '--button IgnoreFailure "title"'.split()
EXAMPLE004 = '--button AbortScenarioButNoError "title"'.split()
EXAMPLE005 = '--button JumpForward "title" 3'.split()
EXAMPLE006 = '--button JumpBackward "title" 3'.split()
EXAMPLE007 = '--button JumpToOperation "title" op'.split()
EXAMPLE008 = '--button JumpToStep "title" step'.split()
EXAMPLE009 = '--button RestartFromTop "title"'.split()

EXAMPLE010 = '--button Resume 1'.split()
EXAMPLE011 = '--button MoveOn'.split()
EXAMPLE012 = '--button TreatAsError 1 1'.split()
EXAMPLE013 = '--button IgnoreFailure Hello World'.split()
EXAMPLE014 = '--button AbortScenarioButNoError "title" 1'.split()
EXAMPLE015 = '--button JumpForward "title"'.split()
EXAMPLE016 = '--button JumpBackward "title" Hello'.split()
EXAMPLE017 = '--button JumpToOperation "title"'.split()
EXAMPLE018 = '--button JumpToStep "title"'.split()
EXAMPLE019 = '--button RestartFromTop'.split()


################################################################################
G_PARAMS = ['0,0',]


################################################################################
class TU(TestCase):

    # ==========================================================================
    def setUp(self):
        pass

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    def test0100_argument_parser_check(self):
        """
        --motion 옵션 검사
        :return:
        """
        self.assertTrue(check_args(_main(*EXAMPLE001)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE002)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE003)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE004)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE005)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE006)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE007)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE008)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE009)[1]))

    # ==========================================================================
    def test0100_argument_parser_check_error(self):
        """
        --motion 옵션 검사
        :return:
        """
        self.assertTrue(check_args(_main(*EXAMPLE010)[1]))
        with self.assertRaises(ValueError):
            check_args(_main(*EXAMPLE011)[1])
        self.assertTrue(check_args(_main(*EXAMPLE012)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE013)[1]))
        self.assertTrue(check_args(_main(*EXAMPLE014)[1]))
        with self.assertRaises(ValueError):
            check_args(_main(*EXAMPLE015)[1])
        self.assertTrue(check_args(_main(*EXAMPLE016)[1]))
        with self.assertRaises(ValueError):
            check_args(_main(*EXAMPLE017)[1])
        with self.assertRaises(ValueError):
            check_args(_main(*EXAMPLE018)[1])

    # ==========================================================================
    def test_argument_click_point(self):
        """
        --coordinates 옵션 검사
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
        --button 옵션 검사
        :return:
        """
        _VALUE = "Left"
        _WRONG_VALUE = "ABC"

        # 값 입력 유무 검사
        args = '--button'
        with self.assertRaises(ArgsError):
            _main(*G_PARAMS, args)

        # 유효 값 오류 검사
        args = '--button', _WRONG_VALUE
        with self.assertRaises(ArgsError):
            _main(*G_PARAMS, args)

        # 유효 값 검사
        args = '--button', _VALUE
        _main(*G_PARAMS, args)

