import unittest
import pathlib
from alabs.pam.scenario import Scenario
from alabs.pam.operations import SetVariable, ExecuteProcess, \
    ImageMatch, TypeText, TypeKeys, SearchImage, Repeat, Delay
from alabs.common.util import vvlogger
from alabs.pam.dumpspec_parser import plugin_spec_parser, get_plugin_dumpspec
from alabs.pam.dumpspec_parser import append
from alabs.pam.dumpspec_parser import store
from alabs.pam.dumpspec_parser import storeconst
from alabs.pam.dumpspec_parser import storefalse
from alabs.pam.dumpspec_parser import storetrue
from alabs.pam.dumpspec_parser import count
from alabs.pam.dumpspec_parser import cast_type


SCENARIO_1 = pathlib.Path('./scenarios/MacOs/'
                          'LA-Scenario0010/LA-Scenario0010.json')

SCENARIO_2 = pathlib.Path('./scenarios/restapi.json')





class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self):
        # logger = vvlogger.get_logger("test_log.log")

        self.scenario = Scenario()


    # ==========================================================================
    def tearDown(self):
        pass

    # # ==========================================================================
    # # def test_100_load_scenario(self):
    #     # 시나리오 파일을 사전형 데이터로 읽어오는지 검사
    #     self.assertIsInstance(self.scenario.load_scenario_file(SCENARIO_2), dict)
    #
    #     # JSON 형태의 파일이 아닐 경우
    #     with self.assertRaises(TypeError) as cm:
    #         self.scenario.load_scenario_file(NOT_SCN)
    #
    # # ==========================================================================
    # def test_property_steps(self):
    #     # 스텝 전체 데이터
    #     self.assertIsInstance(self.scenario.steps, list)
    #     self.assertEqual(5, len(self.scenario.steps))
    #
    # # ==========================================================================
    # def test_property_step(self):
    #     self.scenario.step

    # ==========================================================================
    # def test_scenario_2_iteration(self):
    #     """
    #     Scenario 객체의 Iteration 기능 검사
    #     * Loop 문 포함
    #     :return:
    #     """
    #     p = pathlib.Path(SCENARIO_1)
    #     self.scenario.update(self.scenario.load_scenario_file(p))
    #     expected_order = (
    #         # Step 1
    #         SetVariable, ExecuteProcess, ImageMatch,
    #         # Step 2
    #         SetVariable, SetVariable, TypeKeys, TypeText, TypeText,
    #         TypeKeys, ImageMatch,
    #         # Step 3
    #         SearchImage, TypeKeys, SetVariable, TypeKeys, TypeText,
    #         TypeKeys, TypeKeys, ImageMatch,
    #         # Step 4
    #         Repeat, TypeKeys, TypeText, TypeKeys, TypeKeys,
    #         TypeText, TypeKeys, TypeKeys, TypeText, TypeKeys,
    #         TypeKeys, TypeText, TypeKeys, TypeKeys, ImageMatch,
    #         Delay, TypeKeys,)
    #
    #     # 시나리오의 Repeat 과 Jump 를 적용하여 사용된 모든 아이템을 구함
    #     output_items = list()
    #     for item in self.scenario:
    #         output_items.append(item.__class__)
    #     self.assertEqual(len(expected_order), len(output_items))
    #
    #     # 기대한 아이템 타입과 맞는지 비교
    #     for o, e in zip(output_items, expected_order):
    #         self.assertEqual(o, e)

    # ==========================================================================
    def test1000_get_plugin_dumpspec(self):
        f = pathlib.Path(SCENARIO_2)
        self.scenario.update(self.scenario.load_scenario_file(f))
        item = next(self.scenario)
        spec = get_plugin_dumpspec(item['pluginDumpspec'])
        self.assertEqual('argoslabs.api.rest', spec['name'])
        self.assertEqual('help', spec['options'][0]['title'])

    # ==========================================================================
    def test1001_action_store(self):
        value_get = ['"get"']
        value_timeout = ['--timeout', '30']

        f = pathlib.Path(SCENARIO_2)
        self.scenario.update(self.scenario.load_scenario_file(f))
        item = next(self.scenario)
        spec = get_plugin_dumpspec(item['pluginDumpspec'])
        # import pprint
        # pprint.pprint(spec['parameters'])
        self.assertEqual('store', spec['parameters'][0]['action'])
        self.assertIsInstance(store(spec['parameters'][0]), list)
        self.assertEqual(store(spec['parameters'][0])[0], value_get[0].upper())

        self.assertEqual(spec['options'][22]['name'], 'timeout')
        self.assertIsInstance(store(spec['options'][22]), list)
        self.assertListEqual(store(spec['options'][22]), value_timeout)

    # ==========================================================================
    def test1002_action_store_const(self):
        argspec = {"options": [{
                    "action": "storeconst",
                    "value": "True",
                    "default": None,
                    "const": True,
                    "type": "str",
                    'option_strings': ['--example',]}]}
        self.assertEqual(
            storeconst(argspec['options'][0]), ['--example'])

    # ==========================================================================
    def test1003_action_store_true(self):
        argspec = {"options": [{
            "action": "storetrue",
            "value": "True",
            "default": None,
            "const": None,
            "type": "bool",
            'option_strings': ['--example', ]}]}
        self.assertEqual(
            storetrue(argspec['options'][0]), ['--example'])

    # ==========================================================================
    def test1003_action_store_false(self):
        argspec = {"options": [{
            "action": "storefalse",
            "value": "False",
            "default": None,
            "const": None,
            "type": "bool",
            'option_strings': ['--example', ]}]}
        self.assertEqual(
            storefalse(argspec['options'][0]), ['--example'])

    # ==========================================================================
    def test1003_action_append(self):
        argspec = {"options": [{
            "action": "append",
            "value": "A|*|*|B|*|*|C",
            "default": None,
            "const": None,
            "type": "bool",
            'option_strings': ['--example', ]}]}
        self.assertEqual(
            append(argspec['options'][0]),
            ['--example', 'A', '--example', 'B', '--example', 'C', ])

    # ==========================================================================
    def test1003_action_count(self):
        argspec = {"options": [{
            "action": "count",
            "value": "3",
            "default": None,
            "const": None,
            "type": "str",
            'option_strings': ['--example', '-e']}]}
        self.assertEqual(
            count(argspec['options'][0]),
            ['-eee'])

    # ==========================================================================
    def test1005_cast_type(self):
        value = "http://dummy.restapiexample.com"
        print(cast_type('str', value))

    # ==========================================================================
    def test110_plugin_parser(self):
        p = pathlib.Path(SCENARIO_2)
        self.scenario.update(self.scenario.load_scenario_file(p))
        item = next(self.scenario)
        print(plugin_spec_parser(item['pluginDumpspec']))

    # ==========================================================================
    def test1010_plugin_cmd(self):
        p = pathlib.Path(SCENARIO_2)
        self.scenario.update(self.scenario.load_scenario_file(p))
        item = next(self.scenario)
        cmd = plugin_spec_parser(item['pluginDumpspec'])
        print(cmd)

    # ==========================================================================
    def test1020_forward(self):
        p = pathlib.Path(SCENARIO_1)
        self.scenario.update(self.scenario.load_scenario_file(p))
        item = next(self.scenario)
        print(self.scenario.current_item_index)
        self.scenario.forward(1)
        print(self.scenario.current_item_index)
        self.scenario.backward(2)
        print(self.scenario.current_item_index)
        self.scenario.step = 1
        self.scenario.set_current_item_by_index(3)
        print(self.scenario.current_step_index)
        print(self.scenario.current_item_index)
        self.scenario.backward(4)
        print(self.scenario.current_step_index)
        print(self.scenario.current_item_index)

    def test2000_set_current_item_by_index(self):
        """
        인덱스 번호를 이용하여 다음 실행될 아이템 지정
        :return:
        """
        p = pathlib.Path(SCENARIO_1)
        self.scenario.update(self.scenario.load_scenario_file(p))

        self.scenario.set_current_item_by_index(2)
        item = next(self.scenario)
        self.assertTupleEqual(('ImageMatch', 2),
                              (item.__class__.__name__, item['index']))

        self.scenario.set_current_item_by_index(1)
        item = next(self.scenario)
        self.assertTupleEqual(('ExecuteProcess', 1),
                              (item.__class__.__name__, item['index']))

        # 스텝을 바꿔서 테스
        self.scenario.set_step_by_index(5)
        self.scenario.set_current_item_by_index(5)
        item = next(self.scenario)
        self.assertTupleEqual(('ImageMatch', 5),
                              (item.__class__.__name__, item['index']))




