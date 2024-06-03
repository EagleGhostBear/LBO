#include <ArduinoJson.h>
#define QUEUE_MAX_SIZE 512
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("____START___");

  

}

int Tx_rear = 0;
int Tx_front = 0;
char Tx_Que[QUEUE_MAX_SIZE];


String test_str;
int _name;
String _time;
double uwb;
float gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z;
int button;

void loop() {
  while(Serial.available()) {
    char data = Serial.read();
    
    if(data == '@') {
      while(Tx_rear != Tx_front) {
        // SerialBT.write(Tx_Que[Tx_front]);
        test_str += Tx_Que[Tx_front];
        Tx_front = (Tx_front + 1) % QUEUE_MAX_SIZE;
      }

      // They Will be global value at developed code
      int _name;
      String _time;
      double uwb;
      float gyro_x =, gyro_y, gyro_z, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z;
      int button;

      char time_buffer[30] = {0, };
      // It just user input
      // When We demonstrate this project, We doesn't use It
      //                        1  str UWB x  y  z  x  y  z  x  y  z  2
      sscanf(test_str.c_str(), "%d/%s/%lf/%f/%f/%f/%f/%f/%f/%f/%f/%f/%d", \
      &_name, time_buffer, &uwb, &gyro_x, &gyro_y, &gyro_z, &acc_x, &acc_y, &acc_z, &mag_x, &mag_y, &mag_z, &button);

      _time = time_buffer;

      
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
      

      test_str.clear();


      // // Storage datas at Tx_doc
      // JsonDocument Tx_doc;
      // JsonDocument info;
      // JsonDocument data;
      // JsonDocument imu;
      // JsonDocument gyro;
      // JsonDocument acc;
      // JsonDocument mag;

      // info["name"] = _name;
      // info["time"] = _time;

      // Tx_doc["info"] = info;




      // data["uwb"] = uwb;
      
      // gyro["x"] = gyro_x;
      // gyro["y"] = gyro_y;
      // gyro["z"] = gyro_z;

      // acc["x"] = acc_x;
      // acc["y"] = acc_y;
      // acc["z"] = acc_z;

      // mag["x"] = mag_x;
      // mag["y"] = mag_y;
      // mag["z"] = mag_z;

      // imu["gyro"] = gyro;
      // imu["acc"] = acc;
      // imu["mag"] = mag;

      // data["imu"] = imu;

      // data["button"] = button;

      // Tx_doc["data"] = data;


      // String sendString;
      // serializeJson(Tx_doc, sendString);

      // Serial.println(sendString);

      // for(int i = 0; i < sendString.length(); i++) {
      //   SerialBT.write(sendString[i]);
      // }
      // SerialBT.write('@');



      break;
    }
    else {
      Tx_Que[Tx_rear] = data;
      Tx_rear = (Tx_rear + 1) % QUEUE_MAX_SIZE;
    }
  }

  delay(1000);
}
