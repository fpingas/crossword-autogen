import itertools as it
import re
from collections import defaultdict
import random
import functools
from enum import Enum


# seed for development and testing
# random.seed(5)


def build_dictionary() -> dict:
    """Parses and filters the raw dictionary file with some heuristics to build a python dictionary of english words """

    english_dict_file_path: str = 'raw_data/29765.txt.utf-8'
    words: list = []
    definitions: list = []
    with open(english_dict_file_path, 'r') as f:
        for key, group in it.groupby(f, lambda f_line: f_line.isupper()):
            if key:
                group = list(group)[0].split(';')
                group = [x.strip(' \n') for x in group]
                words.append(group)
            else:
                group = [x for x in group if x != '\n']
                filtered_g: list = []
                previous = None
                for line in group:
                    if previous is None:
                        previous = line
                    else:
                        if re.match(r'^[0-9]*\.\s', line) or line.startswith('Defn: '):
                            filtered_g.append(previous.replace('\n', ' ').strip())
                            previous = line
                        else:
                            previous += line
                if previous is not None:
                    filtered_g.append(previous.replace('\n', ' ').strip())
                filtered_g = filtered_g[1:]
                filtered_g = [x.replace('Defn:', '').strip() for x in filtered_g]
                filtered_g = [x.replace('Etym:', '').strip() for x in filtered_g]
                filtered_g = [re.sub(r'^[0-9]*\.', '', x) for x in filtered_g]
                filtered_g = [re.sub(r'^\(.*\)$', '', x) for x in filtered_g]
                filtered_g = [x.split('--', 1)[0] for x in filtered_g]
                filtered_g = [x.split('[', 1)[0] for x in filtered_g]
                filtered_g = [x.strip() for x in filtered_g]
                filtered_g = [re.sub(r'^See \w*\.$', '', x) for x in filtered_g]
                filtered_g = [x.strip() for x in filtered_g]
                filtered_g = [x for x in filtered_g if re.match(r'^[A-Z]', x)]
                filtered_g = [x for x in filtered_g if x]
                definitions.append(filtered_g[:1])

    words = words[9:-7]
    definitions = definitions[10:-7]
    dictionary = defaultdict(list)

    def fill_dict(words_in: list, definition_in: list):
        if words_in and definition_in:
            for word in words_in:
                dictionary[word].append(definition_in[0])

    list(map(fill_dict, words, definitions))
    return dictionary


def build_frequency_list(dict_filter) -> list:
    """Parses the raw frequency list file and filters the resulting list with the given dictionary, so we only have
    words whose meaning we can lookup """

    original_file_path: str = 'raw_data/count_1w.txt'
    raw_words: list = []
    with open(original_file_path, 'r') as f:
        for line in f:
            raw_words.append(line.split('\t', 1)[0].upper())
    # consider shuffle necessity
    random.shuffle(raw_words)
    return [x for x in raw_words if len(x) > 1 and x in dict_filter]


def draw_word(freq_list, ref_dict, alpha, beta, max_len=0, regex_constraint=None, filter_words=[]) -> tuple:
    """Draws a word and its meaning from the given frequency list and dictionary, using a gamma distribution with the
    given alpha and beta parameters, with filter possibilities  """

    if max_len:
        freq_list = [x for x in freq_list if len(x) == max_len]
    if regex_constraint:
        freq_list = [x for x in freq_list if re.match(regex_constraint[:len(x)], x)]
    if filter_words:
        freq_list = [x for x in freq_list if x not in filter_words]
    if not freq_list:
        return False, _, _
    # rethink methods of random sampling
    rand_ref = random.gammavariate(alpha, beta)
    normalized_ref = rand_ref/15
    idx_ref = round(min(normalized_ref, 1) * len(freq_list)-1)
    return True, freq_list[idx_ref], random.choice(ref_dict[freq_list[idx_ref]])


dictionary = build_dictionary()
words = build_frequency_list(dictionary)
draw_word_binded = functools.partial(draw_word, words, dictionary, 7.5, 1)


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


# could add some additional directions
def roll_direction():
    ref = random.random()
    if ref < 0.4:
        return Direction.RIGHT
    elif ref < 0.8:
        return Direction.DOWN
    elif ref < 0.9:
        return Direction.LEFT
    else:
        return Direction.UP


class DevGrid:
    """Helper class for development purposes """

    def __init__(self, horz_size, vert_size):
        self.h_size_ = horz_size
        self.v_size_ = vert_size
        self.internal_ = [['.' for _ in range(0, horz_size)] for _ in range(0, vert_size)]
        self.meanings_ = []
        self.words_ = []

    def __repr__(self):
        out = ''
        for row in self.internal_:
            out += str(row)
            out += '\n'
        return out

    def _check_constraints(self, h_pos, v_pos, direction):
        if self.internal_[v_pos][h_pos] != '.':
            return False, _, _
        elif direction == Direction.RIGHT:
            space_for_word = it.takewhile(lambda x: x != '@', self.internal_[v_pos][h_pos+1:])
        elif direction == Direction.DOWN:
            space_for_word = []
            for i in range(v_pos+1, self.v_size_):
                elem = self.internal_[i][h_pos]
                if elem == '@':
                    break
                space_for_word.append(elem)
        elif direction == Direction.LEFT:
            if h_pos == 0:
                return False, _, _
            space_for_word = it.takewhile(lambda x: x != '@', self.internal_[v_pos][h_pos-1::-1])
        elif direction == Direction.UP:
            space_for_word = []
            for i in range(v_pos - 1, -1, -1):
                elem = self.internal_[i][h_pos]
                if elem == '@':
                    break
                space_for_word.append(elem)
        regex_constraint = ''.join(space_for_word)
        allowable_length = len(regex_constraint)
        is_ok = allowable_length > 0
        return is_ok, allowable_length, regex_constraint

    def _insert_to_grid(self, word, meaning, h_pos, v_pos, direction):
        self.meanings_.append(((v_pos, h_pos), direction, word, meaning))
        self.words_.append(word)
        self.internal_[v_pos][h_pos] = '@'
        if direction == Direction.RIGHT:
            for index, i in enumerate(range(h_pos + 1, h_pos + len(word) + 1)):
                self.internal_[v_pos][i] = word[index]
        elif direction == Direction.DOWN:
            for index, i in enumerate(range(v_pos + 1, v_pos + len(word) + 1)):
                self.internal_[i][h_pos] = word[index]
        elif direction == Direction.LEFT:
            for index, i in enumerate(range(h_pos - 1, h_pos - len(word) - 1, -1)):
                self.internal_[v_pos][i] = word[index]
        elif direction == Direction.UP:
            for index, i in enumerate(range(v_pos - 1, v_pos - len(word) - 1, -1)):
                self.internal_[i][h_pos] = word[index]

    def try_single_insert(self):
        empty_starts = []
        for i in range(self.v_size_):
            for j in range(self.h_size_):
                if self.internal_[i][j] == '.':
                    empty_starts.append((i, j))
        v_pos, h_pos = random.choice(empty_starts)
        direction = roll_direction()
        is_ok, allowable_length, regex_constraint = self._check_constraints(h_pos, v_pos, direction)
        if is_ok:
            found_word, word, meaning = draw_word_binded(allowable_length, regex_constraint)
            if found_word:
                self._insert_to_grid(word, meaning, h_pos, v_pos, direction)


g = DevGrid(10, 15)
for _ in range(1000):
    g.try_single_insert()

print(g)

h = DevGrid(20, 15)
for _ in range(1000):
    h.try_single_insert()

print(h)

k = DevGrid(25, 25)
for _ in range(1000):
    k.try_single_insert()

print(k)
