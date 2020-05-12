import hashlib
import select
import socket
import sys
import time
from queue import Queue
from datetime import datetime

from Encryption import *


class Client(object):
    def __init__(self, ip='127.0.0.1', port=8080):
        self.ip = ip
        self.port = port

        self.my_socket = None
        self.r_list = []
        self.w_list = []
        self.x_list = []
        self.key = None
        self.is_end = False

        self._connect_to_server()

        self.username = None
        self.password = None
        self.local_username = 'You'

        self.message_q = Queue()
        self.messages_to_send = []
        self.big_data = ''

        self.current_id = 'public'
        self.current_external_id = 'public'
        self.current_chat_name = 'public'
        self.is_private = False
        self.mode = 'ENABLE'
        self.chat_id = None

        self.documents_folder = "downloads/"

    def _connect_to_server(self):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect((self.ip, self.port))
        print('connect to server just socket')
        self.key = self.my_socket.recv(1024).decode('utf-8').encode()
        print(f"got key{self.key.decode()}")

    def _send_messages(self):
        for message in self.messages_to_send:
            if self.w_list is not []:
                data = f"Start_Seg{Encryption.encrypt(message, self.key).decode()}End_Seg"
                self.my_socket.send(data.encode('utf-8'))
                self.messages_to_send.remove(message)

    def get_username_and_password(self):
        self.username = input('enter username')
        self.password = input('enter password')
        return self.username, self.password

    def _log_in(self):
        username, password = self.get_username_and_password()
        hashed_password = (hashlib.md5(password.encode())).hexdigest()
        msg_to_server = username + "+*!?" + hashed_password
        self.messages_to_send.append(msg_to_server)

    def get_username_passwords_and_mail(self):
        email = input('enter email')
        username = input('enter username')
        password = input('enter password')
        re_password = input('enter re_password')
        return username, password, re_password, email

    def _sign_up(self):
        temp = self.get_username_passwords_and_mail()
        if temp:
            username, password, re_password, email = temp
            if password == re_password and username != "" and email != "" and password != "" and re_password != "":
                hashed_password = (hashlib.md5(password.encode())).hexdigest()
                msg_to_server = email + "+*!?" + username + "+*!?" + hashed_password
                self.messages_to_send.append(msg_to_server)

    def signed_up(self):
        print("signup process done")
        pass

    def failed_sign_up(self, command):
        print(command.decode('utf-8'))

    def loged_in(self):
        print('log in')

    def failed_log_in(self):
        print('failed log in')

    def get_username(self):
        return input('enter username')

    def get_password(self):
        return input('enter password')

    def get_re_password(self):
        return input('enter re password')

    def get_email(self):
        return input('enter email')

    def _signed_up(self):
        pass

    def _got_public_message(self, message):
        print("got public message")
        if self.current_id == "public" and self.mode == "ENABLE":
            sender = message[1].decode()
            message = message[2].decode()
            message = f"{sender}: {message}"
            self.got_public_message(message)

    def got_public_message(self, msg):
        print(msg)

    def _public_mode(self):
        self.mode = 'ENABLE'
        self.current_id = "public"
        self.current_external_id = "public"
        self.current_chat_name = "public"

        self.public_mode()

    def public_mode(self):
        print('public mode')

    def _disable(self):
        self.mode = "DISABLE"

        self.disable()

    def disable(self):
        pass

    def _got_private_message(self, message):
        print("got private message")
        sender = message[1].decode()
        self.chat_id = message[2].decode()
        msg = message[3].decode()
        print(f"username = {sender}, chat_id = {self.chat_id}, msg = {msg}")
        message_to_display = f"{sender}: {msg}"
        if self.current_id == self.chat_id and self.mode == "ENABLE":
            print(message_to_display)
            # to play the sound
        else:
            print(f'got message = {message_to_display}| but DISABLE or not in the same chat')
            # the Buttons object
        self.got_private_message(message)

    def got_private_message(self, message):
        pass

    def _choose_file(self, file_path, file_name):
        if file_path != '':
            print(file_path)
            with open(file_path, 'rb') as f:
                contents = f.read()
                f.close()
            file_msg = (f"private_file+*!?{self.current_id}+*!?" + self.username + f"+*!?{file_name}$$$") \
                           .encode() + contents
            msg_to_send = f"private+*!?{self.username}+*!?{self.current_id}+*!?{self.current_external_id}+*!?" \
                          f"sent a file {file_name}"

            self.messages_to_send.append(file_msg)
            self.messages_to_send.append(msg_to_send)


    def choose_file(self):
        pass

    def _emoji_options(self):
        msg = f"files_request+*!?{self.current_id}"
        self.messages_to_send.append(msg)

    def emoji_options(self):
        self._emoji_options()

    def _got_chat_info(self, message):
        print("got chat info message")
        is_manager = message[1].decode()
        is_linked = message[2].decode()
        num_of_contacts = message[3].decode()
        users_he_linked = message[4].decode()
        contacts = message[5].decode()
        managers = message[6].decode()
        is_private = message[7].decode()
        self.got_chat_info(is_manager, is_linked, num_of_contacts, users_he_linked, contacts, managers, is_private)

    def got_chat_info(self, is_manager, is_linked, num_of_contacts, users_he_linked, contacts, managers, is_private):
        pass

    def _got_new_chat(self, message):
        print("got new chat message")
        chat_id = message[1].decode()
        external_id = message[2].decode()
        chat_name = message[3].decode()
        contacts = message[4].decode()
        new_msgs = message[5].decode()
        is_private = message[6].decode()
        self.got_new_chat(chat_id, external_id, chat_name, contacts, new_msgs, is_private)

    def got_new_chat(self, chat_id, external_id, chat_name, contacts, new_msgs, is_private):
        pass

    def _got_files_in_chat(self, message):
        print("got files in chat message")
        ids = message[1].decode()
        files_names = message[2].decode()
        senders = message[3].decode()

        self.got_files_in_chat(ids, files_names, senders)

    def got_files_in_chat(self, ids, file_names, senders):
        pass


    def _got_files_request(self, message):
        print("got files request message")

    def got_files_request(self):
        pass

    def _got_private_file(self, message):
        splited = message[2]
        file_info = splited.split(b"$$$")
        file_name = file_info[0].decode('utf-8')[10:]  # with out the time part because it is unvalid
        file = file_info[1]
        print("downloading file")
        with open(file_name, 'wb') as f:
            f.write(file)
            f.close()

    def get_msg(self):
        return input('enter msg')

    def _send(self):
        message = self.get_msg()
        msg_to_send = ''
        if self.mode == 'ENABLE':
            if self.current_id == "public":  # in public chat ...
                msg_to_send = "public+*!?" + self.username + "+*!?" + message

            if self.current_id != "public":
                msg_to_send = f"private+*!?{self.username}+*!?{self.current_id}+*!?{self.current_external_id}+*!?" \
                              f"{message}"
            self.messages_to_send.append(msg_to_send)

    def open_new_chat_window(self):
        pass

    def _create_chat(self):
        self.open_new_chat_window()
        pass

    def client_exit(self):
        print('exit')


    def _client_exit(self):
        message = f"NAK+*!?{self.username}"
        self.messages_to_send.append(message)
        self._send_messages()
        self.client_exit()
        self.my_socket.close()
        self.is_end = True



    def _enter_command(self):
        command = input('enter command')
        if command == 'log in':
            self._log_in()
        if command == 'sign up':
            self._sign_up()
        if command == 'send':
            self._send()
        if command == 'create chat':
            self._create_chat()

    def show_message(self, message):
        print(message)

    def _messages_connected(self):
        # print(f"my big big big data = {self.big_data}")
        # msg_split1 = self.big_data.split("End_Seg")
        # print(f"len = {len(msg_split1)}, list = {msg_split1}")
        #
        # for i in range(len(msg_split1) - 1):
        #     mini_part = msg_split1[i]
        #     mini_part = mini_part.split("Start_Seg")[1]
        #     print(f"mini_part = {mini_part}")
        #     data = mini_part
        #     mini_part = Encryption.decrypt(data.encode(), self.key)
        #     self.message_q.put(mini_part)
        # self.big_data = msg_split1[len(msg_split1) - 1]
        print(f"my big big big data = {self.big_data}")
        # self.big_data = self.big_data
        msg_split1 = self.big_data.split("End_Seg")
        print(f"len = {len(msg_split1)}, list = {msg_split1}")

        for i in range(len(msg_split1) - 1):
            mini_part = msg_split1[i]
            mini_part = mini_part.split("Start_Seg")[1]
            print(f"mini_part = {mini_part}")
            # key = mini_part.split("%%%")[0]
            data = mini_part  # .split("%%%")[1]
            mini_part = Encryption.decrypt(data.encode(), self.key)
            self.message_q.put(mini_part)
        self.big_data = msg_split1[len(msg_split1) - 1]

    def _handle_message(self):
        msg = self.message_q.get()
        print(msg)
        split_msg = msg.split(b'+*!?')
        command = split_msg[0]
        print(f"command= {command}")
        if command == b'signed in successfully':
            self.signed_up()
        if command == b'This email and username are\n currently in use':
            self.failed_sign_up(command)
        if command == b'This email is currently in use':
            self.failed_sign_up(command)
        if command == b'This username is currently in use':
            self.failed_sign_up(command)
        if command == b'loged-in':
            self.loged_in()
        if command == b'try again':
            self.failed_log_in()
        if command == b'public':
            self._got_public_message(split_msg)
        if command == b'private':
            self._got_private_message(split_msg)
        if command == b'chat info':
            self._got_chat_info(split_msg)
        if command == b'new chat':
            self._got_new_chat(split_msg)
        if command == b'files_in_chat':
            self._got_files_in_chat(split_msg)
        if command == b'files_request':
            self._got_files_request(split_msg)
        if command == b'private_file':
            print("private filllellelel")
            self._got_private_file(split_msg)

    def _run(self):
        while True:
            self.r_list, self.w_list, self.x_list = select.select([self.my_socket], [self.my_socket], [])
            if self.my_socket in self.r_list:
                data = self.my_socket.recv(1024).decode('utf-8')
                self.big_data = self.big_data + data
                self._messages_connected()
                self._handle_message()

                if data == "":
                    print("connection closed")
                    self.my_socket.close()
                    return

            self._send_messages()
            time.sleep(0.2)
            if type(self) == Client:
                self._enter_command()
                time.sleep(0.25)

            if self.is_end:
                return

    @staticmethod
    def run(ip='127.0.0.1', port=8080):
        client = Client(ip=ip, port=port)
        client._run()






