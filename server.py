from aiohttp import web
import socketio


# -------------------------------------------------- GLOBAL VARIABLES --------------------------------------------------

# Creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()

#Init users array
if open("users.txt", "w+").read() == "":
    users =  {}
else:
    users = eval(open("users.txt").read())


# -------------------------------------------------- CALLBACKS --------------------------------------------------

#User registration
@sio.on("server_register")
async def register_user(sid, message):
    print(message)
    users[message["un"]] = message["pw"]
    with open("users.txt", "w") as f:
        print(users, file=f)

#User login
@sio.on("server_login")
async def login_user(sid, message):
    if message["un"] in users:
        if message["pw"] == users[message["un"]]:
            await sio.emit("client_login_auth", {"response": "Yes", "un": message["un"]})
        else:
            await sio.emit("client_login_auth", {"response": "Password is incorrect", "un": ""}) 
    else:
        await sio.emit("client_login_auth", {"response": "First you should register...", "un": ""})


# -------------------------------------------------- SERVER INIT --------------------------------------------------

#Aiohttp endpoint definition
async def index(request):
    with open("index.html") as f:
        return web.Response(text = f.read(), content_type = "text/html")

# Binds our Socket.IO server to our Web App instance
sio.attach(app)

app.router.add_get("/", index)

# We run the server
if __name__ == "__main__":
    web.run_app(app)