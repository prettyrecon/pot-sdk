import re
import unittest

GROUP_1 = 'ABC'
GROUP_2 = 'DEF'
VARIABLE_NAME_1 = 'VARIABLE_TEXT'
VARIABLE_NAME_2 = 'VARIABLE_ARRAY'
INDEX = '0'

# Get
# {{GROUP.NAME}}
EXAMPLE_1 = '{{{{{GROUP}.{NAME}}}}}'.format(GROUP=GROUP_1, NAME=VARIABLE_NAME_1)
# {{GROUP.NAME(INDEX)}}
EXAMPLE_2 = '{{{{{GROUP}.{NAME}({INDEX})}}}}'.format(
    GROUP=GROUP_1, NAME=VARIABLE_NAME_2, INDEX=INDEX)

# EXAMPLE_3 = '{{ABC.VARIABLE_TEXT($)}}'

# Set
# EXAMPLE_4 = '{{ABC.VARIABLE_TEXT(3)}}'
# EXAMPLE_5 = '{{ABC.VARIABLE_TEXT(7)}}'
# EXAMPLE_6 = '{{ABC.VARIABLE_TEXT(+)}}'
# EXAMPLE_7 = '{{ABC.VARIABLE_TEXT($)}}'
# EXAMPLE_8 = '{{ABC.VARIABLE_TEXT}}'

# Nested Variables

# EXAMPLE_20 = '{{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT}})}}'
EXAMPLE_20 = '{{{{{GROUP_1}.{NAME_1}({{{{{GROUP_2}.{NAME_2}}}}})}}}}'.format(
    GROUP_1=GROUP_1, NAME_1=VARIABLE_NAME_2,
    GROUP_2=GROUP_2, NAME_2=VARIABLE_NAME_1)


# EXAMPLE_21 = '{{ABC.VARIABLE_TEXT({{DEF.VARIABLE(0)}})}}'
# EXAMPLE_22 = '{{ABC.VARIABLE_TEXT({{DEF.VARIABLE({{C.VARIABLE}})}})}}'
# EXAMPLE_23 = '{{ABC.VARIABLE_TEXT(' \
#                 '{{DEF.VARIABLE(' \
#                     '{{C.VARIABLE}}' \
#                 ')' \
#              '}}' \
#              ')' \
#              '}}' \
#              ' {{D.VARIABLE}}'

# Mixed Varialbes

EXAMPLE_30 = 'Hello World {{ABC.VARIABLE_TEXT}} End'
EXAMPLE_31 = 'Hello World {{ABC.VARIABLE_ARRAY(0)}} End'
EXAMPLE_32 = 'Hello World {{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT}})}} End'

EXAMPLE_40 = '{Hello World ({{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}})} End'
EXAMPLE_41 = '{Hello World ({{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}})} ' \
             '(something) End'
EXAMPLE_42 = '{Hello World ({{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}})} ' \
             '{{ABC.VARIABLE_TEXT}} End'


VARIABLE_VALUE_TEXT = 'Text Value'
VARIABLE_VALUE_ARRAY = ['12345', '6789']


