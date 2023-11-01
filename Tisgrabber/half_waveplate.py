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

# Load steps per revolution from JSON file
try:
    with open('motor_calibration.json', 'r') as json_file:
        motor_data = json.load(json_file)
    steps_per_revolution = motor_data.get('motor_4', 0)
except FileNotFoundError:
    print('Calibration file not found. Run calibration first.')
    exit(1)

# Initialize camera
Camera = IC.TIS_CAM()   
Camera.open('DMx 41BU02 8410421')
if Camera.IsDevValid() == 1:
    Camera.StartLive(1)

# Initialize variables
max_intensity = -1
max_position_steps = 0
current_position = 0  # Keep track of the current position

# Rotate and find maximum intensity
for step in range(0, steps_per_revolution * 100, 100):  # Increment of 100, adjust as needed
    move_motor('motor_4', 10)  # Move 100 steps forward
    current_position += 10  # Update current position
    intensity = measure_irradiance(Camera)
    if intensity > max_intensity:
        max_intensity = intensity
        max_position_steps = current_position  # Store the current position as max_position

# Calculate the steps needed to move to the new zero position
new_zero_position = (max_position_steps + int(steps_per_revolution / 4)) % steps_per_revolution
steps_to_new_zero = new_zero_position - current_position  # Calculate the steps needed to reach the new zero position

# Move to the new zero position
move_motor('motor_4', steps_to_new_zero)

# Move to the minimum position again
move_motor('motor_4', -steps_to_new_zero)

print(f'Calibration sequence completed. New zero position is at {new_zero_position} steps.')
print(f'Maximum position is at {max_position_steps} steps.')