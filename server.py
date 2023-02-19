#!/usr/bin/python

import socket
import threading

s = socket.socket()
host = socket.gethostname()
port = 1221

clients = []
usernames = []

messages_to_send = dict()
receivers = dict()

def get_username(client):
    index = clients.index(client)
    username = usernames[index]
    return username

def new_line_and_encode(message):
    message = message + '\n'
    return message.encode()


def send_offline_messages(username, client):
    try:
        offline_messages = messages_to_send[username]
        for message in offline_messages:
            client.send(new_line_and_encode(message))
    except:
        pass


def broadcast(message):
    for client in clients:
        client.send(message)


def send_to(message, receiver, sender):
    try:
        sender_username = get_username(sender)
        message = sender_username + ': ' + message

        client = receivers[receiver]
        client.send(new_line_and_encode(message))
    except:
        sender.send(f"{receiver} is currently offline\n".encode())
        # save meesages to send them later
        if not receiver in messages_to_send:
            messages_to_send[receiver] = []
        messages_to_send[receiver].append(message)


def handle(client):
    while True:
        try:
            received_message = client.recv(1024).decode()
            receiver, message = received_message.split(':')
            if receiver != '':
                send_to(message, receiver, client)
            else:
                broadcast(new_line_and_encode(message))
        except Exception as ex:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast('{} left!\n'.format(username).encode())
            usernames.remove(username)
            print(ex)
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

        # send messaged that were received while offline
        send_offline_messages(username, client)

        print("Username is {}\n".format(username))
        broadcast("{} joined!\n".format(username).encode())
        client.send('Connected to server!\n'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


s.bind((host, port))
s.listen()

receive()
