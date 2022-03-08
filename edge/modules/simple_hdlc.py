#!/usr/bin/python
# coding: utf8

# License posted here: https://github.com/wuttem/simple-hdlc/blob/master/LICENSE
# and copied below:
#
# MIT License
#
# Copyright (c) 2016 wuttem

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__version__ = '0.3'

import sys
import logging
import struct
import time
import six
import binascii
from threading import Thread
from PyCRC.CRCCCITT import CRCCCITT

logger = logging.getLogger(__name__)


ESCAPE_CHAR = 0x7d
END_CHAR = 0x7e
ESCAPE_MASK = 0x20

MAX_FRAME_LENGTH = 1024


def bin_to_hex(b):
    if sys.version_info[0] == 2:
        return b.encode("hex")
    return b.hex()


def calcCRC(data):
    crc = CRCCCITT("FFFF").calculate(six.binary_type(data))
    b = bytearray(struct.pack(">H", crc))
    return b


class Frame(object):
    STATE_READ = 0x01
    STATE_ESCAPE = 0x02

    def __init__(self):
        self.finished = False
        self.error_message = None
        self.error = False
        self.state = self.STATE_READ
        self.data = bytearray()
        self.crc = bytearray()
        self.reader = None

    def __len__(self):
        return len(self.data)

    def reset(self):
        self.data = bytearray()
        self.finished = False
        self.error = False
        self.state = self.STATE_READ

    def addByte(self, b):
        if b == END_CHAR:
            logger.debug("frame start")
            if self.state == self.STATE_ESCAPE:
                return self.abort("invalid framing (got end in escapemode)")
            else:
                # maybe finished
                if len(self.data) >= 3:
                    return self.finish()
            return False

        if self.state == self.STATE_ESCAPE:
            self.state = self.STATE_READ
            b = b ^ 0x20
        elif (b == ESCAPE_CHAR):
            self.state = self.STATE_ESCAPE
            return False

        self.data.append(b)

        if len(self.data) > MAX_FRAME_LENGTH:
            return self.abort("frame to big")

        return False

    def finish(self):
        res = self._checkCRC()
        self.crc = self.data[-2:]
        self.data = self.data[:-2]
        if res:
            self.error = False
            self.finished = True
            return True
        return self.abort("Invalid Frame (CRC FAIL)")

    def abort(self, message):
        self.error = True
        self.finished = True
        self.error_message = message
        return True

    def _checkCRC(self):
        data_without_crc = self.data[:-2]
        crc = self.data[-2:]
        res = bool(crc == calcCRC(data_without_crc))
        if not res:
            c1 = six.binary_type(crc)
            c2 = six.binary_type(calcCRC(data_without_crc))
            logger.warning("invalid crc %s != %s <- our calculation",
                           bin_to_hex(c1), bin_to_hex(c2))
        return res

    def toString(self):
        return six.binary_type(self.data)


class HDLC(object):
    def __init__(self, serial, reset=True):
        self.serial = serial
        self.current_frame = None
        self.last_frame = None
        self.frame_callback = None
        self.error_callback = None
        self.running = False
        logger.debug("HDLC INIT: %s bytes in buffer", self.serial.in_waiting)
        if reset:
            self.serial.reset_input_buffer()

    @classmethod
    def toBytes(cls, data):
        return bytearray(data)

    def sendFrame(self, data):
        bs = self._encode(self.toBytes(data))
        logger.info("Sending Frame: %s", bin_to_hex(bs))
        res = self.serial.write(bs)
        logger.info("Send %s bytes", res)

    def _onFrame(self, frame):
        self.last_frame = frame
        s = self.last_frame.toString()
        logger.info("Received Frame: %s", bin_to_hex(s))
        if self.frame_callback is not None:
            self.frame_callback(s)

    def _onError(self, frame):
        self.last_frame = frame
        s = self.last_frame.toString()
        logger.warning("Frame Error: %s", bin_to_hex(s))
        if self.error_callback is not None:
            self.error_callback(s)

    def _readBytes(self, size):
        cnt = 0
        while cnt < size:
            b = six.binary_type(self.serial.read(1))
            if len(b) < 1:
                return False
            cnt += len(b)
            res = self._readByte(six.byte2int(b))
            if res:
                return True

    def _readByte(self, b):
        assert 0 <= b <= 255

        if not self.current_frame:
            self.current_frame = Frame()

        res = self.current_frame.addByte(b)
        if res:
            if self.current_frame.error:
                self._onError(self.current_frame)
                self.current_frame = None
            else:
                self._onFrame(self.current_frame)
                self.current_frame = None
        return res

    def readFrame(self, timeout=5):
        timer = time.time() + timeout
        while time.time() < timer:
            i = self.serial.in_waiting
            if i < 1:
                time.sleep(0.0001)
                continue

            res = self._readBytes(i)

            if res:
                if self.last_frame.finished:
                    if not self.last_frame.error:
                        # Success
                        s = self.last_frame.toString()
                        return s
                    # error
                    raise ValueError(self.last_frame.error_message)
                raise RuntimeError("Unexpected Framing Error")
        raise RuntimeError("readFrame timeout")

    @classmethod
    def _encode(cls, bs):
        data = bytearray()
        data.append(0x7E)
        crc = calcCRC(bs)
        bs = bs + crc
        for byte in bs:
            if byte == 0x7E or byte == 0x7D:
                data.append(0x7D)
                data.append(byte ^ 0x20)
            else:
                data.append(byte)
        data.append(0x7E)
        return bytes(data)

    def _receiveLoop(self):
        while self.running:
            i = self.serial.in_waiting
            if i < 1:
                time.sleep(0.001)
                continue
            res = self._readBytes(i)

    def startReader(self, onFrame, onError=None):
        if self.running:
            raise RuntimeError("reader already running")
        self.reader = Thread(target=self._receiveLoop)
        self.reader.setDaemon(True)
        self.frame_callback = onFrame
        self.error_callback = onError
        self.running = True
        self.reader.start()

    def stopReader(self):
        self.running = False
        self.reader.join()
        self.reader = None
