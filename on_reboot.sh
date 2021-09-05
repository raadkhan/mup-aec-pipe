#!/bin/bash

sleep 10 && (python3 /home/pi/code/mup-aec-pipe/camera_test.py) &
#sleep 20 && (python3 /home/pi/code/mup-aec-pipe/tflite1/TFLite_detection_webcam.py) &
sleep 20  && (python3 /home/pi/code/mup-aec-pipe/orp_test.py) &


