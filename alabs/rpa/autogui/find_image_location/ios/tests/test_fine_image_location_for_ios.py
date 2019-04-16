#!/usr/bin/env python
"""
====================================
 :mod: Test case for Config Module
====================================
.. module author:: 김인중 <nebori92@gmail.com>
.. note:: MIT License
"""

################################################################################
import os
from alabs.common.util.vvargs import ArgsError
from alabs.rpa.autogui.find_image_location.ios import screenshot_ios, \
    compare_image
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
        self.screenshot_path = 'test.png'
        self.url = 'http://localhost'
        self.port = '8100'

    # ==========================================================================
    def tearDown(self):
        if os.path.exists(self.screenshot_path):
            os.remove(self.screenshot_path)

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)

    # ==========================================================================
    def test0100_screenshot_for_ios(self):
        expectation_result = True
        result = screenshot_ios(url= self.url, port= self.port,
                                screenshot_path=self.screenshot_path)
        self.assertEqual(expectation_result, result)

    # ==========================================================================
    def test0110_compare_image(self):
        expectation_result = True
        result = False
        screenshot_ios(url=self.url, port=self.port,
                       screenshot_path=self.screenshot_path)
        location = compare_image(self.screenshot_path, self.screenshot_path)
        if location is not None:
            result = True
        self.assertEqual(expectation_result, result)



