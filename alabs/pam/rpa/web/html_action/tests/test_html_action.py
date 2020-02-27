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
from alabs.pam.rpa.web.html_action import main as _main
from alabs.pam.rpa.web.html_action import tags_to_xpath_parser
from alabs.pam.rpa.web.html_action import tags_to_xpath
from unittest import TestCase


################################################################################



################################################################################
class TU(TestCase):

    # ==========================================================================
    def setUp(self):
        pass

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test_100_tags_to_xpath_parser(self):
        tag_name = 'example_name'
        attr_type = 'class'
        attr_value = 'example_value'
        argspec = tags_to_xpath_parser(
            [tag_name, attr_type, attr_value])
        self.assertEqual(argspec.tag_name, tag_name)
        self.assertEqual(argspec.attr_type, attr_type)
        self.assertEqual(argspec.attr_value, attr_value)

    def test_110_tags_to_xpath(self):
        tag_name = 'input'
        attr_type = 'name'
        attr_value = 'vehicle2'
        xpath = '//body/*/input[@name="vehicle2"]'
        self.assertEqual(
            xpath, tags_to_xpath([tag_name, attr_type, attr_value]))








