import socket, sys
import threading


listOfRooms = {}
listOfRoomsIds = {}



def closeAllRooms():
    for key in listOfRooms:
        print(key)
        closeAllPorts((listOfRooms[key])[0].listOfClients)
        print("All ports closed. Goodbye.")
        sys.exit()

def closeAllPorts(listOfClients):
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        socket.send(("-9999").encode())

def deleteClient(listOfClients, name):
    del listOfClients[name]

def parseName(joinMessage):
    Username = joinMessage.split()[8]
    chatroomName = joinMessage.split()[2]
    return chatroomName, Username

def parseMessage(chatMessage):
    splitMessage = chatMessage.split()
    chatroom = int(splitMessage[1])
    joinID = int(splitMessage[3])
    clientName = splitMessage[5]
    message = splitMessage[7:]
    message = " ".join(message)
    return chatroom, joinID, clientName, message

def HELO(host, port, message):
    return  message + "\nIP: " + str(host) + "\nPort: " + str(port) + "\nStudentID: 14313774\n" 

def createChatBroadcast(roomID, clientName, message):
    return "CHAT: " + str(roomID) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + message

def createJoinBroadcast(chatroomName, host, port, roomID, joinID):
    return "JOINED_CHATROOM: " + chatroomName + "\nSERVER_IP: " + str(host) + "\nPORT: " + str(port) + "\nROOM_REF: " +  str(roomID) + "\nJOIN_ID: " + str(joinID)

#Function which broadcast a message to all connected clients bar the server and the one that sent the message
def broadCastData(listOfClients,sock, message):
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        if socket != sock:
            try:
                #Send the message to the current client socket
                socket.send(message.encode())
            except: 
                #Client socket not working, close it and remove it from the list of sockets
                print("Socket not working. Closing down that connection")
                socket.close()
                del listOfClients[key]

#CLASS FOR EACH CHATROOM
class chatRoom(object):
    def __init__(self, name, firstClient, firstClientName, roomID):
        self.ChatroomName = name
        self.listOfClients = {}
        self.listOfClients[firstClientName] = [firstClient,firstClientName, 1]
        self.ID = roomID
        self.numberOfClients = 1
        self.clientIDs = 1

#MAIN CLASS
class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.finished = False
        self.chatRoomIdCount = 0
    
    def listen(self):
        self.sock.listen(5)
        while True:
            if self.finished:
                return
            client, address = self.sock.accept()
            socketKey = address[1]
            client.settimeout(120)
            threading.Thread(target = self.listenToClient, args = (client, address, socketKey)).start()

    def listenToClient(self, client, address, socketKey):
        while True:
            
            if self.finished == True:
                return

            data = (client.recv(1024)).decode()
            if data:
                #CLIENT SENDS JOIN MESSAGE
                if(data[:13] == "JOIN CHATROOM"):
                    chatroomName, clientName = parseName(data)
                    if  chatroomName not in listOfRooms:
                        listOfRooms[chatroomName] = [chatRoom(chatroomName,client, clientName, self.chatRoomIdCount)]
                        listOfRoomsIds[self.chatRoomIdCount] = [chatroomName]
                        self.chatRoomIdCount += 1
                    else:
                        (listOfRooms[chatroomName])[0].listOfClients[socketKey] = ([client, clientName, (listOfRooms[chatroomName])[0].clientIDs])
                    
                    (listOfRooms[chatroomName])[0].numberOfClients += 1
                    print(clientName," has joined: ", chatroomName)
                    print(clientName, " has the JoinID: ", (listOfRooms[chatroomName])[0].clientIDs)
                    client.send((createJoinBroadcast(chatroomName, self.host, self.port, (listOfRooms[chatroomName])[0].ID, (listOfRooms[chatroomName])[0].clientIDs)).encode())
                    (listOfRooms[chatroomName])[0].clientIDs += 1
                    broadCastData((listOfRooms[chatroomName])[0].listOfClients, client, "<" + clientName + "> has joined the room")
                    
                #CLIENT SENDS CHAT MESSAGE
                elif(data[:4] == "CHAT"):
                    roomID, joinID, clientName, message = parseMessage(data)
                    chatroomName = (listOfRoomsIds[roomID])[0]
                    if (message == "KILL_SERVICE"):
                        print("Terminating service")
                        closeAllRooms()
                        return
                    elif (message[:4] == "HELO"):
                        response = HELO(self.host, self.port, message).encode()
                        client.send(response)
                    elif (message == "DISCONNECT"):
                        broadCastData((listOfRooms[chatroomName])[0].listOfClients,client,"<" + clientName + "> has disconnected from the server")
                        client.send(("-9999").encode())
                    else:
                        chatroomName = (listOfRoomsIds[roomID])[0]
                        broadCastData((listOfRooms[chatroomName])[0].listOfClients, client, createChatBroadcast(roomID,clientName, message))

if __name__ == "__main__":
    
    if(len(sys.argv) > 0):
        portNum = int(sys.argv[1])
    else:
        portNum = 5000
    host = "134.226.38.26"
    
    print("Server started on: ", host,":", portNum )
    ThreadedServer(host,portNum).listen()
