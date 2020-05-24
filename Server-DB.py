import socket
import sqlite3
import select
import random
import time
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError
from Encryption import *


class Client(object):
    def __init__(self, username, socket, key):
        self._username = username
        self._socket = socket
        self._key = key
        self._big_data = b""

    def get_username(self):
        return self._username

    def set_username(self, username):
        self._username = username

    def is_username(self, username):
        return self._username == username

    def get_socket(self):
        return self._socket

    def get_key(self):
        return self._key

    def get_big_data(self):
        return self._big_data

    def set_big_data(self, big_data):
        self._big_data = big_data


class ListClients(object):
    def __init__(self):
        self._clients = []

    def add_client(self, username, socket, key):
        self._clients.append(Client(username, socket, key))

    def get_sockets(self):
        sockets = []
        for client in self._clients:
            sockets.append(client.get_socket())
        return sockets

    def get_usernames(self):
        usernames = []
        for client in self._clients:
            usernames.append(client.get_username())
        return usernames

    def get_socket(self, username):
        for client in self._clients:
            if client.get_username() == username:
                return client.get_socket()
        raise Exception("username not found in client list")
        # return None

    def get_username(self, socket):
        for client in self._clients:
            if client.get_socket() == socket:
                return client.get_username()
        raise Exception("socket not found in client list")

    def get_client_by_username(self, username):
        for client in self._clients:
            if client.get_username() == username:
                return client
        raise Exception("username not found in client list to return client")

    def _get_client_by_socket(self, socket):
        return self.get_client_by_username(self.get_username(socket))

    def set_username(self, socket, username):
        self._get_client_by_socket(socket).set_username(username)

    def remove_client(self, username):
        for client in self._clients:
            if client.get_username() == username:
                self._clients.remove(client)
                client.get_socket().close()
                # client = None
                return
        raise Exception('There was no client with the username: ', username)

    def get_key_by_socket(self, socket):
        for client in self._clients:
            if client.get_socket() == socket:
                return client.get_key()
        raise Exception("socket not found in client list")

    def get_big_data_by_socket(self, socket):
        for client in self._clients:
            if client.get_socket() == socket:
                return client.get_big_data()
        raise Exception("socket not found in client list")

    def set_big_data_by_socket(self, socket, data):
        if socket in self.get_sockets():
            a = self._get_client_by_socket(socket)
            if a:
                a.set_big_data(data)
            else:
                pass
        else:
            raise Exception("socket not found in client list")


