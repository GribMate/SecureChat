#PyCryptodome functions

from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


# -------------------------------------------------- SETTINGS --------------------------------------------------

AES_MODE = AES.MODE_GCM # The AES mode that the client will use to encrypt and decrypt messages
RSA_KEY_FORMAT = "PEM" # The formatting of saved keys (PEM, DEC or OpenSSH)
RSA_KEY_BITS = 2048 # Bit length of the RSA keys used (default is 2048, 1024 and 3072 is standardized as well)
SESSION_KEY_LENGTH = 16 # Sets the number of bytes for each session key generated


# -------------------------------------------------- AES FUNCTIONS --------------------------------------------------

# Gets a new, random symmetric encryption key
def generateSessionKey():
    return get_random_bytes(SESSION_KEY_LENGTH)

# Encrypts a text message with a given 16 byte long key and returns the data needed to decrypt later
def encryptMessage(sessionKey, plaintext):
    cipher = AES.new(sessionKey, AES_MODE)
    ciphertext, mactag = cipher.encrypt_and_digest(plaintext.encode("UTF-8"))
    return ciphertext, mactag, cipher.nonce

# Decrypts a text message with a given 16 byte long key
def decryptMessage(sessionKey, nonce, mactag, ciphertext):
    cipher = AES.new(sessionKey, AES_MODE, nonce)
    return str(cipher.decrypt_and_verify(ciphertext, mactag), "UTF-8")


# -------------------------------------------------- RSA GEN FUNCTIONS --------------------------------------------------

# Creates a private RSA key
def createPrivateKey():
    return RSA.generate(RSA_KEY_BITS)

# Writes an RSA key to a file, encrypted by a password
def saveKeyToFile(key, path, password):
    with open(path, "wb") as file:
        file.write(key.export_key(RSA_KEY_FORMAT, password))

# Reads an RSA key from a file, decrypts it with the given password
def readKeyFromFile(path, password):
    with open(path, "r") as file:
        key = RSA.import_key(file.read(), password)
    return key

# Generates a public key komponent from a private RSA key
def getPublicKeyFromPrivateKey(privateKey):
    return privateKey.publickey().export_key(RSA_KEY_FORMAT)


# -------------------------------------------------- RSA CODE FUNCTIONS --------------------------------------------------

# Encrypts a symmetric session key (AES) with a public RSA key
def encryptSessionKey(sessionKey, publicKey):
    cipher = PKCS1_OAEP.new(publicKey)
    return cipher.encrypt(sessionKey)

# Decrypts a symmetric session key (AES) with a private RSA key
def decryptSessionKey(sessionKey, privateKey):
    cipher = PKCS1_OAEP.new(privateKey)
    return cipher.decrypt(sessionKey)