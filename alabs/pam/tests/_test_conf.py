import os
import pathlib
import logging
from unittest import TestCase
from ..conf import Config
from ..conf import get_conf, write_conf_file


class Test(TestCase):
    def setUp(self) -> None:
        os.environ['PAM_CONF'] = str(pathlib.Path('./.argos-rpa-pam.conf'))


    def test_100_get_conf(self):
        self.assertIsInstance(get_conf(), dict)

    def test_200_get(self):
        logging.basicConfig(filename='test.log', level=logging.DEBUG)
        logger = logging.getLogger()
        conf = get_conf(logger)
        self.assertEqual('info', conf.get('/MANAGER/LOG_LEVEL'))
