# Jetson Nano

## 환경 설정
### 선택 기준
- ROS2
- CUDA 활용

### 사전세팅
- OS: Ubuntu 20.04
1. micro SD 카드를 준비한다. (최소 사양 32GB 이상)
2. SD Card Formatter를 활용하여 micro SD 카드를 포맷시킨다. 
3. OS 이미지를 [다운로드](https://ln5.sync.com/dl/403a73c60/bqppm39m-mh4qippt-u5mhyyfi-nnma8c4t) 받는다.
4. [balenaEtcher](https://etcher.balena.io/)를 활용해서 microSD Card에 OS 이미지를 넣는다.
5. NVIDIA Jetson Nano에 microSD Card 장착 후 전원을 연결한다.
6. 아래 코드를 통해 현재 시간과 NVIDIA Jetson Nano 시간을 동기화한다. (인터넷 연결을 통해 동기화 할 수 있다면 동기화 한다)
    ```bash
    sudo date -s "2024-04-00 00:00:00"
    ```
7. SD Card 용량을 다 읽지 못한다면 GParted를 설치 후 용량을 늘린다. ([참고](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image/issues/4))

```bash
sudo apt-get install gparted
```
```bash
gparted
```

## reference
- [Jetson Nano with Ubuntu 20.04 OS image](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image?tab=readme-ov-file)