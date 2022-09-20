import cv2
import numpy as np
from scipy.signal import argrelextrema
from matplotlib import pyplot as plt

def find_maxima(image, axis, kernel=5):
    inv_axis = abs(axis-1)
    grad = cv2.Sobel(image, cv2.CV_64F, inv_axis, axis, kernel)

    S = np.sum(grad, axis=axis)
    order = round(0.05 * image.shape[inv_axis])
    return S, argrelextrema(S, np.greater, order=order, mode='wrap')[0]

def find_grid_by_maxima(image, kernel=5, verbose=False):
    working_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    working_image = cv2.GaussianBlur(working_image, (kernel, kernel), sigmaX=0)

    X, x = find_maxima(working_image, 0, kernel)
    Y, y = find_maxima(working_image, 1, kernel)

    if verbose:
        v, u = image.shape[:2]
        plt.figure()
        plt.grid()
        plt.xlim([0, u])
        plt.plot(range(u), X, '--r')
        plt.scatter(x, X[x])
        plt.figure()
        plt.grid()
        plt.xlim([0, v])
        plt.plot(range(v), Y, '--r')
        plt.scatter(y, Y[y])
        plt.show()
        for xi in x:
            cv2.line( image, (xi, 0), (xi, v), (255,0,255), 1, cv2.LINE_AA);
        for yi in y:
            cv2.line( image, (0, yi), (u, yi), (255,0,255), 1, cv2.LINE_AA);

        cv2.imshow('grid', image)
        cv2.waitKey()

    return x, y
