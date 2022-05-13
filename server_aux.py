import errno
import json
import socket
import threading
from functools import reduce
from time import sleep

import numpy as np

SERVER_ADDRESS = "0.0.0.0"
SERVER_PORT = 3322

LIST_PORTS = [3322, 3311, 2233, 1322, 3352, 3382, 3392, 1312]

SUPER_SERVER_ADDRESS = "127.0.0.1"
SUPER_SERVER_PORT = 4040

# MAX_CONNECTIONS = random.randint(1, 5)
MAX_CONNECTIONS = 2


class ServerAux(threading.Thread):
    def __init__(self):
        self.number_of_clientes = 0

    def run(self):
        while True:
            print(" ")
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server.bind((SERVER_ADDRESS, SERVER_PORT))

            server.listen(1)
            client_socket, client_address = server.accept()
            message = client_socket.recv(2048)
            message = message.decode("utf-8")
            print("Recebendo do matriz do super servidor")
            sleep(3)

            if message == "is_available":
                t = threading.Thread(target=self.send_message_available, args=(client_socket, self.check_max_connections()))
                t.start()
            else:
                t = threading.Thread(target=self.send_message, args=(message, client_socket))
                t.start()
            print(" ")

    def send_message(self, message, conn):
        response = self._format_matriz(message).encode("utf-8")
        conn.send(response)
        conn.close()
        print("Encaminhando para super servidor")

    def _format_matriz(self, data):
        matriz_array = json.loads(data)
        return self._matriz_calculate(matriz_array["matrizes"])

    def _matriz_calculate(self, matrizes):
        matriz_result = reduce(np.dot, matrizes)
        result = {"matrizes": matriz_result.tolist()}
        return json.dumps(result)

    def check_max_connections(self):
        return self.number_of_clientes < MAX_CONNECTIONS

    def send_message_available(self, conn, data):
        conn.send(str(data).encode("utf-8"))
        conn.close()


def port_available():
    port_free = SERVER_PORT
    for port in LIST_PORTS:
        if not check_port_in_use(port):
            return port
    return port_free


def check_port_in_use(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_in_use = False
    try:
        s.bind(("0.0.0.0", port))
    except socket.error as e:
        port_in_use = e.errno == errno.EADDRINUSE
    s.close()
    return port_in_use


if __name__ == "__main__":
    SERVER_PORT = port_available()
    # Conectando e se registrando no super server
    print(">>>>>>>>>>>>>>>> SERVER_PORT", SERVER_PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SUPER_SERVER_ADDRESS, SUPER_SERVER_PORT))
    s.send(json.dumps({"max_connections": MAX_CONNECTIONS, "port": SERVER_PORT}).encode())
    s.close()

    # Iniciando servidor TCP
    server = ServerAux()
    server.run()
