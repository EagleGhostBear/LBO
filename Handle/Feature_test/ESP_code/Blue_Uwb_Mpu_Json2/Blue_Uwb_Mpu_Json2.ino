// #include "TwoWayRangingResponder.h"
#include "blooth_lib.h"
#include "driver/gpio.h"
#include "MPU9250.h"

#include <SPI.h>
#include <DW1000Ng.hpp>
#include <DW1000NgUtils.hpp>
#include <DW1000NgTime.hpp>
#include <DW1000NgConstants.hpp>



#define BUZZER_PIN 25


// ---------- button (start) ---------------d
const int buttonPin1 = 32;
const int buttonPin2 = 33;

volatile int buttonState1 = false;
volatile int buttonState2 = false;


// ---------- button (end) -----------------





// --------   UWB value (start)    --------      
// connection pins
const uint8_t PIN_SCK = 18;
const uint8_t PIN_MOSI = 23;
const uint8_t PIN_MISO = 19;
const uint8_t PIN_SS = 2;
const uint8_t PIN_RST = 15;
const uint8_t PIN_IRQ = 17;

// messages used in the ranging protocol
// TODO replace by enum
#define POLL 0
#define POLL_ACK 1
#define RANGE 2
#define RANGE_REPORT 3
#define RANGE_FAILED 255
// message flow state
volatile byte expectedMsgId = POLL_ACK;
// message sent/received state
volatile boolean sentAck = false;
volatile boolean receivedAck = false;
// timestamps to remember
uint64_t timePollSent;
uint64_t timePollAckReceived;
uint64_t timeRangeSent;
// data buffer
#define LEN_DATA 16
byte data[LEN_DATA];
// watchdog and reset period
uint32_t lastActivity;
uint32_t resetPeriod = 250;
// reply times (same on both sides for symm. ranging)
uint16_t replyDelayTimeUS = 3000;
int cnt = 0;

device_configuration_t DEFAULT_CONFIG = {
  false,
  true,
  true,
  true,
  false,
  SFDMode::STANDARD_SFD,
  Channel::CHANNEL_5,
  DataRate::RATE_110KBPS,
  PulseFrequency::FREQ_16MHZ,
  PreambleLength::LEN_256,
  PreambleCode::CODE_4
};

interrupt_configuration_t DEFAULT_INTERRUPT_CONFIG = {
  true,
  true,
  true,
  false,
  true
};





// void noteActivity();
// void resetInactive();
// void handleSent();
// void handleReceived();
// void transmitPoll();
// void transmitRangeReport(float);

// void transmitRangeFailed();
// void receiver();

// --------   UWB value (End)    --------




// --------- MPU value (Start) ---------
// struct IMU_Return_t {
//   float gyro_x;
//   float gyro_y;
//   float gyro_z;
//   float gyro_w;

//   float acc_x;
//   float acc_y;
//   float acc_z; 
// };

IMU_Return_t imu_data;

MPU9250 mpu;
// IMU sequence 
// MPU_init() -> 

void getIMU(); // Task: Update IMU data (imu_data)
void update_quaternion(); // update quanternion
void Mpu_init(); // Init
// void Mpu_loop(); // For Debug, Not use
// void print_IMU(); // For Debug
void update_acc(); // update acc
// --------- MPU value (End) ---------






// -------- UWB function (start) ------------

void Uwb_setup() {
  // DEBUG monitoring
  Serial.begin(115200);

  pinMode(PIN_RST, OUTPUT);
  digitalWrite(PIN_RST, LOW);
  delay(100);
  digitalWrite(PIN_RST, HIGH);

  Serial.println(F("### DW1000Ng-arduino-ranging-tag ###"));
  // initialize the driver
  DW1000Ng::initialize(PIN_SS, PIN_IRQ, PIN_RST);
  Serial.println("DW1000Ng initialized ...");
  // general configuration
  DW1000Ng::applyConfiguration(DEFAULT_CONFIG);
  DW1000Ng::applyInterruptConfiguration(DEFAULT_INTERRUPT_CONFIG);

  DW1000Ng::setNetworkId(10);

  DW1000Ng::setAntennaDelay(16436);

  Serial.println(F("Committed configuration ..."));
  // DEBUG chip info and registers pretty printed
  char msg[128];
  DW1000Ng::getPrintableDeviceIdentifier(msg);
  Serial.print("Device ID: "); Serial.println(msg);
  DW1000Ng::getPrintableExtendedUniqueIdentifier(msg);
  Serial.print("Unique ID: "); Serial.println(msg);
  DW1000Ng::getPrintableNetworkIdAndShortAddress(msg);
  Serial.print("Network ID & Device Address: "); Serial.println(msg);
  DW1000Ng::getPrintableDeviceMode(msg);
  Serial.print("Device mode: "); Serial.println(msg);
  // attach callback for (successfully) sent and received messages
  DW1000Ng::attachSentHandler(handleSent);
  DW1000Ng::attachReceivedHandler(handleReceived);
  // anchor starts by transmitting a POLL message
  transmitPoll();
  noteActivity();
}

