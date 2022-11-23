import socket
import threading
import time

PEER_PORT = 33301    # Port for listening to other peers
SENSOR_PORT = 33403  # Port for listening to other sensors
# BCAST_PORT = 33334   # Port for broadcasting own address

ROUTER_HOST = '10.35.70.24'
ROUTER_PORT = 33334

advertise_string = '[car/speed, car/proximity, car/pressure, car/light-on, car/wiper-on, car/passengers-count, car/fuel, car/engine-temperature]'

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def advertiseFeature(self):
        """Broadcast the host IP."""
        server_tup = (ROUTER_HOST, ROUTER_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_tup)
        message = f'HOST {self.host} PORT {self.port} ACTION {advertise_string}'
        s.send(message.encode())
        s.close()

def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)
    while True:
        t1 = threading.Thread(target=peer.advertiseFeature)
        t1.start()
        time.sleep(10)

if __name__ == '__main__':
    main()