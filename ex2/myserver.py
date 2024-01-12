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
		# Split input into command and parameter
		(command, sep, parameter) = message.strip().partition(' ')
		
		if(command == "MESSAGEALL" and socket.registered == True):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			print("MESSAGING ALL USERS")
			# Check for blank input
			if(parameter.strip() == ""):
				print("INVALID COMMAND")
				myserver.send(self, "Blank message entered, please enter valid message", socket)
			else:
				# Loop through users and send message to each
				# Exclude user whos sending message
				parameter = f"\n{socket.name}: {parameter}"
				message=parameter.encode()
				for s in myserver.users.values():
					if s != socket:
						s.send(message)
		elif(command == "MESSAGE" and socket.registered == True):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			(user, sep, message) = parameter.strip().partition(' ')
			if(message.strip() == ""):
				print("INVALID COMMAND")
				# Check for blank input
				myserver.send(self, "Blank message entered, please enter valid message", socket)
			else:
				if (user == socket.name):
					print("INVALID COMMAND")
					myserver.send(self, "You cannot send a message to yourself", socket)
				else:
					# Check if user is in user dict
					# if found send user message using socket
					if(user in myserver.users.keys()):
						print('SENDING MESSAGE TO: ', user)
						print ('MESSAGE IS: ',message)
						user_socket = myserver.users.get(user)
						message = f"\n{socket.name}: {message}"
						message = message.encode()
						user_socket.send(message)
					else:
						myserver.send(self, "User is not active, please try again or use <SEEALL> to see active users", socket)
		# Run command if registered
		elif(command == "ALLUSERS" and socket.registered == True):
			print('Command is ', command)
			print("DISPLAYING ALL USERS")
			myserver.send(self, "All Active Users:", socket)
			for name in myserver.users.keys():
				if name == socket.name and (myserver.users.get(name)).hidden == False:
					name = f"{name} (ME)"
				name=name.encode()
				socket.send(name)
		# Run command if registered
		elif(command == "CHECK" and socket.registered == True):
			print('Command is ', command)
			if(parameter.strip() == ""):
				print("INVALID COMMAND")
				myserver.send(self, "Blank name entered, please enter valid user", socket)
			else:
				if (parameter == socket.name):
					myserver.send(self, "You are an active user", socket)
				else:
					# Checks if active user is hidden before showing active users
					if(parameter in myserver.users.keys() and (myserver.users.get(parameter)).hidden == False):
						myserver.send(self, f"{parameter} is an active user", socket)
					else:
						myserver.send(self, f"{parameter} is not currently an active user", socket)

		elif(command == "HIDE" and socket.registered == True):
			print('Command is ', command)
			# Swap value of hidden
			if(socket.hidden == False):
				socket.hidden = True
			else:
				socket.hidden = False

		elif(command == "REGISTER"):
			print('Command is ', command)
			print ('Parameter is ',parameter)
			# Validate for character length and blank username
			if(parameter.strip() == ""):
				print("INVALID COMMAND")
				myserver.send(self, "Blank name entered, please enter valid name", socket)
			elif(len(parameter) > 10):
				print("INVALID COMMAND")
				myserver.send(self, "Name entered is too long, please enter valid name < 10 characters", socket)
			else:
				myserver.onRegister(self, socket, parameter)
		elif(command == "HELP"):
			print('Command is ', command)
			# Display commands to user
			myserver.send(self, "Command Details:"
						+"\n'REGISTER'   -> Register new user" 
						+"\n'MESSAGEALL' -> Send message to all active users on system"
						+"\n'MESSAGE'    -> Send direct message to specified user"
						+"\n'ALLUSERS'   -> Displays list of all active users"
						+"\n'CHECK'      -> Checks to see if a specific user is active"
						+"\n'HIDE'       -> Allows user to hide so they dont show as active on system, but can still receive messages, use hide again to unhide"
						+"\n'HELPLIST'   -> Displays list of all commands and how to use them"
						+"\n'HELP'       -> Information about commands"
						+"\n'QUIT'       -> Allows the user to quit and exit the program", socket)
		elif(command == "HELPLIST"):
			print('Command is ', command)
			# Display commands format to user
			myserver.send(self, "List of commands:"
						+"\n'<REGISTER>'   '<username>'"
						+"\n'<MESSAGEALL>' '<message>'"
						+"\n'<MESSAGE>'    '<username>' '<message>'"
						+"\n'<ALLUSERS>'"
						+"\n'<CHECK>'      '<username>'"
						+"\n'<HIDE>'"
						+"\n'<HELPLIST>'"
						+"\n'<HELP>'"
						+"\n'<QUIT>'", socket)
		elif(command == "QUIT"):
			print('Command is ', command)
			return False
			# myserver.onDisconnect(self, socket)
		elif((command != "REGISTER" or command != "HELP" or command != "HELPLIST" or command != "QUIT") and socket.name == ""):
			myserver.send(self, "Please register before using messaging commands", socket)

		else:
			myserver.send(self, "No command found, please type HELPLIST for list of commands OR HELP for more information on commands", socket)
	
		# Signify all is well
		return True

	def onConnect(self, socket):
		# initialise socket attributes
		socket.name = ""
		socket.hidden = False
		socket.registered = False
		# convert the string to an upper case version
		myserver.send(self, "Connected, please register your name\nEnter '<REGISTER>' '<username>' ", socket)
		myserver.count += 1
		print(f"Number of Clients: {myserver.count}")
		# Signify all is well
		return True

	def onDisconnect(self, socket):
		# Remove user from user dict
		if socket.name in myserver.users:
			myserver.users.pop(socket.name)
		socket.close()
		print("User Disconnected")
		myserver.count-=1
		print(f"Number of Clients: {myserver.count}")
		return True

	def onStop(self):
		# Reset server variables 
		myserver.count = 0
		myserver.users = {}
		print("Server has Stopped")

	def onRegister(self, socket, name):
		# validate user name to one word only 
		# validate user name already exists 
		if (" " in name ):
			myserver.send(self, "Name can only be one word please try again", socket)
		elif(socket in myserver.users.values()):
			myserver.send(self, "You are already registered", socket)
		elif(name.upper() in myserver.users.keys()):
			myserver.send(self, "User already exists with given name\nPlease enter another name", socket)
		elif(name.upper() not in myserver.users.keys() and socket not in myserver.users.values()):
			myserver.users.update({name.upper(): socket})
			socket.name = name
			print("NEW USER", name)
			myserver.send(self, f"Registered sucessfully, Welcome {name}!!", socket)
			socket.registered = True

	def send(self, message, socket):
		message=message.encode()
		socket.send(message)

# Parse the IP address and port you wish to listen on.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create a server.
server = myserver()

# Start server
server.start(ip, port)

