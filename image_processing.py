import cv2
import numpy as np
from scipy.signal import argrelextrema
from matplotlib import pyplot as plt

def find_grid_by_maxima(image, refine=False):
    v, u = image.shape[:2]
    working_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    working_image = cv2.Canny(working_image, 1, 1, None, 3)

    X = np.sum(working_image, axis=0)
    order = round(0.05 * u)
    x = argrelextrema(X, np.greater, order=order, mode='wrap')[0]

    Y = np.sum(working_image, axis=1)
    order = round(0.05 * v)
    y = argrelextrema(Y, np.greater, order=order, mode='wrap')[0]

    if refine:
        def refine(grid, shape):
            mean_width = np.mean(np.diff(grid))
            start_point = 0
            if grid[0] - mean_width < 0:
                start_point = grid[0]

            return np.ceil(np.arange(start_point, shape, mean_width)).astype(int)

        x, y = refine(x, u), refine(y, v)

    plt.bar(range(u), X)
    plt.scatter(x, np.full_like(x, 0.5 * max(X)))
    plt.figure()
    plt.bar(range(v), Y)
    plt.scatter(y, np.full_like(y, 0.5 * max(Y)))
    plt.show()
    for xi in x:
        cv2.line( image, (xi, 0), (xi, v), (255,0,255), 1, cv2.LINE_AA);
    for yi in y:
        cv2.line( image, (0, yi), (u, yi), (255,0,255), 1, cv2.LINE_AA);

    cv2.imshow('grid', image)
    cv2.waitKey()

    return(x, y)