import base64
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Cipher import AES

class Encryption:
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, msg):
        # create the combination of key and iv for encryption
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        # encode plaintext in base 64
        msg64 = base64.b64encode(msg)
        # encrypt the msg with padding pkcs7 as arduino
        ciphertext = cipher.encrypt(pad(msg64, AES.block_size, style='pkcs7'))
        # encode the chipertext in base 64
        return base64.b64encode(ciphertext)

    def decrypt(self, msg):
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        try:
            # decode from base64
            msg64 = base64.b64decode(msg)
            # Decrypt msg with unpadding
            pt = unpad(cipher.decrypt(msg64), AES.block_size, style='pkcs7')
            return base64.b64decode(pt)
        except ValueError as err:
            print(f"Decrypt error: {err}")
            return b""