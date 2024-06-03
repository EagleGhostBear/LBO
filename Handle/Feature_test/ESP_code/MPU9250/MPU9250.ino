// #include "mpu_lib.h"
#include "MPU9250.h"


struct IMU_Return_t {
  float gyro_x;
  float gyro_y;
  float gyro_z;
  float gyro_w;

  float acc_x;
  float acc_y;
  float acc_z; 
};

IMU_Return_t imu_data;

void getIMU();
void update_quaternion();
void Mpu_init();
void Mpu_loop();
void print_IMU();
void update_acc();

MPU9250 mpu;



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


void Mpu_loop() {
  getIMU();
  print_IMU();
  vTaskDelay(1000);
}




void getIMU() {
  if (mpu.update()) 
    update_quaternion();
  
  
  vTaskDelay(10);
  
  
  //delay(10);
  if (mpu.update()) 
    update_quaternion();

  update_acc();
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

void print_IMU() {
  Serial.print("gyro_x: ");
  Serial.println(imu_data.gyro_x);

  Serial.print("gyro_y: ");
  Serial.println(imu_data.gyro_y);

  Serial.print("gyro_z: ");
  Serial.println(imu_data.gyro_z);

  Serial.print("gyro_w: ");
  Serial.println(imu_data.gyro_w);

  Serial.print("acc_x: ");
  Serial.println(imu_data.acc_x);

  Serial.print("acc_y: ");
  Serial.println(imu_data.acc_y);

  Serial.print("acc_z: ");
  Serial.println(imu_data.acc_z);
}

void setup() {
  Serial.begin(115200);
  Mpu_init();
}

void loop() {
  Mpu_loop();
}

