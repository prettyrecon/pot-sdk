#!/usr/bin/env python
"""
====================================
 :mod: Test case for Config Module
====================================
.. module author:: 임덕규 <hong18s@gmail.com>
.. note:: MIT License
"""

################################################################################
import json
from alabs.rpa.desktop.compare_text.linux import main, compare_values
from alabs.common.util.vvtest import captured_output
from unittest import TestCase


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
    def test_1000_argument_compare_values(self):
        self.assertTrue(compare_values("1", "==", "1"))
        # 문자열
        self.assertTrue(compare_values(
            json.dumps("Hello"),"==", json.dumps("Hello")))
        self.assertTrue(compare_values(
            json.dumps("Hello"), "!=", json.dumps("Hell")))

        self.assertTrue(compare_values("1", "==", "1"))
        self.assertFalse(compare_values("1", "!=", "1"))
        self.assertTrue(compare_values("2", ">", "1"))
        self.assertTrue(compare_values("2", ">=", "1"))
        self.assertTrue(compare_values("2", ">=", "2"))
        self.assertTrue(compare_values("2", "<=", "2"))
        self.assertTrue(compare_values("1", "<=", "2"))

        # 에러 처리
        with self.assertRaises(ValueError):
            compare_values("import sys", "==", "')")
        with self.assertRaises(ValueError):
            compare_values(json.dumps("Hello"), ">", json.dumps("Hello"))

    # ==========================================================================
    def test_1010_compare(self):
        # True
        with captured_output() as (out, err):
            main(json.dumps("Hello"), "==", json.dumps("Hello"))
        self.assertEqual(out.getvalue().strip(), 'true')

        # True and True
        with captured_output() as (out, err):
            main(json.dumps("Hello"), "==", json.dumps("Hello"),
                 '-c', 'AND', '10', '==', '10')
        self.assertEqual(out.getvalue().strip(), 'true')

        # True and False
        with captured_output() as (out, err):
            main(json.dumps("Hello"), "==", json.dumps("Hello"),
                 '-c', 'AND', '10', '!=', '10')
        self.assertEqual(out.getvalue().strip(), 'false')

        # True and False or True
        with captured_output() as (out, err):
            main(json.dumps("Hello"), "==", json.dumps("Hello"),
                 '-c', 'AND', '10', '!=', '10',
                 '-c', 'OR', '10', '>', '9')
        self.assertEqual(out.getvalue().strip(), 'true')


