import base64
import json
from datetime import datetime

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def default_serializer(o):
    if isinstance(o, datetime):
        return o.isoformat()  # or o.strftime("%Y-%m-%d %H:%M:%S") for custom format
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


class AESCipher:
    def __init__(self, key=None, iv=None):
        self.key = key if key is not None else self.__generate_key()
        self.iv = iv if iv is not None else self.__generate_iv()

    def __generate_key(self):
        return b"qwsmdyfhtjchflsy"
        # return get_random_bytes(16)

    def __generate_iv(self):
        return b"1236547895412365"
        # return get_random_bytes(16)

    def encrypt(self, data):
        json_string = json.dumps(data, default=default_serializer)
        data_bytes = json_string.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted = cipher.encrypt(pad(data_bytes, AES.block_size))
        return base64.b64encode(self.iv + encrypted).decode("utf-8")

    def decrypt(self, data):
        encrypted_data = base64.b64decode(data)
        iv = encrypted_data[: AES.block_size]
        encrypted_message = encrypted_data[AES.block_size :]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted_message), AES.block_size)
        json_string = decrypted.decode("utf-8")
        return json.loads(json_string)


aes = AESCipher()
