// #include "BluetoothSerial.h"
// #include "esp_bt_device.h"
#include "blooth_lib.h"



void setup() {
  Serial.begin(115200);
  Serial.println("SSSSTTTTTAAAAARRRRTTTT");
  blooth_lib_setup();
}

void loop() {
  vTaskDelay(1000);
}