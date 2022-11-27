import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HOST = '127.0.0.1'
PORT_SERVER = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        msg = tkinter.Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        self.peer = -1
        self.in_chat = False

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        chat_receive_thread = threading.Thread(target=self.receive_chat)

        gui_thread.start()
        receive_thread.start()
        chat_receive_thread.start()

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
        self.chat_sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()

        self.chat_sock.close();
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == "NICK":
                    self.sock.send(self.nickname.encode('utf-8'))
                else: 
                    self.peer = int(message)
                    self.chat_sock.connect((HOST, self.peer))
                    self.in_chat = True
            except ConnectionAbortedError:
                break
            except:
                print('Error receive')
                self.sock.close()
                break
    
    def write_text_area(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert('end', message)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def receive_chat(self):
        while self.running:
            if self.in_chat:
                try:
                    message_chat = self.chat_sock.recv(1024).decode('utf-8')
                    print(message_chat)
                    if self.gui_done:
                        self.write_text_area(message_chat)
                except ConnectionAbortedError:
                    break
                except:
                    print('Error receive_chat')
                    self.chat_sock.close()
                    break


client = Client(HOST, PORT_SERVER)