import unittest
from alabs.pam.common.crypt import EncryptAES

PLAIN_TEXT = 'vivans123$'
ENCRYPT_TEXT = 'fINEjX2G1wBd2z0EW4mXuQ=='
KEY = '4c4301a800ad4d77ac96f3b06df3140b'
IV = '2RmmGyA4M63oKxmOV3pzoA=='


################################################################################
class UnitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.aes = EncryptAES(KEY, IV)

    def test_100_encrypt(self):
        res = self.aes.encrypt(PLAIN_TEXT)
        self.assertEqual(ENCRYPT_TEXT, res)

    def test_120_descrypt(self):
        res = self.aes.decrypt(ENCRYPT_TEXT)
        self.assertEqual(PLAIN_TEXT, res)


if __name__ == '__main__':
    unittest.main()