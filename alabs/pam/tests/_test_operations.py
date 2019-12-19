import unittest
import pathlib

from alabs.pam.operations import result_as_csv

SCENARIO_1 = pathlib.Path('./scenarios/MacOS/'
                          'LA-Scenario0010/LA-Scenario0010.json')


class TestUnit(unittest.TestCase):
    # ==========================================================================
    def setUp(self) -> None:
        pass

    # ==========================================================================
    def tearDown(self) -> None:
        pass

    # ==========================================================================
    def test1000_plugin_result_csv_header(self):
        group = "excel"
        data_with_header = """name,address,data
Raven,deokyu@argos-labs.com,1234
Benny,bkpark@argos-labs.com,5678
Brad,brad@argos-labs.com,hello"""

        data_without_header = """Raven,deokyu@argos-labs.com,1234
Benny,bkpark@argos-labs.com,5678
Brad,brad@argos-labs.com,hello"""

        expected_data_with_header = (
            ("{{excel.name}}", ('Raven', 'Benny', 'Brad')),
            ("{{excel.address}}", ('deokyu@argos-labs.com',
                                   'bkpark@argos-labs.com',
                                   'brad@argos-labs.com')),
            ("{{excel.data}}", ('1234', '5678', 'hello')))

        expected_data_without_header = (
            ("{{excel.A}}", ('Raven', 'Benny', 'Brad')),
            ("{{excel.B}}", ('deokyu@argos-labs.com',
                             'bkpark@argos-labs.com',
                             'brad@argos-labs.com')),
            ("{{excel.C}}", ('1234', '5678', 'hello')))

        result_1 = result_as_csv(group, data_with_header, header=True)
        result_2 = result_as_csv(group, data_without_header, header=False)

        self.assertTupleEqual(expected_data_with_header, result_1)
        self.assertTupleEqual(expected_data_without_header, result_2)



