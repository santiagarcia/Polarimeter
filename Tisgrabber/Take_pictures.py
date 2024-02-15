import json
import serial
import tisgrabber as IC
import cv2
import numpy as np
import time

# Initialize serial port
ser = serial.Serial('COM8', 115200)  # Replace 'COM14' with your actual port


# Function to measure irradiance
def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = np.array(image)[:,:,0]
    # image = cv2.flip(image, 0)
    # total_irradiance = np.sum(image)
    return image


# Function to move motor
def move_motor(motor_number, steps):
    command = f'{motor_number},{steps}\n'
    ser.write(command.encode())
    # WAIT FOR DONE MESSAGE FROM SERIAL PORT
    while True:
        if ser.in_waiting > 0:
            line = ser.readline()
            if line.decode().strip() == 'Done!':
                break
        else:
            continue


# Initialize camera
Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
if Camera.IsDevValid() == 1:
    Camera.StartLive(1)

# Initialize variables
max_intensity = -1
max_position_steps = 0
current_position = 0  # Keep track of the current position

# Define desired angles
Desire_angles = np.array([[0, 0, 90, 90], [0, 0, 90, 0], [0, 0, -45, 45], [0, 0, -45, -45],
                          [0, 0, 0, -45], [0, 0, 0, 45], [45, 90, 90, 90], [45, 90, 90, 0], [45, 90, -45, 45],
                          [45, 90, -45, -45], [45, 90, 0, -45], [45, 90, 0, 45], [-22.5, -45, 90, 90],
                          [-22.5, -45, 90, 0], [-22.5, -45, -45, 45], [-22.5, -45, -45, -45], [-22.5, -45, 0, -45],
                          [-22.5, -45, 0, 45], [22.5, 45, 90, 90], [22.5, 45, 90, 0], [22.5, 45, -45, 45],
                          [22.5, 45, -45, -45], [22.5, 45, 0, -45], [22.5, 45, 0, 45], [22.5, 90, 90, 90],
                          [22.5, 90, 90, 0], [22.5, 90, -45, 45], [22.5, 90, -45, -45], [22.5, 90, 0, -45],
                          [22.5, 90, 0, 45], [45, 90, 90, 90], [45, 90, 90, 0], [45, 90, -45, 45], [45, 90, -45, -45],
                          [45, 90, 0, -45], [45, 90, 0, 45], [0, 0, 0, 0]])

# Initialize data volume
DataI = np.zeros((960, 1280, len(Desire_angles)))

# Rotate and image acquisition
for k in range(len(Desire_angles)):
    for m in range(4):
        # Load steps per revolution from JSON file
        try:
            with open('motor_calibration.json', 'r') as json_file:
                motor_data = json.load(json_file)
            steps_per_revolution = motor_data.get(f'motor_{m + 1}', 0)
        except FileNotFoundError:
            print('Calibration file not found. Run calibration first.')
            exit(1)

        # Define current desired angle
        desired_angle = Desire_angles[k, m]

        # Move motor to current desired angle
        move_motor(f'motor_{m + 1}', desired_angle * steps_per_revolution // 360)
        # check if motor has stoppped
        # Measure irradiance
        irradiance = measure_irradiance(Camera)
        time.sleep(0.1)
        # Store the image
        DataI[:, :, k] = irradiance

# Save data
np.save('PS_MSPH_GABOR.npy', DataI)

print('Data acquisition completed.')
