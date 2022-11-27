import socket
import threading
import time
import base64
import random 
import traceback

PEER_PORT = 33301    # Port for listening to other peers

ROUTER_HOST = '10.35.70.28'
ROUTER_PORT = 33334

#vehicle_type = 'car' # bike, truck possible

features_dict = {
    "truck_advertise_string": '[truck/speed, truck/proximity, truck/pressure, truck/light-on, truck/wiper-on, truck/passengers-count, truck/fuel, truck/engine-temperature]',
    "car_advertise_string": '[car/speed, car/proximity, car/pressure, car/light-on, car/wiper-on, car/passengers-count, car/fuel, car/engine-temperature]',
    "bike_advertise_string": '[bike/speed, bike/proximity, bike/pressure, bike/light-on, bike/wiper-on, bike/passengers-count, bike/fuel, bike/engine-temperature]'
}

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

def sendAck(conn, raddr, result):
        try:
            msg = result
            conn.send(bencode(msg).encode())
        except Exception:
            print(traceback.format_exc())
            print('exception occurred while sending acknowledgement: ', Exception)

def senseSpeed():
    baseSpeed = 80
    randomMix = random.randint(-10, 10)
    res = baseSpeed + randomMix
    return str(res)

def senseProximity():
    baseProximity = 20
    randomMix = random.randint(-10, 10)
    res = baseProximity + randomMix
    return str(res)

def sensePressure():
    if vehicle_type == 'car':
        val = random.randint(30, 33) # car tyre pressure
    elif vehicle_type == 'bike':
        val = random.randint(80, 130) # two wheeler tyre pressure
    else:
        val = random.randint(80, 131) # truck tyre pressure
    return str(val)

def senseLight():
    state = ['on', 'off', 'faulty']
    return random.choice(state)

def senseWiper():
    state = ['off', 'on', 'faulty']
    return random.choice(state)

def sensePassengerCount():
    if vehicle_type == 'car':
        val = random.randint(1, 6)
    else: # bike, truck
        val = random.randint(1, 3)
    return str(val)

def senseFuel():
    state = ['low', 'medium', 'full']
    return random.choice(state)

def senseEngineTemperature():
    baseTemp = 200
    randomMix = random.randint(-5, 20)
    res = baseTemp + randomMix
    return str(res)

def callActuator(interest):
    if interest.lower() == "speed":
        return senseSpeed()
    elif interest.lower() == "proximity":
        return senseProximity()
    elif interest.lower() == "pressure":
        return sensePressure()
    elif interest.lower() == "light-on":
        return senseLight()
    elif interest.lower() == "wiper-on":
        return senseWiper()
    elif interest.lower() == "passengers-count":
        return sensePassengerCount()
    elif interest.lower() == "fuel":
        return senseFuel()
    elif interest.lower() == "engine-temperature":
        return senseEngineTemperature()

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def advertiseFeature(self):
        """Advertise the host IP."""
        server_tup = (ROUTER_HOST, ROUTER_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_tup)
        dynamic_advertise_string = vehicle_type.lower() + '_advertise_string'
        adv = features_dict[dynamic_advertise_string]
        message = f'HOST {self.host} PORT {self.port} ACTION {adv}'
        print('Advertising ', message)
        s.send(message.encode())
        s.close()

def receiveData():
    print("listening for actuation requests")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    port = PEER_PORT
    s.bind((host, port))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print("addr: ", addr[0])
        # print("connection: ", str(conn))
        data = conn.recv(1024)
        data = bdecode(data.decode())
        print(data, " to actuate on")
        # call actuators
        [vt, interest] = data.split('/')
        if vehicle_type == vt:
            actuationResult = callActuator(interest)
        
        sendAck(conn, addr[0], actuationResult)
        conn.close()
        time.sleep(1)

def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)

    print('\n')
    print('Enter vehicle type (truck/car/bike): ')
    val = input()
    global vehicle_type
    vehicle_type = val
        
    while True:
        t1 = threading.Thread(target=peer.advertiseFeature)
        t1.start()
        time.sleep(10)
        receiveData()

if __name__ == '__main__':
    main()
