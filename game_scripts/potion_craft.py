import sys
import os

sys.path.append('..')

from window import Window
import cv2
from pynput.keyboard import Key, KeyCode, Controller, Listener
import numpy as np
from matplotlib import pyplot as plt
import time
import pydirectinput
from threading import Thread

class PotionCraftBot:
    def __init__(self):
        self.window = Window('potion')
        self.window.select_roi(store_or_load_roi=True)
        self.is_processing = False

        self.keyboard = Controller()

        with Listener(on_press=self.keyboard_press) as key_listener:
            key_listener.join()

    def debug_process(self):
        while self.is_processing:
            print('processing')
            time.sleep(0.1)
        print('processing done')

    def process(self):
        _state = 0
        while self.is_processing:
            image = self.window.get_roi_image()

            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv_0 = yuv[:,:,2]
            _, threshold = cv2.threshold(yuv[:,:,1], 110, 255, cv2.THRESH_BINARY)

            xs = np.where(threshold[30, :] == 255)[0]

            xmean = int((xs[0] + xs[-1]) / 2)

            yuv_0 = cv2.medianBlur(yuv_0, 3)

            cv2.line(image, (xmean, 0), (xmean, 50), (0, 0, 255), 1)

            cv2.imshow('debug image', image)

            _mean = np.mean(yuv_0[:20, xmean])

            if _mean < 150:
                if _state != 0:
                    print('done')
                    pydirectinput.keyDown('space')
                    pydirectinput.keyUp('space')
                    self.is_processing = False
            else:
                if _mean >= 160:
                    if _state !=2:
                        print('find!')
                        _state = 2
                        pydirectinput.keyDown('space')
                        pydirectinput.keyUp('space')
                else:
                    _state = 1


            cv2.waitKey(1)

        cv2.destroyAllWindows()
        print('processing done')

    def keyboard_press(self, key):
        if isinstance(key, Key):
            if key == Key.esc:
                return False
        elif key.char == 'p':
            if self.is_processing:
                self.is_processing = False
            else:
                self.is_processing = True
                process_thread = Thread(target=self.process)
                process_thread.start()
                print('p pressed')

if __name__ == "__main__":
    bot = PotionCraftBot()