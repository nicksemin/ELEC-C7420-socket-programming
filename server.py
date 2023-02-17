#!/usr/bin/python

import socket
import threading

s = socket.socket()
host = socket.gethostname()
port = 1221

clients = []
usernames = []

receivers = dict()

def broadcat(message):
    for client in clients:
        client.send(message)


def send_to(message, receiver):
        print(message)
        client = receivers[receiver]
        print(client)
        client.send(message.encode())


def handle(client):
    while True:
        try:
            received_message = client.recv(1024).decode()
            print(received_message)
            receiver, message = received_message.split(':')
            send_to(message, receiver)
        except Exception as ex:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcat('{} left!'.format(username).encode())
            usernames.remove(username)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            break


def receive():
    while True:
        client, address = s.accept()
        print("Connected with {}".format(str(address)))

        client.send('USRNAME'.encode('ascii'))
        username = client.recv(1024).decode()
        usernames.append(username)
        clients.append(client)
        receivers[username] = client

        print("Username is {}".format(username))
        broadcat("{} joined!".format(username).encode())
        client.send('Connected to server!'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


s.bind((host, port))
s.listen()

receive()
