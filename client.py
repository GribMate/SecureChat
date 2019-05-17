import os, socketio, time, base64
from aiohttp import web
import clientCrypto


# -------------------------------------------------- GLOBALS --------------------------------------------------

# Socket.io client definition
sio = socketio.Client()

# Shows if the "event loop" is currently working on something
processingCommand = False

# Shows if the user is authenticated successfully by the server and is logged in currently
userLoggedIn = False

# The username which identifies a user on the server
account_userName = ""

# The password associated with a registered user (set from local client only)
account_password = ""

# The private RSA key, read from file locally
account_privateKey = ""

# The group of which the user is currently a member of
account_currentGroup = ""

# Crypto session with other users
sessions = dict()


# -------------------------------------------------- DEFAULT CALLBACKS --------------------------------------------------

# Connection function
@sio.on("connect")
def on_connect():
    print("Connection successful. Welcome to SecureChat!\n")

# Message function
@sio.on("message")
def on_message(data):
    return
    # Not used default direct data callback

# Disconnection function
@sio.on("disconnect")
def on_disconnect():
    user_logout()
    print("Client disconnected!\n")


# -------------------------------------------------- ADMINISTRATIVE FUNCTIONS --------------------------------------------------

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
    clientCrypto.saveKeyToFile(privateKey, username + ".pem", password) # Saving encrpyted private key locally
    publicKey = clientCrypto.getPublicKeyFromPrivateKey(privateKey) # Public key component to send to the server

    sio.emit("server_register", {"userName": username, "password": password, "publicKey": publicKey})
    print("Account has been created.\n")
    processingCommand = False

# Login function
def client_login():
    global account_password
    global account_userName
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
    account_password = password
    account_userName = username
    sio.emit("server_login", {"userName": username, "password": password}, callback = cb_user_login)

# Login authentication
def cb_user_login(response):
    global processingCommand
    global userLoggedIn
    global account_userName
    global account_password
    global account_privateKey
    if response == "AUTH_SUCCESSFUL":
        # If response is successful, we login with the given user
        print("Login successful!")
        userLoggedIn = True
        account_privateKey = clientCrypto.readKeyFromFile(account_userName + ".pem", account_password)
        processingCommand = False
        return userSessionLoop()
    elif response == "ERROR":
        print("Login error!")
        account_password = ""
        account_userName = ""
    processingCommand = False

# Logs the user out both in the client and the server
def user_logout():
    global processingCommand
    global userLoggedIn
    global account_currentGroup
    global account_userName
    global account_password
    global account_privateKey
    global sessions
    print("Logging out...\n")
    sio.emit("server_logout", {"groupName": account_currentGroup, "userName": account_userName})
    userLoggedIn = False
    account_currentGroup = ""
    account_userName = ""
    account_password = ""
    account_privateKey = ""
    sessions = dict()
    print("Logged out. Bye!")
    processingCommand = False


# -------------------------------------------------- GROUP FUNCTIONS --------------------------------------------------

# Gets a group name list from the server
def user_listGroups():
    sio.emit("server_getGroups", callback = cb_user_listGroups)

# Displays the group name list
def cb_user_listGroups(response):
    global processingCommand
    print("Currently available groups:")
    for groupName in response:
        print(groupName)
    processingCommand = False

# Creates a new group on the server
def user_createGroup():
    while True:
        groupname = input("Group name: ")
        if len(groupname) <= 2:
            print("Group name must be longer than 2 characters!")
        else:
            sio.emit("server_createGroup", {"groupName": groupname, "owner": account_userName}, callback = cb_user_createGroup)
            break

# Displays group creation response
def cb_user_createGroup(response):
    global processingCommand
    if (response == "ALREADY_EXISTS"):
        print("Group name is already in use.")
    elif (response == "OK"):
        print("Group created.")
    else:
        print("Unknown error happened during group creation.")
    processingCommand = False

# Attempts to join to a group
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
            sio.emit("server_joinGroup", {"groupName": groupname, "userName": account_userName}, callback = cb_user_joinGroup)
            break

# Displays joining response and empties local variable if needed
def cb_user_joinGroup(response):
    global processingCommand
    global account_currentGroup
    if (response == "GROUP_NOT_EXIST"):
        account_currentGroup = "" # We clear the variable, since joining failed
        print("The group does not exist.")
    elif (response == "ALREADY_MEMBER"):
        # We leave the variable as is, since user is a member of given group
        print("You are already a member of this group.")
    elif (response == "OK"):
        # We leave the variable as is, since the join was successful
        print("You joined the group!")
    else:
        account_currentGroup = "" # We clear the variable, since joining failed
        print("Unknown error happened during joining the group.")
    processingCommand = False

# Attempts to leave a group
def user_leaveGroup():
    global account_currentGroup
    if len(account_currentGroup) < 3:
        print("You are not member of any group!")
    else:
        sio.emit("server_leaveGroup", {"groupName": account_currentGroup, "userName": account_userName}, callback = cb_user_leaveGroup)
    
# Displays group leave response
def cb_user_leaveGroup(response):
    global processingCommand
    global account_currentGroup
    if (response == "OK"):
        account_currentGroup = ""
        print("You left the group!")
    else:
        print("Unknown error happened during leaving the group.")
    processingCommand = False

# Attempts to delete a group (only possible if owned by the current user)
def user_deleteGroup():
    while True:
        groupname = input("Group name: ")
        if len(groupname) < 1:
            print("Group name can't be blank!")
        else:
            sio.emit("server_deleteGroup", {"groupName": groupname, "userName": account_userName}, callback = cb_user_deleteGroup)
            break