void noteActivity() {
  // update activity timestamp, so that we do not reach "resetPeriod"
  lastActivity = millis();
}

void resetInactive() {
  // tag sends POLL and listens for POLL_ACK
  expectedMsgId = POLL_ACK;
  DW1000Ng::forceTRxOff();
  transmitPoll();
  noteActivity();
}

void handleSent() {
  // status change on sent success
  sentAck = true;
}

void handleReceived() {
  // status change on received success
  Serial.println("RRRRRR");
  receivedAck = true;
}

void transmitPoll() {
  data[0] = POLL;
  DW1000Ng::setTransmitData(data, LEN_DATA);
  DW1000Ng::startTransmit();
}

void transmitRange() {
  data[0] = RANGE;

  /* Calculation of future time */
  byte futureTimeBytes[LENGTH_TIMESTAMP];

  timeRangeSent = DW1000Ng::getSystemTimestamp();
  timeRangeSent += DW1000NgTime::microsecondsToUWBTime(replyDelayTimeUS);
  DW1000NgUtils::writeValueToBytes(futureTimeBytes, timeRangeSent, LENGTH_TIMESTAMP);
  DW1000Ng::setDelayedTRX(futureTimeBytes);
  timeRangeSent += DW1000Ng::getTxAntennaDelay();

  DW1000NgUtils::writeValueToBytes(data + 1, timePollSent, LENGTH_TIMESTAMP);
  DW1000NgUtils::writeValueToBytes(data + 6, timePollAckReceived, LENGTH_TIMESTAMP);
  DW1000NgUtils::writeValueToBytes(data + 11, timeRangeSent, LENGTH_TIMESTAMP);
  DW1000Ng::setTransmitData(data, LEN_DATA);
  DW1000Ng::startTransmit(TransmitMode::DELAYED);
  //Serial.print("Expect RANGE to be sent @ "); Serial.println(timeRangeSent.getAsFloat());
}

void Uwb_loop() {
  if (!sentAck && !receivedAck) {
    // check if inactive
    if (millis() - lastActivity > resetPeriod) {
      resetInactive();
    }
    return;
  }
  // continue on any success confirmation
  if (sentAck) {
    sentAck = false;
    DW1000Ng::startReceive();
  }
  if (receivedAck) {
    receivedAck = false;
    // get message and parse
    DW1000Ng::getReceivedData(data, LEN_DATA);
    byte msgId = data[0];
    Serial.println(msgId);

    if (msgId != expectedMsgId) {
      // unexpected message, start over again
      //Serial.print("Received wrong message # "); Serial.println(msgId);
      expectedMsgId = POLL_ACK;
      transmitPoll();
      return;
    }
    if (msgId == POLL_ACK) {
      timePollSent = DW1000Ng::getTransmitTimestamp();
      timePollAckReceived = DW1000Ng::getReceiveTimestamp();
      expectedMsgId = RANGE_REPORT;
      Serial.println("RANGE");
      transmitRange();
      noteActivity();
    } else if (msgId == RANGE_REPORT) {
      expectedMsgId = POLL_ACK;
      float curRange;
      memcpy(&curRange, data + 1, 4);
      delay(10);
      transmitPoll();
      noteActivity();
    } else if (msgId == RANGE_FAILED) {
      expectedMsgId = POLL_ACK;
      transmitPoll();
      noteActivity();
    }
  }
}

// -------- UWB function (End) ------------


// -------- MPU function(start) -----------
void Mpu_init() {
  // Serial.begin(115200);
  Wire.begin();
  delay(100);

  if (!mpu.setup(0x68)) {  // change to your own address
      while (1) {
          Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
          delay(1000);
      }
  }

  mpu.selectFilter(QuatFilterSel::MADGWICK);
  mpu.verbose(true);
  mpu.calibrateAccelGyro();
  delay(1000);
  mpu.calibrateMag();
  mpu.verbose(false);
}


// void Mpu_loop() {
//   getIMU();
//   print_IMU();
//   vTaskDelay(1000);
// }




void getIMU() {
  if (mpu.update()) 
    update_quaternion();
    update_acc();
  
  vTaskDelay(10);
  
  
  //delay(10);
  if (mpu.update()) 
    update_quaternion();
    update_acc();
  
  // update_acc();
  vTaskDelay(100);
}

