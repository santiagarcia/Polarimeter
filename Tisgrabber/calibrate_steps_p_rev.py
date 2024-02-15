import ctypes as C
import tisgrabber as IC
import cv2
import numpy as np
import serial
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import json
import os
# Initialize serial portdm
ser = serial.Serial('COM8', 115200)

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
irradiance_list = []
line, = ax.plot(irradiance_list)
plt.show()

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
        
def calibrate_single_motor(Camera, motor_number, step_increment):
    total_steps = 0
    irradiance_list = []
    avg_irradiance = 0
    prev_avg_irradiance = 0

    while len(irradiance_list) < 500 or abs(avg_irradiance - prev_avg_irradiance) > 0.01 * avg_irradiance:
        move_motor(motor_number, total_steps)
        print(len(irradiance_list))
        # Measure and plot irradiance
        irradiance = measure_irradiance(Camera)
        irradiance_list.append(irradiance)
        line.set_ydata(irradiance_list)
        line.set_xdata(range(len(irradiance_list)))
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(0.1)
        
        # Update average irradiance
        prev_avg_irradiance = avg_irradiance
        avg_irradiance = np.mean(irradiance_list[-10000:])
        
        total_steps += step_increment

    # Find peaks to get steps per revolution
    peaks, _ = find_peaks(irradiance_list, height=0.94 * max(irradiance_list))
    steps_per_revolution = step_increment*(peaks[2] - peaks[1]) if len(peaks) > 2 else 0

    print(f'Steps per revolution: {steps_per_revolution}')
    ## Save irradiance_list to file
    np.savetxt('irradiance_list.csv', irradiance_list, delimiter=',')
    
    
    return total_steps, steps_per_revolution


def average_calibration(Camera, motor_number, step_increment, num_trials=3):
    steps_per_revolution_list = []
    for i in range(num_trials):
        print(f"Running calibration trial {i + 1}...")
        _, steps_per_revolution = calibrate_single_motor(Camera, motor_number, step_increment)
        steps_per_revolution_list.append(steps_per_revolution)
    
    avg_steps_per_revolution = int(np.mean(steps_per_revolution_list))
    return avg_steps_per_revolution

if __name__ == '__main__':
    Camera = IC.TIS_CAM()
    Camera.open('DMx 41BU02 8410421')
    if Camera.IsDevValid() == 1:
        Camera.StartLive(1)
        
        step_increment = 1000
        motor_number = 4
        num_trials = 2  # Number of times to run the calibration
        
        avg_steps_per_revolution = average_calibration(Camera, motor_number, step_increment, num_trials)
        
        motor_data = {f'motor_{motor_number}': avg_steps_per_revolution}
        save_to_json(motor_data)
        
        print(f'Average steps per revolution: {avg_steps_per_revolution}')
        print(f'Conversion Rate: {360 / avg_steps_per_revolution} degrees/step')
        
        Camera.StopLive()
    else:
        print('No device selected')
        
        
        