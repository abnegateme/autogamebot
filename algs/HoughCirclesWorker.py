import cv2
import numpy as np


def show_letter_circles_image(image, circles, win_name):
    img = image.copy()
    for (x, y, r) in circles:
        cv2.circle(img, (x, y), r, (0, 0, 255), 2)
    cv2.imshow(win_name, img)


class HoughCirclesWorker():
    def __init__(self, image):
        self.image = image
        self.mimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.dp = 10
        self.mindist = 30
        self.maxr = 100
        self.minr = 10
        self.param1 = 50
        self.param2 = 50
        cv2.namedWindow('circles', cv2.WINDOW_NORMAL)
        cv2.createTrackbar('dp', 'circles', self.dp, 50, self.on_dp)
        cv2.createTrackbar('mindist', 'circles', self.mindist, 150,
                           self.on_mindist)
        cv2.createTrackbar('maxr', 'circles', self.maxr, 150, self.on_maxr)
        cv2.createTrackbar('minr', 'circles', self.minr, 150, self.on_minr)
        cv2.createTrackbar('param1', 'circles', self.param1, 200,
                           self.on_param1)
        cv2.createTrackbar('param2', 'circles', self.param2, 200,
                           self.on_param2)
        self.on_dp(self.dp)
        self.on_mindist(self.mindist)
        self.on_maxr(self.maxr)
        self.on_maxr(self.minr)
        self.on_param1(self.param1)
        self.on_param2(self.param2)
        cv2.imshow('circles', image)
        cv2.waitKey()

    def render(self):
        circles = cv2.HoughCircles(self.mimage,
                                   cv2.HOUGH_GRADIENT,
                                   self.dp,
                                   self.mindist,
                                   maxRadius=self.maxr,
                                   minRadius=self.minr,
                                   param1=self.param1,
                                   param2=self.param2)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            show_letter_circles_image(self.image, circles, 'circles')
        else:
            cv2.imshow('circles', self.image)

    def on_dp(self, val):
        self.dp = val / 10.0
        self.render()

    def on_mindist(self, val):
        self.mindist = val
        self.render()

    def on_maxr(self, val):
        self.maxr = val
        self.render()

    def on_minr(self, val):
        self.minr = val
        self.render()

    def on_param1(self, val):
        self.param1 = val
        self.render()

    def on_param2(self, val):
        self.param2 = val
        self.render()