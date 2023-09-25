from machine import Pin, UART
import time


motor_pins1 = [32, 33, 25, 26] # Corresponding to D32, D33, D25, D26
motor_pins2 = [27, 14, 12, 13] # Corresponding to D27, D14, D12, D13
motor_pins3 = [15, 2, 4, 16]   # Corresponding to D15, D2, D4, D16
motor_pins4 = [5, 18, 19, 21] # Corresponding to D5, D18, D19, D21


boudRate = 115200
comPort = 9

class StepperMotor:
    def __init__(self, pins):
        self.pins = [Pin(p, Pin.OUT) for p in pins]
        self.sequence = [
            (1, 0, 0, 1),
            (1, 0, 0, 0),
            (1, 1, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 1),
        ]
        self.step_count = len(self.sequence)
        self.current_step = 0

    def step(self, direction):
        self.current_step += direction
        self.current_step %= self.step_count
        for pin, value in zip(self.pins, self.sequence[self.current_step]):
            pin.value(value)

    def rotate(self, steps, direction=1, delay=3):
        for _ in range(steps):
            self.step(direction)
            time.sleep_ms(delay)
        self.stop()

    def stop(self):
        for pin in self.pins:
            pin.value(0)


def initialize_uart(port, baud_rate):
    return UART(port, baud_rate)

def receive_command(uart):
    if uart.any():
        command = uart.readline().decode('utf-8').strip()
        # Echo the command back
        uart.write(command + '\n')
        return [int(x) for x in command.split(',')]
    return None


# Initialize four stepper motors
#motor1 = StepperMotor(motor_pins1)
#motor2 = StepperMotor(motor_pins2)
#motor3 = StepperMotor(motor_pins3)
#motor4 = StepperMotor(motor_pins4)


uart = initialize_uart(comPort, boudRate)

motor1 = StepperMotor(motor_pins1)
motor2 = StepperMotor(motor_pins2)
motor3 = StepperMotor(motor_pins3)
motor4 = StepperMotor(motor_pins4)

while True:
    commands = receive_command(uart)
    if commands:
        m1_steps, m2_steps, m3_steps, m4_steps = commands
        motor1.rotate(m1_steps)
        motor2.rotate(m2_steps)
        motor3.rotate(m3_steps)
        motor4.rotate(m4_steps)

