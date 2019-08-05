import unittest
import os
from requests import Response
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI
# from alabs.pam.variable_manager import ResponseData, ResponseErrorData


import warnings

################################################################################
# 작성된 "EXAMPLE"은 절대 수정 금지
# 추가한 "EXAMPLE"은 테스트에 추가 필요
EXAMPLE_00 = 'Hello World'
EXAMPLE_01 = '{{ABC}}'
EXAMPLE_10 = '{{ABC.DEF}}'
EXAMPLE_11 = '{{ABC.DEF.GHI}}'

# Array
EXAMPLE_20 = '{{ABC.DEF(1)}}'
EXAMPLE_21 = '{{ABC.DEF({{DEF.GHI}})}}'
EXAMPLE_22 = '{{ABC.DEF(1,2)}}'
EXAMPLE_23 = '{{ABC.DEF(1,2,3)}}'
EXAMPLE_24 = '{{ABC.DEF(1,2,{{DEF.GHI}})}}'

EXAMPLE_30 = """Hello {{ABC.DEF}} World"""
EXAMPLE_31 = """Hello {{ABC.DEF}} World Hi {{DEF.GHI}} Jo"""
EXAMPLE_32 = """Hello {{ABC.DEF}} World\nHi {{DEF.GHI}} Jo"""

# GLOBAL Store
EXAMPLE_90 = '{{@ABC}}'
EXAMPLE_100 = '{{@ABC.DEF}}'
EXAMPLE_101 = '{{@ABC.DEF.GHI}}'

# GLOBAL Store Array
EXAMPLE_120 = '{{@ABC.DEF(1)}}'
EXAMPLE_121 = '{{@ABC.DEF({{DEF.GHI}})}}'
EXAMPLE_122 = '{{@ABC.DEF(1,2)}}'
EXAMPLE_123 = '{{@ABC.DEF(1,2,3)}}'
EXAMPLE_124 = '{{@ABC.DEF(1,2,{{DEF.GHI}})}}'

EXAMPLE_130 = """Hello {{@ABC.DEF}} World"""
EXAMPLE_131 = """Hello {{@ABC.DEF}} World Hi {{DEF.GHI}} Jo"""
EXAMPLE_132 = """Hello {{@ABC.DEF}} World\nHi {{DEF.GHI}} Jo"""

# XPATH
EXAMPLE_XPATH_01 = 'ABC'
EXAMPLE_XPATH_10 = 'ABC/DEF'
EXAMPLE_XPATH_11 = 'ABC/DEF/GHI'
EXAMPLE_XPATH_20 = 'ABC/DEF/1'
EXAMPLE_XPATH_22 = 'ABC/DEF/1/2'
EXAMPLE_XPATH_23 = 'ABC/DEF/1/2/3'

# Error


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test


################################################################################
class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self):
        self.pid = os.getpid()
        self.vars = VariableManagerAPI(pid=self.pid)

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test_100_create(self):
        value = "Hello"
        # 성공 케이스
        code, data = self.vars.create("{{DEF.GHI}}", value)
        self.assertEqual(200, code)

    # ==========================================================================
    def test_101_create_incorrect_path(self):
        # 실패 케이스
        value = "Hello"
        code, data = self.vars.create("{DEF.GHI}}", value)
        expect = {'message': '{DEF.GHI}} is a wrong variable name'}
        self.assertEqual(400, code)
        self.assertDictEqual(expect, data)

    # ==========================================================================
    def test_200_get(self):
        value = "Hello"
        path = "{{DEF.GHI}}"

        # 데이터가 있고, 값이 올바를 경우
        code, data = self.vars.create(path, value)
        self.assertEqual(200, code)

        code, data = self.vars.get(path)
        self.assertEqual(200, code)
        self.assertEqual(value, data)

    # ==========================================================================
    def test_201_get_non_existent(self):
        non_existent_path = "{{EF.GHI}}"
        # 데이터가 없을 경우 207
        code, data = self.vars.get(non_existent_path)
        self.assertEqual(207, code)

    # ==========================================================================
    def test_202_get_incorrect_path(self):
        non_existent_path = "{{EF.GHI}"
        # 잘못된 변수형태
        code, data = self.vars.get(non_existent_path)
        self.assertEqual(400, code)

    # ==========================================================================
    def test_203_using_incorrect_or_not_supported_array_function(self):
        non_existent_path = "{{EF.GHI(COUN)}}"
        # 잘못된 변수형태
        code, data = self.vars.get(non_existent_path)
        self.assertEqual(400, code)

    # ==========================================================================
    def test_300_convert_local(self):
        value = 'Hello'
        statement = '{{DEF.GHI}} World!'
        path = "{{DEF.GHI}}"

        self.vars.create(path, value)
        code, data = self.vars.convert(statement)
        self.assertEqual(200, code)
        self.assertEqual('Hello World!', data)

    # ==========================================================================
    def test_301_convert_non_existent_path(self):
        value = 'Hello'
        statement = '{{DE.ABC}} World!'
        path = "{{DEF.ABC}}"
        expect = {'message': "ftjson.get_xpath: Invalid Key <'DE'>"}

        code, data = self.vars.create(path, value)
        self.assertEqual(200, code)

        code, data = self.vars.convert(statement)
        self.assertEqual(207, code)
        # 데이터가 없을 때는 None 이라고 기록
        self.assertDictEqual(expect, data)

    # ==========================================================================
    def test_302_convert_incorrect_path(self):
        value = 'Hello'
        statement = '{DEF.ABC}} World!'
        path = "{{DEF.ABC}}"

        self.vars.create(path, value)
        code, data = self.vars.convert(statement)
        # 데이터가 없을 때는 None 이라고 기록
        self.assertEqual(statement, data)

    # ==========================================================================
    def test_400_long_data(self):
        path = "{{DEF.ABC}}"
        with open("mailoutput.txt", 'r') as fs:
            d = fs.read()
        code, data = self.vars.create(path, d)
        self.assertEqual(200, code)

        code, data = self.vars.get(path)
        self.assertEqual(200, code)
