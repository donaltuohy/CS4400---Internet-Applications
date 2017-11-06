import socket, sys, time
import threading

ERASE_LINE = '\x1b[2K'

def joinChatMessage(chatroomName, userName):
	chatroomName = "JOIN CHATROOM: " + chatroomName + "\n"
	userName = "CLIENT_NAME: " + userName + "\n"
	return chatroomName + "CLIENT_IP: 0\n" + "PORT: 0\n" + userName

def prompt():
	sys.stdout.write('<You>')


class ThreadedClient(object):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.settimeout(600)
        self.joinedRoom = False
    
    def listenToServer(self):
        
        while True:
            try:
                response = (self.sock.recv(1024)).decode()
                if response == "":
                    print("Pipe broken, error 1: Disconnecting")
                    self.sock.close()
                    sys.exit()
                else:
                    sys.stdout.write(ERASE_LINE)
                    sys.stdout.write(response)

            except:
                sys.exit()
                

    def sendToServer(self):
        name = input("Enter your name: ")
        threading.Thread(target = self.listenToServer).start()
        print("In server function")
        print("Number of Threads: ", threading.activeCount())
        while True:
            if self.joinedRoom ==True:
                prompt()
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

    

    
