#include <Stepper.h>

#define STEPS 2048 
Stepper stepper(STEPS, 8, 10, 9, 11);

void setup() {
  Serial.begin(9600);
  stepper.setSpeed(10);  
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == 'L') {
      stepper.step(50);
    } 
    else if (command == 'R') {
      stepper.step(-50);
    }
  }
}