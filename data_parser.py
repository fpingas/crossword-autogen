import itertools as it
import re
from collections import defaultdict
import pickle


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
    return [x for x in raw_words if x in dict_filter]


dictionary = build_dictionary()
words = build_frequency_list(dictionary)

with open('dictionary.blob', 'w+b') as f:
    pickle.dump(dictionary, f)

with open('frequency_list.blob', 'w+b') as f:
    pickle.dump(words, f)

