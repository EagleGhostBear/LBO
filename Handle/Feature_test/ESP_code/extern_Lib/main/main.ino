#include "AA.h"

extern int A;
extern int B;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("START");
}





void loop() {
  // put your main code here, to run repeatedly:

  

  Serial.println(A+B);

  vTaskCreate(Add, "Add", 1024, NULL, 1, NULL);

  vTaskDelay(1000);
}
