import json
import random
import socket
from time import sleep

import numpy as np


class Client:
    def __init__(self):
        self.server_address = "super_server_service"
        self.server_port = 4242
        self.buffer_size = 1024

    def start(self):

        while True:
            matriz_array = json.dumps({"matrizes": self._generate_random_matriz()})
            data_send = str.encode(matriz_array)

            serverAddressPort = (self.server_address, self.server_port)

            UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPClientSocket.sendto(data_send, serverAddressPort)

            response = UDPClientSocket.recvfrom(self.buffer_size)
            print(response[0].decode("utf-8"))
            sleep(7)

    def _generate_random_matriz(self):
        number_of_matrizes = random.randint(2, 6)
        matrizes = []

        for _ in range(number_of_matrizes):
            m = np.random.randint(10, size=(3, 3))
            matrizes.append(m.tolist())

        return matrizes


client = Client()
client.start()
