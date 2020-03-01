# crossword-autogen
Procedural generation of crossword puzzles, parametric in puzzle size, "expected" difficulty, and input dictionaries!

For now, there is no front end for this project as it is currently only a proof-of-concept.

## Concept
Given that it should be easy to get hands on an regular dictionary and that a crossword puzzle is pretty simple in its format, it should be possible to generate a random puzzle, drawing words from this input dictionary.

One worry was that randomly drawing words from a dictionary would almost always make puzzles mostly containing obscure words. To offset this, we also use as an input a possible frequency list of words (all of which should be present in the dictionary), and it draws from this frequency list by using indexes derived from a random engine that is also an input. This way, it is possible, for example, to input a regular frequency list and a random engine that gives random numbers drawn from a gamma distribution with parameters such that we mainly get words from the first percentiles of the list. This is flexible enough to make puzzles that are "easier" or "harder", or even just random.

To test the idea, I prepared a dictionary and frequency list for english words. Most-frequently used english words are derived from <a href="https://norvig.com/ngrams/" rel="nofollow">Peter Norvig's</a> compilation of the <a href="https://norvig.com/ngrams/count_1w.txt" rel="nofollow"> 1/3 million most frequent English words</a>, which links the _Google Web Trillion Word Corpus_, as <a href="http://googleresearch.blogspot.com/2006/08/all-our-n-gram-are-belong-to-you.html">described</a> by Thorsten Brants and Alex Franz, and are <a href="http://tinyurl.com/ngrams">distributed</a> by the Linguistic Data Consortium. The dictionary is the Webster's Unabridged Dictionary by Various, made available by the <a href="http://www.gutenberg.org/ebooks/29765">Gutenberg Project</a>.

Since using the complete dictionary reading for a given word would be too naive even for a showcase, I did some ad-hoc data cleaning. This routine can be seen in the *data_parser.py* script. To run the cleanup, you will need to unpack the data files from the *raw_data.tar.xz* file. It is not necessary to run the cleanup to generate puzzles from this dataset. The processed dictionary and frequency list are saved as *.blob* files in this repo.

The algorithm is something like: It makes an empty grid with the given size. It randomly picks a spot in the grid and a direction. It checks the constraints for the word that will fit this spot (size and possibly letters). It filters words to only those that fit. It there are any, it randomly picks one and puts it in the grid. It once again picks a spot in the grid and repeats. It repeats until it is taking too long to find a new word.

There are no third-party dependencies. It was made using Python 3.6.9.

## How to use

Example of a 15 x 15 puzzle of words with 3 letters or more, with words drawn with a gamma distribution of alpha = 0.5 and beta = 1 over the frequency list. The random engine is initialized with seed = 10, so this puzzle is always the same. This puzzle is created with 35% chance of a word pointing right, 30% pointing down, 20% left, 15% up.

```python
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


words_aux = [x for x in words if len(x) > 2]
g = DevGrid(15, 15, dictionary, words_aux, GammaEngine(0.5, 1, 10), [0.35, 0.3, 0.2, 0.15])
g.fill()
print(g)
```
25 x 25 crossword puzzle of 4 letters or more. Here, the frequency list is shuffled so its order is no longer really important. The random engine is not given a seed and the word distribution is uniform. This puzzle is created with 25% chance of a word pointing right, 25% pointing down, 25% left, 25% up.
```python
class UniformEngine:
    def __init__(self):
        self.engine_ = random.Random()

    def word_dist(self):
        return self.engine_.random()

    def random(self):
        return self.engine_.random()

    def choice(self, iterable):
        return self.engine_.choice(iterable)



words_aux = [x for x in words if len(x) > 3]
random.shuffle(words_aux)
k = DevGrid(25, 25, dictionary, words_aux, UniformEngine(), [0.25, 0.25, 0.25, 0.25])
k.fill()
print(k)
```
This 13 x 11 puzzle also uses a shuffled word list and a uniform distribution, but this time, we are only using words starting with vowels, and the resulting puzzle will only have words pointing right or down.
```python
words_aux = [x for x in words if len(x) > 2 and re.match(r'^[AEIOU]', x)]
random.shuffle(words_aux)
m = DevGrid(13, 11, dictionary, words_aux, UniformEngine(), [0.5, 0.5, 0, 0])
m.fill()
print(m)
```

