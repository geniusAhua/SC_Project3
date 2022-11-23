import socket
import threading
import time
import base64

PEER_PORT = 33301  # Port for listening to other peers
BCAST_PORT = 33334  # Port for broadcasting own address
INTEREST_PORT = 33310

map_dict = {}


def tabular_display(temp_dict):
    print("{:<25} | {:<15}".format('ACTION', 'IP_ADDR'))
    for key, val in temp_dict.items():
        print("{:<25} | {:<15}".format(key, str(val)))


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def encrypt(self, toEncode):
        ascii_encoded = toEncode.encode("ascii")
        base64_bytes = base64.b64encode(ascii_encoded)
        base64_string = base64_bytes.decode("ascii")
        return base64_string

    def decrypt(self, toDecode):
        base64_bytes = toDecode.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("ascii")
        return sample_string

    def updatePeerList(self):
        """Update peers list on receipt of their address broadcast."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        host = socket.gethostbyname(hostname)
        port = BCAST_PORT
        s.bind((host, port))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            print("BRaddr: ", addr[0])
            print("BRconnection: ", str(conn))
            data = conn.recv(1024)
            # #print("Base 64 decode data updat peer", data)
            # base64_decode_data = self.decode(data)
            # print("Base 64 decode data updat peer", base64_decode_data)
            # utf_data = base64_decode_data.decode(data)
            # print("utd 8 decode data updat peer", utf_data)
            # print(data, " Peer List data")
            # #data, _ = s.recvfrom(1024)
            data = data.decode()
            # print("received message:", data)
            dataMessage = data.split(' ')
            action_list = self.split_using_act(data.split('ACTION '))
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

                peer = (host, port, action_list)

                if peer != (self.host, self.port, action_list) and peer not in self.peers:
                    self.peers.add(peer)
                    print('Known vehicles:', self.peers)
                    self.maintain_router()
            time.sleep(2)

    def parse_interest(self, interest):
        return interest
        # inter = interest.split("/")
        # return inter[len(inter) - 1]

    def filter_ips(self, data):
        if data in map_dict.keys():
            return map_dict[data]
        else:
            return None

    def split_using_act(self, act_string):

        temp_str = act_string[1].replace('[', '').replace(']', '').replace(' ', '').lower()
        # new_ls = temp_str.split(',')
        return str(temp_str)

    # def receiveData(self):
    #     """Listen on own port for other peer data."""
    #     print("listening for interest data")
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     hostname = socket.gethostname()
    #     host = socket.gethostbyname(hostname)
    #     port = INTEREST_PORT
    #     s.bind((host, port))
    #     s.listen(5)
    #     while True:
    #         conn, addr = s.accept()
    #         print("addr: ", addr[0])
    #         print("connection: ", str(conn))
    #         data = conn.recv(1024)
    #         base64_decode = self.decrypt(data)
    #         utf_data = base64_decode.decode('utf-8')
    #         print(utf_data, " to actuate on")
    #         interset = self.parse_interest(utf_data.lower())
    #         print("Final interset", interset)
    #         filtered_ips = self.filter_ips(interset)
    #         ack = self.route_to_pi(filtered_ips, interset)
    #         self.send_back_to_interested_node(ack, addr[0], conn)
    #         # call actuators
    #         # sendAck(addr[0], actuationResult)
    #         conn.close()
    #         time.sleep(1)

    def send_none_to_intereseted_node(self,host,conn):
        msg = "404 not found"
        encoded_msg = str(self.encrypt(msg)).encode()
        print("WHAT IS ENCODED BACK TO SENDEr", encoded_msg)
        conn.send(encoded_msg)
        return
        

    def receiveData(self):
        """Listen on own port for other peer data."""
        print("listening for interest data")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        host = socket.gethostbyname(hostname)
        port = INTEREST_PORT
        s.bind((host, port))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            print("addr: ", addr[0])
            print("connection: ", str(conn))
            data = conn.recv(1024)
            print("Received data", data)
            utf_data = data.decode()
            print("Decoded data", utf_data)
            base64_decode = self.decrypt(utf_data)
            print("Base 64 decode data", base64_decode)
            # print(utf_data, " to actuate on")
            interset = self.parse_interest(base64_decode.lower())
            print("Final interset", interset)
            filtered_ips = self.filter_ips(interset)
            if filtered_ips is None:
                self.send_none_to_intereseted_node(addr[0],conn)
            else:
                ack = self.route_to_pi(filtered_ips, interset)
                self.send_back_to_interested_node(ack, addr[0], conn)
            # call actuators
            # sendAck(addr[0], actuationResult)
            conn.close()
            time.sleep(1)

    def send_back_to_interested_node(self, message, host, conn):

        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((host,INTEREST_PORT))
        msg = message
        print("Idhar aaya kya", msg)
        encoded_msg = str(self.encrypt(msg)).encode()
        print("WHAT IS ENCODED BACK TO SENDEr", encoded_msg)
        conn.send(encoded_msg)
        return

    def remove_node(self, node, command):
        try:
            print("REMOVING NODE", node)
            if node in map_dict[command]:
                map_dict[command].remove(node)
            print("UPDATED MAP DICT", tabular_display(map_dict))
        except:
            print("ERROR IN REMOVING NODE")

    def route_to_pi(self, peer_list, command):
        """Send sensor data to all peers."""
        sent = False
        # if command == 'ALERT':
        print("What is peer list and command :{} {}".format(peer_list, command))
        for peer in peer_list:
            print("What is peer inside peerlist", peer)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer, PEER_PORT))
                msg = command
                print("Idhar aaya kya", msg)
                s.send(str(self.encrypt(msg)).encode())
                print("Sent command", msg)
                sent = True
                ack = s.recv(1024)
                print("Acknowledgement received", ack)
                utf_decode = ack.decode()
                base64_ack = self.decrypt(utf_decode)
                print("Base 64 ack", base64_ack)
                s.close()
                return base64_ack
            except Exception:
                print("An exception occured")
                continue
                # self.remove_node(peer,command)

    def maintain_router(self):
        empty_set = set()
        count = 1
        for peer in self.peers:
            # print("No of iterations", count)
            # print("Inside peer", peer)
            host = peer[0]
            # print("Inside host",host)
            port = peer[1]
            action_list = peer[2].split(',')
            # print("Inside action", action)
            for action in action_list:
                if action in map_dict.keys():
                    temp_set = map_dict[action]
                    temp_set.add(host)
                    map_dict[action] = temp_set


                else:
                    empty_set.add(host)
                    map_dict[action] = empty_set
            count += 1
        print("What is router table now", tabular_display(map_dict))


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PEER_PORT)

    t1 = threading.Thread(target=peer.updatePeerList)
    t2 = threading.Thread(target=peer.receiveData)
    t1.start()
    time.sleep(15)
    t2.start()


if __name__ == '__main__':
    main()
