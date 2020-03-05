import base64
import hashlib
# sys.modules['Crypto'] = crypto
from Crypto.Cipher import AES


################################################################################
class EncryptAES:
    def __init__(self, key, iv):
        self._key = key
        self._iv = iv
        self.length = AES.block_size
        self.aes = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.unpad = lambda date: date[0:-ord(date[-1])]

    # ==========================================================================
    @property
    def key(self):
        key = hashlib.sha256(self._key.encode()).hexdigest()
        key = bytes.fromhex(key)
        return key

    # ==========================================================================
    @property
    def iv(self):
        return base64.b64decode(self._iv)

    # ==========================================================================
    def _pad(self, text):
        count = len(text.encode("utf-8"))
        add = self.length - (count % self.length)
        enc_text = text + (chr(add) * add)
        return enc_text

    # ==========================================================================
    def encrypt(self, enc_text):
        res = self.aes.encrypt(self._pad(enc_text).encode("utf8"))
        msg = str(base64.b64encode(res), encoding="utf8")
        return msg

    # ==========================================================================
    def decrypt(self, dec_text):
        res = base64.decodebytes(dec_text.encode("utf8"))
        msg = self.aes.decrypt(res).decode("utf8")
        return self.unpad(msg)


ENCYPT_MAKR = "ENC::"


################################################################################
def argos_decrypt(enc_text, key, iv):
    enc_text = enc_text[len(ENCYPT_MAKR):]
    aes = EncryptAES(key, iv)
    return aes.decrypt(enc_text)


################################################################################
def argos_encrypt(plain_text, key, iv):
    aes = EncryptAES(key, iv)
    res = aes.encrypt(plain_text)
    return ENCYPT_MAKR + res
