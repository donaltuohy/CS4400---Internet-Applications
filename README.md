# Chat Server
## Details
* Author:           Donal Tuohy
* Student Number:   14313774
* Assignment 1: Socket Chat Server

## Overall Design
The chat server I have designed consists of 3 classes:
* A server class
* A chatroom class
* A client class

The server file has a global dictionary for keeping track of the chatrooms and one for keeping track of the clients which are connected to the server and which chatrooms they are currently connected to.

The server has a main thread which is listening for new connections from clients. Once a connection is accepted, the server will create a new thread which will just listen to this client. This way, everything that this client sends will be recieved regardless of what other clients are sending.

In the thread which listens to the client, there is a series of if statements which check if the incoming messages correspond to the preset messages and if so, respond accordingly.

I created several functions which parse certain messages or create specific responses which are then called if the corresponding condition is met in the listening thread.

## Broadcast Function

```python
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
```


This function was essential in creating the chatroom. It allows my server to broadcast a message to all the current clients connected in a room. The list of clients for a room and the client socket sending the message are passed into the function. The message too be sent is allso passed in. The function then steps through each client socekt and sends the message unless the socket is the sending client's.    