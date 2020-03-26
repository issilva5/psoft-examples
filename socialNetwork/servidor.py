#coding: utf-8
import socket
import sys
import re
import datetime
from threading import Thread

'''

HOW TO USE

This is the server of a little social network
At the moment, the following actions are allowed

1) Register - allows a new user to register to the network
   register,<user>,<password>

2) Login - allows a user to access its account
   login,<user>,<password>

3) Logout - disconnect the user
   logout

4) List users registered in the network
   see

5) Send a message to a registered user
   send,<user>,<message>

6) Read your receiveds messages
   read - to get all your messages
   read,<user> - to filter for a specific user

'''

NEWLINE = '\n'
DELIMITER = ','
users = {}
logins = {}

class Message:
		
	def __init__(self, sender, msg):
		self.sender = sender
		self.msg = msg
		self.date = datetime.datetime.now()

	def __str__(self):
		body = "[" + str(self.date.date())
		body += " " + str(self.date.hour) + ":" + str(self.date.minute) + "] "
		body += self.sender + ": " + self.msg
		return(body)

class User:
	
	def __init__(self, nickname, password):
		self.nickname = nickname
		self.password = password
		self.receivedMessages = []

	def validPassword(self, password):
		return(self.password == password)

	def changePassword(self, oldPassword, newPassword):
		if self.password == oldPassword:
			self.password = newPassword
			return(True)
		else:
			return(False)

	def newMessage(self, sender, msg):
		self.receivedMessages.append(Message(sender, msg))
		return(True)

	def getMessages(self, sender=''):
		if sender == '':
			strMsgs = map(str, self.receivedMessages)
		else:
			strMsgs = [str(m) for m in self.receivedMessages if m.sender == sender]
		
		return(NEWLINE.join(strMsgs))

def register(nickname, password, address):
	if nickname in users:
		returnValue = "nickname already in use"
	elif address in logins:
		returnValue = "you cannot register being logged"
	else:
		users[nickname] = User(nickname, password)
		returnValue = "user " + nickname + " was registered"

	return(returnValue)

def login(nickname, password, address):
	if nickname in users:
		if address in logins and logins[address] == nickname:
			returnValue = "user already logged"
		elif users[nickname].validPassword(password):
			logins[address] = nickname
			returnValue = "logged in user"
		else:
			returnValue = "wrong data"
	else:
		returnValue = "wrong data"

	return(returnValue)

def logout(address):
	if address in logins:
		del logins[address]
		returnValue = "logged out"
	else:
		returnValue = "you are already logged out"

	return(returnValue)

def see():
	userl = list(users.keys())
	userl.sort()
	if len(userl) != 0:
		returnValue = '\n'.join(userl)
	else:
		returnValue = "there are no users"

	return(returnValue)

def send(nickname, msg, address):
	if nickname in users:
		users[nickname].newMessage(logins[address], msg)
		returnValue = "message send to " + nickname
	else:
		returnValue = nickname + " is not a registered user"
	return(returnValue)

def read(address, sender=''):
	if sender != '':
		returnValue = users[logins[address]].getMessages(sender=sender)
	else:
		returnValue = users[logins[address]].getMessages()
	return(returnValue)

def loggedActions(args, address):
	
	command = args[0]
	returnValue = ""

	if command == 'see':
		returnValue = see()
	elif command == 'send':
		returnValue = send(args[1], args[2], address)
	elif command == 'read':
		if len(args) == 2:
			returnValue = read(address, sender=args[1])
		else:
			returnValue = read(address)
	else:
		returnValue = "command not found"

	return(returnValue)

def evaluate(args, address):
	
	command = args[0]
	returnValue = ""

	if command == 'register':
		returnValue = register(args[1], args[2], address)
	elif command == 'login':
		returnValue = login(args[1], args[2], address)
	elif command == 'logout':
		returnValue = logout(address)
	elif address in logins:
		returnValue = loggedActions(args, address)
	else:
		returnValue = "command not found or require login"

	returnValue += NEWLINE
	return(returnValue)
		
def on_new_client(clientsocket, address):
	while True:
		dataBytes = clientsocket.recv(1024)
		if not dataBytes: break
		dataString = dataBytes.decode()
		args = dataString.strip().split(DELIMITER)
		print(address, args)
		result = evaluate(args, address)
		clientsocket.sendall(result.encode())
	clientsocket.close()

port = int(sys.argv[1] if len(sys.argv) > 1 else 9090)
s = socket.socket()
s.bind(('', port))

s.listen(1)
print("Esperando conexões na porta %s..." % port)

while True:
	conection, address = s.accept()
	print("Cliente em %s:%s" % address)
	Thread(target=on_new_client, args=(conection, address)).start() 
