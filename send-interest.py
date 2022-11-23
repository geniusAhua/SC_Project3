import socket
import time
import base64

ROUTER_IP = '10.35.70.24'
ROUTER_PORT = 33310

def bencode(toEncode):
    ascii_encoded = toEncode.encode("ascii")
    base64_bytes = base64.b64encode(ascii_encoded)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def bdecode(toDecode):
    base64_bytes = toDecode.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string

def actuate(data):
    print("Data packet received: ", data)

def sendInterest(interest):
        routers = {(ROUTER_IP, ROUTER_PORT)}
        print('attempting to send interest packet: ', interest)
                
        for router in routers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(router)
                base64encoded = str(bencode(interest))
                s.send(base64encoded.encode())
                ack = s.recv(1024)
                actuate(bdecode(ack.decode('utf-8')))
                s.close()
            except Exception:
                print("An exception occured")

def main():
    # interest_packets = ['car/speed', 'car/proximity', 'car/light-on', 'car/wiper-on', 'car/passengers-count', 'car/fuel', 'car/engine-temperature', 
    # 'bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature', 'truck_speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature']
    interest_packets = ['truck/speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature',
                    'bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature']

    while True:
        for c in interest_packets:
            # time.sleep(10)
            print('Press enter to send next interest packet')
            input()
            sendInterest(c)
            print('\n')
        # time.sleep(20)

if __name__ == '__main__':
    main()
