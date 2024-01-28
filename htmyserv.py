from http import HTTPStatus
import logging
from pathlib import Path
from queue import Queue
import socket
from typing import NamedTuple
from hthelper import get_request, make_answer

from htworker import Worker


class MyServer:
    def __init__(
        self,
        host: str,
        port: int,
        max_workers: int = 3,
        timeout: float = 5.0,
        basedir: str = ".",
        bind: bool = True,
        chunklen=24,
    ):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.max_workers = max_workers
        self.timeout = timeout
        self.basedir = Path(basedir)
        if not self.basedir.is_dir():
            raise FileNotFoundError(f"{basedir} is not a directory")
        self.__shutdown_request = False
        self.queue = Queue()
        self.worker_pool = []
        self.chunklen = chunklen
        self._bind = bind
        if bind:
            self.bind_server_socket()

    def bind_server_socket(self):
        try:
            self.server_socket.bind((self.host, self.port))
        except Exception:
            self.close()
            raise

    def init_workers(self):
        for number in range(self.max_workers):
            self.worker_pool.append(
                Worker(self.queue, self.handle_client_connection, _id=(number + 1))
            )
        return len(self.worker_pool) == self.max_workers

    def start_workers(self):
        [worker.start() for worker in self.worker_pool]

    def stop_workers(self):
        logging.info("Killing workers...")
        for worker in self.worker_pool:
            self.queue.put((None, None))
            worker.__shutdown_request = True
            worker.join(timeout=0.5)

    @staticmethod
    def send_answer(data, client_socket):
        client_socket.sendall(data)
        if len(data) > 70:
            data = data[:70]
        logging.debug(f"Send {data} to {client_socket}")

    def check_file_path(self, request, client_socket) -> Path or None:
        if request.address.endswith("/") and len(request.address) > 3:
            addr = request.address[1:-1]  # get rid of starting and ending /
            file = self.basedir / Path(addr) / Path("index.html")
        elif request.address == "/":
            file = self.basedir / Path("index.html")
        else:
            file = self.basedir / Path(request.address[1:])
        if self.basedir.resolve() not in file.resolve().parents:
            logging.info("Someone tried to escape basedir. Forbidden")
            MyServer.send_answer(make_answer(code=HTTPStatus.FORBIDDEN), client_socket)
            client_socket.close()
            return
        return file

    def get_and_check_request(self, data, client_socket) -> NamedTuple:
        try:
            request = get_request(data)
            return request
        except Exception as exc:
            logging.error(f"Bad request. Exc: {exc}")
            MyServer.send_answer(
                make_answer(code=HTTPStatus.METHOD_NOT_ALLOWED), client_socket
            )
            client_socket.close()

    def read_response(self, client_socket) -> str:
        buf = b""
        delim = b"\r\n\r\n"
        while True:
            r = client_socket.recv(self.chunklen)
            buf += r
            if delim in buf:
                buf = buf.split(delim)[0]
                break
            elif not r:
                raise socket.error("Server closed connection")
        logging.debug(f"Received {buf}")
        return buf.decode("utf-8")

    def handle_client_connection(self, client_socket):
        data = self.read_response(client_socket)
        request = self.get_and_check_request(data, client_socket)
        if not request:
            return
        file = self.check_file_path(request, client_socket)
        if not file:
            return
        if file.is_file():
            answer = make_answer(code=HTTPStatus.OK, file=file, method=request.method)
            logging.debug("Sending back valid answer")
            MyServer.send_answer(answer, client_socket)
        else:
            logging.info(f"No such file {repr(file)}")
            MyServer.send_answer(make_answer(code=HTTPStatus.NOT_FOUND), client_socket)
        client_socket.close()

    def serve_forever(self):
        if not self._bind:
            self.bind_server_socket()
        self.init_workers()
        logging.info("Starting workers...")
        self.start_workers()
        logging.info(f"Listening at {self.host}:{self.port}...")
        logging.info(f"Serving files from: {self.basedir.absolute()}")
        self.server_socket.listen(5)
        while not self.__shutdown_request:
            client_socket, addr = self.server_socket.accept()
            logging.info(f"Connected by {repr(addr)}")
            client_socket.settimeout(self.timeout)
            self.queue.put((client_socket, addr))

    def close(self):
        logging.info("Got a shutdown request...")
        self.__shutdown_request = True
        self.server_socket.close()
        self.stop_workers()
