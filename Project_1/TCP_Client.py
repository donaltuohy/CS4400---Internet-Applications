import socket, select, string, sys

def prompt():
	sys.stdout.write("<You>")
	sys.stdout.flush()

def JoinChatMessage(chatroomName, userName):
	chatroomName = "JOIN CHATROOM: " + chatroomName + "\n"
	userName = "CLIENT_NAME: " + userName + "\n"
	return chatroomName + "CLIENT_IP: 0\n" + "PORT: 0\n" + userName



if __name__ == "__main__":

	if(len(sys.argv) < 3):
		print("Usage: python telnet.py hostname port")
		sys.exit()
	
	displayName = input("Enter your display name: ")
	
	host = sys.argv[1]
	port = int(sys.argv[2])
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	#connect to remote host
	try:
		s.connect((host, port))
	except:
		print("Unable to connect.")
		sys.exit()
	
	print("Connected to remote host. Chat away good sir!")
	s.send(JoinChatMessage("JIMS ROOM", displayName).encode())
	prompt()

	RECV_BUFFER = 4096

	while 1:
		socketList = [sys.stdin, s]

		# Get the list sockets which are readable
		readSockets, writeSockets, errorSockets = select.select(socketList, [], [])


		for sock in readSockets:
			#incoming message from server
			if sock == s:
				data = sock.recv(RECV_BUFFER)
				if not data:
					print("\nDisconnected from chat server")
					sys.exit()
				else:
						data = data.decode()
						#print data
						sys.stdout.write(data)
						prompt()

			#user entered a message
			else:
				message = sys.stdin.readline()
				s.send(message.encode())
				prompt()

s.close()