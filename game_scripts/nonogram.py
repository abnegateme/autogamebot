import numpy as np
import cv2
from algs.nonogram_draw import Field
from algs.nonogram import Nonogram


def main():
    ver_numbers = [
        [2, 2, 2],
        [1, 1, 2],
        [2, 2, 1],
        [1, 2, 4],
        [3, 5],
        [3, 5],
        [1, 2, 4],
        [2, 2, 1],
        [1, 1, 2],
        [2, 2, 2],
    ]
    hor_numbers = [
        [2, 4, 2],
        [1, 1, 2, 1, 1],
        [6],
        [1, 1],
        [1, 2, 1],
        [10],
        [6],
        [4],
        [2, 4, 2],
        [3, 3],
    ]
    n = Nonogram(len(ver_numbers), ver_numbers, hor_numbers)
    n.solve()
    field = Field(len(ver_numbers), 50)
    field.add_ver_numbers(ver_numbers)
    field.add_hor_numbers(hor_numbers)
    field.fill_by_array(n.field_map, False)
    field.fill_by_array(n.field_map_inv, True)
    cv2.imshow("field", field.field_image)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()