## Example of generated crossword puzzle (the last one from the example code above):

```
| → A G R E E ↓ → A M I S H |
| → A F F Y → E N D O R S E |
| ↓ → E N T A B L A T U R E |
| U . . ↓ → A U L D ↓ . . . |
| N . → A D D L E → A L E E |
| C ↓ ↓ V → I L I U M ↓ . . |
| T U A I → A I L → I A M B |
| U N L S ↓ ↓ E ↓ . R N . . |
| O C T I A O N O . → E Y E |
| U O H O R J T B → E L S E |
| S → O N T O → I N F E S T |

{(1, 1): 'In good part; kindly.',
 (1, 7): 'Boiling up or over; hence, manifesting exhilaration or excitement, '
         'as of feeling; effervescing. "Ebullient with subtlety." De Quincey. '
         'The ebullient enthusiasm of the French. Carlyle.',
 (1, 8): 'The Amish Mennonites.',
 (2, 1): "To confide (one's self to, or in); to trust.",
 (2, 6): 'Same as Indorse. Note: Both endorse and indorse are used by good '
         'writers; but the tendency is to the more general use of indorse and '
         'its derivatives indorsee, indorser, and indorsement.',
 (3, 1): 'Of the nature or quality of an unguent or ointment; fatty; oily; '
         'greasy. "The unctuous cheese." Longfellow.',
 (3, 2): 'The superstructure which lies horizontally upon the columns. See '
         'Illust. of Column, Cornice. Note: It is commonly divided into '
         'architrave, the part immediately above the column; frieze, the '
         'central space; and cornice, the upper projecting moldings. Parker.',
 (4, 4): 'Vision.',
 (4, 5): 'Old; as, Auld Reekie (old smoky), i. e., Edinburgh.',
 (4, 10): 'Same as Ameer.',
 (5, 3): 'Having lost the power of development, and become rotten, as eggs; '
         'putrid. Hence: Unfruitful or confused, as brains; muddled. Dryden.',
 (5, 9): 'On or toward the lee, or the side away from the wind; the opposite '
         'of aweather. The helm of a ship is alee when pressed close to the '
         'lee side. Hard alee, or Luff alee, an order to put the helm to the '
         'lee side.',
 (6, 2): 'Unknown; strange, or foreign; unusual, or surprising; distant in '
         'manner; reserved.',
 (6, 3): 'Although.',
 (6, 5): 'The dorsal one of the three principal bones comprising either '
         'lateral half of the pelvis; the dorsal or upper part of the hip '
         'bone. See Innominate bone, under Innominate.',
 (6, 11): 'To anoint. Shipley.',
 (7, 5): 'To affect with pain or uneasiness, either physical or mental; to '
         'trouble; to be the matter with;',
 (7, 9): 'An iambus or iambic.',
 (8, 5): 'The employment of means to accomplish some desired end; the '
         'adaptation of things in the natural world to the uses of life; the '
         'application of knowledge or power to practical purposes. Blest with '
         'each grace of nature and of art. Pope.',
 (8, 6): 'A spring, surrounded by rushes or rank grass; an oasis.',
 (8, 8): 'A form of folk magic, medicine or witchcraft originating in Africa '
         'and practised in parts of the Caribbean.',
 (9, 10): 'To appear; to look.',
 (10, 9): 'Besides; except that mentioned; in addition; as, nowhere else; no '
          'one else.',
 (11, 2): 'On the top of; upon; on. See On to, under On, prep.',
 (11, 7): 'Mischievous; hurtful; harassing.'}
```
See also the *100x100_example* file for a 100 x 100 crossword puzzle!

Note that the definitions for the words are strange at best, some mentioning the word itself, some containing names of authors that have used the word, and other issues. Also, this dictionary is from 1913(!), so many words and definitions are archaic. For these reasons, these are not "production-grade" puzzles. Then again, the algorithm generated these puzzles and it can generate many more! The quality of its output is really only limited by the quality of the given dictionary.
