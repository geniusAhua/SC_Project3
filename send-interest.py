import argparse
import random
import selectors
import socket
import time
import types



def sendData(command):
        """Send sensor data to all peers."""
        sent = False
        # if command == 'ALERT':
        hardcodedPeers = {('10.35.70.24', 33310)}
        for peer in hardcodedPeers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(peer)
                msg = command
                s.send(msg.encode())
                print("Sent command", msg)
                sent = True
                ack = s.recv(1024)
                print("Acknowledgement received", ack)
                s.close()
            except Exception:
                print("An exception occured")

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--command', help='Type of sensor', required=True)
    # args = parser.parse_args()
    command_name = ['vehicle/Speed', 'vehicle/WATER', 'vehicle/FIRE']
    while True:
        for c in command_name:
            time.sleep(10)
            sendData(c)
        time.sleep(5)
    # port_table = {'VehiclePort': 33401}  # Hardcoded port table for testing
    # port = port_table['VehiclePort']     # The port used by the server

    # sendData(command_name)
    # initial_message = sensorType + " 1"
    # byte_messages = [initial_message.encode('UTF-8')]

    # The server's hostname or IP address
    # host = socket.gethostbyname(socket.gethostname())


if __name__ == '__main__':
    main()
