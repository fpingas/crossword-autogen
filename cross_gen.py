import itertools as it
import re
from collections import defaultdict
import functools
from enum import Enum
import pprint


def draw_word(freq_list, ref_dict, rand_engine, max_len=0, regex_constraint=None, filter_words=[]) -> tuple:
    """Draws a word and its meaning from the given frequency list and dictionary, using the given random engine to
    draw the word, with filtering parameters """

    if max_len:
        freq_list = [x for x in freq_list if len(x) == max_len]
    if regex_constraint:
        freq_list = [x for x in freq_list if re.match(regex_constraint[:len(x)], x)]
    if filter_words:
        freq_list = [x for x in freq_list if x not in filter_words]
    if not freq_list:
        return False, "", ""
    normalized_ref = rand_engine.word_dist()
    idx_ref = round(min(normalized_ref, 1) * len(freq_list) - 1)
    return True, freq_list[idx_ref], rand_engine.choice(ref_dict[freq_list[idx_ref]])


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


def roll_direction(rand_engine, percents):
    cutoffs = list(it.accumulate(percents))
    ref = rand_engine.random()
    if ref < cutoffs[0]:
        return Direction.RIGHT
    elif ref < cutoffs[1]:
        return Direction.DOWN
    elif ref < cutoffs[2]:
        return Direction.LEFT
    else:
        return Direction.UP


class DevGrid:
    """Create a instance of this class and call the method fill to generate a single crossword puzzle. The init
    parameters are the grid size (horz_size and vert_size). The dictionary and frequency_list are the data structures
    from which words and meanings will be drawn to fill the puzzle. rand_engine is the mean through which the user
    can inject the random devices that will be used in the crossword assemble. The rand_engine instance should have
    at least 3 methods: random, choice and word_dist. The method word_dist should return a float between 0 and 1. The
    method choice should return a single random element from a given iterable. The method random should return a
    random float between 0 and 1. Use the method word_dist to define the probability distribution of the words drawn
    from the frequency list. The parameter direction_percents is a list of 4 floats between 0 and 1, whose total sum
    is 1, in order, each respectively indicating the chance of rolling a word pointing Right, Down, Left, and Up. """

    def __init__(self, horz_size, vert_size, dictionary, frequency_list, rand_engine, direction_percents):
        self.rand_engine_ = rand_engine
        self.draw_word_binded_ = functools.partial(draw_word, frequency_list, dictionary, self.rand_engine_)
        self.h_size_ = horz_size
        self.v_size_ = vert_size
        self.internal_ = [['.' for _ in range(0, horz_size)] for _ in range(0, vert_size)]
        self.empty_starts_ = [(i, j) for i in range(horz_size) for j in range(vert_size)]
        self.meanings_ = {}
        self.words_ = []
        self.direction_percents_ = direction_percents

    def __repr__(self):
        def process_char(char, v_pos, h_pos):
            if char == '@':
                dir, _, _ = self.meanings_[(v_pos, h_pos)]
                if dir == Direction.RIGHT:
                    return '\u2192'
                elif dir == Direction.DOWN:
                    return '\u2193'
                elif dir == Direction.LEFT:
                    return '\u2190'
                elif dir == Direction.UP:
                    return '\u2191'
            else:
                return char

        out = ''
        for v, row in enumerate(self.internal_):
            out += '| '
            out += ' '.join([process_char(x, v, h) for h, x in enumerate(row)])
            out += ' |\n'

        pretty_dict = {(key_v + 1, key_h + 1): mean for (key_v, key_h), (direct, word, mean) in self.meanings_.items()}
        out += pprint.pformat(pretty_dict)
        out += '\n'
        return out

    def _check_constraints(self, h_pos, v_pos, direction):
        if self.internal_[v_pos][h_pos] != '.':
            return False, 0, ""
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
                return False, 0, ""
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
        self.meanings_[(v_pos, h_pos)] = (direction, word, meaning)
        self.words_.append(word)
        self.internal_[v_pos][h_pos] = '@'
        self.empty_starts_.remove((h_pos, v_pos))
        if direction == Direction.RIGHT:
            for index, i in enumerate(range(h_pos + 1, h_pos + len(word) + 1)):
                self.internal_[v_pos][i] = word[index]
                if (i, v_pos) in self.empty_starts_:
                    self.empty_starts_.remove((i, v_pos))
        elif direction == Direction.DOWN:
            for index, i in enumerate(range(v_pos + 1, v_pos + len(word) + 1)):
                self.internal_[i][h_pos] = word[index]
                if (h_pos, i) in self.empty_starts_:
                    self.empty_starts_.remove((h_pos, i))
        elif direction == Direction.LEFT:
            for index, i in enumerate(range(h_pos - 1, h_pos - len(word) - 1, -1)):
                self.internal_[v_pos][i] = word[index]
                if (i, v_pos) in self.empty_starts_:
                    self.empty_starts_.remove((i, v_pos))
        elif direction == Direction.UP:
            for index, i in enumerate(range(v_pos - 1, v_pos - len(word) - 1, -1)):
                self.internal_[i][h_pos] = word[index]
                if (h_pos, i) in self.empty_starts_:
                    self.empty_starts_.remove((h_pos, i))

    def _try_single_insert(self):
        h_pos, v_pos = self.rand_engine_.choice(self.empty_starts_)
        direction = roll_direction(self.rand_engine_, self.direction_percents_)
        is_ok, allowable_length, regex_constraint = self._check_constraints(h_pos, v_pos, direction)
        if is_ok:
            found_word, word, meaning = self.draw_word_binded_(allowable_length, regex_constraint, self.words_)
            if found_word:
                self._insert_to_grid(word, meaning, h_pos, v_pos, direction)

    def fill(self):
        aux_counter = 0
        previous_len = 0
        while aux_counter < (4 * len(self.empty_starts_)):
            self._try_single_insert()
            if len(self.words_) == previous_len:
                aux_counter += 1
            else:
                previous_len = len(self.words_)
                aux_counter = 0
