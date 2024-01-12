import sys
import time
import im

# Set up server object
server = im.IMServerProxy(
    "https://web.cs.manchester.ac.uk/j46835ss/comp28112_ex1/IMserver.php")

print("Welcome doctors\nEnter your messages in the terminal")
print("Please send Q to quit the program\n")

# Assign user an ID based on who joins first
# Checks if user ID exists already
# If not it will assign ID
if(server.__getitem__("doc1_key") != b'1\n'):
    server.__setitem__("doc1_key", "1")
    doc_id = server.__getitem__("doc1_key")

elif (server.__getitem__("doc2_key") != b'2\n'):
    server.__setitem__("doc2_key", "2")
    doc_id = server.__getitem__("doc2_key")
    print("Waiting for message\n")
# Will prevent a third user from joining
else:
    print("Two users are currently usign the program, try again later")
    sys.exit()

# Actions depend on user ID
while(True):
    # User 1 takes input first
    # Message is sent to server and
    # Boolean is set as True so User 2 can see if received
    if(doc_id == b'1\n'):
        message = input("Doctor One enter your message:\n--> ")
        server.__setitem__("doc1_message", message)
        server.__setitem__("received_one", "True")
        # If user quits it will end program
        if(message == "Q"):
            print("You have quit the program bye")
            sys.exit()
        print("Waiting for reply\n")
        time.sleep(1)
        # Will keep checking for received signal for reply
        # Once received it will decode message
        # If message is quit it will clear server and exit
        while(True):
            if(server.__getitem__("received_two").decode() != "True\n"):
                continue
            else:
                getmessage1 = server.__getitem__("doc2_message").decode()
                if(getmessage1 == "Q\n"):
                    print("Doc Two has quit, the program will now end")
                    server.clear()
                    sys.exit()
                else:
                    break
        # If normal message it will display message
        # Resets received signal
        print("Doc two:\n--> "+str(getmessage1))
        server.__setitem__("received_two", "False")

    # User 2 waits for message first
    # When message received checks for quit
    elif(doc_id == b'2\n'):
        while(True):
            if(server.__getitem__("received_one").decode() != "True\n"):
                continue
            else:
                getmessage2 = server.__getitem__("doc1_message").decode()
                if(getmessage2 == "Q\n"):
                    print("Doc One has quit, the program will now end")
                    server.clear()
                    sys.exit()
                else:
                    break
        # User 2 then gives input and sets signal for user 1 to recieve
        # Message is sent to server and user 2 waits again
        print("Doc One:\n--> "+str(getmessage2))
        server.__setitem__("received_one", "False")
        message = input("Doctor Two enter your message:\n--> ")
        server.__setitem__("doc2_message", message)
        server.__setitem__("received_two", "True")
        if(message == "Q"):
            print("You have quit the program bye")
            sys.exit()
        print("Waiting for reply\n")
        time.sleep(1)
