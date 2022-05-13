import json
import logging
import random
import socket
import subprocess
import threading
from functools import reduce
from time import sleep, time

import numpy as np

SERVER_ADDRESS = "0.0.0.0"
SERVER_UDP_PORT = 4242
SERVER_TCP_PORT = 4040
NUMBER_OF_SUBPROCCESS = 3


class SuperServer:
    def __init__(self):
        logging.info("Server Running")

        # UDP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_UDP_PORT))

        # TCP Servidor Parceiro
        self.server_tcp = self.create_server_tcp()

        self.number_of_clientes = 0
        self.limit_clients = 3
        self.servers_aux_available = {}
        self.servers_aux_unavailable = {}

    def listener(self):
        # Start thread for listen TCP connections
        t = threading.Thread(target=self.listener_servers_aux)
        t.start()

        self._start_servers_aux_process(NUMBER_OF_SUBPROCCESS)

        while True:
            msg, client = self.sock.recvfrom(1024)
            self.number_of_clientes += 1

            if self.number_of_clientes > self.limit_clients:
                # print("Limite atingido para este servidor, encaminhando mensagem...")
                if len(self.servers_aux_available) > 0:
                    matriz_result, server_aux = self.send_server_aux(msg.decode("utf-8"), client)
                    t = threading.Thread(target=self.send_response_by_server_aux, args=(client, matriz_result, server_aux))
                else:
                    # print("Sem servidores auxiliares disponiveis")
                    t = threading.Thread(target=self.send_response, args=(client, None))
            else:
                # print("Clients connected: ", self.number_of_clientes)
                t = threading.Thread(target=self.send_response, args=(client, msg.decode("utf-8")))

            t.start()

    def _matriz_calculate(self, matrizes):
        matriz_result = reduce(np.dot, matrizes)
        result = {"result": matriz_result.tolist()}
        return json.dumps(result)

    def create_server_tcp(self):
        # print("Criando servidor tcp")
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind((SERVER_ADDRESS, SERVER_TCP_PORT))
        socket_tcp.listen(1)
        return socket_tcp

    def listener_servers_aux(self):
        # print("Descobrindo servidores auxiliares")
        while True:
            conn, client_address = self.server_tcp.accept()
            message = conn.recv(1024)
            data = json.loads(message.decode("utf-8"))
            data["address"] = client_address[0]
            data["current_connections"] = 0

            key_dict = f"{data['address']}-{data['port']}"

            self.servers_aux_available[key_dict] = data
            # print("Servidor auxiliar conectado: ", len(self.servers_aux_available))

    def send_server_aux(self, data, client):
        server = self._get_server_aux()

        address = server["address"]
        port = server["port"]

        if server["current_connections"] < server["max_connections"]:
            start_time = time()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            s.send(data.encode())

            message = s.recv(2048)
            s.close()

            server["current_connections"] += 1

            duration = time() - start_time

            print("------------------------- Resultado-------------------------")
            print("Cliente: ", client)
            print("Time: ", duration - 3)
            print("Matriz receive: ", data)
            print("Matriz result: ", message.decode("utf-8"))
            print("Taxa: ", self.calculate_performance_rate(data, duration - 3))
            print("------------------------------------------------------------")
            print("")

            return message.decode("utf-8"), f"{address}-{port}"
        else:
            return "Not Available", f"{address}-{port}"

    def _format_matriz(self, data):
        matriz_array = json.loads(data)
        return self._matriz_calculate(matriz_array["matrizes"])

    def send_response(self, ip, matriz_str=None):
        sleep(3)
        result = self._format_matriz(matriz_str) if matriz_str else ""

        self.sock.sendto(result.encode("utf-8"), ip)
        self.number_of_clientes -= 1

    def send_response_by_server_aux(self, ip, matriz_str, server_aux):
        # sleep(7)
        self.sock.sendto(matriz_str.encode("utf-8"), ip)
        if self.servers_aux_available[server_aux]["current_connections"] > 0:
            self.servers_aux_available[server_aux]["current_connections"] -= 1

    def _get_server_aux(self):
        keys = list(self.servers_aux_available.keys())
        server_key = random.randint(0, (len(keys) - 1))
        server = keys[server_key]
        return self.servers_aux_available[server]

    def _start_servers_aux_process(self, number_of_servers_aux=1):
        for _ in range(number_of_servers_aux):
            # print("Iniciando servidor aux")
            subprocess.Popen(["python", "-m", "server_aux"])

    def calculate_performance_rate(self, matrizes_str, duration):
        formated = json.loads(matrizes_str)
        matriz = formated["matrizes"]
        size_processing = len(matriz[0]) * len(matriz[1][0])
        return round((duration / size_processing), 6)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    server = SuperServer()
    server.listener()
