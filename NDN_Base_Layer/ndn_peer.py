import base64
import socket
import threading
import time
from math import ceil

Dictionary = {
              'SEND_SHORTNAME': 'tiliu3', #send your device name
             }

host = '10.6.57.217'
port1 = 33000

Sem_conn_change = threading.Semaphore(1)
Sync_connections = 0

def InitialConnection():
    global Sync_connections
    Sync_connections = 0

def newConnection():
    global Sync_connections
    Sync_connections += 1

def closeConnection():
    global Sync_connections
    Sync_connections -= 1

def anyConnection():
    global Sync_connections
    if(Sync_connections == 0):
        return False
    else:
        return True

#to get the ip address of current device
def get_host_ip():
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

def thread_client(threadName,ids, socket):
    s = socket
    try:
        s.connect((host , port1))
        with Sem_conn_change:
            newConnection()
        print('thread_1: Client is running...')
        message = base64.b64encode(f'SHORTNAME:{Dictionary["SEND_SHORTNAME"]}'.encode())
        s.send(message)
        t = threading.Thread(target=send_msg, args=(s))
        t.setDaemon(True)
        t.start()
        while True:
            if(getattr(s, '_closed') == True):
                print("!!! - server has been closed - !!!")
                s.close()
                with Sem_conn_change:
                    closeConnection()
                break
            # message = input(">>")
            # # message = base64.b64encode(message.encode())
            # s.send(message.encode())

        return
    except ConnectionRefusedError:
        print('Failed to connect to server.')
        s.close()
        if anyConnection():
            with Sem_conn_change:
                print("connections: " + str(Sync_connections))
                closeConnection()
                print("connections: " + str(Sync_connections))
        return
    
    except BrokenPipeError:
        print("Connection was broken.")
        s.close()
        with Sem_conn_change:
            closeConnection()
        return

# def thread_listenServer():

def send_msg(sock):
    while True:
        message = input(">>")
        sock.send(message.encode())


def createConnection(socket):
    t = threading.Thread(target = thread_client, args = ("Thread-client", 1, socket))
    t.setDaemon(True)
    t.start()

def main():
    # 主进程:
    print('*************************************************')
    print('**                This is peer1                **')
    print('*************************************************')
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = get_host_ip()
    src_addr = (host, port1)
    _socket.bind(src_addr)

    InitialConnection()

    createConnection(_socket)

    while True:
        time.sleep(1)
        if(not anyConnection()):
            print("no connection can be accessed.")
            print("Are you want to try again? (yes/no)")
            while True:
                _comma = input(">>")
                print("_comma: " + _comma)
                if(_comma == "yes" or _comma == 'y'):
                    createConnection()
                    break
                if (_comma == 'no' or _comma == 'n'):
                    print("Thanks for using, Goodbye!")
                    return
                else:
                    print("unknown command:" + _comma)

        else:
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
