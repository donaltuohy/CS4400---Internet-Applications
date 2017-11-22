import socket, sys
import threading


listOfRooms = {}
listOfConnectedClients = {}
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

def deleteClient(listOfClients, socketKey):
    del listOfClients[socketKey]

def parseName(joinMessage):
    Username = joinMessage.split()[7]
    chatroomName = joinMessage.split()[1]
    return chatroomName, Username

def parseLeave(leaveMessage):
    splitMessage = leaveMessage.split()
    chatID = int(splitMessage[1])
    joinID = int(splitMessage[3])
    clientName = splitMessage[5]
    return chatID, joinID, clientName


def parseMessage(chatMessage):
    splitMessage = chatMessage.split()
    chatroom = int(splitMessage[1])
    joinID = int(splitMessage[3])
    clientName = splitMessage[5]
    message = splitMessage[7:]
    message = " ".join(message)
    return chatroom, joinID, clientName, message

def HELO(host, port, message):
    return  message + "IP: " + str(host) + "\nPort: " + str(port) + "\nStudentID: 14313774\n" 

def createChatBroadcast(roomID, clientName, message):
    return "CHAT: " + str(roomID) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + message + "\n"

def createLeaveResponse(roomID, joinID):
    return "LEFT_CHATROOM: " + str(roomID) + "\nJOIN_ID: " + str(joinID) + "\n"

def removeClientFromList(listOfClients, clientName):
    del listOfClients[clientName]

def createJoinBroadcast(chatroomName, host, port, roomID, joinID):
    return "JOINED_CHATROOM: " + chatroomName + "\nSERVER_IP: " + str(host) + "\nPORT: " + str(port) + "\nROOM_REF: " +  str(roomID) + "\nJOIN_ID: " + str(joinID) +"\n"

#Function which broadcast a message to all connected clients bar the server and the one that sent the message
def broadCastData(listOfClients,sock, message):
    print("Broadcasting: ", message)
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

class clientObject(object):
    def __init__(self, client, name, firstRoomID, joinID):
        self.clientName = name
        self.joinedRooms = {}
        self.joinedRooms[firstRoomID] = joinID
        self.sock = client 

class chatRoom(object):
    def __init__(self, name, firstClient, firstClientName, roomID):
        self.ChatroomName = name
        self.listOfClients = {}
        self.listOfClients[firstClientName] = [firstClient,firstClientName, 1]
        self.ID = roomID
        self.numberOfClients = 1
        self.clientIDs = 1

    def getNewID(self):
        self.clientIDs += 1
        self.numberOfClients += 1
        return self.clientIDs

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
            try:
                print("Listening...")
                if self.finished == True:
                    print("Finished is true")
                    return

                data = (client.recv(1024)).decode()

                if data:
                    print(data)
                    #CLIENT SENDS JOIN MESSAGE
                    if(data[:4] == "HELO"):
                        response = HELO(self.host, self.port, data).encode()
                        client.send(response)

                    elif(data[:5] == "LEAVE"):
                        chatroomName = (listOfRoomsIds[roomID])[0]
                        print("list of clients: ", (listOfRooms[chatroomName])[0].listOfClients)
                        roomID, joinID, clientName = parseLeave(data)
                        leaveResponse = createLeaveResponse(roomID, joinID)
                        client.send(leaveResponse.encode())
                        leftBroadcast = "<" +clientName + "> has left the room."
                        deleteClient((listOfRooms[chatroomName])[0].listOfClients,socketKey)
                        broadCastData((listOfRooms[chatroomName])[0].listOfClients, client,leftBroadcast)

                    elif(data[:13] == "JOIN_CHATROOM"):
                        chatroomName, clientName = parseName(data)

                        #Add a new chatroom if not present
                        if  chatroomName not in listOfRooms:
                            listOfRooms[chatroomName] = [chatRoom(chatroomName,client, clientName, self.chatRoomIdCount)]
                            listOfRoomsIds[self.chatRoomIdCount] = [chatroomName]
                            self.chatRoomIdCount += 1
                        #Add new client if chatroom exists
                        else:
                            (listOfRooms[chatroomName])[0].listOfClients[socketKey] = ([client, clientName, (listOfRooms[chatroomName])[0].clientIDs])

                        currRoomId = (listOfRooms[chatroomName])[0].ID
                        currJoinId = (listOfRooms[chatroomName])[0].clientIDs

                        #If new client, add client to list of clients
                        if client not in listOfConnectedClients:
                            listOfConnectedClients[client] = clientObject(client,clientName, currRoomId, currJoinId)
                        else:
                            (listOfConnectedClients[client]).joinedRooms[currRoomId] = currJoinId                     
                        
                        print((listOfConnectedClients[client]).joinedRooms[currRoomId])
                        (listOfRooms[chatroomName])[0].numberOfClients += 1
                        print(clientName," has joined: ", chatroomName)
                        print(clientName, " has the JoinID: ", (listOfRooms[chatroomName])[0].clientIDs)
                        client.send((createJoinBroadcast(chatroomName, self.host, self.port, (listOfRooms[chatroomName])[0].ID, (listOfRooms[chatroomName])[0].clientIDs)).encode())
                        (listOfRooms[chatroomName])[0].clientIDs += 1
                        joinchat = createChatBroadcast((listOfRooms[chatroomName])[0].ID,clientName, "<" + clientName + "> has joined the room")
                        broadCastData((listOfRooms[chatroomName])[0].listOfClients, client, joinchat)
                        client.send(joinchat.encode())
                        
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
            except Exception:
                print("Fuccck")
if __name__ == "__main__":
    
    if(len(sys.argv) > 0):
        portNum = int(sys.argv[1])
    else:
        portNum = 5000
    host = "127.0.0.1"
    
    print("Server started on: ", host,":", portNum )
    ThreadedServer(host,portNum).listen()
