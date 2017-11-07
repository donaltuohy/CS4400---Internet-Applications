import socket
import threading

listOfClients = {}

def closeAllPorts():
    for key in listOfClients:
        socket = (listOfClients[key])[0]
        socket.close()
    print("All ports closed. Goodbye.")

def parseName(joinMessage):
    Username = joinMessage.split()[8]
    return Username

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
    
    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            socketKey = address[1]
            if client:
                listOfClients[socketKey] = [client,""]
            client.settimeout(50)
            client.send(("Welcome to the chat room.\n\n").encode())
            threading.Thread(target = self.listenToClient, args = (client, address, socketKey)).start()

    def listenToClient(self, client, address, socketKey):
        while True:
            try:
                data = (client.recv(1024)).decode()
                if data:
                    if(data[:13] == "JOIN CHATROOM"):
                        listOfClients[socketKey] = [client,parseName(data)]
                        clientName = (listOfClients[socketKey])[1]                      
                        print(clientName," has joined the chat room.")
                        broadCastData(client,clientName + " has joined the chatroom.")
                    elif data == "KILL_SERVICE\n":
                        print("Terminating sevrice")
                        closeAllPorts()
                        return
                    else:
                        response = data.encode()
                        broadCastData(client, data)
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
    