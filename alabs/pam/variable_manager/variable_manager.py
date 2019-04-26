import re
import enum
import hvac
from alabs.common.util.vvjson import get_xpath, set_xpath
from alabs.pam.variable_manager import EXTERNAL_STORE_TOKEN, \
    EXTERNAL_STORE_ADDRESS_PORT, EXTERNAL_STORE_NAME


PATTERN = r'\{\{(.+)\}\}'
GROUP_VARIABLE_NAME = r'(\w+)[.](\w+)\(?.+?\)?'
VAR_OPEN = '{{'
VAR_CLOSE = '}}'
ARRAY_OPEN = '('
ARRAY_CLOSE = ')'
DELIMITERS = '{{', '}}', '(', ')', '@', ','
DELIMITERS_PATTERN = '|'.join(map(re.escape, DELIMITERS))
PAIR = {VAR_OPEN: VAR_CLOSE, ARRAY_OPEN: ARRAY_CLOSE}


################################################################################
class Sign(enum.Enum):
    GLOBAL = '@'


################################################################################
class ArrayFunction(enum.Enum):
    COUNT = 'COUNT'
    APPEND = 'APPEND'
    LAST = 'LAST'


################################################################################
class ParsingError(Exception):
    pass


class Client:
    def __init__(self, url='http://localhost:8200', token=None,
                 cert=None, verify=True, timeout=30, proxies=None,
                 allow_redirects=True, session=None, adapter=None, namespace=None):
        self.client = hvac.Client(url, token, cert, verify, timeout, proxies,
                 allow_redirects, session, adapter, namespace)

    def __enter__(self):
        return self.client

    def close(self):
        self.client.logout()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()


################################################################################
def get_delimiter_index(pattern):
    """
    문자열에서 지정된 구분자 단위로 분리한 "Offset"을 반환한다.
    :param pattern:
        Example >
        'Hello World {{ABC.VARIABLE_TEXT}} End'
        '{Hello World ({{ABC.VARIABLE_TEXT({{DEF.VARIABLE_TEXT}})}})} End'
    :return:
        [0, 12, 14, 31, 33, 37]
        [0, 13, 14, 14, 16, 33, 34, 34, 36, 53, 55, 55, 56, 56, 58, 58, 59, 64]
    """
    idx = [(v.start(), v.end()) for v in
           re.finditer(DELIMITERS_PATTERN, pattern)]
    # re.finditer 는 주어진 패턴에 해당된 문자의 시작과 끝을 반환
    # >>> list(re.finditer(DELIMITERS_PATTERN, "{{ABC.DEF}}"))
    # [<re.Match object; span=(0, 2), match='{{'>,
    # <re.Match object; span=(9, 11), match='}}'>]

    print(idx)
    idx = [i for sub in idx for i in sub]
    if not idx:
        idx = [0, len(pattern)]
    if 0 != idx[0]:
        idx.insert(0, 0)
    if len(pattern) != idx[-1]:
        idx.append(len(pattern))

    # 한 개의 문자 처리 과정에서 인덱스가 넘버가 중복으로 생기는 부분을 제거
    idx = list(set(idx))
    idx.sort()
    return idx


################################################################################
def split(text:str)->list:
    """
    지정된 구분자 단위로 문자열을 분리한 문자열 리스트를 반환한다.
    :param text:
        '{{ABC.VARIABLE_TEXT}}'
        '{{ABC.VARIABLE_TEXT(0)}}'
    :return:
        ['{{', 'ABC.VARIABLE_TEXT', '}}']
        ['{{', 'ABC.VARIABLE_TEXT', '(', '0', ')', '}}']
    """
    if not text:
        raise ValueError('The argument text is empty.')

    def separate(t:str, idx:list, word=None, s=0, e=1)->list:
        word = [] if not word else word
        if e >= len(idx):
            return word
        word.append(t[idx[s]:idx[e]])
        return separate(t, idx, word, s + 1, e + 1)

    index = get_delimiter_index(text)
    value = separate(text, index)
    return value


