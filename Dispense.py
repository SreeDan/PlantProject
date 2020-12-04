import RPi.GPIO as GPIO
import time


def dispense(seconds):
	GPIO.setmode(GPIO.BOARD)
	
	GPIO.setup(32, GPIO.OUT)
	GPIO.output(32, GPIO.HIGH)
	
	GPIO.output(32, GPIO.LOW)
	time.sleep(seconds)
	GPIO.output(32, GPIO.HIGH)
	GPIO.cleanup()
