import socket
import threading

listOfClients = {}

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
            if client:
                print("Client joined: ", address)
                listOfClients[address[1]] = [client,""]
            client.settimeout(50)
            client.send(("Hello, This was sent from server").encode())
            threading.Thread(target = self.listenToClient, args = (client, address)).start()

    def listenToClient(self, client, address):
        while True:
            try:
                data = (client.recv(1024)).decode()
                if data:
                    print(data)
                    print(listOfClients)
                    response = data.encode()
                    client.send(response)
            except:
                print("Client disconnected")
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
    