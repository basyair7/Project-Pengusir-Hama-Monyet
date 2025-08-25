#define LED LED_BUILTIN
#define SENSOR 16

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED, OUTPUT);
  pinMode(SENSOR, INPUT_PULLUP);
}

void loop() {
  // put your main code here, to run repeatedly:
  bool value = digitalRead(SENSOR);
  Serial.println(value);
  if (value == LOW) {
    digitalWrite(LED, HIGH);
  }
  else {
    digitalWrite(LED, LOW);
  }
}
