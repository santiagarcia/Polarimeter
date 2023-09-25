import serial
import random
import time

# Initialize serial connection (replace 'COM3' with your port)
ser = serial.Serial('COM14', 115200, timeout=1)

# Function to move a random motor a random number of steps
def move_random_motor():
    motor_number = random.randint(2, 2)  # Random motor number between 1 and 4
    steps = random.randint(2000, 5000)  # Random steps between 2000 and 10000

    # Create the command string
    command = f"{motor_number},{steps}\n"

    # Send the command
    ser.write(command.encode('utf-8'))

    # Read and print the ESP32's response
    response = ser.readline().decode('utf-8').strip()
    print(f"ESP32 says: {response}")

    # Wait for the "Done" message
    while True:
        done_message = ser.readline().decode('utf-8').strip()
        if done_message == "Done":
            print("ESP32 says: Done")
            break

# Main loop to move random motors
while True:
    move_random_motor()
    time.sleep(3)  # Wait for 2 seconds before the next command
