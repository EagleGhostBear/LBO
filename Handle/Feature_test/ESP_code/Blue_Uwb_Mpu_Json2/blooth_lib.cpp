#include "blooth_lib.h"
#include "Arduino.h"
#include <ArduinoJson.h>
#include "MPU9250.h"



#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif


#define QUEUE_MAX_SIZE 1024

// BT instance created
BluetoothSerial SerialBT;

// Semaphore value
SemaphoreHandle_t rx_semaphore_b;


// Receive Queue
char Rx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Rx_rear = 0U;
volatile uint16_t Rx_front = 0U;

// Transmitt Queue It will be "not" used
char Tx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Tx_rear = 0U;
volatile uint16_t Tx_front = 0U;

// Tx value
const int _name = 1;
String _time = "";
double uwb = 0.0;
float gyro_x = 0.0, gyro_y = 0.0, gyro_z = 0.0, gyro_w = 0.0;
float acc_x = 0.0, acc_y = 0.0, acc_z = 0.0;
// float gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z;
int button = 0;




// Rx value
int rx_name = 0;
String rx_time = "";
int rx_servo = 0;
int rx_beep = 0;


// Button
extern int buttonState1;
extern int buttonState2;



// Function for now Time(Tick)
String tickToTime(TickType_t tickCount) {
    const uint32_t ticksPerSecond = 1000;

    uint32_t seconds = tickCount / ticksPerSecond;
    uint32_t minutes = seconds / 60;
    uint32_t hours = minutes / 60;
    seconds %= 60;
    minutes %= 60;

    String timeString = String(hours < 10 ? "0" + String(hours) : String(hours)) + ":" +
                        String(minutes < 10 ? "0" + String(minutes) : String(minutes)) + ":" +
                        String(seconds < 10 ? "0" + String(seconds) : String(seconds));

    return timeString;
}


// Function: String -> Json for Transmitt
JsonDocument makeJson() {
// Storage datas at Tx_doc
  JsonDocument Tx_doc;
  JsonDocument info;
  JsonDocument data;
  JsonDocument imu;
  JsonDocument gyro;
  JsonDocument acc;

  info["name"] = _name;
  info["time"] = _time;

  Tx_doc["info"] = info;

  data["uwb"] = uwb;
  
  gyro["x"] = gyro_x;
  gyro["y"] = gyro_y;
  gyro["z"] = gyro_z;
  gyro["w"] = gyro_w;

  acc["x"] = acc_x;
  acc["y"] = acc_y;
  acc["z"] = acc_z;
  
  imu["gyro"] = gyro;
  imu["acc"] = acc;
  
  data["imu"] = imu;


  data["button"] = button;

  Tx_doc["data"] = data;

  return Tx_doc;
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

// Function: Json -> String & Print data at Serial Monitor
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


        rx_name = Rx_doc["info"]["name"];
        String str_Temp = Rx_doc["info"]["time"];
        rx_time = str_Temp;

        rx_servo = Rx_doc["data"]["servo"];
        rx_beep = Rx_doc["data"]["beep"];

        Serial.println("New");

        Serial.print("name: ");
        Serial.println(rx_name);

        Serial.print("time: ");
        Serial.println(rx_time);

        Serial.print("servo: ");
        Serial.println(rx_servo);

        Serial.print("beep: ");
        Serial.println(rx_beep);

        Serial.println("Original String: " + str);

        Rx_rear = 0U;
        Rx_front = 0U;
        str.clear();
      }
    }
    vTaskDelay(300);
  }
  // vTaskDelete(NULL);
}

// dummy data
int goorooroo = 0;

// Send Data
void Task_Send_Tx_Data(void *params) {
  for(;;) {

    TickType_t tickCount = xTaskGetTickCount();
    _time = tickToTime(tickCount);



    goorooroo++;

    uwb = 0.1 + goorooroo;
    
    gyro_x = imu_data.gyro_x;
    gyro_y = imu_data.gyro_y;
    gyro_z = imu_data.gyro_z;
    gyro_w = imu_data.gyro_w;
    
    acc_x = imu_data.acc_x;
    acc_y = imu_data.acc_y;
    acc_z = imu_data.acc_z;
    



    button = (buttonState1 * 2 + buttonState2);
  

    JsonDocument Tx_doc = makeJson();

    String sendString;
    serializeJson(Tx_doc, sendString);

    

    for(int i = 0; i < sendString.length(); i++) {
      SerialBT.write(sendString[i]);
    }
    SerialBT.write('@');

    Serial.println(sendString);

    

    vTaskDelay(100);
  }
}






// void IRAM_ATTR rxInterrupt()
// esp_spp_cb_event_t event, esp_spp_cb_param_t *param

// Function for collect Receive data with Interrupt
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

  xTaskCreate(Task_Print_Rx_Queue, "Task_Print_Message_Queue", 4096, NULL, 2, NULL);
  xTaskCreate(Task_Send_Tx_Data, "Task_Send_Tx_Data", 4096, NULL, 2, NULL);

  Serial.println("End of blue tooth Init");
}
