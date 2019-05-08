from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

AES_MODE = AES.MODE_GCM # The AES mode that the client will use to encrypt and decrypt messages

# Encrypts a text message with a given 16 byte long key and returns the data needed to decrypt later
def encryptMessage(key, data):
    cipher = AES.new(key, AES_MODE)
    ciphertext, mactag = cipher.encrypt_and_digest(data)
    return ciphertext, mactag, cipher.nonce

# Decrypts a text message with a given 16 byte long key
def decryptMessage(key, nonce, mactag, data):
    cipher = AES.new(key, AES_MODE, nonce)
    return cipher.decrypt_and_verify(data, mactag)


# TODO: törölni, tesztkód
key = get_random_bytes(16)
#secretMessage, mactag, nonce = encryptMessage(key, "My secret message.".encode("UTF-8"))
#decryptedMessage = decryptMessage(key, nonce, mactag, secretMessage)