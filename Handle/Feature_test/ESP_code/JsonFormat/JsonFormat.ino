#include <ArduinoJson.h>

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("START");

  JsonDocument doc;
  String input =
      "{\"sensor\":\"gps\",\"time\":1351824120,\"data\":[48.756080,2.302038]}";
  deserializeJson(doc, input);

  long time = doc["time"];
  String sensor = doc["sensor"];
  double data1 = doc["data"][0];
  double data2 = doc["data"][1];

  Serial.println("1. Read data from Json");
  Serial.println(time);
  Serial.println(sensor);
  Serial.println(data1);
  Serial.println(data2);




  Serial.println("");
  Serial.println("");
  Serial.println("");





  Serial.println("2. Change Json data and make new item(=name) to Json");

  time = 22355213;
  sensor = "WIFI";
  data1 = 24.24242424;
  data2 = 9.00234;

  doc["time"] = time;
  doc["sensor"] = sensor;
  doc["data"][0] = data1;
  doc["data"][1] = data2;

  doc["name"] = "kyr";

  long time_temp = doc["time"];
  String sensor_temp = doc["sensor"];
  double data1_temp = doc["data"][0];
  double data2_temp = doc["data"][1];
  String name = doc["name"];
  
  Serial.println(time_temp);
  Serial.println(sensor_temp);
  Serial.println(data1_temp);
  Serial.println(data2_temp);
  Serial.println(name);




  Serial.println("");
  Serial.println("");
  Serial.println("");



  Serial.println("3. Make String from Json");
  String result;
  JsonDocument doc2;
  doc2["name"] = "kyr";
  doc2["age"] = 25;
  doc2["hobby"] = "sleeping";

  serializeJson(doc2, result);
  result += '@';
  Serial.println(result);




  Serial.println("");
  Serial.println("");
  Serial.println("");


  Serial.println("4. Json In Json and convert to String");
  JsonDocument doc3;
  JsonDocument temp_doc;

  doc3["Aaa"] = 25;
  doc3["aBa"] = "AbA";
  temp_doc["start"] = 56;
  temp_doc["end"] = 99;
  doc3["kokoro"] = temp_doc;

  String retString;
  serializeJson(doc3, retString);
  Serial.println(retString);



  Serial.println("");
  Serial.println("");
  Serial.println("");


  Serial.println("5. Json Array");
  JsonDocument doc4;
  doc4["kkk"] = "kkk is IS";

  JsonDocument doc_temp;
  deserializeJson(doc_temp, "[2, 6, 9]");
  JsonArray array = doc_temp.as<JsonArray>();

  doc4["arr"] = array;

  String arrString;
  serializeJson(doc4, arrString);
  Serial.println(arrString);
  
}

void loop() {
  // put your main code here, to run repeatedly:

}