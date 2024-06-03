#include "BluetoothSerial.h"
#include "esp_bt_device.h"


#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define QUEUE_MAX_SIZE 512
const TickType_t loopDelay = 1000000;

BluetoothSerial SerialBT;

SemaphoreHandle_t Send_Semaphore = NULL;

char Rx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Rx_rear = 0U;
volatile uint16_t Rx_front = 0U;


char Tx_Que[QUEUE_MAX_SIZE];
volatile uint16_t Tx_rear = 0U;
volatile uint16_t Tx_front = 0U;




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
  for(;;){
    if (Rx_front != Rx_rear) {
      // for(int i = Rx_front; i != Rx_rear; i++) {
      //   Serial.print(Rx_Que[i]);
      // }
      while(Rx_front != Rx_rear) {
        Serial.print(Rx_Que[Rx_front++]);
      }
      Serial.println();
      Rx_rear = 0U;
      Rx_front = 0U;
    }
    vTaskDelay(100);
  }
  // vTaskDelete(NULL);
}


void Task_Send_Tx_Data(void *params) {
  for(;;) {
    while(Serial.available()) {
      char data = Serial.read();
      
      if(data == '@') {
        while(Tx_rear != Tx_front) {
          SerialBT.write(Tx_Que[Tx_front]);
          Tx_front = (Tx_front + 1) % QUEUE_MAX_SIZE;
        }
        
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
      Rx_Que[Rx_rear++] = SerialBT.read(); // 데이터를 읽음
    }
  }
}



void setup() {
  Serial.begin(115200);
  Serial.println("\n---Start---");
  SerialBT.begin("ESP32test"); //Bluetooth device name
  
  Serial.println("The device started, now you can pair it with bluetooth!");
  Serial.println("Device Name: ESP32test");
  Serial.print("BT MAC: ");
  printDeviceAddress();
  Serial.println();

 // semaphore
 // (max_count, init_count)
 Send_Semaphore = xSemaphoreCreateCounting(10, 0);
 
  // attachInterrupt(digitalPinToInterrupt(1), rxInterrupt, RISING);
  SerialBT.register_callback(rxInterrupt);

  xTaskCreate(Task_Print_Rx_Queue, "Task_Print_Message_Queue", 1024, NULL, 4, NULL);
  xTaskCreate(Task_Send_Tx_Data, "Task_Send_Tx_Data", 1024, NULL, 2, NULL);

}

void loop() {
  vTaskDelay(1000);
}