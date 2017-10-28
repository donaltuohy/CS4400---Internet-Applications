# chat_server.py

 
import socket, select


#Function which broadcast a message to all connected clients bar the server and the one that sent the message
def broadCastData(sock, message):
	for socket in CONNECTION_LIST:
		if socket != serverSocket and socket != sock:
			try:
				#Send the message to the current client socket
				socket.send(message.encode())
			except: 
				#Client socket not working, close it and remove it from the list of sockets
				print("Socket not working. Closing down that connection")
				socket.close()
				CONNECTION_LIST.remove(socket)

if __name__ == "__main__":
	#List to keep track of socket descriptors
	CONNECTION_LIST = []
	RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
	PORT = 5000
	
	#Initialize the main server socker
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverSocket.bind(("0.0.0.0", PORT))
	serverSocket.listen(10)
 
	#Add server socket to the list of readable connections
	CONNECTION_LIST.append(serverSocket)

	print ("Chat server started on port ", str(PORT))


	while 1:
		readSockets, writeSockets, errorSockets = select.select(CONNECTION_LIST, [], [])

		for sock in readSockets:
			#New Connection
			if sock == serverSocket:
				#Deals with a new socket trying to connect to server, adds it to the connection list
				sockfd, addr = serverSocket.accept()
				CONNECTION_LIST.append(sockfd)
				print("Client ",addr," connected")
				broadCastData(sockfd, "[%s,%s] entered room\n" % addr)

			#Not a connection request so must be a message
			else:
				#Data recieved from client so set up a try process
				try:
					data = sock.recieve(RECV_BUFFER)
					if data:
						data = data.decode()
						broadCastData(sock, "\r" + "<" + str(sock.getpeername()) + ">" + data)
				except:
					broadCastData(sock, "Client (%s, %s) is offline" % addr)
					print("Client", addr, "is offline")
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue

serverSocket.close()