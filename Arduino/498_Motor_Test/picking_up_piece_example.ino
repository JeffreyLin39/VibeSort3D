const int IN1 = 10;
const int IN2 = 11;
const int PUMP = 9;

void setup() {
  // Set motor control pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PUMP, OUTPUT);
}

void loop() {
  delay(5000);
  // Reverse rotation GO DOWN
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  delay(1667);  // run for 1.667 seconds

  // Brake
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  delay(2000);

  // Turn pump on
  digitalWrite(PUMP, HIGH);

  delay(200);

  // Forward rotation GO UP
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  delay(2100);

  // Brake
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  delay(2000);

  // Turn Pump off
  digitalWrite(PUMP, LOW);

  delay(4000);

}
