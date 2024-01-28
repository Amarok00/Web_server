import logging
import threading
import uuid


class Worker(threading.Thread):
    """
    Consumes task from queue.
    """

    def __init__(self, queue, handler, _id=str(uuid.uuid4())[:4]):
        threading.Thread.__init__(self)
        self.queue = queue
        self.handler = handler
        self.__id = _id
        self.__shutdown_request = False

    def run(self):
        logging.info(f"Worker {self.__id} started")
        while not self.__shutdown_request:
            client_socket, addr = self.queue.get()
            if client_socket is None and addr is None:
                break
            logging.debug(f"Worker {self.__id} manages request from {addr}")
            try:
                self.handler(client_socket)
            except Exception as exc:
                logging.error(
                    f"Worker {self.__id} cannot handle {addr}. "
                    f"Error: {exc.with_traceback(exc.__traceback__)}"
                )
            else:
                logging.debug(f"Worker {self.__id} finished with {addr}")
            finally:
                try:
                    client_socket.close()
                except Exception:
                    pass
                self.queue.task_done()
