from aiohttp import web
import socketio

# Creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()

sio.attach(app)

async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

users = {}

@sio.on('message')
async def print_message(sid, message):
    # When we receive a new event of type
    # 'message' through a socket.io connection
    # we print the socket ID and the message
    print("Socket ID: " , sid)
    print(message)

@sio.on('register')
async def register_user(sid, message):
    print(message)
    users[message['un']] = message['pw']

@sio.on('login')
async def login_user(sid, message):
    if message['un'] in users:
        if message['pw'] == users[message['un']]:
            await sio.emit('login_auth', {'response': 'Yes', 'un': message['un']})
        else:
            await sio.emit('login_auth', {'response': 'First you should register...', 'un': ''})
    else:
        await sio.emit('login_auth', {'response': 'Password is incorrect', 'un': ''}) 

app.router.add_get('/', index)

# We run the server
if __name__ == '__main__':
    web.run_app(app)