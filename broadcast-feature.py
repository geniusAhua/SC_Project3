#!/usr/bin/env python3

import socket
import threading
import time

PEER_PORT = 33301    # Port for listening to other peers
SENSOR_PORT = 33403  # Port for listening to other sensors
# BCAST_PORT = 33334   # Port for broadcasting own address

ROUTER_HOST = '10.35.70.24'
ROUTER_PORT = 33334


class Peer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def broadcastIP(self):
        """Broadcast the host IP."""
        server_tup = (ROUTER_HOST, ROUTER_PORT)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_tup)
        message = f'HOST {self.host} PORT {self.port} ACTION [truck_speed, truck_proximity, truck_pressure, truck_light-on, truck_wiper-on, truck_passengers-count, truck_fuel, truck_engine-temperature]'
        s.send(message.encode())
        s.close()
    


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)
    while True:
        t1 = threading.Thread(target=peer.broadcastIP)
        t1.start()
        time.sleep(10)


if __name__ == '__main__':
    main()

