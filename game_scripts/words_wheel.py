import sys
import argparse
import time
import cv2
import numpy as np

from pynput.mouse import Button, Controller, Listener

import pytesseract
if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r"D:\\soft\\Tesseract-OCR\\tesseract.exe"

from bot import Bot

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.joinpath('game_algs')))
from lookup_words import lookup_words

class Letter:
    def __init__(self):
        self.coords = None
        self.image = None
        self.symbol = None
        self.is_used = False

    def set_coords(self, coords):
        self.coords = coords

    def set_image(self, image):
        self.image = image

    def set_symbol(self, symbol):
        self.symbol = symbol

class WordsWheelBot(Bot):
    def __init__(self, window_name, verbose):
        super().__init__(window_name)
        self.verbose = verbose
        print(self.verbose)
        while not self.is_done:
            pass

    def process(self):
        print('process once thread wake up')

        if self.verbose:
            w = cv2.namedWindow('verbose_image')

        while self.is_processing:
            letters = []

            roi_img_gray = cv2.cvtColor(self.window.get_roi_image(), cv2.COLOR_BGR2GRAY)

            circles = cv2.HoughCircles(roi_img_gray,
                               cv2.HOUGH_GRADIENT,
                               dp=1.0,
                               minDist=30,
                               param1=50,
                               param2=50,
                               minRadius=20,
                               maxRadius=80)

            if circles is not None:
                if self.verbose:
                    verbose_image = roi_img_gray.copy()
                    circles_v = np.uint16(np.around(circles))
                    for i in circles_v[0, :]:
                        center = (i[0], i[1])
                        # circle center
                        cv2.circle(verbose_image, center, 1, (0, 100, 100), 3)
                        # circle outline
                        radius = i[2]
                        cv2.circle(verbose_image, center, radius, (255, 0, 255), 3)

                    cv2.imshow('verbose_image', verbose_image)
                    cv2.waitKey(0)

                circles = np.round(circles.reshape(-1, 3)).astype(np.int16)
            else:
                print('could\'t get letter circles, break')
                self.is_processing = False
                break

            i = 0
            for (x, y, r) in circles:
                letter = Letter()
                letter.set_coords((self.window.roi[0] + x, self.window.roi[1] + y))

                per = .8
                select_x = (x - int(r * per))
                select_y = (y - int(r * per))
                select_s = int(2 * r * per)

                select = roi_img_gray[select_y:(select_y + select_s),
                                    select_x:(select_x + select_s)]

                cv2.threshold(select, 254, 255, cv2.THRESH_OTSU, select)

                contours, _ = cv2.findContours(select, cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)
                bbs = np.array([cv2.boundingRect(ctr) for ctr in contours])

                max_width = 0
                max_idx = 0
                for idx, bb in enumerate(bbs):
                    width = bb[2] - bb[0]
                    if width == select_s:
                        continue
                    if width > max_width:
                        max_width = width
                        max_idx = idx

                bb = bbs[max_idx]
                select = select[:, bb[0]:bb[0] + bb[2]]

                if self.verbose:
                    cv2.imshow('verbose_image', select)
                    cv2.waitKey(0)


                kernel = np.ones((2, 2), 'uint8')

                select = cv2.dilate(select, kernel, iterations=1)

                letter.set_image(select)
                letters.append(letter)

            overall_image = np.full((100, len(letters) * 50 + 50), 255, dtype=np.uint8)

            for idx, letter in enumerate(letters):
                y, x = letter.image.shape
                shift_x = int((100 - x) / 2) + idx * 50
                shift_y = int((100 - y) / 2)
                overall_image[shift_y:shift_y + y, shift_x:shift_x + x] = letter.image

            symbols = pytesseract.image_to_string(overall_image,
                                          lang="rus",
                                          config=r'--oem 3 --psm 6')

            symbols = [e.lower() for e in symbols if e.isalnum()]
            print(f'detected symbols: {symbols}')
            try:
                for idx, sym in enumerate(symbols):
                    letters[idx].set_symbol(sym)
            except IndexError:
                cv2.imshow('', overall_image)
                cv2.waitKey(0)
                return


            words = lookup_words(symbols)
            print(words)

            # xr = self.window.roi[0]
            # yr = self.window.roi[1]
            # xw = self.window.geometry[0]
            # yw = self.window.geometry[1]
            mouse = Controller()
            for word in words:
                print(f'select {word}')
                time.sleep(0.4)
                coords = []
                for symbol in word:
                    for letter in letters:
                        if symbol == letter.symbol and not letter.is_used:
                            coords.append((letter.coords[0], letter.coords[1]))
                            letter.is_used = True
                            break
                current_pos = mouse.position
                mouse.move(coords[0][0] - current_pos[0],
                        coords[0][1] - current_pos[1])
                mouse.move(1, 1)
                mouse.press(Button.left)
                for cho in coords:
                    current_pos = mouse.position
                    time.sleep(0.1)
                    mouse.move(cho[0] - current_pos[0], cho[1] - current_pos[1])

                time.sleep(0.1)
                current_pos = mouse.position
                mouse.move(
                    int(self.window.roi[2] / 2) - current_pos[0],
                    int(self.window.roi[3] / 2) - current_pos[1])
                mouse.release(Button.left)
                for letter in letters:
                    letter.is_used = False

            if self.verbose:
                cv2.imshow('verbose_image', overall_image)
                cv2.waitKey(0)
            self.is_processing = False

        if self.verbose:
            cv2.destroyAllWindows()

    # def check_button(self, name):
    #     print(f'check {name} button tread start')

    #     do_click = True
    #     while True:
    #         time.sleep(0.5)
    #         region = (self.window.get_x(), self.window.get_y(),
    #                   self.window.get_width(), self.window.get_height())
    #         detected_box = pyautogui.locateOnScreen(f'{name}.png',
    #                                                 grayscale=True,
    #                                                 region=region,
    #                                                 confidence=0.6)

    #         if not detected_box is None and do_click:
    #             point = pyautogui.center(detected_box)
    #             print(f'detect {name} button on {point} - press once')
    #             current_pos = self.mouse.position
    #             self.mouse.move(int(point.x - current_pos[0]),
    #                             int(point.y - current_pos[1]))
    #             self.mouse.press(Button.left)
    #             self.mouse.release(Button.left)
    #             do_click = False
    #         else:
    #             do_click = True

    # def check_new_stage(self):
    #     print(f'check new stage tread start')

    #     while True:
    #         time.sleep(0.5)
    #         region = (self.window.get_x(), self.window.get_y(),
    #                   self.window.get_width(), self.window.get_height())
    #         detected_box = pyautogui.locateOnScreen('refresh.png',
    #                                                 grayscale=True,
    #                                                 region=region,
    #                                                 confidence=0.7)

    #         if not detected_box is None:
    #             if not self.new_stage:
    #                 print('it is new stage -- do process')
    #                 self.new_stage = True
    #         else:
    #             self.new_stage = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-wn', '--window_name', default='scrcpy', type=str)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    bot = WordsWheelBot(**vars(args))