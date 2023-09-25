from Serial_Stepper import StepperMotorController  # Importa la clase

try:
    controller = StepperMotorController()  # Auto-detecta Arduino
    controller.move_motor(1, 2000)  # Mueve el motor 1, 200 pasos
    controller.close()  # Cierra la conexión serial
except Exception as e:
    print(f'Error: {e}')
