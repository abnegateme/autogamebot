from ppadb.client import Client as adbClient
import numpy as np
import cv2
import re

class Device(adbClient):
    def __init__(self):
        super().__init__()
        self.dev = self.devices()[0]

    def get_image(self):
        image = self.dev.screencap()
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, 1)

        return image

    def get_resolution(self):
        resp_str = self.dev.shell('wm size')
        res = re.findall(r'\d+', resp_str)
        return list(map(int, res))

if __name__ == "__main__":
    d = Device()
    print(d.get_resolution())