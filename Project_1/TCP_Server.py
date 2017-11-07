# chat_server.py

#Outline (Need to get it working like this)#

###########################################
#Start server
#check for connection
#if there is one, create new client object
#client object runs starting a new thread
#if it gets a message, broadcast it 
#if the pipe breaks, the client disconnects
###########################################

from threading import Thread 
import socket, select

class threadForClient(Thread):

	def __init__(self, ip, port):
		Thread.__init__(self)
		self.ip = ip
		self.port = port
		print("New server socket thread started for client: ", ip, ":", port)

	def run(self):
		while True:
			try:
				data = conn.recv(RECV_BUFFER)
				broadCastData()		
			except BrokenPipeError as e:
					print(e)


def parseName(joinMessage):
	Username = joinMessage.split()[9:]
	return Username

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
					data = sock.recv(RECV_BUFFER)
					if data:
						data = data.decode()
						if(data[:13] == "JOIN CHATROOM"):
							Username = parseName(data)
							print("Connection list: ",CONNECTION_LIST)
							print(Username, "has joined the room.")
							broadCastData(sock, Username + "has joined the room.")
						else:
							print("Data: ", data[:13] )
							print("Message thing didn't work")
							broadCastData(sock, "\r" + "<>" + data)
				except:
					print("About to close connection")
					broadCastData(sock, "Client (%s, %s) is offline" % addr)
					print("Client", addr, "is offline")
					sock.close()
					CONNECTION_LIST.remove(sock)
					continue

serverSocket.close()