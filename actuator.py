import socket
import time
import traceback

PEER_PORT = 33301    # Port for listening to other peers
SENSOR_PORT = 33401  # Port for listening to other sensors

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

def callActuator(data):
    return 'actuation success'

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
            print("connection: ", str(conn))
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