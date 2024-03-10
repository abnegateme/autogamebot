import sys
import os
import time
from threading import Thread
import pathlib


from pynput.keyboard import Key, KeyCode, Controller, Listener
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from window import Window


class Bot:
    def __init__(self, window_name='scrcpy'):
        self.window = Window(window_name)
        self.window.select_roi(store_or_load_roi=True)
        self.is_processing = False
        self.is_done = False

        self.keyboard = Controller()

        self.key_listener = Listener(on_press=self.keyboard_press)
        self.key_listener.start()


    def process(self):
        while self.is_processing:
            print('processing')
            time.sleep(0.1)
        print('processing done')


    def keyboard_press(self, key):
        if isinstance(key, Key):
            if key == Key.esc:
                self.is_done = True
                return False
        elif key.char == 'p':
            if self.is_processing:
                self.is_processing = False
            else:
                self.is_processing = True
                process_thread = Thread(target=self.process)
                process_thread.start()
                print('p pressed -> process start')