################################################################################
class VariableForLa(dict):
    pattern = r'\{\{(.+)\}\}'
    group_variable_name = r'(\w+)[.](\w+)\(?.+?\)?'
    VAR_OPEN = '{{'
    VAR_CLOSE = '}}'
    ARRAY_OPEN = '('
    ARRAY_CLOSE = ')'
    DELIMITERS = "{{", "}}", "(", ")"
    DELIMITERS_PATTERN = '|'.join(map(re.escape, DELIMITERS))
    PAIR = {VAR_OPEN:VAR_CLOSE, ARRAY_OPEN:ARRAY_CLOSE}

    # ==========================================================================
    def _parser_group_var_name(self, text):
        """
        :param text:
        :return:
        >>> print(self._parser_group_var_name('A.VARIABLE_TEXT({{B.VARIABLE}})'))
        (A, VARIABLE_TEXT)
        """
        group_name, variable_name = re.match(
            self.group_variable_name, text).groups()
        return group_name, variable_name

    # ==========================================================================
    def _separate(self, t, idx, word=None, s=0, e=1):
        word = [] if not word else word
        if e >= len(idx):
            return word
        word.append(t[idx[s]:idx[e]])
        return self._separate(t, idx, word,  s+1, e+1)

    # ==========================================================================
    def _split(self, t):
        """
        :param t:
            '{{ABC.VARIABLE_TEXT}}'
            '{{ABC.VARIABLE_TEXT(0)}}'
            '{{ABC.VARIABLE_TEXT($)}}'
        :return:
            ['{{', 'ABC.VARIABLE_TEXT', '}}']
            ['{{', 'ABC.VARIABLE_TEXT', '(', '0', ')', '', '}}']
        """
        # idx = [(v.start(), v.end()) for v in re.finditer(
        #     self.DELIMITERS_PATTERN, t)]
        # idx = [i for sub in idx for i in sub]
        idx = self._get_delimiter_index(t)
        value = self._separate(t, idx)
        return [x for x in value if x]

    @classmethod
    def _get_delimiter_index(cls, pattern):
        """
        :param pattern:
            Example >
            'Hello World {{ABC.VARIABLE_TEXT}} End'
            '{Hello World ({{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}})} End'
        :return:

        """
        idx = [(v.start(), v.end()) for v in
               re.finditer(cls.DELIMITERS_PATTERN, pattern)]
        idx = [i for sub in idx for i in sub]
        if 0 != idx[0]:
            idx.insert(0, 0)
        if len(pattern) != idx[-1]:
            idx.append(len(pattern))
        return idx

    def _split_string_variables(
            self, data:str, idx, stack=None, value='', variables=''):
        """
        * 지정된 구분자를 찾을때 까지 문자열을 탐색
        * 일반 문자열은 value에 저장
        * 변수 문자열은 varialbes에 저장
        * '{{' 다음 구분자는 '(' 또는 '}}' 가 올 수 있다.
        * '(' 다음 구분자는 ')'를 요구한다.
        # todo: 현재는 배열 인덱스에 변수 사용불가
        EXAMPLE_29 = 'Hello World {{ABC.VARIABLE_TEXT}} End'

        :param t:
        :return:
        """
        if stack is None:
            stack = list()

        if len(idx) == 1:
            # 모든 문자 파싱 끝
            variables = variables.split('|')
            variables.remove('')
            return value, tuple(variables)

        t = data[idx[0]:idx[1]]

        if stack:
            variables += t
        elif not stack and t not in ('{{', '}}'):
            # '{', '}' 문자일 경우 format 사용시 문제가 되므로 '{{', '}}'으로 변경
            # {hello} -> {{hello}}
            tv = t.replace('{','{{')
            tv = tv.replace('}','}}')
            value += tv

        if t == '{{':
            if not stack:
                value += '{}'
                variables += t
            stack.append(t)
        elif t == '(':
            if stack:
                stack.append(t)
        elif t == ')':
            if stack:
                stack.pop()
        elif t == '}}':
            stack.pop()
            if not stack:
                variables += '|'

        idx.pop(0)
        return self._split_string_variables(data, idx, stack, value, variables)

    # ==========================================================================
    def _variable_parser(self, data:list, stack=None):
        """
        사용자 문자열 변수 값을 분석하여 해당 변수의 값을 가져온다.
        :param data:
            {{ABC.VARIABLE}}
            {{ABC.VARIABLE(0)}}
            {{ABC.VARIABLE}} {{ABC.VARIABLE(0)}}
        :param stack:
        :param depth:
        :return:
        """
        if stack is None:
            stack = list()

        t = data.pop(0)
        if t in self.PAIR.values():
            value = stack.pop()
            if t == self.PAIR['{{']:
                value = value.split('.')
                return self[value[0]][value[1]]
            else:
                # (0) 배열일때
                return  value
        else:
            stack.append(t)
            if t == '(':
                idx = self._variable_parser(data, stack)
                while stack[-1] in self.PAIR:
                    stack.pop()
                value = stack.pop()
                value = value.split('.')
                return self[value[0]][value[1]][int(idx)]

        return self._variable_parser(data, stack)

    # ==========================================================================
    def create(self, group_name:str, variable_name:str)->dict:
        """
        그룹과 변수 생성시 사용
        그룹이 없다면 주어진 그룹명을 이용하여 생성
        :param group_name:
        :param variable_name:
        :return:
        """
        if group_name not in self:
            self[group_name] = dict()
        self[group_name][variable_name] = None
        return self

    # ==========================================================================
    def _set_as_text(self, group_name, variable_name, value:str):
        """
        Text 형태의 변수 선언시 사용
        todo: 아직 어떻게 쓰일지 정해지지 않았음
        :param group_name:
        :param variable_name:
        :param value:
        :return:
        """
        self[group_name][variable_name] = value

    # ==========================================================================
    def set_value(self, group_name, variable_name, variable_type, value, idx=None):
        """
        다양한 방법으로 변수를 선언할때 사용
        :param group_name:
        :param variable_name:
        :param variable_type:
        :param value:
        :param idx:
        :return:
        """
        if variable_type == 'Text':
            self._set_as_text(group_name, variable_name, value)

    # ==========================================================================
    def get_value(self, group_name, variable_name, idx=None):
        value = self[group_name][variable_name]
        if isinstance(value, str):
            return value

    # ==========================================================================
    def convert(self, statement:str)->str:
        """
        문장안에 사용된 변수를 찾아서 값을 치환하여 다시 문장을 반환
        :param statement:
        :return:
        """
        idx = self._get_delimiter_index(statement)
        data = self._split_string_variables(statement, idx)
        data_index = [self._split(x) for x in data[1]]
        value = [self._variable_parser(x) for x in data_index]
        return data[0].format(*value)



