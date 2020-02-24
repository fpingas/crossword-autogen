from cross_gen import DevGrid
import pickle
import random
import re


with open('dictionary.blob', 'r+b') as f:
    dictionary = pickle.load(f)

with open('frequency_list.blob', 'r+b') as f:
    words = pickle.load(f)


class GammaEngine:
    def __init__(self, alpha, beta, seed=None):
        self.engine_ = random.Random(seed)
        self.alpha_ = alpha
        self.beta_ = beta

    def word_dist(self):
        return self.engine_.gammavariate(self.alpha_, self.beta_) / 15

    def random(self):
        return self.engine_.random()

    def choice(self, iterable):
        return self.engine_.choice(iterable)


# 15x15 crossword puzzle of words of 3 letters or more, with words drawn with a gamma distribution of alpha = 0.5 and
# beta = 1 over the frequency list. The random engine is initialized with seed = 10, so this puzzle is always the same.
# This puzzle is created with 35% chance of a word pointing right, 30% pointing down, 20% left, 15% up.
words_aux = [x for x in words if len(x) > 2]
g = DevGrid(15, 15, dictionary, words_aux, GammaEngine(0.5, 1, 10), [0.35, 0.3, 0.2, 0.15])
g.fill()
print(g)


class UniformEngine:
    def __init__(self):
        self.engine_ = random.Random()

    def word_dist(self):
        return self.engine_.random()

    def random(self):
        return self.engine_.random()

    def choice(self, iterable):
        return self.engine_.choice(iterable)


# 25x25 crossword puzzle of words of 4 letters or more. Here, the frequency list is shuffled so its order is no
# longer really important. The random engine is not given a seed and the word distribution is uniform.
# This puzzle is created with 25% chance of a word pointing right, 25% pointing down, 25% left, 25% up.
words_aux = [x for x in words if len(x) > 3]
random.shuffle(words_aux)
k = DevGrid(25, 25, dictionary, words_aux, UniformEngine(), [0.25, 0.25, 0.25, 0.25])
k.fill()
print(k)


# This 13x11 puzzle also uses a shuffled word list and a uniform distribution, but this time, we are only using words
# starting with vowels, and the resulting puzzle will only have words pointing right or down.
words_aux = [x for x in words if len(x) > 2 and re.match(r'^[AEIOU]', x)]
random.shuffle(words_aux)
m = DevGrid(13, 11, dictionary, words_aux, UniformEngine(), [0.5, 0.5, 0, 0])
m.fill()
print(m)
