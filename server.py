from aiohttp import web
import socketio


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


# -------------------------------------------------- CALLBACKS --------------------------------------------------

# User registration
@sio.on("server_register")
async def register_user(sid, message):
    print(message)
    users[message["userName"]] = {"password": message["password"], "publicKey": message["publicKey"] }
    with open(USERS_FILE_PATH, "w") as f:
        print(users, file = f)

# User login
@sio.on("server_login")
async def login_user(sid, message):
    if message["userName"] in users:
        if message["password"] == users[message["userName"]]["password"]:
            await sio.emit("client_login_auth", {"response": "Yes", "userName": message["userName"]})
        else:
            await sio.emit("client_login_auth", {"response": "Password is incorrect", "userName": ""}) 
    else:
        await sio.emit("client_login_auth", {"response": "First you should register...", "userName": ""})


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