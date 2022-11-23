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
    truck_interest_packets = ['truck/speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature']
    bike_interest_packets = ['bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on', 'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature']
    car_interest_packets = ['car/speed', 'car/proximity', 'car/light-on', 'car/wiper-on', 'car/passengers-count', 'car/fuel', 'car/engine-temperature']
    
    while True:
        print('\n')
        print('Press 1 to send truck interest packets')
        print('Press 2 to send bike interest packets')
        print('Press 3 to send car interest packets\n')
        val = input()

        if val == '1':
            for c in truck_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print('\n')
        elif val == '2':
            for c in bike_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print('\n')
        elif val == '3':
            for c in car_interest_packets:
                print('press 1 to send next packet, press 2 to change vehicle type')
                inp = input()
                if inp != '1':
                    break
                sendInterest(c)
                print('\n')

if __name__ == '__main__':
    main()
