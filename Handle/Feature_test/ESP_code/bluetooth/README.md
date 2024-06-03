# ESP32 Bluetooth
Author: 김영래 (문제있으면 알려주세요)
date: 2024-04-29

해당 코드의 특징
- FreeRTOS 사용
- Bluetooth 사용 (인터럽트 방식)

## FreeRTOS 사용방법
ESP32에서는 FreeRTOS가 자체적으로 내장되어 있다.
따라서 FreeRTOS의 API를 call하기만 하면 바로 사용가능하다.


아래는 기본적인 FreeRTOS의 예시 코드다.

### 들어가기 앞서
FreeRTOS나 uC/OS-II와 같은 임베디드의 Kernel, RTOS에서는 multi-threading이라는 말을 쓰지 않는다. 리눅스에서 모든 작업은 결국 Task단위이라는 교수님의 말도 있었다.
따라서 본 문서에서도 multi-tasking으로 한다.

### Task 만들기
- vTaskCreate()
- vTaskDelay()
- vTaskDelete()

```c
void Task1(void *param) {
    for(;;) {
        실제 작업

        vTaskDelay( 정수 ); // 단위 Tick(=1ms)
    }
    VTaskDelete(NULL);
}

void setup() {
    // vTaskCreate(함수이름, 함수닉네임, 태스크 스택 사이즈, param으로 넘겨줄거, 우선순위, 태스크 핸들=태스크 실제 주소)
    vTaskCreate(Task1, "Task1", 1024, NULL, 1, NULL);
}

```

우선순위는 숫자가 작을수록 우선도가 높음
함수닉넴임은 꼭 함수이름과 같을 필요는 없음


그러면 이제 실습을 해보자.
Task1, Task2, Task3는 각각 1, 2, 3초마다 Taskn을 출력한다.
우선순위는 task 1, 2, 3 순이다.

```c
void Task1(void *param) { // void *param은 필수다.
    for(;;) {
        Serial.println("Task1");
        vTaskDelay(1000);
    }
    // 이 경우에 따로 삭제 함수 vTaskDelete()는 필요없다. 
}

void Task2(void *param) { // void *param은 필수다.
    for(;;) {
        Serial.println("Task2");
        vTaskDelay(2000);
    }
    // 이 경우에 따로 삭제 함수 vTaskDelete()는 필요없다. 
}

void Task3(void *param) { // void *param은 필수다.
    for(;;) {
        Serial.println("Task3");
        vTaskDelay(3000);
    }
    // 이 경우에 따로 삭제 함수 vTaskDelete()는 필요없다. 
}

void setup() {
    vTaskCreate(Task1, "Task1", 1024, NULL, 1, NULL);
    vTaskCreate(Task2, "Task2", 1024, NULL, 2, NULL);
    vTaskCreate(Task3, "Task3", 1024, NULL, 3, NULL);
}

void loop() {
    vTaskDelay(100000);
}
```
여기서 중요한 점은 loop()안에 vTaskDelay()를 해야한다.
실험으로는 Tick Interrupt가 발생해도 우선순위가 loop()가 높은지, Task들이 실행하지 않았다.

그리고 Delay()를 사용해선 안된다.
core자체가 해당 시간만큼 task에서 대기해서 그 어떤 작업도 진행하지 않는다.


### 세마포
- SemaphoreHandle_t semaphore변수명;
- semaphore = xSemaphoreCreateBinary(); // ON/OFF
- semaphore = xSemaphoreCreateCounting(최대크기, init크기);
- if (xSemaphoreTake(semaphore, portMAX_DELAY) == pdTRUE)
- xSemaphoreGive(semaphore);

세마포는 자원의 공유를 위해 사용된다.