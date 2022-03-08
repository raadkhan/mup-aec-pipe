#============================================================================
#
# Filename:  orp_test.py
#
# Purpose: Python script to receives a base64 string from a raspberry pi, and 
#          use UART connection to send the base64 string to Octave by using 
#          ORP(Octave Resource Protocol). This script can also run a HDLC framed
#          commands using ORP. 
#          
#
# Editor: Seungmin, Raad
#
# MIT License
#
# Copyright (c) 2020 Sierra Wireless Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#----------------------------------------------------------------------------
#
# NOTES:
#
# 1. Install Python 3.x
#
# 2. Install the following, using pip3:
#
#    Windows:
#    > pip3 install six pythoncrc pyserial
#
#    Linux
#    > sudo -H pip3 install six pythoncrc pyserial
#

import sys
import os
from time import sleep
import serial
from random import randint
import filecmp 

# Import local versions of orp_protocol and simple_hdlc
if sys.version_info[0] == 2:
    # Python 2 - hack
    mypath = os.path.dirname(os.path.abspath(__file__))
    #sys.path.append(mypath + '/modules')
    from simple_hdlc import HDLC
    from simple_hdlc import __version__ as hdlc_version
    import orp_protocol
    from orp_protocol import decode_response
    from orp_protocol import encode_request
else:
    # Python 3
    from modules.simple_hdlc import HDLC
    from modules.simple_hdlc import __version__ as hdlc_version
    import modules.orp_protocol as orp_protocol
    from modules.orp_protocol import decode_response
    from modules.orp_protocol import encode_request

# Example base64 string of my face 
vps_shot_example = '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'
        
#
# Function to automatically reply to sync
#
def sync_acknowledge(data):
    if sys.version_info[0] == 2:
        checkPacket = data[0]
    else:
        checkPacket = chr(data[0])

    if orp_protocol.ORP_PKT_SYNC_SYN == checkPacket or orp_protocol.ORP_PKT_SYNC_SYNACK == checkPacket:
        request = 'r y 0'
        packet = encode_request(request)
        h.sendFrame(packet.encode())
        print('\nService Restarted\nConnected\n>')

    if orp_protocol.ORP_PKT_NTFY_HANDLER_CALL == checkPacket or orp_protocol.ORP_PKT_RESP_HANDLER_CALL == checkPacket:
        request = 'r C 0'
        packet = encode_request(request)
        h.sendFrame(packet.encode())
        print('\nAcknowledged push notification\n>')

    if orp_protocol.ORP_PKT_NTFY_SENSOR_CALL == checkPacket or orp_protocol.ORP_PKT_RESP_SENSOR_CALL == checkPacket:
        request = 'r B 0'
        packet = encode_request(request)
        h.sendFrame(packet.encode())
        print('\nAcknowledged sensor notification\n>')

#
# Function to receive and decode incoming frames
#
def frame_callback(data):
    decode_response(data)
    
    if auto_ack == True:
        sync_acknowledge(data)

#
# Function to encode the requested message and send to Octave - added by Seungmin
#
def encode_and_send(request):
    packet = encode_request(request)
    if packet != None:
        prestr = 'Sending: ' + packet[0] + packet[1] + str(ord(packet[2])) + str(ord(packet[3]))
        print((prestr + packet[4:75] + '...') if len(packet) > 75  else (prestr + packet[4:]))

        # Wake up the WP UART with a preamble of 0x7E bytes
        s.write(preamble.encode())
        sleep(0.1)
        s.write(preamble.encode())

        h.sendFrame(packet.encode())
        sleep(0.5)
            
#-Program-starts-from-here---------------------------------------------------

# Require minimum version of simple_hdlc
if float(hdlc_version) < 0.3 :
    print('HDLC version: ' + hdlc_version + ' too old. Minimum 0.3 required. Exiting')
    exit()

# Raspberry Pi's USB0 is being used
dev='/dev/ttyUSB0'
baud='9600'

auto_ack = True

# Using the default UART config: 8/N/1
s = serial.Serial(port=dev, baudrate=baud)
h = HDLC(s)
h.startReader(onFrame=frame_callback)

# Provide information to users
print('Welcome to ORP VPS Client. To test, restart the program with an additional argument. "t"' )
print('device: ' + dev + ', speed: ' + baud + ', 8N1')

packet = ''
preamble = '~~'
previous_time = 0

if len(sys.argv) >= 2:
    while (1):
        if sys.version_info[0] == 2:
            request = raw_input('> ')
        else:
            request = input('> ')
        
        # type 't' goes to test and send json file
        if  request == 't':
            print('start testing')
            
            # first it creates data type 'vps_data'
            request = 'create input json vps_data'
            encode_and_send(request)
            
            # then it example json file to 'vps_data' with default value
            request = 'example json vps_data "{"object":"HU", "confidence":99}"'
            encode_and_send(request)
            
            try:
                # send json object 'human' with random confident level between 50 and 100
                while True:
                    vps_data = '{{"object":"HU", "confidence":{0}}}'.format(randint(50, 100))
                    request = 'push json vps_data 0 {0}'.format(vps_data)
                    encode_and_send(request)
                    
                    # send one json file every one mintue
                    sleep(60)

            # To trigger the KeyboardInterrupt, type ctrl+c
            except KeyboardInterrupt:
                print('interrupted testing')
                request = 'delete resource vps_data'
                encode_and_send(request)

        # type 's' will send an example of base64 string
        elif request == 's':
            print('start shooting')
            
            # first creates data type 'vps_shot'
            request = 'create input str vps_shot'
            encode_and_send(request)

            try:
                while True:
                    request = 'push str vps_shot 0 {0}'.format(vps_shot_example)
                    encode_and_send(request)

                    # send one vps_shot every one minute
                    sleep(60)

            # To trigger the KeyboardInterrupt, type ctrl+c
            except KeyboardInterrupt:
                print('interrupted shooting')
                request = 'delete resource vps_shot'
                encode_and_send(request)

        # type 'q' will terminate the program
        elif request == 'q':
            s.close()
            break
        
        # users can also type any commend they want. ex) 'create input str vps_shot' can be manually typed.
        else:        
            # remove trailing whitespace
            request = request.rstrip()
            if request != "":
                packet = encode_request(request)
    
# if there is no additional argument, the program send base64 string if encoded_string.txt is updated
else:
    # first creates data type 'vps_shot'
    request = 'create input str vps_shot'
    encode_and_send(request)

    while (1):   
       # get the encoded_string.txt file's information
       path = './tflite1/encoded_string.txt'
       status=os.stat(path)
       print("waiting for new base64 string...") 
    
       # check if the base64 string is updated by checking the modified time, and if it is modified, send the string to orp
       while (previous_time != status.st_mtime_ns):
           previous_time=status.st_mtime_ns

           #read the encoded_string file
           read_file = open (path, 'r')
           data = read_file.read()
           
           #send one vps_shot every 30seconds
           request = 'push str vps_shot 0 {0}'.format(data)
           encode_and_send(request)
           #print(data)
           sleep(30)
           print("waiting for new base64 string...") 
