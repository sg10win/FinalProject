import socket
import sqlite3
import select
import datetime
import random
import time

import sqlite_utils
from cryptography.fernet import Fernet
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError

class Client(object):
    def __init__(self, username, socket):
        self._username = username
        self._socket = socket

    # def send(self, message):
    #     self._socket.send(message.encode('utf-8'))
    #
    # def recv(self):
    #     return self._socket.recv(1024).decode('utf-8')

    def get_username(self):
        return self._username

    def set_username(self, username):
        self._username = username

    def is_username(self, username):
        return self._username == username

    def get_socket(self):
        return self._socket


class ListClients(object):
    def __init__(self):
        self._clients = []

    def add_client(self, username, socket):
        self._clients.append(Client(username, socket))

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

    def _get_client_by_username(self, username):
        for client in self._clients:
            if client.get_username() == username:
                return client
        raise Exception("username not found in client list to return client")

    def _get_client_by_socket(self, socket):
        return self._get_client_by_username(self.get_username(socket))

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
        # new_client_list = []
        # for client in self._clients:
        #     if not client.get_username() == None:
        #         new_client_list.append(client)
        # self._clients = new_client_list


# you need to remember to colse the database connection
class Server(object):
    def __init__(self):
        self.ip = "0.0.0.0"
        self.port = 8080
        self.server_socket = socket.socket()
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        #self.conn = sqlite3.connect('users_01.db')
        self.db = Database(sqlite3.connect("users_01.db"))
        print("opened database successfully")
        self.database_reset_temp()  # res
        self.all_client_seckets = {}
        self.open_client_sockets = {}
        self.messages = []
        self.managing_client_sockets = []
        self.denied_clients = []
        self.private_conversation = []
        self.last_id=0

        self.clients = ListClients()

    def database_reset_temp(self):
        try:
            #self.conn.execute('''DROP TABLE CHATS;''')

            self.db["chats"].drop()
        except:
            print("there is no table CHATS")
        try:
            #self.conn.execute('''DROP TABLE USERS;''')
            self.db["users"].drop()
        except:
            print("there is no table USERS")
        # self.conn.execute('''CREATE TABLE USERS
        # (
        # id                  INTEGER     PRIMARY KEY,
        # email               TEXT        NOT NULL,
        # username            TEXT        NOT NULL,
        # hashed_password     TEXT        NOT NULL);''')

        self.db['users'].create({
            "id": int,
            "email": str,
            "username": str,
            "hashed_password":str,
            },pk="id")
        print("table created successfully")
        users = self.db["users"]
        users.insert({"username": "segev10",
                      "email": "segevshalom86@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "a",
                      "email": "a@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "b",
                      "email": "b6@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('segevshalom86@gmail.com','segev10','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('a@gmail.com','a','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('b@gmail.com','b','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute('''CREATE TABLE CHATS
        #         (
        #         id                  INTEGER     PRIMARY KEY,
        #         name                TEXT        NOT NULL,
        #         contacts            TEXT        NOT NULL,
        #         msgs                TEXT        NOT NULL,
        #         user_id             INTEGER        NOT NULL,
        #         external_id         INTEGER     NOT NULL,
        #         FOREIGN KEY(user_id)  REFERENCES  USERS(id));''')
        self.db["chats"].create({
            "id":int,
            "name":str,
            "contacts":str,
            "msgs":str,
            "user_id":int,
            "external_id":int,},
            foreign_keys=["user_id"])
        # self.conn.close

    def msg_maker(self, data, list_of_sockets_to_send):  # the type is 's'-signup, 'l'-login, 'm'-msg, **'f'-file**
        print(data)
        msg = data, list_of_sockets_to_send
        self.messages.append(msg)


    def get_list_of_contacts(self, external_id):
        i = 1
        contacts = None
        while True:
            try:
                chat = self.db["chats"].get(i)
                print(f"--------------194: {chat}----------------")
                temp_external_id = chat["external_id"]
                print(f"temp_external_id: {temp_external_id}")
                print(f"external_id: {external_id}")
                if str(temp_external_id) == str(external_id) :
                    contacts = chat["contacts"]
                    break
                i +=1
            except NotFoundError:
                 print("the chat not found")
                 break

        list_of_contacts = contacts.split(",")
        return list_of_contacts

        # this method adds a msg to send about whats wrong with the params if it is and return true if the process done and false if not
    def save_new_user_to_database(self, socket, email, username, hashed_password):
        cursor1 = []
        cursor2 = []
        for row in self.db["users"].rows_where("username = ?", [username]):
            cursor1.append(row)
        for row in self.db["users"].rows_where("email = ?", [email]):
            cursor2.append(row)
        #cursor = self.conn.execute('''SELECT email,username FROM USERS;''')
        list = []
        list.append(socket)

        if cursor1 and cursor2:
            self.msg_maker("This email and username are\n currently in use", list)
            return False
        elif cursor2:
            self.msg_maker("This email is currently in use", list)
            return False
        elif cursor1:
            self.msg_maker("This username is currently in use", list)
            return False

        #email = "'" + email + "'"
        #username = "'" + username + "'"
        #hashed_password = "'" + hashed_password + "'"
        #self.conn.execute(
        #    "INSERT INTO USERS (email, username, hashed_password) VALUES (" + email + ',' + username + ',' + hashed_password + ");")
        self.db["users"].insert({"email": email, "username":username, "hashed_password": hashed_password}, pk='id')
        #cursor = self.conn.execute('''SELECT email,username,hashed_password FROM USERS;''')
        self.msg_maker("signed in successfully", list)
        return True

    def get_column_from_db(self, column, db):
        list = []
        i = 1
        while True:
            try:
                dict = db.get(i)[column]
                list.append(dict)
                i = i+1
            except NotFoundError:
                return list





    def convert_list_str(self, list):

        return "".join(list)

    def create_new_chat(self, chat_name, contacts):#contacts is list object not string

        c = ','.join(contacts)
        new_chat_msg = 'you were added to this chat'
        random_external_id = random.randint(1, 10000)
        while random_external_id in self.get_column_from_db("external_id", self.db["chats"]):
            random_external_id = random.randint(1, 10000)
        ids = self.get_column_from_db("id", self.db["users"])
        usernames = self.get_column_from_db("username", self.db["users"])
        for i in range(len(usernames)):
            if usernames[i] in contacts:
                self.db["chats"].insert_all([
                    {"id":self.last_id+1, "name": chat_name, "msgs": new_chat_msg, "contacts": c, "user_id": ids[i],
                    "external_id": random_external_id}], pk="id")
                self.last_id = + 1
                print(f"--------{self.db['chats'].get(self.last_id)}---------")
                # TODO TO SEND TO CLIENTS THE : ID, NAME, MSGS
                if usernames[i] in self.clients.get_usernames():
                    print(f'new chat {usernames[i]}')
                    list_client = [self.clients.get_socket(usernames[i])]
                    self.msg_maker(
                        "new chat%%%" + str(self.last_id) + "%%%" + str(random_external_id) + "%%%" + chat_name + "%%%" + c + "%%%" + new_chat_msg, list_client)
                # TODO  IF THE CLIENT NOT HAS A CONNECTION IN THIS MOMENT





        # new_chat_msg = 'You'
        # random_external_id = random.randint(1, 10000)
        # cursor = self.conn.execute("""SELECT external_id FROM CHATS;""")
        # while random_external_id in cursor:
        #     random_external_id = random.randint(1,10000)
        # cursor = self.conn.execute('''SELECT id,username FROM USERS;''')
        # c = str(contacts)[1:-1]
        # print("c= "+c)
        # db = sqlite_utils.Database("users_01.db")
        # for row in cursor:
        #     id = row[0]
        #     username = row[1]
        #     if username in contacts:
        #         db["CHATS"].insert_all([
        #             {"name": chat_name, "msgs": new_chat_msg, "contacts": c, "user_id": id, "external_id": random_external_id}], pk="id")
        #         #self.conn.execute("""INSERT INTO CHATS (name, msgs, contacts, user_id, external_id) VALUES ("""+str(chat_name)+","+
        #                           #str(new_chat_msg)+","+str(c)+","+str(id)+","+str(random_external_id)+");")
        #         #TODO TO SEND TO CLIENTS THE : ID, NAME, MSGS
        #         if username in self.open_client_sockets.keys():
        #             self.msg_maker("new chat%%%"+id+"%%%"+random_external_id+"%%%"+chat_name+"%%%"+c+"%%%"+new_chat_msg,self.open_client_sockets.keys())
        #         #TODO  IF THE CLIENT NOT HAS A CONNECTION IN THIS MOMENT

    def save_msg_in_db (self,msg):
        msg = msg.split("%%%")
        username = msg[1]
        id = msg[2]
        external_id = msg[3]
        input = msg[4]


    def run(self):
        print("server started")
        while True:
            # aaa = [self.server_socket] + list(self.open_client_sockets.keys())
            aaa = [self.server_socket] + self.clients.get_sockets()
            # rlist, wlist, xlist = select.select(aaa, list(self.open_client_sockets.keys()), [])
            rlist, wlist, xlist = select.select(aaa, self.clients.get_sockets(), [])
            # print(self.messages)
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    # self.open_client_sockets[
                    #     new_socket] = ""  # now if new socket is signing in, his name will be "" and then it is easy to get him
                    self.clients.add_client('', new_socket)
                    print("new client")
                    print(rlist)
                else:
                    data = current_socket.recv(1024)
                    if not data.decode('utf-8') == '':
                        print("189" + data.decode())

                        key, data = data.split(b"%%%")
                        print(type(key), "= ", key)
                        data = self.do_decrypt(key, data)
                        print(str(data.decode('utf-8')))
                    # if self.open_client_sockets[current_socket] == "":  # this is the sign of new singing in user
                    if self.clients.get_username(current_socket) == '':  # this is the sign of new singing in user
                        if self.check_client_exit(data):
                            temp_d = data.split(b'%%%')
                            if len(temp_d) == 3:
                                self.signup_process(data, current_socket, wlist)
                            if len(temp_d) == 2:
                                self.login_process(data, current_socket, wlist)
                    else:
                        self.decifer(data, current_socket)
            time.sleep(0.05)
            self.send_waiting_messages(wlist)

    def send_waiting_messages(self, wlist):
        for message in self.messages:
            (data, current_sockets) = message
            # for client_socket in list(self.open_client_sockets.keys()):
            for i, client_socket in enumerate(self.clients.get_sockets()):
                if client_socket in current_sockets and client_socket in wlist:
                    print(f'\n\nsend waiting messages in loop{i} {client_socket}\n\n')
                    key = Fernet.generate_key()  # generates new key (bytes object) randomly
                    data = key.decode() + "%%%" + self.do_encrypt(key, data.encode()).decode()
                    print("the data in line 336: " + str(data))

                    msg_to_send = data.encode('utf-8')
                    client_socket.send(msg_to_send)
                    current_sockets.remove(client_socket)
                    message = (data, current_sockets)
            if len(current_sockets) == 0:
                try:
                    self.messages.remove(message)
                except:
                    continue
                break

    def login_process(self, data, current_socket, wlist):
        arr = data.split(b'%%%')
        username = arr[0].decode()
        hashed_pass = arr[1].decode()
        print("username= ", username, "hashed_pass= ", hashed_pass)
        boolean = self.is_user_in_database(current_socket, username, hashed_pass)
        print(self.messages)
        self.send_waiting_messages(wlist)
        if boolean == True:
            print("dict before :", self.open_client_sockets)
            self.open_client_sockets[current_socket] = username
            self.clients.set_username(current_socket, username)
            print(self.clients.get_usernames(), self.clients)
            print("dict after :", self.open_client_sockets)
            # current_socket.send()

    def is_user_in_database(self, current_socket, username, hashed_pass):
        list = []
        list.append(current_socket)
        i = 1
        while True:
            try:
                dict = self.db['users'].get(i)
                if dict["username"] == username and dict["hashed_password"] == hashed_pass:
                    self.msg_maker("loged-in", list)
                    return True
                i = i+1
            except NotFoundError:
                self.msg_maker("try again", list)
                return False



        # list = []
        # list.append(current_socket)
        # cursor = self.conn.execute('''SELECT username,hashed_password FROM USERS;''')
        # for row in cursor:
        #     if username == row[0] and hashed_pass == row[1]:
        #         self.msg_maker("loged-in", list)
        #         return True
        # self.msg_maker("try again", list)
        # return False

    def check_client_exit(self, data):
        if len(data.split(b'%%%')) == 2:
            tmp = data.split(b'%%%')
            if tmp[1] == b'NAK':
                print(tmp[0].decode("utf-8") + " has logedout")
                self.clients.remove_client(tmp[0].decode('utf-8'))
                print('exit client: ', tmp[0].decode('utf-8'))
                return False
        return True

    def do_decrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.decrypt(data)

    def do_encrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.encrypt(data)

    def decifer(self, data, current_socket):
        '''___TODO___'''
        print('enter decifer')
        if len(data.split(b'%%%')) == 2:
            tmp = data.split(b'%%%')
            if tmp[1] == b'NAK':
                print(tmp[0].decode("utf-8") + " has logedout")
                self.clients.remove_client(tmp[0].decode('utf-8'))
                print('exit client: ', tmp[0].decode('utf-8'))

        if len(data.split(b'%%%')) == 3:
            print("322"+data.decode('utf-8'))
            temp = data.decode('utf-8').split("%%%")
            command = temp[0]
            if command == "public":
                username = temp[1]
                socket_sender = self.clients.get_socket(username)
                msg = command + '%%%' + username + '%%%' + temp[2]
                self.send_messages_without_sender(msg, socket_sender)
            if command == "create chat":
                chat_name = temp[1]
                print("332 temp[2] = "+temp[2])
                contacts = temp[2].split(",")#the self username
                print(str(contacts))
                #print("contacts = "+str(contacts))
                self.create_new_chat(chat_name, contacts)
            if command == "chat request":
                id = temp[1]
                external_id = temp[2]

        if len(data.split(b'%%%')) == 5:# this is a private msg condition
            data = data.decode('utf-8')
            data = data.split("%%%")
            command = data[0]

            username = data[1]
            id = data[2]
            external_id = data[3]
            msg = data[4]
            # I NEED TO SEND THE MSG TO THE CHAT CONTACTS AND TO SAVE IT IN THE DB
            list_of_sockets_to_send = []
            list_of_contacts = self.get_list_of_contacts(external_id)
            for client in list_of_contacts:
                socket = self.clients.get_socket(client)
                list_of_sockets_to_send.append(socket)
            list_of_sockets_to_send.remove(self.clients.get_socket(username))
            self.msg_maker(f"private%%%{username}%%%{id}%%%{msg}", list_of_sockets_to_send)


    def send_messages_without_sender(self, message, sender):
        orgi_msg = message
        for client_socket in self.clients.get_sockets():
            if not client_socket == sender:
                key = Fernet.generate_key()  # generates new key (bytes object) randomly
                message = key.decode() + "%%%" + self.do_encrypt(key, orgi_msg.encode()).decode()
                client_socket.send(message.encode('utf-8'))
                print(f"ad{client_socket} :" + message)
                print(self.clients.get_username(client_socket))

    def send_message_clients(self, message, clients):
        for client in self.clients.get_sockets():
            if client in clients:
                client.send(message.encode('utf-8'))

    def signup_process(self, data, curret_socket, wlist):
        '''__TODO__ SEND THIS PARAMS TO THE DATABASE'''
        '''THE PROTOCLOL IS SIMPLE <EMAIL>%%%<USERNAME>%%%<HASHED PASSWORD>'''
        arr = data.split(b'%%%')
        email = arr[0].decode()
        username = arr[1].decode()
        hashed_pass = arr[2].decode()
        print("username= ", username, 'email= ', email, "hashed_pass= ", hashed_pass)
        boolean = self.save_new_user_to_database(curret_socket, email, username, hashed_pass)
        if boolean == True:
            self.send_waiting_messages(wlist)
            print("dict before :", self.open_client_sockets)
            # self.open_client_sockets.__delitem__(curret_socket)
            print("dict after :", self.open_client_sockets)


Server().run()
