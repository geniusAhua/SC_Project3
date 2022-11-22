import socket
import time
import traceback
import random

PEER_PORT = 33301    # Port for listening to other peers
SENSOR_PORT = 33401  # Port for listening to other sensors
VEHICLE_TYPE = 'car' # bike, truck possible

def sendAck(conn, raddr, result):
        """Send sensor data to all peers."""
        router = (raddr, SENSOR_PORT)

        try:
            # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # s.connect((raddr, SENSOR_PORT))
            msg = result
            conn.send(msg.encode())
            # sent = True
            # s.close()
        except Exception:
            print(traceback.format_exc())
            print('exception occurred while sending acknowledgement: ', Exception)

def senseSpeed():
    baseSpeed = 20
    randomMix = random.randint(-10, 10)
    res = baseSpeed + randomMix
    return res + " km/h"

def senseProximity():
    baseProximity = 20
    randomMix = random.randint(-10, 10)
    res = baseProximity + randomMix
    return res + " metres"

def sensePressure():
    if VEHICLE_TYPE == 'car':
        val = random.randint(30, 33) # car tyre pressure
    elif VEHICLE_TYPE == 'bike':
        val = random.randint(80, 130) # two wheeler tyre pressure
    else:
        val = random.randint(116, 131) # truck tyre pressure
    return val + " psi"

def senseLight():
    state = ['on', 'off']
    return random.choice(state)

def senseWiper():
    state = ['off', 'on-slow', 'on-medium', 'on-fast']
    return random.choice(state)

def sensePassengerCount():
    if VEHICLE_TYPE == 'car':
        val = random.randint(1, 4) # car
    else:
        val = random.randint(1, 2) # bike, truck 
    return val 

def senseFuel():
    state = ['low', 'medium', 'full']
    return random.choice(state)

def senseEngineTemperature():
    baseTemp = 200
    randomMix = random.randint(-5, 20)
    res = baseTemp + randomMix
    return res + " degree celcius"

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

def receiveData():
        """Listen on own port for other peer data."""
        print("listening for actuation requests")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            data = data.decode('utf-8')
            print(data, " to actuate on")
            # call actuators
            actuationResult = callActuator(data)
            sendAck(conn, addr[0], actuationResult)
            conn.close()
            time.sleep(1)

def main():
    while True:
        receiveData();


if __name__ == '__main__':
    main()