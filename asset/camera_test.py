from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30
camera.rotation = 180 #rotating angle 5 degrees.

'''preview on raspberry pi connected screen. This doesn't work through VNC/SSH'''
camera.start_preview() #at least 2nds to camera's light sensor to be ready
sleep(5)
camera.capture('/home/pi/Desktop/image.jpg')
sleep(5)
camera.capture('/home/pi/Desktop/image2.jpg')
camera.stop_preview()

'''testing recording'''
# camera.start_preview()
# sleep(5)
# camera.start_recording('/home/pi/Desktop/video.h264')
# sleep(10)
# camera.stop_recording('/home/pi/Desktop/video.h264')
# camera.stop_preview()

#import cv2
#import base64

#starting to capture the video from port 0
cap= cv2.VideoCapture(0)

#return value(retval) = true, if image is captured. Captured image will be saved as "image"
retval, image = cap.read()

#stop capturing the video
cap.release()

#Convert captured image to JPG(binary file)
retval, buffer = cv2.imencode('.jpg', image)

#convert to base64 encoding and show start first 80 data
jpg_as_text = base64.b64encode(buffer)
print(jpg_as_text[:80]) 

#convert back to binary. This is just for reference. This part must be done in octave
#jpg_origianl=base64.b64decode(jpg_as_text)


