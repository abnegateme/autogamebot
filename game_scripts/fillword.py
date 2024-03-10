#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import time
import itertools
import numpy as np
from itertools import combinations
from multiprocessing import Pool

class WordMatr():
    def __init__(self, filename):
        with codecs.open(filename, 'r', encoding='utf8') as f:
            text = f.read()
        self.size = len(text.split('\r\n')[0])
        self.square = [[0 for x in range(self.size)] for x in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                self.square[i][j] = text.split('\r\n')[i][j]#.encode('utf8')
        return

    def __len__(self):
        return self.size

    def __str__(self):
        output = ''
        for i in range(self.size):
            for j in range(self.size):
                output += self.square[i][j]
                output += ' '
            output += '\n'
        return output


class WordSet():
    def __init__(self, filename):
        self.wordset = set()
        with open(filename, 'r', encoding='utf8') as f:
            for word in f:
                self.wordset.add(word.replace('\n', ''))

class Solver():
    def __init__(self, dict_source, char_range):
        self.dictionary = WordSet(dict_source)
        self.char_range = range(*char_range)
        self.word_coords = []
        self.coord = []
        self.word_masks = []
        self.words = []
        self.solve_words = []
        self.unique_words = []

    def solve(self, fillword_data):
        A = WordMatr(fillword_data)
        B = [[0 for x in range(len(A))] for x in range(len(A))]
        current_word = ''
        for self.char_num in self.char_range:
            for i in range(len(A)):
                for j in range(len(A)):
                    if A.square[i][j] in ['ь', 'ъ']:
                        continue
                    self.search(current_word, A.square, B, i, j)
                    self.coord = []
        return

    def search(self, current_word, A, B, i, j):
        current_word += (A[i][j])
        if len(current_word) == self.char_num:
            if current_word in self.dictionary.wordset:
                self.coord.append((i, j))
                self.word_coords.append(np.array(self.coord))
                self.coord.pop()
                B[i][j] = 1
                self.word_masks.append(np.array(B))
                B[i][j] = 0
                self.words.append(current_word)
                print(current_word, j+1, i+1)
                # self.coord.pop()
                return
            # self.coord.pop()
            return

        self.coord.append((i, j))
        B[i][j] = 1
        if i < len(A)-1:
            if B[i+1][j] == 0:
                self.search(current_word, A, B, i+1, j)

        if j < len(A)-1:
            if B[i][1+j] == 0:
                self.search(current_word, A, B, i, j+1)

        if i > 0:
            if B[i-1][j] == 0:
                self.search(current_word, A, B, i-1, j)

        if j > 0:
            if B[i][j-1] == 0:
                self.search(current_word, A, B, i, j-1)

        self.coord.pop()
        B[i][j] = 0
        return

    def release_arrays(self):
        self.word_coords = []
        self.coord = []
        self.word_masks = []
        self.unique_words = []

    def find(self, i):
        print(f'load function with i = {i}')
        for x in combinations(self.word_masks, i):
            if np.logical_xor.reduce(x).all():
                for mask1 in x:
                    for idx, mask2 in enumerate(self.word_masks):
                        if np.all(mask1 == mask2):
                            self.solve_words.append(self.words[idx])
        print(f'done function with i = {i}')

    def get_unique_words(self):
        self.search_unique_words(self.word_coords)

        return self.unique_words

    def search_unique_words(self, words_crd):
        coordinates = np.concatenate(words_crd, axis=0)
        coord_list, counts = np.unique(coordinates, return_counts=True, axis=0)
        cross_check = lambda x: x.all(2).any(1).any(0)
        uq_crd = coord_list[counts == 1]
        unique_mask = [cross_check(crd[:, None] == uq_crd) for crd in words_crd]
        unique_words = np.array(words_crd)[unique_mask].tolist()

        if len(unique_words) == 0:
            return

        self.unique_words.extend(unique_words)

        sl_crd = np.concatenate(unique_words, axis=0)
        mask = [cross_check(crd[:, None] == sl_crd) for crd in words_crd]
        filtered_words = np.array(words_crd)[np.logical_not(mask)]

        if filtered_words.size > 0:
            self.search_unique_words(filtered_words)

        # return unique_words, filtered_words, unique_mask




# def search(s, A, B, i, j, coord, words):
#     s += (A[i][j])
#     if len(s) == size:
#         if s in set_words.wordset:
#             # words.append(np.argwhere(np.array(B) == 1))
#             coord.append((i, j))
#             words.append(coord.copy())
#             # print(np.argwhere(np.array(B) == 1))
#             print(s, j+1, i+1)
#             return
#         return

#     coord.append((i, j))
#     # print(coord)
#     B[i][j] = 1
#     if i < len(A)-1:
#         if B[i+1][j] == 0:
#             search(s, A, B, i+1, j, coord, words)


#     if j < len(A)-1:
#         if B[i][1+j] == 0:
#             search(s, A, B, i, j+1, coord, words)

#     if i > 0:
#         if B[i-1][j] == 0:
#             search(s, A, B, i-1, j, coord, words)


#     if j > 0:
#         if B[i][j-1] == 0:
#             search(s, A, B, i, j-1, coord, words)
#     B[i][j] = 0
#     coord.pop()
#     return


# def go():
#     A = WordMatr('square.txt')
#     global set_words
#     global size
#     set_words = WordSet('text.txt')
#     B = [[0 for x in range(len(A))] for x in range(len(A))]
#     s = ''
#     coord = []
#     words = []
#     for size in range(7, 8):
#         for i in range(len(A)):
#             for j in range(len(A)):
#                 search(s, A.square, B, i, j, coord, words)
#                 coord = []
#     return words

if __name__ == "__main__":
    timestamp = time.time()
    solver = Solver('dict.txt', (3, 10))
    solver.solve('square4x4.txt')

    words = solver.get_unique_words()
    # for word in words:
    #     print(word)

    solver.release_arrays()

    # print(time.time() - timestamp)
    # timestamp = time.time()
    # words = go()
    # print(time.time() - timestamp)
