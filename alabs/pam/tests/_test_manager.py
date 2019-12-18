import unittest
import pathlib

from alabs.pam.manager import PamManager

SCENARIO_1 = pathlib.Path('./scenarios/MacOS/'
                          'LA-Scenario0010/LA-Scenario0010.json')
# mgr = PamManager()
class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self):
        # logger = vvlogger.get_logger("test_log.log")
        # p = pathlib.Path(SCENARIO_2)
        # self.scenario = Scenario(str(p), logger)
        pass
    # ==========================================================================
    def tearDown(self):
        pass

    def test100_create_runner(self):
        mgr = PamManager()
        result = mgr.create()
        self.assertTrue(result)
        self.assertEqual(1, len(mgr))

    def test110_set_bot_to_runner(self):
        mgr = PamManager()
        runner = mgr.create()
        result = mgr.set_bot_to_runner(runner, SCENARIO_1)
        self.assertTrue(True, result)

    def test110_create(self):
        mgr = PamManager()
        self.assertEqual(0, len(mgr))
        mgr.create(str(SCENARIO_1))
        self.assertEqual(1, len(mgr))

    def test120_run_stop(self):
        mgr = PamManager()
        mgr.create(str(SCENARIO_1))
        self.assertTrue(mgr.start_runner(0))
        # self.assertTrue(mgr.stop_runner(0))








