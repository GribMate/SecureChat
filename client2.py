import socketio
from aiohttp import web
import time

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Client connected')

@sio.on('message')
def on_message(data):
    print('I received a message!')

@sio.on('disconnect')
def on_disconnect():
    print('I\'m disconnected!')

@sio.on('login_auth')
def auth(message):
    if message['response'] == 'Yes':
        return user_session(message['un'])
    else:
        print(message['response']+ '\n')
        login()

def register():
    while True:
        username = input('Your username: ')
        if len(username) < 3:
            print('Username must be longer than 2 characters')
            continue
        else:
            break
    while True:
        password = input('New password: ')
        if len(password) < 6:
            print('Password must be longer than 5 characters')
            continue
        else:
            break
    
    print('Creating account...')
    sio.emit('register', {'un' : username, 'pw' : password})
    time.sleep(1)
    print('Account has been created\n')
    print('Options: register | login | exit')

def login():
    while True:
        username = input('Username: ')
        if len(username) < 1:
            print("Username can't be blank")
        else: 
            break
    while True:
        password = input('Password: ')
        if len(password) < 1:
            print("Username can't be blank")
        else:
            break

    sio.emit('login', {'un' : username, 'pw' : password})

def user_session(username):
    print('Welcome ' + username)
    print('Options: logout | create_group | join_group | delete_group')
    while True:
        option = input(username + ' > ')
        if option == 'logout':
            break
    
sio.connect('http://localhost:8080')

print('Options: register | login | exit')

while True:
    option = input('> ')
    if option == 'login':
        login()
    elif option == 'register':
        register()
    elif option == 'exit':
        break
    else:
        print(option + ' is not a valid option')