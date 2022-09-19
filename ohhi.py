
from gettext import find
from window import Window
from device import Device
import numpy as np
import math
import cv2
from matplotlib import pyplot as plt
from pynput.mouse import Button, Controller
import time
import argparse
import sys

from image_processing import find_grid_by_maxima

def main(adb = False, mss = False, window_name='scrcpy'):

    if adb and mss:
        print('choose one method')
        return
    if not adb and not mss:
        return

    if adb:
        device = Device()
        image = cv2.cvtColor(device.get_image(), cv2.COLOR_BGR2GRAY)
        width, height = device.get_resolution()
        roi = [math.ceil(0.01 * width), math.ceil(0.28 * height),
               math.ceil(0.99 * width), math.ceil(0.47 * height)]
        shift_top = math.ceil(0.28 * height)
        shift_bottom = shift_top + math.ceil(0.47 * height)
        image = image[shift_top:shift_bottom, :]
        height, width = image.shape
        true_values = [86, 94]
        false_values = [107, 118]
        none_value = 33

    if mss:
        window = Window(window_name)
        if not window.is_valid():
            return
        window.select_roi()
        image = window.get_roi_image()
        mouse = Controller()

    grid_x, grid_y = find_grid_by_maxima(image, show=True)

    N_current = np.floor((len(grid_x) + len(grid_y)) / 2)

    x_half_width = np.mean(np.diff(grid_x)) / 2
    y_half_width = np.mean(np.diff(grid_y)) / 2

    xx, yy = np.meshgrid(grid_x + x_half_width, grid_y + y_half_width)

    # for x in grid_x + x_half_width:
    #     for y in grid_y + y_half_width:
    #         cv2.drawMarker(image, (int(x), int(y)), (255,0,255))

    # cv2.imshow('grid', image)
    # cv2.waitKey()
    # sys.exit()

    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)[:, :, 0]

    # rng = lambda x: np.arange(x, 2 * N_current * x, 2 * x)
    # xx, yy = np.meshgrid(rng(math.floor(0.5 * image.shape[1] / N_current)),
    #                      rng(math.floor(0.5 * image.shape[0] / N_current)))

    none_value = 60
    false_values = [25, 24]
    true_values = [114, 113]

    init_plate = image[yy.astype(int), xx.astype(int)].astype(np.int)
    print('init_plate\n', init_plate)
    plate = init_plate.copy()
    plate[plate == none_value] = 0
    plate[np.logical_or(*[plate == value for value in true_values])] = 1
    plate[np.logical_or(*[plate == value for value in false_values])] = -1


    states = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 1],
              [-1, -1, 0], [-1, 0, -1], [0, -1, -1]], dtype=np.int)
    replaces = np.array([[1, 1, -1], [1, -1, 1], [-1, 1, 1],
                [-1, -1, 1], [-1, 1, -1], [1, -1, -1]], dtype=np.int)

    def compute_1st(line):
        is_compute = False
        for p in np.arange(1, N_current-1):
            slc = line[p-1:p+2]
            idx = (states == slc).all(axis=1).nonzero()[0]
            if idx.size > 0:
                is_compute = True
                line[p-1:p+2] = replaces[idx[0]]

        n_empty = np.sum(line == 0)
        line_sum = np.sum(line)
        if n_empty != 0 and abs(line_sum) == n_empty:
            is_compute = True
            line[np.argwhere(line == 0)] = -1 * line_sum / n_empty

        return line, is_compute

    def compute_2nd(plate):
        is_compute = False
        for idx in range(0, N_current):
            if np.sum(plate[idx, :] == 0) == 2:
                is_compute = True
                ids = np.argwhere(plate[idx, :] == 0).flatten()
                work_plate = np.delete(plate, ids, 1)
                same = (work_plate == work_plate[idx, :]).all(axis=1)
                ids_line = np.argwhere(same).flatten()
                ids_line = ids_line[ids_line != idx]
                if ids_line.size != 1:
                    is_compute = False
                    continue
                plate[idx, ids[0]] = plate[ids_line[0], ids[1]]
                plate[idx, ids[1]] = plate[ids_line[0], ids[0]]
        return plate, is_compute


    is_compute = True
    itr = 0
    while is_compute:
        itr += 1
        print(f'iter: {itr}')
        print(plate)
        is_compute = False
        for idx in range(0, N_current):
            plate[:, idx], is_compute_row = compute_1st(plate[:, idx])
            is_compute = is_compute or is_compute_row
            plate[idx, :], is_compute_column = compute_1st(plate[idx, :])
            is_compute = is_compute or is_compute_column

        plate, is_s_compute = compute_2nd(plate)
        is_compute = is_compute or is_s_compute
        plate, is_s_compute = compute_2nd(plate.T)
        is_compute = is_compute or is_s_compute
        plate = plate.T

    print('final:')
    print(plate)

    plate[np.logical_or(*[init_plate == value for value in true_values])] = -2
    plate[np.logical_or(*[init_plate == value for value in false_values])] = -2

    # plate[np.logical_or(init_plate == true_colors[0], init_plate == true_colors[1])] = -2
    # plate[np.logical_or(init_plate == false_colors[0], init_plate == false_colors[1])] = -2

    print(plate)

    if mss:
        shift_x = 0
        for state, x, y in zip(plate.ravel(), xx.ravel(), yy.ravel()):
            if x == xx.ravel()[0]:
                shift_x = 3
            elif x == xx.ravel()[N_current-1]:
                shift_x = -3
            mouse.position = window.roi[0] + x + shift_x, window.roi[1] + y
            time.sleep(0.02)
            if state == 1:
                mouse.click(Button.left, count=1)
            elif state == -1:
                mouse.click(Button.left, count=1)
                time.sleep(0.02)
                mouse.click(Button.left, count=1)
            else:
                continue
            time.sleep(0.02)

    if adb:
        for state, x, y in zip(plate.ravel(), xx.ravel(), yy.ravel()):
            if state == 1:
                device.dev.shell(f'input tap {roi[0] + x} {roi[1] + y}')
            elif state == -1:
                device.dev.shell(f'input tap {roi[0] + x} {roi[1] + y}')
                device.dev.shell(f'input tap {roi[0] + x} {roi[1] + y}')


    # cv2.imshow('image', image)
    # cv2.waitKey(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--adb', action='store_true')
    parser.add_argument('--mss', action='store_true')
    parser.add_argument('--window_name', default='scrcpy', type=str)
    args = parser.parse_args()

    main(**vars(args))