# Displayes group delete response
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


# -------------------------------------------------- MESSAGE FUNCTIONS --------------------------------------------------

# Sends a message to everyone in the group
def user_sendMessage():
    global account_currentGroup
    if len(account_currentGroup) < 3:
        print("You cannot send a message until you join a group.")
    else:
        # First of all, we request a list of targeted users from the server (username and public key)
        sio.emit("server_getGroupMembers", {"groupName": account_currentGroup}, callback = cb_sendMessage)

# Handles the list, builds encrypted connections (if needed) then sends the message
def cb_sendMessage(targetUsers):
    global processingCommand
    while True:
        message = input("Your message: ")
        if len(message) < 1:
            print("Message cannot be blank!")
        else:
            for targetUser in targetUsers:
                if targetUser["userName"] != account_userName:
                    checkOrBuildSession(targetUser["userName"], targetUser["publicKey"]) # Building session (if needed)
                    sendMessageToTarget(targetUser["userName"], message) # Sending message
            break
    processingCommand = False

# Builds or refreshes a connection between two clients
def checkOrBuildSession(userName, publicKey):
    global sessions
    if userName not in sessions: # No session built before
        sessions[userName] = {"sessionKey": clientCrypto.generateSessionKey(), "publicKey": publicKey, "handshakeDone": "False"} # New session, needs handshake first
        sendHandshake(userName)
    elif sessions[userName]["handshakeDone"] == "False": # There was a session, but handshake is needed (likely because session timed out)
        sendHandshake(userName)

# Establishes crypto handshake with a client
def sendHandshake(userName):
    global sessions
    global account_userName
    sessionKey = sessions[userName]["sessionKey"]
    publicKey =  clientCrypto.getKeyFromEncodedData(sessions[userName]["publicKey"]) # Gets the public RSA key from the other client
    encryptedSessionKey = clientCrypto.encryptSessionKey(sessionKey, publicKey) # Encrypts new symmetric session key with RSA public key
    # Base64 encoding / decoding seems to be needed, since sio.emit() otherwise disconnects the client,
    # however sending bytes should be supported according to the API documentation
    sio.emit("server_passHandshake", {"senderUserName": account_userName, "targetUserName": userName,
    "encryptedSessionKey": base64.b64encode(encryptedSessionKey)})
    sessions[userName]["handshakeDone"] = "True"

# Sends a private, encrypted message to a client (with previous session established)
def sendMessageToTarget(userName, message):
    global sessions
    sessionKey = sessions[userName]["sessionKey"]
    encryptedMessage, macTag, nonce = clientCrypto.encryptMessage(sessionKey, message) # Encrypting message with session key
    # Base64 encoding / decoding seems to be needed, since sio.emit() otherwise disconnects the client,
    # however sending bytes should be supported according to the API documentation
    sio.emit("server_passMessage", {"senderUserName": account_userName, "targetUserName": userName,
    "encryptedMessage": base64.b64encode(encryptedMessage), "macTag": base64.b64encode(macTag), "nonce": base64.b64encode(nonce)})

# Receives handshake, initialized by another client
@sio.on("client_receiveHandshake")
def receiveHandshake(message):
    # Base64 encoding / decoding seems to be needed, since sio.emit() otherwise disconnects the client,
    # however sending bytes should be supported according to the API documentation
    global account_privateKey
    global sessions
    userName = message["senderUserName"]
    encryptedSessionKey = base64.b64decode(message["encryptedSessionKey"])
    publicKey = message["publicKey"]
    sessionKey = clientCrypto.decryptSessionKey(encryptedSessionKey, account_privateKey) # Decrypting session key with private RSA key
    if userName in sessions:
        del sessions[userName] # We renew the session anyway on an incoming handshake request
    sessions[userName] = {"sessionKey": sessionKey, "publicKey": publicKey, "handshakeDone": "True"}

# Receives a private encrypted message from another client
@sio.on("client_receiveMessage")
def receiveMessage(message):
    # Base64 encoding / decoding seems to be needed, since sio.emit() otherwise disconnects the client,
    # however sending bytes should be supported according to the API documentation
    global sessions
    userName = message["senderUserName"]
    encryptedMessage = base64.b64decode(message["encryptedMessage"])
    macTag = base64.b64decode(message["macTag"])
    nonce = base64.b64decode(message["nonce"])
    if userName in sessions:
        if sessions[userName]["handshakeDone"] == "True":
            sessionKey = sessions[userName]["sessionKey"]
            message = clientCrypto.decryptMessage(sessionKey, nonce, macTag, encryptedMessage) # Decrypting with session key
            print(userName + ": " + message + "\n")


# -------------------------------------------------- COMMAND LOOP FUNCTIONS --------------------------------------------------

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
    print("Available commands: msg | list | create | join | leave | delete | logout")
    while True:
        while processingCommand: # If we are already processing an async command, we shouldn't spam the output, so we wait
            time.sleep(0.1)
        # We aren't in a command processing (anymore)
        option = input(account_userName + " (" + account_currentGroup + ") > ")
        if option == "msg":
            processingCommand = True
            user_sendMessage()
        elif option == "list":
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
            processingCommand = True
            user_logout()
            break
        else:
            print("\"" + option + "\" is not a valid option!")


# -------------------------------------------------- MAIN --------------------------------------------------

print("\n\nSecureChat client initializing:")

# Socket connection with the server
sio.connect("http://localhost:8080")

defaultLoop()