################################################################################
def split_string_variables(data:str, idx, stack=None, value='', variables=''):
    """
    * 서식(Format) 문자열과 문자열 변수를 분리
    * 지정된 구분자를 찾을때 까지 문자열을 탐색
    * 일반 문자열은 value에 저장
    * 변수 문자열은 varialbes에 저장
    * '{{' 다음 구분자는 '(' 또는 '}}' 가 올 수 있다.
    * '(' 다음 구분자는 ')'를 요구한다.

    EXAMPLE_29 = 'Hello World {{ABC.VARIABLE_TEXT}} End'
    'Hello World {} End', '{{ABC.VARIABLE_TEXT}}'
    """
    if stack is None:
        stack = list()

    if len(idx) == 1:
        # 모든 문자 파싱 끝
        variables = variables.split('|')
        variables.pop()
        return value, tuple(variables)

    t = data[idx[0]:idx[1]]
    # print("t:{}\ndata:{}\nidx:{}\nstack:{}\nvalue:{}\nvariables:{}".format(t, data, idx, stack, value, variables))
    # print()
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
            # 값은 문자열로 합치고 구분자로 `|` 사용
            variables += '|'

    idx.pop(0)
    return split_string_variables(data, idx, stack, value, variables)


################################################################################
class Variables(dict):
    """
    변수 관리 매니져
    xpath를 이용해서 값 가져오고나 넣기 가능
    """

    # ==========================================================================
    def convert(self, text):
        idx = get_delimiter_index(text)
        form, variables = split_string_variables(text, idx)

        # 변수 사용이 없는 문자열일 경우
        if not variables:
            return text

        arg = list()
        option = dict(store='LOCAL', array_function=None)
        for v in variables:
            t = split(v)
            value, path, *_ = self.parse(t, option=option)
            array_function = option.setdefault('array_function', None)
            if array_function == ArrayFunction.APPEND.value:
                # TODO: 전용 Exception Class 를 만들기
                # APPEND는 값을 가져올 때는 사용하지 못함
                raise ValueError("Array Function - "
                                 "'APPEND' IS FOR SETTING ONLY")
            arg.append(value)
        return form.format(*arg)

    # ==========================================================================
    def get_by_argos_variable(self, variable, raise_exception=False):
        """
        ARGOS 변수형태로 위치 값을 찾아서 값 반환
        :param variable: {{ABC.DEF[1]}}
        :return:
        """
        idx = get_delimiter_index(variable)
        _, variables = split_string_variables(variable, idx)

        # 변수 사용이 없는 문자열일 경우
        if not variables:
            raise ValueError

        t = split(variables[0])
        value, path, option = self.parse(t)
        array_function = option.setdefault('array_function', None)
        if array_function == ArrayFunction.APPEND.value:
            # TODO: 전용 Exception Class 를 만들기
            # APPEND는 값을 가져올 때는 사용하지 못함
            raise ValueError("Array Function - "
                             "'APPEND' IS FOR SETTING ONLY")

        value = self.get_by_xpath(path, option['store'], raise_exception)
        return value

    # ==========================================================================
    def set_by_argos_variable(self, variable, value):
        """
        ARGOS 변수형태로 위치 값을 찾아서 값 저장
        :param variable: {{ABC.DEF[1]}}
        :param value: 값
        :return:
        """
        idx = get_delimiter_index(variable)
        _, variables = split_string_variables(variable, idx)

        # 변수 사용이 없는 문자열일 경우
        if not variables:
            raise ValueError

        t = split(variables[0])
        _, path, option = self.parse(t)
        return self.set_by_xpath(path,  value, option['store'])

    # ==========================================================================
    def set_by_xpath(self, xpath:str, value:object, sign:str)->None:
        if sign == Sign.GLOBAL.name:
            self._global_set_by_xpath(xpath, value)
        else:
            self._local_set_by_xpath(xpath, value)

    # ==========================================================================
    def get_by_xpath(self, xpath:str, sign:str, raise_exception=False):

        if sign == Sign.GLOBAL.name:
            value = self._global_get_by_xpath(xpath)
        else:
            value = self._local_get_by_xpath(xpath, raise_exception)
        return value

    # ==========================================================================
    def _local_set_by_xpath(self, xpath:str, value:object)-> None:
        """
        주어진 xpath에 값을 입력
        :param xpath: 'a/b/e/f/g'
        :param value: object
        :return:
        """
        set_xpath(self, xpath, value)


    # ==========================================================================
    def _local_get_by_xpath(self, xpath:str, raise_exception=False):
        """
        :param xpath: 'a/b/e/f/g'
        :return: object
        """
        return get_xpath(self, xpath, raise_exception=raise_exception)


    # ==========================================================================
    def _global_set_by_xpath(self, xpath: str, value: object) -> None:
        """
        주어진 xpath에 값을 입력
        :param xpath: 'a/b/e/f/g'
        :param value: object
        :return:
        """
        data = dict()
        try:
            with Client( url=EXTERNAL_STORE_ADDRESS_PORT,
                              token=EXTERNAL_STORE_TOKEN) as client:
                v = client.read(EXTERNAL_STORE_NAME)
                if v:
                    data = v['data']['variables']
                set_xpath(data, xpath, value)

                client.write(EXTERNAL_STORE_NAME, variables=data)
        except Exception as e:
            print(e)
            raise


    # ==========================================================================
    def _global_get_by_xpath(self, xpath: str):
        """
        :param xpath: 'a/b/e/f/g'
        :return: object
        """
        try:
            with Client(url=EXTERNAL_STORE_ADDRESS_PORT,
                        token=EXTERNAL_STORE_TOKEN) as client:
                print('is_authenticated? %s' % client.is_authenticated())
                data = client.read(EXTERNAL_STORE_NAME)['data']['variables']
                return get_xpath(data, xpath)
        except KeyError as e:
            print(e)
            raise

    # ==========================================================================
    def _global_delete_by_xpath(self, xpath):
        try:
            with Client(url=EXTERNAL_STORE_ADDRESS_PORT,
                        token=EXTERNAL_STORE_TOKEN) as client:
                print('is_authenticated? %s' % client.is_authenticated())
                client.delete(EXTERNAL_STORE_NAME + xpath)
        except KeyError as e:
            print(e)
            raise

    # ==========================================================================
    def parse(self, data: list, stack=None, parsed='', option=None):
        """
        :param data:
            Example: Hello World, {{abc.def.ghi}}
        :param stack:
        :param parsed:
        :param option:
        :return:
        """

        if stack is None and parsed == '':
            stack = list()
            parsed = str()
        if not option:
            option = dict(store='LOCAL')

        # 탈출
        if not data:
            if stack:
                raise ParsingError("{}".format(str(stack)))
            path = parsed.replace('.', '/')

            store = option.setdefault('store', 'LOCAL')
            array_function = option.setdefault('array_function', None)

            if not array_function:
                value = self.get_by_xpath(path, store)

            elif array_function == 'COUNT':
                value = len(self.get_by_xpath(path[:-2], store))

            elif array_function == 'LAST':
                # TODO: OUT OF INDEX 처리 필요
                temporary_value = self.get_by_xpath(path[:-2], store)
                value = temporary_value[-1]
                path = path[:-2] + "[{}]".format(len(temporary_value) - 1)

            elif array_function == 'APPEND':
                # TODO: OUT OF INDEX 처리 필요
                temporary_value = self.get_by_xpath(path[:-2], store)
                value = temporary_value[-1]
                path = path[:-2] + "[{}]".format(len(temporary_value))

            else:
                raise ParsingError(
                    "Array Function - {} is not a supported function")

            return value, path, option

        t = data.pop(0)
        if t == '{{':
            stack.append(t)
        elif t == '(':
            stack.append(t)
            result = self.parse(data, stack, option=option)
            parsed += ''.join(["[{}]".format(x) for x in result.split(",")])

        # Sign
        elif t == Sign.GLOBAL.value:
            option['store'] = Sign.GLOBAL.name

        # List 처리
        elif t == ',':
            parsed += ','
            parsed += self.parse(data, stack, option=option)
            return parsed

        elif t.upper() in tuple(map(lambda n: n.name, ArrayFunction)):
            option['array_function'] = t.upper()

        # t의 값이 '}}', 값을 요청하여 리턴
        # 조건: 스택 마지막이 '{{' 이거나 ')'일 경우
        elif t == ')' and stack[-1] == '(':
            stack.pop()
            return parsed
        elif t == '}}':
            stack.pop()
            if stack:
                v = self.get_by_xpath(parsed.replace('.', '/'), option['store'])
                return self.parse(data, stack, str(v), option)
        else:
            parsed = t
            return self.parse(data, stack, parsed, option)

        # 가장 깊이 중첩되어 있는 값 부터 처리
        return self.parse(data, stack, parsed, option)



