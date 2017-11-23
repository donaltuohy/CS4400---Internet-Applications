import socket, sys
import threading


### Dictionaries ###
listOfRooms = {}
listOfConnectedClients = {}
listOfRoomsIds = {}

### Functions for creating and parsing messages ###

#Deletes all clients in a given list of clients
def closeAllPorts(listOfClients):
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        socket.send(("-9999").encode())

#Function that closes every chatroom open
def closeAllRooms():
    for key in listOfRooms:
        print(key)
        closeAllPorts((listOfRooms[key])[0].listOfClients)
        print("All ports closed. Goodbye.")
        sys.exit()

#Deletes a certain client from a chatroom list of clients
def deleteClient(listOfClients, clientName):
    del listOfClients[clientName]

#Given a message, takes out the clientName and chatroomName
def parseName(joinMessage):
    Username = joinMessage.split()[7]
    chatroomName = joinMessage.split()[1]
    return chatroomName, Username

#Given a leave message, parses each part and returns them as seperate variables 
def parseLeave(leaveMessage):
    splitMessage = leaveMessage.split()
    chatID = int(splitMessage[1])
    joinID = int(splitMessage[3])
    clientName = splitMessage[5]
    return chatID, joinID, clientName

#Given a chat message, parses each part and returns them as seperate variables
def parseMessage(chatMessage):
    splitMessage = chatMessage.split()
    chatroom = int(splitMessage[1])
    joinID = int(splitMessage[3])
    clientName = splitMessage[5]
    message = splitMessage[7:]
    message = " ".join(message)
    return chatroom, joinID, clientName, message

#Returns a string in the fromat given for when a HELO message is sent
def HELO(host, port, message):
    return  message + "IP: " + str(host) + "\nPort: " + str(port) + "\nStudentID: 14313774\n" 

#Given the parameters, creates a chat message whhich is recognised by all clients
def createChatBroadcast(roomID, clientName, message):
    return "CHAT: " + str(roomID) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + message + "\n"

#Returns the correct string to sends to a client when it has sent a leave message 
def createLeaveResponse(roomID, joinID):
    return "LEFT_CHATROOM: " + str(roomID) + "\nJOIN_ID: " + str(joinID) + "\n"

#
#def removeClientFromList(listOfClients, clientName):
#    del listOfClients[clientName]

#Given the parameters return a specific "joined chatroom" message
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

### CLASSES ###

#Client class
class clientObject(object):

    #Constructor for client object
    def __init__(self, client, name, firstRoomID, joinID):
        self.clientName = name
        self.joinedRooms = {}
        self.joinedRooms[firstRoomID] = joinID
        self.sock = client 

#Chatroom class
class chatRoom(object):

    #Constructor for chatroom object
    def __init__(self, name, firstClient, firstClientName, roomID):
        self.ChatroomName = name
        self.listOfClients = {}
        self.listOfClients[firstClientName] = [firstClient,firstClientName, 1]
        self.ID = roomID
        self.numberOfClients = 1
        self.clientIDs = 1

    #Method which returns the Id for a new client and increments the total ID count
    def getNewID(self):
        self.clientIDs += 1
        self.numberOfClients += 1
        return self.clientIDs


#MAIN CLASS
class ThreadedServer(object):

    #Constructor for the server 
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.finished = False
        self.chatRoomIdCount = 0
    
    #Method which listens for new connections
    def listen(self):
        self.sock.listen(5)
        while True:
            if self.finished:
                return
            client, address = self.sock.accept()
            socketKey = address[1]
            client.settimeout(120)
            #Create a thread using the "listenToClient" function which will handle that client in it's own thread.
            threading.Thread(target = self.listenToClient, args = (client, address, socketKey)).start()

    #Method which is called by client thread and constantly listens for incoming data form the client
    def listenToClient(self, client, address, socketKey):

        #Constantly loop though this function
        while True:
            print("Listening...")
            if self.finished == True:
                print("Finished is true")
                return
            
            #The thread will block here and wait for data sent by the client, data must then be decoded
            data = (client.recv(1024)).decode()
            if data:

                #Client sends HELO message - return the correct response using the HELO function created above
                if(data[:4] == "HELO"):
                    response = HELO(self.host, self.port, data).encode()
                    client.send(response)

                #Client sends LEAVE message - send back the "LEFT CHATROOM" response and post a relevant notification to that chat room
                elif(data[:5] == "LEAVE"):
                    #Parse the data from the Leave message
                    roomID, joinID, clientName = parseLeave(data)
                    chatroomName = (listOfRoomsIds[roomID])[0]
                    #Create a corresponding leave response to be sent back and send it to the client
                    leaveResponse = createLeaveResponse(roomID, joinID)
                    client.send(leaveResponse.encode())
                    #Remove that client from the chatroom
                    deleteClient((listOfRooms[chatroomName])[0].listOfClients,clientName)
                    #Create a message to be broadcast to the chatroom, notifying clients that a client has left
                    leftBroadcast = "<" +clientName + "> has left the room."
                    broadCastData((listOfRooms[chatroomName])[0].listOfClients, client,leftBroadcast)

                #Client sends JOIN message - check if chatroom exists, create one if not. Then add client to listOfConnected clients of not already in it 
                elif(data[:13] == "JOIN_CHATROOM"):
                    #Parse message to get relevant data
                    chatroomName, clientName = parseName(data)
                    #Add a new chatroom if not present. (The chatroom constructor takes in the details of the client that created it and automatically adds them to the client list)
                    if  chatroomName not in listOfRooms:
                        listOfRooms[chatroomName] = [chatRoom(chatroomName,client, clientName, self.chatRoomIdCount)]
                        listOfRoomsIds[self.chatRoomIdCount] = [chatroomName]
                        self.chatRoomIdCount += 1
                    #Add new client to the chatroom if chatroom exists
                    else:
                        (listOfRooms[chatroomName])[0].listOfClients[clientName] = ([client, clientName, (listOfRooms[chatroomName])[0].clientIDs])
                    #Retrieve the room and join id for this current action 
                    currRoomId = (listOfRooms[chatroomName])[0].ID
                    currJoinId = (listOfRooms[chatroomName])[0].clientIDs
                    #If new client, add client to global list of clients
                    if client not in listOfConnectedClients:
                        listOfConnectedClients[client] = clientObject(client,clientName, currRoomId, currJoinId)
                    #Else add this room to the list of connected room for this certain client
                    else:
                        (listOfConnectedClients[client]).joinedRooms[currRoomId] = currJoinId
                    client.send((createJoinBroadcast(chatroomName, self.host, self.port, (listOfRooms[chatroomName])[0].ID, (listOfRooms[chatroomName])[0].clientIDs)).encode())
                    joinchat = createChatBroadcast((listOfRooms[chatroomName])[0].ID,clientName, "<" + clientName + "> has joined the room")
                    client.send(joinchat.encode())
                    print((listOfConnectedClients[client]).joinedRooms[currRoomId])
                    (listOfRooms[chatroomName])[0].numberOfClients += 1
                    print(clientName," has joined: ", chatroomName)
                    print(clientName, " has the JoinID: ", (listOfRooms[chatroomName])[0].clientIDs)
                    (listOfRooms[chatroomName])[0].clientIDs += 1
                    broadCastData((listOfRooms[chatroomName])[0].listOfClients, client, joinchat)
                    
                    
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
    host = "127.0.0.1"
    
    print("Server started on: ", host,":", portNum )
    ThreadedServer(host,portNum).listen()
