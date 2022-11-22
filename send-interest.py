import socket
import time
import base64

ROUTER_IP = '10.35.70.24'
ROUTER_PORT = 33310

def encode(toEncode):
    ascii_encoded = toEncode.encode("ascii")
    base64_bytes = base64.b64encode(ascii_encoded)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def decode(toDecode):
    base64_bytes = toDecode.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string

def sendData(command):
        """Send sensor data to all peers."""
        hardcodedPeers = {(ROUTER_IP, ROUTER_PORT)}
        for peer in hardcodedPeers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(peer)
                msg = command
                s.send(encode(msg.encode()))
                print("Sent command: ", msg)
                ack = s.recv(1024)
                print("Acknowledgement received", decode(ack))
                s.close()
            except Exception:
                print("An exception occured")

def main():
    command_name = ['car/speed', 'car/proximity', 'car/light-on', 'car/wiper-on', 'car/passengers-count', 'car/fuel', 'car/engine-temperature', 'bike/speed', 'bike/proximity', 'bike/light-on', 'bike/wiper-on',
                    'bike/passengers-count', 'bike/fuel', 'bike/engine-temperature', 'truck/speed', 'truck/proximity', 'truck/light-on', 'truck/wiper-on', 'truck/passengers-count', 'truck/fuel', 'truck/engine-temperature']
    while True:
        for c in command_name:
            time.sleep(10)
            sendData(c)
        time.sleep(20)

if __name__ == '__main__':
    main()
