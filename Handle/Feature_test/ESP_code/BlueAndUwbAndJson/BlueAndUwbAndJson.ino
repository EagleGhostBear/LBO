#include "TwoWayRangingResponder.h"
#include "blooth_lib.h"


void TaskUWB(void *param) {
  for(;;) {
    double ret = Uwb_loop();
    //if(ret != 0.1)
      //Serial.println(ret);

    vTaskDelay(1);
  }
}



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Start");
  // put your setup code here, to run once:

  blooth_lib_setup();

  delay(10);

  Uwb_setup();
  xTaskCreate(TaskUWB, "TaskUWB", 1024, NULL, 1, NULL);
}

void loop() {
  // put your main code here, to run repeatedly:
  vTaskDelay(10000);
}
