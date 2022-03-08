import serial
from serial import Serial
import array
from array import array

ser = Serial('/dev/ttyUSB0')
# utf-8 encoding HU99\n, object type=HU(MAN), confidence=99(%)
data = [72, 85, 57, 57, 10] 
data = bytearray(data)
ser.write(data)
