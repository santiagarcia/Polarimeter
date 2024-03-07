# # **Calibration of a complete Mueller polarimeter**
# *Author*: @ mariajloperaa
#
# ## This notebook contains all the elements to calibrate and use the automatic Mueller polarimeter. The calibration assumes a vertical polarized light source.
# The polarimeter consists on a polarized light source, on a PSG a $\lambda/2$ followed by a $\lambda/4$, then after the sample a $\lambda/4$ followed by a linear polarizer.
#
# The **initial calibration** consists on finding the steps per revolution or the steps per degree of each motor.
# Later the elements should be positioned as follows: Linear Polarizer, $\lambda/2 (PSG)$, $\lambda/4 (PGS)$, $\lambda/4 (PSA)$ following the commands regarding the **second callibration**.


from polarimeter_functions import *
import time
import serial
import tisgrabber as IC
import numpy as np
import pandas as pd
import cv2 as cv

# Default parameters

# step = 50
# iterations = 800

# Initialize serial port
# ser = serial.Serial('COM8', 115200)

# Move each motor to make sure all are connected and working
# move_motor(ser, 1, 200)
# move_motor(ser, 2, 200)
# move_motor(ser, 3, 200)
# move_motor(ser, 4, 200)
# ser.close()
# print('Closing port')
# Initialize camera
Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
Camera.StartLive(1)
Camera.SnapImage()
measure_irradiance(Camera)



# Calibration 2: Finding the zero or fast axis of each of the polarization elements
calibration = pd.read_csv('complete_calibration.csv')
d_m1 = calibration['1'][0]
d_m2 = calibration['2'][0]
d_m3 = calibration['3'][0]
d_m4 = calibration['4'][0]


print('Opening port')
ser = serial.Serial('COM8', 115200)

# Linear polarizer at 90 degrees
calibrate_element(ser, Camera, 4, d_m4)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# PSG  lambda/2’s fast axis aligned to the polarization axis of the source, zero degrees
calibrate_element(ser, Camera, 1, d_m1)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)
# PSG  lambda/4’s fast axis aligned to the polarization axis of the source, zero degrees
calibrate_element(ser, Camera, 2, d_m2)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# *PSA* $\lambda /4$'s fast axis aligned to the polarization axis of the source, *zero degrees*
calibrate_element(ser,Camera, 3, d_m3)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# The intensity should remain at zero, then the linear polarized is shifted again to its zero.
measure_irradiance(Camera)
move_motor(ser, 4, d_m4 * 90)
measure_irradiance(Camera)