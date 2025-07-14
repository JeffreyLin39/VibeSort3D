//step_coordinate corresponds to the coordinate printed on the CNC shield.
//we're using X and Z cuz i'm too lazy to move the driver on the shield
const int stepX = 2;

const int dirX  = 5;


const int stepY = 3;

const int dirY  = 6;


const int stepZ = 4;

const int dirZ  = 7;



const int enPin = 8;


void setup() {


  Serial.begin(9600);

  pinMode(stepX,OUTPUT);

  pinMode(dirX,OUTPUT);

  pinMode(stepZ,OUTPUT);

  pinMode(dirZ,OUTPUT);



  pinMode(enPin,OUTPUT);

  digitalWrite(enPin,LOW);



  digitalWrite(dirX,HIGH);

  digitalWrite(dirZ,HIGH);

}

void loop() {
  if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      if (command == "W") moveCoreXY(true, false);   // +Y
      else if (command == "S") moveCoreXY(false, true); // -Y
      else if (command == "D") moveCoreXY(true, true);  // +X
      else if (command == "A") moveCoreXY(false, false); // -X
  }

}

void moveCoreXY(bool dirAVal, bool dirBVal) {
  //HIGH -> rotate forward
  //LOW -> rotate backwards
  digitalWrite(dirX, dirAVal);
  digitalWrite(dirZ, dirBVal);

  for (int i = 0; i < 695; i++) {
    digitalWrite(stepX, HIGH);
    digitalWrite(stepZ, HIGH);
    delayMicroseconds(500);
    digitalWrite(stepX, LOW);
    digitalWrite(stepZ, LOW);
    delayMicroseconds(500);
  }
}