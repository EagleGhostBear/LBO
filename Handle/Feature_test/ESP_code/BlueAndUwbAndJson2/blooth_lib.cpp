#include "blooth_lib.h"
#include "Arduino.h"
#include <ArduinoJson.h>


#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif


#define QUEUE_MAX_SIZE 512


BluetoothSerial SerialBT;
SemaphoreHandle_t rx_semaphore_b;

char Rx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Rx_rear = 0U;
volatile uint16_t Rx_front = 0U;


char Tx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Tx_rear = 0U;
volatile uint16_t Tx_front = 0U;

String tickToTime(TickType_t tickCount) {
    const uint32_t ticksPerSecond = 1000;

    uint32_t seconds = tickCount / ticksPerSecond;
    uint32_t minutes = seconds / 60;
    uint32_t hours = minutes / 60;
    seconds %= 60;
    minutes %= 60;

    String timeString = String(hours) + ":" + String(minutes) + ":" + String(seconds);

    return timeString;
}

// function for address, Mac address must be equal value at addr of RPI code
void printDeviceAddress() {
  const uint8_t* point = esp_bt_dev_get_address();
  
  for (int i = 0; i < 6; i++) {
    char str[3];
    sprintf(str, "%02X", (int)point[i]);
    Serial.print(str);
    
    if (i < 5){
      Serial.print(":");
    }
  }
}


void Task_Print_Rx_Queue(void *pvParameters) {
  String str;
  for(;;){
    if (Rx_front != Rx_rear) {
      // for(int i = Rx_front; i != Rx_rear; i++) {
      //   Serial.print(Rx_Que[i]);
      // }

      if(xSemaphoreTake(rx_semaphore_b, portMAX_DELAY) == pdTRUE) {
        // rx_data is so small, so I(KYR) didin't use it circular
        while(Rx_front != Rx_rear) {
          str += Rx_Que[Rx_front++];
        }


        Serial.println(str);
        str.remove(str.length() - 1);
        Serial.println(str);

        JsonDocument Rx_doc;
        deserializeJson(Rx_doc, str);


        int name = Rx_doc["info"]["name"];
        String time = Rx_doc["info"]["time"];
        
        int servo = Rx_doc["data"]["servo"];
        int beep = Rx_doc["data"]["beep"];

        Serial.println("New");

        Serial.print("name: ");
        Serial.println(name);

        Serial.print("time: ");
        Serial.println(time);

        Serial.print("servo: ");
        Serial.println(servo);

        Serial.print("beep: ");
        Serial.println(beep);

        Serial.println("Original String: " + str);

        Rx_rear = 0U;
        Rx_front = 0U;
        str.clear();
      }
    }
    vTaskDelay(100);
  }
  // vTaskDelete(NULL);
}


int goorooroo = 0;
String test_str;
// UWB/gyrox/gyroy/.../Button@
void Task_Send_Tx_Data(void *params) {
  for(;;) {
    while(Serial.available()) {
      char data = Serial.read();
      
      if(data == '@') {
        while(Tx_rear != Tx_front) {
          // SerialBT.write(Tx_Que[Tx_front]);
          test_str += Tx_Que[Tx_front];
          Tx_front = (Tx_front + 1) % QUEUE_MAX_SIZE;
        }


        TickType_t tickCount = xTaskGetTickCount();
        String _time = tickToTime(tickCount);


        int _name;
        double uwb;
        float gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z;
        int button;

        goorooroo++;

        _name = goorooroo;

        uwb = 0.1 + goorooroo;

        gyro_x = 1.1 + goorooroo;
        gyro_y = gyro_x +1.5;
        gyro_z = gyro_x * 2;

        acc_x = 0.2 + goorooroo;
        acc_y = acc_x + 1.5;
        acc_z = acc_x * 2;

        mag_x = 0.7 + goorooroo;
        mag_y = mag_x + 1.5;
        mag_z = mag_x * 2;

        button = goorooroo * 2;        

        test_str.clear();
        Serial.println(_name);
        Serial.println(_time);
        Serial.println(uwb);
        Serial.println(gyro_x);
        Serial.println(gyro_y);
        Serial.println(gyro_z);
        Serial.println(acc_x);
        Serial.println(acc_y);
        Serial.println(acc_z);
        Serial.println(mag_x);
        Serial.println(mag_y);
        Serial.println(mag_z);
        Serial.println(button);
        




        // Storage datas at Tx_doc
        JsonDocument Tx_doc;
        JsonDocument info;
        JsonDocument data;
        JsonDocument imu;
        JsonDocument gyro;
        JsonDocument acc;
        JsonDocument mag;

        info["name"] = _name;
        info["time"] = _time;

        Tx_doc["info"] = info;




        data["uwb"] = uwb;
        
        gyro["x"] = gyro_x;
        gyro["y"] = gyro_y;
        gyro["z"] = gyro_z;

        acc["x"] = acc_x;
        acc["y"] = acc_y;
        acc["z"] = acc_z;

        mag["x"] = mag_x;
        mag["y"] = mag_y;
        mag["z"] = mag_z;

        imu["gyro"] = gyro;
        imu["acc"] = acc;
        imu["mag"] = mag;

        data["imu"] = imu;

        data["button"] = button;

        Tx_doc["data"] = data;


        String sendString;
        serializeJson(Tx_doc, sendString);

        Serial.println(sendString);

        for(int i = 0; i < sendString.length(); i++) {
          SerialBT.write(sendString[i]);
        }
        SerialBT.write('@');



        break;
      }
      else {
        Tx_Que[Tx_rear] = data;
        Tx_rear = (Tx_rear + 1) % QUEUE_MAX_SIZE;
      }
    }

    vTaskDelay(100);
  }
}





// void IRAM_ATTR rxInterrupt()
// esp_spp_cb_event_t event, esp_spp_cb_param_t *param
void rxInterrupt(esp_spp_cb_event_t event, esp_spp_cb_param_t *param) {
  if (event == ESP_SPP_DATA_IND_EVT) { 
    while(SerialBT.available()) {
      // Rx_Que[Rx_rear++] = SerialBT.read(); // 데이터를 읽음
      char temp = SerialBT.read();
      if(temp == '@') {
        xSemaphoreGive(rx_semaphore_b);
      }
      Rx_Que[Rx_rear++] = temp;
    }
  }
}

void blooth_lib_setup() {
  Serial.begin(115200);
  Serial.println("\n---Blue Tooth Init Start---");
  SerialBT.begin("ESP32test"); //Bluetooth device name
  
  Serial.println("The device started, now you can pair it with bluetooth!");
  Serial.println("Device Name: ESP32test");
  Serial.print("BT MAC: ");
  printDeviceAddress();
  Serial.println();


  rx_semaphore_b = xSemaphoreCreateBinary();

 
  // attachInterrupt(digitalPinToInterrupt(1), rxInterrupt, RISING);
  SerialBT.register_callback(rxInterrupt);

  xTaskCreate(Task_Print_Rx_Queue, "Task_Print_Message_Queue", 2048, NULL, 4, NULL);
  xTaskCreate(Task_Send_Tx_Data, "Task_Send_Tx_Data", 4096, NULL, 2, NULL);

  Serial.println("End of blue tooth Init");
}
