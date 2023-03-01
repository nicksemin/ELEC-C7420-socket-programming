#!/usr/bin/python

import socket
import threading
from datetime import datetime

s = socket.socket()
host = socket.gethostname()
port = 1221

clients = []
usernames = []

messages_to_send = dict()
last_seen = dict()
receivers = dict()
groups = dict()
group_owners = dict()

def belongs_to_group(username):
    try:
        for group in groups.values():
            print(group)
            for member in group:
                print(member)
                if member == username:
                    groupname = list(groups.keys())[list(groups.values()).index(group)]
                    return (True, group, groupname)
        return (False, ['empty'], 'empty')
    except:
        return (False, ['empty'], 'empty')



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
        messages_to_send[username] = []
        for message in offline_messages:
            client.send(new_line_and_encode(message))
    except:
        pass


# wrapper for sending in chat
def send_wrapper(message, username, sender):
    try:
        client = receivers[username]
        client.send(new_line_and_encode(message))
    except Exception as e:
        print(e)
        if not username in last_seen:
            sender.send(f"{username} is currently offline\n".encode())
        else:
            sender.send(f"{username} is offline, last seen {last_seen[username]}\n".encode())
        # save messages to send them later
        if not username in messages_to_send:
            messages_to_send[username] = []
        messages_to_send[username].append(message)


def broadcast(message, sender):
    sender_username = get_username(sender)
    message = sender_username + ': ' + message

    for client in clients:
        if client != sender:
            client.send(new_line_and_encode(message))


def server_broadcast(message):
    for client in clients:
        client.send(message)


def send_in_chat(message, usernames, sender, groupname):
    sender_username = get_username(sender)
    message = 'From {} in {}: {}'.format(sender_username, groupname, message)

    print(usernames)
    for username in usernames:
        if sender_username != username:
            send_wrapper(message, username, sender)
    if sender_username != group_owners[groupname]:
        send_wrapper(message, group_owners[groupname],sender)


def send_to(message, receiver, sender):
    try:
        sender_username = get_username(sender)
        message = f"{sender_username}: {message} ({datetime.now()})"

        client = receivers[receiver]
        client.send(new_line_and_encode(message))
    except:
        if not receiver in last_seen:
            sender.send(f"{receiver} is currently offline\n".encode())
        else:
            sender.send(f"{receiver} is offline, last seen {last_seen[receiver]}\n".encode())
        # save messages to send them later
        if not receiver in messages_to_send:
            messages_to_send[receiver] = []
        messages_to_send[receiver].append(message)


def handle(client):
    while True:
        try:
            received_message = client.recv(1024).decode()

            if 'REMOVE:' in received_message:
                service_message = True
                command, groupname = received_message.split(':')
                del groups[groupname]
            else:
                service_message = False

            if not service_message:
                message, chatters, groupname = received_message.split(':')
                print(groups)
                client_username = get_username(client)

                does_belong, group_members, group_to_belong = belongs_to_group(client_username)

                if chatters == '' and not does_belong:
                    broadcast(message, client)
                elif groupname == '' and not does_belong:
                    send_to(message, chatters, client)
                elif does_belong:
                    send_in_chat(message, group_members, client, group_to_belong)
                else:
                    chatters_usernames = chatters.split(', ')
                    groups[groupname] = chatters_usernames
                    group_owners[groupname] = get_username(client)
                    send_in_chat(message, chatters_usernames, client, groupname)
        except Exception as ex:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            last_seen[username] = datetime.now()
            server_broadcast('{} left!\n'.format(username).encode())
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
        server_broadcast("{} joined!\n".format(username).encode())
        client.send('Connected to server!\n'.encode())

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


s.bind((host, port))
s.listen()

receive()
