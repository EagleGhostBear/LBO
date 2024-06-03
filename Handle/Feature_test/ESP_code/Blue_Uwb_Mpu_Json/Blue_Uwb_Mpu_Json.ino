#include "TwoWayRangingResponder.h"
#include "blooth_lib.h"
#include "driver/gpio.h"

#define BUZZER_PIN 25

void beep_func1();
void beep_func2();
void beep_func3();

void TaskUWB(void *param) {
  for(;;) {
    double ret = Uwb_loop();
    //if(ret != 0.1)
      //Serial.println(ret);

    vTaskDelay(10);
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

    vTaskDelay(500);
  }
}


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Start");
  // put your setup code here, to run once:

  blooth_lib_setup();

  delay(100);

  Uwb_setup();
  xTaskCreate(TaskUWB, "TaskUWB", 2048, NULL, 20, NULL);

  gpio_pad_select_gpio(34);
  gpio_set_direction(gpio_num_t(BUZZER_PIN), gpio_mode_t(2));
  xTaskCreate(TaskBeep, "TaskBeep", 1024, NULL, 10, NULL);
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

