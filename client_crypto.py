from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes



def encryptMessage(key, header, nonce, data):
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    cipher.update(header)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return ciphertext, tag

def decryptMessage(key, header, nonce, tag, data):
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    cipher.update(header)
    return cipher.decrypt_and_verify(data, tag)

key = get_random_bytes(16)
header = b"header"
nonce = b"0123456789"

secretMessage, tag = encryptMessage(key, header, nonce, "My secret message.".encode("UTF-8"))
decryptedMessage = decryptMessage(key, header, nonce, tag, secretMessage)

print(str(decryptedMessage, "UTF-8"))