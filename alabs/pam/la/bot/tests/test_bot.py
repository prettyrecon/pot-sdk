import unittest
import pathlib
from alabs.pam.la.bot.scenario import Scenario
from alabs.pam.la.bot.operations import Items, SetVariable, ExecuteProcess, \
    ImageMatch, TypeText, TypeKeys, SearchImage, Repeat, Delay
from alabs.common.util import vvlogger

SCENARIO_1 = pathlib.Path('./scenarios/LA-Scenario0010/LA-Scenario0010.json')
SCENARIO_2 = pathlib.Path('./scenarios/LA-Scenario0020/LA-Scenario0020.json')
NOT_SCN = pathlib.Path('./scenarios/LA-Scenario0010/TestRunScenario_0010.py')

class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self):
        logger = vvlogger.get_logger("test_log.log")
        p = pathlib.Path(SCENARIO_2)
        self.scenario = Scenario(str(p), logger)

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
    def test_scenario_2_iteration(self):
        """
        Scenario 객체의 Iteration 기능 검사
        * Loop 문 포함
        :return:
        """
        expected_order = (
            # Step 1
            SetVariable, ExecuteProcess, ImageMatch,
            # Step 2
            SetVariable, SetVariable, TypeKeys, TypeText, TypeText,
            TypeKeys, ImageMatch,
            # Step 3
            SearchImage, TypeKeys, SetVariable, TypeKeys, TypeText,
            TypeKeys, TypeKeys, ImageMatch,
            # Step 4
            Repeat, TypeKeys, TypeText, TypeKeys, TypeKeys,
            TypeText, TypeKeys, TypeKeys, TypeText, TypeKeys,
            TypeKeys, TypeText, TypeKeys, TypeKeys, ImageMatch,
            Delay, TypeKeys,)

        # 시나리오의 Repeat 과 Jump 를 적용하여 사용된 모든 아이템을 구함
        output_items = list()
        for item in self.scenario:
            output_items.append(item.__class__)
        self.assertEqual(len(expected_order), len(output_items))

        # 기대한 아이템 타입과 맞는지 비교
        for o, e in zip(output_items, expected_order):
            self.assertEqual(o, e)

    # ==========================================================================
    def test_request_available_operators(self):
        # # [StringValue("LocateImage")]
        # SearchImage,
        # # [StringValue("Click and Focus")]
        # MouseClick,
        # # [StringValue("Scroll")]
        # MouseScroll,
        # # [StringValue("TextInput")]
        # TypeText, SelectWindow, HTMLAction,
        # # [StringValue("JavaScript")]
        # BrowserScript,
        # # [StringValue("Delay")]
        # Delay, ReadMessage,
        # # [StringValue("OCR")]
        # ReadImageText, Repeat,
        # # [StringValue("ShortcutKeys")]
        # TypeKeys,
        # # [StringValue("CTCDemo")]
        # RunModule,
        # SendEmail,
        # ClearCache,
        # # [StringValue("End of Scenario")]
        # EndScenario,
        # # [StringValue("End of Step")]
        # EndStep,
        # # [StringValue("SetVariables")]
        # SetVariable,
        # UserModule,
        # # [StringValue("ExcelBasics")]
        # Excel,
        # CSV,
        # # [StringValue("OpenBrowser")]
        # Navigate,
        # UserInputPopup,
        # WindowObject
        #
        # # [StringValue("OnloadEvent")]
        # Document, Frame,
        # [StringValue("WebElement")]
        # Component, ImageMatch, WaitingPopup, TextMatch,
        # [StringValue("CompareValue")]
        # CompareText
        # DeleteFile,
        # [StringValue("RunProgram")]
        # ExecuteProcess,
        # [StringValue("KillProcess")]
        # StopProcess, ClosePopup
        #
        # Beep,
        # [StringValue("Dialogue")]
        # PopupInteraction,
        # UserParams
        data = {
            "data": [
                {"name": "SearchImage"},
                {"name": "MouseClick"},
                {"name": "TypeKeys"},
            ]
        }
        return data
