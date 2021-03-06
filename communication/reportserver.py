__author__ = 'susperius'


import logging

import gevent
import gevent.monkey
import gevent.socket as socket
from gevent.server import StreamServer

gevent.monkey.patch_all()


class ReportServer:
    def __init__(self, port, task_queue):
        self._port = port
        self._serving = False
        self._serving_greenlet = None
        self._report_server = None
        self._logger = logging.getLogger(__name__)
        self._task_queue = task_queue

    def __report_receiver(self, sock, address):
        report = ""
        fp = sock.makefile("rb")
        while True:
            line = fp.readline()
            if not line:
                break
            report += line
            fp.flush()
        sock.shutdown(socket.SHUT_WR)
        sock.close()
        self._task_queue.put((address[0], report))

    def __serve(self):
        self._logger.info("[Report Server] initialized on port " + str(self._port) + " ...")
        self._report_server = StreamServer(('', self._port), self.__report_receiver)
        self._report_server.serve_forever()
        gevent.sleep(0)

    def serve(self):
        if not self._serving:
            self._serving_greenlet = gevent.spawn(self.__serve)
            self._serving = True
            gevent.sleep(0)
        else:
            pass
