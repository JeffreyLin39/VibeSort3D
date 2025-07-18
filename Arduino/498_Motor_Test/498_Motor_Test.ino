
//X: left motor
const int stepX = 2;

const int dirX = 5;

//Y: Daniel's motor
const int stepY = 3;

const int dirY = 6;


//Z: right motor
const int stepZ = 4;

const int dirZ = 7;

//pins for the pump and linear actuator
const int IN1 = 10;
const int IN2 = 11;
const int PUMP = 9;

//enable pin
const int enPin = 8;

//proof by experimentation lol
#define PIXELS_TO_CM 0.013
#define CM_TO_STEPS 50

#define X_OFFSET 6

void setup() {
  // Pump and actuator pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PUMP, OUTPUT);

  Serial.begin(9600);

  pinMode(stepX, OUTPUT);

  pinMode(dirX, OUTPUT);

  pinMode(stepZ, OUTPUT);

  pinMode(dirZ, OUTPUT);



  pinMode(enPin, OUTPUT);

  digitalWrite(enPin, LOW);



  digitalWrite(dirX, HIGH);

  digitalWrite(dirZ, HIGH);
}

/*
Define (0,0) as this position:
<-------------- Positive Y
M─────────────(0,0)   |
│               │     |
│               │     | Positive X
│               │     |
M───────────────┘     ▼
Where M = motor

// -----------------------------
// | Direction | moveCoreXY   |
// -----------------------------
// |   +Y      | (true, false)  |
// |   -Y      | (false, true)  |
// |   +X      | (false, false) |
// |   -X      | (true, true)   |
// -----------------------------

*/
void loop() {

  //by default always run the conveyor
  // runConveyor();
  if (Serial.available() > 0) {
    //Raspberry pi sends 3 things: centerX and centerY of lego piece in pixels, and centerX of bin
    String input = Serial.readStringUntil('\n');

    int first = input.indexOf(',');
    int second = input.indexOf(',', first + 1);

    if (first > 0 && second > first) {
      float x = input.substring(0, first).toFloat();
      float y = input.substring(first + 1, second).toFloat();
      float bin_x = input.substring(second + 1).toFloat();

      //x*PIXELS_TO_CM*CM_TO_STEPS
      int x_steps = x * PIXELS_TO_CM * CM_TO_STEPS;
      int y_steps = y * PIXELS_TO_CM * CM_TO_STEPS;

      int bin_x_steps = max(0, bin_x * CM_TO_STEPS);
      //positive Y
      moveCoreXY(true, false, y_steps);   // +Y
      moveCoreXY(false, false, x_steps);    // +X

      // // TODO: gantry & pump logic

      // Go Down
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      delay(1667);  // run for 1.667 seconds

      // Brake
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      delay(1000);

      // Turn pump on
      digitalWrite(PUMP, HIGH);

      delay(200);

      // Go Up
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      delay(2100);
      
      // Brake
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, LOW);
      delay(1000);

      //Go back to 0 Y
      moveCoreXY(false, true, y_steps);   // -Y

      if (bin_x_steps >= x_steps){
        moveCoreXY(false, false, bin_x_steps - x_steps);   // +X
      }
      else
      {
        moveCoreXY(true, true, x_steps - bin_x_steps); // -X
      }

      // Turn Pump off
      digitalWrite(PUMP, LOW);
      delay(6000);
      
      // //Shake for a bit
      // if (bin_x_steps <= 10)
      // {
      //   //right then left
      //   for (int i = 0; i < 5; i++)
      //   {
      //     moveCoreXY(false, false, 25);
      //     moveCoreXY(true, true, 25);
      //   }

      // }
      // else
      // {
      //   //left then right
      //   for (int i = 0; i < 5; i++)
      //   {
      //     moveCoreXY(true, true, 25);
      //     moveCoreXY(false, false, 25);
      //   }
      // }
      moveCoreXY(true, true, bin_x_steps); // back to X = 0

      //Send message back to the Pi
      Serial.println("a");
    }
    // if (command == "W") moveCoreXY(true, false);   // +Y
    // else if (command == "S") moveCoreXY(false, true); // -Y
    // else if (command == "D") moveCoreXY(true, true);  // +X
    // else if (command == "A") moveCoreXY(false, false); // -X
  }

}

//runs the conveyor belt motor
void runConveyor()
{
  digitalWrite(dirY, HIGH);
  digitalWrite(stepY, HIGH);
  delayMicroseconds(500);
  digitalWrite(stepY, LOW);
  delayMicroseconds(500);
}

void moveCoreXY(bool dirAVal, bool dirBVal, int steps) {
  //HIGH -> rotate forward
  //LOW -> rotate backwards
  digitalWrite(dirX, dirAVal);
  digitalWrite(dirZ, dirBVal);

  for (int i = 0; i < steps; i++) {
    digitalWrite(stepX, HIGH);
    digitalWrite(stepZ, HIGH);
    delayMicroseconds(500);
    digitalWrite(stepX, LOW);
    digitalWrite(stepZ, LOW);
    delayMicroseconds(500);
  }
}