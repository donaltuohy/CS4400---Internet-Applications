import socket, sys, time
import threading


class ThreadedClient(object):

    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.settimeout(600)
    
    def listenToServer(self):
        
        while True:
            try:
                response = (self.sock.recv(1024)).decode()
                if response == "":
                    print("Pipe broken, error 1: Disconnecting")
                    self.sock.close()
                    break
                else:
                    print("Received:", response)
            
            except:
                print("Pipe broken error 2: Disconnecting")
                time.sleep(5)
                break
                

    def sendToServer(self):
        threading.Thread(target = self.listenToServer).start()
        print("In server function")
        print("Number of Threads: ", threading.activeCount())
        while True:
            message = input("<You> ")
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

    

    
