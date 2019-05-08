from aiohttp import web
import socketio



# Creates a new Async Socket IO Server
sio = socketio.AsyncServer()

# Creates a new Aiohttp Web Application
app = web.Application()

# Binds our Socket.IO server to our Web App instance
sio.attach(app)

#Aiohttp endpoint definition
async def index(request):
    with open('index.html') as f:
        return web.Response(text = f.read(), content_type = 'text/html')

#Init users array
if open("users.txt").read() == "":
    users =  {}
else:
     users = eval(open("myfile.txt").read())

#User registration
@sio.on('register')
async def register_user(sid, message):
    print(message)
    users[message['un']] = message['pw']
    with open('users.txt', 'w') as f:
        print(users, file=f)

#User login
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