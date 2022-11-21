
import selectors
import socket
import threading
import time
import types

PEER_PORT = 33301    # Port for listening to other peers
BCAST_PORT = 33334   # Port for broadcasting own address

map_dict = {}


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def broadcastIP(self):
        """Broadcast the host IP."""
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.5)
        message = f'HOST {self.host} PORT {self.port}'.encode('utf-8')
        print("What is the message", message)
        while True:
            server.sendto(message, ('<broadcast>', BCAST_PORT))
            # print("Host IP sent!")
            print("Broadcasting my IP {}:{}".format(self.host,self.port))
            time.sleep(10)


    def updatePeerList(self):
        """Update peers list on receipt of their address broadcast."""
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                socket.IPPROTO_UDP)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", BCAST_PORT))
        while True:
            data, _ = client.recvfrom(1024)
            print("received message:", data.decode('utf-8'))
            data = data.decode('utf-8')
            dataMessage = data.split(' ')
            command = dataMessage[0]
            if command == 'HOST':
                host = dataMessage[1]
                port = int(dataMessage[3])
                if len(dataMessage) > 5:
                    action = dataMessage[5]
                else:
                    action = ''
                # host = dataMessage[1]
                # port = int(dataMessage[3])
                peer = (host, port, action)
                if peer != (self.host, self.port, action) and peer not in self.peers:
                    self.peers.add(peer)
                    print('Known vehicles:', self.peers)
                    self.maintain_router()
            time.sleep(2)


    def maintain_router(self):
        print("What are peers", self.peers)
        empty_set = set()
        count = 1
        for peer in self.peers:
            print("No of iterations", count)
            print("Inside peer", peer)
            host = peer[0]
            print("Inside host",host)
            port = peer[1]
            action = peer[2]
            print("Inside action", action)
            
            if action in map_dict.keys():
                temp_set = map_dict[action]
                print("What is type", type(temp_set))
                print("What is temp set", temp_set)
                print("What is host", host)
                temp_set.add(host)
                print("What is new set", temp_set)
                map_dict[action] = temp_set
                print("What is map dict in action",map_dict)

            else:
                empty_set.add(host)
                map_dict[action] = empty_set
                print("What is map dict in else",map_dict)
            count+=1
        print("What is router table now", map_dict)


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)
    t1 = threading.Thread(target=peer.broadcastIP)
    t2 = threading.Thread(target=peer.updatePeerList)
    t1.start()
    time.sleep(3)
    t2.start()


if __name__ == '__main__':
    main()
