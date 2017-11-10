import socket
import threading


listOfRooms = {}
listOfRoomsIds = {}



def closeAllRooms():
    for key in listOfRooms:
        closeAllPorts(listOfRooms[key].listOfClients)
        del listOfRooms[key]
    print("All ports closed. Goodbye.")

def closeAllPorts(listOfClients):
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        socket.send(("-9999").encode())

def parseName(joinMessage):
    Username = joinMessage.split()[8]
    chatroomName = joinMessage.split()[2]
    return chatroomName, Username

def parseMessage(chatMessage):
    splitMessage = chatMessage.split()
    chatroom = splitMessage[1]
    joinID = splitMessage[3]
    clientName = splitMessage[5]
    message = splitMessage[7:]
    return chatroom, joinID, clientName, message

def HELO(host, port):
    return "HELO text\nIP: " + str(host) + "\nPort: " + str(port) + "\nStudentID: 14313774\n" 

def createChatBroadcast(chatroomName, clientName, message):
    return "CHAT: " + chatroomName + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + message

def createJoinBroadcast(chatroomName, host, port, roomID, joinID):
    return "JOINED_CHATROOM: " + chatroomName + "\nSERVER_IP: " + host + "\nPORT: " + port + "\nROOM_REF: " +  roomID + "\nJOIN_ID: " + joinID

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
        self.listOfClients.append([firstClient, firstClientName , 0])
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
        try:
            self.sock.listen(5)
            while True:
                if self.finished:
                    return
                client, address = self.sock.accept()
                socketKey = address[1]
                if client:
                    listOfClients[socketKey] = [client,"", self.numberOfJoinID]
                    self.numberOfJoinID += 1
                client.settimeout(50)
                threading.Thread(target = self.listenToClient, args = (client, address, socketKey)).start()
        except:
            print("Closing Down")

    def listenToClient(self, client, address, socketKey):
        while True:
            if self.finished == True:
                return
            try:
                data = (client.recv(1024)).decode()
                if data:
                    
                    #CLIENT SENDS JOIN MESSAGE
                    if(data[:13] == "JOIN CHATROOM"):
                        chatroomName, clientName = parseName(data)
                        if not listOfRooms[chatroomName]:
                            listOfRooms[chatroomName] = [chatRoom(chatroomName,client, clientName, chatRoomIdCount)]
                            listOfRoomsIds[chatRoomIdCount] = [chatroomName]
                            listOfRooms[chatroomName].chatRoomIdCount += 1
                        else:
                            listOfRooms[chatroomName].listOfClients[socketKey] = ([client, clientName, listOfRooms[chatroomName].numberOfJoinIdCount])
                            listOfRooms[chatroomName].numberOfClients += 1
                        listOfRooms[chatroomName].numberOfJoinID += 1
                        print(clientName," has joined: ", chatroomName)
                        print(clientName, " has the JoinID: ", listOfRooms[chatroomName].numberOfJoinID)
                        clientName.send(createJoinBroadcast(chatroomName, self.host, self.port, listOfRooms[chatroomName].roomID, listOfRooms[chatroomName].joinID))
                        listOfRooms[chatroomName].joinID += 1
                        broadCastData(listOfRooms[chatroomName].listOfClients, client, createJoinBroadcast(chatroomName,self.host,self.port, listOfRooms[chatroomName].joinID))
                    
                    #CLIENT SENDS CHAT MESSAGE
                    elif(data[:4] == "CHAT"):
                        chatroomName, joinID, clientName, message = parseMessage(data)
                        broadCastData(listOfRooms[chatroomName].listOfClients,client, createChatBroadcast(chatroomName,clientName, message))
                    
                    #CLIENT SENDS KILL MESSAGE
                    elif (data == "KILL_SERVICE\n"):
                        print("Terminating sevrice")
                        closeAllRooms()
                        return
                    
                    #CLIENT SENDS HELO PROMPT
                    elif (data == "HELO text\n"):
                        response = HELO(self.host, self.port).encode()
                        client.send(response)

                    #CLIENT WANTS TO DISCONNECT
                    elif(data[:9] == "DISCONNECT"):
                        print("in disconect part")
            except:
                self.numberOfJoinID -= 1
                print(clientName + " has left the chatroom")
                broadCastData(client,clientName + " has left the chatroom.")
                del listOfClients[address[1]]
                client.close()
                return False

if __name__ == "__main__":
    try:
        while True:
            portNum = input("Enter port number: ")
            try:
                portNum = int(portNum)
                break
            except ValueError:
                pass
        ThreadedServer('',portNum).listen()

    except: 
        print("Closing Down")