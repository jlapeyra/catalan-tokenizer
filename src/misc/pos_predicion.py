import numpy as np
import probability
from collections import defaultdict
from typing import Iterable
from diccionari import getDiccionari
from utils import group
import pos
from model import PosModel, allPos


# exemple = 'Jo la vaig veure un dia clar, sota una llum que m\'encegava i quan la vaig gosar mirar ella em tornava la mirada.' \
#     #'I ara en les nits que em gronxo al mar, quan vaig mirant la lluna clara, ja no sé veure més que un far des d\'on somriu la seva cara'
# #exemple = 'I avui també.'

# test_data = open('corpus/espanya.wiki.txt', encoding='utf-8').read()

tokens = []
with open('corpus/ancora-test.pos.txt', encoding='utf-8') as f:
    tokens = [pos.WordInfo(*line.split()) for line in f]

word_tokens : list[pos.WordInfo] = []
for t in tokens:
    if t.word == '_':
        t.word = '\n'
        t.lemma = '\n'
        word_tokens.append(t)
    elif '_' not in t.word:
        word_tokens.append(t)
    else:
        for word in t.word.split('_'):
            word_tokens.append(pos.WordInfo(word, 'loc-'+t.lemma, 'loc-'+t.pos))


pos_len=2
model = PosModel('ancora', pos_len=pos_len, pos_list=allPos(tokens))
#words = pos.splitWords(test_data)
pos_vecs = model.predictPos([t.word for t in word_tokens])

idx2pos = model.idx2pos #[p for p in model.idx2pos if p[0] not in ('$', '-', 'W', 'F', 'Z')]
pos2idx = {p:i for i,p in enumerate(idx2pos)}
num_pos = len(idx2pos)

#confusion_matrix = np.zeros((num_pos, num_pos), dtype=np.int64)
confusion_dict = defaultdict(lambda: defaultdict(int))

inici_frase = True
hit = defaultdict(int)
chance = defaultdict(int)
total = defaultdict(int)
for wi, prediction in zip(word_tokens, map(model.posMax, pos_vecs)):
    actual = wi.pos[:pos_len]
    cat = {p.pos[:pos_len] for p in pos.dictionaryEntries(wi.word, inici_frase=inici_frase)}
    if not wi.pos.startswith('loc') and actual in cat \
        and actual in pos2idx and prediction in pos2idx:
        #confusion_matrix[pos2idx[actual], pos2idx[prediction]] += 1
        confusion_dict[actual][prediction] += 1
        for x in ('TOTAL', actual):
            hit[x] += actual == prediction
            total[x] += 1
            chance[x] += 1/(len(cat))
    inici_frase = wi.word in ('.', '\n') or wi.pos in ('$', 'Fp')


for p in 'TOTAL', *idx2pos:
    print(p)
    print('total:', total[p])
    if total[p] > 0:
        print('accuracy:', hit[p]/total[p])
        print('chance:', chance[p]/total[p])
        print('confidence:', 1-(total[p]-hit[p])/(total[p]-chance[p]) if total[p] != chance[p] else 'NA')
        print('confusion:', dict(confusion_dict[p]))
    print()
    

def plot_confusion_matrix(confusion_matrix:np.ndarray):
    confusion_matrix = confusion_matrix.astype(np.float64)
    confusion_matrix /= confusion_matrix.sum(axis=1, keepdims=True)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 10))
    cax = ax.matshow(confusion_matrix, cmap='Blues')
    plt.colorbar(cax)

    ax.set_xticks(range(num_pos))
    ax.set_yticks(range(num_pos))
    ax.set_xticklabels(idx2pos, rotation=90)
    ax.set_yticklabels(idx2pos)

    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()


# with open('corpus/espanya.wiki.pos.txt', 'w', encoding='utf-8') as f:
#     pos.printAssignacio(zip(tokens, map(posMax, model)), f)

# print_pos(tokens, pos_vecs, limit=100)

pass