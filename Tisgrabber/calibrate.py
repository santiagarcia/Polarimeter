import ctypes as C
import tisgrabber as IC
import cv2
import numpy as np
import serial
# Initialize serial port
ser = serial.Serial('COM3', 115200)  # Replace 'COM3' with your actual port

def move_motor(motor_number, steps):
    command = f"{motor_number},{steps}\n"
    ser.write(command.encode())

def calibrate_stepper(Camera, motor_number):
    min_intensity = float('inf')
    max_intensity = 0
    min_step = 0
    max_step = 0

    for step in range(0, 360, 5):  # Assuming 1 step = 1 degree
        move_motor(motor_number, step)
        
        # Measure irradiance
        irradiance = measure_irradiance(Camera)
        
        # Update min and max
        if irradiance < min_intensity:
            min_intensity = irradiance
            min_step = step
        if irradiance > max_intensity:
            max_intensity = irradiance
            max_step = step

    return min_step, max_step

def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    total_irradiance = np.sum(image)
    return total_irradiance
def calibrate_single_motor(Camera, motor_number):
    """
    Calibrate a single stepper motor to find the steps corresponding to minimum and maximum irradiance.
    The motor will complete a full 360-degree rotation to confirm the pattern repeats.
    
    Parameters:
        Camera (IC.TIS_CAM): The camera object for capturing images.
        motor_number (int): The number of the motor to calibrate.
        
    Returns:
        int: The number of steps it took to complete a full 360-degree rotation.
    """
    min_intensity = float('inf')
    max_intensity = 0
    min_step = 0
    max_step = 0
    total_steps = 0  # To count the total steps for a full 360-degree rotation

    # First pass to find min and max
    for step in range(0, 360, 5):  # Assuming 1 step = 1 degree
        move_motor(motor_number, step)
        total_steps += 5  # Increment the total steps
        
        # Measure irradiance
        irradiance = measure_irradiance(Camera)
        
        # Update min and max
        if irradiance < min_intensity:
            min_intensity = irradiance
            min_step = step
        if irradiance > max_intensity:
            max_intensity = irradiance
            max_step = step

    # Move to the starting point (min intensity)
    move_motor(motor_number, min_step)
    
    # Second pass to confirm the pattern repeats
    for step in range(min_step, min_step + 360, 5):
        move_motor(motor_number, step % 360)  # Wrap around to 0 after 360
        total_steps += 5  # Increment the total steps

    # Move to the maximum intensity position
    move_motor(motor_number, max_step)

    return total_steps

if __name__ == '__main__':
    Camera = IC.TIS_CAM()
    Camera.open('DMx 41BU02 8410421')
    if Camera.IsDevValid() == 1:
        Camera.StartLive(1)
        
        # Calibrate each stepper motor
        for motor_number in [1, 2, 3, 4]:
            min_step, max_step = calibrate_stepper(Camera, motor_number)
            print(f"Motor {motor_number}: Min at step {min_step}, Max at step {max_step}")
        
        Camera.StopLive()
    else:
        print('No device selected')

