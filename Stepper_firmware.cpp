# arduino code for the project
#include <AccelStepper.h>
/*  Program to control two or more stepper motors, with posibility of using acceleration 
    or deceleration ramps
    From serial port send:
     H: To check the status of the serial connection
     O: To open shutter
     N: To close shutter
     D: To query position of current motor
     C: To change the speed and then send the value 
     P: To make a given stepper the order to move a given number of steps
     R: To make a given stepper the order to move at a certain speed
     S: To stop a stepper that is already running
     V: To query the speed of a motor that is already running

  Author1  Carlos Cuartas, ccuarta1@eafit.edu.co
  Author2  Santiago Echeverri, sechev14@eafit.edu.co
  Author3  Camilo Cano, ccanoba@eafit.edu.co
  Author4  Santiago Garcia Botero
*/

#define X_AXIS_STEP_PIN 2
#define Y_AXIS_STEP_PIN 3
#define Z_AXIS_STEP_PIN 4
#define A_AXIS_STEP_PIN 12     // requires an optional jumper

#define X_AXIS_DIR_PIN 5
#define Y_AXIS_DIR_PIN 6
#define Z_AXIS_DIR_PIN 7
#define A_AXIS_DIR_PIN 13      // requires an optional jumper

#define STEPPER_ENABLE_PIN 8  // active-low (i.e. LOW turns on the drivers)

// Definition of output pins as stepper wires.
AccelStepper xaxis(AccelStepper::DRIVER, X_AXIS_STEP_PIN, X_AXIS_DIR_PIN);
AccelStepper yaxis(AccelStepper::DRIVER, Y_AXIS_STEP_PIN, Y_AXIS_DIR_PIN);
AccelStepper zaxis(AccelStepper::DRIVER, Z_AXIS_STEP_PIN, Z_AXIS_DIR_PIN);
AccelStepper aaxis(AccelStepper::DRIVER, A_AXIS_STEP_PIN, A_AXIS_DIR_PIN);
AccelStepper motores[] = {zaxis, yaxis, xaxis, aaxis};
int speedIni, paso,n,dummy,engine,rev,cp;    //Definition of variables.
char parar, vel, cambiar, command;
float valor,cs;
const int shutter = A5;
void setup()
{  
  // initialize the LED pin as an output:
   pinMode(shutter, OUTPUT);   
   command='\*'; 
   speedIni = 1000;  // Stepper speed in steps per second. 
// Define maximun speed and acceleration;
// we recomend using values of 50 (speed) and 20 (acceleration).
  
  pinMode(STEPPER_ENABLE_PIN, OUTPUT);
   motores[1].setMaxSpeed(200.0);   
   motores[1].setAcceleration(50.0);
   motores[0].setMaxSpeed(200.0);
   motores[0].setAcceleration(200.0);
   motores[2].setMaxSpeed(200.0);
   motores[2].setAcceleration(100.0);
   motores[3].setMaxSpeed(500.0);
   motores[3].setAcceleration(20.0);
   motores[0].setSpeed(100.0);
   motores[1].setSpeed(100.0);
   motores[2].setSpeed(100.0);
   motores[3].setSpeed(100.0);
   Serial.begin(9600);	// Start serial port with 9600 baudios of speed.
   digitalWrite(STEPPER_ENABLE_PIN, LOW); // initialize drivers in disabled state

}


float velocidad()   //Funtion to obtain stepper speed.
{
  n=steppers(); // Identifies the engine wich you want to get information.
  valor=motores[n].speed();   // Speed value obtained.
  return valor;
}
int readValue()   // Receives a numerical value at the input of the serial port.
{
  // Receive up to 7 bytes,
  // http://www.baldengineer.com/blog/2012/07/30/arduino-multi-digit-integers/
   char buffer[] = {' ',' ',' ',' ',' ',' ',' '}; 
   while (!Serial.available()); // Wait for characters
   Serial.readBytesUntil('n', buffer, 7);
   rev = atoi(buffer); //transform string into an int.
   Serial.println(rev);
   return rev; 
}
int steppers()  // Determines the engine to use.
{
  dummy=0;  // Dummy variable, It's use to get into the while.muda
  while(dummy==0)
  {
   engine=readValue(); 
   if(engine==1)
   {
     n=0; //stepper
     dummy=1;
     return n;
   }
   if(engine==2)
   {
     n=1;
     dummy=1;
     return n;
   }
   if(engine==3)
   {
     n=2;
     dummy=1;
     return n;
   }
   
   if(engine==4)
   {
     n=3;
     dummy=1;
     return n;
   }
  }
}
void loop()  
{
  if (Serial.available()) {
  command=Serial.read();  // Wait command.
  delay(40);
  }
   if (command == 'H') // Command to check if we have connexion.
    {
      Serial.print('Y');
      command='\*'; 
    }
   if (command == 'Z')
   {
     n=steppers();
     motores[n].setCurrentPosition(0);
     command='\*';
   }
  if (command == 'O') // Command to open shutter.
    {
      digitalWrite(shutter, HIGH); 
     command='\*'; 
    }
  if (command == 'N') // Command to close shutter.
    {
      digitalWrite(shutter, LOW);  
      command='\*'; 
    }         
  if (command == 'D')
  {
    n=steppers();
    cp=motores[n].currentPosition();
    Serial.print(cp);
    command='\*'; 
  }
// If the command is C (Change), is because you want to change the stepper speed.
  if(command =='C')  
  {
    speedIni = readValue();
//Sets the speed, by default it starts with a speed of 50 steps / second.
      motores[0].setSpeed(speedIni);  
      motores[1].setSpeed(speedIni);
      motores[2].setSpeed(speedIni); 
      motores[3].setSpeed(speedIni);
//Sets the speed, by default it starts with a speed of 50 steps / second.
      motores[0].setMaxSpeed(speedIni);  
      motores[1].setMaxSpeed(speedIni);
      motores[2].setMaxSpeed(speedIni); 
      motores[3].setMaxSpeed(speedIni);
      command='\*'; 
  }
// If the command is P (Pasos), then enter the engine you wnat to move and number of steps.
if(command =='P')   
{
  n=steppers();
  paso=readValue();

  // Enable the motor outputs for the motor you want to move
  motores[n].enableOutputs();

  motores[n].moveTo(paso);  //Determines the step at which you want to move the engine.
  motores[n].runToPosition();  // Move the motor to the desired step.



  if(motores[n].currentPosition() == paso)
  {
    Serial.print('F');
  }
  command='\*'; 
}

  // If the command is R (Run), the selected motor will move at constant speed.
  if(command =='R')  
  {
    n=steppers();
    while(command =='R')
    {
//Activates the motor.
      motores[n].runSpeed();  
//Receives the command to be used while the engine is moving.    
      parar = Serial.read();  
      vel = parar; 
      cambiar = parar; 
// If the command is V (Velocidad), returns the speed at which the selected motor moves.       
      if(vel=='V') 
      {
        valor = velocidad();
        Serial.print(valor);
        vel='c';
      }
//If the command is S (stop), the motor stops.     
      if(parar=='S')  
      {
        Serial.print("Pausa");
        motores[n].stop();  
        parar='a';  
        command='\*'; 
        cambiar ='ab';
      }
//If the command is C (Change), is because you want to change the stepper speed.
      if(cambiar=='C')  
      {
        speedIni = readValue();
        parar='a';
        command='\*'; 
        cambiar='ab';
      }
    }
  }
}
