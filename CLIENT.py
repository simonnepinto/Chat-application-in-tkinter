#import the required modules
from tkinter import Tk, Frame, Scrollbar, Label, END, Entry, Text, VERTICAL, Button, messagebox #Tkinter Python Module for GUI
import socket #Sockets for network connection
import threading # for multiple proccess
import sys
import time

#For GUI 
class GUI:
    client_socket = None
    last_received_message = None

    def __init__(self, master): #called when an object is created from the GUI class
        #we initialise the attributes to default values
        self.root = master
        self.chat_transcript_area = None
        self.name_widget = None
        self.enter_text_widget = None
        self.join_button = None
        self.initialize_socket()
        self.initialize_gui()
        self.listen_for_incoming_messages_in_a_thread()

    #function to initialise socket and connect to the server
    def initialize_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initializing socket with TCP and IPv4
            remote_ip = '127.0.0.1' # IP address
            remote_port = 10319 #TCP port
            self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server
        except:
            print("Couldn't connect to remote server");

    # GUI initializer
    def initialize_gui(self): 
        self.root.title("CHATROOM")
        self.root.resizable(0, 0)
        self.display_chat_box()
        self.display_name_section()
        self.display_chat_entry_box()
        self.root.configure(bg="coral1") #provide background color

    #function to listen messages in a thread
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time
        thread.start()
        
    #function to receive messages from the server
    def receive_message_from_server(self, so):
        while True:
            try:
                buffer = so.recv(256) #get a buffer 
                if not buffer:
                    break
                message = buffer.decode('utf-8')

                if "joined" in message: #Display appropriate messages to the users
                    user = message.split(":")[1]
                    message = user + " has joined the chat"
                    self.chat_transcript_area.insert('end', message + '\n')
                    self.chat_transcript_area.yview(END)
                else:
                    self.chat_transcript_area.insert('end', message + '\n')
                    self.chat_transcript_area.yview(END)

            except: #Error handling for "Connection aborted error" on abruptly closing the chat window
                print("A client left the chat");
                break;

        so.close() #close the socket

    #GUI component to ask for client name
    def display_name_section(self):
        frame = Frame() #frame to hold the corresponding elements
        self.label = Label(frame, text='Enter your name:', font=("Helvetica", 16))
        self.label.pack(side='left', padx=10)
        self.name_widget = Entry(frame, width=50, borderwidth=2)
        self.name_widget.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Join", width=10, command=self.on_join) #call on_join method
        self.join_button.pack(side='left')
        frame.pack(side='top', anchor='nw')

    #GUI component to display chatbox to accept user input
    def display_chat_box(self):
        frame = Frame()#frame to hold the corresponding elements
        Label(frame, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=6, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')
        frame.configure(bg="sandy brown") #provide background color

    #GUI component to take in the user input and display to other clients
    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=10)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed) #call on_enter_key_pressed
        frame.pack(side='top')
        frame.configure(bg="bisque2")

    #After the client joins the chat by entering their name
    def on_join(self):
        try:
            if len(self.name_widget.get()) != 0:
                self.name_widget.config(state='disabled')
                self.client_socket.send(("joined:" + self.name_widget.get()).encode('utf-8'))
                self.B = Button(root, text ="Play A Game", command = self.playGame)
                self.B.pack()
                self.name_widget.pack_forget()
                self.join_button.pack_forget()
                self.label.pack_forget()
            else:
                raise
        except:
            messagebox.showerror(
                "Enter your name", "Enter your name to send a message")
            return

    #When user presses the enter button to send messages
    def on_enter_key_pressed(self, event):
        try:
            if len(self.name_widget.get()) != 0:

                self.send_chat()
                self.clear_text()
            else:
                raise
        except:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return


    #clear the text after user has entered messages in the chatbox and sent it
    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    #send the messages to the server 
    def send_chat(self):
        senders_name = self.name_widget.get().strip() + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    #Function to play a game 
    def playGame(self):
        frame = Frame()
        self.label = Label(frame, text='Enter something to encode:', font=("Helvetica", 16))
        self.label.pack(side='left', padx=10)
        self.name = Entry(frame, width=33, borderwidth=2)
        self.name.pack(side='left', anchor='e')
        self.join_button = Button(frame, text="Enter", width=10, command=self.encrypt) #call encrypt method
        self.join_button.pack(side='left')
        frame.pack(side='top', anchor='nw')
        

    #Function to encrypt the message and send to the other clients
    def encrypt(self):
        if len(self.name.get()) == 0:
            messagebox.showerror("Enter your name", "Enter your name to send a message")
            return

        # conversion Chart 
        conversion_code = { 
            
            # Uppercase Alphabets 
            'A': 'Z', 'B': 'Y', 'C': 'X', 'D': 'W', 'E': 'V', 'F': 'U', 
            'G': 'T', 'H': 'S', 'I': 'R', 'J': 'Q', 'K': 'P', 'L': 'O', 
            'M': 'N', 'N': 'M', 'O': 'L', 'P': 'K', 'Q': 'J', 'R': 'I', 
            'S': 'H', 'T': 'G', 'U': 'F', 'V': 'E', 'W': 'D', 'X': 'C', 
            'Y': 'B', 'Z': 'A', 
          
            # Lowercase Alphabets 
            'a': 'z', 'b': 'y', 'c': 'x', 'd': 'w', 'e': 'v', 'f': 'u', 
            'g': 't', 'h': 's', 'i': 'r', 'j': 'q', 'k': 'p', 'l': 'o', 
            'm': 'n', 'n': 'm', 'o': 'l', 'p': 'k', 'q': 'j', 'r': 'i', 
            's': 'h', 't': 'g', 'u': 'F', 'v': 'e', 'w': 'd', 'x': 'c', 
            'y': 'b', 'z': 'a'
        } 
          
        # Creating converted output 
        converted_data = "" 
        data = self.name.get()
          
        for i in range(0, len(data)): 
            if data[i] in conversion_code.keys(): 
                converted_data += conversion_code[data[i]] 
            else: 
                converted_data += data[i]
                
        senders_name = "Can you decrypt this: "
        message = (senders_name + converted_data).encode('utf-8')
        self.client_socket.send(message) #send the encrypted text to the server 
        self.enter_text_widget.delete(1.0, 'end')
        
        self.clear_text()
   
   #On closing the window 
    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.client_socket.send((self.name_widget.get()+ " has left the chat").encode('utf-8')) #display messages to other clients
                root.destroy()
                self.client_socket.close()
                time.sleep(5)
                sys.exit(0)


#the mail function
if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
