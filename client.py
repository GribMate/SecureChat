from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

header = b"header"
data = b"secret"
key = get_random_bytes(16)
cipher = AES.new(key, AES.MODE_GCM)
cipher.update(header)
ciphertext, tag = cipher.encrypt_and_digest(data)