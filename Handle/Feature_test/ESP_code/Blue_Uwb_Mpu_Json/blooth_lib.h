#ifndef BLOOTH_LIB_H
#define BLOOTH_LIB_H

#include "BluetoothSerial.h"
#include "esp_bt_device.h"

void printDeviceAddress();
void Task_Print_Rx_Queue(void *pvParameters);
void Task_Send_Tx_Data(void *params);
void rxInterrupt(esp_spp_cb_event_t event, esp_spp_cb_param_t *param);
void blooth_lib_setup();


extern int rx_servo;
extern int rx_beep;

#endif