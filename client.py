#!/usr/bin/python

import socket
import threading

username = input("Input your username: ")
chat_with = input("Message with (blank for broadcast): ")

client = socket.socket()
host = socket.gethostname()
port = 1221

client.connect((host, port))


def receive():
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'USRNAME':
                client.send(username.encode())
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break


def write():
    while True:
        # currently, the sender is set when connection between a server and a client is open, but can be entered manually
        message = '{}:{}'.format(chat_with, input(''))
        client.send(message.encode())


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
