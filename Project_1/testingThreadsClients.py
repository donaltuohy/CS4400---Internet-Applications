import socket, sys, time
import threading


def joinChatMessage(chatroomName, userName):
	chatroomName = "JOIN CHATROOM: " + chatroomName + "\n"
	userName = "CLIENT_NAME: " + userName + "\n"
	return chatroomName + "CLIENT_IP: 0\n" + "PORT: 0\n" + userName


class ThreadedClient(object):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.settimeout(600)
        self.joinedRoom = False
        self.finished = False
    
    def listenToServer(self):
        
        while True:
            try:
                response = (self.sock.recv(1024)).decode()
                if response == "":
                    print("Pipe broken, error 1: Disconnecting")
                    self.sock.close()
                    self.finished = True
                    print("Setting finished true!!!!!!!!!!!")
                    break
                else:
                    sys.stdout.write(response)
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

            else:
                print(chr(27) + "[2J") #Clear the console
                message = joinChatMessage("Chatroom", name)
                self.joinedRoom = True
            
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