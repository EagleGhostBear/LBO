#include "TwoWayRangingResponder.h"


void Task1(void *param) {
  for(;;) {
    double ret = Uwb_loop();

    Serial.println(ret);

    vTaskDelay(1000);
  }
}


void setup() {
  Serial.begin(115200);
  Serial.println("Start");
  // put your setup code here, to run once:
  Uwb_setup();
  xTaskCreate(Task1, "Task1", 1024, NULL, 1, NULL);
}



void loop() {
  // put your main code here, to run repeatedly:
  vTaskDelay(10000);
}
