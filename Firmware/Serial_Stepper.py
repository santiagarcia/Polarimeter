import serial
import time
import serial.tools.list_ports

class StepperMotorController:
    def __init__(self, baud_rate=115200):
        self.ser = self.auto_detect_arduino(baud_rate)
        time.sleep(2)  # Wait for Arduino to initialize

    def auto_detect_arduino(self, baud_rate):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if 'Arduino' in p.description:
                return serial.Serial(p.device, baud_rate)
        raise Exception('Arduino device not found')

    def move_motor(self, motor_number, steps):
        command = f'{motor_number},{steps}\n'
        self.ser.write(command.encode())

    def close(self):
        self.ser.close()

# Example usage
if __name__ == '__main__':
    try:
        controller = StepperMotorController()  # Auto-detects Arduino
        controller.move_motor(1, 200)  # Move motor 1 by 200 steps
        controller.close()
    except Exception as e:
        print(f'Error: {e}')