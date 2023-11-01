import json
import os
import serial
import tisgrabber as IC
import cv2
import numpy as np

# Initialize serial port
ser = serial.Serial('COM3', 115200)

# Function to measure irradiance
def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    total_irradiance = np.sum(image)
    return total_irradiance

# Function to move motor
def move_motor(motor_number, steps):
    command = f'{motor_number},{steps}\n'
    ser.write(command.encode())

# Load steps per revolution from JSON file
def load_motor_data(motor_number):
    try:
        with open('motor_calibration.json', 'r') as json_file:
            motor_data = json.load(json_file)
        return motor_data.get(motor_number, 0)
    except FileNotFoundError:
        print('Calibration file not found. Run calibration first.')
        exit(1)

# Save calibration data to JSON file
def save_calibration_data(motor_number, max_position, min_position):
    calibration_data = {motor_number: {'max': max_position, 'min': min_position}}
    try:
        with open('motor_calibration.json', 'r') as json_file:
            existing_data = json.load(json_file)
        existing_data.update(calibration_data)
    except FileNotFoundError:
        existing_data = calibration_data
    with open('motor_calibration.json', 'w') as json_file:
        json.dump(existing_data, json_file)

# Main function for calibration
def calibrate_motor(motor_number):
    steps_per_revolution = load_motor_data(motor_number)
    Camera = IC.TIS_CAM()
    Camera.open('DMx 41BU02 8410421')
    if Camera.IsDevValid() == 1:
        Camera.StartLive(1)
    max_intensity = -1
    max_position_steps = 0
    current_position = 0
    for step in range(0, steps_per_revolution * 100, 100):
        move_motor(motor_number, 10)
        current_position += 10
        intensity = measure_irradiance(Camera)
        if intensity > max_intensity:
            max_intensity = intensity
            max_position_steps = current_position
    new_zero_position = (max_position_steps + int(steps_per_revolution / 4)) % steps_per_revolution
    steps_to_new_zero = new_zero_position - current_position
    move_motor(motor_number, steps_to_new_zero)
    save_calibration_data(motor_number, max_position_steps, new_zero_position)
    print(f'Calibration sequence completed for {motor_number}. New zero position is at {new_zero_position} steps.')

# Calibrate multiple motors
motor = 'motor_4'  # Add your motor numbers here
calibrate_motor(motor)