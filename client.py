import os, socketio, time
from aiohttp import web
import clientCrypto


# -------------------------------------------------- GLOBALS --------------------------------------------------

PRIVATE_KEY_FILE_PATH = "myPrivateKey.pem" # The path that the client saves its private RSA key file

# Socket.io client definition
sio = socketio.Client()

# Shows if the "event loop" is currently working on something
processingCommand = False

# Shows if the user is authenticated successfully by the server and is logged in currently
userLoggedIn = False


# -------------------------------------------------- DEFAULT CALLBACKS --------------------------------------------------

# Connection function
@sio.on("connect")
def on_connect():
    print("Connection successful. Welcome to SecureChat!\n")

# Message function
@sio.on("message")
def on_message(data):
    print("I received a message: " + str(data, "UTF-8"))

# Disconnection function
@sio.on("disconnect")
def on_disconnect():
    print("Client disconnected!")


# -------------------------------------------------- CUSTOM CALLBACKS --------------------------------------------------

# Login authentication
@sio.on("client_login_auth")
def auth(message):
    global processingCommand
    global userLoggedIn
    if message["response"] == "Yes":
        # If response == Yes we login with the given user
        userLoggedIn = True
        processingCommand = False
        return userSessionLoop(message["userName"])
    else:
        print(message["response"]+ "\n")
        processingCommand = False


# -------------------------------------------------- CLIENT FUNCTIONS --------------------------------------------------

# Emtpies the console window
def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')


# Registration function
# If the user filled all the requested fields correctly, 
# we send the data in a dictionary to the server
def client_register():
    global processingCommand
    while True:
        username = input("Username: ")
        if len(username) <= 2:
            print("Username must be longer than 2 characters!")
            continue
        else:
            break
    while True:
        password = input("Password: ")
        if len(password) <= 5:
            print("Password must be longer than 5 characters!")
            continue
        else:
            break
    
    print("Creating account...")

    privateKey = clientCrypto.createPrivateKey() # Generating RSA key
    clientCrypto.saveKeyToFile(privateKey, PRIVATE_KEY_FILE_PATH, password) # Saving encrpyted private key locally
    publicKey = clientCrypto.getPublicKeyFromPrivateKey(privateKey) # Public key component to send to the server

    sio.emit("server_register", {"userName": username, "password": password, "publicKey": publicKey})
    time.sleep(1)
    print("Account has been created.\n")
    processingCommand = False

# Login function
def client_login():
    while True:
        username = input("Username: ")
        if len(username) < 1:
            print("Username can't be blank!")
        else: 
            break
    while True:
        password = input("Password: ")
        if len(password) < 1:
            print("Password can't be blank!")
        else:
            break

    sio.emit("server_login", {"userName": username, "password": password})

def user_createGroup():
    print("TODO")

def user_joinGroup():
    print("TODO")

def user_deleteGroup():
    print("TODO")


# Default message loop after the application started
def defaultLoop():
    global processingCommand
    global userLoggedIn
    print("Available commands: register | login | exit")
    while True:
        # If we are already processing an async command,
        # we shouldn"t spam the output, so we wait
        while processingCommand:
            time.sleep(0.1)
        # We aren"t in a command processing (anymore)
        while userLoggedIn: # When the user logs in this loop gets hibernated
            time.sleep(1)
        option = input("> ")
        if option == "login":
            processingCommand = True
            client_login()
        elif option == "register":
            processingCommand = True
            client_register()
        elif option == "exit":
            break
        else:
            print("\"" + option + "\" is not a valid option!")

# User session loop for chat
# If the login was successful we call this function
def userSessionLoop(username):
    global processingCommand
    global userLoggedIn
    clearConsole()
    print("\n\nWelcome " + username + "! :)")
    print("Available commands: create_group | join_group | delete_group | logout")
    while True:
        while processingCommand: # If we are already processing an async command, we shouldn't spam the output, so we wait
            time.sleep(0.1)
        # We aren't in a command processing (anymore)
        option = input(username + " > ")
        if option == "create_group":
            processingCommand = True
            user_createGroup()
        elif option == "join_group":
            processingCommand = True
            user_joinGroup()
        elif option == "delete_group":
            processingCommand = True
            user_deleteGroup()
        elif option == "logout":
            print("Logging out...\n")
            userLoggedIn = False
            processingCommand = False
            break
        else:
            print("\"" + option + "\" is not a valid option!")


# -------------------------------------------------- MAIN --------------------------------------------------

print("\n\nSecureChat client initializing:")

# Socket connection with the server
sio.connect("http://localhost:8080")

defaultLoop()