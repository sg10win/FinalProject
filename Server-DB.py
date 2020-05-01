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
            print("oy")
            a= self._get_client_by_socket(socket)
            if a:
                a.set_big_data(data)
            else:
                print("oy 2")
        # for client_socket in self.get_sockets():
        #     if client_socket == socket:
        #        self._get_client_by_socket(client_socket).set_big_data(data)
        else:
            raise Exception("socket not found in client list")


# you need to remember to colse the database connection
class Server(object):
    def __init__(self):
        self.ip = "0.0.0.0"
        self.port = 8080
        self.server_socket = socket.socket()
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.db = Database(sqlite3.connect("users_01.db"))
        print("opened database successfully")
        self.database_reset_temp()  # resets DB
        self.messages = []
        self.last_id = 1
        self.last_file_id = 1

        self.clients = ListClients()

    def database_reset_temp(self):
        try:
            #self.conn.execute('''DROP TABLE CHATS;''')

            self.db["files"].drop()
        except:
            print("there is no table FILES")
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
                      "id" : 1,
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
        print(users.get(1))
        print(users.get(2))
        print(users.get(3))
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
            "files_ids": str},
            pk="id"
            )
        self.db["files"].create({
            "id": int,
            "name": str,
            "value": bytes,
            "username_of_sender": str
        })

    def msg_maker(self, data, list_of_sockets_to_send):  # the type is 's'-signup, 'l'-login, 'm'-msg, **'f'-file**
        #print(data)
        msg = data, list_of_sockets_to_send
        self.messages.append(msg)


    def get_list_of_contacts(self, external_id):
        i = 1
        contacts = None
        while True:
            try:
                chat = self.db["chats"].get(i)
                temp_external_id = chat["external_id"]
                if str(temp_external_id) == str(external_id) :
                    contacts = chat["contacts"]
                    break
                i +=1
            except NotFoundError:
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

    def get_column_from_db(self, column, table):
        list = []
        i = 1
        while True:
            try:
                dict = table.get(i)[column]
                list.append(dict)
                i = i+1
            except NotFoundError:
                return list

    def shared_list(self, list1, list2):
        list3 = []
        for i in list1:
            if i in list2 and i not in list3:
                list3.append(i)
        return list3

    def convert_list_str(self, list):

        return "".join(list)


    def create_new_chat(self, chat_name, contacts):
        creator_username = contacts[-1]
        _ids = self.get_column_from_db("id", self.db["users"])
        for _id in _ids:
            if self.db["users"].get(_id)["username"] == creator_username:
                creator_id = str(_id)
        new_chat_msg = 'IChat Server: you were added to this chat'
        # list of right contacts only
        all_usernames = self.get_column_from_db("username",self.db["users"])#list of all the usernames in the db
        usernames = self.shared_list(all_usernames, contacts)#list of the usernames we need to make a chat for them
        contacts = ','.join(usernames)
        random_external_id = random.randint(1, 10000)
        while random_external_id in self.get_column_from_db("external_id", self.db["chats"]):
            random_external_id = random.randint(1, 10000)
        user_ids = self.get_column_from_db("id", self.db["users"])
        #print(user_ids)
        for user_id in user_ids:
            print(f"user_id={user_id}")
            username = self.db["users"].get(user_id)["username"]
            if username in usernames:
                self.db["chats"].insert({"id": self.last_id, "name": chat_name, "msgs": new_chat_msg, "contacts": contacts
                                            , "user_id": user_id, "external_id": random_external_id, "new_msgs": 1, "managers_id": creator_id, "is_linked": False, "files_ids": ""})
                print(f"created this chat now=>{self.db['chats'].get(self.last_id)}")
                if username in self.clients.get_usernames():
                    list_client = [self.clients.get_socket(username)]
                    self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(random_external_id) + "+*!?" + chat_name + "+*!?" + contacts + "+*!?" + "1", list_client)
                    #print("sent after it=>"+"new chat%%%" + str(self.last_id) + "%%%" + str(random_external_id) + "%%%" + chat_name + "%%%" + contacts + "%%%" + new_chat_msg)
                self.last_id = self.last_id + 1


    def print_table (self, table ):
        for i in self.get_column_from_db("id", table):
            print(table.get(i))



    def save_msg_in_db1 (self,msg):
        self.print_table(self.db["chats"])
        msg = msg.split("+*!?")
        username = msg[1]
        sender_chat_id = msg[2]
        external_id = msg[3]
        msg = msg[4]

        sender_id = str(self.db['chats'].get(int(sender_chat_id))['user_id'])
        managers_ids = self.db["chats"].get(int(sender_chat_id))["managers_id"]
        managers_ids = managers_ids.split(',')


        for chat_id in self.get_column_from_db("id",self.db["chats"]):
            if self.db["chats"].get(chat_id)["external_id"] == int(external_id):
                print("in if 1")
                if str(chat_id) != sender_chat_id:
                    print("in if 2")
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\n{username}: {msg}"
                    if sender_id in managers_ids:
                        msgs = f"{previous_msgs}\n@{username}: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})
                    username_that_want_the_msg = self.db["users"].get(self.db["chats"].get(chat_id)["user_id"])["username"]
                    if username_that_want_the_msg not in self.clients.get_usernames(): # the client isn't online
                        new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                        self.db["chats"].update(chat_id, {"new_msgs": new_msgs+1})
                        print(f"did it and new_msgs = {self.db['chats'].get(chat_id)['new_msgs']}")
                else:
                    print("in else")
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\nYou: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})
                #print(f"updated = {self.db['chats'].get(chat_id)}")



    def run(self):
        print("server started")
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + self.clients.get_sockets(), self.clients.get_sockets(), [], 0.01)
            # print(self.messages)
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    # self.open_client_sockets[
                    #     new_socket] = ""  # now if new socket is signing in, his name will be "" and then it is easy to get him
                    key = Fernet.generate_key()
                    self.clients.add_client('', new_socket,key)
                    print("new client")
                    new_socket.send(key.decode().encode('utf-8'))
                    print("sent key")
                else:
                    data_list = []
                    data = current_socket.recv(1024)
                    if not data.decode('utf-8') == '':
                        #print("189" + data.decode())

                        #key, data = data.split(b"%%%")
                        #print(type(key), "= ", key)
                        #key = self.clients.get_key_by_socket(current_socket)
                        #data = self.do_decrypt(key, data)
                        if current_socket in self.clients.get_sockets():
                            print("ok")
                            self.clients.set_big_data_by_socket(current_socket,self.clients.get_big_data_by_socket(current_socket)+data)
                            data_list = self.messages_connected(current_socket)
                            print(data_list)
                        else:
                            print("wtf")
                            if current_socket == self.server_socket:
                                print("r r r ")


                        #print(str(data.decode('utf-8')))
                    # if self.open_client_sockets[current_socket] == "":  # this is the sign of new singing in user
                    if self.clients.get_username(current_socket) == '':  # this is the sign of new singing in user
                        print("no username")
                        if data_list != [] and self.check_client_exit(data_list[0]):
                            print("logging")
                            data = data_list.pop(0)
                            temp_d = data.split(b'+*!?')
                            if len(temp_d) == 3:
                                self.signup_process(data, current_socket, wlist)
                            if len(temp_d) == 2:
                                self.login_process(data, current_socket, wlist)
                        if data_list != []:
                            print("decipher after logging")
                            for data in data_list:
                                self.decifer(data, current_socket)

                    else:
                        print("only decipher")
                        for data in data_list:
                            self.decifer(data, current_socket)
            time.sleep(0.05)
            self.send_waiting_messages(wlist)

    def send_waiting_messages(self, wlist):
        for message in self.messages:
            (data, current_sockets) = message
            # for client_socket in list(self.open_client_sockets.keys()):
            for i, client_socket in enumerate(self.clients.get_sockets()):
                if client_socket in current_sockets and client_socket in wlist:
                    #print(f'\n\nsend waiting messages in loop{i} {client_socket}\n\n')
                    #key = Fernet.generate_key()  # generates new key (bytes object) randomly
                    #lol = data
                    print ("a")
                    key = self.clients.get_key_by_socket(client_socket)
                    # me = key.decode() + "%%%" + self.do_encrypt(key, data.encode()).decode()
                    me = self.do_encrypt(key, data).decode()
                    print("b")

                    #print("the data in line 336: " + str(data))
                    start_msg = "Start_Seg".encode('utf-8')
                    close_msg = "End_Seg".encode('utf-8')
                    msg_to_send = me.encode('utf-8')

                    # time.sleep(0.25)
                    msg_to_send = start_msg + msg_to_send + close_msg
                    client_socket.send(msg_to_send)

                    print("384 msg_to_send = "+str(msg_to_send))
                    #print(self.clients.get_username(client_socket))
                    current_sockets.remove(client_socket)
                    message = (data, current_sockets)
            if len(current_sockets) == 0:
                try:
                    self.messages.remove(message)
                except:
                    continue
                break

    def login_process(self, data, current_socket, wlist):
        arr = data.split(b'+*!?')
        username = arr[0].decode()
        hashed_pass = arr[1].decode()
        #print("username= ", username, "hashed_pass= ", hashed_pass)
        boolean = self.is_user_in_database(current_socket, username, hashed_pass)
        self.send_waiting_messages(wlist)
        #print(self.messages)
        self.send_waiting_messages(wlist)
        if boolean == True:
            #print("dict before :", self.open_client_sockets)
            self.clients.set_username(current_socket, username)
            current_id = None
            for i in self.get_column_from_db("id", self.db["users"]):
                if self.db["users"].get(i)["username"] == username:
                    current_id = i
                    break
            for chat_id in self.get_column_from_db("id", self.db["chats"]):
                if self.db["chats"].get(chat_id)["user_id"] == current_id:
                    chat_id = self.db["chats"].get(chat_id)["id"]
                    chat_external_id = self.db["chats"].get(chat_id)["external_id"]
                    chat_name = self.db["chats"].get(chat_id)["name"]
                    contacts = self.db["chats"].get(chat_id)["contacts"]
                    new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                    msg_to_send = f"new chat+*!?{chat_id}+*!?{chat_external_id}+*!?{chat_name}+*!?{contacts}+*!?{new_msgs}"
                    self.msg_maker(msg_to_send, [current_socket])
            #print(self.clients.get_usernames(), self.clients)
            #print("dict after :", self.open_client_sockets)
            # current_socket.send()

    def is_user_in_database(self, current_socket, username, hashed_pass):
        list = []
        list.append(current_socket)
        current_id = 1
        while True:
            try:
                dict = self.db['users'].get(current_id)
                if dict["username"] == username and dict["hashed_password"] == hashed_pass:
                    # here the server needs send key to client and to send the chats msgs  "new chat msgs"
                    self.msg_maker("loged-in", list)
                    ###########################################
                    rlist, wlist, xlist = select.select([self.server_socket] + self.clients.get_sockets(), self.clients.get_sockets(), [], 0.01)
                    self.send_waiting_messages(wlist)
                    for chat_id in self.get_column_from_db("id", self.db["chats"]):
                        chat = self.db["chats"].get(chat_id)
                        if chat["user_id"] == current_id:
                            print("hello")
                            print (str(current_id))
                            chat_id = chat_id
                            external_id = chat["external_id"]
                            chat_name = chat["name"]
                            contacts = chat["contacts"]
                            self.msg_maker(f"new chat+*!?{chat_id}+*!?{external_id}+*!?{chat_name}+*!?{contacts}", list)
                    ##########################################

                    return True
                current_id = current_id + 1
            except NotFoundError:
                self.msg_maker("try again", list)
                return False


    def check_client_exit(self, data):
        if len(data.split(b'+*!?')) == 2:
            tmp = data.split(b'+*!?')
            if tmp[1] == b'NAK':
                #print(tmp[0].decode("utf-8") + " has logedout")
                self.clients.remove_client(tmp[0].decode('utf-8'))
                #print('exit client: ', tmp[0].decode('utf-8'))
                return False
        return True

    def do_decrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.decrypt(data)

    def do_encrypt(self, key, data):  # the params are byte object. return byte object
        if isinstance(data, str):
            data = data.encode()
        f = Fernet(key)
        return f.encrypt(data)
    def update_db_after_client_NAK(self, data):
        if len(data) > 2:
            data = data[2:]
            for i, dt in enumerate(data):
                if i % 2 == 0:
                    chat_id = int(dt)
                    new_msgs = int(data[i + 1])
                    self.db["chats"].update(chat_id, {"new_msgs": new_msgs})
    def decifer(self, data, current_socket):
        '''___TODO___'''
        #print('enter decifer')
        if data.split(b'+*!?')[0].decode('utf-8') == 'NAK':
            data = data.decode('utf-8').split("+*!?")
            print(f"NAK data: {data}")
            username = data[1]
            self.update_db_after_client_NAK(data)
            self.clients.remove_client(username)
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

        elif data.split(b'+*!?')[0].decode('utf-8') == "files_request":
            chat_id = data.split(b'+*!?')[1].decode('utf-8')
            self.hendle_file_request(chat_id)

        elif data.split(b'+*!?')[0].decode('utf-8') == "get_file_value":
            print("ttl")
            tmp = data.split(b'+*!?')
            chat_id = tmp[1]
            file_id = tmp[2]
            self.send_file_to_client(chat_id, file_id)


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


            if command == "public_file":
                username = temp[1].decode("utf-8")
                socket_sender = self.clients.get_socket(username)
                msg_byte_object = temp[0] + b'+*!?' + temp[1] + b'+*!?' + temp[2]
                self.send_messages_without_sender(msg_byte_object, socket_sender)

            if command == "create chat":
                print("here")
                temp = data.decode('utf-8').split('+*!?')
                chat_name = temp[1]
                contacts = temp[2].split(",")#the self username
                self.create_new_chat(chat_name, contacts)
            if command == "chat request":
                temp = data.decode('utf-8').split('+*!?')
                chat_id = temp[1]
                external_id = temp[2]
            #sends all the msgs in this chat
                msgs = self.db["chats"].get(chat_id)["msgs"]
                self.db["chats"].update(chat_id, {"new_msgs": 0})
                #user_id = self.db["chats"].get(chat_id)["user_id"]
                #username = self.db["users"].get(user_id)["username"]
                #print(f"user_id: {user_id}\nusername{username}\nself.clients.get_usernames(){self.clients.get_usernames()}")
                msg_to_send = f"private+*!?+*!?{chat_id}+*!?{msgs}"
                sockets_list_to_send = []
                sockets_list_to_send.append(current_socket)
                self.msg_maker(msg_to_send, sockets_list_to_send)
        elif len (data.split(b'+*!?')) == 4:
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
                #socket_sender = self.clients.get_socket(username)
                self.save_file_in_db(file, file_name, username, chat_id)  #  , file, file_name, username, chat_id)

                # check if I saved the file in db
                f = self.db["files"].get(1)["value"]
                print("this is f",f)




        elif len(data.split(b'+*!?')) == 5:
            # this is a private msg condition
            data = data.decode('utf-8')
            # save the new msgs in db---
            self.save_msg_in_db1(data)
            #---------------------------
            data = data.split("+*!?")
            command = data[0]
            sender_username = data[1]
            sender_chat_id = data[2]
            external_id = data[3]
            msg = data[4]

            manager = False
            sender_id = ""
            for i in self.get_column_from_db("id", self.db["users"]):
                if self.db["users"].get(i)["username"] == sender_username:
                    sender_id = str(i)
            managers = self.db["chats"].get(int(sender_chat_id))["managers_id"].split(",")
            if sender_id in managers:
                manager = True
            linker_two_id = None
            linker_username_two = None
            managers_ids = self.db["chats"].get(int(sender_chat_id))["managers_id"]
            managers_ids = managers_ids.split(',')
            #SENDS THE MSG TO THE CHAT CONTACTS AND TO SAVE IT IN THE DB
            list_of_sockets_to_send = []
            #list_of_contacts = self.get_list_of_contacts(external_id)
            list_of_contacts = self.db["chats"].get(sender_chat_id)["contacts"].split(',')
            _list_of_contacts = list_of_contacts
            print(f"list of contacts = {list_of_contacts}")
            contacts_with_linked = list_of_contacts
            for _id in self.get_column_from_db("id", self.db["chats"]):
                if self.db["chats"].get(_id)["is_linked"] and str(self.db["chats"].get(_id)["external_id"]) == external_id:
                    username = self.db["users"].get(self.db["chats"].get(_id)["user_id"])["username"]
                    contacts_with_linked .append(username)
            all_ids_in_users = self.get_column_from_db("id", self.db["users"])
            ids_to_send = []
            usernames_to_send = []
            for contact in contacts_with_linked :
                if contact in self.clients.get_usernames():
                    for current_id in all_ids_in_users:
                        if self.db["users"].get(current_id)["username"] == contact:
                            ids_to_send.append(current_id)
                            usernames_to_send.append(contact)
                            break
            list_of_contacts = _list_of_contacts
            print(f"1sender_username = {sender_username}    ,list_of_contacts = {list_of_contacts}")
            linker_username_two_is_manager = False
            is_sender_linked: bool = False
            linker_username = None
            linker_is_manager = False
            print(f"2sender_username = {sender_username}    ,list_of_contacts = {list_of_contacts}")
            if sender_username not in list_of_contacts:
                is_sender_linked = True
                linker = self.db['users'].get(self.db["chats"].get(int(sender_chat_id))["linker_id"])
                linker_username = linker["username"]
                linker_id = self.db["chats"].get(int(sender_chat_id))["linker_id"]
                if linker_id in managers:
                    linker_is_manager = True

            #now the usernames and the ids orgenized
            for i in range(len(usernames_to_send)):
                username = usernames_to_send[i]
                id_of_username = ids_to_send[i]
                if username != sender_username:
                    socket = self.clients.get_socket(username)
                    sockets = [socket]
                    print("self.get_column_from_db('id',self.db['chats']) = "+str(self.get_column_from_db("id",self.db["chats"])))
                    c = None
                    for id in self.get_column_from_db("id",self.db["chats"]):
                        if str(self.db["chats"].get(id)["user_id"]) == str(id_of_username) and str(self.db["chats"].get(id)["external_id"]) == str(external_id):
                            c = id
                            break
                    is_user_linked = True
                    if username in list_of_contacts:
                        is_user_linked = False

                    if is_user_linked and is_sender_linked:
                        for _id in self.get_column_from_db("id", self.db["user"]):
                            if self.db["users"].get(_id)["username"] == username:
                                id_of_username = _id
                                break
                        for i in self.get_column_from_db("id", self.db["chats"]):
                            chat = self.db["chats"].get(i)
                            if id_of_username == chat["user_id"] and str(chat["external_id"]) == external_id:
                                linker_two_id = chat["linker_id"]
                                linker_username_two = self.db["users"].get(linker_two_id)
                                break

                        if linker_two_id in managers:
                            linker_username_two_is_manager = True

                        if linker_is_manager :
                            linker_username = "@"+linker_username
                        if linker_username_two_is_manager:
                            linker_username_two = "@"+linker_username_two
                        self.msg_maker(f"private+*!?[{linker_username_two}][{linker_username}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                    print(f"is_user_linked= {is_user_linked}\nis_sender_linked= {is_sender_linked}")
                    if is_user_linked == False and is_sender_linked:
                        if linker_is_manager :
                            self.msg_maker(f"private+*!?[@{linker_username}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                        else:
                            self.msg_maker(f"private+*!?[{linker_username}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                    if is_user_linked and not is_sender_linked:
                        if linker_username_two_is_manager:
                            self.msg_maker(f"private+*!?[@{linker_username_two}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                        else:
                            self.msg_maker(f"private+*!?[{linker_username_two}]{sender_username}+*!?{c}+*!?{msg}", sockets)
                    else:
                        if manager:
                            self.msg_maker(f"private+*!?@{sender_username}+*!?{c}+*!?{msg}", sockets)
                        else:
                            self.msg_maker(f"private+*!?{sender_username}+*!?{c}+*!?{msg}", sockets)

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
        for _id in self.get_column_from_db('id', self.db["users"]):
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
                    self.msg_maker("new chat+*!?" + str(self.last_id) + "+*!?" + str(chat_external_id) + "+*!?" + linked_chat_name + "+*!?" + contacts + "+*!?" + "1", list_client)
                    #print("sent after it=>"+"new chat%%%" + str(self.last_id) + "%%%" + str(random_external_id) + "%%%" + chat_name + "%%%" + contacts + "%%%" + new_chat_msg)
                self.last_id = self.last_id + 1


    def messages_connected(self,socket):
        big_data = self.clients.get_big_data_by_socket(socket)
        key = self.clients.get_key_by_socket(socket)
        print(f"my big big big data = {big_data}")
        # self.big_data = self.big_data
        msg_split1 = big_data.split("End_Seg".encode())
        print(f"len = {len(msg_split1)}, list = {msg_split1}")
        wanted_list = []
        for i in range(len(msg_split1)-1):
            mini_part = msg_split1[i]
            mini_part = mini_part.split("Start_Seg".encode())[1]
            # print(f"mini_part = {mini_part}")
            #key = mini_part.split("%%%")[0]
            data = mini_part#.split("%%%")[1]
            mini_part = self.do_decrypt(key, data)
            wanted_list.append(mini_part)
        self.clients.set_big_data_by_socket(socket, msg_split1[len(msg_split1)-1])
        print(wanted_list)
        return wanted_list









    def send_messages_without_sender(self, message, sender):
        orgi_msg = message
        for client_socket in self.clients.get_sockets():
            if not client_socket == sender:
                #key = Fernet.generate_key()  # generates new key (bytes object) randomly
                # message = key.decode() + "%%%" + self.do_encrypt(key, orgi_msg.encode()).decode()
                key = self.clients.get_key_by_socket(client_socket)
                if isinstance(orgi_msg, str):
                    message = self.do_encrypt(key, orgi_msg.encode()).decode()
                elif isinstance(orgi_msg, bytes):
                    message = self.do_encrypt(key, orgi_msg).decode()
                message = "Start_Seg" + message + "End_Seg"
                client_socket.send(message.encode('utf-8'))
                #print(f"id{client_socket} :" + message)
                #print(self.clients.get_username(client_socket))

    def send_message_clients(self, message, clients):
        for client in self.clients.get_sockets():
            if client in clients:
                client.send(message.encode('utf-8'))

    def signup_process(self, data, curret_socket, wlist):
        '''__TODO__ SEND THIS PARAMS TO THE DATABASE'''
        '''THE PROTOCLOL IS SIMPLE <EMAIL>%%%<USERNAME>%%%<HASHED PASSWORD>'''
        arr = data.split(b'+*!?')
        email = arr[0].decode()
        username = arr[1].decode()
        hashed_pass = arr[2].decode()
        #print("username= ", username, 'email= ', email, "hashed_pass= ", hashed_pass)
        boolean = self.save_new_user_to_database(curret_socket, email, username, hashed_pass)
        if boolean == True:
            self.send_waiting_messages(wlist)
            #print("dict before :", self.open_client_sockets)
            # self.open_client_sockets.__delitem__(curret_socket)
            #print("dict after :", self.open_client_sockets)



    def remove_client_from_chat(self, username, _chat_external_id, _chat_id):
        if _chat_id == 'public' or _chat_external_id == "public":
            return
        chat_ids = self.get_column_from_db("id", self.db["chats"])
        contacts_in_chat_before_remove = self.db["chats"].get(_chat_id)["contacts"].split(",")
        contacts_in_chat_before_remove.remove(username)

        contacts_in_chat_after_remove = ','.join(contacts_in_chat_before_remove)
        msg_to_save = f"private+*!?Server+*!?{_chat_id}+*!?{_chat_external_id}+*!?{username} left"
        self.save_msg_in_db1(msg_to_save)
        for chat_id in chat_ids:
            chat = self.db["chats"].get(chat_id)
            if str(chat['external_id']) == _chat_external_id:
                chat.update({"contacts": contacts_in_chat_after_remove})
                if self.db["users"].get(chat["user_id"])["username"] in self.clients.get_usernames() and self.db["users"].get(chat["user_id"])["username"] != username:
                    msg_to_send = f"private+*!?Server+*!?{chat_id}+*!?{username} left"
                    self.msg_maker(msg_to_send, [self.clients.get_socket(self.db["users"].get(chat["user_id"])["username"])])
            if str(chat['id']) == _chat_id:
                self.db["chats"].delete(chat_id)
                break

    def send_info_request(self, chat_id):
        user_chat = self.db["chats"].get(int(chat_id))
        name = self.db["users"].get(user_chat["user_id"])["username"]
        sock = [self.clients.get_socket(name)]
        external_id = user_chat["external_id"]
        is_linked =  user_chat["is_linked"]
        print("z")
        is_manager = False
        user_id = str(user_chat["user_id"])
        _managers = user_chat["managers_id"].split(',')
        _contacts = user_chat["contacts"]
        contacts = user_chat['contacts'].split(',')
        num_of_contacts = len(contacts)
        managers = ""
        print("k")
        for mng in _managers:
            managers = managers+","+self.db["users"].get(int(mng))["username"]
        m = managers.split(',')
        m = m[1:]
        i=0
        for mm in m :
            m[i] = "@"+mm
            i+=1
        m= ','.join(m)
        print(m )
        if user_id in managers:
            is_manager = True
        users_he_linked = ""
        print(f"is_manager = {is_manager}")
        for chat_id in self.get_column_from_db("id", self.db["chats"]):
            chat = self.db["chats"].get(chat_id)
            if chat["is_linked"] and str(chat["linker_id"]) == user_id and chat["external_id"] == external_id:
                username = self.db["users"].get(chat["user_id"])['username']
                users_he_linked = users_he_linked+","+username
        users_he_linked = ','.join(users_he_linked.split(',')[1:])

        msg = f"chat info+*!?{is_manager}+*!?{is_linked}+*!?{num_of_contacts}+*!?{users_he_linked}+*!?{_contacts}+*!?{m}"
        print('t')
        self.msg_maker(msg,sock)
        print("c")

    def save_file_in_db(self, file, file_name, username, chat_id):
        chat_id = int(chat_id)
        self.db['files'].insert({"id": self.last_file_id, "name": file_name, "value": file, "username_of_sender": username})
        external_id = self.db["chats"].get(chat_id)["external_id"]
        #todo: to update the files in the chats
        for _id in self.get_column_from_db("id", self.db['chats']):
            chat = self.db["chats"].get(chat_id)
            if chat["external_id"] == external_id:

                files = chat["files_ids"]
                if not files:
                    self.db['chats'].update(_id, {"files_ids": f"{self.last_file_id}"})
                else:
                    self.db['chats'].update(_id,{"files_ids": f"{self.last_file_id},{files}"})
        self.last_file_id += 1

    def hendle_file_request(self, chat_id):
        chat = self.db["chats"].get(int(chat_id))
        files_ids = chat["files_ids"]
        ids = files_ids.split(',')
        senders = ''
        file_names = ''
        for file_id in ids:
            print("file_id=",file_id)
            if file_id != '':
                f = self.db["files"].get(int(file_id))
                file_names += f["name"]+","
                senders += f["username_of_sender"]+","
        file_names = file_names[:-1]
        senders = senders[:-1]
        msg = f"files_in_chat+*!?{files_ids}+*!?{file_names}+*!?{senders}"
        sock = [self.clients.get_socket(self.db["users"].get(chat['user_id'])['username'])]
        self.msg_maker(msg, sock)

    def send_file_to_client(self, chat_id, file_id):
        chat_id = int(chat_id)
        file_id = int(file_id)
        f = self.db["files"].get(file_id)
        file_name = f["name"]
        value = f["value"]
        msg_byte_object = (f"public_file+*!?+*!?{file_name}$$$").encode()+value
        sock = [self.clients.get_socket(self.db["users"].get(self.db["chats"].get(chat_id)["user_id"])['username'])]
        self.msg_maker(msg_byte_object, sock)

Server().run()
