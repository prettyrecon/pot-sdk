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
from alabs.rpa.desktop.delete_file import main as _main
from unittest import TestCase
from pathlib import Path


################################################################################
FILES = ['test_1.txt', 'test_2.txt', 'test_3.txt']


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
    def test_100_delete_option_check(self):
        # 값을 입력 안했을 때
        with self.assertRaises(ArgsError):
            _main()

    # ==========================================================================
    def test_100_delete_files(self):
        """
        더미 파일 생성 후, 삭제
        :return:
        """
        for file in FILES:
            Path(file).touch()
        self.assertTrue(not _main(*FILES))

    # ==========================================================================
    def test_101_not_found_files(self):
        """
        파일이 없을때
        :return:
        """
        ret = [('test_1.txt', 'file not found'),
               ('test_2.txt', 'file not found'),
               ('test_3.txt', 'file not found')]

        self.assertListEqual(ret, _main(*FILES))

