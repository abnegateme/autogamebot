import sys
import os

sys.path.append('..')

from window import Window
import cv2
# from pynput.mouse import Button, Controller
from pynput.keyboard import Key, Controller, Listener
import numpy as np
from matplotlib import pyplot as plt
import time
import pydirectinput

class PotionCraftBot:
    def __init__(self):
        self.window = Window('potion')
        self.window.select_roi(store_or_load_roi=True)
        self.is_done = False

        self.klis = Listener(on_release=self.on_esc_release)
        self.klis.start()

        # self.mouse = Controller()
        self.keyboard = Controller()
        self.state = 0

        while True:
            if self.is_done:
                break
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
                if self.state != 0:
                    print('done')
                    pydirectinput.keyDown('space')
                    pydirectinput.keyUp('space')
                    self.is_done = True
            else:
                if _mean >= 160:
                    if self.state !=2:
                        print('find!')
                        self.state = 2
                        pydirectinput.keyDown('space')
                        pydirectinput.keyUp('space')
                else:
                    self.state = 1


            cv2.waitKey(1)

        cv2.destroyAllWindows()

    def on_esc_release(self, key):
        if key == Key.esc:
            # Stop listener
            self.is_done = True
            return False

if __name__ == "__main__":
    bot = PotionCraftBot()