import numpy as np
import math


class Nonogram:
    def __init__(self, shape, ver_numbers, hor_numbers):
        self.shape = shape
        self.field_map = np.zeros((self.shape, self.shape), dtype=np.bool)
        self.field_map_inv = np.zeros((self.shape, self.shape), dtype=np.bool)
        self.ver_numbers = ver_numbers
        self.hor_numbers = hor_numbers
        self.ver_sums = list(map(sum, ver_numbers))
        self.hor_sums = list(map(sum, hor_numbers))
        self.ver_check = [0] * self.shape
        self.hor_check = [0] * self.shape

    def solve(self):
        for idx, numbers in enumerate(self.ver_numbers):
            if numbers[0] == self.shape:
                self.field_map[:, idx] = True
            for k in range(self.shape - 1, math.floor(self.shape / 2), -1):
                # подумать, что делать с половиной длинны для нечетных
                n = self.shape - k
                if len(numbers) == 1 and numbers[0] == k:
                    self.field_map[n:-n, idx] = True

                if len(numbers) == self.shape + 1 - self.ver_sums[idx]:
                    shift = 0
                    for num in numbers:
                        self.field_map[shift : shift + num, idx] = True
                        shift = shift + num + 1

        for idx, numbers in enumerate(self.hor_numbers):
            if numbers[0] == self.shape:
                self.field_map[idx, :] = True
            for k in range(self.shape - 1, math.floor(self.shape / 2), -1):
                n = self.shape - k
                if len(numbers) == 1 and numbers[0] == k:
                    self.field_map[idx, n:-n] = True

                if len(numbers) == self.shape + 1 - self.hor_sums[idx]:
                    shift = 0
                    for num in numbers:
                        self.field_map[idx, shift : shift + num] = True
                        shift = shift + num + 1

        for idx, numbers in enumerate(self.ver_numbers):
            if self.field_map[0, idx] == True:
                self.field_map[: numbers[0], idx] = True
            elif self.field_map[-1, idx] == True:
                self.field_map[-numbers[-1] :, idx] = True

        for idx, numbers in enumerate(self.hor_numbers):
            if self.field_map[idx, 0] == True:
                self.field_map[idx, : numbers[0]] = True
            elif self.field_map[idx, -1] == True:
                self.field_map[idx, -numbers[-1] :] = True

        for k in range(self.shape):
            if np.sum(self.field_map[:, k]) == self.ver_sums[k]:
                self.ver_check[k] = 1
            if np.sum(self.field_map[k, :]) == self.hor_sums[k]:
                self.hor_check[k] = 1

        for idx, k in enumerate(self.hor_check):
            if not k and self.hor_sums[idx] == np.sum(self.field_map[idx, :]) + np.sum(
                np.array(self.ver_check) == 0
            ):
                self.field_map[idx, np.array(self.ver_check) == 0] = True
                self.hor_check[idx] = 1

        for idx, k in enumerate(self.ver_check):
            if not k and self.ver_sums[idx] == np.sum(self.field_map[:, idx]) + np.sum(
                np.array(self.hor_check) == 0
            ):
                self.field_map[idx, np.array(self.hor_check) == 0] = True
                self.ver_check[idx] = 1

        print(self.hor_check)
        print(self.ver_check)
        for idx in range(self.shape):
            if self.hor_check[idx]:
                self.field_map_inv[idx, :] = self.field_map[idx, :] == 0
            if self.ver_check[idx]:
                self.field_map_inv[:, idx] = self.field_map[:, idx] == 0


if __name__ == "__main__":
    ver_numbers = [[2], [4], [3, 1], [4], [2]]
    hor_numbers = [[1, 1, 1], [5], [3], [1, 1], [3]]

    n = Nonogram(len(ver_numbers), ver_numbers, hor_numbers)
    n.solve()
