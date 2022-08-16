import sys
import mss
import time
import numpy as np

class Window():
    def __init__(self, name):
        self.name = name
        self.id = None
        self.lookup_geometry()

    def set_focus(self):
        self.focus()

    def is_valid(self):
        return self.valid

    def _get_image(self, crop):
        image = mss.mss().grab(crop)

        return np.array(image)

    def get_full_image(self):
        return self._get_image(self.geometry)

    def set_roi(self, x, y, w, h):
        x1, y1, _, _ = self.geometry
        self.roi = (x1 + x, y1 + y, x1 + x + w, y1 + y + h)

    def get_roi_image(self):
        return self._get_image(self.roi)

    def lookup_geometry(self):
        if sys.platform == 'win32':
            from win32gui import EnumWindows, SetForegroundWindow, GetWindowRect, GetWindowText

            def callback(hwnd, extra):
                if self.name.lower() in GetWindowText(hwnd).lower():
                    self.id = hwnd

            EnumWindows(callback, None)

            if self.id is None:
                print(f'could not find {self.name}\'s window')
                self.valid = False
            else:
                self.valid = True

            def focus():
                SetForegroundWindow(self.id)

            self.focus = focus

            self.geometry = GetWindowRect(self.id)

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

    def get_width(self):
        return self.geometry[2] - self.geometry[0]

    def get_height(self):
        return self.geometry[3] - self.geometry[1]

    def get_roi_width(self):
        return self.roi[2] - self.roi[0]

    def get_roi_height(self):
        return self.roi[3] - self.roi[1]

if __name__ == "__main__":
    name = 'scrcpy'
    w = Window(name)
    if w.is_valid():
        print(f'{name}\'s window geometry (x1, y1, x2, y2):')
        print(f'\t{w.geometry}')
        print(f'now setup {name}\'s window focus')
        w.set_focus()
        image = w.get_full_image()