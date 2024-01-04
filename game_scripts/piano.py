from gettext import find
from window import Window
from device import Device
import numpy as np
import math
import cv2
from matplotlib import pyplot as plt
from pynput.mouse import Button, Controller
from pynput import keyboard
import time
import argparse
import sys
import time

window = Window('2201116PG')
width_step = window.get_width() // 8
forth_height = window.get_height() // 4
height_3_4 = 3 * forth_height

idx = [width_step, 3 * width_step, 5 * width_step, 7 * width_step]

mouse = Controller()
# button = Button()

# image = window.get_full_image()

# cv2.namedWindow('test')
# cv2.imshow('test', image)
# cv2.waitKey(0)
pushed = [False, False, False, False]
global is_stop
is_stop = False

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
        
def on_release(key):
    global is_stop
    print('{0} released'.format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        is_stop = True
        return False
 
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

while True:
    if is_stop:
        break
    image = window.get_full_image()
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    print(gray[height_3_4, idx])
    mask = gray[height_3_4, idx] < 30
    for i in range(4):
        if mask[i]:
            if not pushed[i]:
                mouse.position = window.geometry[0] + idx[i], window.geometry[1] + height_3_4 + 15
                time.sleep(0.015)
                mouse.click(Button.left, count=1)
                pushed[i] = True
                print(f"pushed {i}")
        else:
            pushed[i] = False


    # cv2.imshow('test', image)


    time.sleep(0.005)