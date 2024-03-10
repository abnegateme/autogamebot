import itertools
import argparse
import sys

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))


import requests
from bs4 import BeautifulSoup

URL=''

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.116 Safari/537.36'
}


def get_words(letters):
    url = URL
    page = requests.get(url.format(letters), headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    words_block = soup.find('ol', class_='words')
    return [r.text for r in words_block.find_all('a')]


def lookup_words(letter_sequence):
    dictionary = [
        line.rstrip("\n") for line in open("game_algs/dict.txt", "r", encoding='utf8')
    ]
    words = []
    for length in range(3, len(letter_sequence) + 1):
        permutations = itertools.permutations(letter_sequence, length)
        for combination in permutations:
            word = "".join(combination)
            word_ye = word.replace('е', 'ё')
            if word in dictionary and word not in words:
                words.append(word)
                # print(word)
            if word_ye in dictionary and word not in words:
                words.append(word)
    return words


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("letter_sequence")
    # parser.add_argument('word_length', type=int)
    args = parser.parse_args()
    lookup_words(**vars(args))