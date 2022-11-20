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

# 线程创建函数:
# 线程1：与server连接的客户端线程
def thread_client(threadName,ids):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((host , port1))
        with Sem_conn_change:
            newConnection()
        print('线程1：用于各种用户操作的客户端正在运行...')
        message = base64.b64encode(f'SHORTNAME:{Dictionary["SEND_SHORTNAME"]}'.encode())
        s.send(message)
        while True:
            if(getattr(s, '_closed') == True):
                print("!!! - server has been closed - !!!")
                s.close()
                with Sem_conn_change:
                    closeConnection()
                break
            message = input(">>")
            # message = base64.b64encode(message.encode())
            s.send(message.encode())

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


def createConnection():
    t = threading.Thread(target = thread_client, args = ("Thread-client", 1))
    t.setDaemon(True)
    t.start()

def main():
    # 主进程:
    print('*************************************************')
    print('**                This is peer1                **')
    print('*************************************************')
    InitialConnection()

    createConnection()

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
