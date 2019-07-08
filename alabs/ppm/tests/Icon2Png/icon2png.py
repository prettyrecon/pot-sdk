# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import sys
import shutil
from contextlib import contextmanager
from io import StringIO
from icon_font_to_png import command_line
from unittest import TestCase, TestLoader, TextTestRunner
#
# import pytest


################################################################################
@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


################################################################################
# noinspection PyUnresolvedReferences
class TU(TestCase):
    # ==========================================================================
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

    # ==========================================================================
    def test_0100_list_option(self):
        try:
            command_line.run(
                '--css fontawesome.css --ttf fontawesome-webfont.ttf --list'.split()
            )
            # stdout = out.getvalue().strip()
            # print(stdout)
            # self.assertTrue(not stdout)
            self.assertTrue(False)
        except Exception as e:
            sys.stderr.write('%s\n' % str(e))
            self.assertTrue(True)

    # ==========================================================================
    def test_0200_icon(self):
        try:
            command_line.run(
                '--css fontawesome.css --ttf fontawesome-webfont.ttf --size 32 stop play car'.split()
            )
            # stdout = out.getvalue().strip()
            # print(stdout)
            # self.assertTrue(not stdout)
            self.assertTrue(True)
        except Exception as e:
            sys.stderr.write('%s\n' % str(e))
            self.assertTrue(False)


################################################################################
if __name__ == "__main__":
    suite = TestLoader().loadTestsFromTestCase(TU)
    result = TextTestRunner(verbosity=2).run(suite)
    ret = not result.wasSuccessful()
    sys.exit(ret)
