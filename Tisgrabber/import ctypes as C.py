import ctypes as C
import tisgrabber as IC
import cv2
import numpy as np
import serial
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Initialize serial port
ser = serial.Serial('COM3', 115200)

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
    peaks, _ = find_peaks(irradiance_list, height=0.9 * max(irradiance_list))
    steps_per_revolution = step_increment*(peaks[1] - peaks[0]) if len(peaks) > 1 else 0
    
    return total_steps, steps_per_revolution

if __name__ == '__main__':
    Camera = IC.TIS_CAM()
    Camera.open('DMx 41BU02 8410421')
    if Camera.IsDevValid() == 1:
        Camera.StartLive(1)
        
        step_increment = 5
        motor_number = 1
        total_steps, steps_per_revolution = calibrate_single_motor(Camera, motor_number, step_increment)
        
        print(f'Steps per revolution: {steps_per_revolution}')
        print(f'Conversion Rate: {360 / steps_per_revolution} degrees/step')
        
        Camera.StopLive()
    else:
        print('No device selected')
