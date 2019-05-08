import socketio
from aiohttp import web
import time

# Socket.io client definition
sio = socketio.Client()

# Connection function
@sio.on('connect')
def on_connect():
    print('Client connected')

# Message function
@sio.on('message')
def on_message(data):
    print('I received a message!')

# Disconnection function
@sio.on('disconnect')
def on_disconnect():
    print('I\'m disconnected!')

# Login authentication
# If response == Yes we login with the given user
@sio.on('login_auth')
def auth(message):
    if message['response'] == 'Yes':
        return user_session(message['un'])
    else:
        print(message['response']+ '\n')
        login()

# Registration function
# If the user filled all the requested fields correctly, 
# we send the data in a dictionary to the server
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

# Login function
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

# User session for chat 
# If the login was successful we call this function
def user_session(username):
    print('Welcome ' + username)
    print('Options: logout | create_group | join_group | delete_group')
    while True:
        option = input(username + ' > ')
        if option == 'logout':
            print("Logging out...")
            break

# Socket connection with the server
sio.connect('http://localhost:8080')

# Default messages after the application started
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