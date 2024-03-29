import sys
import mss
import numpy as np
import cv2
import time
import os

class Window():
    def __init__(self, name):
        self.name = name
        self.valid = False
        self.geometry = None
        self.roi = None
        self.lookup_geometry()

    def set_focus(self):
        self.focus()

    def is_valid(self):
        return self.valid

    def _get_image(self, crop):
        with mss.mss() as sct:
            image = sct.grab(crop)

        return np.array(image)

    def get_full_image(self):
        return self._get_image(tuple(self.geometry))

    def select_roi(self, from_center=False, store_or_load_roi=False):
        if store_or_load_roi:
            name = self.name.replace(' ', '_') + '.npy'
            if os.path.exists(name):
                self.roi = tuple(np.load(name).tolist())
                print(f'loaded roi: {self.roi}')
                return
        self.set_focus()
        image = self.get_full_image()
        _roi = cv2.selectROI('roi', image, fromCenter=from_center)
        self.roi = (
            self.geometry[0] + _roi[0],
            self.geometry[1] + _roi[1],
            self.geometry[0] + _roi[0] + _roi[2],
            self.geometry[1] + _roi[1] + _roi[3],
        )
        print(f'selected roi: {self.roi}')
        cv2.destroyWindow('roi')

        if store_or_load_roi:
            name = self.name.replace(' ', '_')
            np.save(name, self.roi)

    def get_roi_image(self):
        return self._get_image(self.roi)

    def get_width(self):
        return self.geometry[2] - self.geometry[0]

    def get_height(self):
        return self.geometry[3] - self.geometry[1]

    def get_roi_width(self):
        return self.roi[2] - self.roi[0]

    def get_roi_height(self):
        return self.roi[3] - self.roi[1]

    def lookup_geometry(self):
        if sys.platform == 'win32':
            from win32gui import EnumWindows, SetForegroundWindow, GetWindowRect, GetWindowText

            def callback(hwnd, extra):
                if self.name.lower() in GetWindowText(hwnd).lower():
                    self.geometry = list(GetWindowRect(hwnd))
                    self.focus = lambda: SetForegroundWindow(hwnd)
                    self.valid = True

                    self.geometry[0] += 8
                    self.geometry[1] += 25
                    self.geometry[2] -= 8
                    self.geometry[3] -= 8

            EnumWindows(callback, None)

        elif sys.platform == 'linux':
            from Xlib.display import Display
            from Xlib import X

            disp = Display()

            def find_window(window=None):
                global target_window
                if window is None:
                    window = disp.screen().root
                children = window.query_tree().children
                for win in children:
                    wm_class = win.get_wm_class()
                    if wm_class is not None and self.name.lower() in [
                            x.lower() for x in wm_class
                    ]:
                        self.id = win.id
                    find_window(win)

            find_window()
            if self.id is None:
                print(f'could not find {self.name}\'s window')
                self.valid = False
            else:
                self.valid = True

            w = disp.create_resource_object('window', self.id)

            def focus():
                w.set_input_focus(X.RevertToParent, X.CurrentTime)
                w.configure(stack_mode=X.Above)
                disp.sync()

            self.focus = focus

            p_geometry = w.query_tree().parent.get_geometry()
            px = p_geometry.x
            py = p_geometry.y

            m_geometry = w.get_geometry()
            mx = m_geometry.x
            my = m_geometry.y
            mw = m_geometry.width
            mh = m_geometry.height

            self.geometry = (px + mx, py + my, px + mx + mw, py + my + mh)


if __name__ == "__main__":
    name = 'scrcpy'
    w = Window(name)
    if w.is_valid():
        print(f'{name}\'s window geometry (x1, y1, x2, y2):')
        print(f'\t{w.geometry}')
        print(f'now setup {name}\'s window focus')
        w.set_focus()

        cv2.namedWindow('test_image')
        while True:
            k = cv2.waitKey(1) & 0xFF

            if k == ord('q'):
                break

            get_image_time = time.time()
            image = w.get_full_image()
            print(f'get image time: {time.time() - get_image_time}')

            cv2.imshow('test_image', image)

    cv2.destroyAllWindows()