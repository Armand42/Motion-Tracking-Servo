# sudo chmod 666 /dev/ttyACM0 
import numpy as np
import cv2
from pyfirmata import Arduino, util
from pyfirmata import ArduinoMega
from pyfirmata import INPUT, OUTPUT, PWM
import time
import math
import serial #Import Serial Library
board = ArduinoMega('/dev/ttyACM0')
servoX = board.get_pin('d:9:s')
servoY = board.get_pin('d:7:s')

def blinkGreen():
    board.digital[13].write(1)

def blinkRed():
    board.digital[12].write(1)
def moveServoX(v):
    servoX.write(v)
def moveServoY(v):
    servoY.write(v)
def gstreamer_pipeline (capture_width=3280, capture_height=2464, display_width=820, display_height=616, framerate=21, flip_method=0) :   
    return ('nvarguscamerasrc ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

    


# Initialize webcam
#cap = cv2.VideoCapture(-1)
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
# take first frame of the video
ret, frame = cap.read()
print(type(frame))

# setup default location of window
r, h, c, w = 240, 100, 400, 160 
track_window = (c, r, w, h)

# Crop region of interest for tracking
roi = frame[r:r+h, c:c+w]

# Convert cropped window to HSV color space
hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# Create a mask between the HSV bounds
lower_purple = np.array([40,0,0])
upper_purple = np.array([75,255,255])
mask = cv2.inRange(hsv_roi, lower_purple, upper_purple)

# Obtain the color histogram of the ROI
roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0,180])

# Normalize values to lie between the range 0, 255
cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

# Setup the termination criteria
# We stop calculating the centroid shift after ten iterations 
# or if the centroid has moved at least 1 pixel
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

angleX = 0
angleY = 0
while True:
    
    # Read webcam frame
    ret, frame = cap.read()

    if ret == True:
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate the histogram back projection 
        # Each pixel's value is it's probability
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

        # apply meanshift to get the new location
        ret, track_window = cv2.meanShift(dst, track_window, term_crit)

        # Draw it on image
        x, y, w, h = track_window
        img2 = cv2.rectangle(frame, (x,y), (x+w, y+h), 255, 2)  
        board.digital[8].write(0)
       # moveServo(xx)
        if ( x < 190):
            angleX+= 5
            if (angleX > 200):
                angleX=200
            moveServoX(angleX)

        if (x > 210):
            angleX-= 5
            if (angleX < 10):
                angleX=10
            moveServoX(angleX)
        
        if (y < 190):
            angleY+= 5
            if (angleY > 200):
                angleY = 200
            moveServoY(angleY)

        if (y > 210):
            angleY-= 5
            if (angleY < 10):
                angleY = 10
            moveServoY(angleY)
        
        print("angleX====",angleX)
        print("angleY====",angleY)
        #if (x == 480):
         #   board.digital[13].write(0)

        #if (x - c < 80 or x - c < 0):
         #   blinkGreen()
          #  board.digital[8].write(0)
        #blinkRed()

        blinkGreen()
        print("x=",x,"y=", y,"x+w=", x+w,"y+h=", y+h)         
        #print(x, c)
        cv2.imshow('Meansift Tracking', img2)
        
        if cv2.waitKey(1) == 13: #13 is the Enter Key
             break

    else:
        break

cv2.destroyAllWindows()
cap.release()
blinkRed()
board.digital[13].write(0)
