#!/usr/bin/python

import socket
import threading

class Client:
    def __init__(self, username, chat_with, groupname):
        self.username = username
        self.chat_with = chat_with
        self.groupname = groupname

username = input("Input your username: ")
chat_with = input("Message with (blank for broadcast): ")
if ', ' in chat_with:
    groupname = input('Name for your group: ')
else:
    groupname = ''

client_instance = Client(username, chat_with, groupname)

client = socket.socket()
host = socket.gethostname()
port = 1221

client.connect((host, port))


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'USRNAME':
                client.send(client_instance.username.encode())
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break


def write():
    while True:
        # currently, the sender is set when connection between a server and a client is open, but can be entered manually
        client_input = input('')
        if client_input == 'e' and ', ' in client_instance.chat_with:
            remove_message = 'REMOVE:{}'.format(client_instance.groupname)
            client.send(remove_message.encode())
            client_instance.groupname = input('New groupname: ')
            client_instance.chat_with = input('New group members: ')
            client_input = input('Your message: ')

        message = '{}:{}:{}'.format(client_input, client_instance.chat_with, client_instance.groupname)
        client.send(message.encode())


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
