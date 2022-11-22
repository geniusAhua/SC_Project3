import base64
import socket
import threading
import sys
import time
import cmd2
from math import ceil

Dictionary = {
              'SEND_SHORTNAME': 'tiliu3', #send your device name
             }

class Demo(cmd2.Cmd):

    def __init__(self):
        cmd2.Cmd.__init__(self)
        self.prompt = 'ndn>'
        self.__host = '10.6.57.217'
        self.__port = 33000
        self.__host_target = self.__get_host_ip()
        self.__port_target = 33000
        self.__Sem_conn_change = threading.Semaphore(1)
        self.__Sem_conns = threading.Semaphore(4) # the maximum number of connections is 4/最大连接数量为4
        self.__socket_pool = {}

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
            sock.close()
            self.__socket_pool.remove(shortname)

    def __Console(self, sock, addr, src_addr):
        with self.__Sem_conns:
            try:
                print('set connection: source address %s:%s' %addr + ' --- destination address %s:%s'  %src_addr )
                #when first accept the connection, we need save the shortname of the device
                isLoop = False
                data = sock.recv(1024)
                data = base64.b64decode(data).decode()
                if data.split(':')[0] == 'SHORTNAME':
                    shortname = data.split(':')[1]
                    print(shortname + "has connected to this device")
                    #append the connection in socket pool
                    self.__addConnection(shortname, sock)
                    message = base64.b64encode(f'SHORTNAME:{Dictionary["SEND_SHORTNAME"]}'.encode())
                    sock.send(message)
                    isLoop = True
                else:
                    print(data)
                    isLoop = False
                    print("illegal connection!")
                    return
                while isLoop:
                    if(getattr(sock, '_closed') == True):
                        print('Connection terminate: source: ' + shortname + ' --- %s:%s' %addr + ' --- destination: %s:%s' %src_addr)
                        break
                    data = sock.recv(1024)
                    if not data:
                        sock.close()
                        break
                    print(shortname + '>>' +data.decode())
                    command = data[:4].decode()
                
                self.__deleteConnection(shortname)
                print('==================================================')
                return
            except ConnectionResetError:
                print('A peer client suddenly disconnected')
                self.__deleteConnection(shortname)
                return
    
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

    
    def do_listen_host(self, arg):
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("IP address of current device: " + self.__host)
        src_addr = (self.__host, self.__port)
        socket_.bind(src_addr)
        #set the num of wating connection application
        socket_.listen(0)
        print('======================start=======================')
        print('                  service is running...')
        print('=======================end========================')
        # to maintain listening the host
        maintain_listen = threading.Thread(target = self.__maintain_listen, args = (socket_, src_addr))
        maintain_listen.setDaemon(True)
        maintain_listen.start()

    # def do_recieve_from(self, shortname):
    #     sock = self.__socket_pool[shortname]
    #     try:
    #         while True:
    #             data = sock.recv(1024)
    #             if not data:
    #                 sock.close()
    #                 break
    #             print(shortname + '>>' +data.decode())
    #             command = data[:4].decode()

    def do_exit(self, arg):
        sys.exit(1)

if __name__ == '__main__':
    demo = Demo()
    demo.cmdloop()