void update_quaternion() {
  imu_data.gyro_x = mpu.getQuaternionX();
  imu_data.gyro_y = mpu.getQuaternionY();
  imu_data.gyro_z = mpu.getQuaternionZ();
  imu_data.gyro_w = mpu.getQuaternionW();
}

void update_acc() {
  imu_data.acc_x = mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;
  imu_data.acc_y = mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;
  imu_data.acc_z = mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;
}

// void print_IMU() {
//   Serial.print("gyro_x: ");
//   Serial.println(imu_data.gyro_x);

//   Serial.print("gyro_y: ");
//   Serial.println(imu_data.gyro_y);

//   Serial.print("gyro_z: ");
//   Serial.println(imu_data.gyro_z);

//   Serial.print("gyro_w: ");
//   Serial.println(imu_data.gyro_w);

//   Serial.print("acc_x: ");
//   Serial.println(imu_data.acc_x);

//   Serial.print("acc_y: ");
//   Serial.println(imu_data.acc_y);

//   Serial.print("acc_z: ");
//   Serial.println(imu_data.acc_z);
// }

// -------- MPU function(End) -----------


// -------- button function(start) -------
void IRAM_ATTR buttonISR1() {
  buttonState1?buttonState1 = 0:buttonState1 = 1;
}

void IRAM_ATTR buttonISR2() {
  buttonState2?buttonState2 = 0:buttonState2 = 1;
}



// ---------- button function(end) --------










void beep_func1();
void beep_func2();
void beep_func3();

void TaskUWB(void *param) {
  for(;;) {
    Uwb_loop(); // update Distance
    //if(ret != 0.1)
      //Serial.println(ret);

    vTaskDelay(5);
  }
}

void TaskGetIMU(void *param) {
  for(;;) {

    getIMU(); // update IMU data

    vTaskDelay(500);
  }
}

void TaskBeep(void *param) {
  for(;;) {
    // We use extern value "rx_beep" in File: "blooth_lib.h" 
    if(rx_beep == 0) {
      ;
    }
    else if(rx_beep == 1) {
      beep_func1();
    }
    else if(rx_beep == 2) {
      beep_func2();
    }
    else if(rx_beep == 3) {
      beep_func3();
    }
    else {
      Serial.printf("?? why rx_beep is over 4 !!!!");
    }

    rx_beep = 0;

    vTaskDelay(1000);
  }
}

void TaskUwbDebug(void *param) {
  for(;;){
    Serial.print("is_debug1: ");
    Serial.println(is_debug1);
    Serial.print("is_debug2: ");
    Serial.println(is_debug2);

    vTaskDelay(2000);
  }
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Start");
  // put your setup code here, to run once:

  // Button
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(buttonPin1), buttonISR1, FALLING);
  attachInterrupt(digitalPinToInterrupt(buttonPin2), buttonISR2, FALLING);

  // IMU = MPU
  Mpu_init();
  delay(500);

  // UWB = Distance
  Uwb_setup();
  delay(500);

  // bluetooth
  blooth_lib_setup();
  delay(500);


  xTaskCreate(TaskUWB, "TaskUWB", 2048, NULL, 2, NULL);


  gpio_pad_select_gpio(34);
  gpio_set_direction(gpio_num_t(BUZZER_PIN), gpio_mode_t(2));
  xTaskCreate(TaskBeep, "TaskBeep", 1024, NULL, 10, NULL);

  xTaskCreate(TaskGetIMU, "TaskGetIMU", 2048, NULL, 1, NULL);

  xTaskCreate(TaskUwbDebug, "TaskUwbDebug", 1024, NULL, 12, NULL);
}

void loop() {
  // put your main code here, to run repeatedly:
  vTaskDelay(10000);
}



void beep_func1(){
  Serial.println("beep_func1");
  gpio_set_level(gpio_num_t(BUZZER_PIN), 1);
  vTaskDelay(100);
  gpio_set_level(gpio_num_t(BUZZER_PIN), 0);
}

void beep_func2(){
  Serial.println("beep_func2");
  for (int i = 0; i < 3; i++) {
    gpio_set_level(gpio_num_t(BUZZER_PIN), 1);
    vTaskDelay(100); 
    gpio_set_level(gpio_num_t(BUZZER_PIN), 0);
    vTaskDelay(300);
  }
}

void beep_func3(){
  Serial.println("beep_func3");
  gpio_set_level(gpio_num_t(BUZZER_PIN), 1);
  vTaskDelay(1000);
  gpio_set_level(gpio_num_t(BUZZER_PIN), 0);
}






