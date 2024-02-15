# %%
import json
import os
import serial
import tisgrabber as IC
import cv2
import numpy as np
import time

# Initialize serial port
ser = serial.Serial('COM8', 115200)
motor = 'motor_4'


def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    total_irradiance = np.sum(image)
    return total_irradiance


# Function to move motor
def move_motor(motor_number, steps):
    command = f"{motor_number},{steps}\n"
    ser.write(command.encode())


# Load steps per revolution from JSON file
try:
    with open('motor_calibration.json', 'r') as json_file:
        motor_data = json.load(json_file)
    steps_per_revolution = motor_data.get(motor, 0)
except FileNotFoundError:
    print('Calibration file not found. Run calibration first.')
    exit(1)

# Initialize camera
Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
Camera.StartLive(1)



# Move the motor to an initial position
initial_position = 0
move_motor(motor, initial_position)

# Initialize variables to store the minimum irradiance and its corresponding motor position
min_irradiance = float('inf')
min_position = 0
current_position = 0

# steps_per_revolution
step = 50

max_iterations = int(steps_per_revolution)
# Perform iterative calibration
for iteration in range(max_iterations):
    # Move the motor by a certain number of steps
    move_motor(motor, step)

    # Measure the irradiance at the current position
    current_irradiance = measure_irradiance(Camera)
    current_position += 1

    # Check if the current irradiance is lower than the minimum found so far
    if current_irradiance < min_irradiance:
        min_irradiance = current_irradiance
        min_position = current_position  # Replace with the actual method to get the motor position
        print(f"Calibrated zero position: {min_position}")

max_pos = 0.25 * steps_per_revolution + min_position
# Move the motor to the position with the minimum irradiance
# print('Moving to zero position')
# move_motor(motor, min_position*step)
# pause()

print('Moving to max position')
move_motor(motor, max_pos*step)
time.sleep(5)
print(f"Done")
