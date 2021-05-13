import serial
from serial import Serial
import array
from array import array

ser = Serial('/dev/ttyUSB0')
# utf-8 encoding HU99\n, object type=HU(MAN), confidence=99(%)
data = [72] 
data = bytearray(data)

while True:
    try:
        ser.write(data)
        print("transmission success")
        break
    except:
        print("transmission to the bridege has failed")
        