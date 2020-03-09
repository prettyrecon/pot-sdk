#!/usr/bin/env python
# coding=utf8
"""
====================================
 :mod:`alabs.pam.tests.test_me.tests.test_me`
====================================
.. moduleauthor:: Jerry Chae <mcchae@argos-labs.com>
.. note:: ARGOS-LABS License

Description
===========
ARGOS LABS plugin module : unittest
"""
# Authors
# ===========
#
# * Jerry Chae
#
# Change Log
# --------
#
#  * [2019/10/09]
#     - chagne --lang choices into real language name
#  * [2019/04/25]
#     - add arguments' display_name
#  * [2019/03/08]
#     - starting

################################################################################
import os
import sys
from unittest import TestCase


################################################################################
class TU(TestCase):
    # ==========================================================================
    isFirst = True

    # ==========================================================================
    def test0000_init(self):
        self.assertTrue(True)


    # ==========================================================================
    def test9999_quit(self):
        self.assertTrue(True)
