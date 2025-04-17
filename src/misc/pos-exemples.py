from collections import defaultdict
from time import time

start = time()

with open('diccionari/diccionari.txt', 'r', encoding='utf-8') as f:
    dict1 = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for line in f:
        word, lemma, tag = line.split()
        dict1[tag[:1]][tag[:2]][tag].append(word)

with open('diccionari/pos-exemples.txt', 'w', encoding='utf-8') as f:
    for tag1, dict2 in sorted(dict1.items()):
        print(tag1, file=f)
        for tag2, dict3 in sorted(dict2.items()):
            print('\t' + tag2, file=f)
            for tag3, words in sorted(dict3.items()):
                print('\t\t' + tag3 + ': ' + ', '.join(words[::1+len(words)//100]), file=f)


end = time()
print(end-start, 'sec')
print('Done')