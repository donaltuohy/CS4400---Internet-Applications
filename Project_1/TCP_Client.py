#
# TCP Client
#
from socket import *
from ctypes import *
import time

#Setting up the socket
serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

message = input("Enter your message: ")

clientSocket.send(message)
	
print ('Data sent to server.')

clientSocket.close()
