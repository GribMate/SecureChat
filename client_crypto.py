#PyCryptodome functions
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

AES_MODE = AES.MODE_GCM # The AES mode that the client will use to encrypt and decrypt messages
RSA_KEY_FORMAT = "PEM" # The formatting of saved keys (PEM, DEC or OpenSSH)
RSA_KEY_BITS = 2048 # Bit length of the RSA keys used (default is 2048, 1024 and 3072 is standardized as well)

# Encrypts a text message with a given 16 byte long key and returns the data needed to decrypt later
def encryptMessage(key, data):
    cipher = AES.new(key, AES_MODE)
    ciphertext, mactag = cipher.encrypt_and_digest(data)
    return ciphertext, mactag, cipher.nonce

# Decrypts a text message with a given 16 byte long key
def decryptMessage(key, nonce, mactag, data):
    cipher = AES.new(key, AES_MODE, nonce)
    return cipher.decrypt_and_verify(data, mactag)

# Creates a private RSA key
def createPrivateKey():
    return RSA.generate(RSA_KEY_BITS)

# Writes an RSA key to a file, encrypted by a password
def saveKeyToFile(key, path, password):
    file = open(path, "wb")
    file.write(key.export_key(RSA_KEY_FORMAT, password))
    file.close()

# Reads an RSA key from a file, decrypts it with the given password
def readKeyFromFile(path, password):
    file = open(path, "r")
    key = RSA.import_key(file.read(), password)
    file.close()
    return key

# Generates a public key komponent from a private RSA key
def getPublicKeyFromPrivateKey(privateKey):
    return privateKey.publickey()



# TODO: törölni, tesztkód
key = createPrivateKey()
saveKeyToFile(key, "mykey.pem", "EgyJelszoLol")
keyRead = readKeyFromFile("mykey.pem", "EgyJelszoLol")
public = getPublicKeyFromPrivateKey(keyRead)
saveKeyToFile(public, "mykeyPublic.pem", "MasikJelszo")

secretMessage, mactag, nonce = encryptMessage(key, "My secret message.".encode("UTF-8"))
decryptedMessage = decryptMessage(key, nonce, mactag, secretMessage)