class Server(object):
    def __init__(self):
        self.ip = None
        self.port = None
        self.configuration_path = 'configuration.txt'
        self._read_configuration_file()
        self.server_socket = socket.socket()
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(20)
        self.wlist = None
        self.rlist = None
        self.xlist = None
        self.db = Database(sqlite3.connect("users_01.db"))
        print("opened database successfully")
        self.database_reset_temp()  # resets DB
        self.messages = []
        self.last_id = 1
        self.last_file_id = 1

        self.clients = ListClients()

    def database_reset_temp(self):
        try:
            self.db["files"].drop()
        except:
            print("there is no table FILES")
        try:
            self.db["chats"].drop()
        except:
            print("there is no table CHATS")
        try:
            self.db["users"].drop()
        except:
            print("there is no table USERS")

        self.db['users'].create({
            "id": int,
            "email": str,
            "username": str,
            "hashed_password": str,
        }, pk="id")
        print("table created successfully")
        users = self.db["users"]
        users.insert({"username": "segev10",
                      "id": 1,
                      "email": "segevshalom86@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "a",
                      "id": 2,
                      "email": "a@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "b",
                      "id": 3,
                      "email": "b6@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        self.db["chats"].create({
            "id": int,
            "name": str,
            "msgs": str,
            "contacts": str,
            "user_id": int,
            "external_id": int,
            "new_msgs": int,
            "managers_id": str,
            "is_linked": bool,
            "linker_id": int,
            "files_ids": str,
            "is_private": bool},
            pk="id"
        )
        self.db["files"].create({
            "id": int,
            "name": str,
            "value": bytes,
            "username_of_sender": str
        })

    def _read_configuration_file(self):
        f = open(self.configuration_path, "r")
        args = f.readlines()
        self.ip, self.port = args[0].split(',')
        self.ip = str(self.ip)
        self.port = int(self.port)

    # gets a data and list of sockets to send it to them and builds a message and appends it to self.messages
    # (the messages that need to be sent)
    def msg_maker(self, data, list_of_sockets_to_send):
        msg = data, list_of_sockets_to_send
        self.messages.append(msg)

    # gets chat external_id and returns a list of all the users names that take a part of it
    def get_list_of_contacts(self, external_id):
        i = 1
        contacts = None
        while True:
            try:
                chat = self.db["chats"].get(i)
                temp_external_id = chat["external_id"]
                if str(temp_external_id) == str(external_id):
                    contacts = chat["contacts"]
                    break
                i += 1
            except NotFoundError:
                break

        list_of_contacts = contacts.split(",")
        return list_of_contacts

    # this function sends a message to client about what is wrong with the params
    # if it is and return true if the process done and false if not
    def save_new_user_to_database(self, socket, email, username, hashed_password):
        cursor1 = []
        cursor2 = []
        for row in self.db["users"].rows_where("username = ?", [username]):
            cursor1.append(row)
        for row in self.db["users"].rows_where("email = ?", [email]):
            cursor2.append(row)
        _list = [socket]
        if cursor1 and cursor2:
            self.msg_maker("This email and username are\n currently in use", _list)
            return False
        elif cursor2:
            self.msg_maker("This email is currently in use", _list)
            return False
        elif cursor1:
            self.msg_maker("This username is currently in use", _list)
            return False
        self.db["users"].insert({"email": email, "username": username, "hashed_password": hashed_password}, pk='id')
        self.msg_maker("signed up successfully", _list)
        return True

    # creates a new private chat - starts a new row of chat, insert all the
    # data it needs and sends to the online clients new chat message
    def create_new_privet_chat(self, username_1, username_2):
        for i in get_column_from_db('id', self.db['chats']):
            chat = self.db['chats'].get(i)
            cont = chat["contacts"]
            is_private = chat['is_private']
            if is_private is 1:
                cont_split = cont.split(',')
                if cont_split == [username_1, username_2] or cont_split == [username_2, username_1]:
                    return

        new_chat_msg_1 = f'IChat Server: this is a private chat with {username_2}'
        new_chat_msg_2 = f'IChat Server: this is a private chat with {username_1}'
        ids = get_column_from_db("id", self.db['users'])
        _bool = False
        id_1 = None
        id_2 = None
        for _id in ids:
            user = self.db["users"].get(_id)
            if user['username'] == username_1:
                id_1 = _id
                if _bool is True:
                    break
                _bool = True
            if user['username'] == username_2:
                id_2 = _id
                if _bool is True:
                    break
                _bool = True

        if id_1 is None or id_2 is None:  # if one of them not in db
            return

        random_external_id = random.randint(1, 10000)
        while random_external_id in get_column_from_db("external_id", self.db["chats"]):
            random_external_id = random.randint(1, 10000)
        contacts = f"{username_1},{username_2}"

        self.db["chats"].insert({"id": self.last_id, "name": username_2, "msgs": new_chat_msg_2, "contacts": contacts
                                    , "user_id": id_1, "external_id": random_external_id, "new_msgs": 1,
                                 "managers_id": "", "is_linked": False, "files_ids": "", "is_private": True})
        if username_1 in self.clients.get_usernames():
            list_client = [self.clients.get_socket(username_1)]
            self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(
                random_external_id) + "+*!?" + username_2 + "+*!?" + contacts + "+*!?" + "1+*!?" + str(True),
                           list_client)
        self.last_id += 1

        self.db["chats"].insert({"id": self.last_id, "name": username_1, "msgs": new_chat_msg_1, "contacts": contacts
                                    , "user_id": id_2, "external_id": random_external_id, "new_msgs": 1,
                                 "managers_id": "", "is_linked": False, "files_ids": "", "is_private": True})
        if username_2 in self.clients.get_usernames():
            list_client = [self.clients.get_socket(username_2)]
            self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(
                random_external_id) + "+*!?" + username_1 + "+*!?" + contacts + "+*!?" + "1+*!?" + str(True),
                           list_client)
        self.last_id += 1

    # creates a new chat - starts a new row of chat, insert all the
    # data it needs and sends to the online clients new chat message
    def create_new_chat(self, chat_name, contacts):
        creator_id = None
        creator_username = contacts[-1]
        _ids = get_column_from_db("id", self.db["users"])
        for _id in _ids:
            if self.db["users"].get(_id)["username"] == creator_username:
                creator_id = str(_id)
        new_chat_msg = 'IChat Server: you were added to this chat'
        # list of right contacts only
        all_usernames = get_column_from_db("username", self.db["users"])  # list of all the usernames in the db
        usernames = shared_list(all_usernames, contacts)  # list of the usernames we need to make a chat for them
        contacts = ','.join(usernames)
        random_external_id = random.randint(1, 10000)
        while random_external_id in get_column_from_db("external_id", self.db["chats"]):
            random_external_id = random.randint(1, 10000)
        user_ids = get_column_from_db("id", self.db["users"])
        for user_id in user_ids:
            print(f"user_id={user_id}")
            username = self.db["users"].get(user_id)["username"]
            if username in usernames:
                self.db["chats"].insert({"id": self.last_id, "name": chat_name, "msgs": new_chat_msg,
                                         "contacts": contacts
                                            , "user_id": user_id, "external_id": random_external_id, "new_msgs": 1,
                                         "managers_id": creator_id, "is_linked": False, "files_ids": "",
                                         "is_private": False})
                print(f"created this chat now=>{self.db['chats'].get(self.last_id)}")
                if username in self.clients.get_usernames():
                    list_client = [self.clients.get_socket(username)]
                    self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(
                        random_external_id) + "+*!?" + chat_name + "+*!?" + contacts + "+*!?" + "1+*!?" + str(False),
                                   list_client)
                self.last_id += 1


    # save the message (msg) in the database according to username, sender_id and external_id
    def save_msg_in_db(self, username, sender_chat_id, external_id, msg):
        sender_id = str(self.db['chats'].get(int(sender_chat_id))['user_id'])
        managers_ids = self.db["chats"].get(int(sender_chat_id))["managers_id"]
        managers_ids = managers_ids.split(',')
        for chat_id in get_column_from_db("id", self.db["chats"]):
            if self.db["chats"].get(chat_id)["external_id"] == int(external_id):
                if str(chat_id) != sender_chat_id:
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\n{username}: {msg}"
                    if sender_id in managers_ids:
                        msgs = f"{previous_msgs}\n@{username}: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})
                    username_that_want_the_msg = self.db["users"].get(self.db["chats"].get(chat_id)["user_id"])[
                        "username"]
                    if username_that_want_the_msg not in self.clients.get_usernames():  # the client isn't online
                        new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                        self.db["chats"].update(chat_id, {"new_msgs": new_msgs + 1})
                else:
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\nYou: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})

    # this is the main loop of the server.
    # Here it collects all the messages and call the functions of log_in and sign_up
    # and the handle_message function that handles messages of online clients
    def run(self):
        print("server started")
        while True:
            self.rlist, self.wlist, self.xlist = select.select([self.server_socket] + self.clients.get_sockets(),
                                                               self.clients.get_sockets(), [], 0.01)
            for current_socket in self.rlist:
                if current_socket is self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    key = Fernet.generate_key()
                    self.clients.add_client('', new_socket, key)
                    new_socket.send(key.decode().encode('utf-8'))
                else:
                    data_list = []
                    data = current_socket.recv(1024)
                    if not data.decode('utf-8') == '':
                        if current_socket in self.clients.get_sockets():
                            self.clients.set_big_data_by_socket(current_socket, self.clients.get_big_data_by_socket(
                                current_socket) + data)
                            data_list = self.messages_connected(current_socket)
                            print(data_list)
                        else:
                            if current_socket == self.server_socket:
                                pass
                    if self.clients.get_username(current_socket) == '':  # this is the sign of new singing in user
                        print("no username")
                        if data_list is not [] and self.check_client_exit(data_list[0]):
                            data = data_list.pop(0)
                            temp_d = data.split(b'+*!?')
                            if len(temp_d) == 3:
                                self.signup_process(data, current_socket)
                            if len(temp_d) == 2:
                                self.login_process(data, current_socket)
                        elif data_list:
                            for data in data_list:
                                self.handle_message(data, current_socket)
                    else:
                        for data in data_list:
                            self.handle_message(data, current_socket)
            self.send_waiting_messages()


    def big_message_spliter(self, message, buffer):
        msg_len = len(message)
        num_of_indexes = int(msg_len/buffer)
        if msg_len % buffer != 0:
            num_of_indexes += 1
        _list = []
        start = 0
        for l in range(0, num_of_indexes):
            if l is num_of_indexes-1:
                _list.append(message[start:])
            else:
                _list.append(message[start:start+buffer])
            start += buffer
        return _list

    # this function sends all the messages from self.messages to the clients
    def send_waiting_messages(self):
        for message in self.messages:
            (data, current_sockets) = message
            for i, client_socket in enumerate(self.clients.get_sockets()):
                if client_socket in current_sockets and client_socket in self.wlist:
                    key = self.clients.get_key_by_socket(client_socket)
                    me = Encryption.encrypt(data, key).decode()
                    start_msg = "Start_Seg".encode('utf-8')
                    close_msg = "End_Seg".encode('utf-8')
                    msg_to_send = me.encode('utf-8')
                    msg_to_send = start_msg + msg_to_send + close_msg
                    time.sleep(0.28)
                    split_msg_to_send = self.big_message_spliter(msg_to_send, 640000000)
                    for spl in split_msg_to_send:
                        client_socket.send(spl)
                        print(f"{spl}")
                        #time.sleep(0.65)
                    print("boom= " + str(msg_to_send))
                    current_sockets.remove(client_socket)
                    message = (data, current_sockets)
            if len(current_sockets) == 0:
                try:
                    self.messages.remove(message)
                except:
                    continue
                break

    # this function connects the client to the system after login and sends to him list of all his chats
    def login_process(self, data, current_socket):
        arr = data.split(b'+*!?')
        username = arr[0].decode()
        hashed_pass = arr[1].decode()
        boolean = self.is_user_in_database(current_socket, username, hashed_pass)
        if boolean is True:
            self.clients.set_username(current_socket, username)
            current_id = None
            for i in get_column_from_db("id", self.db["users"]):
                if self.db["users"].get(i)["username"] == username:
                    current_id = i
                    break
            for chat_id in get_column_from_db("id", self.db["chats"]):
                if self.db["chats"].get(chat_id)["user_id"] == current_id:
                    chat_id = self.db["chats"].get(chat_id)["id"]
                    chat_external_id = self.db["chats"].get(chat_id)["external_id"]
                    chat_name = self.db["chats"].get(chat_id)["name"]
                    contacts = self.db["chats"].get(chat_id)["contacts"]
                    new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                    is_private = self.db["chats"].get(chat_id)["is_private"]
                    msg_to_send = f"new chat+*!?{chat_id}+*!?{chat_external_id}+*!?" \
                                  f"{chat_name}+*!?{contacts}+*!?{new_msgs}+*!?{is_private}"
                    self.msg_maker(msg_to_send, [current_socket])

    # this function checks if the user already signed up to the system sends a message to client according to the state
    def is_user_in_database(self, current_socket, username, hashed_pass):
        _list = [current_socket]
        current_id = 1
        while True:
            try:
                dict = self.db['users'].get(current_id)
                if dict["username"] == username and dict["hashed_password"] == hashed_pass and\
                        username not in self.clients.get_usernames():
                    # here the server needs send key to client and to send the chats msgs  "new chat msgs"
                    self.msg_maker("loged-in", _list)
                    self.send_waiting_messages()
                    for chat_id in get_column_from_db("id", self.db["chats"]):
                        chat = self.db["chats"].get(chat_id)
                        if chat["user_id"] == current_id:
                            print("hello")
                            print(str(current_id))
                            chat_id = chat_id
                            external_id = chat["external_id"]
                            chat_name = chat["name"]
                            contacts = chat["contacts"]
                            self.msg_maker(f"new chat+*!?{chat_id}+*!?{external_id}+*!?{chat_name}+*!?{contacts}",
                                           _list)
                    return True
                current_id = current_id + 1
            except NotFoundError:
                self.msg_maker("try again", _list)
                return False

    # checks if client that didn't sign in exits
    def check_client_exit(self, data):
        if len(data.split(b'+*!?')) == 2:
            tmp = data.split(b'+*!?')
            if tmp[0] == b'NAK':
                try:
                    self.clients.remove_client(tmp[0].decode('utf-8'))
                except:
                    pass
                return False
        return True

    # save to the database all the numbers of messages the client didn't read
    def update_db_after_client_NAK(self, data):
        if len(data) > 2:
            data = data[2:]
            for i, dt in enumerate(data):
                if i % 2 == 0:
                    chat_id = int(dt)
                    new_msgs = int(data[i + 1])
                    self.db["chats"].update(chat_id, {"new_msgs": new_msgs})

    # this function calls the functions according to the client requests.
    # handle all messages from online clients - not login and signup
    def handle_message(self, data, current_socket):
        if data.split(b'+*!?')[0].decode('utf-8') == 'NAK':
            data = data.decode('utf-8').split("+*!?")
            print(f"NAK data: {data}")
            username = data[1]
            try:
                self.update_db_after_client_NAK(data)
                self.clients.remove_client(username)
            except:
                print('already NAKed')
        elif data.split(b'+*!?')[0].decode('utf-8') == "exit chat":
            print("got exit chat request")
            data = data.decode("utf-8").split("+*!?")
            username = data[1]
            chat_external_id = data[2]
            chat_id = data[3]
            self.remove_client_from_chat(username, chat_external_id, chat_id)
        elif data.split(b'+*!?')[0].decode('utf-8') == "chat info":
            print("got info request")
            data = data.decode("utf-8").split("+*!?")
            chat_id = data[1]
            self.send_info_request(chat_id)
        elif data.split(b'+*!?')[0].decode('utf-8') == "add_contact":
            data = data.decode("utf-8").split("+*!?")
            sender_username = data[1]
            chat_id = data[2]
            contact = data[3]

            self.add_user_to_chat(sender_username, chat_id, contact)
        elif data.split(b'+*!?')[0].decode('utf-8') == "files_request":
            chat_id = data.split(b'+*!?')[1].decode('utf-8')
            self.handle_file_request(chat_id)

        elif data.split(b'+*!?')[0].decode('utf-8') == "get_file_value":
            tmp = data.split(b'+*!?')
            chat_id = tmp[1]
            file_id = tmp[2]
            self.send_file_to_client(chat_id, file_id)
            print("sent the file to the client")
        elif data.split(b'+*!?')[0].decode('utf-8') == "create private chat":
            tmp = data.split(b'+*!?')
            username_1 = tmp[1].decode('utf-8')
            username_2 = tmp[2].decode('utf-8')
            self.create_new_privet_chat(username_1, username_2)


        elif len(data.split(b'+*!?')) == 3:
            temp = data.split(b"+*!?")
            command = temp[0].decode("utf-8")
            print(command)

            if command == "public":
                temp = data.decode('utf-8').split('+*!?')
                print("in public if ")
                username = temp[1]
                socket_sender = self.clients.get_socket(username)
                msg = command + '+*!?' + username + '+*!?' + temp[2]
                print(f"the msg = {msg}")
                self.send_messages_without_sender(msg, socket_sender)


            if command == "create chat":
                print("here")
                temp = data.decode('utf-8').split('+*!?')
                chat_name = temp[1]
                contacts = temp[2].split(",")  # the self username
                self.create_new_chat(chat_name, contacts)

            if command == "chat request":
                temp = data.decode('utf-8').split('+*!?')
                chat_id = temp[1]
                external_id = temp[2]
                # sends all the msgs in this chat
                msgs = self.db["chats"].get(chat_id)["msgs"]
                self.db["chats"].update(chat_id, {"new_msgs": 0})
                msg_to_send = f"private+*!?+*!?{chat_id}+*!?{msgs}"
                sockets_list_to_send = []
                sockets_list_to_send.append(current_socket)
                self.msg_maker(msg_to_send, sockets_list_to_send)

        elif len(data.split(b'+*!?')) == 4:
            temp = data.split(b"+*!?")
            command = temp[0].decode("utf-8")

            if command == "new link":
                data = data.decode().split("+*!?")
                chat_external_id = data[1]
                manager_chat_id = data[2]
                username_to_link = data[3]
                self.link_in_DB(chat_external_id, manager_chat_id, username_to_link)

            if command == "private_file":
                username = temp[2].decode('utf-8')
                chat_id = temp[1].decode('utf-8')
                contents = temp[3].split(b'$$$')
                file_name = contents[0].decode('utf-8')
                file = contents[1]  # bytes object
                self.save_file_in_db(file, file_name, username, chat_id)

        elif len(data.split(b'+*!?')) == 5:
            data = data.decode('utf-8')
            data = data.split("+*!?")
            command = data[0]
            if command == 'private':  # this is a private msg condition
                sender_username = data[1]
                sender_chat_id = data[2]
                external_id = data[3]
                msg = data[4]
                self.save_msg_in_db(sender_username, sender_chat_id, external_id, msg)
                self.handle_private_message(sender_username, sender_chat_id, external_id, msg)

    def link_in_DB(self, chat_external_id, manager_chat_id, username_to_link):
        manager_chat = self.db["chats"].get(int(manager_chat_id))
        linked_chat_name = f'[LNK]{manager_chat["name"]}'
        linker_name = self.db["users"].get(manager_chat["user_id"])["username"]
        linker_id = self.db["users"].get(manager_chat["user_id"])["id"]
        contacts = manager_chat["contacts"]
        linked_chat_msg = f"Server: You linked to this chat by @{linker_name}"
        managers_id = manager_chat["managers_id"]

        chat_external_id = int(chat_external_id)
        id_of_the_linked = None
        for _id in get_column_from_db('id', self.db["users"]):
            current_user = self.db["users"].get(_id)
            username = current_user["username"]
            if username == username_to_link:
                id_of_the_linked = _id
                self.db["chats"].insert(
                    {"id": self.last_id, "name": linked_chat_name, "msgs": linked_chat_msg, "contacts": contacts
                        , "user_id": id_of_the_linked, "external_id": chat_external_id, "new_msgs": 1,
                     "managers_id": managers_id, "is_linked": True, "linker_id": linker_id, "files_ids": ""})
                if username in self.clients.get_usernames():
                    list_client = [self.clients.get_socket(username)]
                    self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(
                        chat_external_id) + "+*!?" + linked_chat_name + "+*!?" + contacts + "+*!?" + "1+*!?" + str(
                        False), list_client)
                self.last_id = self.last_id + 1

    def messages_connected(self, socket):
        big_data = self.clients.get_big_data_by_socket(socket)
        key = self.clients.get_key_by_socket(socket)
        print(f"my big big big data = {big_data}")
        # self.big_data = self.big_data
        msg_split1 = big_data.split("End_Seg".encode())
        if 'End_Seg'.encode() in big_data:
            print("it is in data")
        print(f"len = {len(msg_split1)}, list = {msg_split1}")
        wanted_list = []
        for i in range(len(msg_split1) - 1):
            mini_part = msg_split1[i]
            mini_part = mini_part.split("Start_Seg".encode())[1]
            data = mini_part
            mini_part = Encryption.decrypt(data, key)
            wanted_list.append(mini_part)
        self.clients.set_big_data_by_socket(socket, msg_split1[len(msg_split1) - 1])
        print(wanted_list)
        return wanted_list

    def send_messages_without_sender(self, message, sender):
        orgi_msg = message
        for client_socket in self.clients.get_sockets():
            if not client_socket == sender:
                key = self.clients.get_key_by_socket(client_socket)
                message = Encryption.encrypt(orgi_msg, key).decode()
                message = "Start_Seg" + message + "End_Seg"
                client_socket.send(message.encode('utf-8'))

    def send_message_clients(self, message, clients):
        for client in self.clients.get_sockets():
            if client in clients:
                client.send(message.encode('utf-8'))

    def signup_process(self, data, current_socket):
        arr = data.split(b'+*!?')
        email = arr[0].decode()
        username = arr[1].decode()
        hashed_pass = arr[2].decode()
        boolean = self.save_new_user_to_database(current_socket, email, username, hashed_pass)
        if boolean is True:
            self.send_waiting_messages()

    # this function removes client (username) from chat (_chat_external_id, _chat_id)
    def remove_client_from_chat(self, username, _chat_external_id, _chat_id):
        if _chat_id == 'public' or _chat_external_id == "public":
            return
        chat_ids = get_column_from_db("id", self.db["chats"])
        contacts_in_chat_before_remove = self.db["chats"].get(_chat_id)["contacts"].split(",")
        contacts_in_chat_before_remove.remove(username)

        contacts_in_chat_after_remove = ','.join(contacts_in_chat_before_remove)
        msg_to_save = f"private+*!?Server+*!?{_chat_id}+*!?{_chat_external_id}+*!?{username} left"
        self.save_msg_in_db("Server", f"{_chat_id}", f"{_chat_external_id}", f"{username} left")
        for chat_id in chat_ids:
            chat = self.db["chats"].get(chat_id)
            if str(chat['external_id']) == _chat_external_id:
                self.db['chats'].update(chat_id, {"contacts": contacts_in_chat_after_remove})
                if self.db["users"].get(chat["user_id"])["username"] in self.clients.get_usernames() and \
                        self.db["users"].get(chat["user_id"])["username"] != username:
                    msg_to_send = f"private+*!?Server+*!?{chat_id}+*!?{username} left"
                    self.msg_maker(msg_to_send,
                                   [self.clients.get_socket(self.db["users"].get(chat["user_id"])["username"])])
            if str(chat['id']) == _chat_id:
                for i in get_column_from_db("id",self.db["chats"]):
                    print(self.db['chats'].get(i))
                self.db["chats"].delete(chat_id)
                for i in get_column_from_db("id",self.db["chats"]):
                    print(self.db['chats'].get(i))
                break

    # this function sends a info of the current chat (chat_id) to the client
    def send_info_request(self, chat_id):
        user_chat = self.db["chats"].get(int(chat_id))
        name = self.db["users"].get(user_chat["user_id"])["username"]
        sock = [self.clients.get_socket(name)]
        external_id = user_chat["external_id"]
        is_linked = user_chat["is_linked"]
        c = user_chat['contacts']
        is_private = user_chat['is_private']
        if is_private:
            msg = f"chat info+*!?{False}+*!?{False}+*!?{2}+*!?{''}+*!?{c}+*!?{''}+*!?{True}"
            self.msg_maker(msg, sock)
            return
        is_manager = False
        user_id = str(user_chat["user_id"])
        _managers = user_chat["managers_id"].split(',')
        _contacts = user_chat["contacts"]
        contacts = user_chat['contacts'].split(',')
        num_of_contacts = len(contacts)
        managers = ""
        for mng in _managers:
            managers = managers + "," + self.db["users"].get(int(mng))["username"]
        m = managers.split(',')
        m = m[1:]
        i = 0
        for mm in m:
            m[i] = "@" + mm
            i += 1
        m = ','.join(m)
        if user_id in managers:
            is_manager = True
        users_he_linked = ""
        for chat_id in get_column_from_db("id", self.db["chats"]):
            chat = self.db["chats"].get(chat_id)
            if chat["is_linked"] and str(chat["linker_id"]) == user_id and chat["external_id"] == external_id:
                username = self.db["users"].get(chat["user_id"])['username']
                users_he_linked = users_he_linked + "," + username
        users_he_linked = ','.join(users_he_linked.split(',')[1:])
        is_private = False
        msg = f"chat info+*!?{is_manager}+*!?{is_linked}+*!?{num_of_contacts}" \
              f"+*!?{users_he_linked}+*!?{_contacts}+*!?{m}+*!?{is_private}"
        self.msg_maker(msg, sock)

    # this function saves to the database a file(file, file_name)
    # that uploaded by client (username) to the chat (chat-id)
    def save_file_in_db(self, file, file_name, username, chat_id):
        print(f"length of file i got: {len(file)}")
        chat_id = int(chat_id)
        self.db['files'].insert(
            {"id": self.last_file_id, "name": file_name, "value": file, "username_of_sender": username})
        external_id = self.db["chats"].get(chat_id)["external_id"]
        for _id in get_column_from_db("id", self.db['chats']):
            chat = self.db["chats"].get(chat_id)
            if chat["external_id"] == external_id:

                files = chat["files_ids"]
                if not files:
                    self.db['chats'].update(_id, {"files_ids": f"{self.last_file_id}"})
                else:
                    self.db['chats'].update(_id, {"files_ids": f"{self.last_file_id},{files}"})
        self.last_file_id += 1

    # this function sends to the client all the names, the ids and the senders of all the files he
    # has access in his current chat (chat_id)
    def handle_file_request(self, chat_id):
        chat = self.db["chats"].get(int(chat_id))
        files_ids = chat["files_ids"]
        ids = files_ids.split(',')
        senders = ''
        file_names = ''
        for file_id in ids:
            print("file_id=", file_id)
            if file_id != '':
                f = self.db["files"].get(int(file_id))
                file_names += f["name"] + ","
                senders += f["username_of_sender"] + ","
        file_names = file_names[:-1]
        senders = senders[:-1]
        msg = f"files_in_chat+*!?{files_ids}+*!?{file_names}+*!?{senders}"
        sock = [self.clients.get_socket(self.db["users"].get(chat['user_id'])['username'])]
        self.msg_maker(msg, sock)

    # this function sends a file (file_id) to the client's chat (chat_id)
    def send_file_to_client(self, chat_id, file_id):
        chat_id = int(chat_id)
        file_id = int(file_id)
        f = self.db["files"].get(file_id)
        file_name = f["name"]
        value = f["value"]
        print(f"length of file i send: {len(value)}")
        msg_byte_object = f"private_file+*!?+*!?{file_name}$$$".encode() + value
        sock = [self.clients.get_socket(self.db["users"].get(self.db["chats"].get(chat_id)["user_id"])['username'])]
        self.msg_maker(msg_byte_object, sock)
        self.send_waiting_messages()

    # this function adds new user (username_to_add) to a chat (chat_id) by (sender_username)
    def add_user_to_chat(self, sender_username, chat_id, username_to_add):
        chat = self.db['chats'].get(int(chat_id))
        chat_name = chat['name']
        files_ids = chat['files_ids']
        external_id = chat['external_id']
        sender_id = chat['user_id']
        managers_ids_list = chat['managers_id'].split(',')
        managers_ids_string = ','.join(managers_ids_list)
        contacts = chat['contacts']
        contacts_split = contacts.split(',')
        new_contacts = contacts_split.copy()
        new_contacts.append(username_to_add)
        new_contacts_string = ','.join(new_contacts)
        id_to_add = None
        is_exists = False
        for i in get_column_from_db('id', self.db['users']):
            user = self.db["users"].get(i)
            if user['username'] == username_to_add:
                is_exists = True
        if is_exists is False:
            return
        if str(sender_id) not in managers_ids_list:
            return
        if username_to_add in contacts_split:
            print(contacts_split)
            return
        else:
            for _id in get_column_from_db("id", self.db['users']):
                if username_to_add == self.db['users'].get(_id)['username']:
                    id_to_add = _id
            for i in get_column_from_db("id", self.db['chats']):
                chat = self.db['chats'].get(i)
                if chat['external_id'] == external_id:
                    print(f'this is new_contacts_string={new_contacts_string}')
                    self.db['chats'].update(i, {"contacts": new_contacts_string})
                    user_name = self.db['users'].get(self.db['chats'].get(i)['user_id'])["username"]
                    if user_name in self.clients.get_usernames():
                        # msg_to_save = f"private+*!?Server+*!?{i}+*!?{external_id}+*!?{user_name} added"
                        msg = f"private+*!?Server+*!?{i}+*!?{username_to_add} added"
                        self.msg_maker(msg, [self.clients.get_socket(user_name)])
            msg_to_save = f"private+*!?Server+*!?{chat_id}+*!?{external_id}+*!?{username_to_add} added"
            self.save_msg_in_db('Server', f"{chat_id}", f"{external_id}", f"{username_to_add} added")
            self.db['chats'].insert({"id": self.last_id, "external_id": external_id, "name": chat_name,
                                     "msgs": f"Server: @{sender_username} added you to this chat",
                                     "contacts": new_contacts_string,
                                     "user_id": id_to_add, "new_msgs": 1, "managers_id": managers_ids_string,
                                     "is_linked": False,
                                     "files_ids": files_ids, "is_private": False})
            if username_to_add in self.clients.get_usernames():
                list_client = [self.clients.get_socket(username_to_add)]
                self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(external_id) + "+*!?" + chat_name
                               + "+*!?" + new_contacts_string + "+*!?" + "1+*!?" + str(False), list_client)
            self.last_id += 1

    # sends the private messages to the clients
    def handle_private_message(self, sender_username, sender_chat_id, external_id, msg):
        manager = False
        sender_id = ""
        for i in get_column_from_db("id", self.db["users"]):
            if self.db["users"].get(i)["username"] == sender_username:
                sender_id = str(i)
        managers = self.db["chats"].get(int(sender_chat_id))["managers_id"].split(
            ",")  # list of str of managers ids
        if sender_id in managers:
            manager = True  # make us know if the sender is a manager
        linker_two_id = None
        linker_username_two = None
        managers_ids = self.db["chats"].get(int(sender_chat_id))["managers_id"]
        managers_ids = managers_ids.split(',')
        list_of_sockets_to_send = []
        list_of_contacts = self.db["chats"].get(int(sender_chat_id))["contacts"].split(',')
        _list_of_contacts = list_of_contacts.copy()
        print(f"list of contacts = {list_of_contacts}")
        contacts_with_linked = _list_of_contacts
        for _id in get_column_from_db("id", self.db["chats"]):
            if self.db["chats"].get(_id)["is_linked"] == 1 and str(
                    self.db["chats"].get(_id)["external_id"]) == external_id:
                print('=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=r=')
                username = self.db["users"].get(self.db["chats"].get(_id)["user_id"])["username"]
                contacts_with_linked.append(username)
        all_ids_in_users = get_column_from_db("id", self.db["users"])
        ids_to_send = []
        usernames_to_send = []
        for contact in contacts_with_linked:  # list with the usernames of all the contacts and all the linked
            if contact in self.clients.get_usernames():
                for current_id in all_ids_in_users:
                    if self.db["users"].get(current_id)["username"] == contact:
                        ids_to_send.append(current_id)
                        usernames_to_send.append(contact)
                        break
        # list_of_contacts = _list_of_contacts
        print(f"1sender_username = {sender_username}    ,list_of_contacts = {list_of_contacts}")
        linker_username_two_is_manager = False
        is_sender_linked: bool = False
        linker_username = None
        linker_is_manager = False
        print(f"2sender_username = {sender_username}    ,list_of_contacts = {list_of_contacts}")
        if sender_username not in list_of_contacts:
            is_sender_linked = True
            print('the sender is a linked ')
            linker = self.db['users'].get(self.db["chats"].get(int(sender_chat_id))["linker_id"])
            linker_username = linker["username"]
            linker_id = self.db["chats"].get(int(sender_chat_id))["linker_id"]
            if str(linker_id) in managers:
                linker_is_manager = True
                print('the linker is also a manager')

        # now the usernames and the ids orgenized
        for i in range(len(usernames_to_send)):
            username = usernames_to_send[i]
            id_of_username = int(ids_to_send[i])
            if username != sender_username:
                socket = self.clients.get_socket(username)
                sockets = [socket]
                print("self.get_column_from_db('id',self.db['chats']) = " + str(
                    get_column_from_db("id", self.db["chats"])))
                c = None
                for id in get_column_from_db("id", self.db["chats"]):
                    if str(self.db["chats"].get(id)["user_id"]) == str(id_of_username) and str(
                            self.db["chats"].get(id)["external_id"]) == str(external_id):
                        c = id  # the current chat id
                        break
                is_user_linked = True
                if username in list_of_contacts:
                    is_user_linked = False

                if is_user_linked is True and is_sender_linked is True:
                    for _id in get_column_from_db("id", self.db["user"]):
                        if self.db["users"].get(_id)["username"] == username:
                            id_of_username = _id
                            break
                    for t in get_column_from_db("id", self.db["chats"]):
                        chat = self.db["chats"].get(t)
                        if id_of_username == chat["user_id"] and str(chat["external_id"]) == external_id:
                            linker_two_id = chat["linker_id"]
                            linker_username_two = self.db["users"].get(linker_two_id)['username']
                            break
                    print(f"linker_two_id = {linker_two_id},")
                    if str(linker_two_id) in managers:
                        linker_username_two_is_manager = True

                    if linker_is_manager is True:
                        linker_username = "@" + linker_username
                    if linker_username_two_is_manager is True:
                        linker_username_two = "@" + linker_username_two
                    self.msg_maker(
                        f"private+*!?[{linker_username_two}][{linker_username}]{sender_username}+*!?{c}+*!?{msg}",
                        sockets)
                print(f"is_user_linked= {is_user_linked}\nis_sender_linked= {is_sender_linked}")
                if is_user_linked is False and is_sender_linked is True:
                    print(f"ttt {linker_username}")
                    if linker_is_manager:
                        self.msg_maker(f"private+*!?[@{linker_username}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                    else:
                        self.msg_maker(f"private+*!?[{linker_username}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                if is_user_linked is True and is_sender_linked is False:
                    self.msg_maker(f"private+*!?{sender_username}+*!?{c}+*!?{msg}", sockets)
                else:
                    if manager:
                        self.msg_maker(f"private+*!?@{sender_username}+*!?{c}+*!?{msg}", sockets)
                    else:
                        self.msg_maker(f"private+*!?{sender_username}+*!?{c}+*!?{msg}", sockets)


# gets two lists and returns new list with all the elements the lists have in common
def shared_list(list1, list2):
    list3 = []
    for i in list1:
        if i in list2 and i not in list3:
            list3.append(i)
    return list3


# this function returns a column (column) from a database table (table)
def get_column_from_db(column, table):
    _list = []
    i = 1
    while True:
        try:
            dict = table.get(i)[column]
            _list.append(dict)
            i = i + 1
        except NotFoundError:
            return _list




if __name__ == '__main__':
    Server().run()
