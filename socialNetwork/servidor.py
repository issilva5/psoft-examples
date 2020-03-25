#coding: utf-8
import socket
import sys
import re
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

'''

NEWLINE = '\n'
users = {}
logins = {}

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

	def newMessage(self, msg):
		self.receivedMessages.append(msg)
		return(True)

def loggedActions(args):

	returnValue = ""

	if args[0] == 'see':
		userl = list(users.keys())
		userl.sort()
		if len(userl) != 0:
			returnValue = '\n'.join(userl)
		else:
			returnValue = "there are no users"
	else:
		returnValue = "command not found"

	return(returnValue)

def evaluate(args, address):
	print(args)
	returnValue = ""

	if args[0] == 'register':
		users[args[1]] = User(args[1], args[2])
		returnValue = "user " + args[1] + " was registered"
	elif args[0] == 'login':
		if args[1] in users:
			if users[args[1]].validPassword(args[2]):
				logins[address] = args[1]
				returnValue = "logged in user"
			else:
				returnValue = "wrong data"
		else:
			returnValue = "wrong data"
	elif args[0] == 'logout':
		if address in logins:
			del logins[address]
			returnValue = "logged out"
		else:
			returnValue = "you are already logged out"
	elif address in logins:
		returnValue = loggedActions(args)
	else:
		returnValue = "command not found or require login"

	returnValue += NEWLINE
	return(returnValue)
		
def on_new_client(clientsocket, address):
	while True:
		dataBytes = clientsocket.recv(1024)
		if not dataBytes: break
		dataString = dataBytes.decode()
		args = dataString.strip().split(',')
		result = evaluate(args, address)
		print(result)
		clientsocket.sendall(result.encode())
	clientsocket.close()

port = int(sys.argv[1] if len(sys.argv) > 1 else 9090)
s = socket.socket()
s.bind(('', port))

s.listen(1)

while True:
	print("Esperando conexões na porta %s..." % port)
	conection, address = s.accept()
	print("Cliente em %s:%s" % address)
	Thread(target=on_new_client, args=(conection, address)).start() 
