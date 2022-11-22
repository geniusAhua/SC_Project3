import base64
import socket
import threading
import time
import cmd2
from math import ceil

Dictionary = {
              'SEND_SHORTNAME': 'tiliu3', #send your device name
             }

class Demo(cmd2.Cmd):

    def __init__(self):
        self.__host = '10.6.57.217'
        self.__port = 33000

    def __get_host_ip():
        """
        Inquire IP address:
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip