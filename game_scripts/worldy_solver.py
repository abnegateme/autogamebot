import re
import argparse
import json
from pprint import pprint as print
from collections import OrderedDict


class Cell:
    def __init__(self, letters: list):
        _data = ''.join(letters)
        self.data = f'{_data}'
        self.is_exact = False

    def get_data(self):
        if not self.is_exact:
            data = f'[{self.data}]'
        else:
            data = self.data

        return data

    def set_exact(self, letter):
        self.data = letter
        self.is_exact = True

    def remove_from_pattern(self, letter):
        if not self.is_exact:
            self.data = self.data.replace(letter, '')

class Solver:
    def __init__(self, kwargs):
        self.num = kwargs['num']
        with open(f'dict_{self.num}.json', encoding="utf8") as _file:
            words = json.load(_file)
        self.words = OrderedDict(sorted(words.items(), key=lambda item: item[1]['weight'], reverse=True))
        with open(f'let_dict_{self.num}.json', encoding="utf8") as _file:
            self.letters = json.load(_file)

        self.cells = [Cell(list(self.letters.keys())) for _ in range(self.num)]

    def get_pattern(self):
        pattern = ''
        for cell in self.cells:
            pattern = pattern + cell.get_data()

        return re.compile(pattern)

    def get_top_n_words(self, n):
        return  list(self.words.items())[:5]

    def get_top_n_unique_words(self, n):
        unique_words = OrderedDict(filter(lambda item: item[1]['unique'], self.words.items()))

        return list(unique_words.items())[:5]

    def remove_from_all_patterns(self, letter):
        for cell in self.cells:
            cell.remove_from_pattern(letter)


    def process(self):
        print(self.get_top_n_words(5))
        print(self.get_top_n_unique_words(5))
        while True:
            word = input('word: ')
            mask = input('mask: ')

            possible = []
            for idx, (m, l) in enumerate(zip(mask, word)):
                if m == '-':
                    if not m in word[:idx] + word[idx+1:]:
                        self.remove_from_all_patterns(l)
                    else:
                        self.cells[idx].remove_from_pattern(l)
                elif m == '*':
                    self.cells[idx].remove_from_pattern(l)
                    possible.append(l)
                elif m == '+':
                    self.cells[idx].set_exact(l)

            self.words.pop(word)
            pattern = self.get_pattern()
            print(pattern)
            self.words = OrderedDict(filter(lambda item: not re.findall(pattern, item[0]) == [], self.words.items()))
            for l in possible:
                self.words = OrderedDict(filter(lambda item: l in item[0], self.words.items()))
            print(self.get_top_n_words(5))
            print(self.get_top_n_unique_words(5))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num', type=int, default=5)
    kwargs = vars(parser.parse_args())

    solver = Solver(kwargs)
    solver.process()