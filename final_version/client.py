import socket
import os
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import filedialog

HOST = '127.0.0.1'
PORT = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_server.bind((host, 0))
        self.chat_server.listen(4)
        
        self.chat_server_port = self.chat_server.getsockname()[1]

        print(self.chat_server_port)

        gui = tkinter.Tk()
        gui.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=gui)

        self.gui_done = False
        self.running = True

        self.peers = []

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        chat_manage_thread = threading.Thread(target=self.chat_manage)

        gui_thread.start()
        receive_thread.start()
        chat_manage_thread.start()
    

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")


        self.chat_label = tkinter.Label(self.win, text="List Friend", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.list_user = tkinter.Frame(self.win)
        self.list_user.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def change_frame_users(self):
        for widget in self.list_user.winfo_children():
            print(widget)
            widget.destroy()
        while len(self.list_user.winfo_children()) != 0: {}
        for peer in self.peers:
            tkinter.Button(self.list_user, width=30, height=2, text=peer[1], command= lambda: self.chat(peer[0])).pack()
        return True

    def chat(self, port):
        sock_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_chat.connect((HOST, port))
        print('connect successfully')
        new_win = Chat(sock_chat, self.win, self.nickname)
        return True

    def chat_manage(self):
        while True:
            peer, address = self.chat_server.accept()
            print(f"Connected with {str(address)} !")

            new_win = Chat(peer, self.win, self.nickname)

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                self.peers = []
                message = self.sock.recv(1024).decode('utf-8')
                if message == "NICK":
                    info = self.nickname + '-' + str(self.chat_server_port)
                    self.sock.send(info.encode('utf-8'))
                else: 
                    list_peer = message.split('/')[:-1]
                    for peer in list_peer:
                        [peer_port, peer_name] = peer.split('-')
                        peer_port = int(peer_port)
                        self.peers.append([peer_port, peer_name])
                    while self.gui_done == False: {}
                    self.change_frame_users()
                    
            except ConnectionAbortedError:
                break
            except:
                print('Errorrrr')
                self.sock.close()
                break

class Chat:
    def __init__(self, peer, win, name1):
        self.peer = peer
        self.win = win
        self.name1 = name1

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()
    
    def gui_loop(self):
        self.top= tkinter.Toplevel(self.win)
        self.top.geometry("750x600")
        self.top.title("Child Window")
        self.top.configure(bg="lightgray")

        self.top_label = tkinter.Label(self.top, text="Chat", bg="lightgray")
        self.top_label.config(font=("Arial", 12))
        self.top_label.pack(padx=20, pady=5)

        self.top_text_area = tkinter.scrolledtext.ScrolledText(self.top)
        self.top_text_area.pack(padx=20, pady=5)
        self.top_text_area.config(state="disabled")

        self.top_chat_label = tkinter.Label(self.top, text="Message: ", bg="lightgray")
        self.top_chat_label.config(font=("Arial", 12))
        self.top_chat_label.pack(padx=20, pady=5)

        self.top_input_area = tkinter.Text(self.top, height=3)
        self.top_input_area.pack(padx=20, pady=5)

        self.top_send_button = tkinter.Button(self.top, text="Send", command=self.write)
        self.top_send_button.config(font=("Arial", 12))
        self.top_send_button.pack(padx=20, pady=5)

        self.top_select_file_btn = tkinter.Button(self.top, text="Choose file", command=self.select_file)

        self.gui_done = True

        self.top.protocol("WM_DELETE_WINDOW", self.stop)

    def select_file(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=(('file_text','*.txt'),('all files', '*.*')))

    def write_text_area(self, message):
        self.top_text_area.config(state='normal')
        self.top_text_area.insert('end', message)
        self.top_text_area.yview('end')
        self.top_text_area.config(state='disabled')

    def write(self):
        message = f"{self.name1}: {self.top_input_area.get('1.0', 'end')}"
        self.write_text_area(message)
        self.peer.send(message.encode('utf-8'))
        self.top_input_area.delete('1.0', 'end')
    
    def stop(self):
        self.running = False
        self.top.destroy()
        self.peer.close()
    
    def receive(self):
        while self.running:
            try:
                print('before receive')
                message_chat = self.peer.recv(1024).decode('utf-8')
                print(message_chat)
                print('after receive')
                if self.gui_done:
                    self.write_text_area(message_chat)
            except ConnectionAbortedError:
                break
            except:
                print('Error receive_chat')
                self.peer.close()
                break

client = Client(HOST, PORT)