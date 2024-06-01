import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import socket
import threading
from queue import Queue

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI")
        self.root.geometry("300x200")

        self.label = tk.Label(root, text="GUI")
        self.label.pack(pady=50)

class MultiThreadingChats:
    def __init__(self, root, username, message_queue, Close):
        self.root = root
        self.username = username
        self.Close = Close 
        self.root.title(f"Multithreading Chat - {self.username}")
        self.root.geometry("400x300")

        self.chat_history = ScrolledText(root, state='disabled')
        self.chat_history.pack(fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(root)
        self.message_entry.pack(fill=tk.X, padx=5, pady=5)

        self.send_button = tk.Button(root, text="Send", command=self.Sending)
        self.send_button.pack(pady=5)

        self.label_username = tk.Label(root, text=f"Username: {self.username}")
        self.label_username.pack(pady=5)


        self.message_queue = message_queue

    def Sending(self):
        message = self.message_entry.get()
        if message:
            try:
                self.message_queue.put((self.username, message))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Error sending message: {e}")

    def Closing(self, event=None):  
        self.root.withdraw()  
        self.Close(self.root)  

def Close(root):
    roots.remove(root)  

def Starting(message_queue, clients):
    SocketOfServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SocketOfServer.bind(('127.0.0.1', 1000))
    SocketOfServer.listen(5)
    print("Server started")

    while True:
        SocketOfClient, _ = SocketOfServer.accept()
        print("New connected")
        clients.append(SocketOfClient)
        client_thread = threading.Thread(target=HandelingClient, args=(SocketOfClient, message_queue, clients))
        client_thread.start()

def HandelingClient(SocketOfClient, message_queue, clients):
    try:
        while True:
            message = SocketOfClient.recv(1024).decode()
            if message:
                message_queue.put(message)
                for other_client in clients:
                    if other_client != SocketOfClient:
                        try:
                            other_client.send(message.encode())
                        except Exception as e:
                            print(f"broadcasting Error : {e}")
    except Exception as e:
        print("Client disconnected")
    finally:
        SocketOfClient.close()
        clients.remove(SocketOfClient)

def Appending(root, chat_history, message):
    if isinstance(message, tuple):  
        username, content = message
        chat_history.config(state='normal')
        chat_history.insert(tk.END, f"{username}: {content}\n")
        chat_history.config(state='disabled')
        chat_history.see(tk.END)

def Updating(root, HistoryOfChats, message_queue):
    def update():
        if not message_queue.empty():
            message = message_queue.get()
            for chat_history in HistoryOfChats:
                Appending(root, chat_history, message)
        root.after(100, update)  

    update()  

def main():
    message_queue = Queue()
    clients = []
    global roots
    roots = []  
    global HistoryOfChats
    HistoryOfChats = [] 

    #Server Start threading
    server_thread = threading.Thread(target=Starting, args=(message_queue, clients))
    server_thread.daemon = True
    server_thread.start()

    for i in range(3):
        root = tk.Tk()
        roots.append(root)
        app = MultiThreadingChats(root, f"User {i+1}", message_queue, Close)
        app.root.protocol("Delete Window", app.Closing)  #handeling when user close a window
        HistoryOfChats.append(app.chat_history)

    # Start Updating GUI
    gui_thread = threading.Thread(target=Updating, args=(roots[0], HistoryOfChats, message_queue))
    gui_thread.daemon = True
    gui_thread.start()

    for root in roots:
        root.mainloop()

if __name__ == "__main__":
    main()
