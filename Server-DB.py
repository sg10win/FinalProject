import socket
import sqlite3
import select
import datetime


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
        self.conn = sqlite3.connect('users_01.db')
        print("opened database successfully")
        self.database_reset_temp()  # res
        self.all_client_seckets = {}
        self.open_client_sockets = {}
        self.messages = []
        self.managing_client_sockets = []
        self.denied_clients = []
        self.private_conversation = []

        self.clients = ListClients()

    def database_reset_temp(self):
        try:
            self.conn.execute('''DROP TABLE USERS;''')
        except:
            print("there is no table USERS")
        self.conn.execute('''CREATE TABLE USERS 
        (
        email               TEXT        NOT NULL,
        username            TEXT        NOT NULL,
        hashed_password     TEXT        NOT NULL);''')
        print("table created successfully")
        self.conn.execute(
            '''INSERT INTO USERS (email, username, hashed_password) VALUES ('segevshalom86@gmail.com','segev10','0b4e7a0e5fe84ad35fb5f95b9ceeac79');''')
        self.conn.execute(
            '''INSERT INTO USERS (email, username, hashed_password) VALUES ('dshalom01@gmail.com','dshalom01','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.close()

    def msg_maker(self, data, list_of_sockets_to_send,
                  type):  # the type is 's'-signup, 'l'-login, 'm'-msg, **'f'-file**
        print(data)
        # if type is "s":
        # data = "s"+data
        # if type is "l":
        # data = "l"+data
        # if type is "m":
        # data = "m"+data
        msg = data, list_of_sockets_to_send
        self.messages.append(msg)

        # this method adds a msg to send about whats wrong with the params if it is and return true if the process done and false if not

    def save_new_user_to_database(self, socket, email, username, hashed_password):
        cursor = self.conn.execute('''SELECT email,username FROM USERS;''')
        list = []
        list.append(socket)
        for row in cursor:
            if email == row[0] and row[1] == username:
                self.msg_maker("This email and username are\n currently in use", list, 's')
                return False
            if email == row[0]:
                self.msg_maker("This email is currently in use", list, 's')
                return False
            if row[1] == username:
                self.msg_maker("This username is currently in use", list, 's')
                return False

        email = "'" + email + "'"
        username = "'" + username + "'"
        hashed_password = "'" + hashed_password + "'"
        self.conn.execute(
            "INSERT INTO USERS (email, username, hashed_password) VALUES (" + email + ',' + username + ',' + hashed_password + ");")
        cursor = self.conn.execute('''SELECT email,username,hashed_password FROM USERS;''')
        print("database after adding ")
        for row in cursor:
            print(row)
        self.msg_maker("signed in successfully", list, 's')
        print(self.messages)
        return True

    def run(self):
        print("server started")
        while True:
            # aaa = [self.server_socket] + list(self.open_client_sockets.keys())
            aaa = [self.server_socket] + self.clients.get_sockets()
            # rlist, wlist, xlist = select.select(aaa, list(self.open_client_sockets.keys()), [])
            rlist, wlist, xlist = select.select(aaa, self.clients.get_sockets(), [])
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
                    self.send_waiting_messages(wlist)

    def send_waiting_messages(self, wlist):
        for message in self.messages:
            (data, current_sockets) = message
            # for client_socket in list(self.open_client_sockets.keys()):
            for client_socket in self.clients.get_sockets():
                if client_socket in current_sockets and client_socket in wlist:

                    msg_to_send = data.encode('utf-8')
                    client_socket.send(msg_to_send)
                    current_sockets.remove(client_socket)
                    message = (current_sockets, data)
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
        cursor = self.conn.execute('''SELECT username,hashed_password FROM USERS;''')
        for row in cursor:
            if username == row[0] and hashed_pass == row[1]:
                self.msg_maker("loged-in", list, "l")
                return True
        self.msg_maker("try again", list, "l")
        return False

    def check_client_exit(self, data):
        if len(data.split(b'%%%')) == 2:
            tmp = data.split(b'%%%')
            if tmp[1] == b'NAK':
                print(tmp[0].decode("utf-8") + " has logedout")
                self.clients.remove_client(tmp[0].decode('utf-8'))
                print('exit client: ', tmp[0].decode('utf-8'))
                return False
        return True

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
            temp = data.decode('utf-8').split("%%%")
            command = temp[0]
            username = temp[1]
            # msg = temp[2]
            # temp = str(temp[1] + temp[2])
            data = data.split(b'%%%')
            # data type identifier
            if command == "public":
                socket_sender = self.clients.get_socket(username)
                msg = command + '%%%' + username + '%%%' + temp[2]
                self.send_messages_without_sender(msg, socket_sender)
                # sender = data[1].decode()
                # msg = data[2]
                # self.messages.append(temp, self.open_client_sockets.keys())

    def send_messages_without_sender(self, message, sender):
        for client_socket in self.clients.get_sockets():
            if not client_socket == sender:
                client_socket.send(message.encode('utf-8'))

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
