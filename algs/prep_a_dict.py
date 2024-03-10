import re
import argparse
from pprint import pprint as print
from collections import OrderedDict
import json
from os.path import dirname, realpath, join

def main(kwargs):
    with open(kwargs['word_list_path'], encoding="utf8") as _file:
        words = _file.readlines()

    regex = re.compile(r'[\n\r\t]')
    words = [regex.sub('', word) for word in words]
    if not kwargs['replace_it_patterns'] is None or not kwargs['replace_with_patterns'] is None:
        for a, b in zip(kwargs['replace_it_patterns'], kwargs['replace_with_patterns']):
            words = [word.replace(a, b) for word in words]

    letters_number = kwargs['letters_number']
    pattern = re.compile(kwargs['filter_pattern'] + '{' + f'{letters_number}' + '}$')
    words = [word for word in words if not re.match(pattern, word) is None]

    sorted_letters = {}
    for word in words:
        for letter in word:
            if letter in sorted_letters:
                sorted_letters[letter]['count'] += 1
            else:
                sorted_letters.update({letter: {'count': 0, 'weight': 0.0}})
                sorted_letters[letter]['count'] += 1

    max_count = max([stat['count'] for stat in sorted_letters.values()])
    for _, stat in sorted_letters.items():
        stat['weight'] = stat['count'] / max_count

    sorted_letters = OrderedDict(sorted(sorted_letters.items(), key=lambda item: item[1]['weight'], reverse=True))

    sorted_words = {}
    for word in words:
        weight = 0.0
        for letter in word:
            weight += sorted_letters[letter]['weight']
        is_unique = len(word) == len(set(word))
        sorted_words.update({word: {'weight': weight, 'unique': is_unique}})

    sorted_words = OrderedDict(sorted(sorted_words.items(), key=lambda item: item[1]['weight'], reverse=True))

    print(sorted_letters)
    print(list(sorted_words.items())[:5])

    with open(join(dirname(realpath(__file__)), f'dict_{letters_number}.json'), 'w',  encoding='utf8') as _file:
        json.dump(sorted_words, _file, ensure_ascii=False, indent=4)
    with open(join(dirname(realpath(__file__)), f'let_dict_{letters_number}.json'), 'w',  encoding='utf8') as _file:
        json.dump(sorted_letters, _file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-wlp', '--word_list_path', type=str, required=True)
    parser.add_argument('-n', '--letters_number', type=int, default=5)
    parser.add_argument('-rip', '--replace_it_patterns', type=str, nargs='*')
    parser.add_argument('-rwp', '--replace_with_patterns', type=str, nargs='*')
    parser.add_argument('-fp', '--filter_pattern', type=str, default='[a-z]')

    kwargs = vars(parser.parse_args())
    print(kwargs)
    if not kwargs['replace_it_patterns'] is None or not kwargs['replace_with_patterns'] is None:
        assert len(kwargs['replace_it_patterns']) == len(kwargs['replace_with_patterns'])

    main(kwargs)