import socket
import threading

HOST = '127.0.0.1'
POST = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, POST))

server.listen()

list_client = "('127.0.0.1', 53627)-b'2'/"

# receive
def receive():
    while True: 
        client, address = server.accept()
        print(f"Connected with {(address)} !")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)        

        print(f"Nickname of the client is {nickname}")
        
        global list_client
        list_client = list_client + f"{address}-{nickname}/" 
        print(list_client)
        client.send(list_client.encode('utf-8'))


print("Server running...")
receive()