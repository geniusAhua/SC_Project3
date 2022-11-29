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

from Generator import Generator
from CS import CS

from FIB import FIB
from PIT import PIT

Dictionary = {
              'NO_USER': 'This connection is not found. Please check the route table.',
              'USER_EXISTED': 'User has existed on socket.',
              'BROADCAST': 'BROADCAST',
              'GROUP': 'GROUP17',
             }

IP_table = {
    
}

class SendType():
    #The values of these variables must be as same as the end of private function
    CHAT = 'CHAT'
    INTEREST = 'INTEREST'
    DATA = 'DATA'

    def __init__(self, shortname, targetname):
        self.__shortname = shortname
        self.__targetname = targetname

    def __sendCHAT(self, param):
        package = {
            1: True,
            2: f"CHAT:{self.__targetname}//{self.__shortname}:{param}",
        }
        return package

    def __sendINTEREST(self, param):
        package = {
            1: True,
            2: f"INTEREST://{param}",
        }
        return package

    def __sendDATA(self, param):
        package = {
            1: True,
            2: f"DATA://{param}",#param = {dataname}:{data}
        }
        return package

    def __Default(self, param):
        package = {
            1: False,
            2: f"Can't send this type of packag: {param}",
        }
        return package

    def send_(self, type_, param):
        sendtype = "_SendType__send" + type_
        fun = getattr(self, sendtype, self.__Default)
        return fun(param)

class SensorType():

    def platform_car(self):
        return True

    def platform_truck(self):
        return True

    def platform_bike(self):
        return True

    def sensor_speed(self):
        return True

    def sensor_light(self):
        return True
    
    def sensor_proximity(self):
        return True
    
    def sensor_pressure(self):
        return True

    def sensor_wiper(self):
        return True

    def sensor_passenger(self):
        return True

    def sensor_fuel(self):
        return True

    def sensor_temperature(self):
        return True

    def Default(self):
        return False

    @staticmethod
    def sensor_isExist(param):
        type_ = "sensor_" + param
        fun = getattr(SensorType, type_, SensorType.Default)
        return fun(SensorType)

    @staticmethod
    def platform_isExist(param):
        type_ = "platform_" + param
        fun = getattr(SensorType, type_, SensorType.Default)
        return fun(SensorType)

class Command():
    SET_NAME = 'set-name'
    OPEN_NET = 'open-net'
    SHOW_MSG = 'show-msg'
    SHUT_SHOW_MSG = 'shut-show-msg'
    CHAT = 'chat'
    CONNECT = 'connect'
    SEARCH_CONN = 'search-conn'
    APPLY = 'apply'
    SHOWCS = 'show-cs'
    SHOWPIT = 'show-pit'
    SHOWFIB = 'show-fib'
    SET_GENERATOR = 'set-generator'

    @staticmethod
    def not_found(input):
        print(f'Command "{input}" not found.')

    @staticmethod
    def chat_success(target_name, text):
        print(f'You have sent to {target_name} - {text}')

    @staticmethod
    def chat_failed(target_name, text):
        print(f'There has something wrong to send to {target_name} - {text}')
    
    @staticmethod
    def connect_failed(target_name):
        print(f'There has something wrong to connect to {target_name}.')

class _Prompt():
    __cli_header = f'ndn-cli:'
    @staticmethod
    def begining(name = ''):
        _Prompt.__cli_header += str(name)
        return _Prompt.__cli_header + ' >'
    
    @staticmethod
    def running_bind():
        return _Prompt.__cli_header + '-running >'

