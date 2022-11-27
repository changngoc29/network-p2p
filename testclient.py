import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT = 9092

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(4)

        self.peer = None
        self.peerAddr = None

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)

        gui_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat: ", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.chat_label = tkinter.Label(self.win, text="Message: ", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.write_text_area(message)
        if self.peer.send(message.encode('utf-8')):
            print('send success')
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        if self.peer:
            self.peer.close()
        exit(0)

    def peer_server(self):
        while True:
            self.peer, self.peerAddr = self.sock.accept()
            if self.peer:
                print(self.peerAddr)
                self.write_text_area(f"Connect with: {self.peerAddr}\n")
            self.peer_threading = threading.Thread(target=self.receive)
            self.peer_threading.start()

    def write_text_area(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert('end', message)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def receive(self):   
        while self.running:
            try:
                message = self.peer.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.write_text_area(message)
            except ConnectionAbortedError:
                break
            except:
                print('Error')
                self.sock.close()
                break

client = Client(HOST, PORT)
client.peer_server()