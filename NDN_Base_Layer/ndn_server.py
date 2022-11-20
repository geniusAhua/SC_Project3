import socket
import threading
import base64

Dictionary = {
              'SEND_SHORTNAME': 'tiliu', #send your device name 
             }

port1 = 8848

#number of connection - semaphore/最大连接数量为4（可同时处理）
sem = threading.Semaphore(2)

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
        
def Console(sock,addr,src_addr):
    with sem:
        try:
            print('set connection: source address %s:%s' %addr + ' --- destination address %s:%s'  %src_addr )
            #when first accept the connection, we need save the shortname of the device
            data = sock.recv(1024)
            data = base64.b64decode(data).decode()
            if data.split(':')[0] == 'SHORTNAME':
                shortname = data.split(':')[1]
                print(shortname + "has connected to this device")
                message = base64.b64encode(f'SHORTNAME:{Dictionary["SEND_SHORTNAME"]}'.encode())
                sock.send(message)
            else:
                print(data)
                sock.close()
                print("illegal connection!")
                return
            while True:
                data = sock.recv(1024)
                if not data: 
                    sock.close()
                    break
                print(shortname + '>>' +data.decode())
                command = data[:4].decode()
               
            print('Connection terminate: source: ' + shortname + ' == %s:%s' %addr + ' --- destination: %s:%s' %src_addr)
            print('==================================================')
            return
        except ConnectionResetError:
            print('A peer client suddenly disconnected')
            return
        

def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = get_host_ip()
    print(">>" + host)
    #33000 ~ 39000
    port1 = 33000
    src_addr = (host , port1)
    s.bind(src_addr)
    #设置可排队连接数量为0
    s.listen(0)
    print('======================start=======================')
    print('                  service is running...')
    print('=======================end========================')

    while True:
        sock1,addr1 = s.accept()
        try:
            print(f'new connection: {addr1}')
            t = threading.Thread(target = Console, args = (sock1,addr1,src_addr))
            t.setDaemon(True)
            t.start()
        except:
            print ("Error: Failed to create a new thread")
       
if __name__ == '__main__':
    main()
