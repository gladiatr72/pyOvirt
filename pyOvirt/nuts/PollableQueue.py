# -*- coding: utf-8 -*-

'''
Huzzah, Python Cookbook!  

This bit is taken directly from Section 12.13 of aforementioned volume, and
is actually kinda, quite a bit brilliant. (adapted for python 2.x's use of
old-style classes for Queue.Queue() (sigh)

PollableQueue subclasses Queue and adds one thing: 
    put() writes a single byte of data to one of the sockets after putting
    data on the queue.

    get() reads a single byte of data from the other socket when removing an
    item from the queue

'''
from Queue import Queue
import socket
import os

class PollableQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        # Create a pair of connected sockets
        if os.name == 'posix':
            self._putsocket, self._getsocket = socket.socketpair()
        else:
            # Compatibility on non-POSIX systems
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(('127.0.0.1', 0))
            server.listen(1)
            self._putsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._putsocket, _ = server.accept()
            server.close()

    def fileno(self):
        return self._getsocket.fileno()

    def put(self, item):
        Queue.put(self, item)
        self._putsocket.send(b'x')

    def get(self):
        self._getsocket.recv(1)
        return Queue.get(self)