class Demo():

    def __init__(self):
        self.__host = self.__get_host_ip()
        self.__host_broadcast = None
        self.__shortname = None
        self.__group = Dictionary['GROUP']
        self.__port_LAN = 33000
        self.__port_WAN = 33001
        self.__port_BROADCAST = 33002
        self.__recv_size = 2048#1024/2048/3072
        self.__isWAN_occupied = False
        self.__Sem_conn_change = threading.Semaphore(1)
        self.__Sem_conns = threading.Semaphore(3) # the maximum number of connections is 2/最大连接数量为2
        self.__Sem_IPT_change = threading.Semaphore(1)
        self.__Sem_PIT_change = threading.Semaphore(1)
        self.__Sem_CS_change = threading.Semaphore(1)
        self.__Sem_FIB_change = threading.Semaphore(1)
        self.__socket_pool = {}
        self.__isShow_msg = True
        self.__isShow_recv = True
        self.__isShow_bd = False
        self.__isRun_net = False
        self.__CS = CS()
        self.__PIT = PIT()
        self.__FIB = FIB()
        self.__Generator = None

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
        if shortname not in self.__socket_pool:
            with self.__Sem_conn_change:
                self.__socket_pool[shortname] = sock
        else:
            self.__echo(Dictionary['USER_EXISTED'])
            return False
        return True

    def __deleteConnection(self, shortname):
        if shortname in self.__socket_pool:
            sock = self.__socket_pool[shortname]
            if sock:
                sock.close()
                with self.__Sem_conn_change:
                    del self.__socket_pool[shortname]

    def __isRight_group(self, group):
        if group == self.__group:
            return True
        else: return False
    #debug for socket
    def __echo(self, text):
        with patch_stdout():
            if self.__isShow_msg:
                print(text)
            else: return
    #debug for broadcast
    def __echo_bc(self, text):
        with patch_stdout():
            if self.__isShow_bd:
                print(text)
            else: return
    #debug for recv message
    def __echo_recv(self, text):
        with patch_stdout():
            if self.__isShow_recv:
                print(text)
            else: return

    def __broadcast(self):
        try:
            broad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            broad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            broad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            host_broadcast = self.__host[::-1]
            host_broadcast = host_broadcast.replace(host_broadcast.split('.')[0], '552', 1)[::-1]
            # self.__host_broadcast = host_broadcast
            self.__host_broadcast = '255.255.255.255'
            broad.bind(("", self.__port_BROADCAST))
            self.__echo_bc(f'broadcast_ip: {host_broadcast}')
            isDie = [False]
            isLoop = False
            if self.__addConnection(Dictionary['BROADCAST'], broad) == True:
                t = threading.Thread(target = self.__broadcast_recv, args = (broad, isDie))
                t.setDaemon(True)
                t.start()
                isLoop = True

            while isLoop:
                time.sleep(3)
                if(isDie[0] == True):
                    self.__echo_bc(f'Socket of broadcast is closed <{self.__host_broadcast} - {self.__port_BROADCAST}>.')
                    break

        finally:
            broad.close()
            self.__deleteConnection(Dictionary['BROADCAST'])
        
    def __broadcast_ip(self):
        try:
            while True:
                if self.__shortname:
                    label = Dictionary['BROADCAST']
                    if label in self.__socket_pool:
                        broad = self.__socket_pool[label]
                        message = base64.b64encode(f'{self.__group}/SHORTNAME:{self.__shortname}'.encode())
                        broad.sendto(message, (self.__host_broadcast, self.__port_BROADCAST))
                        self.__echo_bc('IP has been broadcasted.')
                    else:
                        self.__echo_bc('There is no socket for socket.')
                    time.sleep(5)
        except Exception as e:
            self.__echo_bc(e)

    def __broadcast_recv(self, broad, isDie):
        try:
            while True:
                data, addr = broad.recvfrom(self.__recv_size)
                data = base64.b64decode(data).decode()
                self.__echo_bc(str(data) + ' ' + str(addr))
                t = threading.Thread(target=self.__process_bc, args=(data, addr))
                t.daemon = True
                t.start()
        except Exception as e:
            self.__echo_bc(e)
        finally:
            isDie[0] = True
            return

    def __process_bc(self, data, addr):
        conn_ip = addr[0]
        if(conn_ip != self.__host):
            header = data.split('/')[0]
            if self.__isRight_group(header):
                conn_name = data.split('/')[1].split(':')[1]
                if conn_name not in IP_table:
                    with self.__Sem_IPT_change:
                        IP_table[conn_name] = conn_ip
            else:
                self.__echo_bc(f"The connection - {conn_ip} is illegal.")

    def __search_conn(self):
        print('Searching connection.....')
        time.sleep(2)
        with self.__Sem_IPT_change:
            if len(IP_table) != 0:
                print('Connections are shown as below:')
                for name, ip in IP_table.items():
                    print(name)
                    self.__echo_bc(f'debug: {name} - {ip}')
            else:
                print('No connection has been found.')

    def __WAN_slot(self, target_name):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        src_addr = ("", self.__port_WAN)
        #Use a specific port to connect
        socket_.bind(src_addr)
        socket_.settimeout(3)

        try:
            isLoop = False
            isDie = [False]
            target = (IP_table[target_name], self.__port_LAN)
            socket_.connect(target)
            
            print(f'Trying to connect to {target_name}......')
            message = base64.b64encode(f'SHORTNAME:{self.__shortname}'.encode())
            socket_.sendall(message)
            data = socket_.recv(self.__recv_size)
            data = base64.b64decode(data).decode()

            if data.split(':')[0] == 'SHORTNAME':
                sendername = data.split(':')[1]
                if sendername == target_name:
                    self.__echo(f'Success to connect to {sendername}.')
                    #append the connection in socket pool
                    if self.__addConnection(target_name, socket_) == True:
                        isLoop = True
                        self.__isWAN_occupied = True
                        self.__FIB.add_nexthop_fib(target_name)
                        socket_.settimeout(None)
                        print(f"You have successfully connected to {target_name}")
                        t = threading.Thread(target = self.__receive, args = (socket_, sendername, isDie))
                        t.setDaemon(True)
                        t.start()
                    else:
                        isLoop = False
                        self.__isWAN_occupied = False
                else:
                    isLoop = False
                    self.__isWAN_occupied = False
                    self.__echo('The name of connection does not match, please check the IP_table!!!')
            else:
                isLoop = False
                self.__isWAN_occupied = False
                print(f'Device: <{target_name}>, is illegal. It cannot be connected')

            while isLoop:
                time.sleep(3)
                if(isDie[0] == True):
                    print('Connection terminate: source: ' + self.__shortname + ' --- destination: ' + sendername)
                    break
            
        except socket.timeout:
            print("connection timed out.")
        except ConnectionRefusedError:
            print(f'Failed to connect to {target_name}')
        finally:
            socket_.close()
            print("WAN slot is released now.")
            self.__isWAN_occupied = False
            if isDie[0]:
                self.__FIB.delete_nexthop_fib(target_name)
                self.__deleteConnection(target_name)
            else:
                socket_.close()

    def __LAN_slot(self, sock, addr, src_addr):
        with self.__Sem_conns:
            try:
                # self.__echo('set connection: source address %s:%s' %addr + ' --- destination address %s:%s'  %src_addr )
                #when first accept the connection, we need save the shortname of the device
                isLoop = False
                isDie = [False]

                data = sock.recv(self.__recv_size)
                data = base64.b64decode(data).decode()
                
                if data.split(':')[0] == 'SHORTNAME':
                    sendername = data.split(':')[1]
                    #append the connection in socket pool
                    if self.__addConnection(sendername, sock) == True:
                        print(sendername + " has connected to this device.")
                        message = base64.b64encode(f'SHORTNAME:{self.__shortname}'.encode())
                        sock.send(message)
                        isLoop = True
                        self.__FIB.add_nexthop_fib(sendername)
                        t = threading.Thread(target = self.__receive, args =(sock, sendername, isDie))
                        t.setDaemon(True)
                        t.start()
                    else:
                        isLoop = False
                        return
                else:
                    isLoop = False
                    self.__echo(f"illegal connection! ==> {data}")
                    return
                
                while isLoop:
                    time.sleep(3)
                    if(isDie[0] == True):
                        print('Connection terminate: source: ' + sendername + ' --- destination: ' + self.__shortname)
                        break
                return
            except ConnectionResetError:
                self.__echo('A peer client suddenly disconnected')
                return
            finally:
                #this token means whether the socket is added into socket pool.
                if isDie[0] == True:
                    self.__deleteConnection(sendername)
                    self.__FIB.delete_nexthop_fib(sendername)
                    text = '++++++++++++++++++++++++++++++++++++++++++++++++++\n'
                    text += f'        connection: {sendername} closed\n'
                    text += '++++++++++++++++++++++++++++++++++++++++++++++++++'
                    print(text)
                else:
                    sock.close()

    def __send(self, targetname, text, type_):
        send_filter = SendType(self.__shortname, targetname)
        if targetname in self.__socket_pool:
            sock = self.__socket_pool[targetname]
            pack = send_filter.send_(type_, text)
            if pack[1] == True:
                msg = pack[2]
                self.__echo(msg)
                msg = base64.b64encode(msg.encode())
                sock.sendall(msg)
            else:
                print(pack[2])
                return False
            return True
        else:
            print(Dictionary['NO_USER'])
            return False

    def __receive(self, sock, sendername, isDie):
        try:
            while True:
                data = sock.recv(self.__recv_size)
                data = base64.b64decode(data).decode()
                if not data:
                    isDie[0] = True
                    break
                self.__echo_recv("previous node: " + sendername + ', data: ' + data)
                type_ = data.split('//')[0].split(':')[0]
                if type_ == SendType.CHAT:
                    header, param = data.split('//')
                    targetname = header.split(':')[1]
                    t = threading.Thread(target = self.__recvCHAT, args = (targetname, param, sendername))
                    t.setDaemon(True)
                    t.start()
                # elif type_ == SendType.ROUTE:
                #     param = data.split('//')[1]
                #     t = threading.Thread(target = self.__recvROUTE, args = (param,))
                #     t.setDaemon(True)
                #     t.start()
                elif type_ == SendType.INTEREST:
                    param = data.split('//')[1]
                    t = threading.Thread(target = self.__recvINTEREST, args = (param, sendername))
                    t.setDaemon(True)
                    t.start()
                elif type_ == SendType.DATA:
                    param = data.split('//')[1]
                    t = threading.Thread(target = self.__recvDATA, args = (param, sendername))
                    t.setDaemon(True)
                    t.start()

        except ConnectionResetError:
            isDie[0] = True
            return

        except BrokenPipeError:
            isDie[0] = True
            return
        finally:
            isDie[0] = True
            return

    def __recvCHAT(self, targetname, param, sendername):
        if targetname == self.__shortname:
            sendername = param.split(':')[0]
            msg = param.split(':')[1]
            print(f'{SendType.CHAT}: {sendername}>>{msg}')
        else:
            #TODO
            pass

    def __recvINTEREST(self, param, sendername):
        #param = targetname/sensor_type/time
        dataname = param
        targetname = param.split('/')[0]
        if targetname == self.__shortname:
            #targetname/sensor_type/time
            data_path = param
            #TODO
            data = self.__getSensorData(data_path)
            msg = f'{param}:{data}'
            self.__send(sendername, msg, SendType.DATA)
            
        elif self.__CS.isExist(dataname):
            with self.__Sem_CS_change:
                data = self.__CS.find_item(dataname)
            msg = f'{dataname}:{data}'
            self.__send(sendername, msg, SendType.DATA)
        else:
            if self.__PIT.isExist(dataname):
                with self.__Sem_PIT_change:
                    self.__PIT.add_pit_item(dataname, sendername, targetname)
            else:
                with self.__Sem_PIT_change:
                    self.__PIT.add_pit_item(dataname, sendername, targetname)
                with self.__Sem_FIB_change:
                    next_hop_name = self.__FIB.select_nexthop(targetname)
                if next_hop_name[0] != -1:
                    self.__send(next_hop_name, dataname, SendType.INTEREST)
                else:
                    with self.__Sem_FIB_change:
                        broadcast_list = self.__FIB.broadcast_list()
                    for next_ in broadcast_list:
                        if next_ != sendername:
                            self.__send(next_, dataname, SendType.INTEREST)
                        else:
                            self.__PIT.delete_pit_item(dataname)
            

    def __recvDATA(self, param, sendername):
        #TODO
        dataname = param.split(':')[0]
        old_targetname = dataname.split('/')[0]
        data = param.split(':')[1]
        if self.__PIT.isExist(dataname):
            with self.__Sem_PIT_change:
                outfaces = self.__PIT.find_item(dataname)
            for out in outfaces:
                if out[0] == self.__shortname:
                    if data == "None":
                        print("Data not found.")
                    else:
                        data = data.replace(';', ':', 1)
                        data = data.replace('_', ' ', 1)
                        print(f'{old_targetname}:{data}')
                else:
                    self.__send(out[0], param, SendType.DATA)

            with self.__Sem_CS_change:
                self.__CS.add_cs_item(dataname, data)
            with self.__Sem_FIB_change:
                self.__FIB.update_fib(sendername, old_targetname)

    def __getSensorData(self, data_path):
        #data_path = target_name/sensor_type/time
        if self.__Generator != None:
            target_name = data_path.split('/')[0]
            sensor_type = data_path.split('/')[1]
            """
            device_name, device_type, data, time = p1,car,19_km_per_h,202211290238
            """
            data_plain = self.__Generator.read_from_csv(target_name, sensor_type)
            device_type = data_plain.split(',')[1]
            data = data_plain.split(',')[2]
            time_ = data_plain.split(',')[3]
            year = time_[:4]
            month = time_[4:6]
            day = time_[6:8]
            hour = time_[8:10]
            minute = time_[10:12]
            return f'{year}-{month}-{day}_{hour};{minute}"{device_type}-{data}"'
        else:
            return 'None'
        pass
    
    def __maintain_listen(self, socket_, src_addr):
        while True:
            try:
                sock_,addr_ = socket_.accept()
                # self.__echo(f'new connection: {addr_}')
                t = threading.Thread(target = self.__LAN_slot, args = (sock_,addr_,src_addr))
                t.setDaemon(True)
                t.start()
            except:
                print ("Error: Failed to create a new thread")
    
    def __listen_host(self):
        if not self.__isRun_net:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("IP address of current device: " + self.__host)
            src_addr = (self.__host, self.__port_LAN)
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
            self.__isRun_net = True
        else:
            print("You have already started the net.")

    def __connect_to(self, target_name):
        if self.__isWAN_occupied == False:
            t = threading.Thread(target = self.__WAN_slot, args = (target_name,))
            t.setDaemon(True)
            t.start()
            return True
        else:
            print("You have already connected to another device. No more slot are available")
            return False

    def __do_showMsg(self):
        self.__isShow_msg = True

    def __do_shut_showMsg(self):
        self.__isShow_msg = False

    async def __cli_input(self):
        #add a key binding to quit the cli
        isLoop = True
        kb = KeyBindings()
        @kb.add('escape')
        async def _(event):
            nonlocal isLoop
            isLoop = False
            event.app.exit()

        @kb.add('c-b')#debug broadcast
        async def _(event):
            self.__isShow_bd = not self.__isShow_bd

        @kb.add('c-d')#debug recv
        async def _(event):
            self.__isShow_recv = not self.__isShow_recv

        @kb.add('c-g')#switch of generator
        async def _(event):
            if self.__Generator != None:
                self.__Generator.close()

        #welcom text
        welcom_text = "Welcom to use ndn cli.\nYou can press 'escape' or 'Control + c' to quit.\n"
        print(welcom_text)
        #Create Prompt
        session = PromptSession()
        prompt = _Prompt.begining
        #Run echo loop.
        while isLoop:
            try:
                if not self.__shortname:
                    print("To use this application, please use 'set-name -name' to set the name of the application")

                commandline = await session.prompt_async(prompt, key_bindings = kb)
                if commandline != None and commandline != '':
                    command = commandline.split(" ")

                    if not self.__shortname:
                        if command[0] == Command.SET_NAME:
                            if len(command) != 2:
                                print(f"The expression is wrong. Please check it. {command[0]} -name")
                            else:
                                self.__shortname = command[1]
                                prompt = _Prompt.begining(self.__shortname)
                        else:
                            print("Please set your name first!")
                    
                    else:

                        if command[0] == Command.OPEN_NET:
                            self.__listen_host()
                            prompt = _Prompt.running_bind

                        elif command[0] == Command.SHOW_MSG:
                            self.__do_showMsg()
                        
                        elif command[0] == Command.SHUT_SHOW_MSG:
                            self.__do_shut_showMsg()

                        elif command[0] == Command.SEARCH_CONN:
                            self.__search_conn()

                        # elif command[0] == Command.CHAT:
                        #     if len(command) != 3:
                        #         print(f"The expression is wrong. please check it. {command[0]} -name -text")
                        #     else:
                        #         target_name = commandline.split(" ")[1]
                        #         text = commandline.split(" ")[2]
                        #         if self.__send(target_name, text, SendType.CHAT) == True:
                        #             Command.chat_success(target_name, text)
                        #         else:
                        #             Command.chat_failed(target_name, text)
                        #         pass

                        elif command[0] == Command.CONNECT:
                            if len(command) != 2:
                                print(f'The expression is wrong. please check it. {command[0]} -name')
                            else:
                                target_name = commandline.split(' ')[1]
                                if self.__connect_to(target_name) != True:
                                    Command.connect_failed(target_name)
                        
                        elif command[0] == Command.APPLY:
                            if self.__isRun_net:
                                if len(command) == 3 or len(command) == 4:
                                    #TODO
                                    target_name = command[1]
                                    sensor_name = command[3]
                                    if SensorType.sensor_isExist(sensor_name):
                                        time_ = time.strftime("%Y%m%d%H%M", time.localtime())
                                        if len(command) == 4:
                                            time_ = command[3]
                                        msg = f'{target_name}/{sensor_name}/{time_}'
                                        self.__recvINTEREST(msg, self.__shortname)
                                        # if self.__send(target_name, msg, SendType.INTEREST) == True:
                                        #     print(f'You have applied {sensor_name} data from {target_name} at {time_}.')
                                        # else:
                                        #     print(f'There are something wrong to send interest package.')
                                    else:
                                        print(f'There are no sensor: <{sensor_name}>.')
                                else:
                                    print(f'The expression is wrong. Please check it. {command[0]} -pi_name -sensor_from -sensor_type -time')
                            else:
                                print("The network is not available. Please open network first.")

                        elif command[0] == Command.SHOWCS:
                            cs_ = self.__CS.get_cs()
                            if len(cs_) == 0:
                                print("There is no item in Content Store.")
                            else: print(cs_)

                        elif command[0] == Command.SHOWPIT:
                            pit_ = self.__PIT.get_pit()
                            if len(pit_) == 0:
                                print("There is no item in Pending Interest Table.")
                            else: print(pit_)
                        
                        elif command[0] == Command.SHOWFIB:
                            fib_ = self.__FIB.get_fib()
                            if len(fib_) == 0:
                                print("There is no item in Forward Informant Base.")
                            else: print(fib_)

                        elif command[0] == Command.SET_GENERATOR:
                            if self.__Generator != None:
                                if len(command) != 2:
                                    print(f'The expression is wrong. please check it. {command[0]} -generator_type')
                                else:
                                    gen_type = command[1]
                                    self.__Generator = Generator(self.__shortname, gen_type)
                                    self.__Generator.run()
                            else:
                                print("Generator has already run.")

                        elif command != None:
                            Command.not_found(command)

            except (EOFError, KeyboardInterrupt):
                return

    async def __main(self):
        with patch_stdout():
            t1 = threading.Thread(target = self.__broadcast)
            t1.setDaemon(True)
            t1.start()

            t2 = threading.Thread(target=self.__broadcast_ip)
            t2.daemon = True
            t2.start()
            try:
                await self.__cli_input()
            finally:
                #cancell background tasks
                # bct.cancel()
                pass
            print("\nQuitting CLI. Bye.\n")

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
