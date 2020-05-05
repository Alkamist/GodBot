import zmq
import binascii
import os
import sys
import socket

def chunk(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def parse_message(message):
    lines = message.splitlines()

    assert(len(lines) % 2 == 0)

    diffs = chunk(lines, 2)

    for diff in diffs:
        diff[1] = binascii.unhexlify(diff[1].zfill(8))

    return diffs

class MemoryWatcher:
    def __init__(self, port=5555):
        print('Creating MemoryWatcher.')
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://127.0.0.1:%d" % port)
        self.messages = None

    def get_messages(self):
        if self.messages is None:
            message = self.socket.recv()
            message = message.decode('utf-8')
            self.messages = parse_message(message)

        return self.messages

    def advance(self):
        self.socket.send(b'')
        self.messages = None