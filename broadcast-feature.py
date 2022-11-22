#!/usr/bin/env python3

import selectors
import socket
import threading
import time
import types

PEER_PORT = 33301    # Port for listening to other peers
SENSOR_PORT = 33403  # Port for listening to other sensors
BCAST_PORT = 33334   # Port for broadcasting own address


class Peer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def accept_wrapper(self, sock, selector):
        conn, addr = sock.accept()
        print("Accepted connection from", addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, in_bytes=b'', out_bytes=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        selector.register(conn, events, data=data)

    def service_connection(self, key, mask, selector):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(8000)
                if recv_data:
                    data.out_bytes += recv_data
                    data1 = recv_data.decode('utf-8')
                    print('Received', data1)
                    value = int(data1.split(' ')[1])
                    sensortype = data1.split(' ')[0]
                    if sensortype == 'speed':
                        if value >= 80:
                            self.sendData("is overspeeding", 'ALERT')
                    elif sensortype == 'proximity':
                        if value <= 20:
                            self.sendData("is closeby to you", 'ALERT')
                    elif sensortype == 'pressure':
                        if value <= 25:
                            self.sendData("is having tyre issue", 'ALERT')
                    elif sensortype == 'heartrate':
                        if value <= 60 or value >= 100:
                            self.sendData("passenger heart rate level low/high", 'ALERT')
                else:
                    print("Closing connection to:", data.addr)
                    selector.unregister(sock)
                    sock.close()
            except Exception:
                selector.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if data.out_bytes:
                # print("Echoing", repr(data.out_bytes), "to", data.addr)
                sent = sock.send(data.out_bytes)
                data.out_bytes = data.out_bytes[sent:]

    # def listentosensor(self):
    #     selector = selectors.DefaultSelector()
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.bind((self.host, SENSOR_PORT))
    #     print("Socket bound to Port for sensor:", SENSOR_PORT)
    #     sock.listen()
    #     # print("Listening for connections...")
    #     sock.setblocking(False)
    #     selector.register(sock, selectors.EVENT_READ, data=None)
    #     while True:
    #         events = selector.select(timeout=None)
            
    #         for key, mask in events:
    #             if key.data is None:
    #                 self.accept_wrapper(key.fileobj, selector)
    #             else:
    #                 self.service_connection(key, mask, selector)
    #         time.sleep(1)

    def broadcastIP(self):
        """Broadcast the host IP."""
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                               socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.5)
        message = f'HOST {self.host} PORT {self.port} ACTION [truck_speed, truck_proximity, truck_pressure, truck_light-on, truck_wiper-on, truck_passengers-count, truck_fuel, truck_engine-temperature]'.encode('utf-8')
        while True:
            server.sendto(message, ('<broadcast>', BCAST_PORT))
            # print("Host IP sent!")
            time.sleep(10)

    # def updatePeerList(self):
    #     """Update peers list on receipt of their address broadcast."""
    #     client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
    #                            socket.IPPROTO_UDP)
    #     client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #     client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #     client.bind(("", BCAST_PORT))
    #     while True:
    #         data, _ = client.recvfrom(1024)
    #         # print("received message:", data)
    #         data = data.decode('utf-8')
    #         print("decoded message ", data)
    #         dataMessage = data.split(' ')
    #         print('Split message ', dataMessage)
    #         command = dataMessage[0]
    #         if command == 'HOST':
    #             host = dataMessage[1]
    #             port = int(dataMessage[3])
    #             action = ''
    #             if len(dataMessage) > 5:
    #               action = str(dataMessage[5])
    #             print('Check Action '+ action)
    #             peer = (host, port, action)
    #             if peer != (self.host, self.port, action) and peer not in self.peers:
    #                 self.peers.add(peer)
    #                 print('Known vehicles:', self.peers)
    #         time.sleep(2)

    def sendData(self, data, command):
        """Send data to all peers."""
        delset = set()
        sent = False
        if command == 'ALERT':
        
            for peer in self.peers:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print('Maa chudalo')
                    peer_tup = (peer[0], peer[1])
                    s.connect(peer_tup)
                    print('Maa chud gayi')
                    msg = f' Speed ALERT from {self.host}, WATER {data}'
                    s.send(msg.encode())
                    sent = True
                    s.close()
                except Exception:
                    delset.add(peer)
        for peer in delset:
            self.peers.discard(peer)
            print('Vehicle removed due to inactivity:', peer)
            print("Known vehicles:", self.peers)
        if sent:
            print("Alert sent to known vehicles")

    # def receiveData(self):
    #     """Listen on own port for other peer data."""
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     s.bind((self.host, self.port))
    #     s.listen(5)
    #     while True:
    #         conn, _ = s.accept()
    #         data = conn.recv(1024)
    #         data = data.decode('utf-8')
    #         print(data)
    #         conn.close()
    #         time.sleep(1)
            
    def filter_peers(self, interest):
        print('OG list', self.peers)
        filterest_list = [peer for peer in self.peers if peer[2] == interest]
        filter_set = set(filterest_list)
        print('filtered list ', filter_set)
        return filter_set
    
    


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)
    t1 = threading.Thread(target=peer.broadcastIP)
    #t2 = threading.Thread(target=peer.updatePeerList)
    # t3 = threading.Thread(target=peer.listentosensor)
    # t4 = threading.Thread(target=peer.receiveData)
    t1.start()
    # t4.start()
    time.sleep(3)
    #t2.start()
    # t3.start()


if __name__ == '__main__':
    main()

