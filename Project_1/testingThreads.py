import socket
import threading

listOfClients = {}

def closeAllPorts():
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        socket.send(("-9999").encode())
    print("All ports closed. Goodbye.")

def parseName(joinMessage):
    Username = joinMessage.split()[8]
    return Username

def HELO(host, port):
    return "HELO text\nIP: " + str(host) + "\nPort: " + str(port) + "\nStudentID: 14313774\n" 

#Function which broadcast a message to all connected clients bar the server and the one that sent the message
def broadCastData(sock, message):
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


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.finished = False
    
    def listen(self):
        self.sock.listen(5)
        while True:
            if self.finished:
                return
            client, address = self.sock.accept()
            socketKey = address[1]
            if client:
                listOfClients[socketKey] = [client,""]
            client.settimeout(50)
            threading.Thread(target = self.listenToClient, args = (client, address, socketKey)).start()

    def listenToClient(self, client, address, socketKey):
        while True:
            if self.finished == True:
                return
            try:
                data = (client.recv(1024)).decode()
                if data:
                    if(data[:13] == "JOIN CHATROOM"):
                        listOfClients[socketKey] = [client,parseName(data)]
                        clientName = (listOfClients[socketKey])[1]                      
                        print(clientName," has joined the chat room.")
                        broadCastData(client,clientName + " has joined the chatroom.\n")
                    elif data == "KILL_SERVICE\n":
                        print("Terminating sevrice")
                        closeAllPorts()
                        return
                    elif data == "HELO text\n":
                        response = HELO(self.host, self.port).encode()
                        client.send(response)
                    else:
                        response = data.encode()
                        broadCastData(client, "[" + clientName + "]:" + data)
            except:
                print(clientName + " has left the chatroom")
                broadCastData(client,clientName + " has left the chatroom.")
                del listOfClients[address[1]]
                client.close()
                return False

if __name__ == "__main__":
    while True:
        portNum = input("Enter port number: ")
        try:
            portNum = int(portNum)
            break
        except ValueError:
            pass
    ThreadedServer('',portNum).listen()
    