import numpy as np
import probability
from collections import defaultdict
from typing import Iterable
from diccionari import getDiccionari
from utils import group
import pos
from pos import DICCIONARI, categoriesPossibles, splitWords
from copy import copy

idx2pos = copy(pos.pos_list)
pos2idx = {p:i for i,p in enumerate(idx2pos)}
num_pos = len(idx2pos)
ALPHA = 0.5


count_back = np.zeros((num_pos, num_pos), dtype=np.int64)
with open('model/pos.2gram.txt') as f:
    for line in f:
        k1, k2, num = line.split()
        k1 = pos2idx[k1]
        k2 = pos2idx[k2]
        num = int(num)
        count_back[k1, k2] = num

count_fwd = count_back.T

prob_cond_fwd = probability.distribution(count_fwd + ALPHA)
prob_cond_back = probability.distribution(count_back + ALPHA)

count_totals = sum(count_back)
assert np.array_equal(count_totals, sum(count_fwd))
prob_a_priori = probability.distribution(np.ones(num_pos, dtype=np.float64))

count_by_word = defaultdict(lambda: np.zeros(num_pos, dtype=np.int64))
with open('model/pos.count.txt', encoding='utf-8') as f:
    for line in f:
        word, k, num = line.split()
        k = pos2idx[k]
        num = int(num)
        count_by_word[word][k] = num

def getBoolArrayPos(pos_list:Iterable[str]):
    ret = np.zeros(num_pos, dtype=bool)
    for pos_ in pos_list:
        ret[pos2idx[pos_]] = True
    return ret

def getCountArrayPos(pos_list:Iterable[str]):
    ret = np.zeros(num_pos, dtype=np.int32)
    for pos_ in pos_list:
        ret[pos2idx[pos_]] += 1
    return ret

# small_lower_dict = defaultdict(list)
# for k,v in DICCIONARI.items():
#     if k.lower() in count_by_word:
#         small_lower_dict[k.lower()].extend(v)

def getPosAllCase(word:str):
    return {
        info.pos[0] for info in 
        DICCIONARI[word] + DICCIONARI[word.upper()] + DICCIONARI[word.capitalize()]
    }

prob_by_word = dict()
for word, count_ in count_by_word.items():
    prob_by_word[word] = probability.distribution(
            count_ + 0.8*getCountArrayPos(getPosAllCase(word))
    )

def getSortedPos(arr_prob:np.ndarray):
    return sorted([
        (arr_prob[j], idx2pos[j]) for j in range(num_pos) if arr_prob[j]
    ], reverse=True)

pass

def getProbPosWord(paraula:str, inici_frase:bool):
    if paraula.lower() in prob_by_word:
        return prob_by_word[paraula.lower()]
    else:
        categories = categoriesPossibles(paraula, inici_frase)
        if not categories: 
            return probability.uniform(num_pos)
        return probability.distribution(getBoolArrayPos(categories))
    #prob *= getBoolArrayPos(categoriesPossibles(paraula, inici_frase))
    #if not np.any(prob): return copy(prob_a_priori)
    #return probability.distribution(prob)
    

exemple = 'Jo la vaig veure un dia clar, sota una llum que m\'encegava i quan la vaig gosar mirar ella em tornava la mirada.' \
    #'I ara en les nits que em gronxo al mar, quan vaig mirant la lluna clara, ja no sé veure més que un far des d\'on somriu la seva cara'
#exemple = 'I avui també.'

train = open('corpus/espanya.wiki.txt', encoding='utf-8').read()


words = splitWords(train)
pos_vecs = []
ini_frase = True
for word in words:
    pos_vecs.append(getProbPosWord(word, ini_frase))
    ini_frase = (word == '.')

boundary_pos_vec = getBoolArrayPos(['-'])


def print_pos(words, pos_vecs, / , limit=200):
    for w,probs in zip(words[:limit], pos_vecs):
        print(w, end=': ')
        for i,p in enumerate(probs):
            if p > 0:
                print(f'{idx2pos[i]}:{p:.4f}', end=', ')
        print()
    print()


for i in range(len(pos_vecs)):
    prev_pos_vec = pos_vecs[i-1] if i>0 else boundary_pos_vec
    pos_vecs[i] = probability.combination(pos_vecs[i], (prob_cond_fwd @ prev_pos_vec))
    #pos_vecs[i] = (prev_pos_vec @ prob_cond_fwd) * pos_vecs[i] / prob_a_priori
print()

for i in reversed(range(len(pos_vecs))):
    prev_pos_vec = pos_vecs[i+1] if i<len(pos_vecs)-1 else boundary_pos_vec
    pos_vecs[i] = probability.combination(pos_vecs[i], (prob_cond_back @ prev_pos_vec))
    #pos_vecs[i] = (prev_pos_vec @ prob_cond_back) * pos_vecs[i] / prob_a_priori
print()

def posMax(vec):
    imax = max(range(num_pos), key=lambda i: vec[i])
    return idx2pos[imax]

with open('corpus/espanya.wiki.pos.txt', 'w', encoding='utf-8') as f:
    pos.printAssignacio(zip(words, map(posMax, pos_vecs)), f)

print_pos(words, pos_vecs, limit=100)

pass