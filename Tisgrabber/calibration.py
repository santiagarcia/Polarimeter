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

step = 50
iterations = 500

# Initialize serial port
ser = serial.Serial('COM8', 115200)

# Move each motor to make sure all are connected and working
# move_motor(ser, 1, 200)
# move_motor(ser, 2, 200)
# move_motor(ser, 3, 200)
# move_motor(ser, 4, 200)
ser.close()
print('Closing port')
# Initialize camera
Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
Camera.StartLive(1)
Camera.SnapImage()
measure_irradiance(Camera)

# Calibration 1, Motor 1
print('Opening port')
# ser = serial.Serial('COM8', 115200)
ser = serial.Serial('COM8', baudrate=115200)
time.sleep(3)

motor_1 = calibration_spr(ser, Camera, 1, step, iterations)
# motor_1 = pd.read_csv('Calibration_motor_1.csv',index_col=0)
d_m1 = steps_per_degree(motor_1, 1)
ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# Calibration 1, Motor 1
motor_2 = calibration_spr(ser, Camera, 2, step, iterations)
# motor_2 = pd.read_csv('Calibration_motor_2.csv',index_col=0)
d_m2 = steps_per_degree(motor_2, 2)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# Calibration 1, Motor 1
motor_3 = calibration_spr(ser, Camera, 3, step, iterations)
# motor_3 = pd.read_csv('Calibration_motor_3.csv',index_col=0)
d_m3 = steps_per_degree(motor_3, 3)

ser.close()
print('Closing port')
print('Opening port')
ser = serial.Serial('COM8', 115200)

# Calibration 1, Motor 1
motor_4 = calibration_spr(ser, Camera, 4, step, iterations)
# motor_4 = pd.read_csv('Calibration_motor_4.csv',index_col=0)
d_m4 = steps_per_degree(motor_4, 4)


