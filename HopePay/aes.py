import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


BLOCK_SIZE = 16
def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + chr(length)*length

def unpad(data):
    return data[:-data[-1]]

def encrypt(message, passphrase):
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CBC, IV)
    return base64.b64encode(IV + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CBC, IV)
    return unpad(aes.decrypt(encrypted[BLOCK_SIZE:]))
