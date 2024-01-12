"""

IRC client exemplar.

"""

import sys
from ex2utils import Client
import signal

import time

timeout = 2

class myClient(Client):

    def onMessage(self, socket, message):
        # *** process incoming messages here ***
        print(message)
        return True


# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])

# Create an IRC client.
client = myClient()

# Start server
client.start(ip, port)

# #send message to the server

while(True):
    try:
        message = input()
        if(message.strip() == "QUIT"):
            client.send(message.encode())
            break
        client.send(message.encode())
    except OSError:
        print("Server has ended, the program will quit")
        break
    except KeyboardInterrupt:
        print("To exit program enter QUIT")


#stops client
client.stop()
