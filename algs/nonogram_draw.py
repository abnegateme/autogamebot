import numpy as np
import cv2


class Field:
    def __init__(self, cell_count, cell_size):
        self.pad = int(0.2 * cell_size)
        self.cell_count = cell_count
        self.cell_size = cell_size
        field_size = self.cell_count * self.cell_size + 2 * self.pad
        self.color = [100, 100, 100]
        self.field_image = np.zeros((field_size, field_size, 3), np.uint8)
        self.field_map = np.zeros((cell_count, cell_count), dtype=bool)

        for idx in range(0, self.cell_count + 1):
            cv2.line(
                self.field_image,
                (self.pad, self.pad + self.cell_size * idx),
                (field_size - self.pad, self.pad + self.cell_size * idx),
                self.color,
            )
            cv2.line(
                self.field_image,
                (self.pad + self.cell_size * idx, self.pad),
                (self.pad + self.cell_size * idx, field_size - self.pad),
                self.color,
            )

    @classmethod
    def create_with_array(cls, array):
        array = np.array(array)
        array_shape, _ = array.shape
        field = cls(array_shape, 50)
        field.field_map = array
        for y in range(array_shape):
            for x in range(array_shape):
                if array[y][x] == 1:
                    field.field_image[
                        field.pad
                        + y * field.cell_size
                        + int(field.pad / 2) : field.pad
                        + (y + 1) * field.cell_size
                        - int(field.pad / 2),
                        field.pad
                        + x * field.cell_size
                        + int(field.pad / 2) : field.pad
                        + (x + 1) * field.cell_size
                        - int(field.pad / 2),
                        :,
                    ] = [100, 100, 100]
        return field

    def fill_by_array(self, array, is_inv):
        self.field_map = array
        array = np.array(array)
        array_shape, _ = array.shape
        for y in range(array_shape):
            for x in range(array_shape):
                if array[y, x]:
                    self.field_image[
                        self.pad
                        + y * self.cell_size
                        + self.pad
                        + 1 : self.pad
                        + (y + 1) * self.cell_size
                        - self.pad,
                        self.pad
                        + x * self.cell_size
                        + self.pad
                        + 1 : self.pad
                        + (x + 1) * self.cell_size
                        - self.pad,
                        :,
                    ] = (
                        [100, 100, 100] if not is_inv else [0, 0, 100]
                    )

    def add_ver_numbers(self, numbers):
        max_count = max(map(len, numbers))
        old_shape = self.field_image.shape
        new_field_image = np.zeros(
            (
                old_shape[0] + max_count * int(self.cell_size / 2),
                old_shape[1],
                old_shape[2],
            ),
            dtype=np.uint8,
        )

        new_field_image[: -max_count * int(self.cell_size / 2), :, :] = self.field_image
        for idx_x, ver_numbers in enumerate(numbers):
            x = 3 * self.pad + idx_x * self.cell_size
            for idx_y, number in enumerate(ver_numbers):
                y = old_shape[0] + idx_y * int(self.cell_size / 2) + 2 * self.pad
                cv2.putText(
                    new_field_image,
                    str(number),
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    self.color,
                )
        self.field_image = new_field_image

    def add_hor_numbers(self, numbers):
        max_count = max(map(len, numbers))
        old_shape = self.field_image.shape
        new_field_image = np.zeros(
            (
                old_shape[0],
                old_shape[1] + max_count * int(self.cell_size / 2),
                old_shape[2],
            ),
            dtype=np.uint8,
        )

        new_field_image[:, : -max_count * int(self.cell_size / 2), :] = self.field_image
        for idx_y, ver_numbers in enumerate(numbers):
            y = 4 * self.pad + idx_y * self.cell_size
            for idx_x, number in enumerate(ver_numbers):
                x = idx_x * int(self.cell_size / 2) + old_shape[1]
                cv2.putText(
                    new_field_image,
                    str(number),
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    self.color,
                )
        self.field_image = new_field_image


if __name__ == "__main__":
    array = [
        [1, 1, 1, 1, 0],
        [1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1],
    ]
    field = Field(len(array), 50)
    field.fill_by_array(array)
    field.add_ver_numbers([[2], [4], [3, 1], [4], [2]])
    field.add_hor_numbers([[1, 1, 1], [5], [3], [1, 1], [3]])
    cv2.imshow("field", field.field_image)
    cv2.waitKey(0)
