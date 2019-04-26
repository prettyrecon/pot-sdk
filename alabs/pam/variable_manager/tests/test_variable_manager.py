import unittest
from alabs.pam.variable_manager.variable_manager import \
    get_delimiter_index, split_string_variables, split, Variables
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
EXAMPLE_25 = '{{ABC.DEF(COUNT)}}'
EXAMPLE_26 = '{{ABC.DEF(APPEND)}}'
EXAMPLE_27 = '{{ABC.DEF(LAST)}}'

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
        self.vars = Variables()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test_100_get_delimiter_index(self):
        idx = get_delimiter_index(EXAMPLE_00)
        expected = [0, 11]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_01)
        expected = [0, 2, 5, 7]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_10)
        expected = [0, 2, 9, 11]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_11)
        expected = [0, 2, 13, 15]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_20)
        expected = [0, 2, 9, 10, 11, 12, 14]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_21)
        expected = [0, 2, 9, 10, 12, 19, 21, 22, 24]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_22)
        expected = [0, 2, 9, 10, 11, 12, 13, 14, 16]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_23)
        expected = [0, 2, 9, 10, 11, 12, 13, 14, 15, 16, 18]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_24)
        expected = [0, 2, 9, 10, 11, 12, 13, 14, 16, 23, 25, 26, 28]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_25)
        expected = [0, 2, 9, 10, 15, 16, 18]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_26)
        expected = [0, 2, 9, 10, 16, 17, 19]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_27)
        expected = [0, 2, 9, 10, 14, 15, 17]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_30)
        expected = [0, 6, 8, 15, 17, 23]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_31)
        expected = [0, 6, 8, 15, 17, 27, 29, 36, 38, 41]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_32)
        expected = [0, 6, 8, 15, 17, 27, 29, 36, 38, 41]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_90)
        expected = [0, 2, 3, 6, 8]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_100)
        expected = [0, 2, 3, 10, 12]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_101)
        expected = [0, 2, 3, 14, 16]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_120)
        expected = [0, 2, 3, 10, 11, 12, 13, 15]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_121)
        expected = [0, 2, 3, 10, 11, 13, 20, 22, 23, 25]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_130)
        expected = [0, 6, 8, 9, 16, 18, 24]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_131)
        expected = [0, 6, 8, 9, 16, 18, 28, 30, 37, 39, 42]
        self.assertListEqual(expected, idx)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_132)
        expected = [0, 6, 8, 9, 16, 18, 28, 30, 37, 39, 42]
        self.assertListEqual(expected, idx)

    # ==========================================================================
    def test_105_split_string_variables(self):
        def test_split_string_variables(example, value):
            idx = get_delimiter_index(example)
            _, variables = split_string_variables(example, idx)
            self.assertTupleEqual(value, variables)

        # ----------------------------------------------------------------------
        test_split_string_variables(EXAMPLE_01, ('{{ABC}}',))
        test_split_string_variables(EXAMPLE_10, ('{{ABC.DEF}}',))
        test_split_string_variables(EXAMPLE_11, ('{{ABC.DEF.GHI}}',))
        test_split_string_variables(EXAMPLE_20, ('{{ABC.DEF(1)}}',))
        test_split_string_variables(EXAMPLE_21, ('{{ABC.DEF({{DEF.GHI}})}}',))
        test_split_string_variables(EXAMPLE_22, ('{{ABC.DEF(1,2)}}',))
        test_split_string_variables(EXAMPLE_23, ('{{ABC.DEF(1,2,3)}}',))
        test_split_string_variables(EXAMPLE_24,
                                    ('{{ABC.DEF(1,2,{{DEF.GHI}})}}',))
        test_split_string_variables(EXAMPLE_25,
                                    ('{{ABC.DEF(COUNT)}}',))
        test_split_string_variables(EXAMPLE_26,
                                    ('{{ABC.DEF(APPEND)}}',))
        test_split_string_variables(EXAMPLE_27,
                                    ('{{ABC.DEF(LAST)}}',))
        test_split_string_variables(EXAMPLE_30, ('{{ABC.DEF}}',))
        test_split_string_variables(EXAMPLE_31, ('{{ABC.DEF}}', '{{DEF.GHI}}'))
        test_split_string_variables(EXAMPLE_32, ('{{ABC.DEF}}', '{{DEF.GHI}}'))

        test_split_string_variables(EXAMPLE_90, ('{{@ABC}}',))
        test_split_string_variables(EXAMPLE_100, ('{{@ABC.DEF}}',))
        test_split_string_variables(EXAMPLE_101, ('{{@ABC.DEF.GHI}}',))
        test_split_string_variables(EXAMPLE_120, ('{{@ABC.DEF(1)}}',))
        test_split_string_variables(EXAMPLE_121, ('{{@ABC.DEF({{DEF.GHI}})}}',))
        test_split_string_variables(EXAMPLE_122, ('{{@ABC.DEF(1,2)}}',))
        test_split_string_variables(EXAMPLE_123, ('{{@ABC.DEF(1,2,3)}}',))
        test_split_string_variables(EXAMPLE_124,
                                    ('{{@ABC.DEF(1,2,{{DEF.GHI}})}}',))
        test_split_string_variables(EXAMPLE_130, ('{{@ABC.DEF}}',))
        test_split_string_variables(EXAMPLE_131, ('{{@ABC.DEF}}', '{{DEF.GHI}}'))
        test_split_string_variables(EXAMPLE_132, ('{{@ABC.DEF}}', '{{DEF.GHI}}'))

    # ==========================================================================
    def test_110_split(self):
        def test_split(example, expected):
            idx = get_delimiter_index(example)
            _, variables = split_string_variables(example, idx)
            value = split(variables[0])
            self.assertListEqual(expected, value)

        # ----------------------------------------------------------------------
        # split 은 비어있는 값은 받지 않는다.
        idx = get_delimiter_index(EXAMPLE_00)
        _, variables = split_string_variables(EXAMPLE_00, idx)
        with self.assertRaises(ValueError):
            split(variables)

        # ----------------------------------------------------------------------
        test_split(EXAMPLE_01, ['{{', 'ABC', '}}'])
        test_split(EXAMPLE_10, ['{{', 'ABC.DEF', '}}'])
        test_split(EXAMPLE_11, ['{{', 'ABC.DEF.GHI', '}}'])
        test_split(EXAMPLE_20, ['{{', 'ABC.DEF', '(', '1', ')', '}}'])
        test_split(EXAMPLE_21,
                   ['{{', 'ABC.DEF', '(', '{{', 'DEF.GHI', '}}', ')', '}}'])
        test_split(EXAMPLE_22,
                   ['{{', 'ABC.DEF', '(', '1',',','2', ')', '}}'])
        test_split(EXAMPLE_23,
                   ['{{', 'ABC.DEF', '(', '1',',','2',',','3', ')', '}}'])
        test_split(EXAMPLE_24,
                   ['{{', 'ABC.DEF', '(', '1',',','2',',',
                    '{{', 'DEF.GHI', '}}', ')', '}}'])
        test_split(EXAMPLE_25, ['{{', 'ABC.DEF', '(', 'COUNT', ')', '}}'])
        test_split(EXAMPLE_26, ['{{', 'ABC.DEF', '(', 'APPEND', ')', '}}'])
        test_split(EXAMPLE_27, ['{{', 'ABC.DEF', '(', 'LAST', ')', '}}'])

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_30)
        form, variables = split_string_variables(EXAMPLE_30, idx)
        expected_form = 'Hello {} World'
        expected_value = ['{{', 'ABC.DEF', '}}']
        value = split(variables[0])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value, value)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_31)
        form, variables = split_string_variables(EXAMPLE_31, idx)
        expected_form = 'Hello {} World Hi {} Jo'
        expected_value_0 = ['{{', 'ABC.DEF', '}}',]
        expected_value_1 = ['{{', 'DEF.GHI', '}}',]
        value_0 = split(variables[0])
        value_1 = split(variables[1])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value_0, value_0)
        self.assertListEqual(expected_value_1, value_1)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_32)
        form, variables = split_string_variables(EXAMPLE_32, idx)
        expected_form = 'Hello {} World\nHi {} Jo'
        expected_value_0 = ['{{', 'ABC.DEF', '}}', ]
        expected_value_1 = ['{{', 'DEF.GHI', '}}', ]
        value_0 = split(variables[0])
        value_1 = split(variables[1])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value_0, value_0)
        self.assertListEqual(expected_value_1, value_1)

        # ----------------------------------------------------------------------
        test_split(EXAMPLE_90, ['{{', '@', 'ABC', '}}'])
        test_split(EXAMPLE_100, ['{{', '@', 'ABC.DEF', '}}'])
        test_split(EXAMPLE_101, ['{{', '@', 'ABC.DEF.GHI', '}}'])

        # ----------------------------------------------------------------------
        test_split(EXAMPLE_120, ['{{', '@', 'ABC.DEF', '(', '1', ')', '}}'])
        test_split(
            EXAMPLE_121,
            ['{{', '@', 'ABC.DEF', '(', '{{', 'DEF.GHI', '}}', ')', '}}'])
        test_split(
            EXAMPLE_122,
            ['{{', '@', 'ABC.DEF', '(', '1', ',', '2', ')', '}}'])
        test_split(
            EXAMPLE_123,
            ['{{', '@', 'ABC.DEF', '(', '1', ',', '2',',','3', ')', '}}'])
        test_split(
            EXAMPLE_124,
            ['{{', '@', 'ABC.DEF', '(', '1', ',', '2', ',',
             '{{', 'DEF.GHI', '}}', ')', '}}'])

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_130)
        form, variables = split_string_variables(EXAMPLE_130, idx)
        expected_form = 'Hello {} World'
        expected_value = ['{{', '@', 'ABC.DEF', '}}']
        value = split(variables[0])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value, value)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_131)
        form, variables = split_string_variables(EXAMPLE_131, idx)
        expected_form = 'Hello {} World Hi {} Jo'
        expected_value_0 = ['{{', '@', 'ABC.DEF', '}}', ]
        expected_value_1 = ['{{', 'DEF.GHI', '}}', ]
        value_0 = split(variables[0])
        value_1 = split(variables[1])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value_0, value_0)
        self.assertListEqual(expected_value_1, value_1)

        # ----------------------------------------------------------------------
        idx = get_delimiter_index(EXAMPLE_132)
        form, variables = split_string_variables(EXAMPLE_132, idx)
        expected_form = 'Hello {} World\nHi {} Jo'
        expected_value_0 = ['{{', '@', 'ABC.DEF', '}}', ]
        expected_value_1 = ['{{', 'DEF.GHI', '}}', ]
        value_0 = split(variables[0])
        value_1 = split(variables[1])
        self.assertEqual(expected_form, form)
        self.assertListEqual(expected_value_0, value_0)
        self.assertListEqual(expected_value_1, value_1)

    # ==========================================================================
    def test_200_convert_local(self):
        var = Variables()
        value = 'Hello World'
        self.assertEqual(value, var.convert(EXAMPLE_00))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC', value, 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_01))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', value, 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_10))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF/GHI', value, 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_11))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', [10, value], 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_20))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Python'
        var.set_by_xpath('ABC/DEF', ['C++', value], 'LOCAL')
        var.set_by_xpath('DEF/GHI', 1, 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_21))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', [10, [1, 2, value, 'World']], 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_22))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF',
                         [1, [1, 2, [1, 2, 3 ,value], 'World']], 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_23))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF',
                         [1, [1, 2, [1, 2, 3, 4, value], 'World']], 'LOCAL')
        var.set_by_xpath('DEF/GHI', 4, 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_24))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', [10, value], 'LOCAL')
        self.assertEqual('2', var.convert(EXAMPLE_25))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', [10, value], 'LOCAL')
        with self.assertRaises(ValueError) as cm:
            var.convert(EXAMPLE_26)

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_xpath('ABC/DEF', [10, value], 'LOCAL')
        self.assertEqual(value, var.convert(EXAMPLE_27))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'John'
        var.set_by_xpath('ABC/DEF', value, 'LOCAL')
        self.assertEqual('Hello ' + value + ' World', var.convert(EXAMPLE_30))

        # ----------------------------------------------------------------------
        var = Variables()
        value = ('John', 'Doe')
        form = 'Hello {} World Hi {} Jo'.format(*value)
        var.set_by_xpath('ABC/DEF', value[0], 'LOCAL')
        var.set_by_xpath('DEF/GHI', value[1], 'LOCAL')
        self.assertEqual(form, var.convert(EXAMPLE_31))

        # ----------------------------------------------------------------------
        var = Variables()
        value = ('John', 'Doe')
        form = 'Hello {} World\nHi {} Jo'.format(*value)
        var.set_by_xpath('ABC/DEF', value[0], 'LOCAL')
        var.set_by_xpath('DEF/GHI', value[1], 'LOCAL')
        self.assertEqual(form, var.convert(EXAMPLE_32))
        
    # # ==========================================================================
    # @ignore_warnings
    # def test_210_parse_global(self):
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC', value, 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_90))
    #     var._global_delete_by_xpath("")
    #
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF', value, 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_100))
    #     var._global_delete_by_xpath("")
    #
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF/GHI', value, 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_101))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF', [10, value], 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_120))
    #     var._global_delete_by_xpath("")
    #
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Python'
    #     var.set_by_xpath('ABC/DEF', ['C++', value], 'GLOBAL')
    #     var.set_by_xpath('DEF/GHI', 1, 'LOCAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_121))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF', [10, [1, 2, value, 'World']], 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_122))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF',
    #                      [1, [1, 2, [1, 2, 3 ,value], 'World']], 'GLOBAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_123))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'Hello'
    #     var.set_by_xpath('ABC/DEF',
    #                      [1, [1, 2, [1, 2, 3, 4, value], 'World']], 'GLOBAL')
    #     var.set_by_xpath('DEF/GHI', 4, 'LOCAL')
    #     self.assertEqual(value, var.convert(EXAMPLE_124))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = 'John'
    #     var.set_by_xpath('ABC/DEF', value, 'GLOBAL')
    #     self.assertEqual('Hello ' + value + ' World', var.convert(EXAMPLE_130))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = ('John', 'Doe')
    #     form = 'Hello {} World Hi {} Jo'.format(*value)
    #     var.set_by_xpath('ABC/DEF', value[0], 'GLOBAL')
    #     var.set_by_xpath('DEF/GHI', value[1], 'LOCAL')
    #     self.assertEqual(form, var.convert(EXAMPLE_131))
    #     var._global_delete_by_xpath("")
    #     # ----------------------------------------------------------------------
    #     var = Variables()
    #     value = ('John', 'Doe')
    #     form = 'Hello {} World\nHi {} Jo'.format(*value)
    #     var.set_by_xpath('ABC/DEF', value[0], 'GLOBAL')
    #     var.set_by_xpath('DEF/GHI', value[1], 'LOCAL')
    #     self.assertEqual(form, var.convert(EXAMPLE_132))
    #     var._global_delete_by_xpath("")
    # ==========================================================================
    def test_set_get_by_argos_variable(self):
        var = Variables()
        with self.assertRaises(ValueError) as cm:
            var.set_by_argos_variable(EXAMPLE_00, 12)

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'ARGOS'
        var.set_by_argos_variable(EXAMPLE_01, value)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_01))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable(EXAMPLE_10, value)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_10))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable(EXAMPLE_11, value)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_11))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable('{{ABC.DEF}}', [10, value])
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_20))

        # ----------------------------------------------------------------------
        # 지정된 인덱스의 값을 변경 또는 추가
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable('{{ABC.DEF}}', [10, value])
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_20))

        value = 'World'
        var.set_by_argos_variable('{{ABC.DEF(0)}}', value)
        self.assertEqual(value, var.get_by_argos_variable('{{ABC.DEF(0)}}'))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Python'
        var.set_by_argos_variable('{{ABC.DEF}}', ['C++', value])
        var.set_by_argos_variable('{{DEF.GHI}}', 1)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_21))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable('{{ABC.DEF}}', [10, [1, 2, value, 'World']])
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_22))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable('{{ABC.DEF}}',
                                  [1, [1, 2, [1, 2, 3, value], 'World']])
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_23))

        # ----------------------------------------------------------------------
        var = Variables()
        value = 'Hello'
        var.set_by_argos_variable('{{ABC.DEF}}',
                                  [1, [1, 2, [1, 2, 3, 4, value], 'World']])
        var.set_by_argos_variable('{{DEF.GHI}}', 4)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_24))

        # ----------------------------------------------------------------------
        # ARRAY APPEND 처리
        var = Variables()
        value = 'World'
        var.set_by_argos_variable('{{ABC.DEF}}', ['Hello'])
        var.set_by_argos_variable(EXAMPLE_26, value)
        self.assertEqual(value, var.get_by_argos_variable('{{ABC.DEF}}')[1])

        # ----------------------------------------------------------------------
        # ARRAY LAST 처리
        var = Variables()
        value = 'World'
        var.set_by_argos_variable('{{ABC.DEF}}', ['Hello'])
        var.set_by_argos_variable(EXAMPLE_27, value)
        self.assertEqual(value, var.get_by_argos_variable(EXAMPLE_27))


