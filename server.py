import socket
import threading

HOST = '127.0.0.1'
POST = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, POST))

server.listen()

clients = []
nicknames = []

# handle
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} : {message}")
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break

# receive
def receive():
    while True: 
        client, address = server.accept()
        print(f"Connected with {str(address)} !")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)
        print("Nickname is:", nickname)
        client.send("9092".encode('utf-8'))

        clients.append(client)
        nicknames.append(nickname)

        print(f"Nickname of the client is {nickname}")

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server running...")
receive()