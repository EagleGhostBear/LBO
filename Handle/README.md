# Handle
Author: 김영래, 김태환

Date(Latest): 2024-05-23

요약: 시각장애인을 위한 손잡이(조작기) SW 개발

<br><br>

## 목록
- [1. 들어가기 앞서](#1-들어가기-앞서)
    - [1-1. 손잡이를 만들게 된 이유](#1-1-손잡이를-만들게-된-이유)
    - [1-2. 포팅 메뉴얼](#1-2-포팅-메뉴얼)
    - [1-2-1. IDE 설치 및 보드 인식](#1-2-1-ide-설치-및-보드-인식)
    - [1-2-2. 라이브러리 설치](#1-2-2-라이브러리-설치)

- [2. Handle 제작도 및 제작품](#2-handle-제작도-및-제작품)

- [3. 하드웨어 구성](#3-하드웨어-구성)

- [4. 기술 스택(SW)](#4-기술-스택sw)

- [5. Handle 폴더 구조](#5-handle-폴더-구조)

- [6. 기술 정리 및 설명](#6-기술-정리-및-설명)
    - [6-1. 참고 사항](#6-1-참고-사항)
    - [6-2. 거리 측정](#6-2-거리-측정)
    - [6-3. 사용자 속도 방향 측정](#6-3-사용자-속도-방향-측정)
    - [6-4. 목적지 입력](#6-4-목적지-입력)
    - [6-5. 이동방향 안내](#6-5-이동방향-안내)
    - [6-6. 통신 bluetooth](#6-6-통신-bluetooth)
    - [6-6-1. 세마포](#6-6-1-semaphore)
    - [6-7. FreeRTOS](#6-7-freertos)
    - [6-8. Interrupt](#6-8-interrupt)

- [7. 이슈 사항](#7-이슈-사항)



<br><br>

## 1. 들어가기 앞서

### 1-1. 손잡이를 만들게 된 이유
---

안내 로봇과 함께 시각 장애인이 실내를 이동하는데 큰 어려움이 없도록 손잡이(조작기)를 만들었습니다.

<br><br>

### 1-2. 포팅 메뉴얼
---

#### 1-2-1. IDE 설치 및 보드 인식

https://www.arduino.cc/en/software 에서 운영체제에 맞는 파일을 다운/설치한다.

<img src="./img/ESP32DEV.PNG" width=500px>

처음 보드를 연결해도 unknown으로 인식된다.

사진과 같이 직접 인식시켜줘야 한다.

#### 1-2-2. 라이브러리 설치

<img src="./img/MPU9250.PNG" width=500px>

IMU 센서

<img src="./img/ESP32Servo.PNG" width=500px>

Servo Motor

https://github.com/F-Army/arduino-dw1000-ng

<img src="./img/ZIPADD.PNG" width=500px>

UWB (사진처럼 zip 파일로 라이브러리 추가 작업 필요)

<br><br>

## 2. Handle 제작도 및 제작품

<img src="./img/Handle.jpg" width="500px">

<br><br>

## 3. 하드웨어 구성

보드: ESP32 (풀네임: ESP WROOM-32) 3개

UWB(DWM1000), IMU(MPU9250), Servo motor(MG996R), Button(없음)

<img src="./img/Handle_HW.png" width="500px">


<br><br>

## 4. 기술 스택(SW)
```
RTOS: FreeRTOS
WatchDog
Json <-> String Parsing
Bluetooth
PWM (Phase Width Modulation)
Qt (PySide6)
ROS2
기타 임베디드 스킬(GPIO, Interrupt, Uart, I2C, SPI 등등)
```

<br><br>

## 5. Handle 폴더 구조
```
Handle
|
├─development               // 실제 시연에서 사용된 코드들입니다.
│  ├─ESP_UWB_STR_WATCHDOG   // UWB Tag 코드입니다.
│  ├─Initator               // UWB Anchor 코드입니다.
│  └─TotalCode_STR          // IMU, Servo Motor, Bluetooth, Button 코드입니다.
|
|
├─Feature_test              // 개발을 위한 기능 개발 코드들 입니다.
│  ├─ESP_code
│  │  ├─blooth
│  │  ├─BlueAndUwb
│  │  ├─BlueAndUwbAndJson
│  │  ├─BlueAndUwbAndJson2
│  │  ├─bluetooth
│  │  ├─bluetooth_Li
│  │  │  └─bluetooth
│  │  ├─Blue_Uwb_Mpu_Json
│  │  ├─Blue_Uwb_Mpu_Json2
│  │  ├─Blue_Uwb_Mpu_Json_Servo
│  │  ├─extern_Lib
│  │  │  └─main
│  │  ├─FreeRTOS_ESP
│  │  ├─JsonFormat
│  │  ├─JsonFormat2
│  │  ├─MPU9250
│  │  ├─Servoring
│  │  ├─tasking
│  │  │  └─semaphore
│  │  └─UWB_Thread
│  └─python_code
│      ├─bluetooth
│      └─Json
└─img
```

<br><br>

## 6. 기술 정리 및 설명

### 6-1. 참고 사항

---

총 3개의 ESP32를 사용하기 떄문에 문서 이해에 어려움이 있습니다.
따라서 ESP32 마다 별칭을 만들었습니다.

- ESP32_Total   : UWB 기능을 제외한 나머지를 구동하는 ESP32입니다.
- ESP32_Tag     : UWB의 Tag 기능을 구동하며, distance 값을 ESP32_Total에게 Uart로 전달합니다.
- ESP32_Anchor  : UWB의 Anchor 기능을 구동합니다.

<br><br>

### 6-2. 거리 측정

---

- 실내에서 정밀한 사용자 위치 추정을 위해 안내 로봇과 안내 손잡이의 거리를 측정
- 두 기기에 UWB 통신 모듈(DWM1000)을 설치하고 ToF(Time if Flight)방식으로 거리를 측정

- 기기 구성 및 거리 측정 방법
    
    <aside>
    💡 거리 측정 방식으로 UWB 기술을 사용한 이유
    
    - 해당 기술은 cm단위의 거리 측정이 가능하며, 이는 타 통신방식(블루투스, Wifi) 대비 10배 이상의 정밀도를 보임
    </aside>
    
    - 각 기기에는 통신 모듈(DWM1000)이 ESP32 MCU보드에 연결된 상태로 설치
    - 아래 방식과 같이 두 모듈은 서로 신호를 주고 받음
        - DS-TWR(Double-Sided Two-Way Ranging)
            
            <img src="./img/DS_TWR1.png" width="500px">
            
            [https://www.jkiees.org/archive/view_article?pid=jkiees-33-1-1](https://www.jkiees.org/archive/view_article?pid=jkiees-33-1-1)
            
    - 통신모듈은 신호를 받은 시점과 보내는 시점을 ESP32에 SPI 통신을 통해 전송
    - ESP32는 각 시점에 대한 정보를 가지고 아래의 수식을 통해 두 기기간 거리를 연산
        - ToF(Time of Flight) 시간 계산 공식
            
            <img src="./img/DS_TWR2.png" width="500px">
            
            [https://www.jkiees.org/archive/view_article?pid=jkiees-33-1-1](https://www.jkiees.org/archive/view_article?pid=jkiees-33-1-1)
            
        
- 측정된 거리는 Main ESP32에 UART통신으로 전송하여 거리 정보 외 IMU센서, 버튼 상태 등의 정보와 결합하여 안내 로봇과 블루투스로 전달
    
    <aside>
    💡 ESP32를 2개로 분리한 이유
    
    - 안내 손잡이는 FreeRTOS에서 멀티태스킹 형태로 구현
    - IMU센서, 거리, 버튼 상태 등 여러 정보를 각각의 Task가 취득하여 블루투스로 전달
    - UWB 통신의 원리가 다회의 신호 송수신을 통해 신호의 파형을 구형파 형태로 변환해야 하기 때문에 하나의 Task 단위에서 측정하는 것이 불가능
    - 따라서, UWB 거리 측정을 위한 별도의 MCU보드를 두어야 해서 ESP32를 2개로 분리
    </aside>
    
<br>

- Watchdog 기능을 추가하여 거리가 일정 시간 이상 측정되지 않을 때, 하드웨어 리셋하여 측정 중 간헐적 끊김 현상 개선

<br><br>

### 6-3. 사용자 속도, 방향 측정

---


```markdown
***목적***

MPU9250(IMU)에는 9축(gyro, acc, mag)의 값을 I2C 통신으로 값을 읽어옵니다.
우리는 이 값들을 입력으로 Madgwick(매드윅)필터를 거쳐 시각장애인의 위치 변화를 예측합니다.
```

ESP32_Total과 연결됩니다.

FreeRTOS의 Multi-Tasking을 이용해 주기적으로 변화를 측정합니다.

측정된 값들은 로봇에게 블루투스로 전달합니다.

<br><br>

### 6-4. 목적지 입력

---


```markdown
***목적***

시각장애인이 건물 내 방문할 목적지와 혹시 이용할 목적지(화장실 등)의 위치로 이동하는 경우 안내 로봇에게 명령을 하기 위해 사용됩니다.
```

ESP32_Total의 GPIO와 버튼을 연결합니다.

ESP32_Total의 GND와 버튼의 반대쪽 핀을 연결합니다.

ESP32의 내부 PULL-UP(저항)모드를 이용해 회로를 간단하게 구성합니다.

인터럽트로 눌림을 감지합니다.

<br><br>

### 6-5. 이동방향 안내

---

```markdown
***목적***

안내 로봇이 앞서 나가면서 시각장애인이 안전히 이동 가능하도록 
이동 방향을 촉각 정보로 전달합니다.
전방을 90도로 하며, 左는 0도, 右는 180도입니다. 
```

시각장애인에게 진행할 방향에 대해 안내하기 위해 서보모터(MG996R)의 각도를 제어합니다.

MG996R를 위한 PWM(펄스 폭 변조)신호의 동작 주기인 20us에서 듀티사이클을 조작해 각도를 제어합니다.

각도는 로봇으로 부터 블.루투스로 0~180의 정수값으로 받아옵니다.

<br><br>

### 6-6. 통신 (Bluetooth)

---

```markdown
***목적***

안내 로봇과 통신을 위해 사용합니다.
IMU, UWB, Button의 정보를 시간과 함께 송신하고 
이동 방향의 정보를 가지는 Servo Motor의 회전각을 수신 받습니다. 
```

ESP32에는 블루투스 4.2 모듈(BLE-Bluetooth Low Energy 아님)이 내장되어 있습니다.

乙의 블루투스 모듈을 이용해, 로봇(Jetson nano)의 ac-8265 모듈과 통신합니다.

통신에는 송신과 수신이 있습니다. 

Json포맷을 String으로 변경해서 송신합니다. Json의 끝을 알리기 위해 ‘@’을 문자열을 전부 보내고 추가로 보냅니다. (’{’와 ‘}’의 갯수 비교보다 훨씬 간단함)

수신도 마찬가지로 ‘@’를 기준으로 문자열의 끝을 판단합니다.

수신은 인터럽트 방식을 사용하는데, UART와 달리 byte단위로 인터럽트가 걸리기 때문에 문제가 없습니다. (물론, 상대측의 송신이 매우 빠르면 수용 가능한 인터럽트 중첩 수보다 많아져서 보드가 reset됩니다)

‘@’를 만나면 수신한 문자열을 Json으로 파싱하고, 전역변수를 업데이트하는 Task에게 Semaphore를 Give합니다.

<br>

#### 6-6-1. Semaphore

(Semaphore를 사용하는 이유; Task는 multi tasking이기 때문에 일정 시간마다 읽는데 문자열을 다 받기 전에 읽으면 위험하다. 즉, 동기화를 해야만 한다. 이 동기화를 위해 Semaphore를 사용한다.) (Take와 Give가 있다. 만약 semaphore가 없는데 Take하면, 누군가 semaphore를 Give할 때 까지 대기한다.)

(일상 생활의 예시: 배고픈 나라의 밀가루 제분과 빵 굽기. 배고픈 나라에서 사람들에게 빵을 만들고자 한다. 밀가루 제분과 빵 굽기를 해야하는데 두 일을 동시에 하지 못하며, 최대한 빨리 배고픔을 해소시키기 위해 빵 굽는게 더 우선시 된다. 하지만 밀가루가 없으면 빵을 못 만든다. 이런 경우 세마포를 사용한다)

송신과 수신은 둘 다 멀티 태스킹을 이용한다.

<br><br>

### 6-7. FreeRTOS

---

```Markdown
***목적***

Multi Tasking: Task마다 먼저 진행할 우선순위가 있습니다. 이를 위해 멀티 태스킹을 사용합니다.

Semaphore: 동일한 자원을 사용하는 경우 멀티 태스킹에 의해 같이 접근함으로서 문제가 생길 수 있습니다. 자세한 내용은 "6-6-1. Semaphore" 를 참고해주세요.

WatchDog: 임베디드 특성상 시스템의 높은 신뢰성을 요구합니다. 이를 위해 비정상적인 작동을 하면 다시 부팅하는 절차를 밟습니다.




***안 쓰면 벌어지는 일***

기존의 절차지향 코드는 우선순위와 상관없이 앞의 내용을 끝내야 뒷 내용을 진행하는데, 이러면 일의 우선도에 상관없이 진행된다.
이러면 정작 중요한 일을 해야할 시기에 다른 작업들을 다 해야한다.

이를 위해 FreeRTOS를 사용하는데, 각 Task마다 우선순위를 지정해 우선순위가 높은 Task를 먼저 수행하도록 한다.
```

```C
// Multi Tasking 구현 방법

void Task(void *param) { // Task 생성
  for(;;) {
    // 작업 추가
    vTaskDelay(500);
  }

  vTaskDelete(); // 무한루프면 없어도 동작함
}

// xTaskCreate(Task, "Task별명", 스택 사이즈, param, 우선순위, pxCreatedTask);

void main() {
    xTaskCreate(Task, "Task", 2048, NULL, 1, NULL);
}


// --------------------------------------------------------------------------



// Semaphore 구현 방법

SemaphoreHandle_t semaphore_b; // 세마포 변수 생성


void TaskOrISR() {
    xSemaphoreGive(rx_semaphore_b); // 세마포 할당
}


void Task(void *param) {
    if(xSemaphoreTake(rx_semaphore_b, portMAX_DELAY) == pdTRUE) { // 세마포 take 및 대기
        // 작업
    }
}


void main() {
    semaphore_b = xSemaphoreCreateBinary(); // 바이너리로 지정
}


// -------------------------------------------------------------------------



// WatchDog 구현 방법

void main() {
    esp_task_wdt_init(10, true); // 데드라인 10초로 지정
    esp_task_wdt_add(NULL);  // 대상 지정
}


void Task(void *param) {
    for(;;) {
        // ...
        esp_task_wdt_reset(); // 타이머 리셋
        // ...
    }
}
```

<br><br>

### 6-8. Interrupt

---

```markdown
***목적***

1. 더 빠른 반응을 위해 사용한다. 
2. 폴링 방식 보다 더 적은 리소스 사용을 위해 사용한다.



***안 쓰면 벌어지는 일***

만약 인터럽트를 사용하지 않으면 버튼을 눌렀는지 계속 지켜보고 있어야 한다. (이를 폴링 방식이라 한다) 이는 매우 비효율적이며, 계속 지켜보고 있어야 하기 때문에 다른 작업을 수행하지 못하고, 멀티태스킹을 이용한다고 해도, 정작 지켜보는 태스크가 수행을 안 하고 있으면 놓친다.


```

```c
// 블루투스 인터럽트 구현 방법

BluetoothSerial SerialBT;

void rxInterrupt(esp_spp_cb_event_t event, esp_spp_cb_param_t *param) {
  if (event == ESP_SPP_DATA_IND_EVT) { 
    while(SerialBT.available()) {
      // ...
    }
  }
}

void main() {
    SerialBT.register_callback(rxInterrupt);
}
```




<br><br>

## 7. 이슈 사항

TODO
UART 인터럽트 방식