import RPi.GPIO as GPIO
import time


buzzer = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)
pwm = GPIO.PWM(buzzer, 262)


if __name__ == "__main__":
    pwm.start(50.0)
    time.sleep(0.5)
    pwm.stop()

    GPIO.cleanup()