import json
import os
import serial
import tisgrabber as IC
import cv2
import numpy as np

# Initialize serial port
ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your actual port


# Function to measure irradiance
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

# Function to measure intensity (replace with your actual measurement function)
def measure_intensity():
    return 0  # Replace with actual measurement

# Load steps per revolution from JSON file
try:
    with open('Tisgrabber/motor_calibration.json', 'r') as json_file:
        motor_data = json.load(json_file)
    steps_per_revolution = motor_data.get('motor_1', 0)
except FileNotFoundError:
    print('Calibration file not found. Run calibration first.')
    exit(1)

# Initialize variables
max_intensity = -1
max_position_steps = 0
# Initialize camera
Camera = IC.TIS_CAM()

# Rotate and find maximum intensity
for step in range(0, steps_per_revolution, 10):  # Increment of 10, adjust as needed
    move_motor('motor_1', step)
    measure_irradiance(Camera)
    if intensity > max_intensity:
        max_intensity = intensity
        max_position_steps = step

# Rotate 90 degrees from maximum to find minimum
new_zero_position = (max_position_steps + int(steps_per_revolution / 4)) % steps_per_revolution
move_motor('motor_1', new_zero_position)

print(f'Calibration sequence completed. New zero position is at {new_zero_position} steps.')
