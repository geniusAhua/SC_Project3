import base64
import enum
import os
import socket
import threading
import sys
import time
import asyncio
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit.application import run_in_terminal
from math import ceil

Dictionary = {
              'SEND_SHORTNAME': 'tiliu3', #send your device name
              'NO_USER': 'This connection is not found. Please check the route table.'
             }

# COMMAND = {
#     'OPEN_PORT': 'open-port', #open socket listener
#     'HELP': 'help'
# }

class Command():
    OPEN_NET = 'open-net'
    HELP = 'help'
    SHOW_MSG = 'show-msg'
    SHUT_SHOW_MSG = 'shut show-msg'

    @staticmethod
    def not_found(input):
        print(f'Command "{input}" not found')

class _Prompt():
    __cli_header = f'ndn-cli:{Dictionary["SEND_SHORTNAME"]}'
    @staticmethod
    def begining():
        return _Prompt.__cli_header + ' >'
    
    @staticmethod
    def running_bind():
        return _Prompt.__cli_header + '-running >'

class Demo():

    def __init__(self):
        self.__host = self.__get_host_ip()
        self.__port = 33000
        self.__shortname = Dictionary['SEND_SHORTNAME']
        self.__host_target = '10.6.57.217'
        self.__port_target = 33000
        self.__Sem_conn_change = threading.Semaphore(1)
        self.__Sem_conns = threading.Semaphore(3) # the maximum number of connections is 4/最大连接数量为4
        self.__socket_pool = {}
        self.__background_tasks = []
        self.__isShow_msg = False

    def __get_host_ip(self):
        """
        Inquire IP address:
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip
    
    def __addConnection(self, shortname, sock):
        with self.__Sem_conn_change:
            self.__socket_pool[shortname] = sock

    def __deleteConnection(self, shortname):
        with self.__Sem_conn_change:
            sock = self.__socket_pool[shortname]
            if sock:
                sock.close()
                self.__socket_pool.remove(shortname)
            else:
                print(Dictionary['NO_USER'])

    def __echo(self, text):
        with patch_stdout():
            if self.__isShow_msg:
                print(text)
            else: return

    def __Console(self, sock, addr, src_addr):
        with self.__Sem_conns:
            try:
                self.__echo('set connection: source address %s:%s' %addr + ' --- destination address %s:%s'  %src_addr )
                #when first accept the connection, we need save the shortname of the device
                isLoop = False
                data = sock.recv(1024)
                data = base64.b64decode(data).decode()
                if data.split(':')[0] == 'SHORTNAME':
                    shortname = data.split(':')[1]
                    self.__echo(shortname + "has connected to this device")
                    #append the connection in socket pool
                    self.__addConnection(shortname, sock)
                    message = base64.b64encode(f'SHORTNAME:{Dictionary["SEND_SHORTNAME"]}'.encode())
                    sock.send(message)
                    isLoop = True
                else:
                    isLoop = False
                    self.__echo(f"illegal connection! ==> {data}")
                    return
                while isLoop:
                    if(getattr(sock, '_closed') == True):
                        self.__echo('Connection terminate: source: ' + shortname + ' --- %s:%s' %addr + ' --- destination: %s:%s' %src_addr)
                        break
                    # data = sock.recv(1024)
                    # if not data:
                    #     sock.close()
                    #     break
                    # print(shortname + '>>' +data.decode())
                    # command = data[:4].decode()
                
                self.__deleteConnection(shortname)
                self.__echo('==================================================')
                return
            except ConnectionResetError:
                self.__echo('A peer client suddenly disconnected')
                self.__deleteConnection(shortname)
                return

    def __send(self, shortname, text):
        sock = self.__socket_pool[shortname]
        if sock:
            sock.send(text)
        else:
            print(Dictionary['NO_USER'])

    
    
    def __maintain_listen(self, socket_, src_addr):
        while True:
            sock_,addr_ = socket_.accept()
            try:
                print(f'new connection: {addr_}')
                t = threading.Thread(target = self.__Console, args = (sock_,addr_,src_addr))
                t.setDaemon(True)
                t.start()
            except:
                print ("Error: Failed to create a new thread")

    
    def __listen_host(self):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("IP address of current device: " + self.__host)
        src_addr = (self.__host, self.__port)
        socket_.bind(src_addr)
        #set the num of wating connection application
        socket_.listen(0)
        print('======================start=======================')
        print('                service is running...')
        print('=======================end========================')

        # to maintain listening the host
        maintain_listen = threading.Thread(target = self.__maintain_listen, args = (socket_, src_addr))
        maintain_listen.setDaemon(True)
        maintain_listen.start()

    def do_recieve_from(self, shortname):
        sock = self.__socket_pool[shortname]
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    sock.close()
                    break
                print(shortname + '>>' +data.decode())
                command = data[:4].decode()

        except ConnectionResetError:
            print('A peer client suddenly disconnected')
            self.__deleteConnection(shortname)
            return

        except BrokenPipeError:
            print("Connection was broken.")
            self.__deleteConnection(shortname)
            return

    def __do_showMsg(self):
        self.__isShow_msg = True

    def __do_shut_showMsg(self):
        self.__isShow_msg = False


    


    async def __print_msg(self, task):
        try:
            await task()
        except asyncio.CancelledError:
            print(f"{self.__shortname}: this chat-listener cancelled")
            return

    async def __cli_input(self):
        #add a key binding to quit the cli
        isLoop = True
        kb = KeyBindings()
        @kb.add('escape')
        async def _(event):
            print("quit cli")
            nonlocal isLoop
            isLoop = False
            event.app.exit()

        #welcom text
        welcom_text = "Welcom to use ndn cli.\nYou can press 'escape' or 'Control + c' to quit.\n"
        print(welcom_text)
        #Create Prompt
        session = PromptSession()
        prompt = _Prompt.begining
        #Run echo loop.
        while isLoop:
            try:
                command = await session.prompt_async(prompt, key_bindings = kb)
                if command == Command.OPEN_NET:
                    self.__listen_host()
                    prompt = _Prompt.running_bind

                elif command == Command.SHOW_MSG:
                    self.__do_showMsg()
                
                elif command == Command.SHUT_SHOW_MSG:
                    self.__do_shut_showMsg()
                    
                else:
                    Command.not_found(command)

            except (EOFError, KeyboardInterrupt):
                return

    async def __main(self):
        with patch_stdout():
            # for recver in self.__recvers:
            #     bct = asyncio.create_task(self.__print_msg(task_recv, recver))
            #     background_tasks.append(bct)
            try:
                #await send task
                await self.__cli_input()
            finally:
                #cancell background tasks
                for bct in self.__background_tasks:
                    bct.cancel()
            print("Quitting CLI. Bye.")

    def run(self):
        try:
            from asyncio import run
        except ImportError:
            asyncio.run_until_complete(self.__main())
        else:
            asyncio.run(self.__main())

if __name__ == '__main__':
    os.system('clear')
    demo = Demo()
    demo.run()
