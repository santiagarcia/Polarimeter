import ctypes as C
import tisgrabber as IC
import cv2
import numpy as np
import serial
from scipy.signal import find_peaks
import json
import os
import pandas as pd

# Initialize serial portdm
ser = serial.Serial('COM8', 115200)


def move_motor(motor_number, steps):
    command = f"{motor_number},{steps}\n"
    ser.write(command.encode())


def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    total_irradiance = np.sum(image)
    return total_irradiance


def save_to_json(motor_data):
    try:
        # Convert int64 to int
        motor_data = {k: int(v) for k, v in motor_data.items()}
        print(f"New motor data: {motor_data}")

        # Read existing data
        existing_data = {}
        if os.path.exists('motor_calibration.json'):
            with open('motor_calibration.json', 'r') as json_file:
                existing_data = json.load(json_file)
        print(f"Existing data: {existing_data}")

        # Update existing data with new motor data
        existing_data.update(motor_data)
        print(f"Updated data: {existing_data}")

        # Save back to file
        with open('motor_calibration.json', 'w') as json_file:
            json.dump(existing_data, json_file)
        print('Data saved successfully.')
    except Exception as e:
        print(f'An error occurred: {e}')



step = 50
iterations = 3000
motor_number = 1

irradiance_ = []
position_ = []
position = 0

Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
Camera.StartLive(1)

for it in range(iterations):
    move_motor(motor_number, step*it)
    irradiance = measure_irradiance(Camera)
    print(irradiance)
    irradiance_.append(irradiance)
    position = position + step
    position_.append(position)

Camera.StopLive()
peaks, _ = find_peaks(irradiance_, height=0.94 * max(irradiance_))
steps_per_revolution = step * (peaks[2] - peaks[1]) if len(peaks) > 2 else 0
print(f'Steps per revolution: {steps_per_revolution}')
motor_data = {f'motor_{motor_number}': steps_per_revolution}
save_to_json(motor_data)

df = pd.DataFrame({'Position': position_,'Irradiance':irradiance_})
df.to_csv(f'Calibration_motor_{motor_number}.csv')


print(f'Conversion Rate: {360 / steps_per_revolution} degrees/step')

