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

# The username which identifies a user on the server
account_userName = "" # TODO might need another ID

# The group of which the user is currently a member of
account_currentGroup = ""


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
    global account_userName
    if message["response"] == "AUTH_SUCCESSFUL":
        # If response is successful, we login with the given user
        print("Login successful!")
        userLoggedIn = True
        account_userName = message["userName"]
        processingCommand = False
        return userSessionLoop()
    elif message["response"] == "INVALID_PWD":
        print("Password is incorrect!")
    elif message["response"] == "INVALID_USER":
        print("User doesn't exist, please register first!")
    else:
        print("Unknown login error happened (server response: " + message["response"] + ").\n")
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

# TODO
def user_listGroups():
    sio.emit("server_getGroups", callback = cb_user_listGroups)


def cb_user_listGroups(response):
    global processingCommand
    print(response)
    processingCommand = False

# TODO
def user_createGroup():
    while True:
        groupname = input("Group name: ")
        if len(groupname) <= 2:
            print("Group name must be longer than 2 characters!")
        else:
            sio.emit("server_createGroup", {"groupName": groupname, "owner": account_userName}, callback = cb_user_createGroup)
            break

def cb_user_createGroup(response):
    global processingCommand
    if (response == "ALREADY_EXISTS"):
        print("Group name is already in use.")
    elif (response == "OK"):
        print("Group created.")
    else:
        print("Unknown error happened during group creation.")
    processingCommand = False

# TODO
def user_joinGroup():
    global processingCommand
    global account_currentGroup
    if len(account_currentGroup) > 2:
        print("You cannot join another group.")
        processingCommand = False
        return

    while True:
        groupname = input("Group name: ")
        if len(groupname) < 1:
            print("Group name can't be blank!")
        else:
            account_currentGroup = groupname
            sio.emit("server_joinGroup", {"groupName": groupname, "user": account_userName}, callback = cb_user_joinGroup)
            break

def cb_user_joinGroup(response):
    global processingCommand
    global account_currentGroup
    if (response == "GROUP_NOT_EXIST"):
        account_currentGroup = "" # We clear the variable, since joining failed
        print("The group does not exist.")
    if (response == "ALREADY_MEMBER"):
        # We leave the variable as is, since user is a member of given group
        print("You are already a member of this group.")
    elif (response == "OK"):
        # We leave the variable as is, since the join was successful
        print("You joined the group!")
    else:
        account_currentGroup = "" # We clear the variable, since joining failed
        print("Unknown error happened during joining the group.")
    processingCommand = False

    # TODO
def user_leaveGroup():
    global account_currentGroup
    if len(account_currentGroup) < 1:
        print("You are not member of any group!")
    else:
        sio.emit("server_leaveGroup", {"groupName": account_currentGroup, "user": account_userName}, callback = cb_user_leaveGroup)
    

def cb_user_leaveGroup(response):
    global processingCommand
    global account_currentGroup
    if (response == "OK"):
        account_currentGroup = ""
        print("You left the group!")
    else:
        print("Unknown error happened during leaving the group.")
    processingCommand = False

# TODO
def user_deleteGroup():
    while True:
        groupname = input("Group name: ")
        if len(groupname) < 1:
            print("Group name can't be blank!")
        else:
            sio.emit("server_deleteGroup", {"groupName": groupname, "user": account_userName}, callback = cb_user_deleteGroup)
            break

def cb_user_deleteGroup(response):
    global processingCommand
    if (response == "NOT_OWNER"):
        print("You aren't the owner of this group, so you cannot delete it!")
    elif (response == "NOT_EXIST"):
        print("The group does not exist!")
    elif (response == "OK"):
        print("You deleted the group.")
    else:
        print("Unknown error happened during deleting the group.")
    processingCommand = False



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
def userSessionLoop():
    global processingCommand
    global userLoggedIn
    global account_userName
    global account_currentGroup
    clearConsole()
    print("\n\nWelcome " + account_userName + "! :)\n")
    print("Available commands: list | create | join | leave | delete | logout")
    while True:
        while processingCommand: # If we are already processing an async command, we shouldn't spam the output, so we wait
            time.sleep(0.1)
        # We aren't in a command processing (anymore)
        option = input(account_userName + " (" + account_currentGroup + ") > ")
        if option == "list":
            processingCommand = True
            user_listGroups()
        elif option == "create":
            processingCommand = True
            user_createGroup()
        elif option == "join":
            processingCommand = True
            user_joinGroup()
        elif option == "leave":
            processingCommand = True
            user_leaveGroup()
        elif option == "delete":
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