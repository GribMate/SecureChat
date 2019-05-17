from aiohttp import web
import socketio, base64


# -------------------------------------------------- GLOBALS --------------------------------------------------

USERS_FILE_PATH = "users.txt" # The file in which public user data is persisted
GROUPS_FILE_PATH = "groups.txt" # The file in which group data is persisted

# Creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()

# Public user data
users = {}

# Public group data
groups = {}

# Active, currently logged in clients (is not persisted) - key: username, data: SID
clients = {}


# -------------------------------------------------- CALLBACKS --------------------------------------------------

# User registration
@sio.on("server_register")
async def register_user(sid, message):
    global users
    users[message["userName"]] = {"password": message["password"], "publicKey": message["publicKey"] }
    with open(USERS_FILE_PATH, "w") as f:
        print(users, file = f)

# User login
@sio.on("server_login")
async def login_user(sid, message):
    global clients
    if message["userName"] in users:
        if message["password"] == users[message["userName"]]["password"]:
            if message["userName"] not in clients:
                clients[message["userName"]] = sid
                return "AUTH_SUCCESSFUL"
    return "ERROR"

# TODO
@sio.on("server_getGroups")
def getGroups(sid):
    return groups # TODO just the names

# TODO
@sio.on("server_createGroup")
def createGroup(sid, message):
    global groups
    if message["groupName"] in groups.values():
        return "ALREADY_EXISTS"
    else:
        groups[message["groupName"]] = {"owner": message["owner"], "members": []} # TODO: proper data storage
        with open(GROUPS_FILE_PATH, "w") as f:
            print(groups, file = f)
        return "OK"

# TODO
@sio.on("server_joinGroup")
def userJoinGroup(sid, message):
    global groups
    if message["groupName"] not in groups:
        return "GROUP_NOT_EXIST"
    elif message["userName"] in groups[message["groupName"]]["members"]:
        return "ALREADY_MEMBER"
    else:
        groups[message["groupName"]]["members"].append(message["userName"])
        with open(GROUPS_FILE_PATH, "w") as f:
            print(groups, file = f)
        return "OK"

# TODO
@sio.on("server_leaveGroup")
def userLeaveGroup(sid, message):
    global groups
    groups[message["groupName"]]["members"].remove(message["userName"])
    with open(GROUPS_FILE_PATH, "w") as f:
        print(groups, file = f)
    return "OK"

# TODO
@sio.on("server_deleteGroup")
def deleteGroup(sid, message):
    global groups
    if message["userName"] != groups[message["groupName"]]["owner"]:
        return "NOT_OWNER"
    else:
        if message["groupName"] not in groups:
            return "NOT_EXIST"
        else:
            del groups[message["groupName"]]
            with open(GROUPS_FILE_PATH, "w") as f:
                print(groups, file = f)
            return "OK"

# TODO
@sio.on("server_logout")
def logout(sid, message):
    global groups
    if len(message["groupName"]) > 2:
        if message["userName"] in groups[message["groupName"]]["members"]:
            groups[message["groupName"]]["members"].remove(message["userName"])
            with open(GROUPS_FILE_PATH, "w") as f:
                print(groups, file = f)
    del clients[message["userName"]]

# TODO
@sio.on("server_getGroupMembers")
def getGroupMembers(sid, message):
    membersData = []
    for userName in groups[message["groupName"]]["members"]:
        data = {"userName": userName, "publicKey": users[userName]["publicKey"]}
        membersData.append(data)
    return membersData

# TODO
@sio.on("server_passHandshake")
async def passHandshake(sid, message):
    targetName = message["targetUserName"]
    senderName = message["senderUserName"]
    encryptedSessionKey = base64.b64decode(message["encryptedSessionKey"])
    if targetName in clients:
        if senderName in users:
            targetSID = clients[targetName]
            publicKey = users[senderName]["publicKey"]
            await sio.emit("client_receiveHandshake", {"senderUserName": senderName, "encryptedSessionKey": base64.b64encode(encryptedSessionKey),
            "publicKey": publicKey}, room = targetSID)

# TODO
@sio.on("server_passMessage")
async def passMessage(sid, message):
    targetName = message["targetUserName"]
    senderName = message["senderUserName"]
    encryptedMessage = base64.b64decode(message["encryptedMessage"])
    macTag = base64.b64decode(message["macTag"])
    nonce = base64.b64decode(message["nonce"])
    if targetName in clients:
        if senderName in users:
            targetSID = clients[targetName]
            await sio.emit("client_receiveMessage", {"senderUserName": senderName, "encryptedMessage": base64.b64encode(encryptedMessage),
            "macTag": base64.b64encode(macTag), "nonce": base64.b64encode(nonce)}, room = targetSID)


# -------------------------------------------------- SERVER INIT --------------------------------------------------

print("\n\nSecureChat server initializing:")

# Loading user persistence
print("Loading user data...")
try:
    with open(USERS_FILE_PATH, "r") as file:
        users = eval(file.read())
        print("User data found and loaded.")
except FileNotFoundError:
    open(USERS_FILE_PATH, "w+").close() # Just create a new file and immediately close the stream
    print("User data was not found, new file created.")
except SyntaxError: # Happens if eval() gets empty string -> an empty file exists
    print("Empty user data file found.")

# Loading group persistence
print("Loading groups data...")
try:
    with open(GROUPS_FILE_PATH, "r") as file:
        groups = eval(file.read())
        print("Group data found and loaded.")
except FileNotFoundError:
    open(GROUPS_FILE_PATH, "w+").close() # Just create a new file and immediately close the stream
    print("Group data was not found, new file created.")
except SyntaxError: # Happens if eval() gets empty string -> an empty file exists
    print("Empty group data file found.")

print("Configuring Aiohttp and Socketio...")

# Aiohttp endpoint definition
async def index(request):
    with open("index.html") as f:
        return web.Response(text = f.read(), content_type = "text/html")

# Binds our Socket.IO server to our Web App instance
sio.attach(app)

app.router.add_get("/", index)

# We run the server
print("\nDone! Starting server...\n")
if __name__ == "__main__":
    web.run_app(app)