/*
 Author: KYR
 Date(Latest): 2024-05-11
 This Library is for Bluetooth
 Make 2 tasks. TX, RX
 RX has 2 function; handler, task
 Tx has 1 function; task
*/


#ifndef BLOOTH_LIB_H
#define BLOOTH_LIB_H


// Internal Library For Bluetooth
#include "BluetoothSerial.h"
#include "esp_bt_device.h"

// Prototype
void printDeviceAddress();
void Task_Print_Rx_Queue(void *pvParameters);
void Task_Send_Tx_Data(void *params);
void rxInterrupt(esp_spp_cb_event_t event, esp_spp_cb_param_t *param);
void blooth_lib_setup();

// KYR: Define Structure for IMU data
struct IMU_Return_t {
  float gyro_x;
  float gyro_y;
  float gyro_z;
  float gyro_w;

  float acc_x;
  float acc_y;
  float acc_z; 
};

// For servo's angle & beep mode
extern int rx_servo;
extern int rx_beep;


// IMU
extern IMU_Return_t imu_data;

#endif