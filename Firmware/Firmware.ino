#include "StepperMotor.h"  // Importing the StepperMotor library
#include "Arduino.h"
#include "BluetoothSerial.h"  // Importing the BluetoothSerial library

BluetoothSerial SerialBT;  // Create BluetoothSerial instance

// Initialize StepperMotor instances
StepperMotor motor1(32, 33, 25, 26);
StepperMotor motor2(27, 14, 12, 13);
StepperMotor motor3(15, 2, 4, 16);
StepperMotor motor4(5, 18, 19, 21);

void setup() {
  Serial.begin(115200);  // Initialize Serial communication
  SerialBT.begin("ESP32_BT");  // Initialize Bluetooth with device name "ESP32_BT"
  Serial.println("The device started, now you can control it via Serial or Bluetooth!");
}

void loop() {
  processSerial(Serial);  // Process data from Serial (USB)
  processSerial(SerialBT);  // Process data from Bluetooth
}

void processSerial(Stream &inputStream) {
  if (inputStream.available() > 0) {
    int motorNumber = inputStream.parseInt();  // Parse the motor number
    int steps = inputStream.parseInt();  // Parse the steps

    // Clear the buffer
    while (inputStream.available() > 0) {
      inputStream.read();
    }

    // Acknowledge the received command
    inputStream.print("Moving motor ");
    inputStream.print(motorNumber);
    inputStream.print(" to ");
    inputStream.println(steps);

    // Process the parsed data
    processSerialData(motorNumber, steps);
    inputStream.println("Done!");
  }
}


void processSerialData(int motorNumber, int steps) {
  switch(motorNumber) {
    case 1:
      moveMotor(motor1, steps);
      break;
    case 2:
      moveMotor(motor2, steps);
      break;
    case 3:
      moveMotor(motor3, steps);
      break;
    case 4:
      moveMotor(motor4, steps);
      break;
    default:
      Serial.println("Invalid motor number.");
      break;
  }
}

void moveMotor(StepperMotor &motor, int steps) {
  motor.rotate(steps, 1, 3000);

  // Acknowledge the completion of the movement
    
}


