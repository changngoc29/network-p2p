import socket
import threading

HOST = '127.0.0.1'
POST = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, POST))

server.listen()

clients = []
chat_ports = []
nicknames = []

# global list_client
# list_client = list_client + f"{address}-{nickname}/" 
# print(list_client)
# client.send(list_client.encode('utf-8'))

def sendListFriend():
    for client in clients:
        client_index = clients.index(client)
        try:
            list_friend = ""
            for i in range(len(clients)):
                if i != client_index:
                    list_friend += f"{chat_ports[i]}-{nicknames[i]}/"
            print(list_friend)
            client.send(list_friend.encode('utf-8'))
        except:
            print("Error client")
            clients.remove(clients[client_index])
            client.close()
            nicknames.remove(nicknames[client_index])
            chat_ports.remove(chat_ports[client_index])

# receive
def receive():
    while True: 
        client, address = server.accept()
        print(client)
        print(f"Connected with {(address)} !")

        client.send("NICK".encode('utf-8'))
        info = client.recv(1024).decode('utf-8')

        [nickname, chat_port] = info.split('-')

        print(f"{nickname} - {chat_port}")

        clients.append(client)
        chat_ports.append(chat_port)
        nicknames.append(nickname)

        sendListFriend()

print("Server running...")
receive()