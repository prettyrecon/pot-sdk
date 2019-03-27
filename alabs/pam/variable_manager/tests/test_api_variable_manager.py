import unittest
from alabs.pam.variable_manager.rc_api_variable_manager import \
    VariableManagerAPI
from alabs.pam.variable_manager import ResponseData, ResponseErrorData

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
        self.vars = VariableManagerAPI()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test_100_create(self):
        value = "Hello"
        # 성공 케이스
        self.assertIsInstance(
            self.vars.create("{{DEF.GHI}}", value), ResponseData)

        # 실패 케이스
        self.assertIsInstance(
            self.vars.create("{DEF.GHI}}", value), ResponseErrorData)

    # ==========================================================================
    def test_200_get(self):
        value = "Hello"
        path = "{{DEF.GHI}}"
        wrong_path = "{{EF.GHI}}"

        # 데이터가 있고, 값이 올바를 경우
        data = self.vars.create(path, value)
        self.assertEqual(200, data['code'])
        self.assertEqual(value, data['data'])

        # 데이터가 없을 경우 404
        self.assertEqual(404, self.vars.get(wrong_path)['code'])

    # ==========================================================================
    def test_300_convert_local(self):
        value = 'Hello'
        statement = '{{DEF.GHI}} World!'
        statement2 = '{{DEF.ABC}} World!'
        path = "{{DEF.GHI}}"

        self.vars.create(path, value)
        self.assertEqual('Hello World!', self.vars.convert(statement)['data'])

        # 데이터가 없을 때는 None 이라고 기록
        self.assertEqual('None World!', self.vars.convert(statement2)['data'])
