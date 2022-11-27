import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        gui = tkinter.Tk()
        gui.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=gui)

        self.gui_done = False
        self.running = True

        self.peers = []

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()


    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")


        self.chat_label = tkinter.Label(self.win, text="Chat: ", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.list_user = self.frame_users(self.win)
        self.list_user.pack(side=tkinter.LEFT)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5, side=tkinter.TOP)
        self.text_area.config(state='disabled')

        self.chat_label = tkinter.Label(self.win, text="Message: ", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5,  side=tkinter.BOTTOM)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def frame_users(self, win):
        frame = tkinter.Frame(win)
        self.user = tkinter.Button(frame, text="user", command=self.write)
        self.user.config(font=("Arial", 12))
        self.user.pack(padx=20, pady=5)
        return frame

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == "NICK":
                    self.sock.send(self.nickname.encode('utf-8'))
                else: 
                    list_peer = message.split('/')[:-1]
                    for peer in list_peer:
                        [peer_addr, peer_name] = peer.split('-')
                        peer_port = int(peer_addr[1:-1].split(", ")[1])
                        self.peers.append([peer_port, peer_name])
                    
            except ConnectionAbortedError:
                break
            except:
                print('Errorrrr')
                self.sock.close()
                break

client = Client(HOST, PORT)