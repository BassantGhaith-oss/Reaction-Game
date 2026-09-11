#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import random
import os
from RPLCD.i2c import CharLCD

# defining
BUTTON = 17
GREEN = 22
RED = 23

# 7-segment
SEGMENTS = {
    'a': 16, 'b': 20, 'c': 21, 'd': 5, 'e': 6, 'f': 13, 'g': 19
}

DIGITS = {
    0: ['a','b','c','d','e','f'],
    1: ['b','c'],
    2: ['a','b','g','e','d'],
    3: ['a','b','g','c','d'],
    4: ['f','g','b','c'],
    5: ['a','f','g','c','d'],
    6: ['a','f','g','e','c','d'],
    7: ['a','b','c'],
    8: ['a','b','c','d','e','f','g'],
    9: ['a','b','c','d','f','g'],
}

HOME = os.path.expanduser("~")
best_time = None

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)

for pin in SEGMENTS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

lcd = CharLCD('PCF8574', 0x27)


def show_digit(number):
    for pin in SEGMENTS.values():
        GPIO.output(pin, GPIO.LOW)
    for seg in DIGITS[number]:
        GPIO.output(SEGMENTS[seg], GPIO.HIGH)


def update_lcd(last_ms, best_ms):
    lcd.clear()
    lcd.write_string(f"Time: {last_ms} ms")
    lcd.crlf()
    lcd.write_string(f"Best: {best_ms} ms")


def save_reading(ms):
    with open(f"{HOME}/reaction/data/readings.txt", "a") as f:
        f.write(f"{ms} ms\n")


def play_round():
    GPIO.output(GREEN, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)

    wait_time = random.uniform(2, 5)

    start_wait = time.time()
    while time.time() - start_wait < wait_time:
        if GPIO.input(BUTTON) == GPIO.LOW:
            GPIO.output(RED, GPIO.HIGH)
            print("Foul! You pressed too early.")
            time.sleep(1)
            GPIO.output(RED, GPIO.LOW)
            return None

    GPIO.output(GREEN, GPIO.HIGH)
    start_time = time.time()

    while GPIO.input(BUTTON) == GPIO.HIGH:
        pass

    end_time = time.time()
    GPIO.output(GREEN, GPIO.LOW)

    reaction_ms = int((end_time - start_time) * 1000)
    return reaction_ms


try:
    while True:
        print("Get ready...")
        result = play_round()

        if result is not None:
            print(f"Time: {result} ms")
            save_reading(result)

            if best_time is None or result < best_time:
                best_time = result

            update_lcd(result, best_time)

            hundreds_digit = (result // 100) % 10
            show_digit(hundreds_digit)

        time.sleep(2)

except KeyboardInterrupt:
    print("Game stopped.")

finally:
    lcd.clear()
    GPIO.cleanup()