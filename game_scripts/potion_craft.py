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


    def _get_triangle_vertex(self, array):
        if len(array) % 2 == 0:
            vertex = np.mean(array)
        else:
            l = int(np.ceil(len(array) / 2))
            start, stop = array[0], array[0] + l
            r = np.arange(start, stop)
            if (r == array[:l]).all():
                vertex = np.floor(np.mean(array[1:]))
            else:
                vertex = np.ceil(np.mean(array[:-1]))

        return int(vertex)


    def process(self):
        _state = 0
        _last_mean = 0
        _eq_count = 0
        while self.is_processing:
            image = self.window.get_roi_image()

            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            _, u_threshold = cv2.threshold(yuv[:,:,1], 110, 255, cv2.THRESH_BINARY)

            y = int(self.window.get_roi_height() * 0.82)
            xs = np.where(u_threshold[y, :] == 255)[0]
            xmean = self._get_triangle_vertex(xs)
            # print(f"xs: {xs}, xmean: {xmean}")

            v_blured = cv2.medianBlur(yuv[:,:,2], 3)

            cv2.line(image, (xmean, 0), (xmean, y), (0, 0, 255), 1)

            cv2.imshow('debug image', image)

            y = int(self.window.get_roi_height() * 0.4)
            v_mean = np.mean(v_blured[:y, xmean])

            if v_mean < 150:
                if _state != 0:
                    print('done')
                    pydirectinput.keyDown('space')
                    pydirectinput.keyUp('space')
                    self.is_processing = False
            else:
                if v_mean >= 160:
                    if _state !=2:
                        print('find!')
                        _eq_count = 0
                        _state = 2
                        pydirectinput.keyDown('space')
                        pydirectinput.keyUp('space')
                else:
                    _state = 1

            if v_mean == _last_mean and _state != 0:
                print(f'stop after {5 - _eq_count}')
                if _eq_count == 5:
                    self.is_processing = False
                _eq_count += 1
            _last_mean = v_mean

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