from socket import socket
import sys
from ex2utils import Server

class myserver(Server):


	def onStart(self):
		# Initialise server variables 
		myserver.count = 0
		myserver.users = {}
		print("Server has started")
		
	def onMessage(self, socket, message):

		(command, sep, parameter) = message.strip().partition(' ')

		if(command == "REGISTER"):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			myserver.onRegister(self, socket, parameter)
		elif(command == "HELP"):
			print('Command is ', command)
			myserver.send(self, "Command Details:"
						+"\n'REGISTER'   -> Register new user" 
						+"\n'MESSAGEALL' -> Send message to all active users on system"
						+"\n'MESSAGE'    -> Send direct message to specified user"
						+"\n'ALLUSERS'   -> Displays list of all active users"
						+"\n'HELPLIST'   -> Displays list of all commands and how to use them"
						+"\n'HELP'       -> Information about commands"
						, socket)
		elif(command == "HELPLIST"):
			print('Command is ', command)
			myserver.send(self, "List of commands:\n'<REGISTER>'   '<username>'\n'<MESSAGEALL>' '<message>'\n'<MESSAGE>'    '<username>' '<message>'\n'<ALLUSERS>'\n'<HELPLIST>'", socket)
		elif(command == "QUIT"):
			print('Command is ', command)
			# myserver.onDisconnect(self, socket)
		elif((command != "REGISTER" or command != "HELP" or command != "HELPLIST" or command != "QUIT") and socket.name == ""):
			myserver.send(self, "Please register before using messaging commands", socket)
		elif(command == "MESSAGEALL"):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			print("MESSAGING ALL USERS")

			if(parameter.strip() == ""):
				myserver.send(self, "Blank message entered, please enter valid message", socket)
			else:
				parameter = f"\n{socket.name}: {parameter}"
				message=parameter.encode()
				for s in myserver.users.values():
					if s != socket:
						s.send(message)
		elif(command == "MESSAGE"):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			(user, sep, message) = parameter.strip().partition(' ')
			if(message.strip() == ""):
				myserver.send(self, "Blank message entered, please enter valid message", socket)
			else:
				if (user == socket.name):
					myserver.send(self, "You cannot send a message to yourself", socket)
				else:
					if(user in myserver.users.keys()):
						print('SENDING MESSAGE TO: ', user)
						print ('MESSAGE IS: ',message)
						user_socket = myserver.users.get(user)
						message = f"\n{socket.name}: {message}"
						message = message.encode()
						user_socket.send(message)
					else:
						myserver.send(self, "User does not active, please try again or use <SEEALL> to see active users", socket)
		elif(command == "ALLUSERS"):
			print('Command is ', command)
			print("DISPLAYING ALL USERS")
			myserver.send(self, "All Active Users:", socket)
			for name in myserver.users.keys():
				if name == socket.name:
					name = f"{name} (ME)"
				name=name.encode()
				socket.send(name)
		else:
			myserver.send(self, "No command found, please type HELPLIST for list of commands OR HELP for more information on commands", socket)
	
		# Signify all is well
		return True

	def onConnect(self, socket):
		# setattr(socket, "name", "")
		socket.name = ""
		# convert the string to an upper case version
		myserver.send(self, "Connected, please register your name\nEnter '<REGISTER>' '<username>' ", socket)
		myserver.count += 1
		print(f"Number of connections: {myserver.count}")
		# Signify all is well
		return True

	def onDisconnect(self, socket):
		if socket.name in myserver.users:
			myserver.users.pop(socket.name)
		socket.close()
		print("User Disconnected")
		myserver.count-=1
		print(f"Number of connections: {myserver.count}")
		return False

	def onRegister(self, socket, name):
		# validate user name to one word only 
		if (" " in name ):
			myserver.send(self, "Name can only be one word please try again", socket)
		elif(socket in myserver.users.values()):
			myserver.send(self, "You are already registered", socket)
		elif(name in myserver.users.keys()):
			myserver.send(self, "User already exists with given name\nPlease enter another name", socket)
		elif(name not in myserver.users.keys() and socket not in myserver.users.values()):
			myserver.users.update({name: socket})
			socket.name = name
			print("NEW USER", name)
			myserver.send(self, f"Registered sucessfully, Welcome {name}!!", socket)

	def send(self, message, socket):
		message=message.encode()
		socket.send(message)

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an echo server.
server = myserver()

# Start server
server.start(ip, port)

