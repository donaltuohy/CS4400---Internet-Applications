import socket, sys, time
import threading


def joinChatMessage(chatroomName, userName):
	chatroomName = "JOIN CHATROOM: " + chatroomName + "\n"
	userName = "CLIENT_NAME: " + userName + "\n"
	return chatroomName + "CLIENT_IP: 0\n" + "PORT: 0\n" + userName

def parseJoinMessage(message):
    splitMessage = message.split()
    chatroomName = splitMessage[1]
    host = splitMessage[3]
    port = int(splitMessage[5])
    roomID = int(splitMessage[7])
    joinID = int(splitMessage[9])
    return chatroomName, host, port, roomID, joinID

def parseChatMessage(message):
    splitMessage = message.split()
    chatroomName = splitMessage[1]
    senderName = splitMessage[3]
    chatMessage = splitMessage[5:]
    return chatroomName, senderName, chatMessage 

def createLeaveMessage(roomID, joinID,clientName):
    return "LEAVE_CHATROOM: " + roomID + "\nJOIN_ID: " + joinID + "\nCLIENT_NAME: " + clientName 

def createChatMessage(roomID, joinID, clientName, chatMessage):
    return "CHAT: " + str(roomID) + "\nJOIN_ID: " + str(joinID) + "\nCLIENT_NAME: " + clientName + "\nMESSAGE: " + chatMessage

class ThreadedClient(object):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.settimeout(600)
        self.joinedRoom = False
        self.finished = False
        self.roomID = 0
        self.joinID = 0
    
    def listenToServer(self):
        
        while True:
            try:
                response = (self.sock.recv(1024)).decode()
                print(response)
                #SOCKET BROKEN OR CHATROOM CLOSED
                if response == "" or response == "-9999":
                    self.sock.close()
                    self.finished = True
                    print("Chatroom has closed, goodbye.")
                    print("Press enter to exit.")
                    break

                #RESPONSE AFTER JOINING THE CHATROOM
                elif (response[:15] == "JOINED_CHATROOM"):
                    print("joined message recieved")
                    chatroomName, host, port, roomId, joinId = parseJoinMessage(response)
                    self.roomID = roomId
                    self.joinID = joinId
                    self.joinedRoom = True
                    print("Joined the chatroom: ", chatroomName, " through port ", port, ".")
                
                #CHAT MESSAGE RECIEVED
                elif (respone[:3] == "CHAT"):
                    print("chat message recieved")
                    chatroomName, senderName, chatMessage = parseChatMessage(response)
                    print("[",senderName,"] ", chatMessage)

                #ERROR_CODE RECIEVED
                elif (response[:9] == "ERROR_CODE"):
                    print("Error recieved")

                #LEFT RESPONSE FROM CHATROOM
                elif (response[:12] == "LEFT_CHATROOM"):
                    print("Succesfully left chatroom")
                    self.joinedRoom = False
                else:
                    print("response: ", response )
            except:
                sys.exit()
                

    def sendToServer(self):
        name = input("Enter you name:")
        threading.Thread(target = self.listenToServer).start()
        while True:
            if self.finished:
                return
            if self.joinedRoom:
                message = sys.stdin.readline()
                if message == "LEAVE":
                    message = createLeaveMessage(self.roomID, self.joinID, name)
                else:
                    message = createChatMessage(self.roomID, self.joinID, name, message)
            else:
                chatroomName = input("Enter chat room name: ")
                message = joinChatMessage(chatroomName, name)
                self.joinedRoom = True

            if self.finished:
                return
            
            try:
                self.sock.send(message.encode())
            except:
                print("Unable to send message.")


if __name__ == "__main__":
    
    if(len(sys.argv) < 3):
        print("Usage: python telnet.py hostname port")
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    ThreadedClient(host,port).sendToServer()