class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self):
        self.vars = VariableForLa()

    # ==========================================================================
    def tearDown(self):
        pass

    # ==========================================================================
    def test_100_create(self):
        """
        create는 자동으로 그룹여부를 확인하여 생성
        :return:
        """
        self.vars.create(GROUP_1, VARIABLE_NAME_1)
        self.assertEqual(None, self.vars[GROUP_1][VARIABLE_NAME_1])

    # ==========================================================================
    def test_101_create_and_add(self):
        """
        create는 자동으로 그룹여부를 확인하여 생성
        :return:
        """
        self.vars.create(GROUP_1, VARIABLE_NAME_1)
        self.vars.create(GROUP_1, VARIABLE_NAME_2)
        self.assertEqual(None, self.vars[GROUP_1][VARIABLE_NAME_1])
        self.assertEqual(None, self.vars[GROUP_1][VARIABLE_NAME_2])
        # {'ABC': {'VARIABLE_TEXT': None, 'test_2': None}}

    # ==========================================================================
    def test_110_set_value_1(self):
        self.vars.create(GROUP_1, VARIABLE_NAME_1)
        self.vars[GROUP_1][VARIABLE_NAME_1] = VARIABLE_VALUE_TEXT
        # {'ABC': {'VARIABLE_TEXT': 'Text Value'}}

        self.assertEqual(
            VARIABLE_VALUE_TEXT, self.vars[GROUP_1][VARIABLE_NAME_1])

    # ==========================================================================
    def test_200_split_example_1(self):
        # print(self.vars._split(EXAMPLE_1))
        # print(self.vars._split(EXAMPLE_2))
        # print(self.vars._split(EXAMPLE_30))
        # print(self.vars._split(EXAMPLE_4))
        # print(self.vars._split(EXAMPLE_5))
        # print(self.vars._split(EXAMPLE_6))
        pass

    # ==========================================================================
    def test_300_variable_parser(self):

        self.vars.create(GROUP_1, VARIABLE_NAME_1)
        self.vars[GROUP_1][VARIABLE_NAME_1] = VARIABLE_VALUE_TEXT
        data = self.vars._split(EXAMPLE_1)
        value = self.vars._variable_parser(data, [])
        self.assertEqual(value, VARIABLE_VALUE_TEXT)

    # ==========================================================================
    def test_310_variable_parser(self):
        # 배열 처리
        # {'ABC': {'VARIABLE_ARRAY': ['ABC', 'DEF']}}
        # {{ABC.VARIABLE_ARRAY(0)}}
        # ABC
        self.vars.create(GROUP_1, VARIABLE_NAME_2)
        self.vars[GROUP_1][VARIABLE_NAME_2] = VARIABLE_VALUE_ARRAY
        data = self.vars._split(EXAMPLE_2)
        value = self.vars._variable_parser(data, [])
        self.assertEqual(value, VARIABLE_VALUE_ARRAY[0])

    # ==========================================================================
    def test_320_variable_parser(self):
        # 배열 원자 변수 처리
        # {{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT}})}}

        self.vars.create(GROUP_1, VARIABLE_NAME_2)
        self.vars.create(GROUP_2, VARIABLE_NAME_1)
        self.vars[GROUP_1][VARIABLE_NAME_2] = VARIABLE_VALUE_ARRAY
        self.vars[GROUP_2][VARIABLE_NAME_1] = '0'
        data = self.vars._split(EXAMPLE_20)

        value = self.vars._variable_parser(data, [])
        self.assertEqual(value, VARIABLE_VALUE_ARRAY[0])

    # ==========================================================================
    def test_330_split_string_variable(self):
        """
        # 원문
        'Hello World {{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT}})}}{{ABC.A}} End'

        # 값
        ('Hello World {0}{1} End',
        ('{{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT)}}', {{ABC.A}}))

        # 최종 사용
        'Hello World {0}{1}'.format(var1, var2)
        :return:

        """

        # 문장 안에서 변수 사용
        _TEST = ('Hello World {} End', ('{{ABC.VARIABLE_TEXT}}',))
        idx = self.vars._get_delimiter_index(EXAMPLE_30)
        ret = self.vars._split_string_variables(EXAMPLE_30, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_331_split_string_variable(self):
        # 문장 안에서 배열 변수 사용,
        _TEST = ('Hello World {} End',
                   ('{{ABC.VARIABLE_ARRAY(0)}}',))

        idx = self.vars._get_delimiter_index(EXAMPLE_31)
        ret = self.vars._split_string_variables(EXAMPLE_31, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_332_split_string_variable(self):
        # 문장 안에서 배열 변수 사용, 인덱스 값은 변수 사용
        _TEST = ('Hello World {} End',
                 ('{{ABC.VARIABLE_ARRAY({{DEF.VARIABLE_TEXT}})}}',))
        idx = self.vars._get_delimiter_index(EXAMPLE_32)
        ret = self.vars._split_string_variables(EXAMPLE_32, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_333_split_string_variable(self):
        # 문장 안에서 변수 사용, 문장에 '{', '}', '(', ')'  문자 포함
        _TEST = ('{{Hello World ({})}} End',
         ('{{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}}',))
        idx = self.vars._get_delimiter_index(EXAMPLE_40)
        ret = self.vars._split_string_variables(EXAMPLE_40, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_334_split_string_variable(self):
        # 문장 안에서 변수 사용, 문장에 '{', '}', '(', ')'  문자 포함
        _TEST = ('{{Hello World ({})}} (something) End',
                 ('{{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}}',))
        idx = self.vars._get_delimiter_index(EXAMPLE_41)
        ret = self.vars._split_string_variables(EXAMPLE_41, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_335_split_string_variable(self):
        # 문장 안에서 변수 사용, 문장에 '{', '}', '(', ')'  문자 포함
        # 1개 이상의 변수 사용
        _TEST = ('{{Hello World ({})}} {} End', (
        '{{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}}',
        '{{ABC.VARIABLE_TEXT}}'))
        idx = self.vars._get_delimiter_index(EXAMPLE_42)
        ret = self.vars._split_string_variables(EXAMPLE_42, idx)
        self.assertEqual(_TEST, ret)

    # ==========================================================================
    def test_330_variable_parser(self):
        self.vars.create(GROUP_1, VARIABLE_NAME_2)
        self.vars.create(GROUP_2, VARIABLE_NAME_1)
        self.vars[GROUP_1][VARIABLE_NAME_2] = VARIABLE_VALUE_ARRAY
        self.vars[GROUP_2][VARIABLE_NAME_1] = '0'
        data = self.vars._split(EXAMPLE_20)
        value = self.vars._variable_parser(data)
        self.assertEqual(value, VARIABLE_VALUE_ARRAY[0])

    # ==========================================================================
    def test_400_convert_values_in_statement(self):
        """
        문장속에 있는 변수들의 값을 구하여 문장과 함께 반환
        :return:
        """
        self.vars.create(GROUP_1, VARIABLE_NAME_1)
        self.vars.create(GROUP_2, VARIABLE_NAME_1)
        self.vars[GROUP_1][VARIABLE_NAME_1] = VARIABLE_VALUE_ARRAY
        self.vars[GROUP_2][VARIABLE_NAME_1] = '0'
        data = self.vars.convert(
            'Hello {{ABC.VARIABLE_TEXT(1)}} World {{DEF.VARIABLE_TEXT}}')
        self.assertEqual('Hello 6789 World 0', data)







